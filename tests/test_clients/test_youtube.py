"""Tests for YouTube Topic Research tool."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.youtube import youtube_topic_research


def test_youtube_no_api_key():
    with patch("marketing_mcp.clients.youtube.get_credential", return_value=None):
        result = youtube_topic_research(query="python tutorial")
        assert "not configured" in result


@patch("marketing_mcp.clients.youtube.get_credential", return_value="test_key")
def test_youtube_success(mock_cred):
    youtube = MagicMock()

    # Mock search response
    youtube.search.return_value.list.return_value.execute.return_value = {
        "items": [{"id": {"videoId": "abc123"}}]
    }

    # Mock videos response
    youtube.videos.return_value.list.return_value.execute.return_value = {
        "items": [
            {
                "id": "abc123",
                "snippet": {
                    "title": "Python Tutorial for Beginners",
                    "channelTitle": "Tech Channel",
                    "publishedAt": "2025-01-15T00:00:00Z",
                },
                "statistics": {
                    "viewCount": "1500000",
                    "likeCount": "50000",
                },
            }
        ]
    }

    mock_build = MagicMock(return_value=youtube)

    from marketing_mcp.clients.youtube import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"googleapiclient": MagicMock(), "googleapiclient.discovery": MagicMock(build=mock_build)}):
        result = youtube_topic_research(query="python tutorial")
        assert "Python Tutorial" in result
        assert "1,500,000" in result


@patch("marketing_mcp.clients.youtube.get_credential", return_value="test_key")
def test_youtube_no_results(mock_cred):
    youtube = MagicMock()
    youtube.search.return_value.list.return_value.execute.return_value = {"items": []}
    mock_build = MagicMock(return_value=youtube)

    from marketing_mcp.clients.youtube import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"googleapiclient": MagicMock(), "googleapiclient.discovery": MagicMock(build=mock_build)}):
        result = youtube_topic_research(query="xyznonexistent")
        assert "No YouTube videos" in result
