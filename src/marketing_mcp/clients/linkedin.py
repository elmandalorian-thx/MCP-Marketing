"""LinkedIn Marketing API — company pages and ad targeting research."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import AUDIENCE_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.linkedin.com/v2"


@mcp.tool()
def linkedin_ad_targeting(
    query: str,
    facet: str = "industries",
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search LinkedIn ad targeting facets — industries, job titles, skills, and company sizes.

    Args:
        query: Search term for targeting options
        facet: Facet type — 'industries', 'titles', 'skills', 'seniorities'
        limit: Max results
        format: 'markdown' or 'json'
    """
    cache_key = f"linkedin_targeting:{query}:{facet}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("LINKEDIN_ACCESS_TOKEN")
    if not token:
        return "LINKEDIN_ACCESS_TOKEN not configured. Get one at https://www.linkedin.com/developers/"

    try:
        resp = httpx.get(
            f"{_API_URL}/adTargetingEntities",
            params={"q": "typeahead", "query": query, "facet": f"urn:li:{facet}", "count": limit},
            headers={"Authorization": f"Bearer {token}", "X-Restli-Protocol-Version": "2.0.0"},
            timeout=15,
        )
        resp.raise_for_status()
        elements = resp.json().get("elements", [])

        if not elements:
            return f"No LinkedIn targeting options found for '{query}' in {facet}."

        results = []
        for el in elements[:limit]:
            results.append({
                "name": el.get("name", ""),
                "urn": el.get("urn", ""),
                "facet": facet,
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, AUDIENCE_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "LinkedIn")
