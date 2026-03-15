"""Tests for response formatting."""

import json

from marketing_mcp.utils.formatting import format_response


def test_json_format_list():
    """JSON format should return valid JSON."""
    data = [{"keyword": "test", "volume": 100}]
    result = format_response(data, response_format="json")
    parsed = json.loads(result)
    assert parsed == data


def test_json_format_dict():
    """JSON format should work with a single dict."""
    data = {"keyword": "test", "volume": 100}
    result = format_response(data, response_format="json")
    parsed = json.loads(result)
    assert parsed == data


def test_markdown_table():
    """Markdown format should produce a table with headers."""
    data = [
        {"keyword": "seo", "volume": 1000},
        {"keyword": "ppc", "volume": 500},
    ]
    result = format_response(data, response_format="markdown")
    assert "| Keyword | Volume |" in result
    assert "| seo | 1000 |" in result
    assert "| ppc | 500 |" in result


def test_markdown_single_dict():
    """Single dict should render as a list."""
    data = {"keyword": "test", "volume": 100}
    result = format_response(data, response_format="markdown")
    assert "**Keyword**" in result
    assert "100" in result


def test_markdown_empty_list():
    """Empty list should return a no-results message."""
    result = format_response([], response_format="markdown")
    assert "No results" in result


def test_custom_headers():
    """Custom headers should control which columns appear."""
    data = [{"a": 1, "b": 2, "c": 3}]
    result = format_response(data, headers=["a", "c"], response_format="markdown")
    assert "| A | C |" in result
    assert "B" not in result
