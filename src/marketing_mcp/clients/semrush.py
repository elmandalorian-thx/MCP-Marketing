"""Semrush API — domain analytics, keyword research, and backlink data."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()
_API_URL = "https://api.semrush.com"


@mcp.tool()
def semrush_domain_overview(
    domain: str,
    database: str = "us",
    limit: int = 10,
    format: str = "markdown",
) -> str:
    """Get domain analytics overview from Semrush — organic traffic, keywords, and top pages.

    Args:
        domain: Domain to analyze (e.g. 'example.com')
        database: Country database code (us, uk, de, etc.)
        limit: Max results to return
        format: 'markdown' or 'json'
    """
    cache_key = f"semrush_domain:{domain}:{database}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("SEMRUSH_API_KEY")
    if not api_key:
        return "SEMRUSH_API_KEY not configured. Get one at https://www.semrush.com/api/"

    try:
        resp = httpx.get(
            _API_URL,
            params={
                "type": "domain_ranks",
                "key": api_key,
                "export_columns": "Dn,Rk,Or,Ot,Oc,Ad,At,Ac",
                "domain": domain,
                "database": database,
            },
            timeout=20,
        )
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        if len(lines) < 2:
            return f"No Semrush data found for '{domain}'."

        headers = lines[0].split(";")
        values = lines[1].split(";")
        col_map = {
            "Dn": "domain", "Rk": "rank", "Or": "organic_keywords",
            "Ot": "organic_traffic", "Oc": "organic_cost",
            "Ad": "paid_keywords", "At": "paid_traffic", "Ac": "paid_cost",
        }
        result_data = {}
        for h, v in zip(headers, values):
            label = col_map.get(h, h)
            result_data[label] = v

        result = format_response(result_data, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Semrush")


@mcp.tool()
def semrush_keyword_overview(
    keyword: str,
    database: str = "us",
    format: str = "markdown",
) -> str:
    """Get keyword metrics from Semrush — volume, difficulty, CPC, and SERP features.

    Args:
        keyword: Keyword to research
        database: Country database code (us, uk, de, etc.)
        format: 'markdown' or 'json'
    """
    cache_key = f"semrush_kw:{keyword}:{database}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    api_key = get_credential("SEMRUSH_API_KEY")
    if not api_key:
        return "SEMRUSH_API_KEY not configured. Get one at https://www.semrush.com/api/"

    try:
        resp = httpx.get(
            _API_URL,
            params={
                "type": "phrase_all",
                "key": api_key,
                "export_columns": "Ph,Nq,Cp,Co,Nr",
                "phrase": keyword,
                "database": database,
            },
            timeout=20,
        )
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        if len(lines) < 2:
            return f"No Semrush data found for '{keyword}'."

        headers = lines[0].split(";")
        values = lines[1].split(";")
        col_map = {
            "Ph": "keyword", "Nq": "search_volume", "Cp": "cpc",
            "Co": "competition", "Nr": "results",
        }
        result_data = {}
        for h, v in zip(headers, values):
            label = col_map.get(h, h)
            result_data[label] = v

        result = format_response(result_data, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Semrush")
