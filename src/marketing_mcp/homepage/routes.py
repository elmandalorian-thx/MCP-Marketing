"""Homepage routes — sales page served at /."""

from marketing_mcp.homepage.templates import HOMEPAGE_HTML


def register_homepage_routes(mcp) -> None:  # noqa: ANN001
    """Register the public homepage route on the FastMCP server."""
    from starlette.requests import Request
    from starlette.responses import HTMLResponse

    @mcp.custom_route("/", methods=["GET"])
    async def homepage(request: Request) -> HTMLResponse:
        return HTMLResponse(HOMEPAGE_HTML)
