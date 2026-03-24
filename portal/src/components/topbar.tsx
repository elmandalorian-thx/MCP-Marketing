"use client";

import { signOut, useSession } from "next-auth/react";
import { useState, useRef, useEffect } from "react";

export function Topbar({ title }: { title: string }) {
  const { data: session } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const initials = session?.user?.name
    ? session.user.name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "?";

  return (
    <header className="h-16 bg-white/80 backdrop-blur-sm border-b border-[#eee] px-8 flex items-center justify-between sticky top-0 z-20">
      <h1 className="text-[1.1rem] font-bold text-[#252422]">{title}</h1>

      <div className="flex items-center gap-4">
        {/* Notifications placeholder */}
        <button className="relative p-2 rounded-lg text-[#9A9A9A] hover:text-[#252422] hover:bg-[#f4f3ef] transition-all">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
          </svg>
        </button>

        {/* User menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center gap-3 px-3 py-1.5 rounded-xl hover:bg-[#f4f3ef] transition-all"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#51cbce] to-[#6bd098] flex items-center justify-center text-white text-[0.7rem] font-bold">
              {initials}
            </div>
            <div className="text-left hidden sm:block">
              <div className="text-[0.78rem] font-semibold text-[#252422] leading-tight">
                {session?.user?.name || "User"}
              </div>
              <div className="text-[0.65rem] text-[#9A9A9A]">
                {(session as any)?.tenantName || "Agency"}
              </div>
            </div>
            <svg className={`w-4 h-4 text-[#9A9A9A] transition-transform ${menuOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-full mt-2 w-52 bg-white rounded-xl shadow-lg border border-[#eee] py-2 animate-in">
              <a href="/dashboard/profile" className="flex items-center gap-3 px-4 py-2.5 text-[0.8rem] text-[#252422] no-underline hover:bg-[#f4f3ef] transition-colors">
                <svg className="w-4 h-4 text-[#9A9A9A]" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                My Profile
              </a>
              <a href="/dashboard/keys" className="flex items-center gap-3 px-4 py-2.5 text-[0.8rem] text-[#252422] no-underline hover:bg-[#f4f3ef] transition-colors">
                <svg className="w-4 h-4 text-[#9A9A9A]" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
                API Keys
              </a>
              <div className="my-1 border-t border-[#eee]" />
              <button
                onClick={() => signOut({ callbackUrl: "/login" })}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-[0.8rem] text-[#ef8157] hover:bg-red-50 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
