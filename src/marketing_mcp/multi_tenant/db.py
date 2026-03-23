"""Database access layer for multi-tenant operations (asyncpg)."""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from uuid import UUID

import asyncpg

from marketing_mcp.multi_tenant.crypto import decrypt_credentials, encrypt_credentials

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None

# Local cache for tenant lookups (API key hash → tenant data + credentials + timestamp)
_tenant_cache: dict[str, tuple[dict, float]] = {}
_TENANT_CACHE_TTL = 60  # seconds


async def get_pool() -> asyncpg.Pool:
    """Get or create the asyncpg connection pool."""
    global _pool
    if _pool is None:
        dsn = os.environ.get("DATABASE_URL", "")
        if not dsn:
            raise RuntimeError(
                "DATABASE_URL env var is required for multi-tenant mode. "
                "Example: postgresql://user:pass@localhost:5432/marketing_mcp"
            )
        _pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)
    return _pool


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


# ─── API Key Operations ───────────────────────────────────────────────


def hash_api_key(raw_key: str) -> str:
    """SHA-256 hash of a raw API key."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key. Returns (full_key, key_hash, key_prefix)."""
    raw = "mk_live_" + secrets.token_urlsafe(32)
    return raw, hash_api_key(raw), raw[:12]


# ─── Tenant Resolution ───────────────────────────────────────────────


async def resolve_tenant_by_api_key(key_hash: str) -> dict | None:
    """Look up tenant + decrypted credentials by API key hash.

    Uses a local TTL cache to avoid DB queries on every tool call.
    Returns dict with keys: id, name, slug, plan_tier, max_connections,
    max_monthly_calls, api_key_id, credentials (dict of all env var names → values).
    """
    # Check cache
    cached = _tenant_cache.get(key_hash)
    if cached and (time.monotonic() - cached[1]) < _TENANT_CACHE_TTL:
        return cached[0]

    pool = await get_pool()

    # Look up API key → tenant
    row = await pool.fetchrow(
        """
        SELECT ak.id AS api_key_id, ak.tenant_id,
               t.name, t.slug, t.plan_tier, t.max_connections, t.max_monthly_calls
        FROM api_keys ak
        JOIN tenants t ON t.id = ak.tenant_id
        WHERE ak.key_hash = $1 AND ak.is_active = true
        """,
        key_hash,
    )
    if row is None:
        return None

    tenant_id = row["tenant_id"]

    # Update last_used_at (fire-and-forget)
    await pool.execute(
        "UPDATE api_keys SET last_used_at = NOW() WHERE id = $1",
        row["api_key_id"],
    )

    # Load and decrypt all active platform connections
    connections = await pool.fetch(
        """
        SELECT platform, credentials_encrypted, credentials_nonce
        FROM platform_connections
        WHERE tenant_id = $1 AND is_active = true
        """,
        tenant_id,
    )

    # Merge all platform credentials into one flat dict
    all_creds: dict[str, str] = {}
    for conn in connections:
        try:
            creds = decrypt_credentials(
                bytes(conn["credentials_encrypted"]),
                bytes(conn["credentials_nonce"]),
            )
            all_creds.update(creds)
        except Exception:
            logger.warning(
                "Failed to decrypt credentials for tenant %s platform %s",
                tenant_id,
                conn["platform"],
            )

    result = {
        "id": str(tenant_id),
        "name": row["name"],
        "slug": row["slug"],
        "plan_tier": row["plan_tier"],
        "max_connections": row["max_connections"],
        "max_monthly_calls": row["max_monthly_calls"],
        "api_key_id": str(row["api_key_id"]),
        "credentials": all_creds,
    }

    # Cache it
    _tenant_cache[key_hash] = (result, time.monotonic())
    return result


def invalidate_tenant_cache(key_hash: str | None = None) -> None:
    """Clear tenant cache for a specific key or all keys."""
    if key_hash:
        _tenant_cache.pop(key_hash, None)
    else:
        _tenant_cache.clear()


# ─── Usage Logging ────────────────────────────────────────────────────


async def log_usage(
    tenant_id: str,
    tool_name: str,
    api_key_id: str | None = None,
    duration_ms: int | None = None,
    success: bool = True,
    error_message: str | None = None,
) -> None:
    """Insert a usage log entry."""
    try:
        pool = await get_pool()
        await pool.execute(
            """
            INSERT INTO usage_logs (tenant_id, api_key_id, tool_name, duration_ms, success, error_message)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            UUID(tenant_id),
            UUID(api_key_id) if api_key_id else None,
            tool_name,
            duration_ms,
            success,
            error_message[:500] if error_message else None,
        )
    except Exception:
        logger.warning("Failed to log usage for tenant %s tool %s", tenant_id, tool_name)


async def get_monthly_usage_count(tenant_id: str) -> int:
    """Count tool calls this calendar month for a tenant."""
    pool = await get_pool()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    row = await pool.fetchrow(
        """
        SELECT COUNT(*) AS cnt FROM usage_logs
        WHERE tenant_id = $1 AND created_at >= $2
        """,
        UUID(tenant_id),
        month_start,
    )
    return row["cnt"] if row else 0


# ─── Tenant Management (for admin/portal) ────────────────────────────


async def create_tenant(name: str, slug: str, plan_tier: str = "free") -> dict:
    """Create a new tenant. Returns the row as dict."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO tenants (name, slug, plan_tier)
        VALUES ($1, $2, $3)
        RETURNING id, name, slug, plan_tier, max_connections, max_monthly_calls, created_at
        """,
        name,
        slug,
        plan_tier,
    )
    return dict(row)


async def create_api_key_for_tenant(tenant_id: str, label: str | None = None) -> dict:
    """Create a new API key for a tenant. Returns full key (shown once) + metadata."""
    raw_key, key_hash, key_prefix = generate_api_key()
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO api_keys (tenant_id, key_hash, key_prefix, label)
        VALUES ($1, $2, $3, $4)
        RETURNING id, key_prefix, label, created_at
        """,
        UUID(tenant_id),
        key_hash,
        key_prefix,
        label,
    )
    return {"raw_key": raw_key, **dict(row)}


async def save_platform_connection(
    tenant_id: str, platform: str, credentials: dict[str, str]
) -> dict:
    """Store encrypted credentials for a platform. Upserts if already exists."""
    ciphertext, nonce = encrypt_credentials(credentials)
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        INSERT INTO platform_connections (tenant_id, platform, credentials_encrypted, credentials_nonce)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (tenant_id, platform)
        DO UPDATE SET credentials_encrypted = EXCLUDED.credentials_encrypted,
                      credentials_nonce = EXCLUDED.credentials_nonce,
                      updated_at = NOW()
        RETURNING id, platform, is_active, created_at, updated_at
        """,
        UUID(tenant_id),
        platform,
        ciphertext,
        nonce,
    )
    # Invalidate cache so next request picks up new credentials
    invalidate_tenant_cache()
    return dict(row)
