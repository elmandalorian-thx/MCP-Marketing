"""FastMCP middleware for multi-tenant authentication and usage logging."""

from __future__ import annotations

import logging
import time
from typing import Any

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from marketing_mcp.multi_tenant.db import (
    get_monthly_usage_count,
    hash_api_key,
    log_usage,
    resolve_tenant_by_api_key,
)
from marketing_mcp.utils.auth import _tenant_ctx

logger = logging.getLogger(__name__)


class TenantAuthMiddleware(Middleware):
    """Authenticate MCP requests via API key and inject tenant context.

    Reads the ``Authorization: Bearer mk_live_...`` header, resolves the
    tenant from the database, decrypts their platform credentials, and
    sets them in the ``_tenant_ctx`` contextvar so ``get_credential()``
    returns the tenant's credentials instead of env vars.
    """

    async def on_call_tool(
        self, context: MiddlewareContext, call_next: Any
    ) -> Any:
        # Extract API key from Authorization header
        headers = get_http_headers() or {}
        auth_header = headers.get("authorization", "")

        if not auth_header.startswith("Bearer mk_live_"):
            raise ToolError(
                "Authentication required. Provide an API key via "
                "Authorization: Bearer mk_live_... header."
            )

        raw_key = auth_header.removeprefix("Bearer ").strip()
        key_hash = hash_api_key(raw_key)

        # Resolve tenant + credentials
        tenant = await resolve_tenant_by_api_key(key_hash)
        if tenant is None:
            raise ToolError("Invalid API key.")

        # Check monthly usage limit
        plan_limit = tenant["max_monthly_calls"]
        current_usage = await get_monthly_usage_count(tenant["id"])
        if current_usage >= plan_limit:
            raise ToolError(
                f"Monthly call limit reached ({plan_limit:,} calls). "
                "Upgrade your plan at portal.statika.net/settings."
            )

        # Inject tenant credentials into contextvar
        creds = tenant["credentials"]
        creds["__tenant_id__"] = tenant["id"]
        creds["__api_key_id__"] = tenant["api_key_id"]
        creds["__plan_tier__"] = tenant["plan_tier"]

        token = _tenant_ctx.set(creds)
        try:
            return await call_next(context)
        finally:
            _tenant_ctx.reset(token)


class UsageLoggingMiddleware(Middleware):
    """Log every tool call to the usage_logs table (async, non-blocking)."""

    async def on_call_tool(
        self, context: MiddlewareContext, call_next: Any
    ) -> Any:
        tool_name = context.message.name
        start = time.perf_counter()
        success = True
        error_msg = None

        try:
            result = await call_next(context)
            return result
        except Exception as exc:
            success = False
            error_msg = str(exc)[:500]
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)

            # Read tenant info from contextvar (set by TenantAuthMiddleware)
            tenant_creds = _tenant_ctx.get()
            if tenant_creds is not None:
                tenant_id = tenant_creds.get("__tenant_id__")
                api_key_id = tenant_creds.get("__api_key_id__")
                if tenant_id:
                    try:
                        await log_usage(
                            tenant_id=tenant_id,
                            tool_name=tool_name,
                            api_key_id=api_key_id,
                            duration_ms=duration_ms,
                            success=success,
                            error_message=error_msg,
                        )
                    except Exception:
                        logger.warning(
                            "Failed to log usage for tool %s", tool_name
                        )
