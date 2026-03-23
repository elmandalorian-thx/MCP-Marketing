"""Main MCP server initialization and entry point."""

import argparse
import logging
import os

from fastmcp import FastMCP

from marketing_mcp.utils.auth import validate_credentials

logger = logging.getLogger(__name__)

mcp = FastMCP("marketing_mcp")

# ── Multi-tenant mode (opt-in via MULTI_TENANT=true) ──
_MULTI_TENANT = os.environ.get("MULTI_TENANT", "").lower() == "true"

if _MULTI_TENANT:
    from marketing_mcp.multi_tenant.middleware import (  # noqa: E402
        TenantAuthMiddleware,
        UsageLoggingMiddleware,
    )

    mcp.add_middleware(TenantAuthMiddleware())
    mcp.add_middleware(UsageLoggingMiddleware())
    logger.info("Multi-tenant mode enabled — API key auth required.")

# Register all Tier 1 tool modules (decorators bind to `mcp` on import)
import marketing_mcp.clients.pagespeed  # noqa: E402, F401
import marketing_mcp.clients.google_ads  # noqa: E402, F401
import marketing_mcp.clients.search_console  # noqa: E402, F401
import marketing_mcp.clients.ga4  # noqa: E402, F401
import marketing_mcp.clients.meta  # noqa: E402, F401
import marketing_mcp.clients.google_trends  # noqa: E402, F401
import marketing_mcp.clients.youtube  # noqa: E402, F401
import marketing_mcp.clients.reddit  # noqa: E402, F401
import marketing_mcp.clients.google_business  # noqa: E402, F401
import marketing_mcp.clients.google_drive  # noqa: E402, F401
import marketing_mcp.clients.client_profiles  # noqa: E402, F401
import marketing_mcp.clients.semrush  # noqa: E402, F401
import marketing_mcp.clients.linkedin  # noqa: E402, F401
import marketing_mcp.clients.bing_webmaster  # noqa: E402, F401
import marketing_mcp.clients.mailchimp  # noqa: E402, F401
import marketing_mcp.clients.tiktok  # noqa: E402, F401
import marketing_mcp.clients.pinterest  # noqa: E402, F401
import marketing_mcp.clients.twitter  # noqa: E402, F401
import marketing_mcp.clients.shopify  # noqa: E402, F401
import marketing_mcp.clients.yelp  # noqa: E402, F401
import marketing_mcp.clients.builtwith  # noqa: E402, F401
import marketing_mcp.clients.hubspot  # noqa: E402, F401

# Register prompt library and generator tools
import marketing_mcp.prompts.tools  # noqa: E402, F401
import marketing_mcp.prompts.mcp_prompts  # noqa: E402, F401

# Register admin dashboard routes (available in HTTP mode)
from marketing_mcp.admin.routes import register_admin_routes  # noqa: E402
from marketing_mcp.homepage.routes import register_homepage_routes  # noqa: E402

register_admin_routes(mcp)
register_homepage_routes(mcp)


def main() -> None:
    """Run the Marketing MCP server."""
    parser = argparse.ArgumentParser(description="Marketing MCP Server")
    subparsers = parser.add_subparsers(dest="command")

    # Default: run the MCP server
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)",
    )

    # Subcommand: setup
    subparsers.add_parser("setup", help="Interactive credential setup wizard")

    # Subcommand: admin
    admin_parser = subparsers.add_parser(
        "admin", help="Launch admin dashboard web UI"
    )
    admin_parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port for admin dashboard (default: 8001)",
    )
    admin_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for admin dashboard (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    if args.command == "setup":
        from marketing_mcp.cli_setup import run_setup

        run_setup()
        return

    if args.command == "admin":
        import uvicorn

        from marketing_mcp.admin.routes import create_admin_app

        app = create_admin_app()
        print(f"Admin dashboard: http://{args.host}:{args.port}/admin")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return

    # Default: run MCP server
    available = validate_credentials()
    if available:
        logger.info("Available API integrations: %s", ", ".join(available))
    else:
        logger.warning("No API credentials configured. See .env.example for setup.")

    if args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
