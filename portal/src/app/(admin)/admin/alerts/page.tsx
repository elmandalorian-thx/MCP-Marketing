"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

interface AlertItem {
  id: number;
  tenantId: string | null;
  severity: string;
  type: string;
  title: string;
  description: string | null;
  isRead: boolean;
  resolvedAt: string | null;
  createdAt: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  info: "bg-[#51cbce]",
  warning: "bg-[#ffa726]",
  critical: "bg-[#ef8157]",
};

export default function AdminAlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [severity, setSeverity] = useState("");
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);

  function loadAlerts() {
    const params = new URLSearchParams();
    if (severity) params.set("severity", severity);
    if (unreadOnly) params.set("unread", "true");

    fetch(`/api/admin/alerts?${params}`)
      .then((r) => r.json())
      .then((d) => { setAlerts(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }

  useEffect(loadAlerts, [severity, unreadOnly]);

  async function bulkAction(action: string) {
    if (selected.size === 0) return;
    await fetch("/api/admin/alerts", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ids: Array.from(selected) }),
    });
    setSelected(new Set());
    loadAlerts();
  }

  return (
    <>
      <Topbar title="Alerts" />
      <div className="p-8">
        {/* Filters + actions */}
        <div className="flex items-center gap-4 mb-6">
          <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="px-3 py-2 border border-[#eee] rounded-lg text-[0.82rem]">
            <option value="">All Severities</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
          <label className="flex items-center gap-2 text-[0.82rem] cursor-pointer">
            <input type="checkbox" checked={unreadOnly} onChange={(e) => setUnreadOnly(e.target.checked)} />
            Unread only
          </label>
          {selected.size > 0 && (
            <div className="ml-auto flex gap-2">
              <button onClick={() => bulkAction("markRead")} className="px-3 py-1.5 bg-[#51cbce] text-white rounded-lg text-[0.75rem] font-semibold">
                Mark Read ({selected.size})
              </button>
              <button onClick={() => bulkAction("resolve")} className="px-3 py-1.5 bg-[#6bd098] text-white rounded-lg text-[0.75rem] font-semibold">
                Resolve ({selected.size})
              </button>
            </div>
          )}
        </div>

        {/* Alert list */}
        <div className="card">
          {loading ? (
            <div className="px-6 py-12 text-center text-[#9A9A9A]">Loading...</div>
          ) : alerts.length === 0 ? (
            <div className="px-6 py-12 text-center text-[#9A9A9A]">No alerts</div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {alerts.map((a) => (
                <div key={a.id} className={`px-6 py-4 flex items-start gap-4 hover:bg-[#fafaf8] ${!a.isRead ? "bg-[#f8f9ff]" : ""}`}>
                  <input
                    type="checkbox"
                    checked={selected.has(a.id)}
                    onChange={(e) => {
                      const next = new Set(selected);
                      e.target.checked ? next.add(a.id) : next.delete(a.id);
                      setSelected(next);
                    }}
                    className="mt-1"
                  />
                  <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${SEVERITY_COLORS[a.severity] || "bg-[#9A9A9A]"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[0.82rem] font-semibold text-[#252422]">{a.title}</span>
                      {!a.isRead && <span className="w-1.5 h-1.5 rounded-full bg-[#51cbce]" />}
                    </div>
                    {a.description && <p className="text-[0.75rem] text-[#9A9A9A] mt-0.5 truncate">{a.description}</p>}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-[0.65rem] uppercase tracking-wider text-[#9A9A9A]">{a.type.replace(/_/g, " ")}</div>
                    <div className="text-[0.7rem] text-[#9A9A9A] mt-0.5">
                      {new Date(a.createdAt).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
