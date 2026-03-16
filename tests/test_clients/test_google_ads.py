"""Tests for Google Ads Keyword Planner tool."""

from unittest.mock import MagicMock, patch

from marketing_mcp.clients.google_ads import gads_keyword_ideas


def test_gads_no_credentials():
    with patch("marketing_mcp.clients.google_ads.get_google_ads_client", return_value=None):
        result = gads_keyword_ideas(seed_keywords=["seo"])
        assert "not configured" in result


@patch("marketing_mcp.clients.google_ads.get_credential")
@patch("marketing_mcp.clients.google_ads.get_google_ads_client")
def test_gads_success(mock_client, mock_cred):
    mock_cred.return_value = "12345"

    # Mock keyword idea
    idea = MagicMock()
    idea.text = "seo tools"
    idea.keyword_idea_metrics.avg_monthly_searches = 5000
    idea.keyword_idea_metrics.competition.name = "MEDIUM"
    idea.keyword_idea_metrics.low_top_of_page_bid_micros = 1_500_000
    idea.keyword_idea_metrics.high_top_of_page_bid_micros = 5_000_000

    client = MagicMock()
    mock_client.return_value = client
    client.get_service.return_value.generate_keyword_ideas.return_value = [idea]

    # Mock the type builder
    request_mock = MagicMock()
    client.get_type.return_value = request_mock
    client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH = 1

    from marketing_mcp.clients.google_ads import _cache
    _cache.clear()

    result = gads_keyword_ideas(seed_keywords=["seo"])
    assert "seo tools" in result
    assert "5000" in result or "5,000" in result


@patch("marketing_mcp.clients.google_ads.get_credential")
@patch("marketing_mcp.clients.google_ads.get_google_ads_client")
def test_gads_empty_results(mock_client, mock_cred):
    mock_cred.return_value = "12345"
    client = MagicMock()
    mock_client.return_value = client
    client.get_service.return_value.generate_keyword_ideas.return_value = []
    request_mock = MagicMock()
    client.get_type.return_value = request_mock
    client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH = 1

    from marketing_mcp.clients.google_ads import _cache
    _cache.clear()

    result = gads_keyword_ideas(seed_keywords=["xyznonexistent"])
    assert "No keyword ideas" in result
