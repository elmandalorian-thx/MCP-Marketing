"""Tests for Google Trends Explorer tool."""

from unittest.mock import MagicMock, patch

import pandas as pd

from marketing_mcp.clients.google_trends import google_trends_explorer


def test_trends_too_many_keywords():
    result = google_trends_explorer(keywords=["a", "b", "c", "d", "e", "f"])
    assert "maximum of 5" in result


@patch("pytrends.request.TrendReq")
def test_trends_success(mock_tr_cls):
    mock_tr = MagicMock()
    mock_tr_cls.return_value = mock_tr

    # Mock interest over time
    iot_df = pd.DataFrame({"seo": [50, 60, 70, 80, 90]})
    mock_tr.interest_over_time.return_value = iot_df

    # Mock related queries
    rising_df = pd.DataFrame({"query": ["seo tips", "seo tools"], "value": [500, 300]})
    mock_tr.related_queries.return_value = {"seo": {"rising": rising_df, "top": None}}

    from marketing_mcp.clients.google_trends import _cache
    _cache.clear()

    result = google_trends_explorer(keywords=["seo"])
    assert "seo" in result.lower()


@patch("pytrends.request.TrendReq")
def test_trends_empty(mock_tr_cls):
    mock_tr = MagicMock()
    mock_tr_cls.return_value = mock_tr
    mock_tr.interest_over_time.return_value = pd.DataFrame()
    mock_tr.related_queries.return_value = {}

    from marketing_mcp.clients.google_trends import _cache
    _cache.clear()

    result = google_trends_explorer(keywords=["xyznonexistent"])
    assert "No trends data" in result
