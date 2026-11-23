import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";
import { api, type Page } from "@/lib/api";
import { HUB_URL, SECTION_LEDE, SECTION_NAME, SECTION_TITLE, SITE_NAME, SITE_URL } from "@/lib/site";

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

// The published answers, newest first. If the API is down, the page still renders with the empty message.
async function Answers() {
  const pages = await api<Pick<Page, "slug" | "title" | "meta_description">[]>("/pages").catch(() => []);
  if (pages.length === 0) {
    return (
      <div className="empty">
        <p><strong>No published answers yet.</strong></p>
        <p className="muted">The first ones are with our reviewer. They appear here as soon as they are approved.</p>
      </div>
    );
  }
  return (
    <ol className="entry-list">
      {pages.map((p, i) => (
        <li key={p.slug}>
          <span className="entry-list__n">{String(i + 1).padStart(2, "0")}</span>
          <div>
            <Link className="entry-list__title" href={`/q/${p.slug}`}>{p.title}</Link>
            <p className="entry-list__meta">{p.meta_description}</p>
          </div>
        </li>
      ))}
    </ol>
  );
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
