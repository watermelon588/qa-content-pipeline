// The results screen (/admin?view=results), Level 6. Top to bottom:
//   1. the headline numbers (visitors, search impressions, AI referrals, AI crawlers, Bluesky engagement);
//   2. what the AI suggests answering next, and why; you pick with the same Select button as the desk;
//   3. AI traffic from our own logs (proxy.ts), by source and by page;
//   4. how each Bluesky post did;
//   5. the GA4 and Search Console exports you uploaded (the Generative AI report has no API, so upload is the way).
// Plain numbers and tables, no charts: with this little data a chart would only hide the numbers.
import ActionForm from "@/components/ActionForm";
import { askForSuggestions, selectQuestion, uploadExport } from "../_lib/actions";
import { bskyUrl, UPLOAD_KINDS, type Stats, type Upload } from "../_lib/api";

const day = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata", day: "numeric", month: "short" });
const n = (v: number) => v.toLocaleString("en-IN");

/** The first total whose column name matches, from the newest upload of that kind. */
function total(uploads: Upload[], kind: Upload["kind"], column: RegExp) {
  for (const u of uploads.filter((u) => u.kind === kind)) {
    const key = Object.keys(u.totals).find((k) => column.test(k));
    if (key) return { value: u.totals[key], from: `${u.filename}, ${key}` };
  }
  return null;
}

export default function ResultsView({ ai, ai_pages, uploads, posts, published, suggestion }: Stats) {
  const sum = (kind: string) => ai.filter((a) => a.kind === kind).reduce((s, a) => s + a.visits, 0);
  const engagement = posts.reduce((s, p) => s + p.likes + p.reposts + p.replies + p.quotes, 0);
  const visitors = total(uploads, "ga4", /users/i);
  const impressions = total(uploads, "gsc", /impressions/i);
  const tiles = [
    { label: "Human visitors", value: visitors ? n(visitors.value) : "–", note: visitors?.from ?? "Upload a GA4 export below" },
    { label: "Search impressions", value: impressions ? n(impressions.value) : "–", note: impressions?.from ?? "Upload a Search Console export below" },
    { label: "AI referrals", value: n(sum("referral")), note: "ChatGPT, Perplexity, Gemini, Copilot, Claude · 30 days" },
    { label: "AI crawler visits", value: n(sum("crawler")), note: "GPTBot, ClaudeBot, PerplexityBot and others · 30 days" },
    { label: "Bluesky engagement", value: n(engagement), note: `Likes, reposts, replies, quotes on ${posts.length} post${posts.length === 1 ? "" : "s"}` },
    { label: "Answers live", value: `${published}`, note: "20 at most" },
  ];

  return (
    <>
      <section className="band--sea band--rule-bottom">
        <div className="wrap ov">
          <h1 className="ov-title">Results</h1>
          <dl className="res-tiles">
            {tiles.map((t) => (
              <div key={t.label} className="res-tile">
                <dt>{t.label}</dt>
                <dd className="res-tile__value">{t.value}</dd>
                <dd className="res-tile__note">{t.note}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section className="wrap ov-list" aria-labelledby="next-h">
        <div className="ov-list__head">
          <h2 id="next-h">What to answer next</h2>
          <p>The AI reads the numbers on this page and suggests up to 3 ranked questions. You decide.</p>
        </div>
        <ActionForm action={askForSuggestions} label={suggestion ? "Ask again with today's numbers" : "Ask the AI"} pendingLabel="Thinking…" buttonClassName={suggestion ? "btn" : "btn btn--primary"} />
        {suggestion && (
          <div className="res-suggest">
            <p className="label">What the audience responds to · {day(suggestion.created_at)}</p>
            <p className="res-insight">{suggestion.insight}</p>
            <ol className="rows">
              {suggestion.picks.map((p, i) => (
                <li key={p.question_id}>
                  <span className="rows__score">#{p.question_id}</span>
                  <div>
                    <p className="rows__title">{p.text}</p>
                    <p className="rows__meta">{p.reason}</p>
                  </div>
                  {p.status === "new" ? (
                    <ActionForm action={selectQuestion} label="Select" pendingLabel="Selecting…" className="rows__action" buttonClassName={i === suggestion.picks.findIndex((x) => x.status === "new") ? "btn btn--small btn--primary" : "btn btn--small"}>
                      <input type="hidden" name="question_id" value={p.question_id} />
                    </ActionForm>
                  ) : (
                    <span className="badge">Picked</span>
                  )}
                </li>
              ))}
            </ol>
          </div>
        )}
      </section>

      <section className="ov-list--ranked" aria-labelledby="ai-h">
        <div className="wrap ov-list">
          <div className="ov-list__head">
            <h2 id="ai-h">AI traffic</h2>
            <p>From our own logs, last 30 days. We count visits only: no IP addresses, nothing about the person.</p>
          </div>
          {ai.length === 0 ? (
            <p className="empty">No AI crawler or AI assistant visits recorded yet. They appear once the site is live.</p>
          ) : (
            <div className="res-pair">
              <Table head={["Source", "Type", "Visits"]} rows={ai.map((a) => [a.name, a.kind === "crawler" ? "crawler" : "sent a person", n(a.visits)])} />
              <Table head={["Page", "From AI assistants", "AI crawler visits"]} rows={ai_pages.map((p) => [p.path, n(p.referrals ?? 0), n(p.crawls ?? 0)])} />
            </div>
          )}
        </div>
      </section>

      <section className="wrap ov-list" aria-labelledby="posts-h">
        <div className="ov-list__head">
          <h2 id="posts-h">Bluesky posts</h2>
          <p>Counts are copied from Bluesky each time the social job runs. Best first.</p>
        </div>
        {posts.length === 0 ? (
          <p className="empty">No posts sent yet.</p>
        ) : (
          <Table
            head={["Answer", "Sent", "Likes", "Reposts", "Replies", "Quotes", ""]}
            rows={posts.map((p) => [p.title, day(p.sent_at), n(p.likes), n(p.reposts), n(p.replies), n(p.quotes),
              <a key="a" href={bskyUrl(p.uri)} target="_blank" rel="noreferrer">Open ↗</a>])}
          />
        )}
      </section>

      <section className="ov-list--ranked" aria-labelledby="up-h">
        <div className="wrap ov-list">
          <div className="ov-list__head">
            <h2 id="up-h">Search and analytics exports</h2>
            <p>We have Viewer access, not an API key, so export CSVs by hand and upload them. The same file name again replaces the old copy.</p>
          </div>
          <ActionForm action={uploadExport} className="res-upload" label="Upload" pendingLabel="Uploading…" buttonClassName="btn">
            <label className="so-field">
              <span className="df-label">What it is</span>
              <select name="kind" className="df-input" defaultValue="gsc">
                {Object.entries(UPLOAD_KINDS).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
              </select>
            </label>
            <label className="so-field">
              <span className="df-label">CSV file</span>
              <input type="file" name="file" accept=".csv,text/csv" className="df-input" />
            </label>
          </ActionForm>
          <p className="df-help">
            GA4: open a report (Pages, or Traffic acquisition), Share › Download file › CSV. Search Console: Performance
            (and Performance › Generative AI), Export › Download CSV, unzip, upload Queries.csv or Pages.csv.
          </p>
          {uploads.map((u) => (
            <div key={`${u.kind}-${u.filename}`} className="res-upload-card">
              <p className="so-meta">
                <span className="badge">{UPLOAD_KINDS[u.kind]}</span>
                <span>{u.filename}</span>
                <span>uploaded {day(u.uploaded_at)}</span>
                <span>{u.row_count} rows</span>
              </p>
              {Object.keys(u.totals).length > 0 && (
                <p className="res-totals">
                  {Object.entries(u.totals).map(([k, v]) => <span key={k}><strong>{n(v)}</strong> {k}</span>)}
                </p>
              )}
              <Table head={u.header} rows={u.rows} />
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

function Table({ head, rows }: { head: string[]; rows: React.ReactNode[][] }) {
  return (
    <div className="res-scroll">
      <table className="res-table">
        <thead>
          <tr>{head.map((h, i) => <th key={i} scope="col">{h}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{r.map((c, j) => <td key={j}>{c}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
