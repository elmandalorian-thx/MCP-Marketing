"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";
import Link from "next/link";

interface TenantRow {
  id: string;
  name: string;
  slug: string;
  planTier: string;
  maxMonthlyCalls: number;
  createdAt: string;
  userCount: number;
  connectionCount: number;
  monthlyUsage: number;
}

export default function TenantsPage() {
  const [tenants, setTenants] = useState<TenantRow[]>([]);
  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (planFilter) params.set("plan", planFilter);

    fetch(`/api/admin/tenants?${params}`)
      .then((r) => r.json())
      .then((d) => { setTenants(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [search, planFilter]);

  return (
    <>
      <Topbar title="Tenants" />
      <div className="p-8">
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="Search tenants..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 border border-[#eee] rounded-lg text-[0.82rem] w-64 focus:outline-none focus:border-[#51cbce]"
          />
          <select
            value={planFilter}
            onChange={(e) => setPlanFilter(e.target.value)}
            className="px-4 py-2 border border-[#eee] rounded-lg text-[0.82rem] focus:outline-none focus:border-[#51cbce]"
          >
            <option value="">All Plans</option>
            <option value="free">Free</option>
            <option value="starter">Starter</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>

        {/* Table */}
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#eee] text-[0.72rem] uppercase tracking-wider text-[#9A9A9A]">
                <th className="px-6 py-3 text-left font-semibold">Tenant</th>
                <th className="px-6 py-3 text-left font-semibold">Plan</th>
                <th className="px-6 py-3 text-center font-semibold">Users</th>
                <th className="px-6 py-3 text-center font-semibold">Connections</th>
                <th className="px-6 py-3 text-center font-semibold">Usage</th>
                <th className="px-6 py-3 text-right font-semibold">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f4f3ef]">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-[0.82rem] text-[#9A9A9A]">Loading...</td></tr>
              ) : tenants.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-[0.82rem] text-[#9A9A9A]">No tenants found</td></tr>
              ) : tenants.map((t) => (
                <tr key={t.id} className="hover:bg-[#fafaf8] transition-colors">
                  <td className="px-6 py-3.5">
                    <Link href={`/admin/tenants/${t.id}`} className="text-[0.82rem] font-semibold text-[#252422] hover:text-[#51cbce] no-underline">
                      {t.name}
                    </Link>
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="badge badge-muted text-[0.65rem] capitalize">{t.planTier}</span>
                  </td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">{t.userCount}</td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">{t.connectionCount}</td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">
                    {t.monthlyUsage.toLocaleString()} / {t.maxMonthlyCalls.toLocaleString()}
                  </td>
                  <td className="px-6 py-3.5 text-right text-[0.72rem] text-[#9A9A9A]">
                    {new Date(t.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
