"""Shared test fixtures."""

import pytest


@pytest.fixture()
def clean_env(monkeypatch):
    """Remove all marketing credential env vars for isolated testing."""
    credential_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CUSTOMER_ID",
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "GA4_PROPERTY_ID",
        "META_ACCESS_TOKEN",
        "ANTHROPIC_API_KEY",
        "YOUTUBE_API_KEY",
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "PAGESPEED_API_KEY",
    ]
    for var in credential_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture()
def mock_google_ads_env(monkeypatch):
    """Set up mock Google Ads credentials."""
    monkeypatch.setenv("GOOGLE_ADS_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_ADS_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("GOOGLE_ADS_REFRESH_TOKEN", "test-refresh")
    monkeypatch.setenv("GOOGLE_ADS_DEVELOPER_TOKEN", "test-dev-token")
    monkeypatch.setenv("GOOGLE_ADS_CUSTOMER_ID", "123-456-7890")
