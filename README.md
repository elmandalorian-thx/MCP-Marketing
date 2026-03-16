# Marketing MCP Server

A centralized marketing data platform built on the [Model Context Protocol](https://modelcontextprotocol.io/). Connect Claude (or any MCP client) to Google Ads, Search Console, GA4, Meta, YouTube, Reddit, Google Trends, PageSpeed, Google Business Profile, and Google Drive — all through a single server.

---

## Why This Exists

Marketing teams juggle dozens of platform dashboards. This server consolidates **10 marketing APIs** into **14 structured MCP tools** that any AI assistant can call directly. Ask Claude to pull your keyword rankings, audit page speed, research trending topics, analyze ad audiences, or save docs straight to Google Drive — without switching tabs or writing API code.

---

## Tools

### Search & SEO

| Tool | What It Does | Auth |
|------|-------------|------|
| **`gsc_search_queries`** | Search Console performance — clicks, impressions, CTR, and average position by query or page | Google Service Account |
| **`gads_keyword_ideas`** | Keyword research — search volume, competition level, and bid estimates from Google Ads Keyword Planner | Google OAuth |
| **`pagespeed_audit`** | Core Web Vitals audit — LCP, CLS, TBT, FCP, performance score, and optimization opportunities | None (free) |

### Analytics & Audiences

| Tool | What It Does | Auth |
|------|-------------|------|
| **`ga4_organic_performance`** | GA4 organic traffic — sessions, engagement rate, bounce rate, and more by dimension | Google Service Account |
| **`meta_interest_targeting`** | Meta ad interest search — audience sizes, topics, and targeting suggestions | Meta Access Token |

### Research & Trends

| Tool | What It Does | Auth |
|------|-------------|------|
| **`google_trends_explorer`** | Google Trends — interest over time, rising queries, and trend direction for up to 5 keywords | None (free) |
| **`youtube_topic_research`** | YouTube video research — titles, view counts, likes, channels, and publish dates | YouTube API Key |
| **`reddit_topic_research`** | Reddit topic mining — top posts, scores, comment counts, and top comment excerpts | Reddit OAuth |

### Local Business

| Tool | What It Does | Auth |
|------|-------------|------|
| **`gbp_insights`** | Google Business Profile — reviews, ratings, and performance metrics for a location | Google Service Account |

### Google Drive

| Tool | What It Does | Auth |
|------|-------------|------|
| **`gdrive_list_files`** | List files in Drive — name, type, modified date, and link, with optional folder and MIME type filters | Google Service Account |
| **`gdrive_search`** | Search Drive by file name or full-text content across all files | Google Service Account |
| **`gdrive_read_file`** | Read file content — exports Google Docs/Sheets/Slides to plain text (or other formats) | Google Service Account |
| **`gdrive_create_doc`** | Create a new Google Doc (or Sheet/Slide) with optional initial content in any folder | Google Service Account |
| **`gdrive_update_doc`** | Update an existing file's content or title | Google Service Account |

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/elmandalorian-thx/MCP-Marketing.git
cd MCP-Marketing
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

### 2. Configure Credentials

**Option A: Setup Wizard (recommended)**
```bash
marketing-mcp setup
```
Interactive CLI that walks you through each integration, prompts for API keys, and writes your `.env` file.

**Option B: Manual**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Only configure the APIs you need — tools gracefully report which credentials are missing.

### 3. Run the Server

```bash
# Local (stdio) — for Claude Desktop or direct piping
python -m marketing_mcp

# Remote (HTTP) — for Claude.ai or networked clients
marketing-mcp --transport streamable-http --port 8000
```

---

## Connect to Claude

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "marketing": {
      "command": "python",
      "args": ["-m", "marketing_mcp"],
      "cwd": "/path/to/MCP-Marketing",
      "env": {
        "GOOGLE_SERVICE_ACCOUNT_JSON": "/path/to/service-account.json",
        "YOUTUBE_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Claude.ai (Remote)

Deploy via Docker (see below), then add the HTTP endpoint as a remote MCP server in Claude.ai settings.

### Claude Code

```bash
claude mcp add marketing -- python -m marketing_mcp
```

---

## Admin Dashboard

A built-in web UI for managing credentials and monitoring tool status.

### Launch Standalone

```bash
marketing-mcp admin
# Dashboard at http://127.0.0.1:8001/admin
```

### In HTTP Mode

When running with `--transport streamable-http`, the dashboard is automatically available at `/admin` on the same port:

```bash
marketing-mcp --transport streamable-http --port 8000
# Dashboard at http://localhost:8000/admin
```

### Features

- **Integration cards** — See which APIs are connected, partially configured, or missing
- **Configure credentials** — Enter API keys through the web form (stored in `.env`)
- **Test connections** — Verify each integration works with a single click
- **Tools overview** — See all 14 tools and their availability status
- **Health endpoint** — `/admin/health` returns uptime, tool count, and integration status

### Security

Set `ADMIN_TOKEN` in your `.env` to require Bearer token auth on admin routes:

```bash
ADMIN_TOKEN=your-secret-token
```

---

## Credential Reference

| Variable | Required By | How to Get |
|----------|------------|------------|
| `GOOGLE_ADS_CLIENT_ID` | Google Ads | [Google Ads API Setup](https://developers.google.com/google-ads/api/docs/get-started/introduction) |
| `GOOGLE_ADS_CLIENT_SECRET` | Google Ads | Same as above |
| `GOOGLE_ADS_REFRESH_TOKEN` | Google Ads | OAuth consent flow |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads | Google Ads Manager account |
| `GOOGLE_ADS_CUSTOMER_ID` | Google Ads | Your account ID (no dashes) |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | GSC, GA4, GBP, Drive | [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts) — file path or JSON string |
| `GA4_PROPERTY_ID` | GA4 (optional) | GA4 Admin > Property Settings |
| `META_ACCESS_TOKEN` | Meta | [Meta Business Suite](https://business.facebook.com/settings) |
| `YOUTUBE_API_KEY` | YouTube | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) — enable YouTube Data API v3 |
| `REDDIT_CLIENT_ID` | Reddit | [Reddit App Preferences](https://www.reddit.com/prefs/apps) — create a "script" app |
| `REDDIT_CLIENT_SECRET` | Reddit | Same as above |
| `REDDIT_USER_AGENT` | Reddit | Any string, e.g. `MyApp/1.0` |
| `PAGESPEED_API_KEY` | PageSpeed (optional) | Google Cloud Console — optional, increases quota |
| `GBP_ACCOUNT_ID` | GBP | Google Business Profile Manager |
| `GBP_LOCATION_ID` | GBP | Google Business Profile Manager |
| `GDRIVE_FOLDER_ID` | Drive (optional) | Default folder ID from Google Drive URL |
| `ADMIN_TOKEN` | Admin dashboard (optional) | Any secret string — protects `/admin` routes |

> You don't need all credentials. Each tool checks its own requirements and returns a helpful message if something is missing.

---

## Tool Details

### `pagespeed_audit`

Audit any URL's performance. No authentication needed.

```
pagespeed_audit(url="https://example.com", strategy="mobile")
```

**Returns:** Performance score (0-100), Core Web Vitals (LCP, CLS, TBT, FCP), Speed Index, and top optimization opportunities ranked by potential time savings.

---

### `gads_keyword_ideas`

Research keywords with Google Ads Keyword Planner data.

```
gads_keyword_ideas(seed_keywords=["seo tools", "marketing automation"], limit=20)
```

**Parameters:**
- `seed_keywords` — list of seed terms
- `language_id` — language constant (default `"1000"` = English)
- `location_id` — geo target (default `"2840"` = United States)
- `limit` — max results (default 20)

**Returns:** Keyword, average monthly searches, competition level (LOW/MEDIUM/HIGH), low and high bid estimates.

---

### `gsc_search_queries`

Pull search performance data from Google Search Console.

```
gsc_search_queries(site_url="https://example.com", days=28, dimensions=["query"])
```

**Parameters:**
- `site_url` — verified property URL
- `days` — lookback period (default 28)
- `dimensions` — `["query"]`, `["page"]`, `["query", "page"]`, etc.
- `row_limit` — max rows (default 20)

**Returns:** Queries/pages with clicks, impressions, CTR (%), and average position.

---

### `ga4_organic_performance`

Get organic traffic metrics from GA4.

```
ga4_organic_performance(property_id="123456789", days=28)
```

**Parameters:**
- `property_id` — GA4 property ID (falls back to `GA4_PROPERTY_ID` env var)
- `days` — lookback period (default 28)
- `metrics` — `["sessions", "engagedSessions", "bounceRate"]` (customizable)
- `dimensions` — `["sessionDefaultChannelGroup"]` (customizable)

**Returns:** Traffic metrics broken down by the specified dimensions.

---

### `meta_interest_targeting`

Search Meta's ad interest database for audience targeting.

```
meta_interest_targeting(query="fitness", limit=10)
```

**Returns:** Interest name, estimated audience size, topic category, and description.

---

### `google_trends_explorer`

Explore Google Trends data for up to 5 keywords.

```
google_trends_explorer(keywords=["AI marketing", "SEO"], timeframe="today 3-m", geo="US")
```

**Returns:** Interest summary (latest, average, max, trend direction) and top rising related queries per keyword.

---

### `youtube_topic_research`

Search YouTube and get engagement data.

```
youtube_topic_research(query="content marketing tips", max_results=10, order="viewCount")
```

**Returns:** Video title, channel, view count, likes, publish date, and direct URL.

---

### `reddit_topic_research`

Mine Reddit for topic insights and community sentiment.

```
reddit_topic_research(query="best CRM software", subreddit="smallbusiness", sort="relevance", limit=10)
```

**Returns:** Post title, subreddit, score, comment count, URL, and top comment excerpt.

---

### `gbp_insights`

Get Google Business Profile reviews and ratings.

```
gbp_insights(account_id="123", location_id="456", days=28)
```

**Returns:** Recent reviews with ratings and comments, reviewer names, dates, and average rating.

---

### `gdrive_list_files`

List files in Google Drive with optional folder and type filters.

```
gdrive_list_files(folder_id="abc123", page_size=20, mime_type="application/vnd.google-apps.document")
```

**Parameters:**
- `folder_id` — restrict to a specific folder (optional)
- `page_size` — max files to return (default 20)
- `mime_type` — filter by MIME type (optional)

**Returns:** File name, type, last modified date, ID, and direct link.

---

### `gdrive_search`

Search Google Drive by file name or full-text content.

```
gdrive_search(query="marketing plan", full_text="Q4 budget", limit=10)
```

**Parameters:**
- `query` — search by file name
- `full_text` — search within file content
- `mime_type` — filter by MIME type (optional)
- `limit` — max results (default 20)

**Returns:** Matching files with name, type, modified date, ID, and link.

---

### `gdrive_read_file`

Read the content of any Google Drive file. Automatically exports Google Workspace files (Docs, Sheets, Slides) to plain text.

```
gdrive_read_file(file_id="abc123", export_format="text/plain")
```

**Parameters:**
- `file_id` — the Drive file ID
- `export_format` — MIME type for export (default `"text/plain"`)

**Returns:** The file's text content with a title header.

---

### `gdrive_create_doc`

Create a new file in Google Drive. Defaults to a Google Doc.

```
gdrive_create_doc(title="Campaign Brief", content="# Q4 Campaign\n\nObjectives...", folder_id="abc123")
```

**Parameters:**
- `title` — document title
- `content` — initial text content (optional)
- `folder_id` — destination folder (optional)
- `mime_type` — `"application/vnd.google-apps.document"` (default), `"application/vnd.google-apps.spreadsheet"`, etc.

**Returns:** Created file name, ID, and direct link.

---

### `gdrive_update_doc`

Update an existing file's content or title.

```
gdrive_update_doc(file_id="abc123", content="Updated content here", new_title="Campaign Brief v2")
```

**Parameters:**
- `file_id` — the Drive file ID
- `content` — new file content (optional)
- `new_title` — rename the file (optional)

**Returns:** Updated file name, ID, modified timestamp, and link.

---

## Project Structure

```
MCP-Marketing/
├── src/marketing_mcp/
│   ├── server.py                  # FastMCP server + tool registration
│   ├── __main__.py                # CLI entry point
│   ├── clients/                   # Tier 1: API integrations (14 tools)
│   │   ├── pagespeed.py           #   PageSpeed Insights
│   │   ├── google_ads.py          #   Google Ads Keyword Planner
│   │   ├── search_console.py      #   Google Search Console
│   │   ├── ga4.py                 #   GA4 Data API
│   │   ├── meta.py                #   Meta Graph API
│   │   ├── google_trends.py       #   Google Trends (pytrends)
│   │   ├── youtube.py             #   YouTube Data API v3
│   │   ├── reddit.py              #   Reddit (PRAW)
│   │   ├── google_business.py     #   Google Business Profile
│   │   └── google_drive.py        #   Google Drive (list, search, read, create, update)
│   ├── admin/                     # Admin dashboard (web UI + API routes)
│   │   ├── routes.py              #   Starlette HTTP handlers
│   │   └── templates.py           #   Single-page HTML dashboard
│   ├── cli_setup.py               # Interactive CLI setup wizard
│   ├── workflows/                 # Tier 2: multi-API orchestration (planned)
│   ├── agents/                    # Tier 3: AI agent tools (planned)
│   └── utils/
│       ├── auth.py                # Credential management
│       ├── cache.py               # Thread-safe TTL cache
│       ├── formatting.py          # Markdown/JSON response formatting
│       └── errors.py              # Error handling + credential sanitization
├── tests/
│   ├── test_utils/                # 24 utility tests
│   └── test_clients/              # 27 tool tests
├── .github/workflows/
│   ├── ci.yml                     # Lint + test (Python 3.12, 3.13)
│   └── auto-merge-to-main.yml    # Auto-merge claude/* branches
├── pyproject.toml                 # Dependencies + config
├── Dockerfile                     # Container deployment
├── .env.example                   # All credential placeholders
└── CLAUDE.md                      # Project context for Claude Code
```

---

## Development

```bash
# Run all tests (51 tests)
python3 -m pytest tests/ -v

# Lint
ruff check src/ tests/

# Run with auto-reload (development)
marketing-mcp --transport streamable-http --port 8000
```

### Adding a New Tool

1. Create `src/marketing_mcp/clients/your_tool.py` following the pattern in any existing client
2. Import `mcp` from `server.py`, decorate with `@mcp.tool()`
3. Add the import to `server.py`
4. Add credentials to `CREDENTIAL_CONFIG` in `utils/auth.py` and `.env.example`
5. Write tests in `tests/test_clients/test_your_tool.py`
6. Run `ruff check src/ tests/ && python3 -m pytest tests/ -v`

---

## Deployment

### Docker

```bash
docker build -t marketing-mcp .
docker run -p 8000:8000 --env-file .env marketing-mcp
```

### Railway / Cloud Run

The Dockerfile exposes port 8000 with streamable-http transport. Set environment variables in your platform's dashboard.

---

## Design Decisions

- **Token-efficient** — Tool descriptions are concise (1-2 sentences). Responses are pre-formatted server-side. Default limits of 10-20 results keep payloads small.
- **Centralized** — All marketing APIs live in one server. Client apps only need MCP connectivity.
- **Cached** — Every tool uses `TTLCache` (1hr for keyword data, 24hr for audience data) to avoid redundant API calls and rate limits.
- **Fail-safe** — Missing credentials return helpful setup messages. API errors are caught, sanitized, and returned as readable text.

---

## Roadmap

- [ ] **Tier 2 Workflows** — `content_gap_analysis`, `cross_channel_keyword_map`, `ad_spend_organic_overlap`
- [ ] **Tier 3 AI Agents** — `keyword_content_brief`, `search_intent_classifier`, `weekly_seo_digest`
- [ ] **AI Search Visibility** — Track brand citations in ChatGPT, Claude, and Gemini responses
- [ ] **SERP Rank Tracking** — Competitive keyword position monitoring

---

## License

Private repository. See project documentation for usage terms.
