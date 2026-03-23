/**
 * OAuth utilities for platform connection flows.
 *
 * These are SEPARATE from the NextAuth login OAuth.
 * NextAuth handles portal login (Google/GitHub sign-in).
 * These handle connecting marketing platforms (Google Ads, Meta, LinkedIn, etc.)
 */

const PORTAL_URL = process.env.NEXTAUTH_URL || "https://portal.statika.net";

// ─── Google Marketing OAuth ─────────────────────────────────────────────

const GOOGLE_MARKETING_SCOPES = [
  "https://www.googleapis.com/auth/adwords",
  "https://www.googleapis.com/auth/analytics.readonly",
  "https://www.googleapis.com/auth/webmasters.readonly",
  "https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/drive.readonly",
  "https://www.googleapis.com/auth/business.manage",
].join(" ");

export function getGoogleOAuthUrl(state: string): string {
  const params = new URLSearchParams({
    client_id: process.env.GOOGLE_CLIENT_ID || "",
    redirect_uri: `${PORTAL_URL}/api/oauth/google/callback`,
    response_type: "code",
    scope: GOOGLE_MARKETING_SCOPES,
    access_type: "offline",
    prompt: "consent",
    state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
}

export async function exchangeGoogleCode(code: string): Promise<{
  access_token: string;
  refresh_token: string;
  scope: string;
}> {
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: process.env.GOOGLE_CLIENT_ID || "",
      client_secret: process.env.GOOGLE_CLIENT_SECRET || "",
      code,
      grant_type: "authorization_code",
      redirect_uri: `${PORTAL_URL}/api/oauth/google/callback`,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Google token exchange failed: ${err}`);
  }

  return res.json();
}

// ─── Meta (Facebook) OAuth ──────────────────────────────────────────────

const META_SCOPES = "ads_read,ads_management,pages_read_engagement";

export function getMetaOAuthUrl(state: string): string {
  const params = new URLSearchParams({
    client_id: process.env.META_APP_ID || "",
    redirect_uri: `${PORTAL_URL}/api/oauth/meta/callback`,
    scope: META_SCOPES,
    response_type: "code",
    state,
  });
  return `https://www.facebook.com/v21.0/dialog/oauth?${params}`;
}

export async function exchangeMetaCode(code: string): Promise<string> {
  // Exchange code for short-lived token
  const shortRes = await fetch(
    `https://graph.facebook.com/v21.0/oauth/access_token?` +
      new URLSearchParams({
        client_id: process.env.META_APP_ID || "",
        client_secret: process.env.META_APP_SECRET || "",
        redirect_uri: `${PORTAL_URL}/api/oauth/meta/callback`,
        code,
      })
  );

  if (!shortRes.ok) throw new Error("Meta token exchange failed");
  const { access_token: shortToken } = await shortRes.json();

  // Exchange short-lived for long-lived token (60 days)
  const longRes = await fetch(
    `https://graph.facebook.com/v21.0/oauth/access_token?` +
      new URLSearchParams({
        grant_type: "fb_exchange_token",
        client_id: process.env.META_APP_ID || "",
        client_secret: process.env.META_APP_SECRET || "",
        fb_exchange_token: shortToken,
      })
  );

  if (!longRes.ok) throw new Error("Meta long-lived token exchange failed");
  const { access_token: longToken } = await longRes.json();

  return longToken;
}

// ─── LinkedIn OAuth ─────────────────────────────────────────────────────

const LINKEDIN_SCOPES = "r_organization_social r_ads_reporting";

export function getLinkedInOAuthUrl(state: string): string {
  const params = new URLSearchParams({
    response_type: "code",
    client_id: process.env.LINKEDIN_CLIENT_ID || "",
    redirect_uri: `${PORTAL_URL}/api/oauth/linkedin/callback`,
    scope: LINKEDIN_SCOPES,
    state,
  });
  return `https://www.linkedin.com/oauth/v2/authorization?${params}`;
}

export async function exchangeLinkedInCode(code: string): Promise<string> {
  const res = await fetch("https://www.linkedin.com/oauth/v2/accessToken", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      client_id: process.env.LINKEDIN_CLIENT_ID || "",
      client_secret: process.env.LINKEDIN_CLIENT_SECRET || "",
      redirect_uri: `${PORTAL_URL}/api/oauth/linkedin/callback`,
    }),
  });

  if (!res.ok) throw new Error("LinkedIn token exchange failed");
  const { access_token } = await res.json();
  return access_token;
}

// ─── State token (CSRF protection) ─────────────────────────────────────

export function generateOAuthState(tenantId: string, platform: string): string {
  const data = JSON.stringify({ tenantId, platform, ts: Date.now() });
  return Buffer.from(data).toString("base64url");
}

export function parseOAuthState(state: string): { tenantId: string; platform: string; ts: number } | null {
  try {
    return JSON.parse(Buffer.from(state, "base64url").toString());
  } catch {
    return null;
  }
}
