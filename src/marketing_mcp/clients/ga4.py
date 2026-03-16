"""GA4 Data API — organic traffic performance tool."""

from datetime import datetime, timedelta

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential, get_google_service_credentials
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def ga4_organic_performance(
    property_id: str = "",
    days: int = 28,
    metrics: list[str] | None = None,
    dimensions: list[str] | None = None,
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """Get organic traffic metrics (sessions, engagement, bounce rate) from GA4."""
    if not property_id:
        property_id = get_credential("GA4_PROPERTY_ID") or ""
    if not property_id:
        return "GA4 property ID not provided and GA4_PROPERTY_ID not set."

    if metrics is None:
        metrics = ["sessions", "engagedSessions", "bounceRate"]
    if dimensions is None:
        dimensions = ["sessionDefaultChannelGroup"]

    cache_key = f"ga4:{property_id}:{days}:{','.join(metrics)}:{','.join(dimensions)}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    creds = get_google_service_credentials(
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    if creds is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )

        client = BetaAnalyticsDataClient(credentials=creds)

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[
                DateRange(
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                )
            ],
            metrics=[Metric(name=m) for m in metrics],
            dimensions=[Dimension(name=d) for d in dimensions],
            limit=limit,
        )

        response = client.run_report(request)

        if not response.rows:
            return f"No GA4 data for property {property_id} in the last {days} days."

        dim_headers = [h.name for h in response.dimension_headers]
        met_headers = [h.name for h in response.metric_headers]

        results = []
        for row in response.rows:
            entry = {}
            for i, dh in enumerate(dim_headers):
                entry[dh] = row.dimension_values[i].value
            for i, mh in enumerate(met_headers):
                entry[mh] = row.metric_values[i].value
            results.append(entry)

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "GA4")
