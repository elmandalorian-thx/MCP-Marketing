"""Credential loading and validation helpers."""

from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file if present
load_dotenv()

# Maps API name -> (required env vars, optional env vars)
CREDENTIAL_CONFIG: dict[str, tuple[list[str], list[str]]] = {
    "google_ads": (
        [
            "GOOGLE_ADS_CLIENT_ID",
            "GOOGLE_ADS_CLIENT_SECRET",
            "GOOGLE_ADS_REFRESH_TOKEN",
            "GOOGLE_ADS_DEVELOPER_TOKEN",
            "GOOGLE_ADS_CUSTOMER_ID",
        ],
        [],
    ),
    "search_console": (
        ["GOOGLE_SERVICE_ACCOUNT_JSON"],
        [],
    ),
    "ga4": (
        ["GOOGLE_SERVICE_ACCOUNT_JSON"],
        ["GA4_PROPERTY_ID"],
    ),
    "meta": (
        ["META_ACCESS_TOKEN"],
        [],
    ),
    "anthropic": (
        ["ANTHROPIC_API_KEY"],
        [],
    ),
    "youtube": (
        ["YOUTUBE_API_KEY"],
        [],
    ),
    "reddit": (
        ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"],
        [],
    ),
    "pagespeed": (
        [],
        ["PAGESPEED_API_KEY"],
    ),
    "google_business_profile": (
        ["GOOGLE_SERVICE_ACCOUNT_JSON"],
        ["GBP_ACCOUNT_ID", "GBP_LOCATION_ID"],
    ),
    "google_drive": (
        ["GOOGLE_SERVICE_ACCOUNT_JSON"],
        ["GDRIVE_FOLDER_ID"],
    ),
    "semrush": (
        ["SEMRUSH_API_KEY"],
        [],
    ),
    "linkedin": (
        ["LINKEDIN_ACCESS_TOKEN"],
        [],
    ),
    "bing_webmaster": (
        ["BING_WEBMASTER_API_KEY"],
        [],
    ),
    "mailchimp": (
        ["MAILCHIMP_API_KEY"],
        [],
    ),
    "tiktok": (
        ["TIKTOK_ACCESS_TOKEN"],
        [],
    ),
    "pinterest": (
        ["PINTEREST_ACCESS_TOKEN"],
        [],
    ),
    "x_twitter": (
        ["X_BEARER_TOKEN"],
        [],
    ),
    "shopify": (
        ["SHOPIFY_STORE_URL", "SHOPIFY_ACCESS_TOKEN"],
        [],
    ),
    "yelp": (
        ["YELP_API_KEY"],
        [],
    ),
    "hubspot": (
        ["HUBSPOT_ACCESS_TOKEN"],
        [],
    ),
    "builtwith": (
        [],
        [],
    ),
}


def get_google_service_credentials(
    scopes: list[str] | None = None,
):
    """Build Google service account credentials from GOOGLE_SERVICE_ACCOUNT_JSON.

    The env var can be a file path or a JSON string.
    Returns google.oauth2.service_account.Credentials or None.
    """
    sa_json = get_credential("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        return None

    from google.oauth2 import service_account

    if os.path.isfile(sa_json):
        return service_account.Credentials.from_service_account_file(
            sa_json, scopes=scopes
        )
    info = json.loads(sa_json)
    return service_account.Credentials.from_service_account_info(info, scopes=scopes)


def get_google_ads_client():
    """Build a GoogleAdsClient from environment variables. Returns None if unconfigured."""
    required = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
    ]
    if any(not get_credential(k) for k in required):
        return None

    from google.ads.googleads.client import GoogleAdsClient

    return GoogleAdsClient.load_from_dict(
        {
            "client_id": get_credential("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": get_credential("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": get_credential("GOOGLE_ADS_REFRESH_TOKEN"),
            "developer_token": get_credential("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "login_customer_id": get_credential("GOOGLE_ADS_CUSTOMER_ID"),
            "use_proto_plus": True,
        }
    )


def get_credential(name: str) -> str | None:
    """Get a credential value from environment variables.

    Returns None if the variable is not set. Never logs the value.
    """
    return os.environ.get(name)


def validate_credentials() -> list[str]:
    """Check which API integrations have valid credentials configured.

    Logs warnings for APIs with missing required credentials.
    Returns a list of API names that are fully configured.
    """
    available: list[str] = []

    for api_name, (required, optional) in CREDENTIAL_CONFIG.items():
        missing_required = [v for v in required if not os.environ.get(v)]
        missing_optional = [v for v in optional if not os.environ.get(v)]

        if missing_required:
            logger.debug(
                "%s: missing required credentials (%s)",
                api_name,
                ", ".join(missing_required),
            )
        else:
            available.append(api_name)

        if missing_optional:
            logger.debug(
                "%s: missing optional credentials (%s)",
                api_name,
                ", ".join(missing_optional),
            )

    return available


# ---------------------------------------------------------------------------
# Human-readable labels for each integration
# ---------------------------------------------------------------------------
INTEGRATION_LABELS: dict[str, str] = {
    "google_ads": "Google Ads",
    "search_console": "Search Console",
    "ga4": "GA4 Analytics",
    "meta": "Meta (Facebook)",
    "anthropic": "Anthropic (AI Agents)",
    "youtube": "YouTube",
    "reddit": "Reddit",
    "pagespeed": "PageSpeed Insights",
    "google_business_profile": "Google Business Profile",
    "google_drive": "Google Drive",
    "semrush": "Semrush",
    "linkedin": "LinkedIn",
    "bing_webmaster": "Bing Webmaster",
    "mailchimp": "Mailchimp",
    "tiktok": "TikTok Ads",
    "pinterest": "Pinterest",
    "x_twitter": "X (Twitter)",
    "shopify": "Shopify",
    "yelp": "Yelp",
    "hubspot": "HubSpot",
    "builtwith": "BuiltWith",
}


def get_credential_status() -> dict[str, dict]:
    """Return configuration status for every integration.

    Returns a dict like::

        {
            "google_ads": {
                "label": "Google Ads",
                "status": "configured",  # or "not_configured" or "partial"
                "required": {"GOOGLE_ADS_CLIENT_ID": True, ...},
                "optional": {"...": False},
            },
            ...
        }

    Values are never exposed — only True/False for "is set".
    """
    result: dict[str, dict] = {}
    for api_name, (required, optional) in CREDENTIAL_CONFIG.items():
        req_status = {v: bool(os.environ.get(v)) for v in required}
        opt_status = {v: bool(os.environ.get(v)) for v in optional}

        all_required_set = all(req_status.values()) if req_status else True
        any_required_set = any(req_status.values()) if req_status else False

        if all_required_set:
            status = "configured"
        elif any_required_set:
            status = "partial"
        else:
            status = "not_configured"

        result[api_name] = {
            "label": INTEGRATION_LABELS.get(api_name, api_name),
            "status": status,
            "required": req_status,
            "optional": opt_status,
        }
    return result


def update_env_file(updates: dict[str, str], env_path: str = ".env") -> None:
    """Write key=value pairs to the .env file.

    - Creates the file if it doesn't exist.
    - Updates existing keys in-place, preserving comments and order.
    - Appends new keys at the end.
    - Also updates ``os.environ`` so changes take effect immediately.
    """
    lines: list[str] = []
    updated_keys: set[str] = set()

    if os.path.isfile(env_path):
        with open(env_path) as f:
            lines = f.readlines()

    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        # Preserve comments and blank lines
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        key = stripped.split("=", 1)[0].strip()
        if key in updates:
            new_lines.append(f"{key}={updates[key]}\n")
            updated_keys.add(key)
        else:
            new_lines.append(line)

    # Append any keys not already in the file
    for key, value in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    # Update live environment
    for key, value in updates.items():
        if value:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
