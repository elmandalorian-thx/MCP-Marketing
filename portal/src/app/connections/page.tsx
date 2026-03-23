"use client";

import { useState } from "react";
import { PLATFORMS } from "@/lib/utils";

type ConnectionStatus = "connected" | "not_connected";

export default function ConnectionsPage() {
  const [connections, setConnections] = useState<Record<string, ConnectionStatus>>({});
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  async function handleSave() {
    if (!selectedPlatform) return;
    setSaving(true);
    setMessage("");

    try {
      const res = await fetch("/api/connections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          platform: selectedPlatform,
          credentials,
        }),
      });

      if (res.ok) {
        setConnections((prev) => ({ ...prev, [selectedPlatform]: "connected" }));
        setMessage("Connection saved successfully!");
        setSelectedPlatform(null);
        setCredentials({});
      } else {
        const data = await res.json();
        setMessage(data.error || "Failed to save connection");
      }
    } catch {
      setMessage("Network error. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Platform Connections</h1>
        <p className="text-gray-500 text-sm mt-1">
          Connect your marketing platforms to enable AI-powered tools.
        </p>
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-lg text-sm ${
            message.includes("success")
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-red-50 text-red-700 border border-red-200"
          }`}
        >
          {message}
        </div>
      )}

      {/* Platform grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(PLATFORMS).map(([key, platform]) => {
          const status = connections[key] || "not_connected";
          const isSelected = selectedPlatform === key;

          return (
            <div
              key={key}
              className={`bg-white rounded-xl border p-5 transition-all cursor-pointer ${
                isSelected
                  ? "border-purple-400 shadow-lg shadow-purple-100"
                  : status === "connected"
                  ? "border-green-200"
                  : "border-gray-200 hover:border-purple-200 hover:shadow-sm"
              }`}
              onClick={() => {
                setSelectedPlatform(isSelected ? null : key);
                setCredentials({});
                setMessage("");
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-xs"
                    style={{ background: platform.color }}
                  >
                    {platform.label.substring(0, 2)}
                  </div>
                  <div>
                    <div className="font-semibold text-sm">{platform.label}</div>
                    <div className="text-xs text-gray-400">
                      {platform.requiredCreds.length === 0
                        ? "No credentials needed"
                        : `${platform.requiredCreds.length} credential${platform.requiredCreds.length > 1 ? "s" : ""}`}
                    </div>
                  </div>
                </div>
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded-full ${
                    status === "connected"
                      ? "bg-green-50 text-green-600"
                      : "bg-gray-50 text-gray-400"
                  }`}
                >
                  {status === "connected" ? "Connected" : "Not Set"}
                </span>
              </div>

              {/* Credential form (expanded) */}
              {isSelected && platform.requiredCreds.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-100" onClick={(e) => e.stopPropagation()}>
                  <div className="space-y-3">
                    {platform.requiredCreds.map((cred) => (
                      <div key={cred}>
                        <label className="block text-xs font-medium text-gray-500 mb-1">
                          {cred}
                        </label>
                        <input
                          type="password"
                          placeholder={`Enter ${cred}`}
                          value={credentials[cred] || ""}
                          onChange={(e) =>
                            setCredentials((prev) => ({ ...prev, [cred]: e.target.value }))
                          }
                          className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-100"
                        />
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="mt-4 w-full py-2.5 rounded-lg bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {saving ? "Saving..." : "Save Connection"}
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
