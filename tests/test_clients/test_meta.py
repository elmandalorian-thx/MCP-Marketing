"""Tests for Meta Interest Targeting tool."""

from unittest.mock import MagicMock, patch

from marketing_mcp.clients.meta import meta_interest_targeting


def test_meta_no_token():
    with patch("marketing_mcp.clients.meta.get_credential", return_value=None):
        result = meta_interest_targeting(query="fitness")
        assert "not configured" in result


@patch("marketing_mcp.clients.meta.get_credential", return_value="test_token")
@patch("marketing_mcp.clients.meta.httpx.get")
def test_meta_success(mock_get, mock_cred):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": [
            {
                "name": "Fitness",
                "audience_size_upper_bound": 500_000_000,
                "topic": "Health & Wellness",
                "description": "People interested in fitness and exercise",
            }
        ]
    }
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    from marketing_mcp.clients.meta import _cache
    _cache.clear()

    result = meta_interest_targeting(query="fitness")
    assert "Fitness" in result
    assert "500" in result


@patch("marketing_mcp.clients.meta.get_credential", return_value="test_token")
@patch("marketing_mcp.clients.meta.httpx.get")
def test_meta_no_results(mock_get, mock_cred):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"data": []}
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    from marketing_mcp.clients.meta import _cache
    _cache.clear()

    result = meta_interest_targeting(query="xyznonexistent")
    assert "No Meta interests" in result
