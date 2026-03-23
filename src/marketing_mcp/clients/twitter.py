"""X (Twitter) API v2 — tweet search and social listening."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.x.com/2"


@mcp.tool()
def x_search_recent(
    query: str,
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search recent tweets/posts on X (Twitter) — get text, likes, retweets, and impression counts.

    Args:
        query: Search query (supports X search operators)
        limit: Max results (10-100)
        format: 'markdown' or 'json'
    """
    cache_key = f"x_search:{query}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    bearer = get_credential("X_BEARER_TOKEN")
    if not bearer:
        return "X_BEARER_TOKEN not configured. Get one at https://developer.x.com/en/portal/dashboard"

    try:
        resp = httpx.get(
            f"{_API_URL}/tweets/search/recent",
            params={
                "query": query,
                "max_results": min(limit, 100),
                "tweet.fields": "created_at,public_metrics,author_id",
            },
            headers={"Authorization": f"Bearer {bearer}"},
            timeout=15,
        )
        resp.raise_for_status()
        tweets = resp.json().get("data", [])

        if not tweets:
            return f"No recent X posts found for '{query}'."

        results = []
        for tw in tweets:
            metrics = tw.get("public_metrics", {})
            results.append({
                "text": tw.get("text", "")[:80],
                "likes": metrics.get("like_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "replies": metrics.get("reply_count", 0),
                "impressions": metrics.get("impression_count", 0),
                "date": (tw.get("created_at") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "X (Twitter)")
