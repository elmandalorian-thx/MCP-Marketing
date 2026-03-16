"""Tests for Google Search Console tool."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.search_console import gsc_search_queries


def test_gsc_no_credentials():
    with patch("marketing_mcp.clients.search_console.get_google_service_credentials", return_value=None):
        result = gsc_search_queries(site_url="https://example.com")
        assert "not configured" in result


@patch("marketing_mcp.clients.search_console.get_google_service_credentials")
def test_gsc_success(mock_creds):
    mock_creds.return_value = MagicMock()

    mock_response = {
        "rows": [
            {"keys": ["best seo tools"], "clicks": 150, "impressions": 3000, "ctr": 0.05, "position": 4.2},
            {"keys": ["seo software"], "clicks": 80, "impressions": 2000, "ctr": 0.04, "position": 6.1},
        ]
    }

    mock_build = MagicMock()
    service = MagicMock()
    mock_build.return_value = service
    service.searchanalytics.return_value.query.return_value.execute.return_value = mock_response

    from marketing_mcp.clients.search_console import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"googleapiclient": MagicMock(), "googleapiclient.discovery": MagicMock(build=mock_build)}):
        result = gsc_search_queries(site_url="https://example.com")
        assert "best seo tools" in result
        assert "150" in result


@patch("marketing_mcp.clients.search_console.get_google_service_credentials")
def test_gsc_no_data(mock_creds):
    mock_creds.return_value = MagicMock()

    mock_build = MagicMock()
    service = MagicMock()
    mock_build.return_value = service
    service.searchanalytics.return_value.query.return_value.execute.return_value = {"rows": []}

    from marketing_mcp.clients.search_console import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"googleapiclient": MagicMock(), "googleapiclient.discovery": MagicMock(build=mock_build)}):
        result = gsc_search_queries(site_url="https://example.com")
        assert "No search data" in result
