"""Response formatting for MCP tool outputs."""

import json
from typing import Any


def format_response(
    data: list[dict[str, Any]] | dict[str, Any],
    headers: list[str] | None = None,
    response_format: str = "markdown",
) -> str:
    """Format tool response data as markdown or JSON.

    Args:
        data: A single dict or list of dicts to format.
        headers: Column headers for markdown table. If None, inferred from keys.
        response_format: "markdown" for readable tables, "json" for structured data.

    Returns:
        Formatted string ready to return as a tool result.
    """
    if response_format == "json":
        return json.dumps(data, indent=2, default=str)

    # Markdown formatting
    if isinstance(data, dict):
        return _format_single_dict(data)

    if not data:
        return "_No results found._"

    return _format_table(data, headers)


def _format_single_dict(data: dict[str, Any]) -> str:
    """Format a single dict as a markdown list."""
    lines = []
    for key, value in data.items():
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}**: {value}")
    return "\n".join(lines)


def _format_table(data: list[dict[str, Any]], headers: list[str] | None = None) -> str:
    """Format a list of dicts as a markdown table."""
    if not headers:
        headers = list(data[0].keys())

    # Header row
    header_labels = [h.replace("_", " ").title() for h in headers]
    lines = ["| " + " | ".join(header_labels) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    # Data rows
    for row in data:
        values = [str(row.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)
