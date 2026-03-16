"""Tests for GA4 Organic Performance tool."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.ga4 import ga4_organic_performance


def test_ga4_no_property_id():
    with patch("marketing_mcp.clients.ga4.get_credential", return_value=None):
        result = ga4_organic_performance()
        assert "property ID" in result.lower() or "not provided" in result.lower() or "not set" in result.lower()


def test_ga4_no_credentials():
    with patch("marketing_mcp.clients.ga4.get_credential", return_value="12345"):
        with patch("marketing_mcp.clients.ga4.get_google_service_credentials", return_value=None):
            result = ga4_organic_performance(property_id="12345")
            assert "not configured" in result


@patch("marketing_mcp.clients.ga4.get_google_service_credentials")
@patch("marketing_mcp.clients.ga4.get_credential")
def test_ga4_success(mock_cred, mock_creds):
    mock_cred.return_value = "12345"
    mock_creds.return_value = MagicMock()

    # Mock GA4 response
    mock_row = MagicMock()
    mock_row.dimension_values = [MagicMock(value="Organic Search")]
    mock_row.metric_values = [
        MagicMock(value="1500"),
        MagicMock(value="1200"),
        MagicMock(value="0.35"),
    ]

    mock_response = MagicMock()
    mock_response.rows = [mock_row]

    dim_header = MagicMock()
    dim_header.name = "sessionDefaultChannelGroup"

    met_header_1 = MagicMock()
    met_header_1.name = "sessions"
    met_header_2 = MagicMock()
    met_header_2.name = "engagedSessions"
    met_header_3 = MagicMock()
    met_header_3.name = "bounceRate"

    mock_response.dimension_headers = [dim_header]
    mock_response.metric_headers = [met_header_1, met_header_2, met_header_3]

    mock_client = MagicMock()
    mock_client.run_report.return_value = mock_response

    mock_client_cls = MagicMock(return_value=mock_client)

    from marketing_mcp.clients.ga4 import _cache
    _cache.clear()

    # Create mock types that behave like dataclasses
    mock_types_mod = MagicMock()
    mock_types_mod.DateRange = lambda **kw: MagicMock(**kw)
    mock_types_mod.Dimension = lambda **kw: MagicMock(**kw)
    mock_types_mod.Metric = lambda **kw: MagicMock(**kw)
    mock_types_mod.RunReportRequest = lambda **kw: MagicMock(**kw)

    ga4_modules = {
        "google.analytics": MagicMock(),
        "google.analytics.data_v1beta": MagicMock(BetaAnalyticsDataClient=mock_client_cls),
        "google.analytics.data_v1beta.types": mock_types_mod,
    }

    with patch.dict(sys.modules, ga4_modules):
        result = ga4_organic_performance(property_id="12345")
        assert "Organic Search" in result
        assert "1500" in result
