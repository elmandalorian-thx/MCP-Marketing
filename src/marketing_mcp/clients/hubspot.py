"""HubSpot API — CRM contacts, deals, and marketing data."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.hubapi.com"


@mcp.tool()
def hubspot_contacts(
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """List recent HubSpot contacts with name, email, company, and lifecycle stage.

    Args:
        limit: Max contacts to return
        format: 'markdown' or 'json'
    """
    cache_key = f"hubspot_contacts:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("HUBSPOT_ACCESS_TOKEN")
    if not token:
        return "HUBSPOT_ACCESS_TOKEN not configured. Get one at https://developers.hubspot.com/"

    try:
        resp = httpx.get(
            f"{_API_URL}/crm/v3/objects/contacts",
            params={
                "limit": limit,
                "properties": "firstname,lastname,email,company,lifecyclestage,createdate",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        contacts = resp.json().get("results", [])

        if not contacts:
            return "No HubSpot contacts found."

        results = []
        for c in contacts:
            props = c.get("properties", {})
            results.append({
                "name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                "email": props.get("email", ""),
                "company": props.get("company", ""),
                "stage": props.get("lifecyclestage", ""),
                "created": (props.get("createdate") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "HubSpot")


@mcp.tool()
def hubspot_deals(
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """List recent HubSpot deals with stage, amount, close date, and owner.

    Args:
        limit: Max deals to return
        format: 'markdown' or 'json'
    """
    cache_key = f"hubspot_deals:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    token = get_credential("HUBSPOT_ACCESS_TOKEN")
    if not token:
        return "HUBSPOT_ACCESS_TOKEN not configured. Get one at https://developers.hubspot.com/"

    try:
        resp = httpx.get(
            f"{_API_URL}/crm/v3/objects/deals",
            params={
                "limit": limit,
                "properties": "dealname,amount,dealstage,closedate,pipeline",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        deals = resp.json().get("results", [])

        if not deals:
            return "No HubSpot deals found."

        results = []
        for d in deals:
            props = d.get("properties", {})
            results.append({
                "deal": props.get("dealname", "")[:40],
                "amount": props.get("amount", ""),
                "stage": props.get("dealstage", ""),
                "close_date": (props.get("closedate") or "")[:10],
                "pipeline": props.get("pipeline", ""),
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "HubSpot")
