import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { getMetaOAuthUrl, generateOAuthState } from "@/lib/oauth";

export async function GET() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.tenantId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const state = generateOAuthState(session.tenantId, "meta");
  const url = getMetaOAuthUrl(state);

  return NextResponse.redirect(url);
}
