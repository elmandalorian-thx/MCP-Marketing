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

  .container { max-width:1100px; margin:0 auto; padding:2rem 1.5rem; }

  /* Header */
  header { display:flex; justify-content:space-between; align-items:center;
           margin-bottom:2rem; flex-wrap:wrap; gap:1rem; }
  header h1 { font-size:1.5rem; font-weight:700; }
  header h1 span { color:var(--accent); }
  .health-badge { background:var(--surface); padding:0.4rem 1rem;
                   border-radius:20px; font-size:0.85rem; color:var(--muted); }
  .health-badge .dot { display:inline-block; width:8px; height:8px;
                        border-radius:50%; margin-right:6px; vertical-align:middle; }
  .health-badge .dot.ok { background:var(--green); }

  /* Cards grid */
  .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
           gap:1.25rem; margin-bottom:2rem; }
  .card { background:var(--surface); border-radius:var(--radius); padding:1.25rem;
          border:1px solid var(--surface2); transition:border-color .2s; }
  .card:hover { border-color:var(--accent); }
  .card-header { display:flex; justify-content:space-between; align-items:center;
                 margin-bottom:0.75rem; }
  .card-title { font-weight:600; font-size:1.05rem; }
  .badge { padding:0.2rem 0.65rem; border-radius:12px; font-size:0.75rem;
           font-weight:600; text-transform:uppercase; letter-spacing:0.03em; }
  .badge.configured { background:rgba(74,222,128,.15); color:var(--green); }
  .badge.partial { background:rgba(251,191,36,.15); color:var(--amber); }
  .badge.not_configured { background:rgba(248,113,113,.12); color:var(--red); }

  .cred-list { list-style:none; margin:0.5rem 0; }
  .cred-list li { font-size:0.85rem; color:var(--muted); padding:0.15rem 0; }
  .cred-list li .check { color:var(--green); margin-right:4px; }
  .cred-list li .cross { color:var(--red); margin-right:4px; }

  /* Buttons */
  .btn { display:inline-block; padding:0.4rem 0.9rem; border:none;
         border-radius:6px; font-size:0.8rem; cursor:pointer;
         font-weight:600; transition:opacity .2s; margin-top:0.5rem; margin-right:0.4rem; }
  .btn:hover { opacity:0.85; }
  .btn-primary { background:var(--accent); color:#0f172a; }
  .btn-outline { background:transparent; border:1px solid var(--surface2); color:var(--muted); }
  .btn-outline:hover { border-color:var(--accent); color:var(--accent); }

  /* Inline form */
  .config-form { display:none; margin-top:0.75rem; }
  .config-form.open { display:block; }
  .config-form label { display:block; font-size:0.8rem; color:var(--muted);
                        margin-top:0.5rem; }
  .config-form input { width:100%; padding:0.45rem 0.6rem; margin-top:0.2rem;
                        background:var(--bg); border:1px solid var(--surface2);
                        border-radius:6px; color:var(--text); font-size:0.85rem; }
  .config-form input:focus { outline:none; border-color:var(--accent); }
  .form-actions { margin-top:0.75rem; }

  /* Tools table */
  .section-title { font-size:1.1rem; font-weight:600; margin:2rem 0 1rem; }
  table { width:100%; border-collapse:collapse; background:var(--surface);
          border-radius:var(--radius); overflow:hidden; }
  th { text-align:left; padding:0.65rem 1rem; background:var(--surface2);
       font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em;
       color:var(--muted); }
  td { padding:0.6rem 1rem; border-top:1px solid var(--surface2); font-size:0.9rem; }
  code { background:var(--bg); padding:0.15rem 0.4rem; border-radius:4px;
         font-size:0.82rem; }

  /* Toast */
  .toast { position:fixed; bottom:2rem; right:2rem; padding:0.8rem 1.4rem;
           border-radius:8px; font-size:0.9rem; display:none; z-index:100;
           box-shadow:0 4px 20px rgba(0,0,0,.4); }
  .toast.success { background:var(--green); color:#0f172a; }
  .toast.error { background:var(--red); color:#fff; }
  .toast.show { display:block; animation:slideIn .3s ease; }
  @keyframes slideIn { from{transform:translateY(20px);opacity:0} to{transform:none;opacity:1} }

  /* Responsive */
  @media(max-width:640px) {
    .cards { grid-template-columns:1fr; }
    header { flex-direction:column; align-items:flex-start; }
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

  <div class="cards" id="cards"></div>

  <div class="section-title">Tools (14)</div>
  <table>
    <thead>
      <tr><th>Tool</th><th>Integration</th><th>Status</th></tr>
    </thead>
    <tbody id="tools-body"></tbody>
  </table>
</div>

<div class="toast" id="toast"></div>

<script>
const TOOL_MAP = {
  pagespeed_audit: "pagespeed",
  gads_keyword_ideas: "google_ads",
  gsc_search_queries: "search_console",
  ga4_organic_performance: "ga4",
  meta_interest_targeting: "meta",
  google_trends_explorer: "pagespeed",  // no auth
  youtube_topic_research: "youtube",
  reddit_topic_research: "reddit",
  gbp_insights: "google_business_profile",
  gdrive_list_files: "google_drive",
  gdrive_search: "google_drive",
  gdrive_read_file: "google_drive",
  gdrive_create_doc: "google_drive",
  gdrive_update_doc: "google_drive",
};
const NO_AUTH_TOOLS = ["pagespeed_audit", "google_trends_explorer"];

function toast(msg, type) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "toast " + type + " show";
  setTimeout(() => el.classList.remove("show"), 3000);
}

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  return res.json();
}

async function loadDashboard() {
  const [creds, health] = await Promise.all([
    fetchJSON("/admin/credentials"),
    fetchJSON("/admin/health"),
  ]);

  // Health badge
  document.getElementById("health-text").textContent =
    health.tools + " tools | Python " + health.python_version;

  // Integration cards
  const container = document.getElementById("cards");
  container.innerHTML = "";
  for (const [key, info] of Object.entries(creds)) {
    const card = document.createElement("div");
    card.className = "card";
    const allVars = {...info.required, ...info.optional};
    const credListHTML = Object.entries(allVars).map(([v, ok]) =>
      `<li>${ok ? '<span class="check">&#10003;</span>' : '<span class="cross">&#10007;</span>'}${v}${info.optional[v] !== undefined ? ' <em>(optional)</em>' : ''}</li>`
    ).join("");

    const formFieldsHTML = Object.keys(allVars).map(v =>
      `<label>${v}<input type="password" name="${v}" placeholder="${allVars[v] ? '(configured)' : '(not set)'}"></label>`
    ).join("");

    card.innerHTML = `
      <div class="card-header">
        <div class="card-title">${info.label}</div>
        <span class="badge ${info.status}">${info.status.replace("_", " ")}</span>
      </div>
      <ul class="cred-list">${credListHTML}</ul>
      <button class="btn btn-primary" onclick="toggleForm(this)">Configure</button>
      <button class="btn btn-outline" onclick="testConnection('${key}', this)">Test</button>
      <div class="config-form" data-integration="${key}">
        ${formFieldsHTML}
        <div class="form-actions">
          <button class="btn btn-primary" onclick="saveCredentials('${key}', this)">Save</button>
          <button class="btn btn-outline" onclick="toggleForm(this)">Cancel</button>
        </div>
      </div>
    `;
    container.appendChild(card);
  }

  // Tools table
  const tbody = document.getElementById("tools-body");
  tbody.innerHTML = "";
  for (const [tool, integration] of Object.entries(TOOL_MAP)) {
    const isNoAuth = NO_AUTH_TOOLS.includes(tool);
    const intInfo = creds[integration];
    let status = "Available";
    let statusStyle = "color:var(--green)";
    if (!isNoAuth && intInfo && intInfo.status !== "configured") {
      status = "Needs config";
      statusStyle = "color:var(--amber)";
    }
    tbody.innerHTML += `<tr>
      <td><code>${tool}</code></td>
      <td>${isNoAuth ? "No auth" : (intInfo ? intInfo.label : integration)}</td>
      <td style="${statusStyle}">${status}</td>
    </tr>`;
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

loadDashboard();
</script>
</body>
</html>
"""
