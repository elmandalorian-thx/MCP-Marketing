import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Marketing MCP — Connect Your AI to Every Marketing Platform",
  description:
    "One MCP server. 22 marketing tools. Connect Claude, GPT, Gemini to Google Ads, Meta, GA4, YouTube, and more. Set up in 30 seconds.",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>",
  },
};

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
