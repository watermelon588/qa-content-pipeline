"use server";
// Server Actions: what each admin button does. They run on the server, call the API, then refresh()
// re-renders the current page with fresh data in the same round trip.
// Docs: node_modules/next/dist/docs/01-app/02-guides/forms.md and .../04-functions/refresh.md

import { refresh } from "next/cache";
import { redirect } from "next/navigation";
import { api, type Result } from "@/lib/api";

const fail = (e: unknown): Result => ({ ok: false, message: e instanceof Error ? e.message : String(e) });
const id = (form: FormData, key: string) => Number(form.get(key)); // non-numbers become NaN and the API refuses them

export async function collectQuestions(): Promise<Result> {
  try {
    const r = await api<Record<string, { found?: number; new?: number; error?: string }>>("/jobs/collect", { method: "POST" });
    const parts = Object.entries(r).map(([src, v]) => (v.error ? `${src}: failed` : `${src}: ${v.new} new of ${v.found}`));
    refresh();
    return { ok: true, message: parts.join(", ") };
  } catch (e) {
    return fail(e);
  }
}

export async function rankQuestions(): Promise<Result> {
  try {
    const r = await api<{ ranked: number; merged: number; error?: string }>("/jobs/rank", { method: "POST" });
    refresh();
    if (r.error) return { ok: false, message: `Ranked ${r.ranked}, then stopped: ${r.error}` };
    return { ok: true, message: r.ranked ? `Ranked ${r.ranked}, merged ${r.merged} duplicates` : "Nothing new to rank" };
  } catch (e) {
    return fail(e);
  }
}

export async function selectQuestion(_: Result, form: FormData): Promise<Result> {
  try {
    await api(`/questions/${id(form, "question_id")}/select`, { method: "POST" });
    refresh();
    return { ok: true, message: "Added to your shortlist" };
  } catch (e) {
    return fail(e);
  }
}

export async function createDraft(_: Result, form: FormData): Promise<Result> {
  // Ticked known pages + any typed addresses (one per line) + at most one pasted page.
  const typed = String(form.get("extra_urls") || "").split(/\s+/).filter(Boolean);
  const urls = [...new Set([...form.getAll("source").map(String), ...typed])];
  const pastedUrl = String(form.get("pasted_url") || "").trim();
  const pastedText = String(form.get("pasted_text") || "").trim();
  if (Boolean(pastedUrl) !== Boolean(pastedText)) {
    return { ok: false, message: "Pasted text needs both the page address and the text." };
  }
  let draftId: number;
  try {
    const r = await api<{ draft_id: number }>(`/questions/${id(form, "question_id")}/draft`, {
      method: "POST",
      body: { source_urls: urls, source_texts: pastedUrl ? [{ url: pastedUrl, text: pastedText }] : [] },
    });
    draftId = r.draft_id;
  } catch (e) {
    return fail(e);
  }
  redirect(`/admin?draft=${draftId}`); // open the new draft so you can check its facts
}

export async function precheckDraft(_: Result, form: FormData): Promise<Result> {
  try {
    const r = await api<{ status: string; unverified_fact_ids: number[] }>(`/drafts/${id(form, "draft_id")}/precheck`, {
      method: "POST",
      body: { verified_fact_ids: form.getAll("fact").map(Number) },
    });
    refresh();
    const left = r.unverified_fact_ids.length;
    return left
      ? { ok: true, message: `Saved. ${left} fact${left === 1 ? "" : "s"} still to check.` }
      : { ok: true, message: "Every fact checked. The draft is pre-checked." };
  } catch (e) {
    return fail(e);
  }
}

export async function sendToExpert(_: Result, form: FormData): Promise<Result> {
  try {
    const r = await api<{ emailed: boolean; link?: string; error?: string }>(`/drafts/${id(form, "draft_id")}/send`, { method: "POST" });
    refresh();
    // The link comes back every time. Only its fingerprint is stored, so this is the one chance to copy it.
    if (r.emailed) return { ok: true, message: "Review email sent to your inbox. Forward it to the expert, or copy the link below.", link: r.link };
    return { ok: true, message: r.error || "Link ready. Copy it and send it to the expert yourself.", link: r.link };
  } catch (e) {
    return fail(e);
  }
}

// ---------- Level 5: Bluesky ----------
export async function writePost(_: Result, form: FormData): Promise<Result> {
  try {
    await api(`/pages/${encodeURIComponent(String(form.get("slug")))}/post`, { method: "POST" });
    refresh();
    return { ok: true, message: "Post written. Read it, edit it, then schedule it." };
  } catch (e) {
    return fail(e);
  }
}

export async function schedulePost(_: Result, form: FormData): Promise<Result> {
  // The time box has no time zone, so we say it's India time (+05:30). Empty = at the next check.
  const when = String(form.get("send_at") || "");
  try {
    await api(`/posts/${id(form, "post_id")}/schedule`, {
      method: "POST",
      body: { text: String(form.get("text") || ""), send_at: when ? `${when}:00+05:30` : null },
    });
    refresh();
    return { ok: true, message: when ? "Scheduled. It goes out at the first check after that time." : "Scheduled for the next check." };
  } catch (e) {
    return fail(e);
  }
}

export async function checkBluesky(): Promise<Result> {
  try {
    const r = await api<{ posts_sent: number; new_replies: number; replies_drafted: number; error: string | null }>("/jobs/social", { method: "POST" });
    refresh();
    const text = `Sent ${r.posts_sent} post${r.posts_sent === 1 ? "" : "s"}, found ${r.new_replies} new repl${r.new_replies === 1 ? "y" : "ies"}, suggested ${r.replies_drafted} answer${r.replies_drafted === 1 ? "" : "s"}.`;
    return r.error ? { ok: false, message: `${text} ${r.error}` } : { ok: true, message: text };
  } catch (e) {
    return fail(e);
  }
}

export async function decideReply(_: Result, form: FormData): Promise<Result> {
  const send = form.get("send") === "yes";
  try {
    await api(`/replies/${id(form, "reply_id")}/decide`, { method: "POST", body: { send, text: String(form.get("text") || "") } });
    refresh();
    return { ok: true, message: send ? "Reply sent." : "Marked as not answered." };
  } catch (e) {
    return fail(e);
  }
}

export async function publishDraft(_: Result, form: FormData): Promise<Result> {
  try {
    const r = await api<{ slug: string }>(`/drafts/${id(form, "draft_id")}/publish`, { method: "POST" });
    refresh();
    return { ok: true, message: `Published at /q/${r.slug}` };
  } catch (e) {
    return fail(e); // includes the API's "20 answers is the most" refusal
  }
}

// ---------- Level 6: results ----------
export async function uploadExport(_: Result, form: FormData): Promise<Result> {
  const file = form.get("file");
  if (!(file instanceof File) || file.size === 0) return { ok: false, message: "Choose a CSV file first." };
  if (file.size > 2_000_000) return { ok: false, message: "That file is over 2 MB. Export fewer rows." };
  try {
    const r = await api<{ rows: number }>("/uploads", {
      method: "POST",
      body: { kind: String(form.get("kind")), filename: file.name, text: await file.text() },
    });
    refresh();
    return { ok: true, message: `Uploaded ${file.name}: ${r.rows} rows.` };
  } catch (e) {
    return fail(e);
  }
}

export async function askForSuggestions(): Promise<Result> {
  try {
    const r = await api<{ picks: unknown[] }>("/jobs/suggest", { method: "POST" });
    refresh();
    return { ok: true, message: `The AI suggested ${r.picks.length} question${r.picks.length === 1 ? "" : "s"}. You pick.` };
  } catch (e) {
    return fail(e);
  }
}
