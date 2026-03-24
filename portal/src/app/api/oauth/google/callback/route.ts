import { NextRequest, NextResponse } from "next/server";
import { exchangeGoogleCode, parseOAuthState } from "@/lib/oauth";
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

async function upsertConnection(tenantId: string, platform: string, credentials: Record<string, string>) {
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
      tenantId, platform,
      credentialsEncrypted: encrypted,
      credentialsNonce: nonce,
    });
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const error = searchParams.get("error");

  if (error) {
    return NextResponse.redirect(new URL("/dashboard/connect?error=google_denied", request.url));
  }

  if (!code || !state) {
    return NextResponse.redirect(new URL("/dashboard/connect?error=missing_params", request.url));
  }

  const parsed = parseOAuthState(state);
  if (!parsed) {
    return NextResponse.redirect(new URL("/dashboard/connect?error=invalid_state", request.url));
  }

  try {
    const tokens = await exchangeGoogleCode(code);

    // Store refresh token for all Google services
    // The MCP gateway uses GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET from its own env
    // plus the user's REFRESH_TOKEN to make API calls
    const googleCreds: Record<string, string> = {};

    if (tokens.refresh_token) {
      googleCreds["GOOGLE_ADS_REFRESH_TOKEN"] = tokens.refresh_token;
    }

    // Determine which scopes were granted and create connections
    const scopes = tokens.scope?.split(" ") || [];

    // Google Ads
    if (scopes.some(s => s.includes("adwords"))) {
      await upsertConnection(parsed.tenantId, "google_ads", {
        GOOGLE_ADS_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        GOOGLE_ADS_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
        GOOGLE_ADS_REFRESH_TOKEN: tokens.refresh_token || "",
        GOOGLE_ADS_DEVELOPER_TOKEN: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || "",
      });
    }

    // GA4
    if (scopes.some(s => s.includes("analytics"))) {
      await upsertConnection(parsed.tenantId, "ga4", {
        GOOGLE_OAUTH_ACCESS_TOKEN: tokens.access_token,
        GOOGLE_OAUTH_REFRESH_TOKEN: tokens.refresh_token || "",
        GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        GOOGLE_OAUTH_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
      });
    }

    // Search Console
    if (scopes.some(s => s.includes("webmasters"))) {
      await upsertConnection(parsed.tenantId, "search_console", {
        GOOGLE_OAUTH_ACCESS_TOKEN: tokens.access_token,
        GOOGLE_OAUTH_REFRESH_TOKEN: tokens.refresh_token || "",
        GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        GOOGLE_OAUTH_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
      });
    }

    // YouTube
    if (scopes.some(s => s.includes("youtube"))) {
      await upsertConnection(parsed.tenantId, "youtube", {
        YOUTUBE_OAUTH_ACCESS_TOKEN: tokens.access_token,
        YOUTUBE_OAUTH_REFRESH_TOKEN: tokens.refresh_token || "",
        YOUTUBE_OAUTH_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        YOUTUBE_OAUTH_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
      });
    }

    // Google Drive
    if (scopes.some(s => s.includes("drive"))) {
      await upsertConnection(parsed.tenantId, "google_drive", {
        GOOGLE_OAUTH_ACCESS_TOKEN: tokens.access_token,
        GOOGLE_OAUTH_REFRESH_TOKEN: tokens.refresh_token || "",
        GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        GOOGLE_OAUTH_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
      });
    }

    // Google Business Profile
    if (scopes.some(s => s.includes("business"))) {
      await upsertConnection(parsed.tenantId, "google_business_profile", {
        GOOGLE_OAUTH_ACCESS_TOKEN: tokens.access_token,
        GOOGLE_OAUTH_REFRESH_TOKEN: tokens.refresh_token || "",
        GOOGLE_OAUTH_CLIENT_ID: process.env.GOOGLE_CLIENT_ID || "",
        GOOGLE_OAUTH_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || "",
      });
    }

    return NextResponse.redirect(new URL("/dashboard/connect?success=google", request.url));
  } catch (err) {
    console.error("Google OAuth callback error:", err);
    return NextResponse.redirect(new URL("/dashboard/connect?error=google_exchange", request.url));
  }
}
