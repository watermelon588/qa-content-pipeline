// Talks to the FastAPI backend. Only ever runs on the server (Server Components and Server Actions),
// so CRON_SECRET stays on the server: it has no NEXT_PUBLIC_ prefix, so Next never sends it to the browser.
// Shared by the admin desk, the expert's review page and the public answer pages.

const API_URL = process.env.API_URL || "http://localhost:8000";

/** An API error that keeps the HTTP status, so a page can tell "wrong code" (401) from "not yours" (403). */
export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function api<T>(path: string, init?: { method?: string; body?: unknown; headers?: Record<string, string> }): Promise<T> {
  let res: Response;
  try {
    res = await fetch(API_URL + path, {
      method: init?.method || "GET",
      headers: { Authorization: `Bearer ${process.env.CRON_SECRET || ""}`, "Content-Type": "application/json", ...init?.headers },
      body: init?.body === undefined ? undefined : JSON.stringify(init.body),
    });
  } catch {
    throw new Error(`The API is not reachable at ${API_URL}. Is it running?`);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(typeof data.detail === "string" ? data.detail : `The API answered ${res.status}`, res.status);
  return data as T;
}

/** What every form button gets back from its Server Action. `link` is only for "send to expert". */
export type Result = { ok: boolean; message: string; link?: string } | null;

/** A fact as the expert and the public page see it. */
export type PublicFact = { n: number; claim: string; source_url: string; snippet?: string; checked_on: string };

/** One published answer, from GET /pages/{slug}. */
export type Page = {
  slug: string;
  published_at: string;
  title: string;
  body: string; // the expert's edit if they made one, else the approved draft
  meta_description: string;
  alt_text: string;
  json_ld: Record<string, unknown>;
  decision: "approved" | "edited";
  advice: string | null;
  decided_at: string;
  reviewer: string | null; // the expert who approved this answer, e.g. "Sanath W, Senior DevOps Engineer"
  facts: PublicFact[];
  bluesky_url: string | null; // our Bluesky post about this answer, once it has been sent
};

/** The reviewers' public names, from GET /experts: {"sanath": "Sanath W, Senior DevOps Engineer", ...}. */
export type Experts = Record<string, string>;

// A link that opens the source AND highlights the quote on it, using a "text fragment" (#:~:text=start,end), a
// browser feature in Chrome, Edge, Safari and Firefox. Long quotes use their first and last 4 words, so a small
// difference in the middle (a line break, a table cell) doesn't stop the match. If a browser can't find the text it
// simply opens the page as normal. The spec needs "-", "," and "&" escaped; encodeURIComponent misses "-".
export const quoteLink = (url: string, quote: string) => {
  const enc = (s: string) => encodeURIComponent(s).replace(/-/g, "%2D");
  const words = quote.split(/\s+/).filter(Boolean);
  const text = words.length <= 8 ? enc(words.join(" ")) : `${enc(words.slice(0, 4).join(" "))},${enc(words.slice(-4).join(" "))}`;
  return `${url.split("#")[0]}#:~:text=${text}`;
};

export const hostOf = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
};
