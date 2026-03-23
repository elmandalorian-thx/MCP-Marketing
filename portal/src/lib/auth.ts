import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";
import { db } from "./db";
import { users, tenants } from "./schema";
import { eq, and } from "drizzle-orm";

export const authOptions: NextAuthOptions = {
  providers: [
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

        // Get tenant info
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
  session: { strategy: "jwt", maxAge: 24 * 60 * 60 },
  pages: { signIn: "/" },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.userId = user.id;
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
