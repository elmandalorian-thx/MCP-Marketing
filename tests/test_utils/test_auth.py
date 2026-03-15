"""Tests for credential validation and loading."""

from marketing_mcp.utils.auth import get_credential, validate_credentials


def test_validate_credentials_none_configured(clean_env):
    """With no env vars set, no APIs should be available."""
    available = validate_credentials()
    # Only pagespeed has no required vars, so it's always available
    assert "google_ads" not in available
    assert "meta" not in available


def test_validate_credentials_google_ads(clean_env, mock_google_ads_env):
    """Google Ads should be available when all required vars are set."""
    available = validate_credentials()
    assert "google_ads" in available


def test_validate_credentials_partial(clean_env, monkeypatch):
    """Partially configured API should not be available."""
    monkeypatch.setenv("GOOGLE_ADS_CLIENT_ID", "test")
    # Missing other required vars
    available = validate_credentials()
    assert "google_ads" not in available


def test_get_credential_exists(monkeypatch):
    """get_credential returns the value when set."""
    monkeypatch.setenv("TEST_CRED", "secret-value")
    assert get_credential("TEST_CRED") == "secret-value"


def test_get_credential_missing():
    """get_credential returns None when not set."""
    assert get_credential("DEFINITELY_NOT_SET_12345") is None


def test_pagespeed_always_available(clean_env):
    """Pagespeed has no required vars, so it's always available."""
    available = validate_credentials()
    assert "pagespeed" in available
