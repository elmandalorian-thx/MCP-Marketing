"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

export default function AdminUsagePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/usage")
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <><Topbar title="Usage Analytics" /><div className="p-8 text-[#9A9A9A]">Loading...</div></>;

  return (
    <>
      <Topbar title="Usage Analytics" />
      <div className="p-8">
        {/* Daily trend (simple bar representation) */}
        <div className="card p-6 mb-6">
          <h3 className="text-[0.85rem] font-bold mb-4">Daily Calls (Last 30 Days)</h3>
          <div className="flex items-end gap-1 h-32">
            {(data?.dailyCounts || []).map((d: any, i: number) => {
              const max = Math.max(...(data?.dailyCounts || []).map((x: any) => x.count), 1);
              const height = (d.count / max) * 100;
              return (
                <div key={i} className="flex-1 group relative">
                  <div
                    className="w-full bg-gradient-to-t from-[#51cbce] to-[#6bd098] rounded-t"
                    style={{ height: `${height}%` }}
                  />
                  <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-[#252422] text-white text-[0.6rem] rounded whitespace-nowrap">
                    {d.date}: {d.count}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top tenants */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Top Tenants</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.topTenants || []).map((t: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-semibold">{t.tenantName}</span>
                  <span className="text-[0.8rem] font-mono">{t.count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top tools */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Top Tools</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.topTools || []).map((t: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-mono font-semibold">{t.toolName}</span>
                  <div className="text-right">
                    <span className="text-[0.8rem] font-mono">{t.count.toLocaleString()}</span>
                    {t.avgDuration && <span className="ml-2 text-[0.65rem] text-[#9A9A9A]">{Math.round(t.avgDuration)}ms avg</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error rates */}
          <div className="card lg:col-span-2">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Error Rates</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.errorRates || []).filter((e: any) => e.failures > 0).map((e: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-mono font-semibold">{e.toolName}</span>
                  <span className="text-[0.8rem]">
                    <span className="text-[#ef8157] font-semibold">{e.failures}</span>
                    <span className="text-[#9A9A9A]"> / {e.total} ({Math.round((e.failures / e.total) * 100)}%)</span>
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* OAuth abuse */}
          {data?.oauthAbuse?.length > 0 && (
            <div className="card lg:col-span-2">
              <div className="px-6 py-4 border-b border-[#eee]">
                <h3 className="text-[0.85rem] font-bold">OAuth Credential Changes (24h)</h3>
              </div>
              <div className="divide-y divide-[#f4f3ef]">
                {data.oauthAbuse.map((a: any, i: number) => (
                  <div key={i} className="px-6 py-3 flex items-center justify-between">
                    <span className="text-[0.8rem] font-semibold">{a.tenantName}</span>
                    <span className="text-[0.8rem]">
                      {a.changes} changes
                      {a.rateLimitHits > 0 && (
                        <span className="ml-2 text-[#ef8157] font-semibold">({a.rateLimitHits} rate limited)</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
