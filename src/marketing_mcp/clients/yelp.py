"""Yelp Fusion API — business reviews and local competitor research."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.yelp.com/v3"


@mcp.tool()
def yelp_business_search(
    term: str,
    location: str,
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search Yelp businesses — get ratings, review counts, categories, and pricing.

    Args:
        term: Search term (e.g. 'dentist', 'coffee shop')
        location: Location (e.g. 'Miami, FL')
        limit: Max results
        format: 'markdown' or 'json'
    """
    cache_key = f"yelp_search:{term}:{location}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("YELP_API_KEY")
    if not api_key:
        return "YELP_API_KEY not configured. Get one at https://www.yelp.com/developers/v3/manage_app"

    try:
        resp = httpx.get(
            f"{_API_URL}/businesses/search",
            params={"term": term, "location": location, "limit": limit},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        businesses = resp.json().get("businesses", [])

        if not businesses:
            return f"No Yelp businesses found for '{term}' in {location}."

        results = []
        for b in businesses:
            cats = ", ".join(c.get("title", "") for c in b.get("categories", []))
            results.append({
                "name": b.get("name", "")[:40],
                "rating": b.get("rating", "N/A"),
                "reviews": b.get("review_count", 0),
                "price": b.get("price", "N/A"),
                "categories": cats[:40],
                "phone": b.get("phone", ""),
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Yelp")


@mcp.tool()
def yelp_business_reviews(
    business_id: str,
    limit: int = 5,
    format: str = "markdown",
) -> str:
    """Get recent Yelp reviews for a specific business.

    Args:
        business_id: Yelp business ID or alias
        limit: Max reviews to return
        format: 'markdown' or 'json'
    """
    cache_key = f"yelp_reviews:{business_id}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("YELP_API_KEY")
    if not api_key:
        return "YELP_API_KEY not configured. Get one at https://www.yelp.com/developers/v3/manage_app"

    try:
        resp = httpx.get(
            f"{_API_URL}/businesses/{business_id}/reviews",
            params={"limit": limit, "sort_by": "newest"},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=15,
        )
        resp.raise_for_status()
        reviews = resp.json().get("reviews", [])

        if not reviews:
            return f"No reviews found for business '{business_id}'."

        results = []
        for r in reviews:
            results.append({
                "rating": r.get("rating", ""),
                "text": (r.get("text") or "")[:100],
                "user": r.get("user", {}).get("name", ""),
                "date": (r.get("time_created") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Yelp")
