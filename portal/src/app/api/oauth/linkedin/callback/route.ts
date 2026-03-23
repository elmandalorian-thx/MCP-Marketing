import { NextRequest, NextResponse } from "next/server";
import { exchangeLinkedInCode, parseOAuthState } from "@/lib/oauth";
import { db } from "@/lib/db";
import { platformConnections } from "@/lib/schema";
import { eq, and } from "drizzle-orm";
import { createCipheriv, randomBytes } from "crypto";

function encrypt(creds: Record<string, string>): { encrypted: Buffer; nonce: Buffer } {
  const key = Buffer.from(process.env.CREDENTIAL_ENCRYPTION_KEY || "", "hex");
  const nonce = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, nonce);
  const encrypted = Buffer.concat([cipher.update(JSON.stringify(creds), "utf8"), cipher.final(), cipher.getAuthTag()]);
  return { encrypted, nonce };
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");

  if (!code || !state) {
    return NextResponse.redirect(new URL("/connect?error=linkedin_denied", request.url));
  }

  const parsed = parseOAuthState(state);
  if (!parsed) {
    return NextResponse.redirect(new URL("/connect?error=invalid_state", request.url));
  }

  try {
    const accessToken = await exchangeLinkedInCode(code);

    const { encrypted, nonce } = encrypt({ LINKEDIN_ACCESS_TOKEN: accessToken });

    const [existing] = await db.select({ id: platformConnections.id }).from(platformConnections)
      .where(and(eq(platformConnections.tenantId, parsed.tenantId), eq(platformConnections.platform, "linkedin")))
      .limit(1);

    if (existing) {
      await db.update(platformConnections).set({
        credentialsEncrypted: encrypted, credentialsNonce: nonce, isActive: true,
      }).where(eq(platformConnections.id, existing.id));
    } else {
      await db.insert(platformConnections).values({
        tenantId: parsed.tenantId, platform: "linkedin",
        credentialsEncrypted: encrypted, credentialsNonce: nonce,
      });
    }

    return NextResponse.redirect(new URL("/connect?success=linkedin", request.url));
  } catch (err) {
    console.error("LinkedIn OAuth callback error:", err);
    return NextResponse.redirect(new URL("/connect?error=linkedin_exchange", request.url));
  }
}
