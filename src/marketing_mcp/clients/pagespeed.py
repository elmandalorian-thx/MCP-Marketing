"""PageSpeed Insights — site performance audit tool."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


@mcp.tool()
def pagespeed_audit(
    url: str,
    strategy: str = "mobile",
    format: str = "markdown",
) -> str:
    """Audit a URL's performance with Core Web Vitals and optimization tips."""
    cache_key = f"pagespeed:{url}:{strategy}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    params: dict = {"url": url, "strategy": strategy, "category": "performance"}
    api_key = get_credential("PAGESPEED_API_KEY")
    if api_key:
        params["key"] = api_key

    try:
        resp = httpx.get(_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return handle_api_error(exc, "PageSpeed Insights")

    lhr = data.get("lighthouseResult", {})
    categories = lhr.get("categories", {})
    audits = lhr.get("audits", {})

    score = categories.get("performance", {}).get("score")
    score_pct = int(score * 100) if score is not None else "N/A"

    metrics = {
        "url": url,
        "strategy": strategy,
        "performance_score": score_pct,
        "LCP_s": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
        "CLS": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
        "TBT_ms": audits.get("total-blocking-time", {}).get("displayValue", "N/A"),
        "FCP_s": audits.get("first-contentful-paint", {}).get("displayValue", "N/A"),
        "speed_index": audits.get("speed-index", {}).get("displayValue", "N/A"),
    }

    # Top opportunities
    opportunities = []
    for key, audit in audits.items():
        details = audit.get("details", {})
        if details.get("type") == "opportunity" and audit.get("score") is not None and audit["score"] < 1:
            savings = details.get("overallSavingsMs", 0)
            if savings > 0:
                opportunities.append({
                    "opportunity": audit.get("title", key),
                    "savings_ms": int(savings),
                })
    opportunities.sort(key=lambda x: x["savings_ms"], reverse=True)

    result_parts = [format_response(metrics, response_format=format)]
    if opportunities:
        result_parts.append("\n**Top Opportunities:**")
        result_parts.append(
            format_response(opportunities[:5], response_format=format)
        )

    result = "\n".join(result_parts)
    _cache.set(cache_key, result, KEYWORD_TTL)
    return result
