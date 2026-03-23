"""HTML template for the Marketing MCP sales homepage."""

HOMEPAGE_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Marketing MCP — Connect Your AI to Every Marketing Platform</title>
<meta name="description" content="One MCP server. 22 marketing tools. Connect Claude, GPT, Gemini to Google Ads, Meta, GA4, YouTube, and more. Set up in 30 seconds.">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>">
<style>
/* ═══════════════════════════════════════════════════════════
   DESIGN SYSTEM
   ═══════════════════════════════════════════════════════════ */
:root {
  --bg: #fafbfc;
  --white: #ffffff;
  --text: #1a1a2e;
  --text-muted: #64748b;
  --text-light: #94a3b8;
  --border: #e2e8f0;

  /* Accent palette */
  --blue: #3b82f6;
  --purple: #8b5cf6;
  --pink: #ec4899;
  --orange: #f97316;
  --green: #10b981;
  --cyan: #06b6d4;

  /* Gradients */
  --gradient-main: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
  --gradient-warm: linear-gradient(135deg, #f97316, #ec4899, #8b5cf6);
  --gradient-cool: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6);
  --gradient-subtle: linear-gradient(135deg, rgba(59,130,246,0.05), rgba(139,92,246,0.05), rgba(236,72,153,0.05));

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
  --shadow-md: 0 4px 24px rgba(139,92,246,0.08), 0 1px 4px rgba(0,0,0,0.04);
  --shadow-lg: 0 8px 40px rgba(139,92,246,0.12), 0 2px 8px rgba(0,0,0,0.04);
  --shadow-glow: 0 0 40px rgba(139,92,246,0.15), 0 0 80px rgba(59,130,246,0.08);

  --radius: 16px;
  --radius-sm: 10px;
  --radius-xs: 6px;
}

/* ═══════════════════════════════════════════════════════════
   RESET & BASE
   ═══════════════════════════════════════════════════════════ */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-font-smoothing: antialiased; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  overflow-x: hidden;
}
a { color: var(--blue); text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; }

.container { max-width: 1140px; margin: 0 auto; padding: 0 1.5rem; }

/* ═══════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════ */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(139,92,246,0.1); }
  50% { box-shadow: 0 0 40px rgba(139,92,246,0.25); }
}
.fade-in {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ═══════════════════════════════════════════════════════════
   NAVBAR
   ═══════════════════════════════════════════════════════════ */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(226,232,240,0.6);
  transition: box-shadow 0.3s;
}
.navbar.scrolled { box-shadow: var(--shadow-sm); }
.navbar .container {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
}
.nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-weight: 800; font-size: 1.15rem; color: var(--text);
  text-decoration: none;
}
.nav-brand .logo {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--gradient-main);
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 0.85rem; font-weight: 900;
}
.nav-links { display: flex; align-items: center; gap: 2rem; }
.nav-links a {
  font-size: 0.9rem; font-weight: 500; color: var(--text-muted);
  text-decoration: none; transition: color 0.2s;
}
.nav-links a:hover { color: var(--text); text-decoration: none; }
.nav-cta {
  background: var(--gradient-main); color: white !important;
  padding: 0.5rem 1.25rem; border-radius: 8px; font-weight: 600;
  font-size: 0.85rem; transition: opacity 0.2s, transform 0.2s;
}
.nav-cta:hover { opacity: 0.9; transform: translateY(-1px); text-decoration: none !important; }

/* Mobile nav toggle */
.nav-toggle { display: none; background: none; border: none; cursor: pointer; padding: 4px; }
.nav-toggle svg { width: 24px; height: 24px; color: var(--text); }

@media (max-width: 768px) {
  .nav-links { display: none; }
  .nav-links.open {
    display: flex; flex-direction: column;
    position: absolute; top: 64px; left: 0; right: 0;
    background: white; padding: 1rem 1.5rem; gap: 1rem;
    border-bottom: 1px solid var(--border);
    box-shadow: var(--shadow-md);
  }
  .nav-toggle { display: block; }
}

/* ═══════════════════════════════════════════════════════════
   HERO
   ═══════════════════════════════════════════════════════════ */
.hero {
  padding: 8rem 0 5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; top: -40%; left: -20%; right: -20%;
  height: 80%;
  background: radial-gradient(ellipse at 50% 80%, rgba(139,92,246,0.06) 0%, transparent 70%),
              radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.04) 0%, transparent 60%),
              radial-gradient(ellipse at 80% 50%, rgba(236,72,153,0.04) 0%, transparent 60%);
  pointer-events: none;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: white; border: 1px solid var(--border);
  padding: 0.4rem 1rem; border-radius: 100px;
  font-size: 0.8rem; font-weight: 600; color: var(--purple);
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
  animation: fadeUp 0.6s ease;
}
.hero-badge .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green);
  animation: pulse-glow 2s infinite;
}
.hero h1 {
  font-size: clamp(2.2rem, 5.5vw, 3.8rem);
  font-weight: 800;
  line-height: 1.15;
  margin-bottom: 1.25rem;
  animation: fadeUp 0.6s ease 0.1s both;
  letter-spacing: -0.02em;
}
.hero h1 .gradient-text {
  background: var(--gradient-main);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero .subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--text-muted);
  max-width: 600px;
  margin: 0 auto 2rem;
  animation: fadeUp 0.6s ease 0.2s both;
}
.hero-buttons {
  display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;
  animation: fadeUp 0.6s ease 0.3s both;
}
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 0.8rem 1.75rem; border-radius: 10px;
  font-size: 1rem; font-weight: 600;
  cursor: pointer; border: none;
  transition: all 0.25s ease;
  text-decoration: none;
}
.btn-primary {
  background: var(--gradient-main); color: white;
  box-shadow: 0 4px 16px rgba(139,92,246,0.25);
}
.btn-primary:hover {
  transform: translateY(-2px); text-decoration: none; color: white;
  box-shadow: 0 6px 24px rgba(139,92,246,0.35);
}
.btn-secondary {
  background: white; color: var(--text);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.btn-secondary:hover {
  transform: translateY(-2px); text-decoration: none;
  box-shadow: var(--shadow-md); border-color: var(--purple);
}

/* Hero code preview */
.hero-preview {
  margin-top: 3.5rem;
  animation: fadeUp 0.8s ease 0.4s both;
}
.code-window {
  max-width: 680px; margin: 0 auto;
  background: #1e1e2e; border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  border: 1px solid rgba(139,92,246,0.2);
  text-align: left;
}
.code-titlebar {
  display: flex; align-items: center; gap: 8px;
  padding: 0.75rem 1rem;
  background: rgba(255,255,255,0.04);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.code-dot { width: 12px; height: 12px; border-radius: 50%; }
.code-dot.red { background: #ff5f57; }
.code-dot.yellow { background: #febc2e; }
.code-dot.green { background: #28c840; }
.code-titlebar span { margin-left: auto; font-size: 0.75rem; color: #64748b; }
.code-body {
  padding: 1.25rem 1.5rem;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 0.85rem;
  line-height: 1.8;
  color: #cdd6f4;
  overflow-x: auto;
}
.code-body .comment { color: #6c7086; }
.code-body .string { color: #a6e3a1; }
.code-body .keyword { color: #cba6f7; }
.code-body .function { color: #89b4fa; }
.code-body .prompt { color: #f9e2af; }
.code-body .response { color: #a6e3a1; }

/* ═══════════════════════════════════════════════════════════
   SECTIONS (shared)
   ═══════════════════════════════════════════════════════════ */
section { padding: 5rem 0; }
.section-label {
  display: inline-block;
  font-size: 0.75rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
  background: var(--gradient-main);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 0.75rem;
}
.section-title {
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 800; line-height: 1.2;
  margin-bottom: 1rem;
  letter-spacing: -0.01em;
}
.section-subtitle {
  font-size: 1.05rem; color: var(--text-muted);
  max-width: 560px;
}
.section-header { text-align: center; margin-bottom: 3.5rem; }
.section-header .section-subtitle { margin: 0 auto; }

/* ═══════════════════════════════════════════════════════════
   HOW IT WORKS
   ═══════════════════════════════════════════════════════════ */
.steps-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
@media (max-width: 768px) { .steps-grid { grid-template-columns: 1fr; } }
.step-card {
  background: white; border-radius: var(--radius);
  padding: 2rem 1.5rem;
  position: relative;
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}
.step-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: transparent;
}
.step-card::before {
  content: ''; position: absolute; inset: -1px;
  border-radius: calc(var(--radius) + 1px);
  background: var(--gradient-main);
  z-index: -1; opacity: 0;
  transition: opacity 0.3s;
}
.step-card:hover::before { opacity: 1; }
.step-number {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; font-weight: 800; color: white;
  margin-bottom: 1.25rem;
}
.step-card:nth-child(1) .step-number { background: linear-gradient(135deg, var(--blue), var(--cyan)); }
.step-card:nth-child(2) .step-number { background: linear-gradient(135deg, var(--purple), var(--pink)); }
.step-card:nth-child(3) .step-number { background: linear-gradient(135deg, var(--orange), var(--pink)); }
.step-card h3 { font-size: 1.15rem; font-weight: 700; margin-bottom: 0.5rem; }
.step-card p { font-size: 0.92rem; color: var(--text-muted); }

/* ═══════════════════════════════════════════════════════════
   PLATFORMS
   ═══════════════════════════════════════════════════════════ */
.platforms-section { background: white; }
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}
@media (max-width: 480px) { .platforms-grid { grid-template-columns: repeat(3, 1fr); } }
.platform-card {
  display: flex; flex-direction: column;
  align-items: center; gap: 0.6rem;
  padding: 1.25rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--bg);
  transition: all 0.25s ease;
  cursor: default;
}
.platform-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--purple);
}
.platform-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
  font-weight: 700;
  color: white;
}
.platform-card span {
  font-size: 0.78rem; font-weight: 600;
  color: var(--text-muted); text-align: center;
}

/* ═══════════════════════════════════════════════════════════
   SETUP / QUICK START
   ═══════════════════════════════════════════════════════════ */
.setup-section { background: var(--bg); }
.setup-tabs {
  display: flex; gap: 0; background: white;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  border: 1px solid var(--border); border-bottom: none;
  overflow-x: auto;
  max-width: 720px; margin: 0 auto;
}
.setup-tab {
  padding: 0.75rem 1.5rem;
  font-size: 0.85rem; font-weight: 600;
  color: var(--text-muted);
  background: none; border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
  flex: 1; text-align: center;
}
.setup-tab:hover { color: var(--text); background: rgba(139,92,246,0.03); }
.setup-tab.active {
  color: var(--purple);
  border-bottom-color: var(--purple);
  background: rgba(139,92,246,0.04);
}
.setup-content {
  max-width: 720px; margin: 0 auto;
  background: white;
  border: 1px solid var(--border);
  border-radius: 0 0 var(--radius-sm) var(--radius-sm);
  padding: 1.5rem 2rem;
  box-shadow: var(--shadow-md);
}
.setup-panel { display: none; }
.setup-panel.active { display: block; }
.setup-panel h4 {
  font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem;
}
.setup-panel p {
  font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1rem;
}
.setup-panel ol {
  padding-left: 1.25rem; margin-bottom: 1rem;
}
.setup-panel ol li {
  font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0.4rem;
}
.setup-code {
  background: #1e1e2e;
  border-radius: var(--radius-xs);
  padding: 1rem 1.25rem;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.82rem;
  color: #cdd6f4;
  overflow-x: auto;
  position: relative;
  line-height: 1.7;
  margin-bottom: 1rem;
}
.copy-btn {
  position: absolute; top: 0.5rem; right: 0.5rem;
  background: rgba(255,255,255,0.1);
  border: none; border-radius: 6px;
  padding: 0.35rem 0.65rem;
  font-size: 0.72rem; color: #94a3b8;
  cursor: pointer; transition: all 0.2s;
}
.copy-btn:hover { background: rgba(255,255,255,0.2); color: white; }
.copy-btn.copied { color: var(--green); }
.setup-note {
  font-size: 0.8rem; color: var(--text-light);
  padding: 0.75rem 1rem;
  background: rgba(139,92,246,0.04);
  border-radius: var(--radius-xs);
  border-left: 3px solid var(--purple);
}

/* ═══════════════════════════════════════════════════════════
   TOOL SHOWCASE
   ═══════════════════════════════════════════════════════════ */
.tools-section { background: white; }
.tools-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}
@media (max-width: 768px) { .tools-grid { grid-template-columns: 1fr; } }
.tool-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1.5rem;
  transition: all 0.25s ease;
}
.tool-card:hover {
  border-color: var(--purple);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.tool-prompt {
  font-size: 0.92rem; font-weight: 600;
  margin-bottom: 0.75rem;
  display: flex; align-items: flex-start; gap: 8px;
}
.tool-prompt .q {
  color: var(--purple); font-weight: 800;
  flex-shrink: 0;
}
.tool-meta {
  display: flex; align-items: center; gap: 0.75rem;
  flex-wrap: wrap;
}
.tool-name {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
  background: rgba(139,92,246,0.08);
  color: var(--purple);
  font-weight: 600;
}
.tool-api {
  font-size: 0.78rem; color: var(--text-light); font-weight: 500;
}

/* ═══════════════════════════════════════════════════════════
   PRICING
   ═══════════════════════════════════════════════════════════ */
.pricing-section { background: var(--bg); }
.pricing-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem; align-items: start;
}
@media (max-width: 900px) { .pricing-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .pricing-grid { grid-template-columns: 1fr; } }
.pricing-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 1.5rem;
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
}
.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
.pricing-card.featured {
  border-color: transparent;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}
.pricing-card.featured::before {
  content: ''; position: absolute; inset: -2px;
  border-radius: calc(var(--radius) + 2px);
  background: var(--gradient-main);
  z-index: -1;
}
.pricing-card.featured::after {
  content: 'Most Popular';
  position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
  background: var(--gradient-main); color: white;
  padding: 0.25rem 1rem; border-radius: 100px;
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pricing-name { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; }
.pricing-price {
  font-size: 2.5rem; font-weight: 800; margin-bottom: 0.25rem;
  letter-spacing: -0.02em;
}
.pricing-price span { font-size: 0.9rem; font-weight: 500; color: var(--text-muted); }
.pricing-desc { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1.5rem; }
.pricing-features { list-style: none; text-align: left; margin-bottom: 1.75rem; }
.pricing-features li {
  font-size: 0.85rem; padding: 0.35rem 0;
  display: flex; align-items: center; gap: 8px;
  color: var(--text-muted);
}
.pricing-features li .check { color: var(--green); font-weight: 700; flex-shrink: 0; }
.pricing-btn {
  display: block; width: 100%;
  padding: 0.7rem; border-radius: 8px;
  font-size: 0.9rem; font-weight: 600;
  border: 1px solid var(--border);
  background: white; color: var(--text);
  cursor: pointer; transition: all 0.2s;
  text-align: center; text-decoration: none;
}
.pricing-btn:hover {
  border-color: var(--purple);
  box-shadow: var(--shadow-sm);
  text-decoration: none;
}
.pricing-card.featured .pricing-btn {
  background: var(--gradient-main); color: white; border: none;
  box-shadow: 0 4px 12px rgba(139,92,246,0.25);
}
.pricing-card.featured .pricing-btn:hover {
  opacity: 0.9; transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(139,92,246,0.35);
}

/* ═══════════════════════════════════════════════════════════
   CTA BANNER
   ═══════════════════════════════════════════════════════════ */
.cta-banner {
  background: var(--gradient-main);
  padding: 4rem 0;
  text-align: center;
  color: white;
}
.cta-banner h2 {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 800; margin-bottom: 1rem;
}
.cta-banner p {
  font-size: 1.05rem; opacity: 0.9; margin-bottom: 2rem;
  max-width: 500px; margin-left: auto; margin-right: auto;
}
.btn-white {
  background: white; color: var(--purple);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.btn-white:hover {
  transform: translateY(-2px); text-decoration: none; color: var(--purple);
  box-shadow: 0 6px 24px rgba(0,0,0,0.15);
}

/* ═══════════════════════════════════════════════════════════
   FOOTER
   ═══════════════════════════════════════════════════════════ */
footer {
  background: white;
  border-top: 1px solid var(--border);
  padding: 3rem 0 2rem;
}
.footer-grid {
  display: flex; justify-content: space-between;
  flex-wrap: wrap; gap: 2rem;
  margin-bottom: 2rem;
}
.footer-brand { max-width: 280px; }
.footer-brand .nav-brand { margin-bottom: 0.75rem; }
.footer-brand p { font-size: 0.85rem; color: var(--text-muted); }
.footer-col h4 { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem; color: var(--text); }
.footer-col a { display: block; font-size: 0.88rem; color: var(--text-muted); padding: 0.2rem 0; transition: color 0.2s; }
.footer-col a:hover { color: var(--purple); text-decoration: none; }
.footer-bottom {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 1.5rem; border-top: 1px solid var(--border);
  font-size: 0.8rem; color: var(--text-light);
  flex-wrap: wrap; gap: 0.5rem;
}
.footer-bottom a { color: var(--text-light); }
.footer-bottom a:hover { color: var(--purple); }
</style>
</head>
<body>

<!-- ═══════════ NAVBAR ═══════════ -->
<nav class="navbar" id="navbar">
  <div class="container">
    <a href="/" class="nav-brand">
      <div class="logo">M</div>
      Marketing MCP
    </a>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Toggle menu">
      <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
    </button>
    <div class="nav-links">
      <a href="#platforms">Platforms</a>
      <a href="#setup">Setup</a>
      <a href="#tools">Tools</a>
      <a href="#pricing">Pricing</a>
      <a href="/admin" target="_blank">Dashboard</a>
      <a href="#setup" class="nav-cta">Get Started</a>
    </div>
  </div>
</nav>

<!-- ═══════════ HERO ═══════════ -->
<section class="hero">
  <div class="container">
    <div class="hero-badge">
      <span class="dot"></span>
      22 tools &middot; 10+ APIs &middot; Open source
    </div>
    <h1>
      Connect your AI to<br>
      <span class="gradient-text">every marketing platform</span>
    </h1>
    <p class="subtitle">
      One MCP server gives Claude, GPT, and Gemini direct access to Google Ads, Meta, GA4, YouTube, Reddit, and 15+ more platforms. Set up in 30 seconds.
    </p>
    <div class="hero-buttons">
      <a href="#setup" class="btn btn-primary">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        Get Started Free
      </a>
      <a href="https://github.com/elmandalorian-thx/MCP-Marketing" target="_blank" class="btn btn-secondary">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        View on GitHub
      </a>
    </div>

    <div class="hero-preview">
      <div class="code-window">
        <div class="code-titlebar">
          <div class="code-dot red"></div>
          <div class="code-dot yellow"></div>
          <div class="code-dot green"></div>
          <span>Claude Desktop</span>
        </div>
        <div class="code-body">
<span class="prompt">You:</span> Find keyword ideas for "organic coffee beans"<br>
<br>
<span class="response">Claude:</span> I'll search Google Ads Keyword Planner for you.<br>
<br>
<span class="comment">  Keyword                        Avg. Searches  Competition</span><br>
<span class="string">  organic coffee beans            22,200         High</span><br>
<span class="string">  best organic coffee              14,800         Medium</span><br>
<span class="string">  organic coffee subscription       6,600         Low</span><br>
<span class="string">  fair trade organic coffee         4,400         Medium</span><br>
<span class="string">  organic coffee brands             3,200         High</span><br>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ HOW IT WORKS ═══════════ -->
<section id="how-it-works">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-label">How It Works</div>
      <h2 class="section-title">Three steps. Thirty seconds.</h2>
      <p class="section-subtitle">No SDKs, no wrappers, no boilerplate. Just connect and go.</p>
    </div>
    <div class="steps-grid">
      <div class="step-card fade-in">
        <div class="step-number">1</div>
        <h3>Add the server</h3>
        <p>One line in your AI tool's config. Works with Claude Desktop, Claude Code, or any MCP client.</p>
      </div>
      <div class="step-card fade-in">
        <div class="step-number">2</div>
        <h3>Connect platforms</h3>
        <p>Add your API keys via the admin dashboard or .env file. Each platform activates independently.</p>
      </div>
      <div class="step-card fade-in">
        <div class="step-number">3</div>
        <h3>Ask questions</h3>
        <p>Your AI can now pull data from Google Ads, GA4, Meta, YouTube, and more — just by asking.</p>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ PLATFORMS ═══════════ -->
<section id="platforms" class="platforms-section">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-label">Integrations</div>
      <h2 class="section-title">22 tools across every major platform</h2>
      <p class="section-subtitle">From search to social, ads to analytics. One server covers it all.</p>
    </div>
    <div class="platforms-grid fade-in">
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#4285f4,#34a853)">G</div>
        <span>Google Ads</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#f9ab00,#e37400)">GA</div>
        <span>GA4</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#4285f4,#0d652d)">SC</div>
        <span>Search Console</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#1877f2,#0059b3)">f</div>
        <span>Meta / Facebook</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#ff0000,#cc0000)">YT</div>
        <span>YouTube</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#ff4500,#ff6634)">R</div>
        <span>Reddit</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#4285f4,#1a73e8)">GT</div>
        <span>Google Trends</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#4285f4,#0f9d58)">BP</div>
        <span>Business Profile</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#0f9d58,#34a853)">GD</div>
        <span>Google Drive</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#ff6c2c,#ff4500)">SR</div>
        <span>SEMrush</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#0a66c2,#004182)">in</div>
        <span>LinkedIn</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#008373,#00a68c)">B</div>
        <span>Bing Webmaster</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#ffe01b,#241c15)">MC</div>
        <span>Mailchimp</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#00f2ea,#ff0050)">TT</div>
        <span>TikTok</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#e60023,#ad081b)">P</div>
        <span>Pinterest</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#1da1f2,#0d8bd9)">X</div>
        <span>X / Twitter</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#96bf48,#5e8e3e)">S</div>
        <span>Shopify</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#af0606,#d32323)">Y</div>
        <span>Yelp</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#ff7a59,#ff5c35)">HS</div>
        <span>HubSpot</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#3eab49,#259634)">BW</div>
        <span>BuiltWith</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:linear-gradient(135deg,#06b6d4,#0891b2)">PS</div>
        <span>PageSpeed</span>
      </div>
      <div class="platform-card">
        <div class="platform-icon" style="background:var(--gradient-main)">+</div>
        <span>More coming</span>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ QUICK SETUP ═══════════ -->
<section id="setup" class="setup-section">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-label">Quick Start</div>
      <h2 class="section-title">Set up in 30 seconds</h2>
      <p class="section-subtitle">Pick your AI tool, paste the config, done.</p>
    </div>

    <div class="fade-in">
      <div class="setup-tabs" role="tablist">
        <button class="setup-tab active" onclick="switchTab(event, 'claude-desktop')" role="tab">Claude Desktop</button>
        <button class="setup-tab" onclick="switchTab(event, 'claude-code')" role="tab">Claude Code</button>
        <button class="setup-tab" onclick="switchTab(event, 'openai')" role="tab">OpenAI / GPT</button>
        <button class="setup-tab" onclick="switchTab(event, 'other')" role="tab">Gemini / Other</button>
      </div>

      <div class="setup-content">
        <!-- Claude Desktop -->
        <div class="setup-panel active" id="tab-claude-desktop">
          <h4>Claude Desktop</h4>
          <p>Add this to your <code>claude_desktop_config.json</code>:</p>
          <ol>
            <li>Open Claude Desktop &rarr; Settings &rarr; Developer &rarr; Edit Config</li>
            <li>Add the server entry below, then restart Claude</li>
          </ol>
          <div class="setup-code" id="code-claude-desktop">
            <button class="copy-btn" onclick="copyCode('code-claude-desktop')">Copy</button>
<span style="color:#cba6f7">{</span>
  <span style="color:#89b4fa">"mcpServers"</span>: <span style="color:#cba6f7">{</span>
    <span style="color:#89b4fa">"marketing"</span>: <span style="color:#cba6f7">{</span>
      <span style="color:#89b4fa">"url"</span>: <span style="color:#a6e3a1">"https://marketingmcp.statika.net/mcp"</span>
    <span style="color:#cba6f7">}</span>
  <span style="color:#cba6f7">}</span>
<span style="color:#cba6f7">}</span>
          </div>
          <div class="setup-note">
            That's it. Claude now has access to all 22 marketing tools. Try asking: "Find keyword ideas for organic coffee"
          </div>
        </div>

        <!-- Claude Code -->
        <div class="setup-panel" id="tab-claude-code">
          <h4>Claude Code (CLI)</h4>
          <p>Run this single command in your terminal:</p>
          <div class="setup-code" id="code-claude-code">
            <button class="copy-btn" onclick="copyCode('code-claude-code')">Copy</button>
<span style="color:#a6e3a1">claude mcp add marketing https://marketingmcp.statika.net/mcp</span>
          </div>
          <div class="setup-note">
            Done. The marketing tools are now available in your Claude Code session. Try: "Audit the PageSpeed of my site"
          </div>
        </div>

        <!-- OpenAI / GPT -->
        <div class="setup-panel" id="tab-openai">
          <h4>OpenAI / GPT (via MCP client)</h4>
          <p>Use any MCP-compatible client that works with OpenAI:</p>
          <div class="setup-code" id="code-openai">
            <button class="copy-btn" onclick="copyCode('code-openai')">Copy</button>
<span style="color:#6c7086"># MCP server endpoint</span>
<span style="color:#a6e3a1">https://marketingmcp.statika.net/mcp</span>

<span style="color:#6c7086"># Transport: Streamable HTTP</span>
<span style="color:#6c7086"># Auth: Bearer token (if configured)</span>
          </div>
          <div class="setup-note">
            Point your MCP bridge or client to the endpoint above. The server speaks standard MCP over Streamable HTTP.
          </div>
        </div>

        <!-- Gemini / Other -->
        <div class="setup-panel" id="tab-other">
          <h4>Gemini / Any MCP Client</h4>
          <p>Marketing MCP works with any MCP-compatible client:</p>
          <div class="setup-code" id="code-other">
            <button class="copy-btn" onclick="copyCode('code-other')">Copy</button>
<span style="color:#6c7086"># Endpoint</span>
<span style="color:#a6e3a1">https://marketingmcp.statika.net/mcp</span>

<span style="color:#6c7086"># Protocol: MCP (Streamable HTTP)</span>
<span style="color:#6c7086"># Tools: 22 marketing tools auto-discovered</span>
          </div>
          <div class="setup-note">
            Any client that supports the Model Context Protocol can connect. Tools are auto-discovered — no manual registration needed.
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ TOOL SHOWCASE ═══════════ -->
<section id="tools" class="tools-section">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-label">What You Can Do</div>
      <h2 class="section-title">Just ask. Your AI handles the rest.</h2>
      <p class="section-subtitle">Real prompts, real tools, real marketing data.</p>
    </div>
    <div class="tools-grid fade-in">
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> Find keyword ideas for 'vegan protein powder'</div>
        <div class="tool-meta">
          <span class="tool-name">gads_keyword_ideas</span>
          <span class="tool-api">Google Ads API</span>
        </div>
      </div>
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> Show my top search queries this month</div>
        <div class="tool-meta">
          <span class="tool-name">gsc_search_queries</span>
          <span class="tool-api">Search Console</span>
        </div>
      </div>
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> What's the audience size for 'fitness' on Meta?</div>
        <div class="tool-meta">
          <span class="tool-name">meta_interest_targeting</span>
          <span class="tool-api">Meta Graph API</span>
        </div>
      </div>
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> Audit the speed of example.com</div>
        <div class="tool-meta">
          <span class="tool-name">pagespeed_audit</span>
          <span class="tool-api">PageSpeed Insights</span>
        </div>
      </div>
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> What's trending on Reddit about AI startups?</div>
        <div class="tool-meta">
          <span class="tool-name">reddit_topic_research</span>
          <span class="tool-api">Reddit / PRAW</span>
        </div>
      </div>
      <div class="tool-card">
        <div class="tool-prompt"><span class="q">&ldquo;</span> Show my organic traffic performance in GA4</div>
        <div class="tool-meta">
          <span class="tool-name">ga4_organic_performance</span>
          <span class="tool-api">GA4 Data API</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ PRICING ═══════════ -->
<section id="pricing" class="pricing-section">
  <div class="container">
    <div class="section-header fade-in">
      <div class="section-label">Pricing</div>
      <h2 class="section-title">Start free. Scale as you grow.</h2>
      <p class="section-subtitle">No credit card required. Upgrade anytime.</p>
    </div>
    <div class="pricing-grid fade-in">
      <!-- Free -->
      <div class="pricing-card">
        <div class="pricing-name">Free</div>
        <div class="pricing-price">$0<span>/mo</span></div>
        <div class="pricing-desc">For individuals exploring</div>
        <ul class="pricing-features">
          <li><span class="check">&#10003;</span> 1 seat</li>
          <li><span class="check">&#10003;</span> 3 connections</li>
          <li><span class="check">&#10003;</span> 500 calls/month</li>
          <li><span class="check">&#10003;</span> All 22 tools</li>
          <li><span class="check">&#10003;</span> Community support</li>
        </ul>
        <a href="#setup" class="pricing-btn">Get Started</a>
      </div>
      <!-- Starter -->
      <div class="pricing-card">
        <div class="pricing-name">Starter</div>
        <div class="pricing-price">$49<span>/mo</span></div>
        <div class="pricing-desc">For small teams</div>
        <ul class="pricing-features">
          <li><span class="check">&#10003;</span> 3 seats</li>
          <li><span class="check">&#10003;</span> 10 connections</li>
          <li><span class="check">&#10003;</span> 5,000 calls/month</li>
          <li><span class="check">&#10003;</span> All 22 tools</li>
          <li><span class="check">&#10003;</span> Email support</li>
        </ul>
        <a href="#setup" class="pricing-btn">Get Started</a>
      </div>
      <!-- Pro -->
      <div class="pricing-card featured">
        <div class="pricing-name">Pro</div>
        <div class="pricing-price">$149<span>/mo</span></div>
        <div class="pricing-desc">For agencies</div>
        <ul class="pricing-features">
          <li><span class="check">&#10003;</span> 10 seats</li>
          <li><span class="check">&#10003;</span> 50 connections</li>
          <li><span class="check">&#10003;</span> 50,000 calls/month</li>
          <li><span class="check">&#10003;</span> All 22 tools</li>
          <li><span class="check">&#10003;</span> Priority support</li>
          <li><span class="check">&#10003;</span> Usage analytics</li>
        </ul>
        <a href="#setup" class="pricing-btn">Get Started</a>
      </div>
      <!-- Enterprise -->
      <div class="pricing-card">
        <div class="pricing-name">Enterprise</div>
        <div class="pricing-price">Custom</div>
        <div class="pricing-desc">For large organizations</div>
        <ul class="pricing-features">
          <li><span class="check">&#10003;</span> Unlimited seats</li>
          <li><span class="check">&#10003;</span> Unlimited connections</li>
          <li><span class="check">&#10003;</span> Unlimited calls</li>
          <li><span class="check">&#10003;</span> All 22 tools</li>
          <li><span class="check">&#10003;</span> Dedicated support</li>
          <li><span class="check">&#10003;</span> Custom integrations</li>
          <li><span class="check">&#10003;</span> SLA guarantee</li>
        </ul>
        <a href="mailto:hello@statika.net" class="pricing-btn">Contact Sales</a>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════ CTA BANNER ═══════════ -->
<section class="cta-banner">
  <div class="container fade-in">
    <h2>Ready to supercharge your marketing AI?</h2>
    <p>Connect your first platform in under a minute. Free forever for personal use.</p>
    <a href="#setup" class="btn btn-white">
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
      Get Started Free
    </a>
  </div>
</section>

<!-- ═══════════ FOOTER ═══════════ -->
<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" class="nav-brand">
          <div class="logo">M</div>
          Marketing MCP
        </a>
        <p>Open-source MCP server connecting AI to marketing platforms. Built with FastMCP.</p>
      </div>
      <div class="footer-col">
        <h4>Product</h4>
        <a href="#platforms">Platforms</a>
        <a href="#tools">Tools</a>
        <a href="#pricing">Pricing</a>
        <a href="#setup">Quick Start</a>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <a href="/admin" target="_blank">Admin Dashboard</a>
        <a href="https://github.com/elmandalorian-thx/MCP-Marketing" target="_blank">GitHub</a>
        <a href="https://github.com/elmandalorian-thx/MCP-Marketing#readme" target="_blank">Documentation</a>
      </div>
      <div class="footer-col">
        <h4>Connect</h4>
        <a href="mailto:hello@statika.net">hello@statika.net</a>
        <a href="https://github.com/elmandalorian-thx" target="_blank">GitHub Profile</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2025 Marketing MCP by <a href="https://statika.net" target="_blank">Statika</a></span>
      <span>Built with <a href="https://github.com/jlowin/fastmcp" target="_blank">FastMCP</a></span>
    </div>
  </div>
</footer>

<!-- ═══════════ JAVASCRIPT ═══════════ -->
<script>
/* ── Tab switching ── */
function switchTab(e, tabId) {
  document.querySelectorAll('.setup-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.setup-panel').forEach(p => p.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById('tab-' + tabId).classList.add('active');
}

/* ── Copy code ── */
function copyCode(id) {
  const el = document.getElementById(id);
  const btn = el.querySelector('.copy-btn');
  const text = el.textContent.replace('Copy', '').trim();
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  });
}

/* ── Scroll animations ── */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

/* ── Navbar shadow on scroll ── */
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 10);
}, { passive: true });
</script>
</body>
</html>
"""
