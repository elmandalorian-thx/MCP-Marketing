import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { usageLogs } from "@/lib/schema";
import { eq, sql, and, gte } from "drizzle-orm";

export async function GET() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  const [daily, topTools] = await Promise.all([
    db.select({
      date: sql<string>`TO_CHAR(created_at, 'YYYY-MM-DD')`,
      total: sql<number>`count(*)`,
    }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, session.tenantId), gte(usageLogs.createdAt, monthStart)))
      .groupBy(sql`TO_CHAR(created_at, 'YYYY-MM-DD')`)
      .orderBy(sql`TO_CHAR(created_at, 'YYYY-MM-DD')`),
    db.select({
      toolName: usageLogs.toolName,
      count: sql<number>`count(*)`,
      avgDuration: sql<number>`COALESCE(AVG(duration_ms)::int, 0)`,
    }).from(usageLogs)
      .where(and(eq(usageLogs.tenantId, session.tenantId), gte(usageLogs.createdAt, monthStart)))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) DESC`)
      .limit(10),
  ]);

  return NextResponse.json({ daily, topTools });
}
