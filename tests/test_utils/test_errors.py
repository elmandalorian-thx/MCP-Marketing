"""Tests for error handling."""

from marketing_mcp.utils.errors import handle_api_error


def test_permission_error():
    result = handle_api_error(PermissionError("forbidden"), "Google Ads")
    assert "Permission denied" in result
    assert "Google Ads" in result


def test_403_in_message():
    result = handle_api_error(Exception("HTTP 403 Forbidden"), "Meta")
    assert "Permission denied" in result


def test_404_not_found():
    result = handle_api_error(Exception("404 Not Found"), "GA4")
    assert "not found" in result.lower()


def test_429_rate_limit():
    result = handle_api_error(Exception("429 Too Many Requests"), "GSC")
    assert "Rate limit" in result


def test_401_auth_error():
    result = handle_api_error(Exception("401 Unauthorized"), "YouTube")
    assert "Authentication failed" in result


def test_generic_error():
    result = handle_api_error(ValueError("something broke"), "Reddit")
    assert "ValueError" in result
    assert "Reddit" in result


def test_credential_sanitization():
    """Credential values in error messages should be redacted."""
    error = Exception("token=sk-secret-123 failed")
    result = handle_api_error(error, "API")
    assert "sk-secret-123" not in result
    assert "REDACTED" in result
