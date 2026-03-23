"""Client profiles — maps friendly names to account IDs across integrations."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_CLIENTS_FILE = "clients.json"


def _clients_path() -> str:
    return os.path.join(os.getcwd(), _CLIENTS_FILE)


def load_clients() -> dict[str, dict[str, Any]]:
    """Load client profiles from clients.json. Returns empty dict if missing."""
    path = _clients_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to load clients.json: %s", e)
        return {}


def save_clients(clients: dict[str, dict[str, Any]]) -> None:
    """Write client profiles to clients.json."""
    path = _clients_path()
    with open(path, "w") as f:
        json.dump(clients, f, indent=2)


def get_client(name: str) -> dict[str, Any] | None:
    """Look up a client by slug (case-insensitive, fuzzy match)."""
    clients = load_clients()
    slug = name.lower().strip().replace(" ", "_").replace("-", "_")

    # Exact match
    if slug in clients:
        return clients[slug]

    # Partial match
    for key, profile in clients.items():
        if slug in key or slug in profile.get("name", "").lower():
            return profile

    return None


def resolve_client_param(client: str | None, param: str) -> str | None:
    """Resolve a parameter from client profile if client is provided.

    Example: resolve_client_param("stihl", "ga4_property_id")
    """
    if not client:
        return None
    profile = get_client(client)
    if not profile:
        return None
    return profile.get(param)
