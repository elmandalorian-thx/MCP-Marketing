import { db } from "@/lib/db";
import { apiKeys, platformConnections, usageLogs, tenants } from "@/lib/schema";
import { eq, sql, and, gte } from "drizzle-orm";

// TODO: Replace with actual session tenant ID after auth is wired
const DEMO_TENANT_ID = process.env.DEMO_TENANT_ID;

async function getStats(tenantId: string) {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  const [keys, connections, usage, tenant] = await Promise.all([
    db
      .select({ count: sql<number>`count(*)` })
      .from(apiKeys)
      .where(and(eq(apiKeys.tenantId, tenantId), eq(apiKeys.isActive, true))),
    db
      .select({ count: sql<number>`count(*)` })
      .from(platformConnections)
      .where(and(eq(platformConnections.tenantId, tenantId), eq(platformConnections.isActive, true))),
    db
      .select({ count: sql<number>`count(*)` })
      .from(usageLogs)
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

async function getRecentUsage(tenantId: string) {
  return db
    .select({
      toolName: usageLogs.toolName,
      success: usageLogs.success,
      durationMs: usageLogs.durationMs,
      createdAt: usageLogs.createdAt,
    })
    .from(usageLogs)
    .where(eq(usageLogs.tenantId, tenantId))
    .orderBy(sql`created_at DESC`)
    .limit(10);
}

export default async function DashboardPage() {
  if (!DEMO_TENANT_ID) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-yellow-800">
          <p className="font-semibold mb-2">Setup Required</p>
          <p className="text-sm">
            Set <code className="bg-yellow-100 px-1 rounded">DEMO_TENANT_ID</code> in your
            environment to connect to a tenant. Full auth coming soon.
          </p>
        </div>
      </div>
    );
  }

  const stats = await getStats(DEMO_TENANT_ID);
  const recentUsage = await getRecentUsage(DEMO_TENANT_ID);

  const planLimit = stats.tenant?.maxMonthlyCalls ?? 500;
  const usagePercent = Math.min((stats.monthlyUsage / planLimit) * 100, 100);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">{stats.tenant?.name ?? "Dashboard"}</h1>
          <p className="text-gray-500 text-sm mt-1">
            Plan: <span className="capitalize font-medium">{stats.tenant?.planTier ?? "free"}</span>
          </p>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-1">API Keys</div>
          <div className="text-3xl font-bold">{stats.activeKeys}</div>
          <div className="text-xs text-gray-400 mt-1">active</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-1">Connections</div>
          <div className="text-3xl font-bold">{stats.activeConnections}</div>
          <div className="text-xs text-gray-400 mt-1">
            of {stats.tenant?.maxConnections ?? 3} max
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="text-sm text-gray-500 mb-1">API Calls This Month</div>
          <div className="text-3xl font-bold">
            {stats.monthlyUsage.toLocaleString()}
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
                style={{ width: `${usagePercent}%` }}
              />
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {planLimit.toLocaleString()} limit
            </div>
          </div>
        </div>
      </div>

      {/* Recent activity */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-semibold">Recent Activity</h2>
        </div>
        {recentUsage.length === 0 ? (
          <div className="p-6 text-center text-gray-400 text-sm">
            No tool calls yet. Connect your AI client to start using Marketing MCP.
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {recentUsage.map((log, i) => (
              <div key={i} className="px-6 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      log.success ? "bg-green-400" : "bg-red-400"
                    }`}
                  />
                  <span className="font-mono text-sm">{log.toolName}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  {log.durationMs && <span>{log.durationMs}ms</span>}
                  <span>
                    {log.createdAt
                      ? new Date(log.createdAt).toLocaleString()
                      : ""}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
