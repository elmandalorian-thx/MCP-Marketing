"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";
import { useParams, useRouter } from "next/navigation";

export default function TenantDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/admin/tenants/${id}`)
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [id]);

  async function changePlan(planTier: string) {
    await fetch(`/api/admin/tenants/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ planTier }),
    });
    router.refresh();
    window.location.reload();
  }

  async function toggleSuspend() {
    await fetch(`/api/admin/tenants/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ isSuspended: !data.tenant.isSuspended }),
    });
    window.location.reload();
  }

  async function deleteTenant() {
    if (!confirm("Delete this tenant? This cannot be undone.")) return;
    await fetch(`/api/admin/tenants/${id}`, { method: "DELETE" });
    router.push("/admin/tenants");
  }

  if (loading) return <div className="p-8 text-[#9A9A9A]">Loading...</div>;
  if (!data?.tenant) return <div className="p-8 text-[#ef8157]">Tenant not found</div>;

  const { tenant, users, apiKeys, connections } = data;

  return (
    <>
      <Topbar title={tenant.name} />
      <div className="p-8">
        {/* Tenant info + actions */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-[#252422]">{tenant.name}</h2>
              <p className="text-[0.75rem] text-[#9A9A9A]">{tenant.slug} &middot; Plan: {tenant.planTier}</p>
            </div>
            <div className="flex gap-2">
              <select
                defaultValue={tenant.planTier}
                onChange={(e) => changePlan(e.target.value)}
                className="px-3 py-1.5 border border-[#eee] rounded-lg text-[0.8rem]"
              >
                <option value="free">Free</option>
                <option value="starter">Starter</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
              <button
                onClick={toggleSuspend}
                className={`px-3 py-1.5 rounded-lg text-[0.8rem] font-semibold ${
                  tenant.isSuspended
                    ? "bg-[#6bd098] text-white hover:bg-[#5bc088]"
                    : "bg-[#ffa726] text-white hover:bg-[#f59b16]"
                }`}
              >
                {tenant.isSuspended ? "Unsuspend" : "Suspend"}
              </button>
              <button
                onClick={deleteTenant}
                className="px-3 py-1.5 bg-[#ef8157] text-white rounded-lg text-[0.8rem] font-semibold hover:bg-[#e06a3e]"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Users */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Users ({users.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {users.map((u: any) => (
                <div key={u.id} className="px-6 py-3 flex items-center justify-between">
                  <div>
                    <div className="text-[0.8rem] font-semibold">{u.name || u.email}</div>
                    <div className="text-[0.7rem] text-[#9A9A9A]">{u.email}</div>
                  </div>
                  <span className="badge badge-muted text-[0.65rem]">{u.role}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Connections */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Connections ({connections.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {connections.map((c: any) => (
                <div key={c.id} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-semibold capitalize">{c.platform.replace(/_/g, " ")}</span>
                  <span className={`w-2 h-2 rounded-full ${c.isActive ? "bg-[#6bd098]" : "bg-[#9A9A9A]"}`} />
                </div>
              ))}
            </div>
          </div>

          {/* API Keys */}
          <div className="card lg:col-span-2">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">API Keys ({apiKeys.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {apiKeys.map((k: any) => (
                <div key={k.id} className="px-6 py-3 flex items-center justify-between">
                  <div>
                    <span className="text-[0.8rem] font-mono font-semibold">{k.keyPrefix}...</span>
                    {k.label && <span className="ml-2 text-[0.72rem] text-[#9A9A9A]">{k.label}</span>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${k.isActive ? "bg-[#6bd098]" : "bg-[#9A9A9A]"}`} />
                    <span className="text-[0.7rem] text-[#9A9A9A]">
                      {k.lastUsedAt ? `Last used ${new Date(k.lastUsedAt).toLocaleDateString()}` : "Never used"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
