"""MCP prompt templates — pre-built prompts that AI clients can discover and invoke."""

from marketing_mcp.server import mcp


@mcp.prompt(
    name="seo_quick_wins",
    description="Find SEO quick wins — pages ranking 4-10 that could reach the top with small improvements",
    tags={"seo", "beginner"},
)
def seo_quick_wins() -> str:
    return (
        "Look at my Search Console data and find SEO quick wins. "
        "I want pages where I'm ranking between positions 4-10 with decent impressions. "
        "These are the easiest pages to push to page 1. "
        "For each one, suggest a specific improvement (title tag, content update, internal link)."
    )


@mcp.prompt(
    name="keyword_research",
    description="Research keywords for a topic with search volume, competition, and content suggestions",
    tags={"seo", "beginner"},
)
def keyword_research(topic: str) -> str:
    return (
        f"Do keyword research for '{topic}'. Find keywords using Google Ads Keyword Planner. "
        "Group them into: (1) high-volume head terms, (2) mid-volume body terms, "
        "(3) long-tail questions. For each group, suggest a content piece I should create."
    )


@mcp.prompt(
    name="weekly_marketing_review",
    description="Generate a weekly marketing performance review across all connected platforms",
    tags={"analytics", "workflow", "advanced"},
)
def weekly_marketing_review() -> str:
    return (
        "Generate my weekly marketing review. Check every connected platform and report:\n"
        "1. **Traffic:** GA4 organic sessions and top pages\n"
        "2. **Search:** Search Console impressions, clicks, and ranking changes\n"
        "3. **Ads:** Google Ads / Meta performance if connected\n"
        "4. **Social:** YouTube, Reddit, LinkedIn engagement if connected\n"
        "5. **Business:** Google Business Profile calls/views if connected\n\n"
        "Summarize: top 3 wins, top 3 concerns, top 3 priorities for next week."
    )


@mcp.prompt(
    name="competitor_analysis",
    description="Full competitor analysis — SEO, tech stack, and market positioning",
    tags={"competitive", "advanced"},
)
def competitor_analysis(competitor_domain: str) -> str:
    return (
        f"Do a full competitor analysis on {competitor_domain}.\n"
        "1. Check their SEO metrics — estimated traffic, top keywords, authority\n"
        "2. Look up their tech stack — CMS, analytics, marketing tools\n"
        "3. Find keywords they rank for that I might be missing\n"
        "4. Summarize their strengths and weaknesses vs my site\n"
        "5. Give me 5 specific actions I can take to compete better."
    )


@mcp.prompt(
    name="content_calendar",
    description="Build a 30-day content calendar based on keyword research, trends, and audience insights",
    tags={"content", "advanced"},
)
def content_calendar(business_type: str) -> str:
    return (
        f"Build a 30-day content calendar for my business: {business_type}.\n"
        "Research:\n"
        "- Keywords with search demand (Google Ads)\n"
        "- Trending topics (Google Trends)\n"
        "- What my audience discusses (Reddit)\n"
        "- Video content opportunities (YouTube)\n\n"
        "For each piece, specify: date, topic, format (blog/video/social), "
        "target keyword, and which platform to publish on."
    )


@mcp.prompt(
    name="site_health_check",
    description="Run a comprehensive site health check — speed, SEO, and analytics",
    tags={"seo", "analytics", "intermediate"},
)
def site_health_check(url: str) -> str:
    return (
        f"Run a full health check on {url}:\n"
        "1. **Speed:** Run a PageSpeed audit and report Core Web Vitals\n"
        "2. **SEO:** Check Search Console for crawl errors, indexing issues, top queries\n"
        "3. **Traffic:** Pull GA4 data for bounce rate, session duration, top pages\n"
        "4. **Priority fixes:** Give me a ranked list of what to fix first."
    )


@mcp.prompt(
    name="ad_campaign_plan",
    description="Plan a cross-platform ad campaign with keywords, audiences, and budget",
    tags={"ads", "advanced"},
)
def ad_campaign_plan(product: str, monthly_budget: str = "$1000") -> str:
    return (
        f"Plan an ad campaign for '{product}' with a {monthly_budget}/month budget.\n"
        "1. **Google Ads:** Find the best keywords, estimate CPCs, suggest ad groups\n"
        "2. **Meta:** Find target audiences and interest categories with audience sizes\n"
        "3. **Budget split:** Recommend how to divide the budget across platforms\n"
        "4. **Creative:** Suggest 3 ad angles/hooks to test\n"
        "5. **Timeline:** Week-by-week plan for the first month."
    )


@mcp.prompt(
    name="audience_research",
    description="Deep audience research — who they are, what they search, where they hang out",
    tags={"social", "ads", "intermediate"},
)
def audience_research(target_audience: str) -> str:
    return (
        f"Research the audience: {target_audience}.\n"
        "1. **Search behavior:** What keywords do they search? (Google Ads)\n"
        "2. **Social behavior:** What do they discuss on Reddit? What YouTube content do they watch?\n"
        "3. **Ad targeting:** What Meta interests match this audience? What's the audience size?\n"
        "4. **Demographics:** Age, interests, pain points, buying triggers\n"
        "5. **Content strategy:** What topics and formats will resonate with them?"
    )


@mcp.prompt(
    name="local_business_audit",
    description="Audit a local business's online presence — Google, Yelp, reviews, and local SEO",
    tags={"local", "intermediate"},
)
def local_business_audit(business_name: str, location: str) -> str:
    return (
        f"Audit the local online presence of '{business_name}' in {location}.\n"
        "1. **Google Business:** Check profile insights — views, searches, actions\n"
        "2. **Yelp:** Find the business and competitors, compare ratings and reviews\n"
        "3. **Local SEO:** Check if the site ranks for '{business_name} {location}' queries\n"
        "4. **Recommendations:** Top 5 things to improve for better local visibility."
    )


@mcp.prompt(
    name="ecommerce_growth_plan",
    description="Growth plan for an ecommerce store — traffic, ads, SEO, and conversion opportunities",
    tags={"ecommerce", "advanced"},
)
def ecommerce_growth_plan(store_url: str, product_category: str) -> str:
    return (
        f"Create a growth plan for my ecommerce store ({store_url}) selling {product_category}.\n"
        "1. **Site speed:** Audit PageSpeed (slow sites kill conversions)\n"
        "2. **SEO keywords:** Find product keywords with commercial intent\n"
        "3. **Ad opportunities:** Best Google Ads keywords and Meta audiences\n"
        "4. **Content:** YouTube video ideas and Reddit communities to engage\n"
        "5. **Action plan:** Prioritized list of growth actions for the next 90 days."
    )
