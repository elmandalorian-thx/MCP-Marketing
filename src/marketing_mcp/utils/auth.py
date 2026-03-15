"""Credential loading and validation helpers."""

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
}


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
