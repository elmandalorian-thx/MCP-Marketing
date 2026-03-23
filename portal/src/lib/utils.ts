import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const PLATFORMS: Record<
  string,
  { label: string; color: string; requiredCreds: string[] }
> = {
  google_ads: {
    label: "Google Ads",
    color: "#4285f4",
    requiredCreds: [
      "GOOGLE_ADS_CLIENT_ID",
      "GOOGLE_ADS_CLIENT_SECRET",
      "GOOGLE_ADS_REFRESH_TOKEN",
      "GOOGLE_ADS_DEVELOPER_TOKEN",
      "GOOGLE_ADS_CUSTOMER_ID",
    ],
  },
  search_console: {
    label: "Search Console",
    color: "#4285f4",
    requiredCreds: ["GOOGLE_SERVICE_ACCOUNT_JSON"],
  },
  ga4: {
    label: "GA4 Analytics",
    color: "#f9ab00",
    requiredCreds: ["GOOGLE_SERVICE_ACCOUNT_JSON"],
  },
  meta: {
    label: "Meta / Facebook",
    color: "#1877f2",
    requiredCreds: ["META_ACCESS_TOKEN"],
  },
  youtube: {
    label: "YouTube",
    color: "#ff0000",
    requiredCreds: ["YOUTUBE_API_KEY"],
  },
  reddit: {
    label: "Reddit",
    color: "#ff4500",
    requiredCreds: ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"],
  },
  semrush: {
    label: "SEMrush",
    color: "#ff6c2c",
    requiredCreds: ["SEMRUSH_API_KEY"],
  },
  linkedin: {
    label: "LinkedIn",
    color: "#0a66c2",
    requiredCreds: ["LINKEDIN_ACCESS_TOKEN"],
  },
  mailchimp: {
    label: "Mailchimp",
    color: "#ffe01b",
    requiredCreds: ["MAILCHIMP_API_KEY"],
  },
  tiktok: {
    label: "TikTok",
    color: "#00f2ea",
    requiredCreds: ["TIKTOK_ACCESS_TOKEN"],
  },
  pinterest: {
    label: "Pinterest",
    color: "#e60023",
    requiredCreds: ["PINTEREST_ACCESS_TOKEN"],
  },
  x_twitter: {
    label: "X / Twitter",
    color: "#1da1f2",
    requiredCreds: ["X_BEARER_TOKEN"],
  },
  shopify: {
    label: "Shopify",
    color: "#96bf48",
    requiredCreds: ["SHOPIFY_STORE_URL", "SHOPIFY_ACCESS_TOKEN"],
  },
  yelp: {
    label: "Yelp",
    color: "#af0606",
    requiredCreds: ["YELP_API_KEY"],
  },
  hubspot: {
    label: "HubSpot",
    color: "#ff7a59",
    requiredCreds: ["HUBSPOT_ACCESS_TOKEN"],
  },
  bing_webmaster: {
    label: "Bing Webmaster",
    color: "#008373",
    requiredCreds: ["BING_WEBMASTER_API_KEY"],
  },
  google_business_profile: {
    label: "Google Business",
    color: "#4285f4",
    requiredCreds: ["GOOGLE_SERVICE_ACCOUNT_JSON"],
  },
  google_drive: {
    label: "Google Drive",
    color: "#0f9d58",
    requiredCreds: ["GOOGLE_SERVICE_ACCOUNT_JSON"],
  },
  pagespeed: {
    label: "PageSpeed",
    color: "#06b6d4",
    requiredCreds: [],
  },
  builtwith: {
    label: "BuiltWith",
    color: "#3eab49",
    requiredCreds: [],
  },
};

export const PLAN_LIMITS = {
  free: { seats: 1, connections: 3, monthlyCalls: 500, price: "$0" },
  starter: { seats: 3, connections: 10, monthlyCalls: 5000, price: "$49" },
  pro: { seats: 10, connections: 50, monthlyCalls: 50000, price: "$149" },
  enterprise: { seats: 999999, connections: 999999, monthlyCalls: 999999999, price: "Custom" },
} as const;
