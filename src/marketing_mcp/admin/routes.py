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
from marketing_mcp.utils.clients import load_clients, save_clients

_start_time = time.monotonic()

# Files the editor can read/write (relative to cwd)
EDITABLE_FILES = {"CLAUDE.md", ".env", "pyproject.toml", "clients.json"}


def _resolve_file(filename: str) -> str | None:
    if filename not in EDITABLE_FILES:
        return None
    return os.path.join(os.getcwd(), filename)


def _tool_count() -> int:
    """Count registered tools dynamically."""
    try:
        import asyncio
        from marketing_mcp.server import mcp as _mcp
        tools = asyncio.get_event_loop().run_until_complete(_mcp.list_tools())
        return len(tools)
    except Exception:
        return 32


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

    @mcp.custom_route("/admin/files/{filename}", methods=["GET"])
    async def read_file(request: Request) -> JSONResponse:
        filename = request.path_params["filename"]
        path = _resolve_file(filename)
        if not path:
            return JSONResponse(
                {"error": f"File not allowed: {filename}"}, status_code=403
            )
        try:
            with open(path) as f:
                content = f.read()
            return JSONResponse({"filename": filename, "content": content})
        except FileNotFoundError:
            return JSONResponse({"filename": filename, "content": ""})

    @mcp.custom_route("/admin/files/{filename}", methods=["PUT"])
    async def write_file(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)

        filename = request.path_params["filename"]
        path = _resolve_file(filename)
        if not path:
            return JSONResponse(
                {"error": f"File not allowed: {filename}"}, status_code=403
            )
        body = await request.json()
        content = body.get("content", "")
        with open(path, "w") as f:
            f.write(content)
        return JSONResponse({"filename": filename, "saved": True})

    # Client profiles
    @mcp.custom_route("/admin/clients", methods=["GET"])
    async def get_clients(request: Request) -> JSONResponse:
        return JSONResponse(load_clients())

    @mcp.custom_route("/admin/clients", methods=["POST"])
    async def save_client(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)

        body = await request.json()
        slug = body.get("slug", "").strip().lower().replace(" ", "_").replace("-", "_")
        if not slug:
            return JSONResponse({"error": "slug is required"}, status_code=400)

        clients = load_clients()
        profile = body.get("profile", {})
        profile["name"] = profile.get("name", slug)
        clients[slug] = profile
        save_clients(clients)
        return JSONResponse({"saved": slug, "clients": clients})

    @mcp.custom_route("/admin/clients/{slug}", methods=["DELETE"])
    async def delete_client(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)

        slug = request.path_params["slug"]
        clients = load_clients()
        if slug in clients:
            del clients[slug]
            save_clients(clients)
        return JSONResponse({"deleted": slug, "clients": clients})

    @mcp.custom_route("/admin/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        uptime_seconds = int(time.monotonic() - _start_time)
        available = validate_credentials()
        tool_count = _tool_count()
        return JSONResponse({
            "status": "ok",
            "uptime_seconds": uptime_seconds,
            "python_version": platform.python_version(),
            "tools": tool_count,
            "integrations_configured": len(available),
            "integrations_total": len(get_credential_status()),
        })


def create_admin_app():
    """Create a standalone Starlette app for the admin dashboard."""
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
        return JSONResponse({"updated": list(body.keys()), "status": get_credential_status()})

    async def test_integration(request: Request) -> JSONResponse:
        integration = request.path_params["integration"]
        status = get_credential_status()
        if integration not in status:
            return JSONResponse({"success": False, "message": f"Unknown integration: {integration}"}, status_code=404)
        info = status[integration]
        if info["status"] == "not_configured":
            return JSONResponse({"success": False, "message": f"{info['label']} has no credentials configured."})
        available = validate_credentials()
        if integration in available or info["status"] == "configured":
            return JSONResponse({"success": True, "message": f"{info['label']} credentials are configured."})
        missing = [k for k, v in info["required"].items() if not v]
        return JSONResponse({"success": False, "message": f"{info['label']} is missing: {', '.join(missing)}"})

    async def health_check(request: Request) -> JSONResponse:
        uptime_seconds = int(time.monotonic() - _start_time)
        available = validate_credentials()
        tool_count = _tool_count()
        return JSONResponse({
            "status": "ok", "uptime_seconds": uptime_seconds,
            "python_version": platform.python_version(), "tools": tool_count,
            "integrations_configured": len(available), "integrations_total": len(get_credential_status()),
        })

    async def read_file(request: Request) -> JSONResponse:
        filename = request.path_params["filename"]
        path = _resolve_file(filename)
        if not path:
            return JSONResponse({"error": f"File not allowed: {filename}"}, status_code=403)
        try:
            with open(path) as f:
                content = f.read()
            return JSONResponse({"filename": filename, "content": content})
        except FileNotFoundError:
            return JSONResponse({"filename": filename, "content": ""})

    async def write_file(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
        filename = request.path_params["filename"]
        path = _resolve_file(filename)
        if not path:
            return JSONResponse({"error": f"File not allowed: {filename}"}, status_code=403)
        body = await request.json()
        with open(path, "w") as f:
            f.write(body.get("content", ""))
        return JSONResponse({"filename": filename, "saved": True})

    async def get_clients(request: Request) -> JSONResponse:
        return JSONResponse(load_clients())

    async def save_client(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
        body = await request.json()
        slug = body.get("slug", "").strip().lower().replace(" ", "_").replace("-", "_")
        if not slug:
            return JSONResponse({"error": "slug is required"}, status_code=400)
        clients = load_clients()
        profile = body.get("profile", {})
        profile["name"] = profile.get("name", slug)
        clients[slug] = profile
        save_clients(clients)
        return JSONResponse({"saved": slug, "clients": clients})

    async def delete_client(request: Request) -> JSONResponse:
        admin_token = os.environ.get("ADMIN_TOKEN")
        if admin_token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {admin_token}":
                return JSONResponse({"error": "Unauthorized"}, status_code=401)
        slug = request.path_params["slug"]
        clients = load_clients()
        if slug in clients:
            del clients[slug]
            save_clients(clients)
        return JSONResponse({"deleted": slug, "clients": clients})

    return Starlette(
        routes=[
            Route("/admin", admin_dashboard, methods=["GET"]),
            Route("/admin/credentials", get_credentials, methods=["GET"]),
            Route("/admin/credentials", post_credentials, methods=["POST"]),
            Route("/admin/test/{integration}", test_integration, methods=["POST"]),
            Route("/admin/health", health_check, methods=["GET"]),
            Route("/admin/files/{filename}", read_file, methods=["GET"]),
            Route("/admin/files/{filename}", write_file, methods=["PUT"]),
            Route("/admin/clients", get_clients, methods=["GET"]),
            Route("/admin/clients", save_client, methods=["POST"]),
            Route("/admin/clients/{slug}", delete_client, methods=["DELETE"]),
        ],
    )
