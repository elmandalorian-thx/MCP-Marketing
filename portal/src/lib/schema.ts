import {
  pgTable,
  uuid,
  varchar,
  integer,
  boolean,
  timestamp,
  text,
  bigserial,
  customType,
} from "drizzle-orm/pg-core";

// Custom bytea type for encrypted credentials
const bytea = customType<{ data: Buffer }>({
  dataType() {
    return "bytea";
  },
});

// ── Tenants ──────────────────────────────────────────────────────────

export const tenants = pgTable("tenants", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: varchar("name", { length: 255 }).notNull(),
  slug: varchar("slug", { length: 100 }).notNull().unique(),
  planTier: varchar("plan_tier", { length: 20 }).notNull().default("free"),
  stripeCustomerId: varchar("stripe_customer_id", { length: 255 }),
  stripeSubscriptionId: varchar("stripe_subscription_id", { length: 255 }),
  maxConnections: integer("max_connections").notNull().default(3),
  maxMonthlyCalls: integer("max_monthly_calls").notNull().default(500),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
  isSuspended: boolean("is_suspended").notNull().default(false),
});

// ── Users ────────────────────────────────────────────────────────────

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  tenantId: uuid("tenant_id")
    .notNull()
    .references(() => tenants.id, { onDelete: "cascade" }),
  email: varchar("email", { length: 255 }).notNull(),
  name: varchar("name", { length: 255 }),
  passwordHash: varchar("password_hash", { length: 255 }),
  role: varchar("role", { length: 20 }).notNull().default("member"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

// ── API Keys ─────────────────────────────────────────────────────────

export const apiKeys = pgTable("api_keys", {
  id: uuid("id").primaryKey().defaultRandom(),
  tenantId: uuid("tenant_id")
    .notNull()
    .references(() => tenants.id, { onDelete: "cascade" }),
  keyHash: varchar("key_hash", { length: 64 }).notNull().unique(),
  keyPrefix: varchar("key_prefix", { length: 12 }).notNull(),
  label: varchar("label", { length: 100 }),
  isActive: boolean("is_active").notNull().default(true),
  lastUsedAt: timestamp("last_used_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

// ── Platform Connections ─────────────────────────────────────────────

export const platformConnections = pgTable("platform_connections", {
  id: uuid("id").primaryKey().defaultRandom(),
  tenantId: uuid("tenant_id")
    .notNull()
    .references(() => tenants.id, { onDelete: "cascade" }),
  platform: varchar("platform", { length: 50 }).notNull(),
  credentialsEncrypted: bytea("credentials_encrypted").notNull(),
  credentialsNonce: bytea("credentials_nonce").notNull(),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
});

// ── Usage Logs ───────────────────────────────────────────────────────

export const usageLogs = pgTable("usage_logs", {
  id: bigserial("id", { mode: "number" }).primaryKey(),
  tenantId: uuid("tenant_id")
    .notNull()
    .references(() => tenants.id),
  apiKeyId: uuid("api_key_id").references(() => apiKeys.id),
  toolName: varchar("tool_name", { length: 100 }).notNull(),
  durationMs: integer("duration_ms"),
  success: boolean("success").notNull().default(true),
  errorMessage: text("error_message"),
  ipAddress: varchar("ip_address", { length: 45 }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

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

// ── Type exports ─────────────────────────────────────────────────────

export type Tenant = typeof tenants.$inferSelect;
export type NewTenant = typeof tenants.$inferInsert;
export type ApiKey = typeof apiKeys.$inferSelect;
export type PlatformConnection = typeof platformConnections.$inferSelect;
export type UsageLog = typeof usageLogs.$inferSelect;
export type OauthChangeLog = typeof oauthChangeLog.$inferSelect;
export type Alert = typeof alerts.$inferSelect;
export type NewAlert = typeof alerts.$inferInsert;
