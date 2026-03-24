import { getToken } from "next-auth/jwt";
import { NextRequest, NextResponse } from "next/server";

const protectedRoutes = ["/dashboard"];
const adminRoutes = ["/admin"];
const authRoutes = ["/login", "/signup"];

export async function middleware(request: NextRequest) {
  const token = await getToken({ req: request });
  const { pathname } = request.nextUrl;

  // Protect admin routes — super admin only
  if (adminRoutes.some((r) => pathname.startsWith(r))) {
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
    if (!token.isSuperAdmin) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  // Protect dashboard routes
  if (protectedRoutes.some((r) => pathname.startsWith(r))) {
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
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
    "/login", "/signup",
    "/dashboard/:path*",
    "/admin/:path*",
  ],
};
