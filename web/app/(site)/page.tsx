import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";
import AnswerList from "@/components/AnswerList";
import { previewOf, type AnswerCard } from "@/lib/answers";
import { api, type Page } from "@/lib/api";
import { HUB_URL, SECTION_LEDE, SECTION_NAME, SECTION_TITLE, SITE_NAME, SITE_URL } from "@/lib/site";
import { providerOf } from "@/lib/sources";

// Describes the site to search engines and AI answer engines. Static, so it is safe to inline.
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: `${SITE_NAME}: ${SECTION_NAME}`,
  url: SITE_URL,
  inLanguage: "en-IN",
  publisher: { "@type": "Organization", name: "Vyohm AI Private Limited", url: HUB_URL },
};

export const metadata: Metadata = { alternates: { canonical: "/" } };

const STEPS = [
  { title: "We find the question", meta: "What business owners search for and ask." },
  { title: "AI drafts an answer", meta: "Only from cited, dated sources." },
  { title: "A named expert edits it", meta: "They check it, add their own experience and sign." },
  { title: "We publish and re-check", meta: "Both bylines, the sources and the review date." },
];

type Listed = Pick<Page, "slug" | "title" | "meta_description">;

const day = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });
const count = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;

// The list endpoint has only titles, so each answer is loaded too, for its opening lines, reviewer and sources.
// ponytail: one request per answer, all at once. Fine because publishing stops at 20; add the fields to
// GET /pages if the page ever feels slow. If one fails, that answer still shows with its search description.
async function toCard(listed: Listed): Promise<AnswerCard> {
  const page = await api<Page>(`/pages/${encodeURIComponent(listed.slug)}`).catch(() => null);
  const fallback = { slug: listed.slug, title: listed.title, preview: listed.meta_description, trust: "", providers: [] };
  if (!page) return fallback;
  const checked = page.facts.map((f) => f.checked_on).sort().at(-1);
  const trust = [
    `Approved by ${page.reviewer ?? "our expert reviewer"}`,
    count(page.facts.length, "cited fact"),
    count(new Set(page.facts.map((f) => f.source_url)).size, "source page"),
    ...(checked ? [`checked ${day(checked)}`] : []),
  ].join(" · ");
  return {
    ...fallback,
    preview: previewOf(page.body) || listed.meta_description,
    trust,
    providers: [...new Set(page.facts.map((f) => providerOf(f.source_url)))],
  };
}

// The published answers, newest first. If the API is down, the page still renders with the empty message.
async function Answers() {
  const pages = await api<Listed[]>("/pages").catch(() => []);
  if (pages.length === 0) {
    return (
      <div className="empty">
        <p><strong>No published answers yet.</strong></p>
        <p className="muted">The first ones are with our reviewer. They appear here as soon as they are approved.</p>
      </div>
    );
  }
  return <AnswerList cards={await Promise.all(pages.map(toCard))} />;
}

export default function Home() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />

      <section className="band--sea band--rule-bottom">
        <div className="wrap plate">
          <div className="plate__text">
            <p className="label label--route">Plate 06 B2</p>
            <h1 className="display">{SECTION_TITLE}</h1>
            <p className="lede">{SECTION_LEDE}</p>
            <p><span className="badge">First answers in review</span></p>
            <p className="plate__note">
              Each page answers one question an Indian business owner asks before renting GPUs or cloud
              compute. Nothing is published here until a named expert has signed it.
            </p>
            <Link className="btn btn--primary" href="/about">How this section works</Link>
          </div>
          <figure className="figure">
            <Image
              src="/plate-gpu.webp"
              alt="Illustration of two server racks with neat cables in a small server room."
              width={1278}
              height={952}
              sizes="(min-width: 900px) 480px, 92vw"
              loading="eager"
              fetchPriority="high"
            />
            <figcaption className="figure__caption"><span>Plate 06</span><span>Illustration</span></figcaption>
          </figure>
        </div>
      </section>

      <section className="wrap section-pad" aria-labelledby="answers-h">
        <h2 id="answers-h" className="h2">Questions business owners are asking</h2>
        <div style={{ marginTop: "var(--atlas-space-5)" }}>
          <Suspense fallback={<p className="muted">Loading answers…</p>}>
            <Answers />
          </Suspense>
        </div>
      </section>

      <section className="band--ink">
        <div className="wrap section-pad">
          <h2 className="h2">How an answer gets published</h2>
          <ol className="entry-list" style={{ marginTop: "var(--atlas-space-5)", borderTopColor: "var(--atlas-paper)" }}>
            {STEPS.map((s, i) => (
              <li key={s.title} style={{ borderBottomColor: "var(--atlas-on-ink-muted)" }}>
                <span className="entry-list__n" style={{ color: "var(--atlas-signal)" }}>{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <p className="entry-list__title">{s.title}</p>
                  <p className="entry-list__meta" style={{ color: "var(--atlas-on-ink-muted)" }}>{s.meta}</p>
                </div>
              </li>
            ))}
          </ol>
          <p style={{ marginTop: "var(--atlas-space-5)" }}>
            <Link className="btn" style={{ borderColor: "var(--atlas-paper)", color: "var(--atlas-paper)" }} href="/about">
              Read how we use AI
            </Link>
          </p>
        </div>
      </section>
    </>
  );
}
