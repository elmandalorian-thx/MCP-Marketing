# Marketing MCP Server

AI-powered marketing data infrastructure built on the [Model Context Protocol](https://modelcontextprotocol.io/). Exposes marketing platform APIs (Google Ads, Search Console, GA4, Meta, and more) as structured tools for Claude and other MCP clients.

## Quick Start

```bash
# Clone and install
git clone https://github.com/elmandalorian-thx/MCP-Marketing.git
cd MCP-Marketing
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

# Configure credentials
cp .env.example .env
# Edit .env with your API credentials

# Run the server (stdio)
python -m marketing_mcp

# Run the server (HTTP)
marketing-mcp --transport streamable-http --port 8000
```

## Project Structure

```
src/marketing_mcp/
├── server.py              # MCP server entry point
├── clients/               # API client modules (Google Ads, GSC, GA4, Meta, etc.)
├── workflows/             # Tier 2: multi-API orchestration tools
├── agents/                # Tier 3: AI agent tools (Claude SDK)
└── utils/
    ├── auth.py            # Credential loading and validation
    ├── formatting.py      # Response formatting (Markdown/JSON)
    ├── errors.py          # Centralized error handling
    └── cache.py           # In-memory TTL cache
tests/                     # Unit and integration tests
docs/                      # PRD and specifications
```

## Development

```bash
# Run tests
pytest

# Run linter
ruff check src/ tests/

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
```

## Docker

```bash
docker build -t marketing-mcp .
docker run -p 8000:8000 --env-file .env marketing-mcp
```

## Documentation

See [docs/PRD-Marketing-MCP-Server.docx](docs/PRD-Marketing-MCP-Server.docx) for the full product requirements document.
