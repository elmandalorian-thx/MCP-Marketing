# Super Admin Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an owner-level super admin dashboard to the existing Next.js portal with tenant management, usage monitoring, OAuth abuse prevention, alerts with email+Telegram notifications, and sales page login integration.

**Architecture:** All new functionality lives inside the existing portal (`portal/`) as role-gated `/admin/*` routes. Two new DB tables (`oauth_change_log`, `alerts`) plus one column addition (`ip_address` on `usage_logs`). Super admin is identified by `SUPER_ADMIN_EMAIL` env var, checked in the JWT callback. An hourly cron endpoint handles usage spike detection and plan limit alerts.

**Tech Stack:** Next.js 14, TypeScript, Drizzle ORM, PostgreSQL, NextAuth 4, Tailwind CSS, Resend (email), Telegram Bot API

**Spec:** `docs/superpowers/specs/2026-03-24-super-admin-dashboard-design.md`

---

## File Structure

### New Files
```
portal/src/lib/
├── admin.ts                          # Super admin helpers (isSuperAdmin check, alert creation, notification dispatch)
├── notifications.ts                  # Email (Resend) + Telegram notification senders

portal/src/app/(admin)/
├── layout.tsx                        # Admin layout (sidebar with admin nav items)
├── admin/page.tsx                    # Overview dashboard (KPIs, recent signups, health)
├── admin/tenants/page.tsx            # Tenant list with search/filter/pagination
├── admin/tenants/[id]/page.tsx       # Tenant detail (users, keys, connections, usage)
├── admin/usage/page.tsx              # Usage dashboards (daily chart, hourly heatmap, leaderboards)
├── admin/alerts/page.tsx             # Alert feed with filters, mark read/resolve
├── admin/credentials/page.tsx        # Platform credential manager (14+ platforms)

portal/src/app/api/admin/
├── stats/route.ts                    # GET overview KPIs
├── tenants/route.ts                  # GET tenant list (search, filter, paginate)
├── tenants/[id]/route.ts             # GET tenant detail, PATCH plan/suspend, DELETE tenant
├── usage/route.ts                    # GET usage dashboards (daily, hourly, leaderboards)
├── alerts/route.ts                   # GET alert feed, PATCH mark read/resolve
├── credentials/route.ts              # GET/POST platform credentials, POST test connection
├── cron/check-alerts/route.ts        # POST hourly alert processing (usage spikes, plan limits)
├── cron/cleanup/route.ts             # POST daily data retention cleanup

portal/src/components/
├── admin-sidebar.tsx                 # Admin-specific sidebar nav

portal/src/types/
├── next-auth.d.ts                    # NextAuth type augmentation for isSuperAdmin
```

### Modified Files
```
portal/src/lib/schema.ts              # Add oauth_change_log, alerts tables; add ipAddress to usageLogs
portal/src/lib/auth.ts                # Add isSuperAdmin to jwt + session callbacks
portal/src/middleware.ts              # Add /admin/* route protection with super admin check
portal/src/app/api/connections/route.ts  # Add OAuth rate limiting + change logging
portal/src/components/sidebar.tsx     # Add admin link for super admin users
```

---

## Task 1: Database Schema — New Tables and Column

**Files:**
- Modify: `portal/src/lib/schema.ts`

- [ ] **Step 1: Add `oauthChangeLog` table to schema**

Add after the `usageLogs` table definition in `portal/src/lib/schema.ts`:

```typescript
// ── OAuth Change Log ────────────────────────────────────────────────

export const oauthChangeLog = pgTable("oauth_change_log", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  tenantId: uuid("tenant_id")
    .notNull()
    .references(() => tenants.id, { onDelete: "cascade" }),
  userId: uuid("user_id")
    .references(() => users.id, { onDelete: "cascade" }),
  actorType: varchar("actor_type", { length: 10 }).notNull().default("user"),
  platform: varchar("platform", { length: 50 }).notNull(),
  action: varchar("action", { length: 20 }).notNull(),
  ipAddress: varchar("ip_address", { length: 45 }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});
```

- [ ] **Step 2: Add `alerts` table to schema**

Add after the `oauthChangeLog` table:

```typescript
// ── Alerts ──────────────────────────────────────────────────────────

export const alerts = pgTable("alerts", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  tenantId: uuid("tenant_id")
    .references(() => tenants.id, { onDelete: "cascade" }),
  severity: varchar("severity", { length: 10 }).notNull(),
  type: varchar("type", { length: 30 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  description: text("description"),
  isRead: boolean("is_read").notNull().default(false),
  resolvedAt: timestamp("resolved_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});
```

- [ ] **Step 3: Add `isSuspended` column to `tenants` table**

In the existing `tenants` definition, add after `updatedAt`:

```typescript
  isSuspended: boolean("is_suspended").notNull().default(false),
```

- [ ] **Step 4: Add `ipAddress` column to `usageLogs` table**

In the existing `usageLogs` definition, add after `errorMessage`:

```typescript
  ipAddress: varchar("ip_address", { length: 45 }),
```

- [ ] **Step 5: Add type exports**

Add to the type exports section:

```typescript
export type OauthChangeLog = typeof oauthChangeLog.$inferSelect;
export type Alert = typeof alerts.$inferSelect;
export type NewAlert = typeof alerts.$inferInsert;
```

- [ ] **Step 6: Generate and run migration**

```bash
cd portal && npx drizzle-kit generate && npx drizzle-kit push
```

Expected: Migration generated in `portal/drizzle/` and applied to database.

- [ ] **Step 7: Commit**

```bash
git add portal/src/lib/schema.ts portal/drizzle/
git commit -m "feat: add oauth_change_log, alerts tables, isSuspended and ipAddress columns"
```

---

## Task 2: Super Admin Auth — JWT, Session, Middleware

**Files:**
- Modify: `portal/src/lib/auth.ts`
- Modify: `portal/src/middleware.ts`

- [ ] **Step 1: Add `isSuperAdmin` to JWT callback**

In `portal/src/lib/auth.ts`, modify the `jwt` callback (line 172-181):

```typescript
    async jwt({ token, user }) {
      if (user) {
        token.userId = (user as any).id || user.id;
        token.tenantId = (user as any).tenantId;
        token.tenantName = (user as any).tenantName;
        token.role = (user as any).role;
        token.planTier = (user as any).planTier;
      }
      // Ensure email is on token (defensive — NextAuth usually copies it)
      if (user?.email) token.email = user.email;
      // Super admin check — always re-evaluate (env var can change)
      token.isSuperAdmin = !!token.email && token.email === process.env.SUPER_ADMIN_EMAIL;
      return token;
    },
```

- [ ] **Step 2: Add `isSuperAdmin` to session callback**

Modify the `session` callback (line 183-192):

```typescript
    async session({ session, token }) {
      return {
        ...session,
        userId: token.userId as string,
        tenantId: token.tenantId as string,
        tenantName: token.tenantName as string,
        role: token.role as string,
        planTier: token.planTier as string,
        isSuperAdmin: token.isSuperAdmin as boolean,
      };
    },
```

- [ ] **Step 3: Update middleware for admin routes**

Replace `portal/src/middleware.ts` content:

```typescript
import { getToken } from "next-auth/jwt";
import { NextRequest, NextResponse } from "next/server";

const protectedRoutes = ["/dashboard", "/connect", "/keys", "/clients", "/usage", "/profile"];
const adminRoutes = ["/admin"];
const authRoutes = ["/", "/signup"];

export async function middleware(request: NextRequest) {
  const token = await getToken({ req: request });
  const { pathname } = request.nextUrl;

  // Protect admin routes — super admin only
  if (adminRoutes.some((r) => pathname.startsWith(r))) {
    if (!token) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    if (!token.isSuperAdmin) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  // Protect dashboard routes
  if (protectedRoutes.some((r) => pathname.startsWith(r))) {
    if (!token) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  }

  // Redirect authenticated users away from login/signup
  if (authRoutes.includes(pathname) && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/", "/signup",
    "/dashboard/:path*", "/connect/:path*", "/keys/:path*",
    "/clients/:path*", "/usage/:path*", "/profile/:path*",
    "/admin/:path*",
  ],
};
```

- [ ] **Step 4: Verify middleware works**

```bash
cd portal && npx next build
```

Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 5: Commit**

- [ ] **Step 6: Create NextAuth type augmentation**

Create `portal/src/types/next-auth.d.ts`:

```typescript
import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    userId: string;
    tenantId: string;
    tenantName: string;
    role: string;
    planTier: string;
    isSuperAdmin: boolean;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    userId?: string;
    tenantId?: string;
    tenantName?: string;
    role?: string;
    planTier?: string;
    isSuperAdmin?: boolean;
  }
}
```

- [ ] **Step 7: Commit**

```bash
git add portal/src/lib/auth.ts portal/src/middleware.ts portal/src/types/next-auth.d.ts
git commit -m "feat: add super admin auth via SUPER_ADMIN_EMAIL env var"
```

---

## Task 3: Admin Helpers and Notification System

**Files:**
- Create: `portal/src/lib/admin.ts`
- Create: `portal/src/lib/notifications.ts`

- [ ] **Step 1: Create admin helper utilities**

Create `portal/src/lib/admin.ts`:

```typescript
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
```

- [ ] **Step 2: Create notification senders**

Create `portal/src/lib/notifications.ts`:

```typescript
import type { Alert } from "./schema";

const SEVERITY_EMOJI: Record<string, string> = {
  info: "ℹ️",
  warning: "⚠️",
  critical: "🚨",
};

/**
 * Send alert notification via email and/or Telegram based on severity.
 * - warning: email only
 * - critical: email + Telegram
 */
export async function sendAlertNotification(alert: Alert): Promise<void> {
  const promises: Promise<void>[] = [];

  if (alert.severity === "warning" || alert.severity === "critical") {
    promises.push(sendEmail(alert));
  }
  if (alert.severity === "critical") {
    promises.push(sendTelegram(alert));
  }

  await Promise.allSettled(promises);
}

async function sendEmail(alert: Alert): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY;
  const toEmail = process.env.SUPER_ADMIN_EMAIL;
  if (!apiKey || !toEmail) return;

  const emoji = SEVERITY_EMOJI[alert.severity] || "";

  try {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "Marketing MCP <alerts@statika.net>",
        to: [toEmail],
        subject: `${emoji} [${alert.severity.toUpperCase()}] ${alert.title}`,
        text: `${alert.title}\n\n${alert.description || ""}\n\nTime: ${alert.createdAt}\nType: ${alert.type}`,
      }),
    });
  } catch (e) {
    console.error("Failed to send alert email:", e);
  }
}

async function sendTelegram(alert: Alert): Promise<void> {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!botToken || !chatId) return;

  const emoji = SEVERITY_EMOJI[alert.severity] || "";
  const text = `${emoji} *${alert.severity.toUpperCase()}*: ${alert.title}\n\n${alert.description || ""}\n\nType: \`${alert.type}\``;

  try {
    await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "Markdown",
      }),
    });
  } catch (e) {
    console.error("Failed to send Telegram alert:", e);
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add portal/src/lib/admin.ts portal/src/lib/notifications.ts
git commit -m "feat: add alert creation helper and email+Telegram notifications"
```

---

## Task 4: OAuth Rate Limiting — Connection Route Changes

**Files:**
- Modify: `portal/src/app/api/connections/route.ts`

- [ ] **Step 1: Add rate limiting imports and helper**

At the top of `portal/src/app/api/connections/route.ts`, add after existing imports:

```typescript
import { oauthChangeLog } from "@/lib/schema";
import { gte, sql } from "drizzle-orm";
import { createAlert } from "@/lib/admin";
```

Add a rate check helper after the `encrypt` function:

```typescript
async function checkOAuthRateLimit(
  tenantId: string,
  platform: string
): Promise<{ blocked: boolean; retryAfterSeconds?: number }> {
  const tenMinutesAgo = new Date(Date.now() - 10 * 60 * 1000);

  const [result] = await db
    .select({ count: sql<number>`count(*)` })
    .from(oauthChangeLog)
    .where(
      and(
        eq(oauthChangeLog.tenantId, tenantId),
        eq(oauthChangeLog.platform, platform),
        gte(oauthChangeLog.createdAt, tenMinutesAgo)
      )
    );

  if ((result?.count ?? 0) >= 4) {
    // Find the oldest change in the window to calculate retry time
    const [oldest] = await db
      .select({ createdAt: oauthChangeLog.createdAt })
      .from(oauthChangeLog)
      .where(
        and(
          eq(oauthChangeLog.tenantId, tenantId),
          eq(oauthChangeLog.platform, platform),
          gte(oauthChangeLog.createdAt, tenMinutesAgo)
        )
      )
      .orderBy(oauthChangeLog.createdAt)
      .limit(1);

    const retryAfterMs = oldest
      ? (oldest.createdAt!.getTime() + 10 * 60 * 1000) - Date.now()
      : 600000;

    return { blocked: true, retryAfterSeconds: Math.ceil(Math.max(retryAfterMs, 0) / 1000) };
  }

  return { blocked: false };
}

async function logOAuthChange(
  tenantId: string,
  userId: string | null,
  platform: string,
  action: string,
  ip: string | null
): Promise<void> {
  await db.insert(oauthChangeLog).values({
    tenantId,
    userId,
    actorType: "user",
    platform,
    action,
    ipAddress: ip,
  });
}
```

- [ ] **Step 2: Add rate limiting to POST handler**

In the `POST` function, add after the `if (!platform || !credentials)` check:

```typescript
  // OAuth rate limiting
  const rateCheck = await checkOAuthRateLimit(tenantId, platform);
  if (rateCheck.blocked) {
    return NextResponse.json(
      { error: `Too many credential changes. Try again in ${rateCheck.retryAfterSeconds} seconds.` },
      { status: 429 }
    );
  }
```

Add after the successful save (before the `return`):

```typescript
  // Log the change
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || null;
  const userId = (session as any)?.userId || null;
  await logOAuthChange(tenantId, userId, platform, existing ? "updated" : "connected", ip);
```

- [ ] **Step 3: Add rate limiting to DELETE handler**

In the `DELETE` function, add after the `if (!platform)` check:

```typescript
  // OAuth rate limiting
  const rateCheck = await checkOAuthRateLimit(tenantId, platform);
  if (rateCheck.blocked) {
    return NextResponse.json(
      { error: `Too many credential changes. Try again in ${rateCheck.retryAfterSeconds} seconds.` },
      { status: 429 }
    );
  }
```

Add after the successful disconnect (before the `return`):

```typescript
  // Log the change
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || null;
  const userId = (session as any)?.userId || null;
  await logOAuthChange(tenantId, userId, platform, "disconnected", ip);
```

- [ ] **Step 4: Commit**

```bash
git add portal/src/app/api/connections/route.ts
git commit -m "feat: add OAuth rate limiting (4 changes/10min) and change logging"
```

---

## Task 5: Admin Layout and Sidebar

**Files:**
- Create: `portal/src/components/admin-sidebar.tsx`
- Create: `portal/src/components/alert-badge.tsx`
- Create: `portal/src/app/(admin)/layout.tsx`
- Modify: `portal/src/components/sidebar.tsx`

- [ ] **Step 1: Create admin sidebar**

Create `portal/src/components/admin-sidebar.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const adminNav = [
  { href: "/admin", label: "Overview", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4" },
  { href: "/admin/tenants", label: "Tenants", icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" },
  { href: "/admin/usage", label: "Usage", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { href: "/admin/alerts", label: "Alerts", icon: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" },
  { href: "/admin/credentials", label: "Credentials", icon: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" },
];

export function AdminSidebar() {
  const pathname = usePathname();
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    fetch("/api/admin/alerts?unread=true&limit=1")
      .then((r) => r.json())
      .then((d) => setAlertCount(d.data?.length > 0 ? d.data.length : 0))
      .catch(() => {});
  }, []);

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-[260px] bg-[#1a1a2e] flex flex-col z-30">
      {/* Brand */}
      <div className="px-6 py-6 border-b border-white/10">
        <Link href="/admin" className="flex items-center gap-3 no-underline">
          <div className="w-9 h-9 rounded-[10px] bg-gradient-to-br from-[#ef8157] to-[#ffa726] flex items-center justify-center text-white font-bold text-sm shadow-sm">
            A
          </div>
          <div>
            <div className="text-[0.9rem] font-bold text-white leading-tight">Marketing MCP</div>
            <div className="text-[0.65rem] font-medium text-white/50 uppercase tracking-wider">Super Admin</div>
          </div>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {adminNav.map((item) => {
          const active = pathname === item.href || (item.href !== "/admin" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-[10px] rounded-[10px] text-[0.82rem] font-semibold no-underline transition-all duration-150 ${
                active
                  ? "bg-white/10 text-[#ffa726]"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              }`}
            >
              <svg className="w-[18px] h-[18px] flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
              </svg>
              {item.label}
              {item.href === "/admin/alerts" && alertCount > 0 && (
                <span className="ml-auto min-w-[20px] h-5 rounded-full bg-[#ef8157] text-white text-[0.65rem] font-bold flex items-center justify-center px-1.5">
                  {alertCount > 99 ? "99+" : alertCount}
                </span>
              )}
              {active && item.href !== "/admin/alerts" && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#ffa726]" />}
            </Link>
          );
        })}
      </nav>

      {/* Back to portal */}
      <div className="px-4 py-4 border-t border-white/10">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 px-3 py-2 text-[0.75rem] text-white/40 no-underline hover:text-white/70 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          Back to Portal
        </Link>
      </div>
    </aside>
  );
}
```

- [ ] **Step 3: Create admin layout**

Create `portal/src/app/(admin)/layout.tsx`:

```typescript
import { AdminSidebar } from "@/components/admin-sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#f8f9fa]">
      <AdminSidebar />
      <div className="ml-[260px]">
        {children}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Add admin link to subscriber sidebar**

In `portal/src/components/sidebar.tsx`, this change requires making the sidebar session-aware. Replace the entire component to add a conditional admin link at the bottom of the nav. After the `nav.map(...)` block inside `<nav>`, add:

```typescript
// Add this import at the top
import { useSession } from "next-auth/react";

// Inside the Sidebar component, add:
  const { data: session } = useSession();

// After the nav.map() closing, before </nav>:
        {(session as any)?.isSuperAdmin && (
          <>
            <div className="my-3 mx-3 border-t border-[#eee]" />
            <Link
              href="/admin"
              className={`flex items-center gap-3 px-4 py-[10px] rounded-[10px] text-[0.82rem] font-semibold no-underline transition-all duration-150 text-[#ef8157] hover:bg-[#ef8157]/5`}
            >
              <svg className="w-[18px] h-[18px] flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
              Super Admin
            </Link>
          </>
        )}
```

- [ ] **Step 5: Commit**

```bash
git add portal/src/components/admin-sidebar.tsx portal/src/components/alert-badge.tsx portal/src/app/\(admin\)/layout.tsx portal/src/components/sidebar.tsx
git commit -m "feat: add admin layout, sidebar, and alert badge components"
```

---

## Task 6: Admin API — Overview Stats

**Files:**
- Create: `portal/src/app/api/admin/stats/route.ts`

- [ ] **Step 1: Create stats API route**

Create `portal/src/app/api/admin/stats/route.ts`:

```typescript
import { NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, usageLogs, alerts } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";

export async function GET(request: Request) {
  const token = await getToken({ req: request as any });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [
    tenantCount,
    userCount,
    callsToday,
    callsMonth,
    activeTenants,
    planBreakdown,
    recentSignups,
    unreadAlerts,
  ] = await Promise.all([
    db.select({ count: sql<number>`count(*)` }).from(tenants),
    db.select({ count: sql<number>`count(*)` }).from(users),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, todayStart)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, monthStart)),
    db.select({ count: sql<number>`count(distinct ${usageLogs.tenantId})` }).from(usageLogs).where(gte(usageLogs.createdAt, thirtyDaysAgo)),
    db.select({ planTier: tenants.planTier, count: sql<number>`count(*)` }).from(tenants).groupBy(tenants.planTier),
    db.select({ id: tenants.id, name: tenants.name, planTier: tenants.planTier, createdAt: tenants.createdAt }).from(tenants).where(gte(tenants.createdAt, sevenDaysAgo)).orderBy(sql`created_at DESC`).limit(10),
    db.select({ count: sql<number>`count(*)` }).from(alerts).where(eq(alerts.isRead, false)),
  ]);

  return NextResponse.json({
    totalTenants: tenantCount[0]?.count ?? 0,
    totalUsers: userCount[0]?.count ?? 0,
    callsToday: callsToday[0]?.count ?? 0,
    callsThisMonth: callsMonth[0]?.count ?? 0,
    activeTenants: activeTenants[0]?.count ?? 0,
    planBreakdown: planBreakdown.reduce((acc, r) => ({ ...acc, [r.planTier]: r.count }), {}),
    recentSignups,
    unreadAlerts: unreadAlerts[0]?.count ?? 0,
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/api/admin/stats/route.ts
git commit -m "feat: add admin stats API endpoint"
```

---

## Task 7: Admin API — Tenant Management

**Files:**
- Create: `portal/src/app/api/admin/tenants/route.ts`
- Create: `portal/src/app/api/admin/tenants/[id]/route.ts`

- [ ] **Step 1: Create tenant list API**

Create `portal/src/app/api/admin/tenants/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, platformConnections, usageLogs } from "@/lib/schema";
import { sql, eq, ilike, gte, and, gt } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { searchParams } = request.nextUrl;
  const search = searchParams.get("search") || "";
  const plan = searchParams.get("plan") || "";
  const cursor = searchParams.get("cursor") || "";
  const limit = Math.min(parseInt(searchParams.get("limit") || "20"), 100);

  const monthStart = new Date(new Date().getFullYear(), new Date().getMonth(), 1);

  // Build conditions
  const conditions = [];
  if (search) conditions.push(ilike(tenants.name, `%${search}%`));
  if (plan) conditions.push(eq(tenants.planTier, plan));
  if (cursor) conditions.push(gt(tenants.id, cursor));

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const rows = await db
    .select({
      id: tenants.id,
      name: tenants.name,
      slug: tenants.slug,
      planTier: tenants.planTier,
      maxMonthlyCalls: tenants.maxMonthlyCalls,
      createdAt: tenants.createdAt,
      userCount: sql<number>`(SELECT count(*) FROM users WHERE users.tenant_id = tenants.id)`,
      connectionCount: sql<number>`(SELECT count(*) FROM platform_connections WHERE platform_connections.tenant_id = tenants.id AND platform_connections.is_active = true)`,
      monthlyUsage: sql<number>`(SELECT count(*) FROM usage_logs WHERE usage_logs.tenant_id = tenants.id AND usage_logs.created_at >= ${monthStart})`,
    })
    .from(tenants)
    .where(where)
    .orderBy(tenants.id)
    .limit(limit + 1);

  const hasMore = rows.length > limit;
  const data = hasMore ? rows.slice(0, limit) : rows;
  const nextCursor = hasMore ? data[data.length - 1].id : null;

  return NextResponse.json({ data, nextCursor });
}
```

- [ ] **Step 2: Create tenant detail / update / delete API**

Create `portal/src/app/api/admin/tenants/[id]/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { tenants, users, apiKeys, platformConnections, usageLogs } from "@/lib/schema";
import { eq, sql, gte } from "drizzle-orm";
import { PLAN_LIMITS } from "@/lib/utils";

export async function GET(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { id } = params;
  const monthStart = new Date(new Date().getFullYear(), new Date().getMonth(), 1);

  const [tenant] = await db.select().from(tenants).where(eq(tenants.id, id)).limit(1);
  if (!tenant) return NextResponse.json({ error: "Tenant not found" }, { status: 404 });

  const [tenantUsers, tenantKeys, tenantConnections, tenantUsage] = await Promise.all([
    db.select({ id: users.id, email: users.email, name: users.name, role: users.role, createdAt: users.createdAt }).from(users).where(eq(users.tenantId, id)),
    db.select({ id: apiKeys.id, keyPrefix: apiKeys.keyPrefix, label: apiKeys.label, isActive: apiKeys.isActive, lastUsedAt: apiKeys.lastUsedAt, createdAt: apiKeys.createdAt }).from(apiKeys).where(eq(apiKeys.tenantId, id)),
    db.select({ id: platformConnections.id, platform: platformConnections.platform, isActive: platformConnections.isActive, createdAt: platformConnections.createdAt }).from(platformConnections).where(eq(platformConnections.tenantId, id)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(eq(usageLogs.tenantId, id)),
  ]);

  return NextResponse.json({
    tenant,
    users: tenantUsers,
    apiKeys: tenantKeys,
    connections: tenantConnections,
    totalUsage: tenantUsage[0]?.count ?? 0,
  });
}

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { id } = params;
  const body = await request.json();
  const updates: Record<string, any> = {};

  if (body.planTier && body.planTier in PLAN_LIMITS) {
    const limits = PLAN_LIMITS[body.planTier as keyof typeof PLAN_LIMITS];
    updates.planTier = body.planTier;
    updates.maxConnections = limits.connections;
    updates.maxMonthlyCalls = limits.monthlyCalls;
  }

  if (typeof body.isSuspended === "boolean") {
    updates.isSuspended = body.isSuspended;
  }

  if (Object.keys(updates).length === 0) {
    return NextResponse.json({ error: "No valid updates" }, { status: 400 });
  }

  updates.updatedAt = new Date();

  await db.update(tenants).set(updates).where(eq(tenants.id, id));
  return NextResponse.json({ updated: true });
}

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  await db.delete(tenants).where(eq(tenants.id, params.id));
  return NextResponse.json({ deleted: true });
}
```

- [ ] **Step 3: Commit**

```bash
git add portal/src/app/api/admin/tenants/
git commit -m "feat: add admin tenant list, detail, update, delete APIs"
```

---

## Task 8: Admin API — Usage Dashboards

**Files:**
- Create: `portal/src/app/api/admin/usage/route.ts`

- [ ] **Step 1: Create usage dashboard API**

Create `portal/src/app/api/admin/usage/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { usageLogs, tenants } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [dailyCounts, hourlyCounts, topTenants, topTools, errorRates] = await Promise.all([
    // Daily calls (last 30 days)
    db.select({
      date: sql<string>`date(created_at)`,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(sql`date(created_at)`)
      .orderBy(sql`date(created_at)`),

    // Hourly calls (last 7 days)
    db.select({
      date: sql<string>`date(created_at)`,
      hour: sql<number>`extract(hour from created_at)`,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, sevenDaysAgo))
      .groupBy(sql`date(created_at)`, sql`extract(hour from created_at)`)
      .orderBy(sql`date(created_at)`, sql`extract(hour from created_at)`),

    // Top 10 tenants by usage (last 30 days)
    db.select({
      tenantId: usageLogs.tenantId,
      tenantName: tenants.name,
      count: sql<number>`count(*)`,
    }).from(usageLogs)
      .innerJoin(tenants, eq(usageLogs.tenantId, tenants.id))
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.tenantId, tenants.name)
      .orderBy(sql`count(*) DESC`)
      .limit(10),

    // Top 10 tools by volume
    db.select({
      toolName: usageLogs.toolName,
      count: sql<number>`count(*)`,
      avgDuration: sql<number>`avg(duration_ms)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) DESC`)
      .limit(10),

    // Error rates by tool
    db.select({
      toolName: usageLogs.toolName,
      total: sql<number>`count(*)`,
      failures: sql<number>`count(*) filter (where not success)`,
    }).from(usageLogs)
      .where(gte(usageLogs.createdAt, thirtyDaysAgo))
      .groupBy(usageLogs.toolName)
      .orderBy(sql`count(*) filter (where not success) DESC`)
      .limit(10),
  ]);

  return NextResponse.json({ dailyCounts, hourlyCounts, topTenants, topTools, errorRates });
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/api/admin/usage/route.ts
git commit -m "feat: add admin usage dashboard API (daily, hourly, leaderboards)"
```

---

## Task 9: Admin API — Alerts

**Files:**
- Create: `portal/src/app/api/admin/alerts/route.ts`

- [ ] **Step 1: Create alerts API**

Create `portal/src/app/api/admin/alerts/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { db } from "@/lib/db";
import { alerts } from "@/lib/schema";
import { sql, eq, and, lt, inArray } from "drizzle-orm";

export async function GET(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const { searchParams } = request.nextUrl;
  const severity = searchParams.get("severity") || "";
  const type = searchParams.get("type") || "";
  const unreadOnly = searchParams.get("unread") === "true";
  const cursor = searchParams.get("cursor") || "";
  const limit = Math.min(parseInt(searchParams.get("limit") || "30"), 100);

  const conditions = [];
  if (severity) conditions.push(eq(alerts.severity, severity));
  if (type) conditions.push(eq(alerts.type, type));
  if (unreadOnly) conditions.push(eq(alerts.isRead, false));
  if (cursor) conditions.push(lt(alerts.id, parseInt(cursor)));

  const where = conditions.length > 0 ? and(...conditions) : undefined;

  const rows = await db
    .select()
    .from(alerts)
    .where(where)
    .orderBy(sql`id DESC`)
    .limit(limit + 1);

  const hasMore = rows.length > limit;
  const data = hasMore ? rows.slice(0, limit) : rows;
  const nextCursor = hasMore ? data[data.length - 1].id : null;

  return NextResponse.json({ data, nextCursor });
}

export async function PATCH(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.isSuperAdmin) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const body = await request.json();
  const { action, ids } = body;

  if (!action || !ids || !Array.isArray(ids)) {
    return NextResponse.json({ error: "action and ids required" }, { status: 400 });
  }

  const idNumbers = ids.map(Number).filter(Boolean);

  if (action === "markRead") {
    await db.update(alerts).set({ isRead: true, updatedAt: new Date() }).where(inArray(alerts.id, idNumbers));
  } else if (action === "resolve") {
    await db.update(alerts).set({ resolvedAt: new Date(), isRead: true, updatedAt: new Date() }).where(inArray(alerts.id, idNumbers));
  } else {
    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  }

  return NextResponse.json({ updated: idNumbers.length });
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/api/admin/alerts/route.ts
git commit -m "feat: add admin alerts API with filtering and bulk actions"
```

---

## Task 10: Admin API — Platform Credentials Manager

**Files:**
- Create: `portal/src/app/api/admin/credentials/route.ts`

- [ ] **Step 1: Create credentials management API**

Create `portal/src/app/api/admin/credentials/route.ts`:

```typescript
import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { PLATFORMS } from "@/lib/utils";

/**
 * Super admin credential manager.
 * Reads/writes platform credentials to environment variables.
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
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/api/admin/credentials/route.ts
git commit -m "feat: add admin credentials status API"
```

---

## Task 11: Admin API — Cron Endpoints

**Files:**
- Create: `portal/src/app/api/admin/cron/check-alerts/route.ts`
- Create: `portal/src/app/api/admin/cron/cleanup/route.ts`

- [ ] **Step 1: Create hourly alert check cron**

Create `portal/src/app/api/admin/cron/check-alerts/route.ts`:

```typescript
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

  for (const row of spikeRows.rows as any[]) {
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
```

- [ ] **Step 2: Create daily cleanup cron**

Create `portal/src/app/api/admin/cron/cleanup/route.ts`:

```typescript
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
```

- [ ] **Step 3: Commit**

```bash
git add portal/src/app/api/admin/cron/
git commit -m "feat: add hourly alert check and daily cleanup cron endpoints"
```

---

## Task 12: Admin Pages — Overview Dashboard

**Files:**
- Create: `portal/src/app/(admin)/admin/page.tsx`

- [ ] **Step 1: Create admin overview page**

Create `portal/src/app/(admin)/admin/page.tsx`:

```typescript
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { tenants, users, usageLogs, alerts } from "@/lib/schema";
import { sql, gte, eq } from "drizzle-orm";
import { Topbar } from "@/components/topbar";
import { StatCard } from "@/components/stat-card";

async function getAdminStats() {
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [
    tenantCount,
    userCount,
    callsToday,
    callsMonth,
    planBreakdown,
    recentSignups,
    unreadAlerts,
  ] = await Promise.all([
    db.select({ count: sql<number>`count(*)` }).from(tenants),
    db.select({ count: sql<number>`count(*)` }).from(users),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, todayStart)),
    db.select({ count: sql<number>`count(*)` }).from(usageLogs).where(gte(usageLogs.createdAt, monthStart)),
    db.select({ planTier: tenants.planTier, count: sql<number>`count(*)` }).from(tenants).groupBy(tenants.planTier),
    db.select({ id: tenants.id, name: tenants.name, planTier: tenants.planTier, createdAt: tenants.createdAt }).from(tenants).where(gte(tenants.createdAt, sevenDaysAgo)).orderBy(sql`created_at DESC`).limit(10),
    db.select({ count: sql<number>`count(*)` }).from(alerts).where(eq(alerts.isRead, false)),
  ]);

  return {
    totalTenants: tenantCount[0]?.count ?? 0,
    totalUsers: userCount[0]?.count ?? 0,
    callsToday: callsToday[0]?.count ?? 0,
    callsMonth: callsMonth[0]?.count ?? 0,
    plans: planBreakdown.reduce((acc, r) => ({ ...acc, [r.planTier]: r.count }), {} as Record<string, number>),
    recentSignups,
    unreadAlerts: unreadAlerts[0]?.count ?? 0,
  };
}

export default async function AdminOverviewPage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.isSuperAdmin) redirect("/dashboard");

  const stats = await getAdminStats();

  return (
    <>
      <Topbar title="Super Admin — Overview" />
      <div className="p-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
          <StatCard icon="🏢" label="Tenants" value={stats.totalTenants} footer="Total accounts" color="teal" />
          <StatCard icon="👥" label="Users" value={stats.totalUsers} footer="Total users" color="green" />
          <StatCard icon="📡" label="Calls Today" value={stats.callsToday} footer={`${stats.callsMonth.toLocaleString()} this month`} color="amber" />
          <StatCard icon="🔔" label="Unread Alerts" value={stats.unreadAlerts} footer="Pending review" color="blue" />
        </div>

        {/* Plan breakdown */}
        <div className="card p-6 mb-8">
          <h3 className="text-[0.85rem] font-bold mb-4">Plan Distribution</h3>
          <div className="grid grid-cols-4 gap-4">
            {["free", "starter", "pro", "enterprise"].map((plan) => (
              <div key={plan} className="text-center">
                <div className="text-2xl font-bold text-[#252422]">{stats.plans[plan] ?? 0}</div>
                <div className="text-[0.72rem] text-[#9A9A9A] capitalize">{plan}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent signups */}
        <div className="card">
          <div className="px-6 py-4 border-b border-[#eee]">
            <h3 className="text-[0.85rem] font-bold">Recent Signups (7 days)</h3>
          </div>
          {stats.recentSignups.length === 0 ? (
            <div className="px-6 py-12 text-center text-[0.85rem] text-[#9A9A9A]">No new signups</div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {stats.recentSignups.map((t) => (
                <div key={t.id} className="px-6 py-3.5 flex items-center justify-between hover:bg-[#fafaf8]">
                  <div>
                    <span className="text-[0.8rem] font-semibold text-[#252422]">{t.name}</span>
                    <span className="ml-2 badge badge-muted text-[0.65rem]">{t.planTier}</span>
                  </div>
                  <span className="text-[0.72rem] text-[#9A9A9A]">
                    {t.createdAt ? new Date(t.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : ""}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add portal/src/app/\(admin\)/admin/page.tsx
git commit -m "feat: add admin overview dashboard page"
```

---

## Task 13: Admin Pages — Tenant List & Detail

**Files:**
- Create: `portal/src/app/(admin)/admin/tenants/page.tsx`
- Create: `portal/src/app/(admin)/admin/tenants/[id]/page.tsx`

- [ ] **Step 1: Create tenant list page**

Create `portal/src/app/(admin)/admin/tenants/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";
import Link from "next/link";

interface TenantRow {
  id: string;
  name: string;
  slug: string;
  planTier: string;
  maxMonthlyCalls: number;
  createdAt: string;
  userCount: number;
  connectionCount: number;
  monthlyUsage: number;
}

export default function TenantsPage() {
  const [tenants, setTenants] = useState<TenantRow[]>([]);
  const [search, setSearch] = useState("");
  const [planFilter, setPlanFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (planFilter) params.set("plan", planFilter);

    fetch(`/api/admin/tenants?${params}`)
      .then((r) => r.json())
      .then((d) => { setTenants(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [search, planFilter]);

  return (
    <>
      <Topbar title="Tenants" />
      <div className="p-8">
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="Search tenants..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-4 py-2 border border-[#eee] rounded-lg text-[0.82rem] w-64 focus:outline-none focus:border-[#51cbce]"
          />
          <select
            value={planFilter}
            onChange={(e) => setPlanFilter(e.target.value)}
            className="px-4 py-2 border border-[#eee] rounded-lg text-[0.82rem] focus:outline-none focus:border-[#51cbce]"
          >
            <option value="">All Plans</option>
            <option value="free">Free</option>
            <option value="starter">Starter</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>
        </div>

        {/* Table */}
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#eee] text-[0.72rem] uppercase tracking-wider text-[#9A9A9A]">
                <th className="px-6 py-3 text-left font-semibold">Tenant</th>
                <th className="px-6 py-3 text-left font-semibold">Plan</th>
                <th className="px-6 py-3 text-center font-semibold">Users</th>
                <th className="px-6 py-3 text-center font-semibold">Connections</th>
                <th className="px-6 py-3 text-center font-semibold">Usage</th>
                <th className="px-6 py-3 text-right font-semibold">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f4f3ef]">
              {loading ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-[0.82rem] text-[#9A9A9A]">Loading...</td></tr>
              ) : tenants.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-12 text-center text-[0.82rem] text-[#9A9A9A]">No tenants found</td></tr>
              ) : tenants.map((t) => (
                <tr key={t.id} className="hover:bg-[#fafaf8] transition-colors">
                  <td className="px-6 py-3.5">
                    <Link href={`/admin/tenants/${t.id}`} className="text-[0.82rem] font-semibold text-[#252422] hover:text-[#51cbce] no-underline">
                      {t.name}
                    </Link>
                  </td>
                  <td className="px-6 py-3.5">
                    <span className="badge badge-muted text-[0.65rem] capitalize">{t.planTier}</span>
                  </td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">{t.userCount}</td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">{t.connectionCount}</td>
                  <td className="px-6 py-3.5 text-center text-[0.8rem]">
                    {t.monthlyUsage.toLocaleString()} / {t.maxMonthlyCalls.toLocaleString()}
                  </td>
                  <td className="px-6 py-3.5 text-right text-[0.72rem] text-[#9A9A9A]">
                    {new Date(t.createdAt).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Create tenant detail page**

Create `portal/src/app/(admin)/admin/tenants/[id]/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";
import { useParams, useRouter } from "next/navigation";

export default function TenantDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/admin/tenants/${id}`)
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [id]);

  async function changePlan(planTier: string) {
    await fetch(`/api/admin/tenants/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ planTier }),
    });
    router.refresh();
    window.location.reload();
  }

  async function toggleSuspend() {
    await fetch(`/api/admin/tenants/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ isSuspended: !data.tenant.isSuspended }),
    });
    window.location.reload();
  }

  async function deleteTenant() {
    if (!confirm("Delete this tenant? This cannot be undone.")) return;
    await fetch(`/api/admin/tenants/${id}`, { method: "DELETE" });
    router.push("/admin/tenants");
  }

  if (loading) return <div className="p-8 text-[#9A9A9A]">Loading...</div>;
  if (!data?.tenant) return <div className="p-8 text-[#ef8157]">Tenant not found</div>;

  const { tenant, users, apiKeys, connections } = data;

  return (
    <>
      <Topbar title={tenant.name} />
      <div className="p-8">
        {/* Tenant info + actions */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-[#252422]">{tenant.name}</h2>
              <p className="text-[0.75rem] text-[#9A9A9A]">{tenant.slug} &middot; Plan: {tenant.planTier}</p>
            </div>
            <div className="flex gap-2">
              <select
                defaultValue={tenant.planTier}
                onChange={(e) => changePlan(e.target.value)}
                className="px-3 py-1.5 border border-[#eee] rounded-lg text-[0.8rem]"
              >
                <option value="free">Free</option>
                <option value="starter">Starter</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
              <button
                onClick={toggleSuspend}
                className={`px-3 py-1.5 rounded-lg text-[0.8rem] font-semibold ${
                  tenant.isSuspended
                    ? "bg-[#6bd098] text-white hover:bg-[#5bc088]"
                    : "bg-[#ffa726] text-white hover:bg-[#f59b16]"
                }`}
              >
                {tenant.isSuspended ? "Unsuspend" : "Suspend"}
              </button>
              <button
                onClick={deleteTenant}
                className="px-3 py-1.5 bg-[#ef8157] text-white rounded-lg text-[0.8rem] font-semibold hover:bg-[#e06a3e]"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Users */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Users ({users.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {users.map((u: any) => (
                <div key={u.id} className="px-6 py-3 flex items-center justify-between">
                  <div>
                    <div className="text-[0.8rem] font-semibold">{u.name || u.email}</div>
                    <div className="text-[0.7rem] text-[#9A9A9A]">{u.email}</div>
                  </div>
                  <span className="badge badge-muted text-[0.65rem]">{u.role}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Connections */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Connections ({connections.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {connections.map((c: any) => (
                <div key={c.id} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-semibold capitalize">{c.platform.replace(/_/g, " ")}</span>
                  <span className={`w-2 h-2 rounded-full ${c.isActive ? "bg-[#6bd098]" : "bg-[#9A9A9A]"}`} />
                </div>
              ))}
            </div>
          </div>

          {/* API Keys */}
          <div className="card lg:col-span-2">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">API Keys ({apiKeys.length})</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {apiKeys.map((k: any) => (
                <div key={k.id} className="px-6 py-3 flex items-center justify-between">
                  <div>
                    <span className="text-[0.8rem] font-mono font-semibold">{k.keyPrefix}...</span>
                    {k.label && <span className="ml-2 text-[0.72rem] text-[#9A9A9A]">{k.label}</span>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`w-2 h-2 rounded-full ${k.isActive ? "bg-[#6bd098]" : "bg-[#9A9A9A]"}`} />
                    <span className="text-[0.7rem] text-[#9A9A9A]">
                      {k.lastUsedAt ? `Last used ${new Date(k.lastUsedAt).toLocaleDateString()}` : "Never used"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add portal/src/app/\(admin\)/admin/tenants/
git commit -m "feat: add admin tenant list and detail pages"
```

---

## Task 14: Admin Pages — Usage, Alerts, Credentials

**Files:**
- Create: `portal/src/app/(admin)/admin/usage/page.tsx`
- Create: `portal/src/app/(admin)/admin/alerts/page.tsx`
- Create: `portal/src/app/(admin)/admin/credentials/page.tsx`

- [ ] **Step 1: Create usage dashboards page**

Create `portal/src/app/(admin)/admin/usage/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

export default function AdminUsagePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/usage")
      .then((r) => r.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <><Topbar title="Usage Analytics" /><div className="p-8 text-[#9A9A9A]">Loading...</div></>;

  return (
    <>
      <Topbar title="Usage Analytics" />
      <div className="p-8">
        {/* Daily trend (simple bar representation) */}
        <div className="card p-6 mb-6">
          <h3 className="text-[0.85rem] font-bold mb-4">Daily Calls (Last 30 Days)</h3>
          <div className="flex items-end gap-1 h-32">
            {(data?.dailyCounts || []).map((d: any, i: number) => {
              const max = Math.max(...(data?.dailyCounts || []).map((x: any) => x.count), 1);
              const height = (d.count / max) * 100;
              return (
                <div key={i} className="flex-1 group relative">
                  <div
                    className="w-full bg-gradient-to-t from-[#51cbce] to-[#6bd098] rounded-t"
                    style={{ height: `${height}%` }}
                  />
                  <div className="hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-[#252422] text-white text-[0.6rem] rounded whitespace-nowrap">
                    {d.date}: {d.count}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top tenants */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Top Tenants</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.topTenants || []).map((t: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-semibold">{t.tenantName}</span>
                  <span className="text-[0.8rem] font-mono">{t.count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top tools */}
          <div className="card">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Top Tools</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.topTools || []).map((t: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-mono font-semibold">{t.toolName}</span>
                  <div className="text-right">
                    <span className="text-[0.8rem] font-mono">{t.count.toLocaleString()}</span>
                    {t.avgDuration && <span className="ml-2 text-[0.65rem] text-[#9A9A9A]">{Math.round(t.avgDuration)}ms avg</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error rates */}
          <div className="card lg:col-span-2">
            <div className="px-6 py-4 border-b border-[#eee]">
              <h3 className="text-[0.85rem] font-bold">Error Rates</h3>
            </div>
            <div className="divide-y divide-[#f4f3ef]">
              {(data?.errorRates || []).filter((e: any) => e.failures > 0).map((e: any, i: number) => (
                <div key={i} className="px-6 py-3 flex items-center justify-between">
                  <span className="text-[0.8rem] font-mono font-semibold">{e.toolName}</span>
                  <span className="text-[0.8rem]">
                    <span className="text-[#ef8157] font-semibold">{e.failures}</span>
                    <span className="text-[#9A9A9A]"> / {e.total} ({Math.round((e.failures / e.total) * 100)}%)</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Create alerts page**

Create `portal/src/app/(admin)/admin/alerts/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

interface AlertItem {
  id: number;
  tenantId: string | null;
  severity: string;
  type: string;
  title: string;
  description: string | null;
  isRead: boolean;
  resolvedAt: string | null;
  createdAt: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  info: "bg-[#51cbce]",
  warning: "bg-[#ffa726]",
  critical: "bg-[#ef8157]",
};

export default function AdminAlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [severity, setSeverity] = useState("");
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);

  function loadAlerts() {
    const params = new URLSearchParams();
    if (severity) params.set("severity", severity);
    if (unreadOnly) params.set("unread", "true");

    fetch(`/api/admin/alerts?${params}`)
      .then((r) => r.json())
      .then((d) => { setAlerts(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }

  useEffect(loadAlerts, [severity, unreadOnly]);

  async function bulkAction(action: string) {
    if (selected.size === 0) return;
    await fetch("/api/admin/alerts", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ids: Array.from(selected) }),
    });
    setSelected(new Set());
    loadAlerts();
  }

  return (
    <>
      <Topbar title="Alerts" />
      <div className="p-8">
        {/* Filters + actions */}
        <div className="flex items-center gap-4 mb-6">
          <select value={severity} onChange={(e) => setSeverity(e.target.value)} className="px-3 py-2 border border-[#eee] rounded-lg text-[0.82rem]">
            <option value="">All Severities</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
          <label className="flex items-center gap-2 text-[0.82rem] cursor-pointer">
            <input type="checkbox" checked={unreadOnly} onChange={(e) => setUnreadOnly(e.target.checked)} />
            Unread only
          </label>
          {selected.size > 0 && (
            <div className="ml-auto flex gap-2">
              <button onClick={() => bulkAction("markRead")} className="px-3 py-1.5 bg-[#51cbce] text-white rounded-lg text-[0.75rem] font-semibold">
                Mark Read ({selected.size})
              </button>
              <button onClick={() => bulkAction("resolve")} className="px-3 py-1.5 bg-[#6bd098] text-white rounded-lg text-[0.75rem] font-semibold">
                Resolve ({selected.size})
              </button>
            </div>
          )}
        </div>

        {/* Alert list */}
        <div className="card">
          {loading ? (
            <div className="px-6 py-12 text-center text-[#9A9A9A]">Loading...</div>
          ) : alerts.length === 0 ? (
            <div className="px-6 py-12 text-center text-[#9A9A9A]">No alerts</div>
          ) : (
            <div className="divide-y divide-[#f4f3ef]">
              {alerts.map((a) => (
                <div key={a.id} className={`px-6 py-4 flex items-start gap-4 hover:bg-[#fafaf8] ${!a.isRead ? "bg-[#f8f9ff]" : ""}`}>
                  <input
                    type="checkbox"
                    checked={selected.has(a.id)}
                    onChange={(e) => {
                      const next = new Set(selected);
                      e.target.checked ? next.add(a.id) : next.delete(a.id);
                      setSelected(next);
                    }}
                    className="mt-1"
                  />
                  <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${SEVERITY_COLORS[a.severity] || "bg-[#9A9A9A]"}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-[0.82rem] font-semibold text-[#252422]">{a.title}</span>
                      {!a.isRead && <span className="w-1.5 h-1.5 rounded-full bg-[#51cbce]" />}
                    </div>
                    {a.description && <p className="text-[0.75rem] text-[#9A9A9A] mt-0.5 truncate">{a.description}</p>}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-[0.65rem] uppercase tracking-wider text-[#9A9A9A]">{a.type.replace(/_/g, " ")}</div>
                    <div className="text-[0.7rem] text-[#9A9A9A] mt-0.5">
                      {new Date(a.createdAt).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 3: Create credentials page**

Create `portal/src/app/(admin)/admin/credentials/page.tsx`:

```typescript
"use client";

import { useState, useEffect } from "react";
import { Topbar } from "@/components/topbar";

interface PlatformStatus {
  key: string;
  label: string;
  color: string;
  requiredCreds: string[];
  status: { configured: boolean; keys: Record<string, boolean> };
}

export default function AdminCredentialsPage() {
  const [platforms, setPlatforms] = useState<PlatformStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/admin/credentials")
      .then((r) => r.json())
      .then((d) => { setPlatforms(d.platforms || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const configured = platforms.filter((p) => p.status.configured).length;
  const partial = platforms.filter((p) => !p.status.configured && Object.values(p.status.keys).some(Boolean)).length;

  return (
    <>
      <Topbar title="Platform Credentials" />
      <div className="p-8">
        <div className="flex gap-4 mb-6 text-[0.82rem]">
          <span className="text-[#6bd098] font-semibold">{configured} configured</span>
          <span className="text-[#ffa726] font-semibold">{partial} partial</span>
          <span className="text-[#9A9A9A] font-semibold">{platforms.length - configured - partial} not set</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {platforms.map((p) => (
            <div key={p.key} className="card p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: p.color }} />
                <h3 className="text-[0.85rem] font-bold text-[#252422]">{p.label}</h3>
                <span className={`ml-auto text-[0.65rem] font-semibold px-2 py-0.5 rounded-full ${
                  p.status.configured
                    ? "bg-[#6bd098]/10 text-[#6bd098]"
                    : Object.values(p.status.keys).some(Boolean)
                    ? "bg-[#ffa726]/10 text-[#ffa726]"
                    : "bg-[#eee] text-[#9A9A9A]"
                }`}>
                  {p.status.configured ? "Configured" : Object.values(p.status.keys).some(Boolean) ? "Partial" : "Not Set"}
                </span>
              </div>
              {p.requiredCreds.length > 0 ? (
                <div className="space-y-1">
                  {p.requiredCreds.map((cred) => (
                    <div key={cred} className="flex items-center gap-2 text-[0.72rem]">
                      <div className={`w-1.5 h-1.5 rounded-full ${p.status.keys[cred] ? "bg-[#6bd098]" : "bg-[#ef8157]"}`} />
                      <span className="font-mono text-[#9A9A9A]">{cred}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[0.72rem] text-[#9A9A9A]">No credentials required</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 4: Create config viewer page**

Create `portal/src/app/(admin)/admin/config/page.tsx`:

```typescript
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { Topbar } from "@/components/topbar";
import { readFile } from "fs/promises";
import { join } from "path";

async function readConfigFile(filename: string): Promise<string | null> {
  try {
    const content = await readFile(join(process.cwd(), "..", filename), "utf-8");
    return content;
  } catch {
    return null;
  }
}

function maskSecrets(content: string): string {
  // Mask values that look like secrets (API keys, tokens, passwords)
  return content.replace(
    /^(\s*\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)\w*\s*[=:]\s*).+$/gim,
    "$1••••••••"
  );
}

export default async function AdminConfigPage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.isSuperAdmin) redirect("/dashboard");

  const configs = await Promise.all([
    readConfigFile("portal/package.json").then((c) => ({ name: "package.json", content: c })),
    readConfigFile("pyproject.toml").then((c) => ({ name: "pyproject.toml", content: c })),
  ]);

  return (
    <>
      <Topbar title="Configuration (Read-Only)" />
      <div className="p-8">
        <p className="text-[0.78rem] text-[#9A9A9A] mb-6">
          Server configuration is read-only. To make changes, use deployment pipelines or SSH.
        </p>
        <div className="space-y-6">
          {configs.map((cfg) => (
            <div key={cfg.name} className="card">
              <div className="px-6 py-4 border-b border-[#eee]">
                <h3 className="text-[0.85rem] font-bold font-mono">{cfg.name}</h3>
              </div>
              <pre className="px-6 py-4 text-[0.72rem] font-mono text-[#252422] overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">
                {cfg.content ? maskSecrets(cfg.content) : "File not found"}
              </pre>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 5: Add OAuth abuse detection to usage page**

In `portal/src/app/api/admin/usage/route.ts`, add an OAuth abuse query to the `Promise.all`:

```typescript
    // OAuth change frequency (top abusers)
    db.select({
      tenantId: oauthChangeLog.tenantId,
      tenantName: tenants.name,
      changes: sql<number>`count(*)`,
      rateLimitHits: sql<number>`count(*) filter (where oauth_change_log.created_at >= ${new Date(Date.now() - 10 * 60 * 1000)})`,
    }).from(oauthChangeLog)
      .innerJoin(tenants, eq(oauthChangeLog.tenantId, tenants.id))
      .where(gte(oauthChangeLog.createdAt, new Date(Date.now() - 24 * 60 * 60 * 1000)))
      .groupBy(oauthChangeLog.tenantId, tenants.name)
      .orderBy(sql`count(*) DESC`)
      .limit(10),
```

Add `oauthChangeLog` to the imports in the usage route. Add the result as `oauthAbuse` in the JSON response.

Then in `portal/src/app/(admin)/admin/usage/page.tsx`, add an OAuth Abuse section after the error rates card:

```typescript
          {/* OAuth abuse */}
          {data?.oauthAbuse?.length > 0 && (
            <div className="card lg:col-span-2">
              <div className="px-6 py-4 border-b border-[#eee]">
                <h3 className="text-[0.85rem] font-bold">OAuth Credential Changes (24h)</h3>
              </div>
              <div className="divide-y divide-[#f4f3ef]">
                {data.oauthAbuse.map((a: any, i: number) => (
                  <div key={i} className="px-6 py-3 flex items-center justify-between">
                    <span className="text-[0.8rem] font-semibold">{a.tenantName}</span>
                    <span className="text-[0.8rem]">
                      {a.changes} changes
                      {a.rateLimitHits > 0 && (
                        <span className="ml-2 text-[#ef8157] font-semibold">({a.rateLimitHits} rate limited)</span>
                      )}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
```

- [ ] **Step 6: Commit**

```bash
git add portal/src/app/\(admin\)/admin/usage/ portal/src/app/\(admin\)/admin/alerts/ portal/src/app/\(admin\)/admin/credentials/ portal/src/app/\(admin\)/admin/config/
git commit -m "feat: add admin usage, alerts, credentials, and config pages with OAuth abuse detection"
```

---

## Task 15: Sales Page Login Integration

**Files:**
- Modify: Sales site HTML (location TBD — not in this repo, changes described for reference)
- Modify: `portal/src/app/signup/page.tsx`

- [ ] **Step 1: Document sales site changes**

The sales site at `marketingmcp.statika.net` needs these changes (to be applied separately since it's not in this repo):

1. Add "Login" button to navbar → links to `https://portal.statika.net/`
2. Update pricing "Get Started" buttons:
   - Free → `https://portal.statika.net/signup?plan=free`
   - Starter → `https://portal.statika.net/signup?plan=starter`
   - Pro → `https://portal.statika.net/signup?plan=pro`
   - Enterprise → `https://portal.statika.net/signup?plan=enterprise`
3. Update hero CTA → `https://portal.statika.net/signup?plan=free`

- [ ] **Step 2: Update signup page to read plan parameter**

In `portal/src/app/signup/page.tsx`, modify to read the `?plan=` query parameter and store it in a cookie so the OAuth callback can use it:

At the top of the signup component, add plan reading:

```typescript
// Read plan from URL params
const searchParams = useSearchParams();
const selectedPlan = searchParams.get("plan") || "free";

// Store in cookie for OAuth flow
useEffect(() => {
  if (selectedPlan && selectedPlan !== "free") {
    document.cookie = `selected_plan=${selectedPlan};path=/;max-age=3600`;
  }
}, [selectedPlan]);
```

- [ ] **Step 3: Update auth to create alert on new signup**

In `portal/src/lib/auth.ts`, make two changes:

**3a. Add `isNew` return field to `findOrCreateOAuthUser`.**

In the `if (existing)` branch (line ~30), add `isNew: false` to the return:

```typescript
    return {
      id: existing.id,
      email: existing.email,
      name: existing.name || profile.name || email,
      tenantId: existing.tenantId,
      tenantName: tenant?.name || "Agency",
      role: existing.role,
      planTier: tenant?.planTier || "free",
      isNew: false,
    };
```

In the auto-provision branch (line ~68), add `isNew: true`:

```typescript
  return {
    id: user.id,
    email,
    name: profile.name || email,
    tenantId: tenant.id,
    tenantName: tenant.name,
    role: "owner",
    planTier: tenant.planTier,
    isNew: true,
  };
```

**3b. Add alert import and fire alert in `signIn` callback.**

Add import at the top of the file:

```typescript
import { createAlert } from "./admin";
```

In the `signIn` callback, after the `findOrCreateOAuthUser` call (line ~157-168), add before `return true`:

```typescript
        if (result.isNew) {
          createAlert({
            tenantId: result.tenantId,
            severity: "info",
            type: "new_signup",
            title: `New signup: ${email}`,
            description: `${result.tenantName} (${email}) signed up via ${account?.provider}.`,
          }).catch(() => {}); // fire and forget
        }
```

- [ ] **Step 4: Commit**

```bash
git add portal/src/app/signup/page.tsx portal/src/lib/auth.ts
git commit -m "feat: add plan selection from URL params and new signup alerts"
```

---

## Task 16: Build Verification and Final Commit

- [ ] **Step 1: Run TypeScript build**

```bash
cd portal && npx next build
```

Expected: Build succeeds. Fix any type errors.

- [ ] **Step 2: Run linting**

```bash
cd portal && npx next lint
```

Expected: No errors. Fix any warnings.

- [ ] **Step 3: Test admin routes manually**

Start dev server and verify:
```bash
cd portal && npm run dev
```

Check these routes render:
- `/admin` — overview page
- `/admin/tenants` — tenant list
- `/admin/usage` — usage dashboards
- `/admin/alerts` — alert feed
- `/admin/credentials` — credential status grid

- [ ] **Step 4: Commit any fixes**

```bash
git add -A && git commit -m "fix: resolve build errors and lint warnings"
```

---

## Environment Variables Checklist

Add to `.env` for the portal:

```env
SUPER_ADMIN_EMAIL=your@email.com
CRON_SECRET=<random-secret>
RESEND_API_KEY=<resend-api-key>
TELEGRAM_BOT_TOKEN=<telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
STRIPE_WEBHOOK_SECRET=<stripe-webhook-secret>
```
