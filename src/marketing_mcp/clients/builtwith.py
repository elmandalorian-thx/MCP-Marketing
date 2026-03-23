"""BuiltWith — technology stack detection for competitor analysis."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def builtwith_lookup(
    domain: str,
    format: str = "markdown",
) -> str:
    """Detect the technology stack of any website — CMS, analytics, ads, frameworks, and hosting.

    Uses the free BuiltWith API. No API key required.

    Args:
        domain: Domain to analyze (e.g. 'example.com')
        format: 'markdown' or 'json'
    """
    cache_key = f"builtwith:{domain}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    try:
        resp = httpx.get(
            f"https://api.builtwith.com/free1/api.json",
            params={"KEY": "free", "LOOKUP": domain},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        groups = data.get("groups", [])
        if not groups:
            return f"No technology data found for '{domain}'."

        results = []
        for group in groups:
            group_name = group.get("name", "")
            for cat in group.get("categories", []):
                for tech in cat.get("live", []):
                    results.append({
                        "group": group_name,
                        "category": cat.get("name", ""),
                        "technology": tech.get("Name", ""),
                        "link": tech.get("Link", ""),
                    })

        if not results:
            return f"No technologies detected for '{domain}'."

        result = format_response(results[:30], response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "BuiltWith")
