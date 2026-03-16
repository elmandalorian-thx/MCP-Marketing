"""Google Business Profile API — local business insights and reviews tool."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential, get_google_service_credentials
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_SCOPES = ["https://www.googleapis.com/auth/business.manage"]


@mcp.tool()
def gbp_insights(
    location_id: str = "",
    account_id: str = "",
    days: int = 28,
    format: str = "markdown",
) -> str:
    """Get Google Business Profile reviews and performance metrics for a location."""
    if not location_id:
        location_id = get_credential("GBP_LOCATION_ID") or ""
    if not account_id:
        account_id = get_credential("GBP_ACCOUNT_ID") or ""
    if not location_id or not account_id:
        return "GBP_ACCOUNT_ID and GBP_LOCATION_ID must be set. See .env.example."

    cache_key = f"gbp:{account_id}:{location_id}:{days}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    creds = get_google_service_credentials(scopes=_SCOPES)
    if creds is None:
        return "Google service account not configured. Set GOOGLE_SERVICE_ACCOUNT_JSON."

    try:
        from googleapiclient.discovery import build

        location_name = f"locations/{location_id}"

        # Use the Account Management API for reviews
        review_service = build("mybusinessreviews", "v1", credentials=creds)
        reviews_resp = (
            review_service.accounts()
            .locations()
            .reviews()
            .list(parent=f"accounts/{account_id}/{location_name}", pageSize=10)
            .execute()
        )

        parts = []

        reviews = reviews_resp.get("reviews", [])
        if reviews:
            review_data = []
            for r in reviews[:10]:
                reviewer = r.get("reviewer", {})
                review_data.append({
                    "rating": r.get("starRating", "N/A"),
                    "comment": (r.get("comment", "") or "")[:80],
                    "reviewer": reviewer.get("displayName", "Anonymous"),
                    "date": r.get("createTime", "")[:10],
                })
            parts.append("**Recent Reviews:**")
            parts.append(format_response(review_data, response_format=format))

            avg_rating = sum(
                {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}.get(
                    r.get("starRating", ""), 0
                )
                for r in reviews
            ) / len(reviews)
            parts.append(f"\n**Average Rating:** {avg_rating:.1f}/5 ({len(reviews)} reviews shown)")
        else:
            parts.append("No reviews found.")

        if not parts:
            return f"No data found for location {location_id}."

        result = "\n".join(parts)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Google Business Profile")
