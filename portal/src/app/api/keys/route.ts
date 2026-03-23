import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiKeys } from "@/lib/schema";
import { eq, and } from "drizzle-orm";
import { createHash, randomBytes } from "crypto";

function getTenantId(session: any): string | null {
  return session?.tenantId || null;
}

export async function GET() {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const keys = await db.select({
    id: apiKeys.id,
    prefix: apiKeys.keyPrefix,
    label: apiKeys.label,
    isActive: apiKeys.isActive,
    createdAt: apiKeys.createdAt,
    lastUsedAt: apiKeys.lastUsedAt,
  }).from(apiKeys)
    .where(eq(apiKeys.tenantId, tenantId))
    .orderBy(apiKeys.createdAt);

  return NextResponse.json(keys);
}

export async function POST(request: NextRequest) {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { label } = await request.json();
  const raw = "mk_live_" + randomBytes(24).toString("base64url");
  const hash = createHash("sha256").update(raw).digest("hex");
  const prefix = raw.substring(0, 12);

  const [inserted] = await db.insert(apiKeys).values({
    tenantId,
    keyHash: hash,
    keyPrefix: prefix,
    label: label || "Default",
  }).returning({ id: apiKeys.id, prefix: apiKeys.keyPrefix });

  return NextResponse.json({ id: inserted.id, rawKey: raw, prefix: inserted.prefix });
}

export async function DELETE(request: NextRequest) {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const id = request.nextUrl.searchParams.get("id");
  if (!id) return NextResponse.json({ error: "Missing key id" }, { status: 400 });

  await db.update(apiKeys).set({ isActive: false })
    .where(and(eq(apiKeys.id, id), eq(apiKeys.tenantId, tenantId)));

  return NextResponse.json({ revoked: true });
}
