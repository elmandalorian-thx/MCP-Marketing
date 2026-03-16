"""Admin dashboard HTTP routes using FastMCP custom_route."""

from __future__ import annotations

import os
import platform
import time

from marketing_mcp.admin.templates import DASHBOARD_HTML
from marketing_mcp.utils.auth import (
    get_credential_status,
    update_env_file,
    validate_credentials,
)

_start_time = time.monotonic()


def register_admin_routes(mcp) -> None:  # noqa: ANN001
    """Register all /admin/* routes on the FastMCP server instance."""
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, JSONResponse

    @mcp.custom_route("/admin", methods=["GET"])
    async def admin_dashboard(request: Request) -> HTMLResponse:
        return HTMLResponse(DASHBOARD_HTML)

    @mcp.custom_route("/admin/credentials", methods=["GET"])
    async def get_credentials(request: Request) -> JSONResponse:
        return JSONResponse(get_credential_status())

    @mcp.custom_route("/admin/credentials", methods=["POST"])
    async def post_credentials(request: Request) -> JSONResponse:
        # Optional token auth
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse(
                    {"error": "Unauthorized"}, status_code=401
                )

        body = await request.json()
        if not isinstance(body, dict) or not body:
            return JSONResponse(
                {"error": "Provide a JSON object of {VAR: VALUE} pairs."},
                status_code=400,
            )

        env_path = os.path.join(os.getcwd(), ".env")
        update_env_file(body, env_path)

        return JSONResponse({
            "updated": list(body.keys()),
            "status": get_credential_status(),
        })

    @mcp.custom_route("/admin/test/{integration}", methods=["POST"])
    async def test_integration(request: Request) -> JSONResponse:
        integration = request.path_params["integration"]
        status = get_credential_status()

        if integration not in status:
            return JSONResponse(
                {"success": False, "message": f"Unknown integration: {integration}"},
                status_code=404,
            )

        info = status[integration]
        if info["status"] == "not_configured":
            return JSONResponse({
                "success": False,
                "message": f"{info['label']} has no credentials configured.",
            })

        # For integrations that require no auth or are fully configured, do a basic check
        available = validate_credentials()
        if integration in available or info["status"] == "configured":
            return JSONResponse({
                "success": True,
                "message": f"{info['label']} credentials are configured.",
            })

        missing = [k for k, v in info["required"].items() if not v]
        return JSONResponse({
            "success": False,
            "message": f"{info['label']} is missing: {', '.join(missing)}",
        })

    @mcp.custom_route("/admin/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        uptime_seconds = int(time.monotonic() - _start_time)
        available = validate_credentials()
        return JSONResponse({
            "status": "ok",
            "uptime_seconds": uptime_seconds,
            "python_version": platform.python_version(),
            "tools": 14,
            "integrations_configured": len(available),
            "integrations_total": len(get_credential_status()),
        })


def create_admin_app():
    """Create a standalone Starlette app for the admin dashboard.

    Used by ``marketing-mcp admin`` to run the dashboard independently
    of the MCP server transport.
    """
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import HTMLResponse, JSONResponse
    from starlette.routing import Route

    async def admin_dashboard(request: Request) -> HTMLResponse:
        return HTMLResponse(DASHBOARD_HTML)

    async def get_credentials(request: Request) -> JSONResponse:
        return JSONResponse(get_credential_status())

    async def post_credentials(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)

        body = await request.json()
        if not isinstance(body, dict) or not body:
            return JSONResponse(
                {"error": "Provide a JSON object of {VAR: VALUE} pairs."},
                status_code=400,
            )
        env_path = os.path.join(os.getcwd(), ".env")
        update_env_file(body, env_path)
        return JSONResponse({
            "updated": list(body.keys()),
            "status": get_credential_status(),
        })

    async def test_integration(request: Request) -> JSONResponse:
        integration = request.path_params["integration"]
        status = get_credential_status()
        if integration not in status:
            return JSONResponse(
                {"success": False, "message": f"Unknown integration: {integration}"},
                status_code=404,
            )
        info = status[integration]
        if info["status"] == "not_configured":
            return JSONResponse({
                "success": False,
                "message": f"{info['label']} has no credentials configured.",
            })
        available = validate_credentials()
        if integration in available or info["status"] == "configured":
            return JSONResponse({
                "success": True,
                "message": f"{info['label']} credentials are configured.",
            })
        missing = [k for k, v in info["required"].items() if not v]
        return JSONResponse({
            "success": False,
            "message": f"{info['label']} is missing: {', '.join(missing)}",
        })

    async def health_check(request: Request) -> JSONResponse:
        uptime_seconds = int(time.monotonic() - _start_time)
        available = validate_credentials()
        return JSONResponse({
            "status": "ok",
            "uptime_seconds": uptime_seconds,
            "python_version": platform.python_version(),
            "tools": 14,
            "integrations_configured": len(available),
            "integrations_total": len(get_credential_status()),
        })

    return Starlette(
        routes=[
            Route("/admin", admin_dashboard, methods=["GET"]),
            Route("/admin/credentials", get_credentials, methods=["GET"]),
            Route("/admin/credentials", post_credentials, methods=["POST"]),
            Route("/admin/test/{integration}", test_integration, methods=["POST"]),
            Route("/admin/health", health_check, methods=["GET"]),
        ],
    )
