"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Topbar } from "@/components/topbar";
import { PLATFORMS } from "@/lib/utils";

export default function ConnectPage() {
  const { data: session } = useSession();
  const [connections, setConnections] = useState<Record<string, boolean>>({});
  const [selected, setSelected] = useState<string | null>(null);
  const [creds, setCreds] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/connections").then(r => r.json()).then(data => {
      if (Array.isArray(data)) {
        const map: Record<string, boolean> = {};
        data.forEach((c: any) => { if (c.isActive) map[c.platform] = true; });
        setConnections(map);
      }
    }).catch(() => {});
  }, []);

  async function handleSave() {
    if (!selected) return;
    setSaving(true); setMsg(null);
    try {
      const res = await fetch("/api/connections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ platform: selected, credentials: creds }),
      });
      if (res.ok) {
        setConnections(p => ({ ...p, [selected]: true }));
        setMsg({ type: "success", text: `${PLATFORMS[selected]?.label} connected successfully!` });
        setSelected(null); setCreds({});
      } else {
        const d = await res.json();
        setMsg({ type: "error", text: d.error || "Failed to save." });
      }
    } catch { setMsg({ type: "error", text: "Network error." }); }
    setSaving(false);
  }

  async function handleDisconnect(platform: string) {
    const res = await fetch(`/api/connections?platform=${platform}`, { method: "DELETE" });
    if (res.ok) {
      setConnections(p => { const n = { ...p }; delete n[platform]; return n; });
      setMsg({ type: "success", text: `${PLATFORMS[platform]?.label} disconnected.` });
    }
  }

  const filtered = Object.entries(PLATFORMS).filter(([, p]) =>
    p.label.toLowerCase().includes(search.toLowerCase())
  );

  const connectedCount = Object.keys(connections).length;

  return (
    <>
      <Topbar title="Connections" />
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-[0.82rem] text-[#9A9A9A]">
              {connectedCount} platform{connectedCount !== 1 ? "s" : ""} connected
            </p>
          </div>
          <input
            type="text"
            className="input w-64"
            placeholder="Search platforms..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        {msg && (
          <div className={`mb-6 px-4 py-3 rounded-xl text-[0.8rem] font-medium animate-in ${
            msg.type === "success"
              ? "bg-[#6bd098]/10 border border-[#6bd098]/20 text-[#4caf50]"
              : "bg-[#ef8157]/8 border border-[#ef8157]/20 text-[#ef8157]"
          }`}>
            {msg.text}
          </div>
        )}

        {/* Platform grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(([key, platform]) => {
            const connected = connections[key];
            const isSelected = selected === key;

            return (
              <div
                key={key}
                className={`card p-5 cursor-pointer transition-all ${
                  isSelected ? "ring-2 ring-[#51cbce] shadow-lg" : ""
                } ${connected ? "border-[#6bd098]/30" : ""}`}
                onClick={() => {
                  if (isSelected) { setSelected(null); setCreds({}); }
                  else { setSelected(key); setCreds({}); setMsg(null); }
                }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-xs shadow-sm"
                      style={{ background: platform.color }}
                    >
                      {platform.label.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="text-[0.85rem] font-bold text-[#252422]">{platform.label}</div>
                      <div className="text-[0.7rem] text-[#9A9A9A]">
                        {platform.requiredCreds.length === 0 ? "No credentials needed" : `${platform.requiredCreds.length} credential${platform.requiredCreds.length > 1 ? "s" : ""}`}
                      </div>
                    </div>
                  </div>
                  {connected ? (
                    <span className="badge badge-success">Connected</span>
                  ) : (
                    <span className="badge badge-muted">Not Set</span>
                  )}
                </div>

                {/* Expanded credential form */}
                {isSelected && platform.requiredCreds.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-[#eee]" onClick={e => e.stopPropagation()}>
                    <div className="space-y-3">
                      {platform.requiredCreds.map(cred => (
                        <div key={cred}>
                          <label className="input-label">{cred}</label>
                          <input
                            type="password"
                            className="input"
                            placeholder={`Enter ${cred}`}
                            value={creds[cred] || ""}
                            onChange={e => setCreds(p => ({ ...p, [cred]: e.target.value }))}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="flex gap-2 mt-4">
                      <button onClick={handleSave} disabled={saving} className="btn btn-primary flex-1 disabled:opacity-50">
                        {saving ? "Saving..." : "Save Connection"}
                      </button>
                      {connected && (
                        <button onClick={() => handleDisconnect(key)} className="btn btn-danger btn-sm">
                          Disconnect
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {isSelected && platform.requiredCreds.length === 0 && (
                  <div className="mt-4 pt-4 border-t border-[#eee]">
                    <p className="text-[0.78rem] text-[#6bd098] font-medium">
                      This platform works without credentials. It&apos;s always available.
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
