import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xl mx-auto mb-4">
            M
          </div>
          <h1 className="text-2xl font-bold mb-2">Marketing MCP Portal</h1>
          <p className="text-gray-500 mb-8">
            Manage your platform connections, API keys, and usage.
          </p>

          <div className="space-y-3">
            <Link
              href="/dashboard"
              className="block w-full py-3 px-4 rounded-lg bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white font-semibold hover:opacity-90 transition-opacity"
            >
              Go to Dashboard
            </Link>
            <Link
              href="/api-keys"
              className="block w-full py-3 px-4 rounded-lg border border-gray-200 text-gray-700 font-semibold hover:border-purple-300 hover:shadow-sm transition-all"
            >
              Manage API Keys
            </Link>
          </div>

          <p className="mt-6 text-xs text-gray-400">
            Don&apos;t have an account?{" "}
            <a href="mailto:hello@statika.net" className="text-purple-500 hover:underline">
              Contact us
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
