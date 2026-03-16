"""Meta Graph API — interest targeting and audience research tool."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import AUDIENCE_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_GRAPH_URL = "https://graph.facebook.com/v21.0"


@mcp.tool()
def meta_interest_targeting(
    query: str,
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search Meta ad interests and get audience size estimates for a topic."""
    cache_key = f"meta_interest:{query}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("META_ACCESS_TOKEN")
    if not token:
        return "META_ACCESS_TOKEN not configured. See .env.example."

    try:
        resp = httpx.get(
            f"{_GRAPH_URL}/search",
            params={
                "type": "adinterest",
                "q": query,
                "limit": limit,
                "access_token": token,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

        if not data:
            return f"No Meta interests found for '{query}'."

        results = []
        for item in data:
            results.append({
                "name": item.get("name", ""),
                "audience_size": item.get("audience_size_upper_bound", "N/A"),
                "topic": item.get("topic", ""),
                "description": (item.get("description", "") or "")[:80],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, AUDIENCE_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Meta")
