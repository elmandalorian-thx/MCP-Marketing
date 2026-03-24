import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { alerts } from "@/lib/schema";
import { sql, eq, and, lt, inArray } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { searchParams } = request.nextUrl;
  const severity = searchParams.get("severity") || "";
  const type = searchParams.get("type") || "";
  const unreadOnly = searchParams.get("unread") === "true";
  const cursor = searchParams.get("cursor") || "";
  const limit = Math.min(parseInt(searchParams.get("limit") || "30"), 100);

  const conditions = [];
  if (severity) conditions.push(eq(alerts.severity, severity));
  if (type) conditions.push(eq(alerts.type, type));
  if (unreadOnly) conditions.push(eq(alerts.isRead, false));
  if (cursor) conditions.push(lt(alerts.id, parseInt(cursor)));

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const rows = await db
    .select()
    .from(alerts)
    .where(where)
    .orderBy(sql`id DESC`)
    .limit(limit + 1);

  const hasMore = rows.length > limit;
  const data = hasMore ? rows.slice(0, limit) : rows;
  const nextCursor = hasMore ? data[data.length - 1].id : null;

  return NextResponse.json({ data, nextCursor });
}

export async function PATCH(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = await request.json();
  const { action, ids } = body;

  if (!action || !ids || !Array.isArray(ids)) {
    return NextResponse.json({ error: "action and ids required" }, { status: 400 });
  }

  const idNumbers = ids.map(Number).filter(Boolean);

  if (action === "markRead") {
    await db.update(alerts).set({ isRead: true, updatedAt: new Date() }).where(inArray(alerts.id, idNumbers));
  } else if (action === "resolve") {
    await db.update(alerts).set({ resolvedAt: new Date(), isRead: true, updatedAt: new Date() }).where(inArray(alerts.id, idNumbers));
  } else {
    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  }

  return NextResponse.json({ updated: idNumbers.length });
}
