import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { apiKeys } from "@/lib/schema";
import { eq } from "drizzle-orm";
import { randomUUID } from "crypto";
import { createHash, randomBytes } from "crypto";

// TODO: Replace with session-based tenant ID after auth is wired
const DEMO_TENANT_ID = process.env.DEMO_TENANT_ID;

function generateApiKey(): { raw: string; hash: string; prefix: string } {
  const raw = "mk_live_" + randomBytes(24).toString("base64url");
  const hash = createHash("sha256").update(raw).digest("hex");
  const prefix = raw.substring(0, 12);
  return { raw, hash, prefix };
}

export async function POST(request: NextRequest) {
  if (!DEMO_TENANT_ID) {
    return NextResponse.json({ error: "No tenant configured" }, { status: 400 });
  }

  const body = await request.json();
  const label = body.label || "Default";

  const { raw, hash, prefix } = generateApiKey();

  const [inserted] = await db
    .insert(apiKeys)
    .values({
      tenantId: DEMO_TENANT_ID,
      keyHash: hash,
      keyPrefix: prefix,
      label,
    })
    .returning({ id: apiKeys.id, prefix: apiKeys.keyPrefix });

  return NextResponse.json({
    id: inserted.id,
    rawKey: raw,
    prefix: inserted.prefix,
    label,
  });
}

export async function DELETE(request: NextRequest) {
  const id = request.nextUrl.searchParams.get("id");
  if (!id) {
    return NextResponse.json({ error: "Missing key id" }, { status: 400 });
  }

  await db.update(apiKeys).set({ isActive: false }).where(eq(apiKeys.id, id));

  return NextResponse.json({ revoked: true });
}
