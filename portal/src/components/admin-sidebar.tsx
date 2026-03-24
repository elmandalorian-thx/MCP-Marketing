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
