"""MCP tools for the prompt library — discover and generate marketing prompts."""

from marketing_mcp.server import mcp
from marketing_mcp.utils.auth import get_credential, validate_credentials, CREDENTIAL_CONFIG
from marketing_mcp.utils.formatting import format_response
from marketing_mcp.prompts.catalog import (
    CATEGORIES,
    PROMPT_CATALOG,
    get_all_categories,
    get_prompts_for_platforms,
)


def _detect_connected_platforms() -> list[str]:
    """Detect which platforms have credentials configured."""
    connected = []
    for api_name, (required, _optional) in CREDENTIAL_CONFIG.items():
        if not required:
            # Platforms with no required creds (e.g., pagespeed, builtwith) are always available
            connected.append(api_name)
            continue
        if all(get_credential(v) for v in required):
            connected.append(api_name)
    return connected


@mcp.tool()
def marketing_prompts(
    category: str = "",
    level: str = "",
    format: str = "markdown",
) -> str:
    """Browse ready-to-use marketing prompts based on your connected platforms.

    Shows prompts you can use right now based on which APIs you have configured.
    Filter by category (seo, ads, social, analytics, content, local, email,
    ecommerce, crm, competitive, workflow) and level (beginner, intermediate, advanced).
    """
    connected = _detect_connected_platforms()

    if not connected:
        return (
            "No platforms connected yet. Add API credentials via the admin "
            "dashboard (/admin) or .env file to unlock marketing prompts."
        )

    prompts = get_prompts_for_platforms(
        connected,
        category=category or None,
        level=level or None,
    )

    if not prompts:
        available_cats = sorted({p.category for p in get_prompts_for_platforms(connected)})
        return (
            f"No prompts found for category='{category}' level='{level}'.\n"
            f"Your connected platforms unlock these categories: {', '.join(available_cats)}\n"
            f"Try: marketing_prompts(category='seo') or marketing_prompts(level='beginner')"
        )

    # Group by category
    grouped: dict[str, list] = {}
    for p in prompts:
        grouped.setdefault(p.category, []).append(p)

    if format == "json":
        return format_response(
            [
                {
                    "category": p.category,
                    "title": p.title,
                    "prompt": p.prompt,
                    "tool": p.tool,
                    "level": p.level,
                    "platforms": ", ".join(p.platforms),
                }
                for p in prompts
            ],
            response_format="json",
        )

    # Markdown output
    lines = [f"# Marketing Prompts ({len(prompts)} available)\n"]
    lines.append(f"*Based on {len(connected)} connected platforms: {', '.join(connected)}*\n")

    for cat_id, cat_prompts in grouped.items():
        cat_info = CATEGORIES.get(cat_id, {})
        icon = cat_info.get("icon", "")
        label = cat_info.get("label", cat_id)
        lines.append(f"\n## {icon} {label}\n")

        for p in cat_prompts:
            level_badge = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}.get(p.level, "")
            lines.append(f"### {p.title} {level_badge}")
            lines.append(f"**Try:** {p.prompt}")
            lines.append(f"*Tool: `{p.tool}` | Platforms: {', '.join(p.platforms)}*\n")

    return "\n".join(lines)


@mcp.tool()
def prompt_generator(
    business_type: str,
    goals: str = "",
    platforms: str = "",
) -> str:
    """Generate a personalized set of marketing prompts for your business.

    Provide your business type (e.g., 'ecommerce store selling sneakers',
    'local dentist in Austin', 'B2B SaaS for HR teams') and optionally your
    marketing goals and preferred platforms. Returns customized prompts
    you can copy and use immediately.
    """
    connected = _detect_connected_platforms()

    if platforms:
        # User specified which platforms they care about
        requested = [p.strip().lower().replace(" ", "_") for p in platforms.split(",")]
        # Filter to only connected ones
        active = [p for p in requested if p in connected]
    else:
        active = connected

    if not active:
        return (
            "No matching platforms connected. Add API credentials via the admin "
            "dashboard (/admin) or .env file, then try again."
        )

    prompts = get_prompts_for_platforms(active)

    # Build personalized prompt suggestions
    lines = [f"# Marketing Prompts for: {business_type}\n"]

    if goals:
        lines.append(f"**Your goals:** {goals}\n")

    lines.append(f"**Connected platforms:** {', '.join(active)}")
    lines.append(f"**Available prompts:** {len(prompts)}\n")

    # Quick-start: top 5 beginner prompts
    beginner = [p for p in prompts if p.level == "beginner"][:5]
    if beginner:
        lines.append("## 🚀 Quick Start (copy & paste these now)\n")
        for i, p in enumerate(beginner, 1):
            # Personalize the prompt with the business type
            personalized = p.prompt.replace("'{topic}'", f"'{business_type}'")
            personalized = personalized.replace("'{product}'", f"'{business_type}'")
            personalized = personalized.replace("'{business}'", f"'{business_type}'")
            lines.append(f"**{i}. {p.title}**")
            lines.append(f"> {personalized}\n")

    # Intermediate prompts
    intermediate = [p for p in prompts if p.level == "intermediate"][:5]
    if intermediate:
        lines.append("## 📈 Level Up (after you've got the basics)\n")
        for p in intermediate:
            personalized = p.prompt.replace("'{topic}'", f"'{business_type}'")
            personalized = personalized.replace("'{product}'", f"'{business_type}'")
            lines.append(f"**{p.title}**")
            lines.append(f"> {personalized}\n")

    # Advanced workflows
    advanced = [p for p in prompts if p.level == "advanced"][:5]
    if advanced:
        lines.append("## 🔥 Power Moves (multi-platform workflows)\n")
        for p in advanced:
            personalized = p.prompt.replace("'{topic}'", f"'{business_type}'")
            personalized = personalized.replace("'{product}'", f"'{business_type}'")
            personalized = personalized.replace("'{business}'", f"'{business_type}'")
            lines.append(f"**{p.title}** ({'→'.join(p.platforms)})")
            lines.append(f"> {personalized}\n")

    lines.append("---")
    lines.append("*💡 Tip: Just paste any prompt above into your AI chat. The right tool will be called automatically.*")

    return "\n".join(lines)


@mcp.tool()
def marketing_categories(format: str = "markdown") -> str:
    """List all marketing prompt categories and how many prompts are available.

    Use this to discover what types of marketing tasks you can do
    with your connected platforms.
    """
    connected = _detect_connected_platforms()
    all_cats = get_all_categories()

    # Count available prompts per category based on connected platforms
    available_prompts = get_prompts_for_platforms(connected)
    available_counts: dict[str, int] = {}
    for p in available_prompts:
        available_counts[p.category] = available_counts.get(p.category, 0) + 1

    results = []
    for cat in all_cats:
        available = available_counts.get(cat["id"], 0)
        results.append({
            "category": cat["label"],
            "icon": cat["icon"],
            "total_prompts": cat["count"],
            "available_now": available,
            "status": "ready" if available > 0 else "needs_setup",
        })

    if format == "json":
        return format_response(results, response_format="json")

    lines = ["# Marketing Prompt Categories\n"]
    lines.append(f"*{len(connected)} platforms connected*\n")
    lines.append("| Category | Prompts | Available | Status |")
    lines.append("|----------|---------|-----------|--------|")
    for r in results:
        status = "✅ Ready" if r["status"] == "ready" else "⚙️ Needs Setup"
        lines.append(
            f"| {r['icon']} {r['category']} | {r['total_prompts']} | "
            f"{r['available_now']} | {status} |"
        )

    lines.append(f"\n**Total:** {len(PROMPT_CATALOG)} prompts across {len(all_cats)} categories")
    lines.append("\n*Use `marketing_prompts(category='seo')` to browse a specific category.*")

    return "\n".join(lines)
