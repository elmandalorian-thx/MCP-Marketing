"""Main MCP server initialization and entry point."""

import argparse
import logging

from fastmcp import FastMCP

from marketing_mcp.utils.auth import validate_credentials

logger = logging.getLogger(__name__)

mcp = FastMCP("marketing_mcp")

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


def main() -> None:
    """Run the Marketing MCP server."""
    parser = argparse.ArgumentParser(description="Marketing MCP Server")
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
    args = parser.parse_args()

    # Validate credentials on startup (warns but doesn't fail)
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
