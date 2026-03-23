"""Prompt catalog — curated prompts organized by platform and use case.

Each prompt includes:
- category: The marketing domain (seo, ads, social, analytics, content, local, email, ecommerce)
- platforms: Which connected platforms it uses
- tool: The MCP tool it triggers
- title: Short human-readable name
- prompt: The ready-to-use prompt text
- level: beginner / intermediate / advanced
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptEntry:
    category: str
    platforms: tuple[str, ...]
    tool: str
    title: str
    prompt: str
    level: str = "beginner"


# ═══════════════════════════════════════════════════════════════════════
# PROMPT CATALOG — organized by category
# ═══════════════════════════════════════════════════════════════════════

PROMPT_CATALOG: list[PromptEntry] = [
    # ── SEO ───────────────────────────────────────────────────────────
    PromptEntry(
        category="seo",
        platforms=("google_ads",),
        tool="gads_keyword_ideas",
        title="Keyword Research",
        prompt="Find keyword ideas for '{topic}' — show search volume, competition, and suggested bid. Focus on commercial intent keywords.",
    ),
    PromptEntry(
        category="seo",
        platforms=("search_console",),
        tool="gsc_search_queries",
        title="Top Search Queries",
        prompt="Show my top 20 search queries this month from Search Console. Sort by clicks and highlight any queries where my average position is between 4-10 (quick win opportunities).",
    ),
    PromptEntry(
        category="seo",
        platforms=("search_console",),
        tool="gsc_search_queries",
        title="Content Gap Finder",
        prompt="Find search queries where I'm getting impressions but very few clicks (CTR below 2%). These are content optimization opportunities.",
        level="intermediate",
    ),
    PromptEntry(
        category="seo",
        platforms=("pagespeed",),
        tool="pagespeed_audit",
        title="Site Speed Audit",
        prompt="Audit the PageSpeed of {url} — show Core Web Vitals, performance score, and the top 5 things I should fix first.",
    ),
    PromptEntry(
        category="seo",
        platforms=("google_trends",),
        tool="google_trends_explorer",
        title="Trending Topics",
        prompt="What are the trending search topics related to '{topic}' right now? Show interest over time and related queries I should target.",
    ),
    PromptEntry(
        category="seo",
        platforms=("bing_webmaster",),
        tool="bing_webmaster_stats",
        title="Bing SEO Performance",
        prompt="Show my Bing search performance — top queries, clicks, and impressions. Compare with what I see in Google Search Console.",
        level="intermediate",
    ),
    PromptEntry(
        category="seo",
        platforms=("semrush",),
        tool="semrush_domain_overview",
        title="Domain Authority Check",
        prompt="Give me a domain overview for {domain} — organic traffic estimate, top keywords, authority score, and main competitors.",
    ),
    PromptEntry(
        category="seo",
        platforms=("builtwith",),
        tool="builtwith_lookup",
        title="Competitor Tech Stack",
        prompt="What technology stack does {domain} use? Show their CMS, analytics, ad tech, CDN, and any marketing tools.",
    ),
    PromptEntry(
        category="seo",
        platforms=("search_console", "google_ads"),
        tool="gsc_search_queries",
        title="SEO + PPC Keyword Synergy",
        prompt="Compare my organic search queries from Search Console with keyword ideas from Google Ads. Find keywords where I rank organically but could also benefit from paid ads, and vice versa.",
        level="advanced",
    ),

    # ── ADVERTISING ───────────────────────────────────────────────────
    PromptEntry(
        category="ads",
        platforms=("google_ads",),
        tool="gads_keyword_ideas",
        title="Ad Keyword Planning",
        prompt="I'm planning a Google Ads campaign for '{product}'. Find the best keywords — include search volume, competition level, and estimated CPC. Group them into ad groups.",
    ),
    PromptEntry(
        category="ads",
        platforms=("meta",),
        tool="meta_interest_targeting",
        title="Meta Audience Research",
        prompt="Find Meta ad interests related to '{topic}'. Show audience sizes so I can plan my targeting. Suggest a targeting strategy.",
    ),
    PromptEntry(
        category="ads",
        platforms=("meta",),
        tool="meta_interest_targeting",
        title="Competitor Audience Targeting",
        prompt="I want to target my competitor's audience on Meta. My competitor is in the '{industry}' space. Find relevant interests and audience segments I should target.",
        level="intermediate",
    ),
    PromptEntry(
        category="ads",
        platforms=("google_ads", "meta"),
        tool="gads_keyword_ideas",
        title="Cross-Platform Campaign Plan",
        prompt="I'm launching '{product}'. Plan a cross-platform campaign: suggest Google Ads keywords (with volumes) AND Meta interest targeting (with audience sizes). Give me a budget split recommendation.",
        level="advanced",
    ),
    PromptEntry(
        category="ads",
        platforms=("tiktok",),
        tool="tiktok_audience_insights",
        title="TikTok Ad Targeting",
        prompt="What TikTok audiences should I target for '{product}'? Show demographics, interests, and content categories relevant to my market.",
    ),
    PromptEntry(
        category="ads",
        platforms=("pinterest",),
        tool="pinterest_analytics",
        title="Pinterest Ad Insights",
        prompt="Show my Pinterest analytics — top performing pins, audience demographics, and engagement trends. Suggest which content to promote as ads.",
    ),

    # ── SOCIAL MEDIA ──────────────────────────────────────────────────
    PromptEntry(
        category="social",
        platforms=("youtube",),
        tool="youtube_topic_research",
        title="YouTube Content Ideas",
        prompt="Research YouTube topics related to '{topic}'. Show me the top performing videos, their view counts, and suggest content ideas with high search demand but low competition.",
    ),
    PromptEntry(
        category="social",
        platforms=("reddit",),
        tool="reddit_topic_research",
        title="Reddit Trend Research",
        prompt="What are people saying about '{topic}' on Reddit? Show the hottest threads, common questions, and pain points. I want to understand what my audience really cares about.",
    ),
    PromptEntry(
        category="social",
        platforms=("reddit",),
        tool="reddit_topic_research",
        title="Product Feedback Mining",
        prompt="Search Reddit for discussions about '{product_or_category}'. Find complaints, feature requests, and praise. Summarize the top themes — this is my voice-of-customer research.",
        level="intermediate",
    ),
    PromptEntry(
        category="social",
        platforms=("linkedin",),
        tool="linkedin_company_insights",
        title="LinkedIn Company Insights",
        prompt="Show insights for my LinkedIn company page — follower growth, post engagement, and audience demographics. What content type performs best?",
    ),
    PromptEntry(
        category="social",
        platforms=("twitter",),
        tool="twitter_analytics",
        title="X/Twitter Performance",
        prompt="Show my X/Twitter analytics — top tweets by engagement, follower growth trend, and best posting times. What topics drive the most engagement?",
    ),
    PromptEntry(
        category="social",
        platforms=("youtube", "reddit"),
        tool="youtube_topic_research",
        title="Content Opportunity Finder",
        prompt="I create content about '{topic}'. Research both YouTube (search demand) and Reddit (discussions). Find topics people are asking about but no one is making great content for.",
        level="advanced",
    ),

    # ── ANALYTICS ─────────────────────────────────────────────────────
    PromptEntry(
        category="analytics",
        platforms=("ga4",),
        tool="ga4_organic_performance",
        title="Organic Traffic Report",
        prompt="Show my GA4 organic traffic performance — sessions, users, top landing pages, and conversion rate. Compare this month vs last month.",
    ),
    PromptEntry(
        category="analytics",
        platforms=("ga4",),
        tool="ga4_organic_performance",
        title="Conversion Analysis",
        prompt="Analyze my conversion funnel in GA4. Which traffic sources convert best? Which landing pages have the highest and lowest conversion rates? Give me actionable recommendations.",
        level="intermediate",
    ),
    PromptEntry(
        category="analytics",
        platforms=("ga4", "search_console"),
        tool="ga4_organic_performance",
        title="SEO Performance Dashboard",
        prompt="Create an SEO performance dashboard: combine GA4 organic traffic data with Search Console query data. Show me rankings, traffic, conversions, and identify pages that rank well but don't convert (and vice versa).",
        level="advanced",
    ),
    PromptEntry(
        category="analytics",
        platforms=("ga4", "google_ads", "meta"),
        tool="ga4_organic_performance",
        title="Full Marketing ROI Report",
        prompt="Generate a comprehensive marketing ROI report. Pull organic data from GA4, paid search data from Google Ads keywords, and social data from Meta. Which channel delivers the best ROI? Where should I increase spend?",
        level="advanced",
    ),

    # ── CONTENT ───────────────────────────────────────────────────────
    PromptEntry(
        category="content",
        platforms=("google_drive",),
        tool="gdrive_list_files",
        title="Content Inventory",
        prompt="List all documents in my Google Drive marketing folder. Help me organize them and identify any content gaps.",
    ),
    PromptEntry(
        category="content",
        platforms=("google_drive",),
        tool="gdrive_read_file",
        title="Content Review",
        prompt="Read the document '{file_name}' from Google Drive and review it. Check for SEO optimization, readability, and suggest improvements.",
        level="intermediate",
    ),
    PromptEntry(
        category="content",
        platforms=("google_drive",),
        tool="gdrive_create_doc",
        title="Create Content Brief",
        prompt="Create a content brief document in Google Drive for a blog post about '{topic}'. Include target keywords, outline, competitor analysis, and word count target.",
        level="intermediate",
    ),
    PromptEntry(
        category="content",
        platforms=("google_ads", "youtube", "reddit"),
        tool="gads_keyword_ideas",
        title="Content Strategy Builder",
        prompt="Build a content strategy for '{business}'. Research keywords (Google Ads), video topics (YouTube), and audience discussions (Reddit). Create a 30-day content calendar with topics, formats, and target keywords.",
        level="advanced",
    ),

    # ── LOCAL BUSINESS ────────────────────────────────────────────────
    PromptEntry(
        category="local",
        platforms=("google_business",),
        tool="gbp_insights",
        title="Google Business Insights",
        prompt="Show my Google Business Profile insights — searches, views, calls, direction requests, and review summary. How am I performing vs last month?",
    ),
    PromptEntry(
        category="local",
        platforms=("yelp",),
        tool="yelp_business_search",
        title="Yelp Competitor Analysis",
        prompt="Search Yelp for businesses like mine in '{location}' in the '{category}' category. Compare ratings, review counts, and what customers say. What can I learn from top-rated competitors?",
    ),
    PromptEntry(
        category="local",
        platforms=("google_business", "yelp"),
        tool="gbp_insights",
        title="Local SEO Audit",
        prompt="Audit my local online presence. Check my Google Business Profile insights and search for my competitors on Yelp. Where am I strong and where do I need to improve?",
        level="intermediate",
    ),

    # ── EMAIL MARKETING ───────────────────────────────────────────────
    PromptEntry(
        category="email",
        platforms=("mailchimp",),
        tool="mailchimp_campaign_report",
        title="Email Campaign Report",
        prompt="Show my recent Mailchimp campaign performance — open rates, click rates, unsubscribes, and top clicked links. How do I compare to industry benchmarks?",
    ),
    PromptEntry(
        category="email",
        platforms=("mailchimp",),
        tool="mailchimp_audience_insights",
        title="Email List Health Check",
        prompt="Analyze my Mailchimp audience — growth rate, engagement segments, and inactive subscribers. How many contacts should I clean up? Recommend a re-engagement strategy.",
        level="intermediate",
    ),

    # ── ECOMMERCE ─────────────────────────────────────────────────────
    PromptEntry(
        category="ecommerce",
        platforms=("shopify",),
        tool="shopify_analytics",
        title="Store Performance Overview",
        prompt="Show my Shopify store performance — total sales, orders, top products, conversion rate, and average order value. Compare with last month.",
    ),
    PromptEntry(
        category="ecommerce",
        platforms=("shopify", "google_ads"),
        tool="shopify_analytics",
        title="Product Ad Performance",
        prompt="Analyze which of my Shopify products would benefit from Google Ads. Cross-reference my best sellers with keyword search volumes to find products with untapped demand.",
        level="advanced",
    ),

    # ── CRM / SALES ───────────────────────────────────────────────────
    PromptEntry(
        category="crm",
        platforms=("hubspot",),
        tool="hubspot_contacts",
        title="Lead Pipeline Overview",
        prompt="Show my HubSpot pipeline — new leads this month, deals in progress, and conversion rates by stage. Which deals need attention?",
    ),
    PromptEntry(
        category="crm",
        platforms=("hubspot", "ga4"),
        tool="hubspot_contacts",
        title="Lead Source Analysis",
        prompt="Analyze where my best leads come from. Combine HubSpot deal data with GA4 traffic sources. Which marketing channels produce the highest-value leads?",
        level="advanced",
    ),

    # ── COMPETITOR INTELLIGENCE ───────────────────────────────────────
    PromptEntry(
        category="competitive",
        platforms=("semrush", "builtwith"),
        tool="semrush_domain_overview",
        title="Full Competitor Teardown",
        prompt="Do a complete competitor analysis on {competitor_domain}. Pull their SEO metrics from SEMrush (traffic, keywords, backlinks) and their tech stack from BuiltWith. What are they doing that I'm not?",
        level="advanced",
    ),
    PromptEntry(
        category="competitive",
        platforms=("semrush", "google_ads"),
        tool="semrush_domain_overview",
        title="Competitor Keyword Gap",
        prompt="Compare my domain {my_domain} with competitor {competitor_domain}. Find keywords they rank for that I don't. Then check Google Ads for the search volumes and competition of those gap keywords.",
        level="advanced",
    ),

    # ── MULTI-PLATFORM WORKFLOWS ──────────────────────────────────────
    PromptEntry(
        category="workflow",
        platforms=("ga4", "search_console", "google_ads", "meta"),
        tool="ga4_organic_performance",
        title="Weekly Marketing Review",
        prompt="Generate my weekly marketing review. Pull: (1) organic traffic from GA4, (2) search rankings from Search Console, (3) ad keyword performance from Google Ads, (4) social audience from Meta. Summarize wins, losses, and priorities for next week.",
        level="advanced",
    ),
    PromptEntry(
        category="workflow",
        platforms=("google_ads", "meta", "youtube", "reddit"),
        tool="gads_keyword_ideas",
        title="New Product Launch Research",
        prompt="I'm launching '{product}'. Research everything: (1) keyword demand on Google, (2) audience targeting on Meta, (3) video content ideas on YouTube, (4) what people say on Reddit. Create a go-to-market research brief.",
        level="advanced",
    ),
    PromptEntry(
        category="workflow",
        platforms=("pagespeed", "search_console", "ga4"),
        tool="pagespeed_audit",
        title="Technical SEO Health Check",
        prompt="Run a full technical SEO health check: (1) audit page speed, (2) check Search Console for errors and indexing issues, (3) identify pages in GA4 with high bounce rates. Give me a prioritized fix list.",
        level="advanced",
    ),
]

# ── Lookup helpers ────────────────────────────────────────────────────

CATEGORIES = {
    "seo": {"label": "SEO & Search", "icon": "🔍", "color": "#3b82f6"},
    "ads": {"label": "Advertising", "icon": "📢", "color": "#f97316"},
    "social": {"label": "Social Media", "icon": "💬", "color": "#ec4899"},
    "analytics": {"label": "Analytics", "icon": "📊", "color": "#8b5cf6"},
    "content": {"label": "Content", "icon": "✍️", "color": "#10b981"},
    "local": {"label": "Local Business", "icon": "📍", "color": "#06b6d4"},
    "email": {"label": "Email Marketing", "icon": "✉️", "color": "#eab308"},
    "ecommerce": {"label": "Ecommerce", "icon": "🛒", "color": "#ef4444"},
    "crm": {"label": "CRM & Sales", "icon": "🤝", "color": "#6366f1"},
    "competitive": {"label": "Competitive Intel", "icon": "🕵️", "color": "#64748b"},
    "workflow": {"label": "Multi-Platform Workflows", "icon": "⚡", "color": "#d946ef"},
}


def get_prompts_for_platforms(
    connected_platforms: list[str],
    category: str | None = None,
    level: str | None = None,
) -> list[PromptEntry]:
    """Filter prompts to those usable with the given connected platforms."""
    results = []
    platform_set = set(connected_platforms)
    for entry in PROMPT_CATALOG:
        # All required platforms must be connected
        if not set(entry.platforms).issubset(platform_set):
            continue
        if category and entry.category != category:
            continue
        if level and entry.level != level:
            continue
        results.append(entry)
    return results


def get_all_categories() -> list[dict]:
    """Return category metadata with prompt counts."""
    counts: dict[str, int] = {}
    for entry in PROMPT_CATALOG:
        counts[entry.category] = counts.get(entry.category, 0) + 1
    return [
        {**info, "id": cat_id, "count": counts.get(cat_id, 0)}
        for cat_id, info in CATEGORIES.items()
        if counts.get(cat_id, 0) > 0
    ]
