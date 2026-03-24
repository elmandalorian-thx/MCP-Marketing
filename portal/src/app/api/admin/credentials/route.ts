import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { PLATFORMS } from "@/lib/utils";

/**
 * Super admin credential manager.
 * Reads platform credentials status from environment variables.
 * These are the server-level credentials (dev tokens, service accounts),
 * NOT per-tenant OAuth connections.
 */

function getCredentialStatus(): Record<string, { configured: boolean; keys: Record<string, boolean> }> {
  const status: Record<string, { configured: boolean; keys: Record<string, boolean> }> = {};

  for (const [platform, config] of Object.entries(PLATFORMS)) {
    const keys: Record<string, boolean> = {};
    let allSet = true;

    for (const cred of config.requiredCreds) {
      const isSet = !!process.env[cred];
      keys[cred] = isSet;
      if (!isSet) allSet = false;
    }

    status[platform] = {
      configured: config.requiredCreds.length === 0 ? true : allSet,
      keys,
    };
  }

  return status;
}

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const status = getCredentialStatus();
  const platforms = Object.entries(PLATFORMS).map(([key, config]) => ({
    key,
    label: config.label,
    color: config.color,
    requiredCreds: config.requiredCreds,
    status: status[key],
  }));

  return NextResponse.json({ platforms });
}
