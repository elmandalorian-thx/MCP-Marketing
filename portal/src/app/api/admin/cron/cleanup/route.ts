import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { alerts, oauthChangeLog } from "@/lib/schema";
import { sql, lt } from "drizzle-orm";

function verifyCronSecret(request: NextRequest): boolean {
  const secret = process.env.CRON_SECRET;
  if (!secret) return false;
  const auth = request.headers.get("authorization");
  return auth === `Bearer ${secret}`;
}

export async function POST(request: NextRequest) {
  if (!verifyCronSecret(request)) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);
  const oneYearAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000);

  const alertsDeleted = await db
    .delete(alerts)
    .where(lt(alerts.createdAt, ninetyDaysAgo))
    .returning({ id: alerts.id });

  const logsDeleted = await db
    .delete(oauthChangeLog)
    .where(lt(oauthChangeLog.createdAt, oneYearAgo))
    .returning({ id: oauthChangeLog.id });

  return NextResponse.json({
    ok: true,
    alertsPruned: alertsDeleted.length,
    changeLogsPruned: logsDeleted.length,
  });
}
