"""YouTube Data API v3 — topic and video research tool."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def youtube_topic_research(
    query: str,
    max_results: int = 10,
    order: str = "relevance",
    format: str = "markdown",
) -> str:
    """Search YouTube videos for a topic and get view counts, likes, and engagement data."""
    cache_key = f"youtube:{query}:{max_results}:{order}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("YOUTUBE_API_KEY")
    if not api_key:
        return "YOUTUBE_API_KEY not configured. See .env.example."

    try:
        from googleapiclient.discovery import build

        youtube = build("youtube", "v3", developerKey=api_key)

        search_resp = (
            youtube.search()
            .list(q=query, part="snippet", type="video", maxResults=max_results, order=order)
            .execute()
        )

        video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
        if not video_ids:
            return f"No YouTube videos found for '{query}'."

        # Fetch statistics for each video
        stats_resp = (
            youtube.videos()
            .list(id=",".join(video_ids), part="statistics,snippet")
            .execute()
        )

        results = []
        for item in stats_resp.get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            results.append({
                "title": snippet["title"][:60],
                "channel": snippet["channelTitle"],
                "views": _fmt_number(stats.get("viewCount", "0")),
                "likes": _fmt_number(stats.get("likeCount", "0")),
                "published": snippet["publishedAt"][:10],
                "url": f"https://youtu.be/{item['id']}",
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "YouTube")


def _fmt_number(n: str) -> str:
    """Format a number string with commas."""
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return n
