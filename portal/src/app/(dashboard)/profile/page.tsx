"use client";

import { useSession } from "next-auth/react";
import { useState } from "react";
import { Topbar } from "@/components/topbar";
import { PLAN_LIMITS } from "@/lib/utils";

export default function ProfilePage() {
  const { data: session } = useSession();
  const [name, setName] = useState(session?.user?.name || "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const plan = (session as any)?.planTier || "free";
  const limits = PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS];

  async function updateProfile() {
    setSaving(true); setMsg(null);
    try {
      const body: any = { name };
      if (currentPassword && newPassword) {
        body.currentPassword = currentPassword;
        body.newPassword = newPassword;
      }
      const res = await fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (res.ok) {
        setMsg({ type: "success", text: "Profile updated successfully." });
        setCurrentPassword(""); setNewPassword("");
      } else {
        setMsg({ type: "error", text: data.error || "Update failed." });
      }
    } catch { setMsg({ type: "error", text: "Network error." }); }
    setSaving(false);
  }

  return (
    <>
      <Topbar title="Settings" />
      <div className="p-8 max-w-3xl">
        {msg && (
          <div className={`mb-6 px-4 py-3 rounded-xl text-[0.8rem] font-medium animate-in ${
            msg.type === "success" ? "bg-[#6bd098]/10 border border-[#6bd098]/20 text-[#4caf50]" : "bg-[#ef8157]/8 border border-[#ef8157]/20 text-[#ef8157]"
          }`}>{msg.text}</div>
        )}

        {/* Account info */}
        <div className="card p-6 mb-6">
          <h3 className="text-[0.9rem] font-bold mb-5">Account Information</h3>
          <div className="space-y-4">
            <div>
              <label className="input-label">Full Name</label>
              <input type="text" className="input" value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div>
              <label className="input-label">Email</label>
              <input type="email" className="input bg-[#f4f3ef] cursor-not-allowed" value={session?.user?.email || ""} disabled />
              <p className="text-[0.68rem] text-[#9A9A9A] mt-1">Contact support to change your email.</p>
            </div>
          </div>
        </div>

        {/* Change password */}
        <div className="card p-6 mb-6">
          <h3 className="text-[0.9rem] font-bold mb-5">Change Password</h3>
          <div className="space-y-4">
            <div>
              <label className="input-label">Current Password</label>
              <input type="password" className="input" placeholder="Enter current password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} />
            </div>
            <div>
              <label className="input-label">New Password</label>
              <input type="password" className="input" placeholder="Min. 8 characters" value={newPassword} onChange={e => setNewPassword(e.target.value)} minLength={8} />
            </div>
          </div>
          <button onClick={updateProfile} disabled={saving} className="btn btn-primary mt-5 disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>

        {/* Plan */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-[0.9rem] font-bold">Current Plan</h3>
            <span className="badge badge-info text-[0.72rem] capitalize">{plan}</span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#f4f3ef] rounded-xl p-4 text-center">
              <div className="text-[0.68rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Seats</div>
              <div className="text-lg font-bold">{limits?.seats}</div>
            </div>
            <div className="bg-[#f4f3ef] rounded-xl p-4 text-center">
              <div className="text-[0.68rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Connections</div>
              <div className="text-lg font-bold">{limits?.connections}</div>
            </div>
            <div className="bg-[#f4f3ef] rounded-xl p-4 text-center">
              <div className="text-[0.68rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">Calls/mo</div>
              <div className="text-lg font-bold">{limits?.monthlyCalls.toLocaleString()}</div>
            </div>
          </div>
          {plan !== "enterprise" && (
            <a href="https://marketingmcp.statika.net/#pricing" target="_blank" rel="noopener noreferrer" className="btn btn-outline mt-4 w-full no-underline">
              Upgrade Plan
            </a>
          )}
        </div>

        {/* Danger zone */}
        <div className="card p-6 border-[#ef8157]/20">
          <h3 className="text-[0.9rem] font-bold text-[#ef8157] mb-2">Danger Zone</h3>
          <p className="text-[0.8rem] text-[#9A9A9A] mb-4">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
          <button className="btn btn-danger btn-sm">
            Delete Account
          </button>
        </div>
      </div>
    </>
  );
}
