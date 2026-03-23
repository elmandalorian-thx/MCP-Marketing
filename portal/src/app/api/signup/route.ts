import { NextRequest, NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { db } from "@/lib/db";
import { tenants, users } from "@/lib/schema";
import { eq } from "drizzle-orm";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { agencyName, name, email, password } = body;

  if (!agencyName || !name || !email || !password) {
    return NextResponse.json({ error: "All fields are required." }, { status: 400 });
  }
  if (password.length < 8) {
    return NextResponse.json({ error: "Password must be at least 8 characters." }, { status: 400 });
  }

  const emailLower = email.toLowerCase().trim();

  // Check if email already exists
  const [existing] = await db
    .select({ id: users.id })
    .from(users)
    .where(eq(users.email, emailLower))
    .limit(1);

  if (existing) {
    return NextResponse.json({ error: "An account with this email already exists." }, { status: 409 });
  }

  // Create slug from agency name
  const slug = agencyName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 100);

  // Check slug uniqueness
  const [existingTenant] = await db
    .select({ id: tenants.id })
    .from(tenants)
    .where(eq(tenants.slug, slug))
    .limit(1);

  const finalSlug = existingTenant ? `${slug}-${Date.now().toString(36)}` : slug;

  // Create tenant
  const [tenant] = await db
    .insert(tenants)
    .values({ name: agencyName.trim(), slug: finalSlug })
    .returning({ id: tenants.id });

  // Hash password and create user
  const passwordHash = await bcrypt.hash(password, 12);

  const [user] = await db
    .insert(users)
    .values({
      tenantId: tenant.id,
      email: emailLower,
      name: name.trim(),
      passwordHash,
      role: "owner",
    })
    .returning({ id: users.id, email: users.email });

  return NextResponse.json({ success: true, userId: user.id, email: user.email });
}
