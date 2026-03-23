import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { platformConnections } from "@/lib/schema";
import { eq, and } from "drizzle-orm";
import { createCipheriv, randomBytes } from "crypto";

function getTenantId(session: any): string | null {
  return session?.tenantId || null;
}

function getEncryptionKey(): Buffer {
  const hex = process.env.CREDENTIAL_ENCRYPTION_KEY;
  if (!hex || hex.length !== 64) throw new Error("CREDENTIAL_ENCRYPTION_KEY required");
  return Buffer.from(hex, "hex");
}

function encrypt(creds: Record<string, string>): { encrypted: Buffer; nonce: Buffer } {
  const key = getEncryptionKey();
  const nonce = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  const plaintext = JSON.stringify(creds);
  const encrypted = Buffer.concat([cipher.update(plaintext, "utf8"), cipher.final(), cipher.getAuthTag()]);
  return { encrypted, nonce };
}

export async function GET() {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const conns = await db.select({
    id: platformConnections.id,
    platform: platformConnections.platform,
    isActive: platformConnections.isActive,
    createdAt: platformConnections.createdAt,
    updatedAt: platformConnections.updatedAt,
  }).from(platformConnections)
    .where(eq(platformConnections.tenantId, tenantId));

  return NextResponse.json(conns);
}

export async function POST(request: NextRequest) {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { platform, credentials } = await request.json();
  if (!platform || !credentials) return NextResponse.json({ error: "platform and credentials required" }, { status: 400 });

  const { encrypted, nonce } = encrypt(credentials);

  const [existing] = await db.select({ id: platformConnections.id }).from(platformConnections)
    .where(and(eq(platformConnections.tenantId, tenantId), eq(platformConnections.platform, platform)))
    .limit(1);

  if (existing) {
    await db.update(platformConnections).set({
      credentialsEncrypted: encrypted,
      credentialsNonce: nonce,
      isActive: true,
    }).where(eq(platformConnections.id, existing.id));
  } else {
    await db.insert(platformConnections).values({
      tenantId,
      platform,
      credentialsEncrypted: encrypted,
      credentialsNonce: nonce,
    });
  }

  return NextResponse.json({ saved: true, platform });
}

export async function DELETE(request: NextRequest) {
  const session = await getServerSession(authOptions);
  const tenantId = getTenantId(session);
  if (!tenantId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const platform = request.nextUrl.searchParams.get("platform");
  if (!platform) return NextResponse.json({ error: "platform required" }, { status: 400 });

  await db.update(platformConnections).set({ isActive: false })
    .where(and(eq(platformConnections.tenantId, tenantId), eq(platformConnections.platform, platform)));

  return NextResponse.json({ disconnected: true });
}
