"""Google Ads Keyword Planner — keyword research tool."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential, get_google_ads_client
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def gads_keyword_ideas(
    seed_keywords: list[str],
    language_id: str = "1000",
    location_id: str = "2840",
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """Get keyword ideas with search volume, competition, and bid estimates from Google Ads."""
    cache_key = f"gads:{','.join(sorted(seed_keywords))}:{location_id}:{language_id}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    client = get_google_ads_client()
    if client is None:
        return "Google Ads credentials not configured. See .env.example."

    customer_id = get_credential("GOOGLE_ADS_CUSTOMER_ID")
    if not customer_id:
        return "GOOGLE_ADS_CUSTOMER_ID not set."

    try:
        kp_service = client.get_service("KeywordPlanIdeaService")
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = f"languageConstants/{language_id}"
        request.geo_target_constants = [f"geoTargetConstants/{location_id}"]
        request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
        request.keyword_seed.keywords.extend(seed_keywords)

        response = kp_service.generate_keyword_ideas(request=request)

        results = []
        for idx, idea in enumerate(response):
            if idx >= limit:
                break
            metrics = idea.keyword_idea_metrics
            results.append({
                "keyword": idea.text,
                "avg_monthly_searches": metrics.avg_monthly_searches,
                "competition": metrics.competition.name,
                "low_bid": f"${metrics.low_top_of_page_bid_micros / 1_000_000:.2f}" if metrics.low_top_of_page_bid_micros else "N/A",
                "high_bid": f"${metrics.high_top_of_page_bid_micros / 1_000_000:.2f}" if metrics.high_top_of_page_bid_micros else "N/A",
            })

        if not results:
            return "No keyword ideas found for the given seeds."

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Ads")
