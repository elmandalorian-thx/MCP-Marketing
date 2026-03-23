"""TikTok Marketing API — ad audience and interest research."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import AUDIENCE_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://business-api.tiktok.com/open_api/v1.3"


@mcp.tool()
def tiktok_interest_targeting(
    advertiser_id: str,
    format: str = "markdown",
) -> str:
    """Get TikTok Ads interest categories for audience targeting research.

    Args:
        advertiser_id: Your TikTok Ads advertiser ID
        format: 'markdown' or 'json'
    """
    cache_key = f"tiktok_interests:{advertiser_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("TIKTOK_ACCESS_TOKEN")
    if not token:
        return "TIKTOK_ACCESS_TOKEN not configured. Get one at https://business-api.tiktok.com/"

    try:
        resp = httpx.get(
            f"{_API_URL}/tool/interest_category/",
            params={"advertiser_id": advertiser_id},
            headers={"Access-Token": token},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        categories = data.get("data", {}).get("interest_categories", [])
        if not categories:
            return "No TikTok interest categories returned."

        results = []
        for cat in categories[:30]:
            results.append({
                "name": cat.get("name", ""),
                "id": cat.get("interest_category_id", ""),
                "level": cat.get("level", ""),
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, AUDIENCE_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "TikTok")
