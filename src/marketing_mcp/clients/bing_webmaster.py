"""Bing Webmaster Tools API — search performance and keyword data."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://ssl.bing.com/webmaster/api.svc/json"


@mcp.tool()
def bing_search_queries(
    site_url: str,
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """Get Bing search query data — impressions, clicks, CTR, and position for your site.

    Args:
        site_url: Your site URL as registered in Bing Webmaster Tools
        limit: Max queries to return
        format: 'markdown' or 'json'
    """
    cache_key = f"bing_queries:{site_url}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("BING_WEBMASTER_API_KEY")
    if not api_key:
        return "BING_WEBMASTER_API_KEY not configured. Get one at https://www.bing.com/webmasters/"

    try:
        resp = httpx.get(
            f"{_API_URL}/GetQueryStats",
            params={"siteUrl": site_url, "apikey": api_key},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json().get("d", [])

        if not data:
            return f"No Bing search data found for '{site_url}'."

        results = []
        for item in data[:limit]:
            results.append({
                "query": item.get("Query", ""),
                "impressions": item.get("Impressions", 0),
                "clicks": item.get("Clicks", 0),
                "ctr": f"{item.get('AvgCTR', 0):.1%}",
                "position": f"{item.get('AvgPosition', 0):.1f}",
                "date": item.get("Date", "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Bing Webmaster")
