import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { tenants, users, usageLogs, alerts } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";
import { Topbar } from "@/components/topbar";
import { StatCard } from "@/components/stat-card";

async function getAdminStats() {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [
    tenantCount,
    userCount,
    callsToday,
    callsMonth,
    planBreakdown,
    recentSignups,
    unreadAlerts,
  ] = await Promise.all([
    db.select({ count: sql<number>`count(*)` }).from(tenants),
    db.select({ count: sql<number>`count(*)` }).from(users),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, todayStart)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, monthStart)),
    db.select({ planTier: tenants.planTier, count: sql<number>`count(*)` }).from(tenants).groupBy(tenants.planTier),
    db.select({ id: tenants.id, name: tenants.name, planTier: tenants.planTier, createdAt: tenants.createdAt }).from(tenants).where(gte(tenants.createdAt, sevenDaysAgo)).orderBy(sql`created_at DESC`).limit(10),
    db.select({ count: sql<number>`count(*)` }).from(alerts).where(eq(alerts.isRead, false)),
  ]);

  return {
    totalTenants: tenantCount[0]?.count ?? 0,
    totalUsers: userCount[0]?.count ?? 0,
    callsToday: callsToday[0]?.count ?? 0,
    callsMonth: callsMonth[0]?.count ?? 0,
    plans: planBreakdown.reduce((acc, r) => ({ ...acc, [r.planTier]: r.count }), {} as Record<string, number>),
    recentSignups,
    unreadAlerts: unreadAlerts[0]?.count ?? 0,
  };
}

export default async function AdminOverviewPage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.isSuperAdmin) redirect("/dashboard");

  const stats = await getAdminStats();

  return (
    <>
      <Topbar title="Super Admin — Overview" />
      <div className="p-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
          <StatCard icon="🏢" label="Tenants" value={stats.totalTenants} footer="Total accounts" color="teal" />
          <StatCard icon="👥" label="Users" value={stats.totalUsers} footer="Total users" color="green" />
          <StatCard icon="📡" label="Calls Today" value={stats.callsToday} footer={`${stats.callsMonth.toLocaleString()} this month`} color="amber" />
          <StatCard icon="🔔" label="Unread Alerts" value={stats.unreadAlerts} footer="Pending review" color="blue" />
        </div>

        {/* Plan breakdown */}
        <div className="card p-6 mb-8">
          <h3 className="text-[0.85rem] font-bold mb-4">Plan Distribution</h3>
          <div className="grid grid-cols-4 gap-4">
            {["free", "starter", "pro", "enterprise"].map((plan) => (
              <div key={plan} className="text-center">
                <div className="text-2xl font-bold text-[#252422]">{stats.plans[plan] ?? 0}</div>
                <div className="text-[0.72rem] text-[#9A9A9A] capitalize">{plan}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent signups */}
        <div className="card">
          <div className="px-6 py-4 border-b border-[#eee]">
            <h3 className="text-[0.85rem] font-bold">Recent Signups (7 days)</h3>
          </div>
          {stats.recentSignups.length === 0 ? (
            <div className="px-6 py-12 text-center text-[0.85rem] text-[#9A9A9A]">No new signups</div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {stats.recentSignups.map((t) => (
                <div key={t.id} className="px-6 py-3.5 flex items-center justify-between hover:bg-[#fafaf8]">
                  <div>
                    <span className="text-[0.8rem] font-semibold text-[#252422]">{t.name}</span>
                    <span className="ml-2 badge badge-muted text-[0.65rem]">{t.planTier}</span>
                  </div>
                  <span className="text-[0.72rem] text-[#9A9A9A]">
                    {t.createdAt ? new Date(t.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
