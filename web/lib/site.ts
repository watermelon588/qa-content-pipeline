// One place for the facts that appear on every page. Change them here, not in the pages.

export const SITE_NAME = "AI Atlas India";
export const HUB_URL = "https://aiatlasindia.com";
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://gpu.aiatlasindia.com";
export const GA_ID = process.env.NEXT_PUBLIC_GA_ID; // GA4 measurement ID from Vyohm, e.g. G-XXXXXXX

// The section Vyohm assigned (setup email, 22 Nov 2026).
export const SECTION_NAME = "GPU cloud and AI infrastructure in India"; // formal name
export const SECTION_TITLE = "GPU and cloud"; // short name used by the hub and in the header
export const SECTION_LEDE = "Where to rent compute in India and what it costs.";

// Exact wording required by the guide on every page. Do not edit.
export const OWNERSHIP_LINE =
  "AI Atlas India is owned by Vyohm AI Private Limited, which also sells AI products. We cover every provider, Vyohm included, by the same rules.";

// Who is credited on the About page. null = not confirmed yet, the page says so honestly.
export const BUILDER_NAME = "Rohit Maity";
export const EXPERT_NAME: string | null = "Sanath W, Senior DevOps Engineer"; // agreed in writing to be named, 24 Nov 2026
export const BLUESKY_URL: string | null = "https://bsky.app/profile/watermelon588.bsky.social"; // set once the automated account exists

// Links into the shared hub. These pages belong to Vyohm's hub, not to this section.
const hub = (path: string) => `${HUB_URL}${path}`;
export const NAV = [
  { label: "Sections", href: hub("/#sections") },
  { label: "Providers", href: hub("/providers/") },
  { label: "How we evaluate", href: hub("/how-we-evaluate/") },
  { label: "Editorial policy", href: hub("/editorial-policy/") },
];
export const CONTACT = { label: "Contact", href: hub("/contact/") };
export const FOOTER_GUIDE = [
  { label: "Provider index", href: hub("/providers/") },
  { label: "How we evaluate", href: hub("/how-we-evaluate/") },
  { label: "Editorial policy", href: hub("/editorial-policy/") },
  { label: "Reviewers", href: hub("/reviewers/") },
];
export const FOOTER_SITE = [
  { label: "Ownership and disclosures", href: hub("/disclosures/") },
  { label: "Contact", href: hub("/contact/") },
  { label: "Privacy", href: hub("/privacy/") },
  { label: "Section kit", href: hub("/kit/") },
];
export const SECTIONS = ["WhatsApp", "CRM", "ERP", "Voice", "Indic", "GPU", "Sellers", "Factory"];
export const THIS_SECTION = "GPU";
