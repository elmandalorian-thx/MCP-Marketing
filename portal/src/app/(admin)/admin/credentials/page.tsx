"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

interface PlatformStatus {
  key: string;
  label: string;
  color: string;
  requiredCreds: string[];
  status: { configured: boolean; keys: Record<string, boolean> };
}

export default function AdminCredentialsPage() {
  const [platforms, setPlatforms] = useState<PlatformStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/credentials")
      .then((r) => r.json())
      .then((d) => { setPlatforms(d.platforms || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const configured = platforms.filter((p) => p.status.configured).length;
  const partial = platforms.filter((p) => !p.status.configured && Object.values(p.status.keys).some(Boolean)).length;

  return (
    <>
      <Topbar title="Platform Credentials" />
      <div className="p-8">
        <div className="flex gap-4 mb-6 text-[0.82rem]">
          <span className="text-[#6bd098] font-semibold">{configured} configured</span>
          <span className="text-[#ffa726] font-semibold">{partial} partial</span>
          <span className="text-[#9A9A9A] font-semibold">{platforms.length - configured - partial} not set</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {platforms.map((p) => (
            <div key={p.key} className="card p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: p.color }} />
                <h3 className="text-[0.85rem] font-bold text-[#252422]">{p.label}</h3>
                <span className={`ml-auto text-[0.65rem] font-semibold px-2 py-0.5 rounded-full ${
                  p.status.configured
                    ? "bg-[#6bd098]/10 text-[#6bd098]"
                    : Object.values(p.status.keys).some(Boolean)
                    ? "bg-[#ffa726]/10 text-[#ffa726]"
                    : "bg-[#eee] text-[#9A9A9A]"
                }`}>
                  {p.status.configured ? "Configured" : Object.values(p.status.keys).some(Boolean) ? "Partial" : "Not Set"}
                </span>
              </div>
              {p.requiredCreds.length > 0 ? (
                <div className="space-y-1">
                  {p.requiredCreds.map((cred) => (
                    <div key={cred} className="flex items-center gap-2 text-[0.72rem]">
                      <div className={`w-1.5 h-1.5 rounded-full ${p.status.keys[cred] ? "bg-[#6bd098]" : "bg-[#ef8157]"}`} />
                      <span className="font-mono text-[#9A9A9A]">{cred}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[0.72rem] text-[#9A9A9A]">No credentials required</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
