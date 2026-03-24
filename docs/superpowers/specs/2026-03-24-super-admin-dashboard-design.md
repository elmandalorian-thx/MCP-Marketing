# Super Admin Dashboard & Sales-Portal Integration

> Design spec for owner-level admin dashboard, usage monitoring, OAuth abuse prevention, alert system, and sales page login integration.

## Overview

Add a super admin section to the existing Next.js portal (`portal.statika.net`) that gives the app owner full visibility and control over all tenants, usage, credentials, and system health. Simultaneously integrate the sales site (`marketingmcp.statika.net`) with the portal's auth flow.

**Approach:** Monolithic — all new functionality lives inside the existing portal codebase as role-gated routes. No separate apps or deployments.

---

## 1. Access Control & Role Model

### Super Admin Identification
- Single env var: `SUPER_ADMIN_EMAIL=<owner-email>`
- NextAuth `session` callback checks `user.email === process.env.SUPER_ADMIN_EMAIL` and sets `isSuperAdmin: true` on the JWT/session
- No DB column — env-driven, tamper-proof from the app layer

### Route Protection
- All `/admin/*` portal routes gated by middleware checking `session.isSuperAdmin`
- Regular users hitting `/admin/*` → redirect to `/dashboard`
- API routes under `/api/admin/*` → 403 if not super admin

### Regular Subscriber Access (unchanged)
- Login via Google/GitHub OAuth
- See only their own tenant: `/dashboard`, `/keys`, `/connect`, `/usage`, `/profile`, `/clients`
- Connect platforms via OAuth only — no raw credential access

---

## 2. Super Admin Pages

### `/admin` — Overview
- KPIs: total tenants, total users, total API calls (today / this month)
- Active vs inactive tenants (last 30 days)
- Revenue by plan tier (count of free/starter/pro/enterprise)
- Recent signups (last 7 days)
- System health: MCP server status, DB connection, uptime

### `/admin/tenants` — Tenant Management
- Searchable/filterable table: tenant name, plan, users count, connections count, monthly usage, created date
- Click-through to tenant detail: their users, API keys, connected platforms, usage history
- Actions: change plan tier, suspend/unsuspend, delete tenant

### `/admin/usage` — Usage Dashboards
- Daily trend chart (calls per day, last 30 days)
- Hourly heatmap (calls per hour, last 7 days — for abuse detection)
- Top tenants by usage (leaderboard)
- Top tools by call volume
- Failed calls breakdown (error rates by tool/tenant)

### `/admin/alerts` — Alerts & Notifications
- Chronological alert feed with severity badges (info/warning/critical)
- Filters by severity and type
- Each alert: timestamp, tenant, description, severity
- Actions: mark as read, resolve, bulk mark as read
- Unread count badge in admin nav

### `/admin/credentials` — Platform Credentials Manager
- Grid of 14+ platforms (migrated from old Python Starlette admin)
- Add/update raw API keys, service account JSON, dev tokens
- Test connection button per platform
- Status badges: configured / partial / not configured

### `/admin/config` — Config Editor
- Edit `.env`, `clients.json`, `pyproject.toml` (whitelist only)
- Syntax-highlighted textarea
- Save with validation

---

## 3. OAuth Abuse Prevention

### Problem
Users swapping OAuth credentials frequently to share one subscription across multiple clients.

### OAuth Change Log — New Table
```
oauth_change_log
├── id (BIGSERIAL PK)
├── tenant_id (FK → tenants, CASCADE)
├── user_id (FK → users, CASCADE)
├── platform (varchar)
├── action (varchar: connected | disconnected | updated)
├── ip_address (varchar)
├── created_at (timestamp, indexed)
```

### Rate Limiting Logic
- On every OAuth connect/disconnect/update, log to `oauth_change_log`
- Before allowing a change, count changes for `(tenant_id, platform)` in the last 10 minutes
- If count >= 2: **hard block** — return error with cooldown timer ("You can change this connection again in X minutes")
- No alert sent — just a block with user-facing message

### Detection Queries (admin dashboard)
- "Tenants with most OAuth changes in last 24h" — surfaces potential abusers
- "Tenants that hit the rate limit" — flagged in alerts page
- Pattern detection: same platform disconnected/reconnected repeatedly across days

### Implementation
- Rate check in existing `/api/connections` POST and DELETE routes
- Simple SQL count query — no background worker needed
- Cooldown timer calculated from most recent change timestamp

---

## 4. Alert System

### Alert Triggers

| Trigger | Severity | Description |
|---------|----------|-------------|
| OAuth rate limit hit | warning | Tenant tried to swap credentials beyond 2/10min |
| Usage spike | warning | Tenant exceeds 200% of their hourly average |
| Failed auth burst | critical | 10+ failed API key attempts from same IP in 5 min |
| Plan limit approaching | info | Tenant at 80% of monthly call limit |
| Plan limit reached | warning | Tenant hit monthly call limit |
| New tenant signup | info | New tenant auto-provisioned via OAuth |

### Alerts Table — New Table
```
alerts
├── id (BIGSERIAL PK)
├── tenant_id (FK → tenants, CASCADE, nullable)
├── severity (varchar: info | warning | critical)
├── type (varchar: oauth_rate_limit | usage_spike | auth_failure | plan_limit_approaching | plan_limit_reached | new_signup)
├── title (varchar)
├── description (text)
├── is_read (boolean, default false)
├── resolved_at (timestamp, nullable)
├── created_at (timestamp, indexed)
```

### Notification Delivery
On alert creation, check severity:
- `info` — dashboard only
- `warning` — dashboard + email
- `critical` — dashboard + email + Telegram

**Email:** Transactional email service (Resend, SES, or SMTP)
**Telegram:** Existing Telegram MCP integration

### Alert Processing

**Inline (synchronous, during requests):**
- OAuth rate limit hits → alert created in `/api/connections` route
- Failed auth bursts → alert created in tenant auth middleware
- New signups → alert created in NextAuth provisioning callback

**Hourly cron** — Next.js API route `/api/admin/cron/check-alerts`:
- Protected by `CRON_SECRET` env var (Bearer auth)
- Triggered by external cron (system crontab, GitHub Actions, or `curl`)
- Checks:
  1. Usage spikes: compare current hour vs 7-day hourly average, alert if > 200%
  2. Plan limit approaching: tenants at >= 80% monthly limit (deduplicated)
  3. Plan limit reached: tenants at 100%

---

## 5. Sales Page → Portal Login Integration

### Current State
Sales site at `marketingmcp.statika.net` — no login/signup flow. "Get Started" buttons link to `#setup`.

### Sales Site Changes

1. **Add "Login" button** to navbar (top right) → redirects to `portal.statika.net/login`
2. **Update pricing CTAs:**
   - Free → `portal.statika.net/signup?plan=free`
   - Starter → `portal.statika.net/signup?plan=starter`
   - Pro → `portal.statika.net/signup?plan=pro`
   - Enterprise → `portal.statika.net/signup?plan=enterprise`
3. **Update hero CTA** ("Get Started Free") → `portal.statika.net/signup?plan=free`

### Portal Changes

1. **`/login` page** — unchanged, accepts redirects from sales site
2. **`/signup` page** — reads `?plan=` query param:
   - Stores selected plan in session/cookie during OAuth flow
   - After account creation, sets `tenant.plan_tier` to selected plan (default: `free`)
   - For paid plans: redirect to Stripe checkout after signup before activating plan
3. **Post-login redirect** → `portal.statika.net/dashboard`

No cross-origin complexity — sales site just links out, portal handles everything.

---

## 6. Database Changes Summary

### New Tables
- `oauth_change_log` — tracks all OAuth credential changes per tenant/platform
- `alerts` — stores triggered alerts with severity, type, read/resolved state

### New Indexes
- `oauth_change_log(tenant_id, platform, created_at)` — rate limit count query
- `alerts(is_read, created_at)` — unread alert feed
- `alerts(tenant_id, created_at)` — tenant-specific alert history

### No Changes to Existing Tables
Super admin role is env-driven (`SUPER_ADMIN_EMAIL`), not a DB column.

---

## 7. New Environment Variables

| Variable | Purpose |
|----------|---------|
| `SUPER_ADMIN_EMAIL` | Email address of the super admin account |
| `CRON_SECRET` | Bearer token protecting the hourly alert cron endpoint |
| `SMTP_*` or `RESEND_API_KEY` | Email delivery for alert notifications |

---

## 8. What Gets Retired

The old Python/Starlette admin dashboard (`src/marketing_mcp/admin/`) becomes redundant once the super admin credential manager is built. It can be deprecated and eventually removed.
