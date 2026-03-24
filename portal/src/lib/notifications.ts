import type { Alert } from "./schema";

const SEVERITY_EMOJI: Record<string, string> = {
  info: "ℹ️",
  warning: "⚠️",
  critical: "🚨",
};

/**
 * Send alert notification via email and/or Telegram based on severity.
 * - warning: email only
 * - critical: email + Telegram
 */
export async function sendAlertNotification(alert: Alert): Promise<void> {
  const promises: Promise<void>[] = [];

  if (alert.severity === "warning" || alert.severity === "critical") {
    promises.push(sendEmail(alert));
  }
  if (alert.severity === "critical") {
    promises.push(sendTelegram(alert));
  }

  await Promise.allSettled(promises);
}

async function sendEmail(alert: Alert): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY;
  const toEmail = process.env.SUPER_ADMIN_EMAIL;
  if (!apiKey || !toEmail) return;

  const emoji = SEVERITY_EMOJI[alert.severity] || "";

  try {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: "Marketing MCP <alerts@statika.net>",
        to: [toEmail],
        subject: `${emoji} [${alert.severity.toUpperCase()}] ${alert.title}`,
        text: `${alert.title}\n\n${alert.description || ""}\n\nTime: ${alert.createdAt}\nType: ${alert.type}`,
      }),
    });
  } catch (e) {
    console.error("Failed to send alert email:", e);
  }
}

async function sendTelegram(alert: Alert): Promise<void> {
  const botToken = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!botToken || !chatId) return;

  const emoji = SEVERITY_EMOJI[alert.severity] || "";
  const text = `${emoji} *${alert.severity.toUpperCase()}*: ${alert.title}\n\n${alert.description || ""}\n\nType: \`${alert.type}\``;

  try {
    await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        parse_mode: "Markdown",
      }),
    });
  } catch (e) {
    console.error("Failed to send Telegram alert:", e);
  }
}
