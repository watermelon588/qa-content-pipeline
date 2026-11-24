// The admin desk's data: types, loaders, and the "what to do next" rules. api() itself lives in lib/api.ts.
import { api } from "@/lib/api";

export { hostOf, quoteLink } from "@/lib/api";

export type Question = {
  id: number;
  text: string;
  source: string;
  source_url: string;
  score: number | null;
  rank_reason: string | null;
  merged_into: number | null;
  status: "new" | "selected" | "drafted";
};

export type DraftStatus = "draft" | "prechecked" | "in_review" | "approved" | "edited" | "rejected" | "published";

export type DraftSummary = { id: number; question_id: number; version: number; title: string; status: DraftStatus };

export type Fact = {
  id: number;
  n: number;
  claim: string;
  source_url: string;
  snippet: string;
  checked_on: string;
  verified: boolean;
};

/** The expert's latest answer on a draft. edited_body is the AFTER version; the draft's body is BEFORE. */
export type Review = {
  decision: "approved" | "edited" | "rejected" | null; // null = link sent, no answer yet
  edited_body: string | null;
  edited_title: string | null; // the expert's AFTER version of each, null = left as the AI wrote it
  edited_meta_description: string | null;
  edited_alt_text: string | null;
  advice: string | null;
  note: string | null;
  decided_at: string | null;
  expert: string | null; // "sanath": the only expert whose code opens this link
  expert_name: string | null; // their display name
  opened_at: string | null; // first time they opened it with their code; null = not yet
};

export type Draft = DraftSummary & {
  body: string;
  meta_description: string;
  alt_text: string;
  json_ld: Record<string, unknown>;
  expert_questions: string[];
  created_at: string;
  facts: Fact[];
  review: Review | null;
  slug: string | null; // set once published
  timeline: { step: string; at: string }[]; // when each step happened, oldest first
  experts: Record<string, string>; // who it can be sent to: {"sanath": "Sanath W, ..."}
};

/** Everything the question screens need, in one go. */
export async function loadPipeline() {
  const [questions, drafts] = await Promise.all([api<Question[]>("/questions"), api<DraftSummary[]>("/drafts")]);
  const latest = new Map<number, DraftSummary>(); // newest draft per question (the list comes newest first)
  for (const d of drafts) if (!latest.has(d.question_id)) latest.set(d.question_id, d);
  const open = questions.filter((q) => q.merged_into === null); // duplicates can't be answered, so hide them
  return { questions: open, merged: questions.length - open.length, latest };
}

export const loadDraft = (id: string) => api<Draft>(`/drafts/${encodeURIComponent(id)}`);

export type Pipeline = Awaited<ReturnType<typeof loadPipeline>>;

/** The steps shown at the top of the desk. */
export const STEPS = ["Collect", "Rank", "Select", "Draft", "Check facts", "Expert review", "Publish"];
export const TARGET = 8; // answers we aim to publish (the API refuses more than 20)

/** The one thing to do next, so the desk can point at it. step is 1-based, matching STEPS. */
export function nextStep({ questions, latest }: Pipeline) {
  const shortlist = questions.filter((q) => q.status !== "new");
  const unscored = questions.filter((q) => q.status === "new" && q.score === null).length;
  const draftWith = (...s: DraftStatus[]) => shortlist.find((q) => s.includes(latest.get(q.id)?.status as DraftStatus));
  const toPublish = draftWith("approved", "edited");
  const toCheck = draftWith("draft");
  const toSend = draftWith("prechecked");
  const toDraft = shortlist.find((q) => q.status === "selected");
  const waiting = shortlist.filter((q) => latest.get(q.id)?.status === "in_review").length;
  const open = (q: Question) => `/admin?draft=${latest.get(q.id)!.id}`;

  if (questions.length === 0) return { step: 1, text: "Collect questions from Stack Exchange and Hacker News.", job: "collect" };
  if (unscored) return { step: 2, text: `Rank the ${unscored} unscored question${unscored === 1 ? "" : "s"}.`, job: "rank" };
  // Finish what's nearest to done first: publish, then send, then check, then draft.
  if (toPublish) return { step: 7, text: `The expert approved “${toPublish.text}”. Publish it.`, href: open(toPublish), label: "Review and publish" };
  if (toSend) return { step: 6, text: `Send “${toSend.text}” to the expert.`, href: open(toSend), label: "Send to expert" };
  if (toCheck) return { step: 5, text: `Check the facts in the draft for “${toCheck.text}”`, href: open(toCheck), label: "Check facts" };
  if (toDraft) return { step: 4, text: `Draft an answer to “${toDraft.text}”`, href: `/admin?q=${toDraft.id}`, label: "Draft it" };
  if (shortlist.length < TARGET) {
    const more = TARGET - shortlist.length;
    return { step: 3, text: `Select ${more} more question${more === 1 ? "" : "s"} worth a page. Best first, below.`, href: "#ranked", label: "See ranked questions" };
  }
  if (waiting) return { step: 6, text: `Waiting for the expert on ${waiting} draft${waiting === 1 ? "" : "s"}. Nothing to do until they answer.` };
  return { step: 7, text: "Everything on the shortlist is done. Select more questions to keep going." };
}

export type Stage = "Ranked" | "Selected" | "Drafted" | "Pre-checked" | "With expert" | "Approved" | "Rejected" | "Published";

const STAGE: Record<DraftStatus, Stage> = {
  draft: "Drafted",
  prechecked: "Pre-checked",
  in_review: "With expert",
  approved: "Approved",
  edited: "Approved", // approved with the expert's changes
  rejected: "Rejected",
  published: "Published",
};

/** Where a question is in the flow, using its newest draft. */
export function stageOf(q: Question, d?: DraftSummary): Stage {
  if (q.status === "new") return "Ranked";
  if (q.status === "selected" || !d) return "Selected";
  return STAGE[d.status];
}

// ---------- Level 5: Bluesky ----------
export type SocialPost = {
  slug: string;
  title: string;
  post_id: number | null; // null = no post written yet for this answer
  text: string | null;
  status: "drafted" | "scheduled" | "sent" | "failed" | null;
  send_at: string | null;
  uri: string | null;
  error: string | null;
  sent_at: string | null;
};

export type SocialReply = {
  id: number;
  their_uri: string;
  their_text: string;
  reason: "reply" | "mention";
  draft: string | null;
  final_text: string | null;
  decision: "approved" | "edited" | "rejected" | null;
  status: "fetched" | "drafted" | "sent" | "discarded";
  our_uri: string | null;
  created_at: string;
};

export const loadSocial = () => api<{ ready: boolean; posts: SocialPost[]; replies: SocialReply[] }>("/social");

/** at://did:plc:abc/app.bsky.feed.post/xyz -> https://bsky.app/profile/did:plc:abc/post/xyz */
export const bskyUrl = (uri: string) => {
  const [, , did, , rkey] = uri.split("/");
  return `https://bsky.app/profile/${did}/post/${rkey}`;
};

/** A stored time as the value of an <input type="datetime-local">, in India time (UTC+5:30). */
export const istInput = (iso: string | null) =>
  iso ? new Date(new Date(iso).getTime() + 330 * 60_000).toISOString().slice(0, 16) : "";

export const scoreText =(s: number | null) => (s === null ? "unscored" : s.toFixed(1));

export const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);

// ---------- Level 6: results ----------
export type Upload = {
  kind: "ga4" | "gsc" | "gsc_ai";
  filename: string;
  header: string[];
  rows: string[][]; // the top rows only
  row_count: number;
  totals: Record<string, number>; // count columns added up (clicks, impressions, users...)
  uploaded_at: string;
};

export type PostStats = {
  slug: string;
  title: string;
  uri: string;
  sent_at: string;
  likes: number;
  reposts: number;
  replies: number;
  quotes: number;
  stats_at: string | null;
};

export type Suggestion = {
  insight: string;
  picks: { question_id: number; reason: string; text: string; status: Question["status"] }[];
  created_at: string;
};

export type Stats = {
  ai: { kind: "crawler" | "referral"; name: string; visits: number }[]; // last 30 days
  ai_pages: { path: string; referrals: number | null; crawls: number | null }[];
  uploads: Upload[];
  posts: PostStats[];
  published: number;
  suggestion: Suggestion | null;
};

export const loadStats = () => api<Stats>("/stats");

export const UPLOAD_KINDS: Record<Upload["kind"], string> = {
  ga4: "GA4 report",
  gsc: "Search Console",
  gsc_ai: "Search Console: Generative AI",
};
