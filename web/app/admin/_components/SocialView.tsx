// The Bluesky screen (/admin?view=social). Top to bottom, in the order things need you:
//   1. replies and mentions with the AI's suggested answer: you edit and send, or don't reply;
//   2. one post per published answer: the AI writes it, you edit it and pick when it goes out;
//   3. what has already been answered.
// As everywhere on the desk, only the ONE next thing to press is yellow.
import ActionForm from "@/components/ActionForm";
import { checkBluesky, decideReply, schedulePost, writePost } from "../_lib/actions";
import { bskyUrl, istInput, type SocialPost, type SocialReply } from "../_lib/api";

const day = (iso: string) =>
  new Date(iso).toLocaleString("en-IN", { timeZone: "Asia/Kolkata", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

export default function SocialView({ ready, posts, replies }: { ready: boolean; posts: SocialPost[]; replies: SocialReply[] }) {
  const waiting = replies.filter((r) => r.status === "drafted");
  const unsuggested = replies.filter((r) => r.status === "fetched").length;
  const done = replies.filter((r) => r.status === "sent" || r.status === "discarded");

  // The one yellow button: answer people first, then schedule a written post, then write one, else check Bluesky.
  const next = waiting[0]
    ? `reply-${waiting[0].id}`
    : posts.find((p) => p.status === "drafted" || p.status === "failed")?.slug ?? posts.find((p) => !p.post_id)?.slug ?? "check";
  const yellow = (key: string, extra = "") => `btn ${next === key ? "btn--primary" : ""} ${extra}`.trim();

  return (
    <>
      <section className="band--sea band--rule-bottom">
        <div className="wrap ov">
          <h1 className="ov-title">Bluesky</h1>
          <p className="so-lede">
            The AI writes a post for each published answer and suggests answers to people who reply to or mention us.
            Nothing goes out until you schedule the post or send the reply. No follows, likes or reposts, ever.
          </p>
          {!ready && (
            <p className="adm-problem">
              Bluesky isn&apos;t connected yet. Add <code>BLUESKY_HANDLE</code> and <code>BLUESKY_APP_PASSWORD</code> to{" "}
              <code>api/.env</code>, run <code>python -m social.setup</code> once, and restart the API.
            </p>
          )}
          <ActionForm action={checkBluesky} label="Check Bluesky now" pendingLabel="Checking…" buttonClassName={yellow("check")} />
          <p className="df-help">Sends posts whose time has come, fetches new replies and mentions, and suggests answers. The scheduler will do this on its own once the API is online.</p>
        </div>
      </section>

      <section className="wrap ov-list" aria-labelledby="replies-h">
        <div className="ov-list__head">
          <h2 id="replies-h">Replies waiting for you</h2>
          <p>{waiting.length} to answer{unsuggested ? `, ${unsuggested} still waiting for a suggestion (check again)` : ""}.</p>
        </div>
        {waiting.length === 0 ? (
          <p className="empty">No one is waiting for an answer.</p>
        ) : (
          <ol className="so-list">
            {waiting.map((r) => (
              <li key={r.id} className="so-item">
                <p className="so-meta">
                  <span className="badge">{r.reason === "reply" ? "Replied to us" : "Mentioned us"}</span>
                  <span>{day(r.created_at)}</span>
                  <a href={bskyUrl(r.their_uri)} target="_blank" rel="noreferrer">Open on Bluesky ↗</a>
                </p>
                <blockquote className="fact-quote so-their">{r.their_text}</blockquote>
                <ActionForm action={decideReply} className="so-form" label="Send this reply" pendingLabel="Sending…" buttonClassName={yellow(`reply-${r.id}`)}>
                  <input type="hidden" name="reply_id" value={r.id} />
                  <input type="hidden" name="send" value="yes" />
                  <label className="so-field">
                    <span className="df-label">Our answer (the AI&apos;s suggestion; change anything, 300 characters at most)</span>
                    <textarea name="text" className="df-input" rows={4} defaultValue={r.draft ?? ""} />
                  </label>
                </ActionForm>
                <ActionForm action={decideReply} label="Don't reply" pendingLabel="Saving…" buttonClassName="btn btn--small">
                  <input type="hidden" name="reply_id" value={r.id} />
                  <input type="hidden" name="send" value="no" />
                </ActionForm>
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="ov-list--ranked">
        <div className="wrap ov-list" aria-labelledby="posts-h">
          <div className="ov-list__head">
            <h2 id="posts-h">Posts</h2>
            <p>One per published answer. Times are India time.</p>
          </div>
          {posts.length === 0 ? (
            <p className="empty">No published answers yet. Each one gets a post here once it&apos;s live.</p>
          ) : (
            <ol className="so-list">
              {posts.map((p) => (
                <li key={p.slug} className="so-item">
                  <p className="so-meta">
                    <span className="badge">{p.status ?? "no post yet"}</span>
                    <a href={`/q/${p.slug}`} target="_blank" rel="noreferrer">{p.title} ↗</a>
                  </p>
                  {!p.post_id && (
                    <ActionForm action={writePost} label="Write a post" pendingLabel="Writing…" buttonClassName={yellow(p.slug)}>
                      <input type="hidden" name="slug" value={p.slug} />
                    </ActionForm>
                  )}
                  {p.post_id && p.status !== "sent" && (
                    <>
                      {p.error && <p className="so-error">Last try failed: {p.error}</p>}
                      <ActionForm action={schedulePost} className="so-form" label={p.status === "scheduled" ? "Save changes" : "Schedule"} pendingLabel="Saving…" buttonClassName={yellow(p.slug)}>
                        <input type="hidden" name="post_id" value={p.post_id} />
                        <label className="so-field">
                          <span className="df-label">Post (300 characters at most; a card linking to the answer is added)</span>
                          <textarea name="text" className="df-input" rows={4} defaultValue={p.text ?? ""} />
                        </label>
                        <label className="so-field so-when">
                          <span className="df-label">Send at (empty = at the next check)</span>
                          <input type="datetime-local" name="send_at" className="df-input" defaultValue={istInput(p.send_at)} />
                        </label>
                      </ActionForm>
                      {p.status === "scheduled" && p.send_at && <p className="df-help">Goes out at the first check after {day(p.send_at)}.</p>}
                      {p.status === "drafted" && (
                        <ActionForm action={writePost} label="Write it again" pendingLabel="Writing…" buttonClassName="btn btn--small">
                          <input type="hidden" name="slug" value={p.slug} />
                        </ActionForm>
                      )}
                    </>
                  )}
                  {p.status === "sent" && (
                    <>
                      <p className="so-text">{p.text}</p>
                      <p className="df-help">
                        Sent {p.sent_at && day(p.sent_at)}. {p.uri && <a href={bskyUrl(p.uri)} target="_blank" rel="noreferrer">See it on Bluesky ↗</a>}
                      </p>
                    </>
                  )}
                </li>
              ))}
            </ol>
          )}
        </div>
      </section>

      {done.length > 0 && (
        <section className="wrap ov-list" aria-labelledby="done-h">
          <div className="ov-list__head">
            <h2 id="done-h">Answered</h2>
            <p>The AI&apos;s suggestion is kept next to what was sent.</p>
          </div>
          <ol className="so-list">
            {done.map((r) => (
              <li key={r.id} className="so-item so-item--done">
                <p className="so-meta">
                  <span className="badge">{r.decision === "rejected" ? "not answered" : r.decision}</span>
                  <a href={bskyUrl(r.their_uri)} target="_blank" rel="noreferrer">Their post ↗</a>
                  {r.our_uri && <a href={bskyUrl(r.our_uri)} target="_blank" rel="noreferrer">Our reply ↗</a>}
                </p>
                <p className="so-text">{r.their_text}</p>
                {r.final_text && <p className="so-text"><strong>We said:</strong> {r.final_text}</p>}
                {r.decision === "edited" && <p className="df-help">The AI suggested: {r.draft}</p>}
              </li>
            ))}
          </ol>
        </section>
      )}
    </>
  );
}
