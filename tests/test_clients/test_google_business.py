"""Tests for Google Business Profile tool."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.google_business import gbp_insights


def test_gbp_no_location():
    with patch("marketing_mcp.clients.google_business.get_credential", return_value=None):
        result = gbp_insights()
        assert "must be set" in result.lower()


def test_gbp_no_credentials():
    with patch("marketing_mcp.clients.google_business.get_credential", return_value="test"):
        with patch("marketing_mcp.clients.google_business.get_google_service_credentials", return_value=None):
            result = gbp_insights(account_id="123", location_id="456")
            assert "not configured" in result


@patch("marketing_mcp.clients.google_business.get_google_service_credentials")
@patch("marketing_mcp.clients.google_business.get_credential", return_value="test")
def test_gbp_success(mock_cred, mock_creds):
    mock_creds.return_value = MagicMock()

    review_service = MagicMock()
    review_service.accounts.return_value.locations.return_value.reviews.return_value.list.return_value.execute.return_value = {
        "reviews": [
            {
                "starRating": "FIVE",
                "comment": "Great service!",
                "reviewer": {"displayName": "John"},
                "createTime": "2025-03-01T00:00:00Z",
            }
        ]
    }

    mock_build = MagicMock(return_value=review_service)

    from marketing_mcp.clients.google_business import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"googleapiclient": MagicMock(), "googleapiclient.discovery": MagicMock(build=mock_build)}):
        result = gbp_insights(account_id="123", location_id="456")
        assert "Great service" in result
        assert "John" in result
