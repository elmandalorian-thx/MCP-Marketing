"""Pinterest API — pin search, board analytics, and interest targeting."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.pinterest.com/v5"


@mcp.tool()
def pinterest_search_pins(
    query: str,
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search Pinterest pins by topic — get pin titles, descriptions, links, and save counts.

    Args:
        query: Search query
        limit: Max pins to return
        format: 'markdown' or 'json'
    """
    cache_key = f"pinterest_search:{query}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("PINTEREST_ACCESS_TOKEN")
    if not token:
        return "PINTEREST_ACCESS_TOKEN not configured. Get one at https://developers.pinterest.com/"

    try:
        resp = httpx.get(
            f"{_API_URL}/search/pins",
            params={"query": query, "page_size": limit},
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        if not items:
            return f"No Pinterest pins found for '{query}'."

        results = []
        for pin in items:
            results.append({
                "title": (pin.get("title") or "")[:50],
                "description": (pin.get("description") or "")[:60],
                "link": pin.get("link", ""),
                "saves": pin.get("save_count", 0),
                "board": pin.get("board_id", ""),
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Pinterest")
