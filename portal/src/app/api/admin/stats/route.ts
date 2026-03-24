import { NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, usageLogs, alerts } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";

export async function GET(request: Request) {
  const token = await getToken({ req: request as any });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [
    tenantCount,
    userCount,
    callsToday,
    callsMonth,
    activeTenants,
    planBreakdown,
    recentSignups,
    unreadAlerts,
  ] = await Promise.all([
    db.select({ count: sql<number>`count(*)` }).from(tenants),
    db.select({ count: sql<number>`count(*)` }).from(users),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, todayStart)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, monthStart)),
    db.select({ count: sql<number>`count(distinct ${usageLogs.tenantId})` }).from(usageLogs).where(gte(usageLogs.createdAt, thirtyDaysAgo)),
    db.select({ planTier: tenants.planTier, count: sql<number>`count(*)` }).from(tenants).groupBy(tenants.planTier),
    db.select({ id: tenants.id, name: tenants.name, planTier: tenants.planTier, createdAt: tenants.createdAt }).from(tenants).where(gte(tenants.createdAt, sevenDaysAgo)).orderBy(sql`created_at DESC`).limit(10),
    db.select({ count: sql<number>`count(*)` }).from(alerts).where(eq(alerts.isRead, false)),
  ]);

  return NextResponse.json({
    totalTenants: tenantCount[0]?.count ?? 0,
    totalUsers: userCount[0]?.count ?? 0,
    callsToday: callsToday[0]?.count ?? 0,
    callsThisMonth: callsMonth[0]?.count ?? 0,
    activeTenants: activeTenants[0]?.count ?? 0,
    planBreakdown: planBreakdown.reduce((acc, r) => ({ ...acc, [r.planTier]: r.count }), {}),
    recentSignups,
    unreadAlerts: unreadAlerts[0]?.count ?? 0,
  });
}
