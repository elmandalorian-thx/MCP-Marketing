"""Google Trends — interest and trending topic explorer (via pytrends)."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def google_trends_explorer(
    keywords: list[str],
    timeframe: str = "today 3-m",
    geo: str = "",
    format: str = "markdown",
) -> str:
    """Explore Google Trends interest over time and related queries for up to 5 keywords."""
    if len(keywords) > 5:
        return "Google Trends supports a maximum of 5 keywords per request."

    cache_key = f"trends:{','.join(sorted(keywords))}:{timeframe}:{geo}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)

        # Interest over time
        iot_df = pytrends.interest_over_time()
        parts = []

        if not iot_df.empty:
            # Summarize: latest values and averages
            summary = []
            for kw in keywords:
                if kw in iot_df.columns:
                    summary.append({
                        "keyword": kw,
                        "latest_interest": int(iot_df[kw].iloc[-1]),
                        "avg_interest": int(iot_df[kw].mean()),
                        "max_interest": int(iot_df[kw].max()),
                        "trend": "rising" if iot_df[kw].iloc[-1] > iot_df[kw].mean() else "declining",
                    })
            if summary:
                parts.append("**Interest Summary:**")
                parts.append(format_response(summary, response_format=format))

        # Related queries
        related = pytrends.related_queries()
        for kw in keywords:
            kw_data = related.get(kw, {})
            rising = kw_data.get("rising")
            if rising is not None and not rising.empty:
                rows = rising.head(5).to_dict("records")
                parts.append(f"\n**Rising queries for '{kw}':**")
                parts.append(format_response(rows, response_format=format))

        if not parts:
            return f"No trends data found for {', '.join(keywords)}."

        result = "\n".join(parts)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Trends")
