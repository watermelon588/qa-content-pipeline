// What the expert sees when they open their one-time link: everything that will be published (title, search-result
// text, image description, the answer, the structured data), every fact with the quote it came from, our questions
// for them, and one form to approve, edit or reject. Choosing "edit" reveals editable boxes for the title, search
// text, image description and answer; "reject" reveals the reason box (pure CSS, see .rv-form in admin.css).
// The link alone shows nothing: the first time, the expert types their personal reviewer code; it is then kept in a
// cookie. Every load and every decision sends it to the API, which checks it belongs to the expert this link went to.
import { cookies } from "next/headers";
import { Suspense } from "react";
import ActionForm from "@/components/ActionForm";
import Markdown from "@/components/Markdown";
import { api, ApiError, hostOf, quoteLink, type PublicFact } from "@/lib/api";
import { decideReview, enterCode, forgetCode } from "../actions";
import { EXPERT_COOKIE, isCode } from "../code";

type ReviewData = {
  expert: string; // the expert this link was sent to, e.g. "Sanath W, Senior DevOps Engineer"
  decision: "approved" | "edited" | "rejected" | null;
  title: string;
  body: string;
  meta_description: string;
  alt_text: string;
  json_ld: Record<string, unknown>;
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
  const code = (await cookies()).get(EXPERT_COOKIE)?.value;
  if (isCode(token) && !code) return <CodeForm token={token} />;
  const data = isCode(token)
    ? await api<ReviewData>(`/review/${token}`, { headers: { "X-Expert-Code": code || "" } }).catch((e: Error) => e)
    : new Error("this review link is not valid");

  // 401: the saved code no longer works (changed, or typed for another site). Ask again.
  if (data instanceof ApiError && data.status === 401) {
    return <CodeForm token={token} message="Your saved reviewer code no longer works. Please type it again." />;
  }
  // 403: a real reviewer, but this answer was sent to the other one.
  if (data instanceof ApiError && data.status === 403) {
    return (
      <div className="wrap wrap--narrow section-pad rv-note">
        <h1 className="h2">This answer was sent to another reviewer</h1>
        <p className="lede">
          Each review link opens only with the code of the expert it was sent to, so the same answer can&apos;t be
          reviewed twice. If this computer is shared and you are that expert, forget the saved code and type yours.
        </p>
        <form action={forgetCode}>
          <button type="submit" className="btn">Forget the saved code</button>
        </form>
      </div>
    );
  }
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
          <p className="label label--route">Expert review · for {data.expert}</p>
          <h1 className="dv-title">{data.title}</h1>
          <p className="lede">
            AI drafted this answer only from the sources listed below it, and we checked every fact against its
            source. Please read it, then approve, edit or reject it at the bottom. Nothing goes live without your approval.
          </p>
        </div>
      </section>

      <div className="wrap wrap--narrow rv-body">
        <section aria-labelledby="meta-h">
          <h2 id="meta-h" className="dv-h">Everything that will be published</h2>
          <dl className="rv-meta">
            <div>
              <dt>Page title</dt>
              <dd>{data.title}</dd>
            </div>
            <div>
              <dt>Search-result text (meta description)</dt>
              <dd>{data.meta_description}</dd>
              <dd className="df-help">The sentence Google and AI assistants show under the title. About 120 to 155 characters reads best.</dd>
            </div>
            <div>
              <dt>Image description (alt text)</dt>
              <dd>{data.alt_text}</dd>
              <dd className="df-help">Describes the page&apos;s lead image for screen readers and search engines. We don&apos;t publish an image yet; this is the text it would carry.</dd>
            </div>
          </dl>
        </section>

        <section aria-labelledby="answer-h">
          <h2 id="answer-h" className="dv-h">The answer</h2>
          <Markdown text={data.body} className="md" />
        </section>

        <section aria-labelledby="facts-h">
          <h2 id="facts-h" className="dv-h">Facts and where they come from</h2>
          <p className="df-help">
            Each link opens the provider&apos;s page with the quote highlighted in yellow. If nothing is highlighted, press
            Ctrl+F and search a few words of the quote.
          </p>
          <ol className="fact-list rv-facts">
            {data.facts.map((f) => (
              <li key={f.n} id={`fact-${f.n}`} className="fact">
                <p className="fact-claim"><span className="fact-n">[{f.n}]</span> {f.claim}</p>
                <blockquote className="fact-quote">{f.snippet}</blockquote>
                <p className="fact-meta">
                  <a href={f.snippet ? quoteLink(f.source_url, f.snippet) : f.source_url} target="_blank" rel="noreferrer">
                    Show the quote on {hostOf(f.source_url)} ↗
                  </a>
                  <span>read {f.checked_on}</span>
                </p>
              </li>
            ))}
          </ol>
        </section>

        <details className="dv-jsonld">
          <summary>Structured data for search engines (built by code from the title and text above)</summary>
          <pre>{JSON.stringify(data.json_ld, null, 2)}</pre>
        </details>

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
              <span className="df-label">Page title</span>
              <input name="title" className="df-input" defaultValue={data.title} maxLength={120} />
            </label>

            <label className="rv-edit">
              <span className="df-label">Search-result text (meta description)</span>
              <textarea name="meta_description" className="df-input" rows={3} defaultValue={data.meta_description} maxLength={300} />
            </label>

            <label className="rv-edit">
              <span className="df-label">Image description (alt text)</span>
              <textarea name="alt_text" className="df-input" rows={2} defaultValue={data.alt_text} maxLength={300} />
            </label>

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
          <p className="df-help">
            This link works once. After you send, the decision can&apos;t be changed here. It is saved under your name,{" "}
            {data.expert}.
          </p>
        </section>
      </div>
    </>
  );
}

// The first visit (or a new browser): one box for the personal reviewer code. Nothing of the answer is shown yet.
function CodeForm({ token, message }: { token: string; message?: string }) {
  return (
    <div className="wrap wrap--narrow section-pad rv-note">
      <p className="label label--route">Expert review</p>
      <h1 className="h2">Enter your reviewer code</h1>
      <p className="lede">
        {message ?? "We sent you a personal code separately from this email. You only need it once on this browser."}
      </p>
      <ActionForm action={enterCode} className="rv-code" label="Open the answer" pendingLabel="Checking…" buttonClassName="btn btn--primary">
        <input type="hidden" name="token" value={token} />
        <label className="rv-code__field">
          <span className="df-label">Reviewer code</span>
          <input
            name="code"
            className="df-input"
            required
            autoComplete="one-time-code"
            autoCapitalize="characters"
            spellCheck={false}
            maxLength={20}
            placeholder="XXXX-XXXX"
          />
        </label>
      </ActionForm>
    </div>
  );
}
