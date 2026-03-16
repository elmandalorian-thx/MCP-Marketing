# CLAUDE.md — Project Intelligence

> This file provides context for Claude Code when working in this repository.

## Project Overview

**Marketing MCP Server** — a Python MCP server that centralizes marketing platform APIs as structured tools for Claude and other MCP clients. Built with [FastMCP](https://github.com/jlowin/fastmcp), deployed via stdio (local) or streamable-http (remote).

## Architecture

```
                  ┌─────────────────────────────────┐
                  │         MCP Clients              │
                  │  (Claude Desktop, Claude.ai,     │
                  │   custom apps, other agents)     │
                  └──────────────┬──────────────────┘
                                 │ MCP Protocol
                  ┌──────────────▼──────────────────┐
                  │     FastMCP Server (server.py)   │
                  │     Transport: stdio | HTTP      │
                  └──────────────┬──────────────────┘
                                 │
          ┌──────────┬───────────┼───────────┬──────────┐
          ▼          ▼           ▼           ▼          ▼
     ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
     │ Tier 1  │ │ Tier 1 │ │ Tier 1 │ │ Tier 2 │ │ Tier 3 │
     │ Clients │ │ Clients│ │ Clients│ │Workflow│ │ Agents │
     │(9 tools)│ │  ...   │ │  ...   │ │(planned│ │(planned│
     └────┬────┘ └───┬────┘ └───┬────┘ └────────┘ └────────┘
          │          │          │
          ▼          ▼          ▼
     External APIs (Google, Meta, Reddit, YouTube, etc.)
```

### Three-Tier Tool Architecture

| Tier | Purpose | Status |
|------|---------|--------|
| **Tier 1 — Base Tools** | Single-API integrations (9 tools) | Built |
| **Tier 2 — Workflows** | Multi-API orchestration (content gap analysis, cross-channel mapping) | Planned |
| **Tier 3 — AI Agents** | Claude SDK inner calls (content briefs, intent classification) | Planned |

## Key Files & Patterns

### Server Entry Point
- `src/marketing_mcp/server.py` — Creates `mcp = FastMCP("marketing_mcp")`, imports all client modules to register tools via decorators

### Tool Registration Pattern
Each tool lives in `src/marketing_mcp/clients/<name>.py` and follows this pattern:
```python
from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential
from marketing_mcp.utils.cache import TTLCache, KEYWORD_TTL
from marketing_mcp.utils.errors import handle_api_error
from marketing_mcp.utils.formatting import format_response

_cache = TTLCache()

@mcp.tool()
def tool_name(param: str, format: str = "markdown") -> str:
    # 1. Check cache
    # 2. Validate credentials
    # 3. Call external API
    # 4. Format response
    # 5. Cache and return
```

### Shared Utilities (always reuse these)
- **`utils/auth.py`** — `get_credential(name)`, `validate_credentials()`, `get_google_service_credentials(scopes)`, `get_google_ads_client()`, `CREDENTIAL_CONFIG`
- **`utils/cache.py`** — `TTLCache` (thread-safe), `KEYWORD_TTL` (1hr), `AUDIENCE_TTL` (24hr)
- **`utils/formatting.py`** — `format_response(data, headers, response_format)` — markdown tables or JSON
- **`utils/errors.py`** — `handle_api_error(error, api_name)` — sanitized user-friendly messages

### Test Pattern
Tests live in `tests/test_clients/` with mocked API responses:
- Use `unittest.mock.patch` + `sys.modules` patching for Google APIs (avoids `cryptography` import issues in CI)
- Each tool has 3-4 tests: success, no credentials, no results, error handling
- Run: `python3 -m pytest tests/ -v`

## Current Tools (Tier 1)

| Tool | File | API | Auth Required |
|------|------|-----|---------------|
| `pagespeed_audit` | `clients/pagespeed.py` | PageSpeed Insights | None |
| `gads_keyword_ideas` | `clients/google_ads.py` | Google Ads Keyword Planner | OAuth |
| `gsc_search_queries` | `clients/search_console.py` | Search Console | Service Account |
| `ga4_organic_performance` | `clients/ga4.py` | GA4 Data API | Service Account |
| `meta_interest_targeting` | `clients/meta.py` | Meta Graph API | Access Token |
| `google_trends_explorer` | `clients/google_trends.py` | Pytrends (unofficial) | None |
| `youtube_topic_research` | `clients/youtube.py` | YouTube Data v3 | API Key |
| `reddit_topic_research` | `clients/reddit.py` | Reddit/PRAW | OAuth |
| `gbp_insights` | `clients/google_business.py` | Business Profile | Service Account |

## Commands

```bash
pip install -e .[dev]             # Install with dev deps
python -m marketing_mcp           # Run server (stdio)
marketing-mcp --transport streamable-http  # Run server (HTTP)
python3 -m pytest tests/ -v       # Run tests (51 tests)
ruff check src/ tests/            # Lint
docker build -t marketing-mcp .   # Build container
```

## Design Principles

1. **Token efficiency** — Concise tool descriptions, server-side formatting, default limits (10-20 results)
2. **Centralized** — All marketing tools live here; client apps just connect via MCP
3. **Cache everything** — TTLCache on every tool to avoid redundant API calls
4. **Graceful degradation** — Missing credentials return helpful messages, never crash
5. **No secrets in output** — `errors.py` sanitizes credentials from error messages

## Dependencies

Core: `fastmcp`, `httpx`, `pydantic`, `python-dotenv`
Google: `google-ads`, `google-api-python-client`, `google-auth`, `google-analytics-data`
Other: `pytrends`, `praw`
Dev: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`

## Git Workflow

- Development happens on `claude/*` branches
- Auto-merge workflow (`.github/workflows/auto-merge-to-main.yml`) syncs to `main` on push
- CI runs lint + tests on Python 3.12 and 3.13
