// The answer desk. One page, three views, picked by the address:
//   /admin           overview: the steps, what to do next, your shortlist and the ranked questions
//   /admin?q=12      two columns: every question on the left, question 12 and its next step on the right
//   /admin?draft=7   two columns: draft 7 to read on the left, its facts to check on the right
//   /admin?view=social   Bluesky: posts for published answers, and replies waiting for your approval
//   /admin?view=results  Level 6: AI traffic, uploaded GA4 / Search Console exports, post results, what to answer next
import Link from "next/link";
import { Suspense } from "react";
import ActionForm from "@/components/ActionForm";
import DraftView from "./_components/DraftView";
import Problem from "./_components/Problem";
import QuestionPanel from "./_components/QuestionPanel";
import { collectQuestions, rankQuestions, selectQuestion } from "./_lib/actions";
import ResultsView from "./_components/ResultsView";
import SocialView from "./_components/SocialView";
import { hostOf, loadDraft, loadPipeline, loadSocial, loadStats, nextStep, one, scoreText, stageOf, STEPS, TARGET, type Pipeline } from "./_lib/api";

export default function AdminPage({ searchParams }: PageProps<"/admin">) {
  return (
    // Cache Components: live data must sit inside Suspense (docs: 01-getting-started/08-caching.md)
    <Suspense fallback={<p className="wrap adm-loading">Loading…</p>}>
      <Desk searchParams={searchParams} />
    </Suspense>
  );
}

async function Desk({ searchParams }: { searchParams: PageProps<"/admin">["searchParams"] }) {
  const params = await searchParams;

  if (one(params.view) === "social") {
    const social = await loadSocial().catch((e: Error) => e);
    return social instanceof Error ? <Problem error={social} /> : <SocialView {...social} />;
  }

  if (one(params.view) === "results") {
    const stats = await loadStats().catch((e: Error) => e);
    return stats instanceof Error ? <Problem error={stats} /> : <ResultsView {...stats} />;
  }

  const draftId = one(params.draft);
  if (draftId) {
    const draft = await loadDraft(draftId).catch((e: Error) => e);
    return draft instanceof Error ? <Problem error={draft} /> : <DraftView draft={draft} />;
  }

  const data = await loadPipeline().catch((e: Error) => e);
  if (data instanceof Error) return <Problem error={data} />;

  const question = data.questions.find((q) => q.id === Number(one(params.q)));
  if (question) {
    return (
      <div className="adm-split">
        <QuestionList data={data} current={question.id} />
        <QuestionPanel q={question} draft={data.latest.get(question.id)} />
      </div>
    );
  }
  return <Overview data={data} />;
}

function Overview({ data }: { data: Pipeline }) {
  const { questions, merged, latest } = data;
  const shortlist = questions.filter((q) => q.status !== "new");
  const ranked = questions.filter((q) => q.status === "new");
  const next = nextStep(data);
  const statuses = shortlist.map((q) => latest.get(q.id)?.status);
  const count = (...s: string[]) => statuses.filter((x) => x && s.includes(x)).length;
  const counts = [
    `${questions.length} questions`,
    `${questions.filter((q) => q.score !== null).length} scored`,
    `${shortlist.length} of ${TARGET}`,
    `${shortlist.filter((q) => latest.has(q.id)).length} drafted`,
    `${count("prechecked", "in_review", "approved", "edited", "rejected", "published")} done`,
    `${count("in_review")} waiting, ${count("approved", "edited", "published")} approved`,
    `${count("published")} live (20 max)`,
  ];
  const job = (name: string) => (next.job === name ? "btn btn--primary" : "btn"); // yellow only if it's the next step

  return (
    <>
      <section className="band--sea band--rule-bottom">
        <div className="wrap ov">
          <h1 className="ov-title">Answer desk</h1>
          <ol className="steps">
            {STEPS.map((name, i) => (
              <li key={name} aria-current={i + 1 === next.step ? "step" : undefined}>
                <span className="steps__n">{i + 1}</span>
                <span>
                  <strong>{name}</strong>
                  <small>{counts[i]}</small>
                </span>
              </li>
            ))}
          </ol>
          <div className="ov-row">
            <div className="next">
              <p className="label label--route">Next step</p>
              <p className="next__text">{next.text}</p>
              {next.href && <Link className="btn btn--primary" href={next.href}>{next.label}</Link>}
            </div>
            <div className="ov-jobs">
              <ActionForm action={collectQuestions} label="Collect new questions" pendingLabel="Collecting…" buttonClassName={job("collect")} />
              <ActionForm action={rankQuestions} label="Rank unscored" pendingLabel="Ranking…" buttonClassName={job("rank")} />
            </div>
          </div>
        </div>
      </section>

      <section className="wrap ov-list">
        <div className="ov-list__head">
          <h2>Shortlist</h2>
          <p>{shortlist.length} of {TARGET} picked. Open one to see its next step.</p>
        </div>
        {shortlist.length === 0 ? (
          <p className="empty">Nothing selected yet. Select the questions worth a page from the ranked list below.</p>
        ) : (
          <ol className="rows rows--link">
            {shortlist.map((q) => (
              <li key={q.id}>
                <span className="rows__score">{scoreText(q.score)}</span>
                <div>
                  <Link className="rows__title" href={`/admin?q=${q.id}`}>{q.text}</Link>
                  <p className="rows__meta">from {hostOf(q.source_url)}</p>
                </div>
                <span className="badge">{stageOf(q, latest.get(q.id))}</span>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="ov-list--ranked" id="ranked">
        <div className="wrap ov-list">
          <div className="ov-list__head">
            <h2>Ranked questions</h2>
            <p>Best buying questions first. {merged} duplicates hidden. The reasons are the AI&apos;s, so judge them yourself.</p>
          </div>
          {ranked.length === 0 ? (
            <p className="empty">No questions waiting. Collect new questions, then rank them.</p>
          ) : (
            <ol className="rows">
              {ranked.map((q) => (
                <li key={q.id}>
                  <span className="rows__score">{scoreText(q.score)}</span>
                  <div>
                    <Link className="rows__title" href={`/admin?q=${q.id}`}>{q.text}</Link>
                    <p className="rows__meta">{q.rank_reason} <span className="rows__host">{hostOf(q.source_url)}</span></p>
                  </div>
                  <ActionForm action={selectQuestion} label="Select" pendingLabel="Selecting…" className="rows__action" buttonClassName="btn btn--small">
                    <input type="hidden" name="question_id" value={q.id} />
                  </ActionForm>
                </li>
              ))}
            </ol>
          )}
        </div>
      </section>
    </>
  );
}

// The left column once a question is open: every question, shortlist first, the open one highlighted.
function QuestionList({ data: { questions, latest }, current }: { data: Pipeline; current: number }) {
  const groups = [
    { name: "Shortlist", list: questions.filter((q) => q.status !== "new") },
    { name: "Ranked", list: questions.filter((q) => q.status === "new") },
  ];
  return (
    <nav className="ql" aria-label="Questions">
      <Link href="/admin" className="ql-home">← Overview</Link>
      {groups.map(({ name, list }) =>
        list.length === 0 ? null : (
          <section key={name}>
            <h2 className="ql-h">{name} <span>{list.length}</span></h2>
            <ul>
              {list.map((q) => (
                <li key={q.id}>
                  <Link href={`/admin?q=${q.id}`} className="ql-item" aria-current={q.id === current ? "page" : undefined}>
                    <span className="ql-score">{scoreText(q.score)}</span>
                    <span className="ql-text">{q.text}</span>
                    {q.status !== "new" && <span className="badge">{stageOf(q, latest.get(q.id))}</span>}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ),
      )}
    </nav>
  );
}
