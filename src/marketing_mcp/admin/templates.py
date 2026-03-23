"""HTML template for the admin dashboard (single-page, no dependencies)."""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marketing MCP Server — Admin</title>
<style>
  :root {
    --bg: #0f172a; --surface: #1e293b; --surface2: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --green: #4ade80; --amber: #fbbf24; --red: #f87171;
    --radius: 10px;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
         background:var(--bg); color:var(--text); line-height:1.6; }

  .container { max-width:1100px; margin:0 auto; padding:1.5rem 1rem; }

  /* Header */
  header { display:flex; justify-content:space-between; align-items:center;
           margin-bottom:1.5rem; flex-wrap:wrap; gap:0.75rem; }
  header h1 { font-size:1.4rem; font-weight:700; }
  header h1 span { color:var(--accent); }
  .health-badge { background:var(--surface); padding:0.35rem 0.9rem;
                   border-radius:20px; font-size:0.8rem; color:var(--muted); }
  .health-badge .dot { display:inline-block; width:8px; height:8px;
                        border-radius:50%; margin-right:6px; vertical-align:middle; }
  .health-badge .dot.ok { background:var(--green); }

  /* Tabs */
  .tabs { display:flex; gap:0; margin-bottom:1.5rem; border-bottom:2px solid var(--surface2);
          overflow-x:auto; -webkit-overflow-scrolling:touch; }
  .tab { padding:0.6rem 1.2rem; cursor:pointer; font-size:0.85rem; font-weight:600;
         color:var(--muted); border-bottom:2px solid transparent; margin-bottom:-2px;
         transition:all .2s; white-space:nowrap; background:none; border-top:none;
         border-left:none; border-right:none; }
  .tab:hover { color:var(--text); }
  .tab.active { color:var(--accent); border-bottom-color:var(--accent); }
  .tab-content { display:none; }
  .tab-content.active { display:block; }

  /* Cards grid */
  .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
           gap:1.25rem; margin-bottom:2rem; }
  .card { background:var(--surface); border-radius:var(--radius); padding:1.25rem;
          border:1px solid var(--surface2); transition:border-color .2s; }
  .card:hover { border-color:var(--accent); }
  .card-header { display:flex; justify-content:space-between; align-items:center;
                 margin-bottom:0.6rem; }
  .card-title { font-weight:600; font-size:1rem; }
  .badge { padding:0.2rem 0.6rem; border-radius:12px; font-size:0.7rem;
           font-weight:600; text-transform:uppercase; letter-spacing:0.03em; }
  .badge.configured { background:rgba(74,222,128,.15); color:var(--green); }
  .badge.partial { background:rgba(251,191,36,.15); color:var(--amber); }
  .badge.not_configured { background:rgba(248,113,113,.12); color:var(--red); }

  .card-desc { font-size:0.8rem; color:var(--muted); margin-bottom:0.5rem; }

  .cred-list { list-style:none; margin:0.5rem 0; }
  .cred-list li { font-size:0.82rem; color:var(--muted); padding:0.15rem 0;
                  display:flex; align-items:center; gap:4px; }
  .cred-list li .check { color:var(--green); flex-shrink:0; }
  .cred-list li .cross { color:var(--red); flex-shrink:0; }

  /* Tooltip */
  .help-link { display:inline-flex; align-items:center; gap:4px; font-size:0.75rem;
               color:var(--accent); text-decoration:none; margin-top:0.5rem;
               padding:0.25rem 0.5rem; border-radius:4px; background:rgba(56,189,248,.08);
               transition:background .2s; }
  .help-link:hover { background:rgba(56,189,248,.18); }
  .help-link svg { width:14px; height:14px; }
  .tooltip-wrap { position:relative; display:inline-block; }
  .tooltip-wrap .tooltip { visibility:hidden; opacity:0; position:absolute; bottom:calc(100% + 8px);
    left:50%; transform:translateX(-50%); background:var(--surface2); color:var(--text);
    padding:0.6rem 0.8rem; border-radius:8px; font-size:0.75rem; line-height:1.5;
    white-space:normal; width:260px; z-index:50; box-shadow:0 4px 16px rgba(0,0,0,.5);
    transition:opacity .2s, visibility .2s; pointer-events:none; }
  .tooltip-wrap .tooltip::after { content:''; position:absolute; top:100%; left:50%;
    transform:translateX(-50%); border:6px solid transparent; border-top-color:var(--surface2); }
  .tooltip-wrap:hover .tooltip, .tooltip-wrap:focus-within .tooltip { visibility:visible; opacity:1; pointer-events:auto; }

  /* Buttons */
  .btn { display:inline-block; padding:0.4rem 0.85rem; border:none;
         border-radius:6px; font-size:0.78rem; cursor:pointer;
         font-weight:600; transition:opacity .2s; margin-top:0.5rem; margin-right:0.35rem; }
  .btn:hover { opacity:0.85; }
  .btn-primary { background:var(--accent); color:#0f172a; }
  .btn-outline { background:transparent; border:1px solid var(--surface2); color:var(--muted); }
  .btn-outline:hover { border-color:var(--accent); color:var(--accent); }
  .btn-sm { padding:0.3rem 0.6rem; font-size:0.72rem; }

  /* Inline form */
  .config-form { display:none; margin-top:0.75rem; }
  .config-form.open { display:block; }
  .config-form label { display:block; font-size:0.78rem; color:var(--muted);
                        margin-top:0.4rem; }
  .config-form input { width:100%; padding:0.4rem 0.55rem; margin-top:0.15rem;
                        background:var(--bg); border:1px solid var(--surface2);
                        border-radius:6px; color:var(--text); font-size:0.82rem; }
  .config-form input:focus { outline:none; border-color:var(--accent); }
  .form-actions { margin-top:0.65rem; }

  /* Tools grid */
  .tools-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
                gap:1rem; }
  .tool-card { background:var(--surface); border-radius:var(--radius); padding:1rem;
               border:1px solid var(--surface2); transition:border-color .2s; }
  .tool-card:hover { border-color:var(--accent); }
  .tool-name { font-family:monospace; font-size:0.9rem; font-weight:700; color:var(--accent); }
  .tool-meta { display:flex; gap:0.5rem; align-items:center; margin:0.35rem 0; flex-wrap:wrap; }
  .tool-tag { font-size:0.68rem; padding:0.15rem 0.45rem; border-radius:10px;
              background:var(--surface2); color:var(--muted); }
  .tool-tag.cat-search { background:rgba(56,189,248,.12); color:var(--accent); }
  .tool-tag.cat-analytics { background:rgba(168,85,247,.12); color:#c084fc; }
  .tool-tag.cat-research { background:rgba(74,222,128,.12); color:var(--green); }
  .tool-tag.cat-drive { background:rgba(251,191,36,.12); color:var(--amber); }
  .tool-tag.cat-clients { background:rgba(244,114,182,.12); color:#f472b6; }
  .tool-desc { font-size:0.8rem; color:var(--muted); margin:0.4rem 0; }
  .tool-params { font-size:0.75rem; color:var(--muted); }
  .tool-params code { font-size:0.72rem; }
  .tool-status { font-size:0.75rem; font-weight:600; }
  .tool-status.available { color:var(--green); }
  .tool-status.needs-config { color:var(--amber); }

  /* Skills editor */
  .editor-wrap { background:var(--surface); border-radius:var(--radius); border:1px solid var(--surface2);
                 overflow:hidden; }
  .editor-toolbar { display:flex; justify-content:space-between; align-items:center;
                    padding:0.6rem 1rem; background:var(--surface2); flex-wrap:wrap; gap:0.5rem; }
  .editor-toolbar .file-name { font-family:monospace; font-size:0.85rem; color:var(--accent); }
  .editor-textarea { width:100%; min-height:500px; padding:1rem; background:var(--bg);
                     color:var(--text); border:none; font-family:'JetBrains Mono',monospace;
                     font-size:0.82rem; line-height:1.7; resize:vertical; tab-size:2; }
  .editor-textarea:focus { outline:none; }
  .editor-status { padding:0.4rem 1rem; font-size:0.75rem; color:var(--muted);
                   border-top:1px solid var(--surface2); }
  .file-select { background:var(--bg); color:var(--text); border:1px solid var(--surface2);
                 border-radius:6px; padding:0.3rem 0.5rem; font-size:0.8rem; }
  .file-select:focus { outline:none; border-color:var(--accent); }

  /* Toast */
  .toast { position:fixed; bottom:1.5rem; right:1.5rem; padding:0.7rem 1.2rem;
           border-radius:8px; font-size:0.85rem; display:none; z-index:100;
           box-shadow:0 4px 20px rgba(0,0,0,.4); max-width:90vw; }
  .toast.success { background:var(--green); color:#0f172a; }
  .toast.error { background:var(--red); color:#fff; }
  .toast.show { display:block; animation:slideIn .3s ease; }
  @keyframes slideIn { from{transform:translateY(20px);opacity:0} to{transform:none;opacity:1} }

  /* Responsive */
  @media(max-width:768px) {
    .container { padding:1rem 0.75rem; }
    header h1 { font-size:1.2rem; }
    .cards { grid-template-columns:1fr; }
    .tools-grid { grid-template-columns:1fr; }
    header { flex-direction:column; align-items:flex-start; }
    .tabs { gap:0; }
    .tab { padding:0.5rem 0.8rem; font-size:0.78rem; }
    .tooltip-wrap .tooltip { width:200px; left:0; transform:none; }
    .tooltip-wrap .tooltip::after { left:20px; }
    .editor-textarea { min-height:350px; font-size:0.75rem; }
  }
  @media(max-width:400px) {
    .cards { grid-template-columns:1fr; }
    .card { padding:1rem; }
    .tool-card { padding:0.8rem; }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1><span>Marketing MCP</span> Admin</h1>
    <div class="health-badge">
      <span class="dot ok"></span>
      <span id="health-text">Loading...</span>
    </div>
  </header>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('integrations')">Integrations</button>
    <button class="tab" onclick="switchTab('clients')">Clients</button>
    <button class="tab" onclick="switchTab('tools')">Skills & Tools</button>
    <button class="tab" onclick="switchTab('editor')">Skills Editor</button>
  </div>

  <div id="tab-integrations" class="tab-content active">
    <div class="cards" id="cards"></div>
  </div>

  <div id="tab-clients" class="tab-content">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:0.5rem;">
      <h2 style="font-size:1.1rem;font-weight:600;">Client Profiles</h2>
      <button class="btn btn-primary btn-sm" onclick="showAddClient()">+ Add Client</button>
    </div>
    <div id="add-client-form" style="display:none;background:var(--surface);border-radius:var(--radius);padding:1.25rem;margin-bottom:1rem;border:1px solid var(--surface2);">
      <h3 style="font-size:0.95rem;margin-bottom:0.75rem;">New Client Profile</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:0.5rem;">
        <label style="font-size:0.78rem;color:var(--muted);">Client Name *<input type="text" id="new-client-name" placeholder="e.g. STIHL" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">GA4 Property ID<input type="text" id="new-client-ga4" placeholder="e.g. 123456789" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Search Console URL<input type="text" id="new-client-gsc" placeholder="e.g. https://example.com" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Google Ads Customer ID<input type="text" id="new-client-gads" placeholder="e.g. 123-456-7890" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">GBP Location ID<input type="text" id="new-client-gbp-loc" placeholder="Location ID" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">GBP Account ID<input type="text" id="new-client-gbp-acct" placeholder="Account ID" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Drive Folder ID<input type="text" id="new-client-drive" placeholder="Google Drive folder ID" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Website URL<input type="text" id="new-client-website" placeholder="e.g. https://example.com" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Shopify Store URL<input type="text" id="new-client-shopify" placeholder="e.g. mystore.myshopify.com" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
        <label style="font-size:0.78rem;color:var(--muted);">Meta Ad Account ID<input type="text" id="new-client-meta" placeholder="e.g. act_123456" style="width:100%;padding:0.4rem;margin-top:0.15rem;background:var(--bg);border:1px solid var(--surface2);border-radius:6px;color:var(--text);font-size:0.82rem;"></label>
      </div>
      <div style="margin-top:0.75rem;">
        <button class="btn btn-primary btn-sm" onclick="addClient()">Save Client</button>
        <button class="btn btn-outline btn-sm" onclick="document.getElementById('add-client-form').style.display='none'">Cancel</button>
      </div>
    </div>
    <div class="cards" id="clients-grid"></div>
  </div>

  <div id="tab-tools" class="tab-content">
    <div class="tools-grid" id="tools-grid"></div>
  </div>

  <div id="tab-editor" class="tab-content">
    <div class="editor-wrap">
      <div class="editor-toolbar">
        <select class="file-select" id="file-select" onchange="loadFile()">
          <option value="CLAUDE.md">CLAUDE.md</option>
          <option value=".env">.env</option>
          <option value="pyproject.toml">pyproject.toml</option>
          <option value="clients.json">clients.json</option>
        </select>
        <div>
          <button class="btn btn-primary btn-sm" onclick="saveFile()">Save</button>
          <button class="btn btn-outline btn-sm" onclick="loadFile()">Reload</button>
        </div>
      </div>
      <textarea class="editor-textarea" id="editor-textarea" spellcheck="false"></textarea>
      <div class="editor-status" id="editor-status">Ready</div>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
const TOOL_INFO = {
  pagespeed_audit: {
    name: "pagespeed_audit",
    desc: "Run Core Web Vitals audit and get performance scores, accessibility metrics, and optimization opportunities for any URL.",
    params: "url, strategy (mobile|desktop), format",
    category: "search",
    integration: "pagespeed",
    noAuth: true,
    useCase: "Site speed audits, competitor analysis, technical SEO"
  },
  gads_keyword_ideas: {
    name: "gads_keyword_ideas",
    desc: "Get keyword ideas from Google Ads Keyword Planner with search volume, competition level, and bid estimates.",
    params: "seed_keywords, language_id, location_id, limit, format",
    category: "search",
    integration: "google_ads",
    noAuth: false,
    useCase: "Keyword research, PPC planning, content strategy"
  },
  gsc_search_queries: {
    name: "gsc_search_queries",
    desc: "Pull Google Search Console data including clicks, impressions, CTR, and average position by query or page.",
    params: "site_url, days, dimensions, row_limit, format",
    category: "search",
    integration: "search_console",
    noAuth: false,
    useCase: "SEO performance tracking, content optimization, ranking analysis"
  },
  ga4_organic_performance: {
    name: "ga4_organic_performance",
    desc: "Fetch GA4 organic traffic metrics including sessions, engagement rate, bounce rate, and conversions.",
    params: "property_id, days, metrics, dimensions, limit, format",
    category: "analytics",
    integration: "ga4",
    noAuth: false,
    useCase: "Traffic analysis, landing page performance, conversion tracking"
  },
  meta_interest_targeting: {
    name: "meta_interest_targeting",
    desc: "Search Meta/Facebook ad interests and get audience size estimates for targeting research.",
    params: "query, limit, format",
    category: "analytics",
    integration: "meta",
    noAuth: false,
    useCase: "Audience research, ad targeting, market sizing"
  },
  google_trends_explorer: {
    name: "google_trends_explorer",
    desc: "Explore Google Trends for interest over time, rising queries, and regional breakdowns for up to 5 keywords.",
    params: "keywords (list), timeframe, geo, format",
    category: "research",
    integration: "pagespeed",
    noAuth: true,
    useCase: "Trend analysis, seasonal planning, topic validation"
  },
  youtube_topic_research: {
    name: "youtube_topic_research",
    desc: "Search YouTube videos by topic and get view counts, likes, publish dates, and channel info.",
    params: "query, max_results, order, format",
    category: "research",
    integration: "youtube",
    noAuth: false,
    useCase: "Video content research, competitor analysis, content gaps"
  },
  reddit_topic_research: {
    name: "reddit_topic_research",
    desc: "Mine Reddit posts by topic or subreddit with scores, comment counts, and engagement metrics.",
    params: "query, subreddit, sort, time_filter, limit, format",
    category: "research",
    integration: "reddit",
    noAuth: false,
    useCase: "Community sentiment, pain point discovery, content ideas"
  },
  gbp_insights: {
    name: "gbp_insights",
    desc: "Pull Google Business Profile reviews, ratings, and performance metrics for local SEO insights.",
    params: "location_id, account_id, days, format",
    category: "analytics",
    integration: "google_business_profile",
    noAuth: false,
    useCase: "Local SEO, reputation monitoring, review analysis"
  },
  gdrive_list_files: {
    name: "gdrive_list_files",
    desc: "List files in Google Drive with optional folder and MIME type filtering.",
    params: "folder_id, page_size, mime_type, format",
    category: "drive",
    integration: "google_drive",
    noAuth: false,
    useCase: "File browsing, asset management"
  },
  gdrive_search: {
    name: "gdrive_search",
    desc: "Full-text and filename search across Google Drive files.",
    params: "query, full_text, mime_type, limit, format",
    category: "drive",
    integration: "google_drive",
    noAuth: false,
    useCase: "Finding documents, content discovery"
  },
  gdrive_read_file: {
    name: "gdrive_read_file",
    desc: "Read file content from Google Drive. Auto-exports Google Workspace files (Docs, Sheets, Slides).",
    params: "file_id, export_format",
    category: "drive",
    integration: "google_drive",
    noAuth: false,
    useCase: "Reading briefs, pulling data, content review"
  },
  gdrive_create_doc: {
    name: "gdrive_create_doc",
    desc: "Create new Google Docs, Sheets, or Slides in Drive with initial content.",
    params: "title, content, folder_id, mime_type",
    category: "drive",
    integration: "google_drive",
    noAuth: false,
    useCase: "Creating briefs, reports, content drafts"
  },
  gdrive_update_doc: {
    name: "gdrive_update_doc",
    desc: "Update file content or rename files in Google Drive.",
    params: "file_id, content, new_title",
    category: "drive",
    integration: "google_drive",
    noAuth: false,
    useCase: "Editing documents, updating reports"
  },
  list_clients: {
    name: "list_clients",
    desc: "List all client profiles with their configured account IDs across all platforms.",
    params: "format",
    category: "clients",
    integration: "builtwith",
    noAuth: true,
    useCase: "Client overview, quick account lookup"
  },
  get_client_profile: {
    name: "get_client_profile",
    desc: "Get a specific client's profile with all linked account IDs. Supports fuzzy name matching.",
    params: "client",
    category: "clients",
    integration: "builtwith",
    noAuth: true,
    useCase: "Quick client lookup before querying tools"
  },
  semrush_domain_overview: {
    name: "semrush_domain_overview",
    desc: "Domain analytics from Semrush — organic traffic estimates, keyword count, and top competitors.",
    params: "domain, database, limit, format",
    category: "search",
    integration: "semrush",
    noAuth: false,
    useCase: "Competitor analysis, domain authority, traffic estimation"
  },
  semrush_keyword_overview: {
    name: "semrush_keyword_overview",
    desc: "Keyword metrics from Semrush — search volume, keyword difficulty, CPC, and competition.",
    params: "keyword, database, format",
    category: "search",
    integration: "semrush",
    noAuth: false,
    useCase: "Advanced keyword research, difficulty analysis"
  },
  linkedin_ad_targeting: {
    name: "linkedin_ad_targeting",
    desc: "Search LinkedIn ad targeting options — industries, job titles, skills, and seniorities.",
    params: "query, facet, limit, format",
    category: "analytics",
    integration: "linkedin",
    noAuth: false,
    useCase: "B2B audience research, LinkedIn ad campaigns"
  },
  bing_search_queries: {
    name: "bing_search_queries",
    desc: "Bing Webmaster search query data — impressions, clicks, CTR, and average position.",
    params: "site_url, limit, format",
    category: "search",
    integration: "bing_webmaster",
    noAuth: false,
    useCase: "Secondary search engine data, Microsoft ecosystem"
  },
  mailchimp_campaigns: {
    name: "mailchimp_campaigns",
    desc: "Recent Mailchimp email campaigns with open rates, click rates, and send counts.",
    params: "limit, format",
    category: "analytics",
    integration: "mailchimp",
    noAuth: false,
    useCase: "Email performance tracking, campaign analysis"
  },
  mailchimp_audiences: {
    name: "mailchimp_audiences",
    desc: "Mailchimp audience lists with subscriber counts, open rates, and engagement stats.",
    params: "format",
    category: "analytics",
    integration: "mailchimp",
    noAuth: false,
    useCase: "List health, subscriber growth tracking"
  },
  tiktok_interest_targeting: {
    name: "tiktok_interest_targeting",
    desc: "TikTok Ads interest categories for audience targeting and campaign planning.",
    params: "advertiser_id, format",
    category: "analytics",
    integration: "tiktok",
    noAuth: false,
    useCase: "TikTok campaign planning, Gen Z audience research"
  },
  pinterest_search_pins: {
    name: "pinterest_search_pins",
    desc: "Search Pinterest pins by topic — titles, descriptions, save counts, and links.",
    params: "query, limit, format",
    category: "research",
    integration: "pinterest",
    noAuth: false,
    useCase: "Visual content research, Pinterest SEO, trend discovery"
  },
  x_search_recent: {
    name: "x_search_recent",
    desc: "Search recent X/Twitter posts with engagement metrics — likes, retweets, impressions.",
    params: "query, limit, format",
    category: "research",
    integration: "x_twitter",
    noAuth: false,
    useCase: "Social listening, brand monitoring, trend tracking"
  },
  shopify_products: {
    name: "shopify_products",
    desc: "List Shopify products with prices, inventory status, and variant details.",
    params: "limit, format",
    category: "analytics",
    integration: "shopify",
    noAuth: false,
    useCase: "E-commerce catalog review, inventory monitoring"
  },
  shopify_orders: {
    name: "shopify_orders",
    desc: "Recent Shopify orders with totals, fulfillment status, and financial details.",
    params: "limit, status, format",
    category: "analytics",
    integration: "shopify",
    noAuth: false,
    useCase: "Sales tracking, order analysis, fulfillment monitoring"
  },
  yelp_business_search: {
    name: "yelp_business_search",
    desc: "Search Yelp businesses by term and location — ratings, reviews, pricing, categories.",
    params: "term, location, limit, format",
    category: "research",
    integration: "yelp",
    noAuth: false,
    useCase: "Local competitor research, reputation analysis"
  },
  yelp_business_reviews: {
    name: "yelp_business_reviews",
    desc: "Get recent Yelp reviews for a specific business with ratings and review text.",
    params: "business_id, limit, format",
    category: "research",
    integration: "yelp",
    noAuth: false,
    useCase: "Review sentiment analysis, reputation monitoring"
  },
  builtwith_lookup: {
    name: "builtwith_lookup",
    desc: "Detect any website's tech stack — CMS, analytics, ads, frameworks, and hosting provider.",
    params: "domain, format",
    category: "research",
    integration: "builtwith",
    noAuth: true,
    useCase: "Competitor tech analysis, migration planning"
  },
  hubspot_contacts: {
    name: "hubspot_contacts",
    desc: "List HubSpot CRM contacts with name, email, company, and lifecycle stage.",
    params: "limit, format",
    category: "analytics",
    integration: "hubspot",
    noAuth: false,
    useCase: "Lead management, CRM overview, sales pipeline"
  },
  hubspot_deals: {
    name: "hubspot_deals",
    desc: "List HubSpot deals with stage, amount, close date, and pipeline info.",
    params: "limit, format",
    category: "analytics",
    integration: "hubspot",
    noAuth: false,
    useCase: "Sales pipeline, revenue forecasting, deal tracking"
  }
};

const INTEGRATION_HELP = {
  google_ads: {
    desc: "Google Ads API for Keyword Planner access. Requires OAuth credentials and a Google Ads manager account.",
    url: "https://developers.google.com/google-ads/api/docs/get-started/introduction",
    steps: "1. Create Google Cloud project\\n2. Enable Google Ads API\\n3. Create OAuth 2.0 credentials\\n4. Get Developer Token from Ads account (Settings > API Center)\\n5. Get Customer ID from your Ads account"
  },
  search_console: {
    desc: "Google Search Console API. Uses a service account shared with GA4, GBP, and Drive.",
    url: "https://console.cloud.google.com/iam-admin/serviceaccounts",
    steps: "1. Create service account in Google Cloud\\n2. Download JSON key\\n3. Enable Search Console API\\n4. Add service account email to your Search Console property"
  },
  ga4: {
    desc: "Google Analytics 4 Data API. Uses the same service account as Search Console.",
    url: "https://analytics.google.com",
    steps: "1. Set up service account (same as Search Console)\\n2. Enable GA4 Data API in Cloud Console\\n3. Add service account to GA4 property (Admin > Property Access)\\n4. Copy Property ID from Admin > Property Settings"
  },
  meta: {
    desc: "Meta Marketing API for Facebook/Instagram ad interest research.",
    url: "https://business.facebook.com/settings",
    steps: "1. Go to Meta Business Suite\\n2. Create System User under Business Settings\\n3. Generate long-lived access token\\n4. Ensure ads_management and ads_read permissions"
  },
  youtube: {
    desc: "YouTube Data API v3 for video search and metrics. Only needs a simple API key.",
    url: "https://console.cloud.google.com/apis/credentials",
    steps: "1. Go to Google Cloud Console > Credentials\\n2. Enable YouTube Data API v3\\n3. Create an API Key\\n4. Copy and paste below"
  },
  reddit: {
    desc: "Reddit API via PRAW for post mining and community research.",
    url: "https://www.reddit.com/prefs/apps",
    steps: "1. Go to Reddit > Preferences > Apps\\n2. Create new app (type: script)\\n3. Set redirect URI to http://localhost:8080\\n4. Copy Client ID and Secret"
  },
  pagespeed: {
    desc: "PageSpeed Insights API. Works without a key (public API). Adding a key increases your daily quota.",
    url: "https://console.cloud.google.com/apis/credentials",
    steps: "No setup needed for basic use. Optional: Create API key in Google Cloud to increase quota from 100 to 25,000 requests/day."
  },
  google_business_profile: {
    desc: "Google Business Profile API for reviews and local SEO data. Uses service account.",
    url: "https://business.google.com",
    steps: "1. Set up service account (same as Search Console)\\n2. Enable My Business API\\n3. Get Account ID and Location ID from Google Business settings"
  },
  google_drive: {
    desc: "Google Drive API v3 for file management. Uses service account. Share folders with the SA email.",
    url: "https://console.cloud.google.com/apis/library/drive.googleapis.com",
    steps: "1. Set up service account (same as Search Console)\\n2. Enable Google Drive API\\n3. Share your Drive folder with the service account email\\n4. Copy folder ID from the Drive URL"
  },
  anthropic: {
    desc: "Anthropic API key for future Tier 3 AI agent tools (content briefs, intent classification).",
    url: "https://console.anthropic.com/settings/keys",
    steps: "1. Go to Anthropic Console\\n2. Create an API key\\n3. Copy and paste below"
  },
  semrush: {
    desc: "Semrush API for domain analytics, keyword research, and competitor analysis.",
    url: "https://www.semrush.com/api/",
    steps: "1. Go to Semrush > Subscription Info\\n2. Your API key is in the API section\\n3. Requires a paid Semrush plan with API access"
  },
  linkedin: {
    desc: "LinkedIn Marketing API for B2B ad targeting and company page analytics.",
    url: "https://www.linkedin.com/developers/apps",
    steps: "1. Create an app at LinkedIn Developers\\n2. Request Marketing Developer Platform access\\n3. Generate a long-lived access token\\n4. Ensure r_ads and r_ads_reporting permissions"
  },
  bing_webmaster: {
    desc: "Bing Webmaster Tools API for search performance data on Microsoft's search engine.",
    url: "https://www.bing.com/webmasters/",
    steps: "1. Sign in to Bing Webmaster Tools\\n2. Go to Settings > API Access\\n3. Generate your API key"
  },
  mailchimp: {
    desc: "Mailchimp API for email campaign metrics and audience management.",
    url: "https://mailchimp.com/developer/",
    steps: "1. Log in to Mailchimp\\n2. Go to Profile > Extras > API Keys\\n3. Create a new API key\\n4. The key includes your data center (e.g. us1)"
  },
  tiktok: {
    desc: "TikTok Marketing API for ad campaign management and audience targeting.",
    url: "https://business-api.tiktok.com/portal/docs",
    steps: "1. Create a TikTok for Business account\\n2. Apply for Marketing API access\\n3. Create an app and get your access token\\n4. You'll also need your Advertiser ID"
  },
  pinterest: {
    desc: "Pinterest API for pin search, board management, and visual content research.",
    url: "https://developers.pinterest.com/",
    steps: "1. Create a Pinterest Business account\\n2. Go to Pinterest Developers\\n3. Create an app\\n4. Generate an access token with pins:read scope"
  },
  x_twitter: {
    desc: "X (Twitter) API v2 for tweet search, social listening, and engagement data.",
    url: "https://developer.x.com/en/portal/dashboard",
    steps: "1. Apply for X Developer access\\n2. Create a project and app\\n3. Generate a Bearer Token (read-only)\\n4. Basic access is free (limited to recent tweets)"
  },
  shopify: {
    desc: "Shopify Admin API for product data, orders, and store analytics.",
    url: "https://admin.shopify.com/",
    steps: "1. Go to your Shopify Admin > Settings > Apps\\n2. Click Develop apps > Create app\\n3. Configure scopes (read_products, read_orders)\\n4. Install the app and copy the access token\\n5. Store URL format: mystore.myshopify.com"
  },
  yelp: {
    desc: "Yelp Fusion API for business search, reviews, and local competitor research.",
    url: "https://www.yelp.com/developers/v3/manage_app",
    steps: "1. Go to Yelp Developers\\n2. Create an app\\n3. Copy your API Key\\n4. Free tier: 5,000 API calls/day"
  },
  hubspot: {
    desc: "HubSpot API for CRM contacts, deals, and marketing automation data.",
    url: "https://developers.hubspot.com/",
    steps: "1. Go to HubSpot > Settings > Integrations > Private Apps\\n2. Create a private app\\n3. Set scopes: crm.objects.contacts.read, crm.objects.deals.read\\n4. Copy the access token"
  },
  builtwith: {
    desc: "BuiltWith technology lookup. Free API — no key required. Detects CMS, analytics, and tech stack.",
    url: "https://api.builtwith.com/",
    steps: "No setup needed. Uses the free BuiltWith API. Optional: Get a paid key for more detailed results."
  }
};

const CATEGORY_LABELS = {
  clients: "Client Profiles",
  search: "Search & SEO",
  analytics: "Analytics & Audiences",
  research: "Research & Trends",
  drive: "Google Drive"
};

const NO_AUTH_TOOLS = ["pagespeed_audit", "google_trends_explorer"];

function toast(msg, type) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast " + type + " show";
  setTimeout(() => el.classList.remove("show"), 3500);
}

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  return res.json();
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelector(`[onclick="switchTab('${name}')"]`).classList.add("active");
  document.getElementById("tab-" + name).classList.add("active");
  if (name === "editor") loadFile();
  if (name === "clients") loadClients();
}

let _credsCache = null;

async function loadDashboard() {
  const [creds, health] = await Promise.all([
    fetchJSON("/admin/credentials"),
    fetchJSON("/admin/health"),
  ]);
  _credsCache = creds;

  document.getElementById("health-text").textContent =
    health.tools + " tools | " + health.integrations_configured + "/" + health.integrations_total + " configured | Python " + health.python_version;

  // Integration cards
  const container = document.getElementById("cards");
  container.innerHTML = "";
  for (const [key, info] of Object.entries(creds)) {
    const help = INTEGRATION_HELP[key] || {};
    const card = document.createElement("div");
    card.className = "card";
    const allVars = {...info.required, ...info.optional};
    const credListHTML = Object.entries(allVars).map(([v, ok]) =>
      `<li>${ok ? '<span class="check">&#10003;</span>' : '<span class="cross">&#10007;</span>'}<span>${v}${info.optional[v] !== undefined ? ' <em style="opacity:.6">(optional)</em>' : ''}</span></li>`
    ).join("");

    const formFieldsHTML = Object.keys(allVars).map(v =>
      `<label>${v}<input type="password" name="${v}" placeholder="${allVars[v] ? '(configured - leave blank to keep)' : '(not set)'}"></label>`
    ).join("");

    const tooltipSteps = (help.steps || "").replace(/\\n/g, "<br>");

    card.innerHTML = `
      <div class="card-header">
        <div class="card-title">${info.label}</div>
        <span class="badge ${info.status}">${info.status.replace("_", " ")}</span>
      </div>
      <div class="card-desc">${help.desc || ''}</div>
      <ul class="cred-list">${credListHTML}</ul>
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:0.4rem;">
        <div class="tooltip-wrap">
          <a href="${help.url || '#'}" target="_blank" rel="noopener" class="help-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            How to get credentials
          </a>
          <div class="tooltip">${tooltipSteps}</div>
        </div>
      </div>
      <div style="margin-top:0.5rem;">
        <button class="btn btn-primary btn-sm" onclick="toggleForm(this)">Configure</button>
        <button class="btn btn-outline btn-sm" onclick="testConnection('${key}', this)">Test</button>
      </div>
      <div class="config-form" data-integration="${key}">
        ${formFieldsHTML}
        <div class="form-actions">
          <button class="btn btn-primary btn-sm" onclick="saveCredentials('${key}', this)">Save</button>
          <button class="btn btn-outline btn-sm" onclick="toggleForm(this)">Cancel</button>
        </div>
      </div>
    `;
    container.appendChild(card);
  }

  // Tools grid
  loadToolsGrid(creds);
}

function loadToolsGrid(creds) {
  const grid = document.getElementById("tools-grid");
  grid.innerHTML = "";

  const categories = {};
  for (const [toolName, tool] of Object.entries(TOOL_INFO)) {
    const cat = tool.category;
    if (!categories[cat]) categories[cat] = [];
    categories[cat].push(tool);
  }

  for (const [cat, tools] of Object.entries(categories)) {
    const catLabel = CATEGORY_LABELS[cat] || cat;
    const catClass = "cat-" + cat;

    for (const tool of tools) {
      const intInfo = creds ? creds[tool.integration] : null;
      const isAvailable = tool.noAuth || (intInfo && intInfo.status === "configured");
      const statusClass = isAvailable ? "available" : "needs-config";
      const statusText = isAvailable ? "Available" : "Needs config";

      const card = document.createElement("div");
      card.className = "tool-card";
      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
          <div class="tool-name">${tool.name}</div>
          <span class="tool-status ${statusClass}">${statusText}</span>
        </div>
        <div class="tool-meta">
          <span class="tool-tag ${catClass}">${catLabel}</span>
          ${tool.noAuth ? '<span class="tool-tag">No auth</span>' : ''}
        </div>
        <div class="tool-desc">${tool.desc}</div>
        <div class="tool-params"><strong>Params:</strong> <code>${tool.params}</code></div>
        <div style="font-size:0.75rem;color:var(--muted);margin-top:0.3rem;"><strong>Use case:</strong> ${tool.useCase}</div>
      `;
      grid.appendChild(card);
    }
  }
}

function toggleForm(btn) {
  const form = btn.closest(".card").querySelector(".config-form");
  form.classList.toggle("open");
}

async function saveCredentials(integration, btn) {
  const form = btn.closest(".config-form");
  const inputs = form.querySelectorAll("input");
  const updates = {};
  inputs.forEach(inp => {
    if (inp.value.trim()) updates[inp.name] = inp.value.trim();
  });
  if (Object.keys(updates).length === 0) {
    toast("No values entered", "error");
    return;
  }
  try {
    await fetchJSON("/admin/credentials", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(updates),
    });
    toast("Credentials saved", "success");
    form.classList.remove("open");
    loadDashboard();
  } catch (e) {
    toast("Failed to save: " + e.message, "error");
  }
}

async function testConnection(integration, btn) {
  btn.textContent = "Testing...";
  btn.disabled = true;
  try {
    const res = await fetchJSON("/admin/test/" + integration, {method: "POST"});
    if (res.success) {
      toast(res.message || "Connection successful", "success");
    } else {
      toast(res.message || "Connection failed", "error");
    }
  } catch (e) {
    toast("Test failed: " + e.message, "error");
  } finally {
    btn.textContent = "Test";
    btn.disabled = false;
  }
}

// Skills editor
async function loadFile() {
  const filename = document.getElementById("file-select").value;
  const status = document.getElementById("editor-status");
  status.textContent = "Loading " + filename + "...";
  try {
    const res = await fetch("/admin/files/" + encodeURIComponent(filename));
    if (!res.ok) throw new Error("Failed to load file");
    const data = await res.json();
    document.getElementById("editor-textarea").value = data.content;
    status.textContent = filename + " loaded (" + data.content.length + " chars)";
  } catch (e) {
    status.textContent = "Error: " + e.message;
    document.getElementById("editor-textarea").value = "";
  }
}

async function saveFile() {
  const filename = document.getElementById("file-select").value;
  const content = document.getElementById("editor-textarea").value;
  const status = document.getElementById("editor-status");
  status.textContent = "Saving " + filename + "...";
  try {
    const res = await fetch("/admin/files/" + encodeURIComponent(filename), {
      method: "PUT",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({content}),
    });
    if (!res.ok) throw new Error("Failed to save");
    status.textContent = filename + " saved successfully";
    toast("File saved", "success");
  } catch (e) {
    status.textContent = "Error saving: " + e.message;
    toast("Failed to save: " + e.message, "error");
  }
}

// Handle tab key in textarea
document.getElementById("editor-textarea").addEventListener("keydown", function(e) {
  if (e.key === "Tab") {
    e.preventDefault();
    const start = this.selectionStart;
    const end = this.selectionEnd;
    this.value = this.value.substring(0, start) + "  " + this.value.substring(end);
    this.selectionStart = this.selectionEnd = start + 2;
  }
});

// Client profiles
async function loadClients() {
  try {
    const clients = await fetchJSON("/admin/clients");
    const grid = document.getElementById("clients-grid");
    grid.innerHTML = "";

    if (Object.keys(clients).length === 0) {
      grid.innerHTML = '<div style="color:var(--muted);font-size:0.9rem;padding:2rem;text-align:center;">No clients configured yet. Click "+ Add Client" to create your first client profile.</div>';
      return;
    }

    for (const [slug, profile] of Object.entries(clients)) {
      const card = document.createElement("div");
      card.className = "card";
      const fields = Object.entries(profile).filter(([k]) => k !== "name").map(([k, v]) =>
        `<li><span class="check">&#10003;</span><span>${k.replace(/_/g, " ").replace(/\\b\\w/g, l => l.toUpperCase())}: <code>${v}</code></span></li>`
      ).join("");

      card.innerHTML = `
        <div class="card-header">
          <div class="card-title">${profile.name || slug}</div>
          <span class="badge configured">${slug}</span>
        </div>
        <ul class="cred-list">${fields || '<li style="color:var(--muted)">No accounts linked yet</li>'}</ul>
        <div style="margin-top:0.5rem;">
          <button class="btn btn-primary btn-sm" onclick="editClient('${slug}')">Edit</button>
          <button class="btn btn-outline btn-sm" style="color:var(--red);border-color:var(--red);" onclick="deleteClient('${slug}')">Delete</button>
        </div>
      `;
      grid.appendChild(card);
    }
  } catch (e) {
    console.error("Failed to load clients:", e);
  }
}

function showAddClient() {
  document.getElementById("add-client-form").style.display = "block";
  document.getElementById("new-client-name").value = "";
  document.getElementById("new-client-ga4").value = "";
  document.getElementById("new-client-gsc").value = "";
  document.getElementById("new-client-gads").value = "";
  document.getElementById("new-client-gbp-loc").value = "";
  document.getElementById("new-client-gbp-acct").value = "";
  document.getElementById("new-client-drive").value = "";
  document.getElementById("new-client-website").value = "";
  document.getElementById("new-client-shopify").value = "";
  document.getElementById("new-client-meta").value = "";
}

async function addClient() {
  const name = document.getElementById("new-client-name").value.trim();
  if (!name) { toast("Client name is required", "error"); return; }

  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
  const profile = { name };

  const fields = {
    ga4_property_id: "new-client-ga4",
    gsc_site_url: "new-client-gsc",
    google_ads_customer_id: "new-client-gads",
    gbp_location_id: "new-client-gbp-loc",
    gbp_account_id: "new-client-gbp-acct",
    gdrive_folder_id: "new-client-drive",
    website_url: "new-client-website",
    shopify_store_url: "new-client-shopify",
    meta_ad_account_id: "new-client-meta",
  };

  for (const [key, elId] of Object.entries(fields)) {
    const val = document.getElementById(elId).value.trim();
    if (val) profile[key] = val;
  }

  try {
    await fetchJSON("/admin/clients", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ slug, profile }),
    });
    toast("Client " + name + " saved", "success");
    document.getElementById("add-client-form").style.display = "none";
    loadClients();
  } catch (e) {
    toast("Failed to save: " + e.message, "error");
  }
}

async function editClient(slug) {
  const clients = await fetchJSON("/admin/clients");
  const profile = clients[slug];
  if (!profile) return;

  document.getElementById("add-client-form").style.display = "block";
  document.getElementById("new-client-name").value = profile.name || slug;
  document.getElementById("new-client-ga4").value = profile.ga4_property_id || "";
  document.getElementById("new-client-gsc").value = profile.gsc_site_url || "";
  document.getElementById("new-client-gads").value = profile.google_ads_customer_id || "";
  document.getElementById("new-client-gbp-loc").value = profile.gbp_location_id || "";
  document.getElementById("new-client-gbp-acct").value = profile.gbp_account_id || "";
  document.getElementById("new-client-drive").value = profile.gdrive_folder_id || "";
  document.getElementById("new-client-website").value = profile.website_url || "";
  document.getElementById("new-client-shopify").value = profile.shopify_store_url || "";
  document.getElementById("new-client-meta").value = profile.meta_ad_account_id || "";
  window.scrollTo({top: 0, behavior: "smooth"});
}

async function deleteClient(slug) {
  if (!confirm("Delete client " + slug + "?")) return;
  try {
    await fetch("/admin/clients/" + slug, { method: "DELETE" });
    toast("Client deleted", "success");
    loadClients();
  } catch (e) {
    toast("Failed to delete: " + e.message, "error");
  }
}

loadDashboard();
</script>
</body>
</html>
"""
