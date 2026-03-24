import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, platformConnections, usageLogs } from "@/lib/schema";
import { sql, eq, ilike, gte, and, gt } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { searchParams } = request.nextUrl;
  const search = searchParams.get("search") || "";
  const plan = searchParams.get("plan") || "";
  const cursor = searchParams.get("cursor") || "";
  const limit = Math.min(parseInt(searchParams.get("limit") || "20"), 100);

  const monthStart = new Date(new Date().getFullYear(), new Date().getMonth(), 1);

  // Build conditions
  const conditions = [];
  if (search) conditions.push(ilike(tenants.name, `%${search}%`));
  if (plan) conditions.push(eq(tenants.planTier, plan));
  if (cursor) conditions.push(gt(tenants.id, cursor));

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const rows = await db
    .select({
      id: tenants.id,
      name: tenants.name,
      slug: tenants.slug,
      planTier: tenants.planTier,
      maxMonthlyCalls: tenants.maxMonthlyCalls,
      createdAt: tenants.createdAt,
      userCount: sql<number>`(SELECT count(*) FROM users WHERE users.tenant_id = tenants.id)`,
      connectionCount: sql<number>`(SELECT count(*) FROM platform_connections WHERE platform_connections.tenant_id = tenants.id AND platform_connections.is_active = true)`,
      monthlyUsage: sql<number>`(SELECT count(*) FROM usage_logs WHERE usage_logs.tenant_id = tenants.id AND usage_logs.created_at >= ${monthStart})`,
    })
    .from(tenants)
    .where(where)
    .orderBy(tenants.id)
    .limit(limit + 1);

  const hasMore = rows.length > limit;
  const data = hasMore ? rows.slice(0, limit) : rows;
  const nextCursor = hasMore ? data[data.length - 1].id : null;

  return NextResponse.json({ data, nextCursor });
}
