"""Reddit API (PRAW) — topic research and community insights tool."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def reddit_topic_research(
    query: str,
    subreddit: str = "all",
    sort: str = "relevance",
    time_filter: str = "year",
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Search Reddit for posts about a topic with scores, comments, and top comment excerpts."""
    cache_key = f"reddit:{query}:{subreddit}:{sort}:{time_filter}:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    client_id = get_credential("REDDIT_CLIENT_ID")
    client_secret = get_credential("REDDIT_CLIENT_SECRET")
    user_agent = get_credential("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        return "Reddit credentials not configured. See .env.example."

    try:
        import praw

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        sub = reddit.subreddit(subreddit)
        posts = sub.search(query, sort=sort, time_filter=time_filter, limit=limit)

        results = []
        for post in posts:
            top_comment = ""
            if post.num_comments > 0:
                post.comment_sort = "best"
                post.comments.replace_more(limit=0)
                if post.comments:
                    top_comment = post.comments[0].body[:100]

            results.append({
                "title": post.title[:70],
                "subreddit": post.subreddit.display_name,
                "score": post.score,
                "comments": post.num_comments,
                "url": f"https://reddit.com{post.permalink}",
                "top_comment": top_comment,
            })

        if not results:
            return f"No Reddit posts found for '{query}'."

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Reddit")
