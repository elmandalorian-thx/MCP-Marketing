"""Pydantic models for multi-tenant entities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    """An agency/organization."""

    id: UUID
    name: str
    slug: str
    plan_tier: str = "free"
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
    max_connections: int = 3
    max_monthly_calls: int = 500
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApiKey(BaseModel):
    """An API key belonging to a tenant."""

    id: UUID
    tenant_id: UUID
    key_hash: str
    key_prefix: str
    label: str | None = None
    is_active: bool = True
    last_used_at: datetime | None = None
    created_at: datetime | None = None


class PlatformConnection(BaseModel):
    """Encrypted credentials for one platform belonging to a tenant."""

    id: UUID
    tenant_id: UUID
    platform: str
    credentials_encrypted: bytes
    credentials_nonce: bytes
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UsageLogEntry(BaseModel):
    """A single tool call usage record."""

    tenant_id: UUID
    api_key_id: UUID | None = None
    tool_name: str
    duration_ms: int | None = None
    success: bool = True
    error_message: str | None = None


# Plan limits for quick lookup
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {"seats": 1, "connections": 3, "monthly_calls": 500},
    "starter": {"seats": 3, "connections": 10, "monthly_calls": 5_000},
    "pro": {"seats": 10, "connections": 50, "monthly_calls": 50_000},
    "enterprise": {"seats": 999_999, "connections": 999_999, "monthly_calls": 999_999_999},
}
