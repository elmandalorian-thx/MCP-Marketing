"""Interactive CLI setup wizard for configuring API credentials."""

from __future__ import annotations

import getpass
import os

from marketing_mcp.utils.auth import (
    CREDENTIAL_CONFIG,
    INTEGRATION_LABELS,
    get_credential_status,
    update_env_file,
    validate_credentials,
)


def _mask(value: str) -> str:
    """Mask a credential value for display (first 4 chars + ****)."""
    if len(value) <= 4:
        return "****"
    return value[:4] + "****"


def _print_status_table() -> None:
    """Print a summary table of all integration statuses."""
    status = get_credential_status()
    print("\n  Integration Status")
    print("  " + "-" * 46)
    for api_name, info in status.items():
        label = info["label"]
        st = info["status"]
        if st == "configured":
            badge = "[OK]"
        elif st == "partial":
            badge = "[PARTIAL]"
        else:
            badge = "[--]"
        print(f"  {badge:>10}  {label}")
    print()


def _prompt_integration(api_name: str) -> dict[str, str]:
    """Prompt the user for credentials for a single integration.

    Returns a dict of {env_var: value} for any values the user entered.
    """
    required, optional = CREDENTIAL_CONFIG[api_name]
    label = INTEGRATION_LABELS.get(api_name, api_name)
    updates: dict[str, str] = {}

    print(f"\n--- {label} ---")

    for var in required:
        current = os.environ.get(var)
        if current:
            print(f"  {var} = {_mask(current)}  (already set)")
            change = input(f"  Update {var}? [y/N]: ").strip().lower()
            if change != "y":
                continue
        value = getpass.getpass(f"  {var}: ")
        if value:
            updates[var] = value

    for var in optional:
        current = os.environ.get(var)
        if current:
            print(f"  {var} = {_mask(current)}  (already set, optional)")
            change = input(f"  Update {var}? [y/N]: ").strip().lower()
            if change != "y":
                continue
        else:
            print(f"  {var}  (optional)")
        value = input(f"  {var}: ").strip()
        if value:
            updates[var] = value

    return updates


def run_setup() -> None:
    """Run the interactive setup wizard."""
    print("\nMarketing MCP Server — Setup Wizard")
    print("=" * 40)
    print("\nThis wizard helps you configure API credentials.")
    print("Press Enter to skip any field. Existing values are preserved.\n")

    _print_status_table()

    status = get_credential_status()
    api_names = list(CREDENTIAL_CONFIG.keys())

    # Let user choose which integrations to configure
    print("Which integrations would you like to configure?\n")
    for i, name in enumerate(api_names, 1):
        info = status[name]
        label = info["label"]
        st = info["status"]
        marker = " [OK]" if st == "configured" else ""
        print(f"  {i}. {label}{marker}")
    print("  A. All integrations")
    print("  Q. Quit\n")

    choice = input("Enter numbers (comma-separated), A, or Q: ").strip().lower()

    if choice == "q":
        print("Setup cancelled.")
        return

    if choice == "a":
        selected = api_names
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            selected = [api_names[i] for i in indices if 0 <= i < len(api_names)]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return

    if not selected:
        print("No integrations selected.")
        return

    # Collect all updates
    all_updates: dict[str, str] = {}
    for api_name in selected:
        updates = _prompt_integration(api_name)
        all_updates.update(updates)

    if not all_updates:
        print("\nNo changes made.")
        return

    # Write to .env
    env_path = os.path.join(os.getcwd(), ".env")
    update_env_file(all_updates, env_path)
    print(f"\nWrote {len(all_updates)} credential(s) to {env_path}")

    # Show updated status
    available = validate_credentials()
    _print_status_table()

    if available:
        print(f"Ready to use: {', '.join(available)}")
    print("\nRun 'marketing-mcp' to start the server.")


if __name__ == "__main__":
    run_setup()
