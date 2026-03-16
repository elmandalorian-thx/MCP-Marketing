"""Tests for Reddit Topic Research tool."""

import sys
from unittest.mock import MagicMock, patch

from marketing_mcp.clients.reddit import reddit_topic_research


def test_reddit_no_credentials():
    with patch("marketing_mcp.clients.reddit.get_credential", return_value=None):
        result = reddit_topic_research(query="python")
        assert "not configured" in result


@patch("marketing_mcp.clients.reddit.get_credential", return_value="test_value")
def test_reddit_success(mock_cred):
    mock_post = MagicMock()
    mock_post.title = "Best Python libraries for data science"
    mock_post.subreddit.display_name = "Python"
    mock_post.score = 500
    mock_post.num_comments = 120
    mock_post.permalink = "/r/Python/comments/abc123/test"

    mock_comment = MagicMock()
    mock_comment.body = "I recommend pandas and numpy for data science work."
    mock_comments = MagicMock()
    mock_comments.__iter__ = MagicMock(return_value=iter([mock_comment]))
    mock_comments.__getitem__ = MagicMock(return_value=mock_comment)
    mock_comments.__bool__ = MagicMock(return_value=True)
    mock_comments.replace_more = MagicMock()
    mock_post.comments = mock_comments

    mock_reddit = MagicMock()
    mock_sub = MagicMock()
    mock_sub.search.return_value = [mock_post]
    mock_reddit.subreddit.return_value = mock_sub

    mock_praw = MagicMock()
    mock_praw.Reddit.return_value = mock_reddit

    from marketing_mcp.clients.reddit import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"praw": mock_praw}):
        result = reddit_topic_research(query="python data science")
        assert "Python" in result
        assert "500" in result


@patch("marketing_mcp.clients.reddit.get_credential", return_value="test_value")
def test_reddit_no_results(mock_cred):
    mock_reddit = MagicMock()
    mock_sub = MagicMock()
    mock_sub.search.return_value = []
    mock_reddit.subreddit.return_value = mock_sub

    mock_praw = MagicMock()
    mock_praw.Reddit.return_value = mock_reddit

    from marketing_mcp.clients.reddit import _cache
    _cache.clear()

    with patch.dict(sys.modules, {"praw": mock_praw}):
        result = reddit_topic_research(query="xyznonexistent")
        assert "No Reddit posts" in result
