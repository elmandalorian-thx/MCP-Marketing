import { NextResponse } from "next/server";
import { db } from "@/lib/db";
import { usageLogs } from "@/lib/schema";
import { eq, sql, gte, and } from "drizzle-orm";

const DEMO_TENANT_ID = process.env.DEMO_TENANT_ID;

export async function GET() {
  if (!DEMO_TENANT_ID) {
    return NextResponse.json({ error: "No tenant configured" }, { status: 400 });
  }

  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  // Daily usage for the current month
  const dailyUsage = await db
    .select({
      date: sql<string>`DATE(created_at)`,
      total: sql<number>`count(*)`,
      successful: sql<number>`count(*) FILTER (WHERE success = true)`,
      failed: sql<number>`count(*) FILTER (WHERE success = false)`,
    })
    .from(usageLogs)
    .where(
      and(eq(usageLogs.tenantId, DEMO_TENANT_ID), gte(usageLogs.createdAt, monthStart))
    )
    .groupBy(sql`DATE(created_at)`)
    .orderBy(sql`DATE(created_at)`);

  // Top tools
  const topTools = await db
    .select({
      toolName: usageLogs.toolName,
      count: sql<number>`count(*)`,
      avgDuration: sql<number>`avg(duration_ms)::int`,
    })
    .from(usageLogs)
    .where(
      and(eq(usageLogs.tenantId, DEMO_TENANT_ID), gte(usageLogs.createdAt, monthStart))
    )
    .groupBy(usageLogs.toolName)
    .orderBy(sql`count(*) DESC`)
    .limit(10);

  return NextResponse.json({ dailyUsage, topTools });
}
