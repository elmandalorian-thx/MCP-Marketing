"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";
import { PLATFORMS } from "@/lib/utils";

// Platforms that use OAuth (one-click connect)
const OAUTH_PLATFORMS: Record<string, { label: string; color: string; endpoint: string; icon: string; services?: string[] }> = {
  google: {
    label: "Google Services",
    color: "#4285f4",
    endpoint: "/api/oauth/google",
    icon: "G",
    services: ["Google Ads", "GA4", "Search Console", "YouTube", "Google Drive", "Business Profile"],
  },
  meta: {
    label: "Meta / Facebook",
    color: "#1877f2",
    endpoint: "/api/oauth/meta",
    icon: "f",
  },
  linkedin: {
    label: "LinkedIn",
    color: "#0a66c2",
    endpoint: "/api/oauth/linkedin",
    icon: "in",
  },
};

// Platforms that need manual API key entry
const MANUAL_PLATFORMS = Object.entries(PLATFORMS).filter(
  ([key]) => !["google_ads", "ga4", "search_console", "youtube", "google_drive", "google_business_profile", "meta", "linkedin", "google_trends", "pagespeed", "builtwith"].includes(key)
);

// Google services that get connected via Google OAuth
const GOOGLE_SERVICES = ["google_ads", "ga4", "search_console", "youtube", "google_drive", "google_business_profile"];

export default function ConnectPage() {
  const [connections, setConnections] = useState<Record<string, boolean>>({});
  const [manualSelected, setManualSelected] = useState<string | null>(null);
  const [creds, setCreds] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    // Check URL params for OAuth callback results
    const params = new URLSearchParams(window.location.search);
    if (params.get("success")) {
      setMsg({ type: "success", text: `${params.get("success")} connected successfully!` });
      window.history.replaceState({}, "", "/connect");
    }
    if (params.get("error")) {
      setMsg({ type: "error", text: `Connection failed: ${params.get("error")}` });
      window.history.replaceState({}, "", "/connect");
    }

    // Load existing connections
    fetch("/api/connections").then(r => r.json()).then(data => {
      if (Array.isArray(data)) {
        const map: Record<string, boolean> = {};
        data.forEach((c: any) => { if (c.isActive) map[c.platform] = true; });
        setConnections(map);
      }
    }).catch(() => {});
  }, []);

  const googleConnected = GOOGLE_SERVICES.some(s => connections[s]);
  const googleServiceCount = GOOGLE_SERVICES.filter(s => connections[s]).length;

  async function handleManualSave() {
    if (!manualSelected) return;
    setSaving(true); setMsg(null);
    try {
      const res = await fetch("/api/connections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ platform: manualSelected, credentials: creds }),
      });
      if (res.ok) {
        setConnections(p => ({ ...p, [manualSelected]: true }));
        setMsg({ type: "success", text: `${PLATFORMS[manualSelected]?.label} connected!` });
        setManualSelected(null); setCreds({});
      } else {
        const d = await res.json();
        setMsg({ type: "error", text: d.error || "Failed to save." });
      }
    } catch { setMsg({ type: "error", text: "Network error." }); }
    setSaving(false);
  }

  return (
    <>
      <Topbar title="Connections" />
      <div className="p-8">
        <p className="text-[0.82rem] text-[#9A9A9A] mb-6">
          Connect your marketing platforms. OAuth platforms use one-click authorization — no API keys needed.
        </p>

        {msg && (
          <div className={`mb-6 px-4 py-3 rounded-xl text-[0.8rem] font-medium animate-in ${
            msg.type === "success" ? "bg-[#6bd098]/10 border border-[#6bd098]/20 text-[#4caf50]" : "bg-[#ef8157]/8 border border-[#ef8157]/20 text-[#ef8157]"
          }`}>{msg.text}</div>
        )}

        {/* ── OAuth Platforms ── */}
        <div className="mb-8">
          <h2 className="text-[0.75rem] font-bold text-[#9A9A9A] uppercase tracking-wider mb-4">One-Click Connect</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Google Services (big card) */}
            <div className="card p-6 lg:col-span-2">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm" style={{ background: "linear-gradient(135deg, #4285f4, #34a853, #fbbc05, #ea4335)" }}>
                  G
                </div>
                <div className="flex-1">
                  <h3 className="text-[1rem] font-bold text-[#252422]">Google Services</h3>
                  <p className="text-[0.78rem] text-[#9A9A9A] mt-0.5">
                    One authorization connects all Google marketing platforms
                  </p>
                </div>
                {googleConnected && (
                  <span className="badge badge-success">{googleServiceCount} connected</span>
                )}
              </div>

              {/* Google services grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-5">
                {[
                  { key: "google_ads", label: "Google Ads", icon: "📢" },
                  { key: "ga4", label: "GA4 Analytics", icon: "📊" },
                  { key: "search_console", label: "Search Console", icon: "🔍" },
                  { key: "youtube", label: "YouTube", icon: "🎬" },
                  { key: "google_drive", label: "Google Drive", icon: "📁" },
                  { key: "google_business_profile", label: "Business Profile", icon: "📍" },
                ].map(svc => (
                  <div key={svc.key} className={`flex items-center gap-2 px-3 py-2 rounded-lg text-[0.78rem] font-medium ${
                    connections[svc.key]
                      ? "bg-[#6bd098]/8 text-[#4caf50]"
                      : "bg-[#f4f3ef] text-[#9A9A9A]"
                  }`}>
                    <span>{connections[svc.key] ? "✅" : svc.icon}</span>
                    {svc.label}
                  </div>
                ))}
              </div>

              <a
                href="/api/oauth/google"
                className="btn btn-primary btn-lg w-full no-underline"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="white" fillOpacity="0.9"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="white" fillOpacity="0.7"/>
                </svg>
                {googleConnected ? "Reconnect Google Services" : "Connect with Google"}
              </a>
            </div>

            {/* Meta + LinkedIn */}
            <div className="space-y-4">
              {/* Meta */}
              <div className="card p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-sm" style={{ background: "#1877f2" }}>
                    f
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[0.88rem] font-bold text-[#252422]">Meta / Facebook</h3>
                    <p className="text-[0.7rem] text-[#9A9A9A]">Ads, Pages, Audiences</p>
                  </div>
                  {connections.meta && <span className="badge badge-success">Connected</span>}
                </div>
                <a href="/api/oauth/meta" className="btn btn-outline w-full no-underline text-[#1877f2] border-[#1877f2]/30 hover:bg-[#1877f2]/4">
                  {connections.meta ? "Reconnect" : "Connect with Meta"}
                </a>
              </div>

              {/* LinkedIn */}
              <div className="card p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xs shadow-sm" style={{ background: "#0a66c2" }}>
                    in
                  </div>
                  <div className="flex-1">
                    <h3 className="text-[0.88rem] font-bold text-[#252422]">LinkedIn</h3>
                    <p className="text-[0.7rem] text-[#9A9A9A]">Company pages, Ads</p>
                  </div>
                  {connections.linkedin && <span className="badge badge-success">Connected</span>}
                </div>
                <a href="/api/oauth/linkedin" className="btn btn-outline w-full no-underline text-[#0a66c2] border-[#0a66c2]/30 hover:bg-[#0a66c2]/4">
                  {connections.linkedin ? "Reconnect" : "Connect with LinkedIn"}
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* ── Always Available ── */}
        <div className="mb-8">
          <h2 className="text-[0.75rem] font-bold text-[#9A9A9A] uppercase tracking-wider mb-4">Always Available (No Setup)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { key: "pagespeed", label: "PageSpeed", icon: "⚡", color: "#06b6d4" },
              { key: "google_trends", label: "Google Trends", icon: "📈", color: "#4285f4" },
              { key: "builtwith", label: "BuiltWith", icon: "🔧", color: "#3eab49" },
              { key: "reddit", label: "Reddit", icon: "🟠", color: "#ff4500" },
            ].map(p => (
              <div key={p.key} className="card p-4 text-center">
                <div className="text-xl mb-1">{p.icon}</div>
                <div className="text-[0.78rem] font-semibold text-[#252422]">{p.label}</div>
                <span className="badge badge-success mt-2">Ready</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Manual API Key Platforms ── */}
        <div>
          <h2 className="text-[0.75rem] font-bold text-[#9A9A9A] uppercase tracking-wider mb-4">API Key Platforms</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {MANUAL_PLATFORMS.map(([key, platform]) => {
              const connected = connections[key];
              const isSelected = manualSelected === key;

              return (
                <div
                  key={key}
                  className={`card p-5 cursor-pointer transition-all ${isSelected ? "ring-2 ring-[#51cbce]" : ""}`}
                  onClick={() => {
                    setManualSelected(isSelected ? null : key);
                    setCreds({}); setMsg(null);
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-xs" style={{ background: platform.color }}>
                        {platform.label.substring(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-[0.82rem] font-bold text-[#252422]">{platform.label}</div>
                        <div className="text-[0.68rem] text-[#9A9A9A]">{platform.requiredCreds.length} credential{platform.requiredCreds.length > 1 ? "s" : ""}</div>
                      </div>
                    </div>
                    {connected ? <span className="badge badge-success">Connected</span> : <span className="badge badge-muted">Not Set</span>}
                  </div>

                  {isSelected && platform.requiredCreds.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[#eee]" onClick={e => e.stopPropagation()}>
                      <div className="space-y-3">
                        {platform.requiredCreds.map(cred => (
                          <div key={cred}>
                            <label className="input-label">{cred}</label>
                            <input type="password" className="input" placeholder={`Enter ${cred}`} value={creds[cred] || ""} onChange={e => setCreds(p => ({ ...p, [cred]: e.target.value }))} />
                          </div>
                        ))}
                      </div>
                      <button onClick={handleManualSave} disabled={saving} className="btn btn-primary w-full mt-4 disabled:opacity-50">
                        {saving ? "Saving..." : "Save Connection"}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
