"use client";

import { PLAN_LIMITS } from "@/lib/utils";

export default function SettingsPage() {
  // TODO: Replace with actual tenant data from session
  const currentPlan = "free";

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">
          Manage your account, team, and billing.
        </p>
      </div>

      {/* Current plan */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="font-semibold mb-4">Current Plan</h2>
        <div className="flex items-center gap-4 mb-4">
          <span className="text-3xl font-bold capitalize">{currentPlan}</span>
          <span className="text-sm text-gray-400">
            {PLAN_LIMITS[currentPlan as keyof typeof PLAN_LIMITS]?.price}/mo
          </span>
        </div>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500 text-xs">Seats</div>
            <div className="font-semibold">
              {PLAN_LIMITS[currentPlan as keyof typeof PLAN_LIMITS]?.seats}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500 text-xs">Connections</div>
            <div className="font-semibold">
              {PLAN_LIMITS[currentPlan as keyof typeof PLAN_LIMITS]?.connections}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-gray-500 text-xs">Monthly Calls</div>
            <div className="font-semibold">
              {PLAN_LIMITS[currentPlan as keyof typeof PLAN_LIMITS]?.monthlyCalls.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Upgrade */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="font-semibold mb-4">Upgrade Plan</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(["starter", "pro", "enterprise"] as const).map((plan) => {
            const limits = PLAN_LIMITS[plan];
            const isPopular = plan === "pro";

            return (
              <div
                key={plan}
                className={`rounded-xl border p-5 relative ${
                  isPopular
                    ? "border-purple-300 shadow-lg shadow-purple-50"
                    : "border-gray-200"
                }`}
              >
                {isPopular && (
                  <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white text-xs font-bold px-3 py-0.5 rounded-full">
                    Popular
                  </span>
                )}
                <div className="font-semibold capitalize mb-1">{plan}</div>
                <div className="text-2xl font-bold mb-3">{limits.price}<span className="text-sm text-gray-400 font-normal">/mo</span></div>
                <ul className="text-sm text-gray-600 space-y-1.5 mb-4">
                  <li>Up to {limits.seats} seats</li>
                  <li>Up to {limits.connections} connections</li>
                  <li>{limits.monthlyCalls.toLocaleString()} calls/mo</li>
                </ul>
                <button
                  className={`w-full py-2 rounded-lg text-sm font-semibold transition-all ${
                    isPopular
                      ? "bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white hover:opacity-90"
                      : "border border-gray-200 text-gray-700 hover:border-purple-300"
                  }`}
                >
                  {plan === "enterprise" ? "Contact Sales" : "Upgrade"}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Team members */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm mb-6">
        <h2 className="font-semibold mb-4">Team Members</h2>
        <p className="text-sm text-gray-400">
          Team member management coming soon. Upgrade to Starter or above for multi-seat access.
        </p>
      </div>

      {/* Danger zone */}
      <div className="bg-white rounded-xl border border-red-200 p-6">
        <h2 className="font-semibold text-red-700 mb-2">Danger Zone</h2>
        <p className="text-sm text-gray-500 mb-4">
          Permanently delete your account and all associated data.
        </p>
        <button className="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors">
          Delete Account
        </button>
      </div>
    </div>
  );
}
