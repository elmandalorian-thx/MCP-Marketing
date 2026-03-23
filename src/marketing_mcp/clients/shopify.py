"""Shopify Admin API — store analytics and product data."""

import httpx

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import KEYWORD_TTL, TTLCache
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()


@mcp.tool()
def shopify_products(
    limit: int = 20,
    format: str = "markdown",
) -> str:
    """List Shopify products with titles, prices, inventory status, and variants.

    Args:
        limit: Max products to return
        format: 'markdown' or 'json'
    """
    cache_key = f"shopify_products:{limit}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    store = get_credential("SHOPIFY_STORE_URL")
    token = get_credential("SHOPIFY_ACCESS_TOKEN")
    if not store or not token:
        return "SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN not configured. Get credentials at https://admin.shopify.com/store/YOUR_STORE/settings/apps/development"

    try:
        url = f"https://{store}/admin/api/2024-01/products.json"
        resp = httpx.get(
            url,
            params={"limit": limit},
            headers={"X-Shopify-Access-Token": token},
            timeout=15,
        )
        resp.raise_for_status()
        products = resp.json().get("products", [])

        if not products:
            return "No Shopify products found."

        results = []
        for p in products:
            variant = p.get("variants", [{}])[0]
            results.append({
                "title": p.get("title", "")[:50],
                "status": p.get("status", ""),
                "price": variant.get("price", ""),
                "inventory": variant.get("inventory_quantity", "N/A"),
                "vendor": p.get("vendor", ""),
                "type": p.get("product_type", ""),
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Shopify")


@mcp.tool()
def shopify_orders(
    limit: int = 20,
    status: str = "any",
    format: str = "markdown",
) -> str:
    """Get recent Shopify orders with totals, fulfillment status, and customer info.

    Args:
        limit: Max orders to return
        status: Filter by status — 'open', 'closed', 'cancelled', 'any'
        format: 'markdown' or 'json'
    """
    cache_key = f"shopify_orders:{limit}:{status}"
    cached = _cache.get(cache_key)
    if cached:
        return cached

    store = get_credential("SHOPIFY_STORE_URL")
    token = get_credential("SHOPIFY_ACCESS_TOKEN")
    if not store or not token:
        return "SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN not configured."

    try:
        url = f"https://{store}/admin/api/2024-01/orders.json"
        resp = httpx.get(
            url,
            params={"limit": limit, "status": status},
            headers={"X-Shopify-Access-Token": token},
            timeout=15,
        )
        resp.raise_for_status()
        orders = resp.json().get("orders", [])

        if not orders:
            return "No Shopify orders found."

        results = []
        for o in orders:
            results.append({
                "order": o.get("name", ""),
                "total": o.get("total_price", ""),
                "currency": o.get("currency", ""),
                "status": o.get("financial_status", ""),
                "fulfillment": o.get("fulfillment_status", "unfulfilled"),
                "date": (o.get("created_at") or "")[:10],
            })

        result = format_response(results, response_format=format)
        _cache.set(cache_key, result, KEYWORD_TTL)
        return result

    except Exception as exc:
        return handle_api_error(exc, "Shopify")
