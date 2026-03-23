import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { db } from "@/lib/db";
import { users } from "@/lib/schema";
import { eq } from "drizzle-orm";
import bcrypt from "bcryptjs";

export async function PUT(request: NextRequest) {
  const session = await getServerSession(authOptions) as any;
  if (!session?.userId) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const { name, currentPassword, newPassword } = body;

  // Update name
  if (name) {
    await db.update(users).set({ name }).where(eq(users.id, session.userId));
  }

  // Change password
  if (currentPassword && newPassword) {
    if (newPassword.length < 8) {
      return NextResponse.json({ error: "New password must be at least 8 characters." }, { status: 400 });
    }

    const [user] = await db.select({ passwordHash: users.passwordHash })
      .from(users).where(eq(users.id, session.userId)).limit(1);

    if (!user?.passwordHash) {
      return NextResponse.json({ error: "Password not set." }, { status: 400 });
    }

    const valid = await bcrypt.compare(currentPassword, user.passwordHash);
    if (!valid) {
      return NextResponse.json({ error: "Current password is incorrect." }, { status: 400 });
    }

    const hash = await bcrypt.hash(newPassword, 12);
    await db.update(users).set({ passwordHash: hash }).where(eq(users.id, session.userId));
  }

  return NextResponse.json({ success: true });
}
