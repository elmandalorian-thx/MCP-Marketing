import { NextRequest, NextResponse } from "next/server";
import { db } from "@/lib/db";
import { tenants, usageLogs } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";
import { createAlert } from "@/lib/admin";

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

  const results = { usageSpikes: 0, planApproaching: 0, planReached: 0 };

  const now = new Date();
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

  // 1. Usage spikes: single query comparing current hour vs 7-day hourly average per tenant
  const spikeRows = await db.execute(sql`
    WITH current_hour AS (
      SELECT tenant_id, count(*) AS cnt
      FROM usage_logs
      WHERE created_at >= ${oneHourAgo}
      GROUP BY tenant_id
    ),
    weekly_avg AS (
      SELECT tenant_id, count(*) / greatest(extract(epoch from (now() - ${sevenDaysAgo}::timestamptz)) / 3600, 1) AS hourly_avg
      FROM usage_logs
      WHERE created_at >= ${sevenDaysAgo}
      GROUP BY tenant_id
    )
    SELECT c.tenant_id, t.name AS tenant_name, c.cnt AS current_count, w.hourly_avg
    FROM current_hour c
    JOIN weekly_avg w ON c.tenant_id = w.tenant_id
    JOIN tenants t ON c.tenant_id = t.id
    WHERE w.hourly_avg > 0 AND c.cnt > w.hourly_avg * 2
  `);

  for (const row of (spikeRows as any) as any[]) {
    await createAlert({
      tenantId: row.tenant_id,
      severity: "warning",
      type: "usage_spike",
      title: `Usage spike: ${row.tenant_name}`,
      description: `${row.current_count} calls in the last hour vs ${Math.round(row.hourly_avg)} hourly average.`,
    }, { deduplicate: true });
    results.usageSpikes++;
  }

  // 2. Plan limit checks
  const tenantUsage = await db
    .select({
      tenantId: tenants.id,
      tenantName: tenants.name,
      maxCalls: tenants.maxMonthlyCalls,
      currentCalls: sql<number>`(SELECT count(*) FROM usage_logs WHERE usage_logs.tenant_id = tenants.id AND usage_logs.created_at >= ${monthStart})`,
    })
    .from(tenants);

  for (const t of tenantUsage) {
    const pct = t.maxCalls > 0 ? (t.currentCalls / t.maxCalls) * 100 : 0;

    if (pct >= 100) {
      await createAlert({
        tenantId: t.tenantId,
        severity: "warning",
        type: "plan_limit_reached",
        title: `Plan limit reached: ${t.tenantName}`,
        description: `${t.currentCalls.toLocaleString()} / ${t.maxCalls.toLocaleString()} calls used.`,
      }, { deduplicate: true });
      results.planReached++;
    } else if (pct >= 80) {
      await createAlert({
        tenantId: t.tenantId,
        severity: "info",
        type: "plan_limit_approaching",
        title: `Plan limit approaching: ${t.tenantName}`,
        description: `${Math.round(pct)}% used (${t.currentCalls.toLocaleString()} / ${t.maxCalls.toLocaleString()}).`,
      }, { deduplicate: true });
      results.planApproaching++;
    }
  }

  return NextResponse.json({ ok: true, results });
}
