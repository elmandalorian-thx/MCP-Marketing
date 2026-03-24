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
