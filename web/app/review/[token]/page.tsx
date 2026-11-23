// What the expert sees when they open their one-time link: the draft, every fact with the quote it came from,
// our questions for them, and one form to approve, edit or reject. Choosing "edit" or "reject" reveals the
// box that goes with it (pure CSS, see .rv-form in admin.css).
import { Suspense } from "react";
import ActionForm from "@/components/ActionForm";
import Markdown from "@/components/Markdown";
import { api, hostOf, type PublicFact } from "@/lib/api";
import { decideReview } from "../actions";
import { isCode } from "../code";

type ReviewData = {
  decision: "approved" | "edited" | "rejected" | null;
  title: string;
  body: string;
  meta_description: string;
  alt_text: string;
  expert_questions: string[];
  facts: PublicFact[];
};

export default function ReviewPage({ params }: PageProps<"/review/[token]">) {
  return (
    // Cache Components: the address and live data are read inside Suspense
    <Suspense fallback={<p className="wrap adm-loading">Loading the draft…</p>}>
      <Review params={params} />
    </Suspense>
  );
}

async function Review({ params }: { params: PageProps<"/review/[token]">["params"] }) {
  const { token } = await params;
  const data = isCode(token)
    ? await api<ReviewData>(`/review/${token}`).catch((e: Error) => e)
    : new Error("this review link is not valid");

  if (data instanceof Error) {
    return (
      <div className="wrap wrap--narrow section-pad rv-note">
        <h1 className="h2">This link doesn&apos;t work</h1>
        <p className="lede">Sorry: {data.message}. Reply to the email you got and we&apos;ll send a fresh one.</p>
      </div>
    );
  }
  if (data.decision) {
    return (
      <div className="wrap wrap--narrow section-pad rv-note">
        <h1 className="h2">Thank you</h1>
        <p className="lede">Your decision ({data.decision}) on &ldquo;{data.title}&rdquo; is saved. You can close this page.</p>
      </div>
    );
  }

  return (
    <>
      <section className="band--sea band--rule-bottom">
        <div className="wrap wrap--narrow rv-head">
          <p className="label label--route">Expert review</p>
          <h1 className="dv-title">{data.title}</h1>
          <p className="lede">
            AI drafted this answer only from the sources listed below it, and we checked every fact against its
            source. Please read it, then approve, edit or reject it at the bottom. Nothing goes live without your approval.
          </p>
        </div>
      </section>

      <div className="wrap wrap--narrow rv-body">
        <Markdown text={data.body} className="md" />

        <section aria-labelledby="facts-h">
          <h2 id="facts-h" className="dv-h">Facts and where they come from</h2>
          <ol className="fact-list rv-facts">
            {data.facts.map((f) => (
              <li key={f.n} id={`fact-${f.n}`} className="fact">
                <p className="fact-claim"><span className="fact-n">[{f.n}]</span> {f.claim}</p>
                <blockquote className="fact-quote">{f.snippet}</blockquote>
                <p className="fact-meta">
                  <a href={f.source_url} target="_blank" rel="noreferrer">Open {hostOf(f.source_url)} ↗</a>
                  <span>read {f.checked_on}</span>
                </p>
              </li>
            ))}
          </ol>
        </section>

        <section aria-labelledby="decide-h" className="next rv-decide">
          <h2 id="decide-h" className="dv-h">Your decision</h2>
          <ActionForm action={decideReview} className="rv-form" label="Send my decision" pendingLabel="Saving…" buttonClassName="btn btn--primary">
            <input type="hidden" name="token" value={token} />
            <fieldset className="rv-choices">
              <legend className="df-label">Choose one</legend>
              <label className="df-source"><input type="radio" name="decision" value="approved" required /> Approve as written</label>
              <label className="df-source"><input type="radio" name="decision" value="edited" /> Approve with my edits</label>
              <label className="df-source"><input type="radio" name="decision" value="rejected" /> Reject</label>
            </fieldset>

            <label className="rv-edit">
              <span className="df-label">Your edited answer</span>
              <span className="df-help">Change anything. Keep the [1], [2] markers next to facts you keep; delete a marker with its fact.</span>
              <textarea name="body" className="df-input" rows={18} defaultValue={data.body} />
            </label>

            <label className="rv-reject">
              <span className="df-label">Why are you rejecting it?</span>
              <textarea name="note" className="df-input" rows={4} />
            </label>

            <label className="rv-advice">
              <span className="df-label">Your advice for readers (optional, 2 to 3 lines)</span>
              {data.expert_questions.length > 0 && (
                <span className="df-help">Some ideas: {data.expert_questions.join(" ")}</span>
              )}
              <textarea name="advice" className="df-input" rows={4} />
            </label>
          </ActionForm>
          <p className="df-help">This link works once. After you send, the decision can&apos;t be changed here.</p>
        </section>
      </div>
    </>
  );
}
