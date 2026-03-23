"""In-memory TTL cache for expensive API calls."""

import threading
import time
from typing import Any

from marketing_mcp.utils.auth import _tenant_ctx

# Default TTLs (seconds)
KEYWORD_TTL = 3600  # 1 hour
AUDIENCE_TTL = 86400  # 24 hours


class TTLCache:
    """Thread-safe in-memory cache with per-key TTL expiry.

    Automatically prefixes keys with the current tenant ID (if set)
    so cached data is isolated per tenant.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _prefixed_key(key: str) -> str:
        """Prefix the key with tenant ID if in multi-tenant context."""
        tenant_creds = _tenant_ctx.get()
        if tenant_creds is not None:
            tenant_id = tenant_creds.get("__tenant_id__", "")
            if tenant_id:
                return f"t:{tenant_id}:{key}"
        return key

    def get(self, key: str) -> Any | None:
        """Get a value if it exists and hasn't expired."""
        pkey = self._prefixed_key(key)
        with self._lock:
            entry = self._store.get(pkey)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() > expires_at:
                del self._store[pkey]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int = KEYWORD_TTL) -> None:
        """Store a value with a TTL in seconds."""
        pkey = self._prefixed_key(key)
        with self._lock:
            self._store[pkey] = (value, time.monotonic() + ttl)

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._store.clear()
