"""Mailchimp API — email campaign metrics and audience data."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


def _get_api_url() -> str | None:
    api_key = get_credential("MAILCHIMP_API_KEY")
    if not api_key:
        return None
    dc = api_key.split("-")[-1] if "-" in api_key else "us1"
    return f"https://{dc}.api.mailchimp.com/3.0"


@mcp.tool()
def mailchimp_campaigns(
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Get recent Mailchimp email campaigns with open rates, click rates, and send counts.

    Args:
        limit: Number of campaigns to return
        format: 'markdown' or 'json'
    """
    cache_key = f"mailchimp_campaigns:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("MAILCHIMP_API_KEY")
    api_url = _get_api_url()
    if not api_key or not api_url:
        return "MAILCHIMP_API_KEY not configured. Get one at https://mailchimp.com/developer/"

    try:
        resp = httpx.get(
            f"{api_url}/campaigns",
            params={"count": limit, "sort_field": "send_time", "sort_dir": "DESC"},
            auth=("anystring", api_key),
            timeout=15,
        )
        resp.raise_for_status()
        campaigns = resp.json().get("campaigns", [])

        if not campaigns:
            return "No Mailchimp campaigns found."

        results = []
        for c in campaigns:
            report = c.get("report_summary", {})
            results.append({
                "campaign": c.get("settings", {}).get("subject_line", "")[:50],
                "status": c.get("status", ""),
                "sent": c.get("emails_sent", 0),
                "open_rate": f"{report.get('open_rate', 0):.1%}",
                "click_rate": f"{report.get('click_rate', 0):.1%}",
                "send_time": (c.get("send_time") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Mailchimp")


@mcp.tool()
def mailchimp_audiences(
    format: str = "markdown",
) -> str:
    """List Mailchimp audiences (lists) with subscriber counts and stats."""
    cache_key = "mailchimp_audiences"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("MAILCHIMP_API_KEY")
    api_url = _get_api_url()
    if not api_key or not api_url:
        return "MAILCHIMP_API_KEY not configured. Get one at https://mailchimp.com/developer/"

    try:
        resp = httpx.get(
            f"{api_url}/lists",
            params={"count": 20},
            auth=("anystring", api_key),
            timeout=15,
        )
        resp.raise_for_status()
        lists = resp.json().get("lists", [])

        if not lists:
            return "No Mailchimp audiences found."

        results = []
        for lst in lists:
            stats = lst.get("stats", {})
            results.append({
                "audience": lst.get("name", ""),
                "subscribers": stats.get("member_count", 0),
                "open_rate": f"{stats.get('open_rate', 0):.1%}",
                "click_rate": f"{stats.get('click_rate', 0):.1%}",
                "last_sent": (stats.get("campaign_last_sent") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Mailchimp")
