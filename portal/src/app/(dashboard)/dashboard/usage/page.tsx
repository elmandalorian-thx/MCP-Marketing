import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { usageLogs } from "@/lib/schema";
import { eq, sql, and, gte } from "drizzle-orm";
import { Topbar } from "@/components/topbar";

async function getUsageData(tenantId: string) {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  const [daily, topTools, totals] = await Promise.all([
    db.select({
      date: sql<string>`TO_CHAR(created_at, 'YYYY-MM-DD')`,
      total: sql<number>`count(*)`,
      successful: sql<number>`count(*) FILTER (WHERE success = true)`,
      failed: sql<number>`count(*) FILTER (WHERE success = false)`,
    }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, tenantId), gte(usageLogs.createdAt, monthStart)))
      .groupBy(sql`TO_CHAR(created_at, 'YYYY-MM-DD')`)
      .orderBy(sql`TO_CHAR(created_at, 'YYYY-MM-DD')`),

    db.select({
      toolName: usageLogs.toolName,
      count: sql<number>`count(*)`,
      avgDuration: sql<number>`COALESCE(AVG(duration_ms)::int, 0)`,
      successRate: sql<number>`ROUND(100.0 * count(*) FILTER (WHERE success = true) / GREATEST(count(*), 1))`,
    }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, tenantId), gte(usageLogs.createdAt, monthStart)))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) DESC`)
      .limit(15),

    db.select({
      total: sql<number>`count(*)`,
      successful: sql<number>`count(*) FILTER (WHERE success = true)`,
      avgDuration: sql<number>`COALESCE(AVG(duration_ms)::int, 0)`,
    }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, tenantId), gte(usageLogs.createdAt, monthStart))),
  ]);

  return { daily, topTools, totals: totals[0] };
}

export default async function UsagePage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.tenantId) redirect("/login");

  const { daily, topTools, totals } = await getUsageData(session.tenantId);
  const successRate = totals?.total ? Math.round((totals.successful / totals.total) * 100) : 100;

  return (
    <>
      <Topbar title="Usage Analytics" />
      <div className="p-8">
        {/* Summary cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-8">
          <div className="card p-5">
            <div className="text-[0.72rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Total Calls</div>
            <div className="text-2xl font-bold">{(totals?.total ?? 0).toLocaleString()}</div>
            <div className="text-[0.7rem] text-[#9A9A9A] mt-1">This month</div>
          </div>
          <div className="card p-5">
            <div className="text-[0.72rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Success Rate</div>
            <div className="text-2xl font-bold" style={{ color: successRate >= 95 ? "#6bd098" : successRate >= 80 ? "#fcc468" : "#ef8157" }}>
              {successRate}%
            </div>
            <div className="text-[0.7rem] text-[#9A9A9A] mt-1">{totals?.successful ?? 0} successful</div>
          </div>
          <div className="card p-5">
            <div className="text-[0.72rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Avg Response</div>
            <div className="text-2xl font-bold">{totals?.avgDuration ?? 0}ms</div>
            <div className="text-[0.7rem] text-[#9A9A9A] mt-1">Average duration</div>
          </div>
        </div>

        {/* Daily breakdown */}
        {daily.length > 0 && (
          <div className="card mb-8">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Daily Breakdown</h3>
            </div>
            <div className="p-6">
              <div className="space-y-2">
                {daily.map((day) => {
                  const maxCalls = Math.max(...daily.map(d => d.total));
                  const pct = maxCalls > 0 ? (day.total / maxCalls) * 100 : 0;
                  return (
                    <div key={day.date} className="flex items-center gap-4">
                      <span className="text-[0.75rem] font-mono text-[#9A9A9A] w-24 flex-shrink-0">{day.date}</span>
                      <div className="flex-1 bg-[#f4f3ef] rounded-full h-6 relative overflow-hidden">
                        <div
                          className="h-full rounded-full flex items-center pl-3"
                          style={{ width: `${Math.max(pct, 8)}%`, background: "linear-gradient(90deg, #51cbce, #6bd098)" }}
                        >
                          <span className="text-[0.65rem] font-bold text-white">{day.total}</span>
                        </div>
                      </div>
                      {day.failed > 0 && (
                        <span className="badge badge-danger text-[0.65rem]">{day.failed} failed</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Top tools */}
        <div className="card">
          <div className="px-6 py-4 border-b border-[#eee]">
            <h3 className="text-[0.85rem] font-bold">Top Tools</h3>
          </div>
          {topTools.length === 0 ? (
            <div className="px-6 py-10 text-center text-[0.82rem] text-[#9A9A9A]">
              No tool usage data yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#eee]">
                    <th className="px-6 py-3 text-left text-[0.7rem] font-semibold text-[#9A9A9A] uppercase tracking-wider">Tool</th>
                    <th className="px-6 py-3 text-right text-[0.7rem] font-semibold text-[#9A9A9A] uppercase tracking-wider">Calls</th>
                    <th className="px-6 py-3 text-right text-[0.7rem] font-semibold text-[#9A9A9A] uppercase tracking-wider">Avg Duration</th>
                    <th className="px-6 py-3 text-right text-[0.7rem] font-semibold text-[#9A9A9A] uppercase tracking-wider">Success</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#f4f3ef]">
                  {topTools.map((tool) => (
                    <tr key={tool.toolName} className="hover:bg-[#fafaf8] transition-colors">
                      <td className="px-6 py-3.5">
                        <code className="text-[0.8rem] font-mono font-semibold text-[#252422]">{tool.toolName}</code>
                      </td>
                      <td className="px-6 py-3.5 text-right text-[0.82rem] font-semibold">{tool.count}</td>
                      <td className="px-6 py-3.5 text-right text-[0.82rem] text-[#9A9A9A]">{tool.avgDuration}ms</td>
                      <td className="px-6 py-3.5 text-right">
                        <span className={`badge ${Number(tool.successRate) >= 95 ? "badge-success" : Number(tool.successRate) >= 80 ? "badge-warning" : "badge-danger"}`}>
                          {tool.successRate}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
