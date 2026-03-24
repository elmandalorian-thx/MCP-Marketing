import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, apiKeys, platformConnections, usageLogs } from "@/lib/schema";
import { eq, sql, gte } from "drizzle-orm";
import { PLAN_LIMITS } from "@/lib/utils";

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { id } = params;
  const monthStart = new Date(new Date().getFullYear(), new Date().getMonth(), 1);

  const [tenant] = await db.select().from(tenants).where(eq(tenants.id, id)).limit(1);
  if (!tenant) return NextResponse.json({ error: "Tenant not found" }, { status: 404 });

  const [tenantUsers, tenantKeys, tenantConnections, tenantUsage] = await Promise.all([
    db.select({ id: users.id, email: users.email, name: users.name, role: users.role, createdAt: users.createdAt }).from(users).where(eq(users.tenantId, id)),
    db.select({ id: apiKeys.id, keyPrefix: apiKeys.keyPrefix, label: apiKeys.label, isActive: apiKeys.isActive, lastUsedAt: apiKeys.lastUsedAt, createdAt: apiKeys.createdAt }).from(apiKeys).where(eq(apiKeys.tenantId, id)),
    db.select({ id: platformConnections.id, platform: platformConnections.platform, isActive: platformConnections.isActive, createdAt: platformConnections.createdAt }).from(platformConnections).where(eq(platformConnections.tenantId, id)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(eq(usageLogs.tenantId, id)),
  ]);

  return NextResponse.json({
    tenant,
    users: tenantUsers,
    apiKeys: tenantKeys,
    connections: tenantConnections,
    totalUsage: tenantUsage[0]?.count ?? 0,
  });
}

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { id } = params;
  const body = await request.json();
  const updates: Record<string, any> = {};

  if (body.planTier && body.planTier in PLAN_LIMITS) {
    const limits = PLAN_LIMITS[body.planTier as keyof typeof PLAN_LIMITS];
    updates.planTier = body.planTier;
    updates.maxConnections = limits.connections;
    updates.maxMonthlyCalls = limits.monthlyCalls;
  }

  if (typeof body.isSuspended === "boolean") {
    updates.isSuspended = body.isSuspended;
  }

  if (Object.keys(updates).length === 0) {
    return NextResponse.json({ error: "No valid updates" }, { status: 400 });
  }

  updates.updatedAt = new Date();

  await db.update(tenants).set(updates).where(eq(tenants.id, id));
  return NextResponse.json({ updated: true });
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  await db.delete(tenants).where(eq(tenants.id, params.id));
  return NextResponse.json({ deleted: true });
}
