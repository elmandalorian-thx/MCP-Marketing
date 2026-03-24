import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";
import { Topbar } from "@/components/topbar";
import { readFile } from "fs/promises";
import { join } from "path";

async function readConfigFile(filename: string): Promise<string | null> {
  try {
    const content = await readFile(join(process.cwd(), "..", filename), "utf-8");
    return content;
  } catch {
    return null;
  }
}

function maskSecrets(content: string): string {
  // Mask values that look like secrets (API keys, tokens, passwords)
  return content.replace(
    /^(\s*\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)\w*\s*[=:]\s*).+$/gim,
    "$1••••••••"
  );
}

export default async function AdminConfigPage() {
  const session = await getServerSession(authOptions) as any;
  if (!session?.isSuperAdmin) redirect("/dashboard");

  const configs = await Promise.all([
    readConfigFile("portal/package.json").then((c) => ({ name: "package.json", content: c })),
    readConfigFile("pyproject.toml").then((c) => ({ name: "pyproject.toml", content: c })),
  ]);

  return (
    <>
      <Topbar title="Configuration (Read-Only)" />
      <div className="p-8">
        <p className="text-[0.78rem] text-[#9A9A9A] mb-6">
          Server configuration is read-only. To make changes, use deployment pipelines or SSH.
        </p>
        <div className="space-y-6">
          {configs.map((cfg) => (
            <div key={cfg.name} className="card">
              <div className="px-6 py-4 border-b border-[#eee]">
                <h3 className="text-[0.85rem] font-bold font-mono">{cfg.name}</h3>
              </div>
              <pre className="px-6 py-4 text-[0.72rem] font-mono text-[#252422] overflow-x-auto max-h-96 overflow-y-auto whitespace-pre-wrap">
                {cfg.content ? maskSecrets(cfg.content) : "File not found"}
              </pre>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
