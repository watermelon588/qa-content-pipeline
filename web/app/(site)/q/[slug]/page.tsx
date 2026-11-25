// One published answer. Only drafts the expert approved ever reach GET /pages/{slug} (the API joins on their
// decision), so this page can't show anything unapproved. It says plainly that AI drafted it, lists every
// source with the date we read it, and credits by name the expert who approved this answer (from the API).
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import Markdown from "@/components/Markdown";
import { api, hostOf, type Page } from "@/lib/api";
import { HUB_URL, SECTION_TITLE } from "@/lib/site";

const loadPage = (slug: string) => api<Page>(`/pages/${encodeURIComponent(slug)}`).catch(() => null);
const day = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });

export async function generateMetadata({ params }: PageProps<"/q/[slug]">): Promise<Metadata> {
  const page = await loadPage((await params).slug);
  if (!page) return { title: "Answer not found", robots: { index: false } };
  return {
    title: page.title,
    description: page.meta_description,
    alternates: { canonical: `/q/${page.slug}` },
    openGraph: { type: "article", title: page.title, description: page.meta_description, publishedTime: page.published_at },
  };
}

export default function AnswerPage({ params }: PageProps<"/q/[slug]">) {
  return (
    <Suspense fallback={<p className="wrap section-pad muted">Loading…</p>}>
      <Answer params={params} />
    </Suspense>
  );
}

async function Answer({ params }: { params: PageProps<"/q/[slug]">["params"] }) {
  const page = await loadPage((await params).slug);
  if (!page) notFound();
  const expert = page.reviewer ?? "our expert reviewer"; // older links (before expert codes) have no name

  return (
    <article>
      {/* Built by code from checked data, not by the AI; "<" is escaped so the text can't close the script tag */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(page.json_ld).replace(/</g, "\\u003c") }} />

      <header className="band--sea band--rule-bottom">
        <div className="wrap wrap--narrow answer-head">
          <p className="label label--route">{SECTION_TITLE} · Answer</p>
          <h1 className="h2">{page.title}</h1>
          <p className="answer-marks">
            <span className="badge">AI-assisted draft</span>
            <span className="badge">Reviewed by {page.reviewer ? "a named expert" : "an expert"}</span>
          </p>
          <p className="muted">Published {day(page.published_at)}. Approved by {expert} on {day(page.decided_at)}.</p>
        </div>
      </header>

      <div className="wrap wrap--narrow section-pad answer-body">
        <Markdown text={page.body} className="prose answer-text" />

        {page.advice && (
          <aside className="answer-advice" aria-label="Expert advice">
            <p className="label">From {expert}</p>
            <p>{page.advice}</p>
          </aside>
        )}

        <section aria-labelledby="sources-h">
          <h2 id="sources-h" className="answer-h">Sources</h2>
          <ol className="answer-sources">
            {page.facts.map((f) => (
              <li key={f.n} id={`fact-${f.n}`}>
                <span className="answer-sources__n">[{f.n}]</span>
                <div>
                  <p>{f.claim}</p>
                  <p className="muted">
                    <a href={f.source_url} rel="noreferrer">{hostOf(f.source_url)}</a>, checked {day(f.checked_on)}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <p className="answer-how muted">
          How this page was made: AI wrote the first draft using only the sources above. A person checked every
          fact against its source, then {expert} reviewed and approved the answer. Prices and features change, so
          check the provider before you buy. Compare every provider in the{" "}
          <a href={`${HUB_URL}/providers/`}>AI Atlas India provider index</a>. Spotted a mistake? <a href={`${HUB_URL}/contact/`}>Tell us</a>.
        </p>
      </div>
    </article>
  );
}
