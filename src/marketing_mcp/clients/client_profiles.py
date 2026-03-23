"""Client profile management tools — list, lookup, and resolve client accounts."""

import json

from marketing_mcp.server import mcp
from marketing_mcp.utils.clients import get_client, load_clients


@mcp.tool()
def list_clients(format: str = "markdown") -> str:
    """List all client profiles with their configured account IDs.

    Use this to see which clients are set up and what accounts they have linked.
    Each client maps a friendly name (e.g. 'stihl') to their GA4 property,
    Search Console site, Google Ads customer ID, and more.
    """
    clients = load_clients()
    if not clients:
        return "No client profiles configured. Add clients via the admin dashboard at /admin (Clients tab)."

    if format == "json":
        return json.dumps(clients, indent=2)

    lines = []
    for slug, profile in clients.items():
        name = profile.get("name", slug)
        lines.append(f"### {name} (`{slug}`)")
        for key, value in profile.items():
            if key == "name":
                continue
            label = key.replace("_", " ").title()
            lines.append(f"- **{label}**: {value}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_client_profile(client: str) -> str:
    """Get a specific client's profile with all their account IDs.

    Args:
        client: Client name or slug (e.g. 'stihl', 'clara_clinic').
                Matches case-insensitively and supports partial matches.
    """
    profile = get_client(client)
    if not profile:
        clients = load_clients()
        available = ", ".join(clients.keys()) if clients else "none"
        return f"Client '{client}' not found. Available clients: {available}"

    lines = [f"## {profile.get('name', client)}"]
    for key, value in profile.items():
        if key == "name":
            continue
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}**: {value}")

    return "\n".join(lines)
