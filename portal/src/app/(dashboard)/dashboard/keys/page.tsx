"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

interface KeyInfo {
  id: string;
  prefix: string;
  label: string;
  isActive: boolean;
  createdAt: string;
  lastUsedAt: string | null;
}

export default function KeysPage() {
  const [keys, setKeys] = useState<KeyInfo[]>([]);
  const [label, setLabel] = useState("");
  const [creating, setCreating] = useState(false);
  const [newKey, setNewKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetch("/api/keys").then(r => r.json()).then(data => {
      if (Array.isArray(data)) setKeys(data);
    }).catch(() => {});
  }, []);

  async function createKey() {
    if (!label.trim()) return;
    setCreating(true);
    try {
      const res = await fetch("/api/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label }),
      });
      if (res.ok) {
        const data = await res.json();
        setNewKey(data.rawKey);
        setKeys(prev => [{ id: data.id, prefix: data.prefix, label, isActive: true, createdAt: new Date().toISOString(), lastUsedAt: null }, ...prev]);
        setLabel("");
        setShowCreate(false);
      }
    } finally { setCreating(false); }
  }

  async function revokeKey(id: string) {
    const res = await fetch(`/api/keys?id=${id}`, { method: "DELETE" });
    if (res.ok) setKeys(prev => prev.map(k => k.id === id ? { ...k, isActive: false } : k));
  }

  function copyKey() {
    if (newKey) {
      navigator.clipboard.writeText(newKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  const activeKeys = keys.filter(k => k.isActive);
  const revokedKeys = keys.filter(k => !k.isActive);

  return (
    <>
      <Topbar title="API Keys" />
      <div className="p-8">
        {/* New key revealed */}
        {newKey && (
          <div className="card p-6 mb-6 border-[#6bd098]/30 bg-[#6bd098]/4 animate-in">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#6bd098] animate-pulse" />
                <span className="text-[0.82rem] font-bold text-[#4caf50]">API Key Created</span>
              </div>
              <span className="badge badge-warning">Shown only once</span>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <code className="flex-1 bg-white border border-[#6bd098]/20 rounded-lg px-4 py-3 text-[0.82rem] font-mono text-[#252422] select-all">
                {newKey}
              </code>
              <button onClick={copyKey} className="btn btn-primary btn-sm">
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <button onClick={() => setNewKey(null)} className="text-[0.72rem] text-[#9A9A9A] hover:text-[#252422] transition-colors">
              I&apos;ve saved it — dismiss
            </button>
          </div>
        )}

        {/* Header + create button */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-[0.82rem] text-[#9A9A9A]">{activeKeys.length} active key{activeKeys.length !== 1 ? "s" : ""}</p>
          <button onClick={() => setShowCreate(!showCreate)} className="btn btn-primary">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg>
            New Key
          </button>
        </div>

        {/* Create form */}
        {showCreate && (
          <div className="card p-5 mb-6 animate-in">
            <h3 className="text-[0.85rem] font-bold mb-4">Create New API Key</h3>
            <div className="flex gap-3">
              <input
                type="text"
                className="input flex-1"
                placeholder="Key label (e.g., Claude Desktop, Production)"
                value={label}
                onChange={e => setLabel(e.target.value)}
                onKeyDown={e => e.key === "Enter" && createKey()}
                autoFocus
              />
              <button onClick={createKey} disabled={creating || !label.trim()} className="btn btn-success disabled:opacity-50">
                {creating ? "Creating..." : "Create"}
              </button>
              <button onClick={() => { setShowCreate(false); setLabel(""); }} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Active keys */}
        <div className="card mb-6">
          <div className="px-6 py-4 border-b border-[#eee]">
            <h3 className="text-[0.85rem] font-bold">Active Keys</h3>
          </div>
          {activeKeys.length === 0 ? (
            <div className="px-6 py-10 text-center">
              <div className="text-2xl mb-2">🔑</div>
              <p className="text-[0.82rem] text-[#9A9A9A]">No API keys yet. Create one to get started.</p>
            </div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {activeKeys.map(key => (
                <div key={key.id} className="px-6 py-4 flex items-center justify-between hover:bg-[#fafaf8] transition-colors group">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <code className="text-[0.8rem] font-mono font-semibold text-[#252422] bg-[#f4f3ef] px-2.5 py-1 rounded-md">{key.prefix}...</code>
                      <span className="text-[0.82rem] font-semibold text-[#252422]">{key.label}</span>
                    </div>
                    <div className="text-[0.7rem] text-[#9A9A9A] mt-1">
                      Created {new Date(key.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                      {key.lastUsedAt && ` · Last used ${new Date(key.lastUsedAt).toLocaleDateString()}`}
                    </div>
                  </div>
                  <button
                    onClick={() => revokeKey(key.id)}
                    className="btn btn-outline btn-sm text-[#ef8157] border-[#ef8157]/30 opacity-0 group-hover:opacity-100 hover:bg-[#ef8157]/5 transition-all"
                  >
                    Revoke
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Revoked keys */}
        {revokedKeys.length > 0 && (
          <div className="card mb-6 opacity-60">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold text-[#9A9A9A]">Revoked Keys</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {revokedKeys.map(key => (
                <div key={key.id} className="px-6 py-3 flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <code className="text-[0.78rem] font-mono text-[#9A9A9A] line-through">{key.prefix}...</code>
                    <span className="text-[0.78rem] text-[#9A9A9A]">{key.label}</span>
                  </div>
                  <span className="badge badge-danger">Revoked</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Setup instructions */}
        <div className="card p-6">
          <h3 className="text-[0.85rem] font-bold mb-4">Quick Setup</h3>
          <div className="space-y-4">
            <div>
              <div className="text-[0.75rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-2">Claude Desktop</div>
              <pre className="bg-[#252422] text-[#e8e6df] rounded-xl p-4 text-[0.78rem] font-mono overflow-x-auto leading-relaxed">
{`{
  "mcpServers": {
    "marketing": {
      "url": "https://marketingmcp.statika.net/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}`}
              </pre>
            </div>
            <div>
              <div className="text-[0.75rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-2">Claude Code</div>
              <pre className="bg-[#252422] text-[#e8e6df] rounded-xl p-4 text-[0.78rem] font-mono overflow-x-auto">
{`claude mcp add marketing https://marketingmcp.statika.net/mcp \\
  --header "Authorization: Bearer YOUR_API_KEY"`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
