import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { getLinkedInOAuthUrl, generateOAuthState } from "@/lib/oauth";

export async function GET() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.tenantId) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const state = generateOAuthState(session.tenantId, "linkedin");
  const url = getLinkedInOAuthUrl(state);

  return NextResponse.redirect(url);
}
