// The right column once a question is open: the question, why it ranked, and ONE next step with a yellow button.

import Link from "next/link";
import { selectQuestion } from "../_lib/actions";
import { hostOf, scoreText, stageOf, type DraftSummary, type Question } from "../_lib/api";
import ActionForm from "@/components/ActionForm";
import DraftForm from "./DraftForm";

export default function QuestionPanel({ q, draft }: { q: Question; draft?: DraftSummary }) {
  const stage = stageOf(q, draft);

  return (
    <article className="qp">
      <Link href="/admin" className="qp-back">← All questions</Link>
      <p className="qp-kicker">
        <span className="badge">{stage}</span>
        <span>Score {scoreText(q.score)}</span>
        <a href={q.source_url} target="_blank" rel="noreferrer">Asked on {hostOf(q.source_url)} ↗</a>
      </p>
      <h1 className="qp-title">{q.text}</h1>
      {q.rank_reason && (
        <p className="qp-reason">
          <span className="label">Why the AI ranked it</span>
          {q.rank_reason}
        </p>
      )}

      <section className="next" aria-labelledby="next-h">
        <h2 id="next-h" className="label label--route">Next step</h2>
        {stage === "Ranked" && (
          <>
            <p className="next__text">Worth a page? Select it to add it to your shortlist.</p>
            <ActionForm action={selectQuestion} label="Select this question" pendingLabel="Selecting…" buttonClassName="btn btn--primary">
              <input type="hidden" name="question_id" value={q.id} />
            </ActionForm>
          </>
        )}
        {stage === "Selected" && (
          <>
            <p className="next__text">Tick the provider pages to draw facts from. The AI may use only these pages.</p>
            <DraftForm questionId={q.id} />
          </>
        )}
        {stage === "Drafted" && draft && (
          <>
            <p className="next__text">Draft v{draft.version} is ready. Compare each fact with its source.</p>
            <Link className="btn btn--primary" href={`/admin?draft=${draft.id}`}>Check facts in draft v{draft.version}</Link>
          </>
        )}
        {stage === "Pre-checked" && draft && (
          <>
            <p className="next__text">Every fact is checked. Send draft v{draft.version} to the expert.</p>
            <Link className="btn btn--primary" href={`/admin?draft=${draft.id}`}>Send to expert</Link>
          </>
        )}
        {stage === "With expert" && draft && (
          <>
            <p className="next__text">Draft v{draft.version} is with the expert. Nothing to do until they answer.</p>
            <Link className="btn" href={`/admin?draft=${draft.id}`}>Open draft v{draft.version}</Link>
          </>
        )}
        {stage === "Approved" && draft && (
          <>
            <p className="next__text">The expert approved draft v{draft.version}. Read their version, then publish it.</p>
            <Link className="btn btn--primary" href={`/admin?draft=${draft.id}`}>Review and publish</Link>
          </>
        )}
        {stage === "Rejected" && draft && (
          <>
            <p className="next__text">The expert rejected draft v{draft.version}. Read why, then write a new version below.</p>
            <Link className="btn" href={`/admin?draft=${draft.id}`}>Read their reasons</Link>
          </>
        )}
        {stage === "Published" && draft && (
          <>
            <p className="next__text">This answer is live. The draft view links to its public page.</p>
            <Link className="btn" href={`/admin?draft=${draft.id}`}>Open draft v{draft.version}</Link>
          </>
        )}
      </section>

      {draft && stage !== "Published" && (
        <details className="qp-again" open={stage === "Rejected"}>
          <summary>Not happy with the draft? Write a new version from other pages</summary>
          <DraftForm questionId={q.id} again />
        </details>
      )}
    </article>
  );
}
