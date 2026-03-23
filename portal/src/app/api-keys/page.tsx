"use client";

import { useState } from "react";

interface ApiKeyDisplay {
  id: string;
  prefix: string;
  label: string;
  createdAt: string;
  lastUsed: string | null;
  isActive: boolean;
}

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKeyDisplay[]>([]);
  const [newKeyLabel, setNewKeyLabel] = useState("");
  const [creating, setCreating] = useState(false);
  const [newRawKey, setNewRawKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  async function createKey() {
    if (!newKeyLabel.trim()) return;
    setCreating(true);

    try {
      const res = await fetch("/api/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label: newKeyLabel }),
      });

      if (res.ok) {
        const data = await res.json();
        setNewRawKey(data.rawKey);
        setKeys((prev) => [
          {
            id: data.id,
            prefix: data.prefix,
            label: newKeyLabel,
            createdAt: new Date().toISOString(),
            lastUsed: null,
            isActive: true,
          },
          ...prev,
        ]);
        setNewKeyLabel("");
      }
    } finally {
      setCreating(false);
    }
  }

  async function revokeKey(id: string) {
    const res = await fetch(`/api/keys?id=${id}`, { method: "DELETE" });
    if (res.ok) {
      setKeys((prev) => prev.map((k) => (k.id === id ? { ...k, isActive: false } : k)));
    }
  }

  function copyKey() {
    if (newRawKey) {
      navigator.clipboard.writeText(newRawKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">API Keys</h1>
        <p className="text-gray-500 text-sm mt-1">
          Create API keys to connect your AI tools to Marketing MCP.
        </p>
      </div>

      {/* New key revealed */}
      {newRawKey && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-green-700">
              New API Key Created
            </span>
            <span className="text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
              Copy now — shown only once
            </span>
          </div>
          <div className="flex items-center gap-2">
            <code className="flex-1 bg-white border border-green-200 rounded-lg px-4 py-2.5 text-sm font-mono text-green-800 select-all">
              {newRawKey}
            </code>
            <button
              onClick={copyKey}
              className="px-4 py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <button
            onClick={() => setNewRawKey(null)}
            className="mt-3 text-xs text-green-600 hover:underline"
          >
            I&apos;ve saved it, dismiss this
          </button>
        </div>
      )}

      {/* Create new key */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="font-semibold mb-4">Create New Key</h2>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Key label (e.g., Production, Claude Desktop)"
            value={newKeyLabel}
            onChange={(e) => setNewKeyLabel(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && createKey()}
            className="flex-1 px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-100"
          />
          <button
            onClick={createKey}
            disabled={creating || !newKeyLabel.trim()}
            className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create Key"}
          </button>
        </div>
      </div>

      {/* Key list */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-semibold">Your API Keys</h2>
        </div>
        {keys.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm">
            No API keys yet. Create one above to get started.
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {keys.map((key) => (
              <div key={key.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm">{key.prefix}...</span>
                    <span className="text-sm text-gray-600">{key.label}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        key.isActive
                          ? "bg-green-50 text-green-600"
                          : "bg-red-50 text-red-500"
                      }`}
                    >
                      {key.isActive ? "Active" : "Revoked"}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Created {new Date(key.createdAt).toLocaleDateString()}
                    {key.lastUsed && ` · Last used ${new Date(key.lastUsed).toLocaleDateString()}`}
                  </div>
                </div>
                {key.isActive && (
                  <button
                    onClick={() => revokeKey(key.id)}
                    className="text-xs text-red-500 hover:text-red-700 font-medium px-3 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
                  >
                    Revoke
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Setup instructions */}
      <div className="mt-8 bg-purple-50 border border-purple-100 rounded-xl p-6">
        <h3 className="font-semibold text-purple-900 mb-3">How to use your API key</h3>
        <div className="space-y-3 text-sm text-purple-800">
          <div>
            <strong>Claude Desktop</strong> — Add to <code className="bg-purple-100 px-1.5 py-0.5 rounded text-xs">claude_desktop_config.json</code>:
          </div>
          <pre className="bg-white border border-purple-200 rounded-lg p-3 text-xs font-mono overflow-x-auto">
{`{
  "mcpServers": {
    "marketing": {
      "url": "https://marketingmcp.statika.net/mcp",
      "headers": {
        "Authorization": "Bearer mk_live_YOUR_KEY_HERE"
      }
    }
  }
}`}
          </pre>
          <div>
            <strong>Claude Code:</strong>
          </div>
          <pre className="bg-white border border-purple-200 rounded-lg p-3 text-xs font-mono">
            claude mcp add marketing https://marketingmcp.statika.net/mcp --header &quot;Authorization: Bearer mk_live_YOUR_KEY_HERE&quot;
          </pre>
        </div>
      </div>
    </div>
  );
}
