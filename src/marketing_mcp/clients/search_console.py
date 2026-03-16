"""Google Search Console — search query performance tool."""

from datetime import datetime, timedelta

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_google_service_credentials
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


@mcp.tool()
def gsc_search_queries(
    site_url: str,
    days: int = 28,
    dimensions: list[str] | None = None,
    row_limit: int = 20,
    format: str = "markdown",
) -> str:
    """Get search query performance (clicks, impressions, CTR, position) from Google Search Console."""
    if dimensions is None:
        dimensions = ["query"]

    cache_key = f"gsc:{site_url}:{days}:{','.join(dimensions)}:{row_limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    creds = get_google_service_credentials(scopes=_SCOPES)
    if creds is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        from googleapiclient.discovery import build

        service = build("searchconsole", "v1", credentials=creds)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        body = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }

        response = (
            service.searchanalytics()
            .query(siteUrl=site_url, body=body)
            .execute()
        )

        rows = response.get("rows", [])
        if not rows:
            return f"No search data found for {site_url} in the last {days} days."

        results = []
        for row in rows:
            entry = {}
            for i, dim in enumerate(dimensions):
                entry[dim] = row["keys"][i]
            entry["clicks"] = row.get("clicks", 0)
            entry["impressions"] = row.get("impressions", 0)
            entry["ctr"] = f"{row.get('ctr', 0):.1%}"
            entry["position"] = f"{row.get('position', 0):.1f}"
            results.append(entry)

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Search Console")
