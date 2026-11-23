// Talks to the FastAPI backend. Only ever runs on the server (Server Components and Server Actions),
// so CRON_SECRET stays on the server: it has no NEXT_PUBLIC_ prefix, so Next never sends it to the browser.
// Shared by the admin desk, the expert's review page and the public answer pages.

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function api<T>(path: string, init?: { method?: string; body?: unknown }): Promise<T> {
  let res: Response;
  try {
    res = await fetch(API_URL + path, {
      method: init?.method || "GET",
      headers: { Authorization: `Bearer ${process.env.CRON_SECRET || ""}`, "Content-Type": "application/json" },
      body: init?.body === undefined ? undefined : JSON.stringify(init.body),
    });
  } catch {
    throw new Error(`The API is not reachable at ${API_URL}. Is it running?`);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : `The API answered ${res.status}`);
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
  facts: PublicFact[];
};

export const hostOf = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
};
