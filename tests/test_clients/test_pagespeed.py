"""Tests for PageSpeed Insights tool."""

from unittest.mock import MagicMock, patch

from marketing_mcp.clients.pagespeed import pagespeed_audit


def _mock_response():
    return {
        "lighthouseResult": {
            "categories": {"performance": {"score": 0.85}},
            "audits": {
                "largest-contentful-paint": {"displayValue": "2.1 s"},
                "cumulative-layout-shift": {"displayValue": "0.05"},
                "total-blocking-time": {"displayValue": "120 ms"},
                "first-contentful-paint": {"displayValue": "1.2 s"},
                "speed-index": {"displayValue": "3.0 s"},
                "render-blocking-resources": {
                    "title": "Eliminate render-blocking resources",
                    "score": 0.5,
                    "details": {"type": "opportunity", "overallSavingsMs": 350},
                },
            },
        }
    }


@patch("marketing_mcp.clients.pagespeed.httpx.get")
def test_pagespeed_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _mock_response()
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = pagespeed_audit("https://example.com")
    assert "85" in result
    assert "2.1" in result
    assert "render-blocking" in result.lower() or "Render" in result


@patch("marketing_mcp.clients.pagespeed.httpx.get")
def test_pagespeed_error(mock_get):
    from marketing_mcp.clients.pagespeed import _cache
    _cache.clear()

    mock_get.side_effect = Exception("Connection timeout")
    result = pagespeed_audit("https://error-test.com")
    assert "Error" in result or "error" in result or "timeout" in result.lower()


@patch("marketing_mcp.clients.pagespeed.httpx.get")
def test_pagespeed_caching(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _mock_response()
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    # Clear cache first
    from marketing_mcp.clients.pagespeed import _cache
    _cache.clear()

    result1 = pagespeed_audit("https://cache-test.com")
    result2 = pagespeed_audit("https://cache-test.com")
    assert result1 == result2
    assert mock_get.call_count == 1  # Only called once due to cache
