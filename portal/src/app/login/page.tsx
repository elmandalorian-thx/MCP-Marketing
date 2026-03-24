"use client";

import { signIn, getProviders } from "next-auth/react";
import Link from "next/link";
import { useState, useEffect } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<string | null>(null);
  const [hasGoogle, setHasGoogle] = useState(false);
  const [hasGithub, setHasGithub] = useState(false);

  useEffect(() => {
    getProviders().then((providers) => {
      if (providers?.google) setHasGoogle(true);
      if (providers?.github) setHasGithub(true);
    });
  }, []);

  async function handleOAuth(provider: string) {
    setOauthLoading(provider);
    await signIn(provider, { callbackUrl: "/dashboard" });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const result = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    if (result?.error) {
      setError("Invalid email or password.");
      setLoading(false);
    } else {
      window.location.href = "/dashboard";
    }
  }

  const hasOAuth = hasGoogle || hasGithub;

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f4f3ef 0%, #e8e6df 100%)" }}>
      <div className="w-full max-w-[420px] mx-4 animate-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#51cbce] to-[#6bd098] flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4 shadow-lg">
            M
          </div>
          <h1 className="text-xl font-bold text-[#252422]">Marketing MCP</h1>
          <p className="text-[0.82rem] text-[#9A9A9A] mt-1">Sign in to your portal</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-lg bg-[#ef8157]/8 border border-[#ef8157]/20 text-[0.8rem] text-[#ef8157] font-medium">
              {error}
            </div>
          )}

          {/* OAuth buttons */}
          {hasOAuth && (
            <>
              <div className="space-y-3 mb-6">
                {hasGoogle && (
                  <button
                    onClick={() => handleOAuth("google")}
                    disabled={!!oauthLoading}
                    className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl border border-[#ddd] bg-white text-[0.85rem] font-semibold text-[#252422] hover:bg-[#f4f3ef] hover:border-[#ccc] transition-all disabled:opacity-50"
                  >
                    {oauthLoading === "google" ? (
                      <svg className="animate-spin h-5 w-5 text-[#9A9A9A]" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    ) : (
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                      </svg>
                    )}
                    Continue with Google
                  </button>
                )}
                {hasGithub && (
                  <button
                    onClick={() => handleOAuth("github")}
                    disabled={!!oauthLoading}
                    className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl bg-[#24292e] text-white text-[0.85rem] font-semibold hover:bg-[#1a1e22] transition-all disabled:opacity-50"
                  >
                    {oauthLoading === "github" ? (
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    ) : (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                    )}
                    Continue with GitHub
                  </button>
                )}
              </div>

              {/* Divider */}
              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-px bg-[#eee]" />
                <span className="text-[0.72rem] font-semibold text-[#c0c0c0] uppercase tracking-wider">or sign in with email</span>
                <div className="flex-1 h-px bg-[#eee]" />
              </div>
            </>
          )}

          {/* Email/password form */}
          <form onSubmit={handleSubmit}>
            <div className="mb-5">
              <label className="input-label">Email Address</label>
              <input
                type="email"
                className="input"
                placeholder="you@agency.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="mb-6">
              <label className="input-label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary btn-lg w-full disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  Signing in...
                </span>
              ) : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-[0.8rem] text-[#9A9A9A]">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-[#51cbce] font-semibold hover:underline no-underline">
                Create one
              </Link>
            </span>
          </div>

          {hasOAuth && (
            <p className="mt-3 text-center text-[0.7rem] text-[#c0c0c0]">
              Sign in with Google or GitHub to auto-create your account
            </p>
          )}
        </div>

        {/* Security badge */}
        <div className="mt-6 text-center">
          <div className="inline-flex items-center gap-1.5 text-[0.68rem] text-[#c0c0c0]">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            AES-256 encrypted &middot; SOC 2 ready
          </div>
        </div>
      </div>
    </div>
  );
}
