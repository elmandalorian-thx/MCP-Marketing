import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { apiKeys, platformConnections, usageLogs, tenants } from "@/lib/schema";
import { eq, sql, and, gte } from "drizzle-orm";
import { Topbar } from "@/components/topbar";
import { StatCard } from "@/components/stat-card";

async function getStats(tenantId: string) {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  const [keys, connections, usage, tenant] = await Promise.all([
    db.select({ count: sql<number>`count(*)` }).from(apiKeys)
      .where(and(eq(apiKeys.tenantId, tenantId), eq(apiKeys.isActive, true))),
    db.select({ count: sql<number>`count(*)` }).from(platformConnections)
      .where(and(eq(platformConnections.tenantId, tenantId), eq(platformConnections.isActive, true))),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, tenantId), gte(usageLogs.createdAt, monthStart))),
    db.select().from(tenants).where(eq(tenants.id, tenantId)).limit(1),
  ]);

  return {
    activeKeys: keys[0]?.count ?? 0,
    activeConnections: connections[0]?.count ?? 0,
    monthlyUsage: usage[0]?.count ?? 0,
    tenant: tenant[0] ?? null,
  };
}

async function getRecentActivity(tenantId: string) {
  return db.select({
    toolName: usageLogs.toolName,
    success: usageLogs.success,
    durationMs: usageLogs.durationMs,
    createdAt: usageLogs.createdAt,
  }).from(usageLogs)
    .where(eq(usageLogs.tenantId, tenantId))
    .orderBy(sql`created_at DESC`)
    .limit(15);
}

export default async function DashboardPage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.tenantId) redirect("/login");

  const stats = await getStats(session.tenantId);
  const recent = await getRecentActivity(session.tenantId);
  const planLimit = stats.tenant?.maxMonthlyCalls ?? 500;
  const usagePct = Math.min((stats.monthlyUsage / planLimit) * 100, 100);

  return (
    <>
      <Topbar title="Dashboard" />
      <div className="p-8">
        {/* Stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
          <StatCard icon="📡" label="API Calls" value={stats.monthlyUsage} footer={`${planLimit.toLocaleString()} limit this month`} color="teal" />
          <StatCard icon="🔌" label="Connections" value={stats.activeConnections} footer={`${stats.tenant?.maxConnections ?? 3} max`} color="green" />
          <StatCard icon="🔑" label="API Keys" value={stats.activeKeys} footer="Active keys" color="amber" />
          <StatCard icon="⚡" label="Plan" value={stats.tenant?.planTier?.charAt(0).toUpperCase() + (stats.tenant?.planTier?.slice(1) ?? "")} footer="Current plan" color="blue" />
        </div>

        {/* Usage bar */}
        <div className="card p-6 mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[0.85rem] font-bold">Monthly Usage</h3>
            <span className="text-[0.75rem] font-semibold text-[#9A9A9A]">
              {stats.monthlyUsage.toLocaleString()} / {planLimit.toLocaleString()}
            </span>
          </div>
          <div className="w-full bg-[#f4f3ef] rounded-full h-3">
            <div
              className="h-3 rounded-full transition-all duration-500"
              style={{
                width: `${usagePct}%`,
                background: usagePct > 80 ? "#ef8157" : "linear-gradient(90deg, #51cbce, #6bd098)",
              }}
            />
          </div>
          {usagePct > 80 && (
            <p className="text-[0.72rem] text-[#ef8157] mt-2 font-medium">
              Approaching plan limit. Consider upgrading.
            </p>
          )}
        </div>

        {/* Recent activity */}
        <div className="card">
          <div className="px-6 py-4 border-b border-[#eee]">
            <h3 className="text-[0.85rem] font-bold">Recent Activity</h3>
          </div>
          {recent.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <div className="text-3xl mb-3">🚀</div>
              <p className="text-[0.85rem] font-semibold text-[#252422] mb-1">No activity yet</p>
              <p className="text-[0.78rem] text-[#9A9A9A]">
                Connect your AI client with an API key to start using Marketing MCP tools.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {recent.map((log, i) => (
                <div key={i} className="px-6 py-3.5 flex items-center justify-between hover:bg-[#fafaf8] transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${log.success ? "bg-[#6bd098]" : "bg-[#ef8157]"}`} />
                    <span className="text-[0.8rem] font-semibold font-mono text-[#252422]">{log.toolName}</span>
                  </div>
                  <div className="flex items-center gap-5 text-[0.72rem] text-[#9A9A9A]">
                    {log.durationMs && (
                      <span className="badge badge-muted">{log.durationMs}ms</span>
                    )}
                    <span>
                      {log.createdAt ? new Date(log.createdAt).toLocaleString("en-US", {
                        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
                      }) : ""}
                    </span>
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
