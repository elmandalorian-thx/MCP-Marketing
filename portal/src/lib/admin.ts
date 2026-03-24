import { db } from "./db";
import { alerts } from "./schema";
import type { NewAlert } from "./schema";
import { and, eq, gte } from "drizzle-orm";
import { sendAlertNotification } from "./notifications";

/**
 * Create an alert and dispatch notifications based on severity.
 * Deduplicates cron-generated alerts: skips if same (tenantId, type) exists within 24h.
 */
export async function createAlert(
  alert: NewAlert,
  options: { deduplicate?: boolean } = {}
): Promise<void> {
  if (options.deduplicate) {
    const since = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const [existing] = await db
      .select({ id: alerts.id })
      .from(alerts)
      .where(
        and(
          alert.tenantId ? eq(alerts.tenantId, alert.tenantId) : undefined,
          eq(alerts.type, alert.type),
          gte(alerts.createdAt, since)
        )
      )
      .limit(1);
    if (existing) return;
  }

  const [created] = await db.insert(alerts).values(alert).returning();

  // Dispatch notifications based on severity
  if (alert.severity === "warning" || alert.severity === "critical") {
    await sendAlertNotification(created);
  }
}
