"use client";

import { signIn } from "next-auth/react";
import Link from "next/link";
import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

export default function SignupPage() {
  return (
    <Suspense>
      <SignupForm />
    </Suspense>
  );
}

function SignupForm() {
  const searchParams = useSearchParams();
  const selectedPlan = searchParams.get("plan") || "free";
  const [form, setForm] = useState({ agencyName: "", name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Store selected plan in cookie for OAuth flow
  useEffect(() => {
    if (selectedPlan && selectedPlan !== "free") {
      document.cookie = `selected_plan=${selectedPlan};path=/;max-age=3600`;
    }
  }, [selectedPlan]);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Something went wrong.");
        setLoading(false);
        return;
      }

      // Auto-login after signup
      const result = await signIn("credentials", {
        email: form.email,
        password: form.password,
        redirect: false,
      });

      if (result?.error) {
        setError("Account created but login failed. Try signing in manually.");
        setLoading(false);
      } else {
        window.location.href = "/dashboard";
      }
    } catch {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: "linear-gradient(135deg, #f4f3ef 0%, #e8e6df 100%)" }}>
      <div className="w-full max-w-[420px] mx-4 animate-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#51cbce] to-[#6bd098] flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4 shadow-lg">
            M
          </div>
          <h1 className="text-xl font-bold text-[#252422]">Create your account</h1>
          <p className="text-[0.82rem] text-[#9A9A9A] mt-1">Start connecting your marketing platforms</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-lg bg-[#ef8157]/8 border border-[#ef8157]/20 text-[0.8rem] text-[#ef8157] font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="input-label">Agency / Company Name</label>
              <input
                type="text"
                className="input"
                placeholder="Acme Marketing"
                value={form.agencyName}
                onChange={(e) => update("agencyName", e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="mb-4">
              <label className="input-label">Full Name</label>
              <input
                type="text"
                className="input"
                placeholder="Jane Smith"
                value={form.name}
                onChange={(e) => update("name", e.target.value)}
                required
              />
            </div>

            <div className="mb-4">
              <label className="input-label">Email Address</label>
              <input
                type="email"
                className="input"
                placeholder="jane@acme.com"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
                required
              />
            </div>

            <div className="mb-6">
              <label className="input-label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="Min. 8 characters"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                required
                minLength={8}
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
                  Creating account...
                </span>
              ) : "Create Account"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-[0.8rem] text-[#9A9A9A]">
              Already have an account?{" "}
              <Link href="/" className="text-[#51cbce] font-semibold hover:underline no-underline">
                Sign in
              </Link>
            </span>
          </div>
        </div>

        <div className="mt-6 text-center">
          <div className="inline-flex items-center gap-1.5 text-[0.68rem] text-[#c0c0c0]">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
            </svg>
            Free plan &middot; No credit card required
          </div>
        </div>
      </div>
    </div>
  );
}
