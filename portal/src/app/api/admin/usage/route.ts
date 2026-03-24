import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { usageLogs, tenants, oauthChangeLog } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [dailyCounts, hourlyCounts, topTenants, topTools, errorRates, oauthAbuse] = await Promise.all([
    // Daily calls (last 30 days)
    db.select({
      date: sql<string>`date(created_at)`,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(sql`date(created_at)`)
      .orderBy(sql`date(created_at)`),

    // Hourly calls (last 7 days)
    db.select({
      date: sql<string>`date(created_at)`,
      hour: sql<number>`extract(hour from created_at)`,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, sevenDaysAgo))
      .groupBy(sql`date(created_at)`, sql`extract(hour from created_at)`)
      .orderBy(sql`date(created_at)`, sql`extract(hour from created_at)`),

    // Top 10 tenants by usage (last 30 days)
    db.select({
      tenantId: usageLogs.tenantId,
      tenantName: tenants.name,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .innerJoin(tenants, eq(usageLogs.tenantId, tenants.id))
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.tenantId, tenants.name)
      .orderBy(sql`count(*) DESC`)
      .limit(10),

    // Top 10 tools by volume
    db.select({
      toolName: usageLogs.toolName,
      count: sql<number>`count(*)`,
      avgDuration: sql<number>`avg(duration_ms)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) DESC`)
      .limit(10),

    // Error rates by tool
    db.select({
      toolName: usageLogs.toolName,
      total: sql<number>`count(*)`,
      failures: sql<number>`count(*) filter (where not success)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) filter (where not success) DESC`)
      .limit(10),

    // OAuth change frequency (top abusers)
    db.select({
      tenantId: oauthChangeLog.tenantId,
      tenantName: tenants.name,
      changes: sql<number>`count(*)`,
      rateLimitHits: sql<number>`count(*) filter (where oauth_change_log.created_at >= ${new Date(Date.now() - 10 * 60 * 1000)})`,
    }).from(oauthChangeLog)
      .innerJoin(tenants, eq(oauthChangeLog.tenantId, tenants.id))
      .where(gte(oauthChangeLog.createdAt, new Date(Date.now() - 24 * 60 * 60 * 1000)))
      .groupBy(oauthChangeLog.tenantId, tenants.name)
      .orderBy(sql`count(*) DESC`)
      .limit(10),
  ]);

  return NextResponse.json({ dailyCounts, hourlyCounts, topTenants, topTools, errorRates, oauthAbuse });
}
