import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import GitHubProvider from "next-auth/providers/github";
import bcrypt from "bcryptjs";
import { db } from "./db";
import { users, tenants } from "./schema";
import { eq } from "drizzle-orm";

/**
 * Find or create a user+tenant for OAuth sign-in.
 * On first login, auto-provisions a tenant named after the user's email domain.
 */
async function findOrCreateOAuthUser(profile: { email: string; name?: string }) {
  const email = profile.email.toLowerCase();

  // Check if user exists
  const [existing] = await db
    .select({
      id: users.id,
      email: users.email,
      name: users.name,
      role: users.role,
      tenantId: users.tenantId,
    })
    .from(users)
    .where(eq(users.email, email))
    .limit(1);

  if (existing) {
    const [tenant] = await db
      .select({ name: tenants.name, planTier: tenants.planTier })
      .from(tenants)
      .where(eq(tenants.id, existing.tenantId))
      .limit(1);

    return {
      id: existing.id,
      email: existing.email,
      name: existing.name || profile.name || email,
      tenantId: existing.tenantId,
      tenantName: tenant?.name || "Agency",
      role: existing.role,
      planTier: tenant?.planTier || "free",
    };
  }

  // Auto-provision: create tenant + user
  const domain = email.split("@")[1] || "agency";
  const agencyName = profile.name ? `${profile.name}'s Agency` : domain;
  const slug = domain.replace(/[^a-z0-9]+/g, "-").slice(0, 80) + "-" + Date.now().toString(36);

  const [tenant] = await db
    .insert(tenants)
    .values({ name: agencyName, slug })
    .returning({ id: tenants.id, name: tenants.name, planTier: tenants.planTier });

  const [user] = await db
    .insert(users)
    .values({
      tenantId: tenant.id,
      email,
      name: profile.name || email,
      role: "owner",
    })
    .returning({ id: users.id });

  return {
    id: user.id,
    email,
    name: profile.name || email,
    tenantId: tenant.id,
    tenantName: tenant.name,
    role: "owner",
    planTier: tenant.planTier,
  };
}

export const authOptions: NextAuthOptions = {
  providers: [
    // OAuth providers (agency-friendly)
    ...(process.env.GOOGLE_CLIENT_ID
      ? [
          GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
          }),
        ]
      : []),
    ...(process.env.GITHUB_CLIENT_ID
      ? [
          GitHubProvider({
            clientId: process.env.GITHUB_CLIENT_ID!,
            clientSecret: process.env.GITHUB_CLIENT_SECRET!,
          }),
        ]
      : []),

    // Email/password (superadmin)
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const [user] = await db
          .select({
            id: users.id,
            email: users.email,
            name: users.name,
            passwordHash: users.passwordHash,
            role: users.role,
            tenantId: users.tenantId,
          })
          .from(users)
          .where(eq(users.email, credentials.email.toLowerCase()))
          .limit(1);

        if (!user || !user.passwordHash) return null;

        const valid = await bcrypt.compare(credentials.password, user.passwordHash);
        if (!valid) return null;

        const [tenant] = await db
          .select({ name: tenants.name, planTier: tenants.planTier })
          .from(tenants)
          .where(eq(tenants.id, user.tenantId))
          .limit(1);

        return {
          id: user.id,
          email: user.email,
          name: user.name || user.email,
          tenantId: user.tenantId,
          tenantName: tenant?.name || "Agency",
          role: user.role,
          planTier: tenant?.planTier || "free",
        };
      },
    }),
  ],

  session: { strategy: "jwt", maxAge: 7 * 24 * 60 * 60 }, // 7 days

  pages: { signIn: "/" },

  callbacks: {
    async signIn({ user, account, profile }) {
      // OAuth sign-in: find or create user
      if (account?.provider === "google" || account?.provider === "github") {
        const email = user.email || (profile as any)?.email;
        if (!email) return false;

        const result = await findOrCreateOAuthUser({
          email,
          name: user.name || undefined,
        });

        // Attach tenant data to the user object for the jwt callback
        (user as any).tenantId = result.tenantId;
        (user as any).tenantName = result.tenantName;
        (user as any).role = result.role;
        (user as any).planTier = result.planTier;
        (user as any).id = result.id;
      }
      return true;
    },

    async jwt({ token, user }) {
      if (user) {
        token.userId = (user as any).id || user.id;
        token.tenantId = (user as any).tenantId;
        token.tenantName = (user as any).tenantName;
        token.role = (user as any).role;
        token.planTier = (user as any).planTier;
      }
      return token;
    },

    async session({ session, token }) {
      return {
        ...session,
        userId: token.userId as string,
        tenantId: token.tenantId as string,
        tenantName: token.tenantName as string,
        role: token.role as string,
        planTier: token.planTier as string,
      };
    },
  },
};
