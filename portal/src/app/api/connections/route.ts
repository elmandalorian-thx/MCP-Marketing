import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { platformConnections } from "@/lib/schema";
import { eq, and } from "drizzle-orm";
import { createCipheriv, createDecipheriv, randomBytes } from "crypto";

const DEMO_TENANT_ID = process.env.DEMO_TENANT_ID;

function getEncryptionKey(): Buffer {
  const keyHex = process.env.CREDENTIAL_ENCRYPTION_KEY;
  if (!keyHex || keyHex.length !== 64) {
    throw new Error("CREDENTIAL_ENCRYPTION_KEY must be a 64-char hex string");
  }
  return Buffer.from(keyHex, "hex");
}

function encryptCredentials(creds: Record<string, string>): {
  encrypted: Buffer;
  nonce: Buffer;
} {
  const key = getEncryptionKey();
  const nonce = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  const plaintext = JSON.stringify(creds);
  const encrypted = Buffer.concat([
    cipher.update(plaintext, "utf8"),
    cipher.final(),
    cipher.getAuthTag(),
  ]);
  return { encrypted, nonce };
}

export async function POST(request: NextRequest) {
  if (!DEMO_TENANT_ID) {
    return NextResponse.json({ error: "No tenant configured" }, { status: 400 });
  }

  const body = await request.json();
  const { platform, credentials } = body;

  if (!platform || !credentials || typeof credentials !== "object") {
    return NextResponse.json(
      { error: "platform and credentials are required" },
      { status: 400 }
    );
  }

  const { encrypted, nonce } = encryptCredentials(credentials);

  // Upsert: insert or update if platform connection already exists
  const existing = await db
    .select({ id: platformConnections.id })
    .from(platformConnections)
    .where(
      and(
        eq(platformConnections.tenantId, DEMO_TENANT_ID),
        eq(platformConnections.platform, platform)
      )
    )
    .limit(1);

  if (existing.length > 0) {
    await db
      .update(platformConnections)
      .set({
        credentialsEncrypted: encrypted,
        credentialsNonce: nonce,
        isActive: true,
      })
      .where(eq(platformConnections.id, existing[0].id));
  } else {
    await db.insert(platformConnections).values({
      tenantId: DEMO_TENANT_ID,
      platform,
      credentialsEncrypted: encrypted,
      credentialsNonce: nonce,
    });
  }

  return NextResponse.json({ saved: true, platform });
}

export async function GET() {
  if (!DEMO_TENANT_ID) {
    return NextResponse.json({ error: "No tenant configured" }, { status: 400 });
  }

  const connections = await db
    .select({
      id: platformConnections.id,
      platform: platformConnections.platform,
      isActive: platformConnections.isActive,
      createdAt: platformConnections.createdAt,
      updatedAt: platformConnections.updatedAt,
    })
    .from(platformConnections)
    .where(eq(platformConnections.tenantId, DEMO_TENANT_ID));

  return NextResponse.json(connections);
}
