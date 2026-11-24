// One draft, in two columns: on the left what the reader would see; on the right the next step and the facts,
// each beside its quote and source. Clicking [3] in the text jumps the panel to fact 3.
// After the expert answers, the left column shows their version (AFTER) with the AI draft (BEFORE) one click away.

import Link from "next/link";
import ActionForm from "@/components/ActionForm";
import Markdown from "@/components/Markdown";
import { precheckDraft, publishDraft, sendToExpert } from "../_lib/actions";
import { hostOf, quoteLink, type Draft } from "../_lib/api";

// Exact time in India time, e.g. "24 Nov, 10:05 am".
const when = (iso: string) =>
  new Date(iso).toLocaleString("en-IN", { timeZone: "Asia/Kolkata", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" });

export default function DraftView({ draft }: { draft: Draft }) {
  const s = draft.status;
  const open = s === "draft"; // only an unchecked draft can be ticked
  const done = draft.facts.filter((f) => f.verified).length;
  const total = draft.facts.length;
  const review = draft.review?.decision ? draft.review : null; // the expert's answer, once they've given one
  const after = review?.edited_body; // their edited text, if they changed it
  // Title, search text and image text they changed: shown with the AI's version beside it.
  const changes = review
    ? ([
        ["Title", review.edited_title, draft.title],
        ["Search-result text", review.edited_meta_description, draft.meta_description],
        ["Image description", review.edited_alt_text, draft.alt_text],
      ] as const).filter(([, now]) => now)
    : [];

  const facts = (
    <ol className="fact-list">
      {draft.facts.map((f) => (
        <li key={f.id} id={`fact-${f.n}`} className={f.verified ? "fact fact--ok" : "fact"}>
          <p className="fact-claim"><span className="fact-n">[{f.n}]</span> {f.claim}</p>
          <blockquote className="fact-quote">{f.snippet}</blockquote>
          <p className="fact-meta">
            <a href={quoteLink(f.source_url, f.snippet)} target="_blank" rel="noreferrer">Show the quote on {hostOf(f.source_url)} ↗</a>
            <span>read {f.checked_on}</span>
          </p>
          {open && !f.verified ? (
            <label className="fact-check">
              <input type="checkbox" name="fact" value={f.id} /> The source says this
            </label>
          ) : (
            <p className="fact-done">{f.verified ? "Checked" : "Not checked"}</p>
          )}
        </li>
      ))}
    </ol>
  );
  const draftId = <input type="hidden" name="draft_id" value={draft.id} />;

  return (
    <div className="adm-split adm-split--draft">
      <article className="dv">
        <p className="dv-top">
          <Link href={`/admin?q=${draft.question_id}`}>← Back to the question</Link>
          <a className="dv-jump" href="#facts">{open ? "Check facts ↓" : "Next step ↓"}</a>
        </p>
        <header>
          <p className="dv-kicker">
            Draft v{draft.version} <span className={`dv-status dv-status--${s}`}>{s.replace("_", " ")}</span>
          </p>
          <h1 className="dv-title">{draft.title}</h1>
          <dl className="dv-seo">
            <div><dt>Search result text (meta description)</dt><dd>{draft.meta_description}</dd></div>
            <div><dt>Image alt text (describes the page&apos;s image for screen readers)</dt><dd>{draft.alt_text}</dd></div>
          </dl>
        </header>

        <details className="dv-timeline" open>
          <summary>Timeline (India time)</summary>
          <ol>
            {draft.timeline.map((t, i) => (
              <li key={i}><time dateTime={t.at}>{when(t.at)}</time> {t.step}</li>
            ))}
          </ol>
        </details>

        {review && (
          <section className="dv-review" aria-labelledby="review-h">
            <h2 id="review-h" className="label label--route">{review.expert_name ?? "The expert"}&apos;s answer, {review.decided_at?.slice(0, 10)}</h2>
            <p className="dv-review__decision">
              {review.decision === "approved" && "Approved as written."}
              {review.decision === "edited" && "Approved with their edits. Their version is below; the AI draft is under it."}
              {review.decision === "rejected" && "Rejected."}
            </p>
            {review.note && <p><strong>Why:</strong> {review.note}</p>}
            {changes.length > 0 && (
              <dl className="dv-review__changes">
                {changes.map(([label, now, was]) => (
                  <div key={label}>
                    <dt>{label} (their version)</dt>
                    <dd>{now}</dd>
                    <dd className="dv-review__was">AI draft: {was}</dd>
                  </div>
                ))}
              </dl>
            )}
            {review.advice && <p><strong>Their advice for readers:</strong> {review.advice}</p>}
          </section>
        )}

        <Markdown text={after ?? draft.body} className="md" />

        {after && (
          <details className="dv-before">
            <summary>Show the AI draft before the expert&apos;s edits</summary>
            <Markdown text={draft.body} className="md" />
          </details>
        )}

        {draft.expert_questions.length > 0 && (
          <section>
            <h2 className="dv-h">Questions for the expert</h2>
            <ul className="dv-list">{draft.expert_questions.map((q) => <li key={q}>{q}</li>)}</ul>
          </section>
        )}

        <details className="dv-jsonld">
          <summary>Structured data for search engines (built by code)</summary>
          <pre>{JSON.stringify(draft.json_ld, null, 2)}</pre>
        </details>
      </article>

      <aside className="fp" id="facts" aria-labelledby="facts-h">
        <div className="fp-head">
          <h2 id="facts-h">Facts <span>{done} of {total} checked</span></h2>
          <div className="fp-bar" aria-hidden="true"><span style={{ width: `${total ? (100 * done) / total : 0}%` }} /></div>
          {open && (
            <p className="fp-hint">
              For each fact: click &ldquo;Show the quote&rdquo;. The page opens with the quote highlighted in yellow. Tick
              the fact if the quote is there and says the same as the claim above it. Nothing highlighted? Press Ctrl+F and
              search a few words of the quote; if it isn&apos;t on the page, leave the fact unticked.
            </p>
          )}
        </div>

        {open ? (
          <ActionForm action={precheckDraft} className="fp-form" label="Save ticked facts" pendingLabel="Saving…" buttonClassName="btn btn--primary fp-save">
            {draftId}
            {facts}
          </ActionForm>
        ) : (
          <div className="fp-form">
            {/* Pre-checked and with-expert share one form, so the link shown after sending survives the page refresh. */}
            {(s === "prechecked" || s === "in_review") && (
              <section className="next fp-next">
                <p className="label label--route">{s === "prechecked" ? "Next step" : "Waiting for the expert"}</p>
                <p className="next__text">
                  {s === "prechecked"
                    ? "Every fact is checked. Choose the expert: the link opens only with their personal code."
                    : `${draft.review?.expert_name ?? "The expert"} has a one-time link (it expires in 14 days). ` +
                      (draft.review?.opened_at ? `They opened it ${when(draft.review.opened_at)}. ` : "They haven't opened it yet. ") +
                      "Lost it, or want the other expert? A new link cancels the old one."}
                </p>
                <ActionForm
                  action={sendToExpert}
                  label={s === "prechecked" ? "Send to the expert" : "Send a new link"}
                  pendingLabel="Sending…"
                  className="fp-send"
                  buttonClassName={s === "prechecked" ? "btn btn--primary" : "btn"}
                >
                  {draftId}
                  <label className="fp-expert">
                    <span className="df-label">Send to</span>
                    <select name="expert" className="df-input" required defaultValue={draft.review?.expert ?? ""}>
                      <option value="" disabled>Choose the expert</option>
                      {Object.entries(draft.experts).map(([key, name]) => (
                        <option key={key} value={key}>{name}</option>
                      ))}
                    </select>
                  </label>
                </ActionForm>
              </section>
            )}
            {(s === "approved" || s === "edited") && (
              <section className="next fp-next">
                <p className="label label--route">Next step</p>
                <p className="next__text">{draft.review?.expert_name ?? "The expert"} approved it. Publish it as a public page.</p>
                <ActionForm action={publishDraft} label="Publish" pendingLabel="Publishing…" buttonClassName="btn btn--primary">
                  {draftId}
                </ActionForm>
              </section>
            )}
            {s === "rejected" && (
              <section className="next fp-next">
                <p className="label label--route">Next step</p>
                <p className="next__text">The expert rejected this version. Write a new one from better sources.</p>
                <Link className="btn btn--primary" href={`/admin?q=${draft.question_id}`}>Write a new version</Link>
              </section>
            )}
            {s === "published" && draft.slug && (
              <section className="next fp-next">
                <p className="label label--route">Live</p>
                <p className="next__text">This answer is published.</p>
                <a className="btn" href={`/q/${draft.slug}`} target="_blank" rel="noreferrer">Open the page ↗</a>
              </section>
            )}
            {facts}
          </div>
        )}
      </aside>
    </div>
  );
}
