"""Level 5 endpoints. All need the admin secret. Nothing here follows, likes, reposts or sends DMs.
- POST /pages/{slug}/post      the AI writes (or rewrites) the post for one published answer
- POST /posts/{id}/schedule    you approve the text and pick the time it goes out
- POST /jobs/social            send due posts, fetch replies and mentions, suggest answers (the scheduler calls this)
- GET  /social                 everything the admin's Bluesky screen shows
- POST /replies/{id}/decide    you send (as written or edited) or reject a suggested reply"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

from core.auth import require_secret
from core.db import get_conn
from core.status import check_move
from social import bluesky
from social.jobs import draft_replies, fetch_replies, refresh_post_stats, send_due_posts
from social.social import check_text, decision_for, make_post, reply_refs
from social.write import write_post

router = APIRouter(dependencies=[Depends(require_secret)])

BUSY = "Every AI model was busy. Wait a minute and try again. The full error is in the API's terminal."


class Schedule(BaseModel):
    text: str
    send_at: datetime | None = None  # empty = at the next run of the job


class ReplyDecision(BaseModel):
    send: bool        # True: send `text` (the suggestion as it was, or your edit). False: don't reply.
    text: str = ""


def _login():
    if not bluesky.ready():
        raise HTTPException(status_code=503, detail="Bluesky isn't set up: add BLUESKY_HANDLE and BLUESKY_APP_PASSWORD to api/.env")
    try:
        return bluesky.login()
    except OSError as e:
        raise HTTPException(status_code=502, detail=f"could not log in to Bluesky ({e})") from e


@router.post("/pages/{slug}/post")
def draft_post(slug: str):
    """The AI writes a post for one of OUR published answers (the only thing we post about)."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT pg.id, d.title, d.meta_description, r.advice, po.status FROM pages pg "
                    "JOIN final_drafts d ON d.id = pg.draft_id "
                    "JOIN reviews r ON r.draft_id = d.id AND r.decision IN ('approved', 'edited') "
                    "LEFT JOIN posts po ON po.page_id = pg.id WHERE pg.slug = %s", (slug,))
        page = cur.fetchone()
    if page is None:
        raise HTTPException(status_code=404, detail="no published answer with that address")
    if page["status"]:
        check_move("post", page["status"], "drafted")  # a post already sent or scheduled isn't rewritten
    try:
        text = write_post(page)
    except RuntimeError as e:
        print(e)  # the full list of provider errors names our accounts: terminal only
        raise HTTPException(status_code=502, detail=BUSY) from e
    with get_conn() as conn:
        post_id = conn.execute(
            "INSERT INTO posts (page_id, text) VALUES (%s, %s) "
            "ON CONFLICT (page_id) DO UPDATE SET text = EXCLUDED.text RETURNING id", (page["id"], text)).fetchone()[0]
    return {"post_id": post_id, "text": text}


@router.post("/posts/{post_id}/schedule")
def schedule_post(post_id: int, request: Schedule):
    """Approve the post's text (yours or the AI's) and set when it goes out."""
    try:
        text = check_text(request.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    with get_conn() as conn:
        row = conn.execute("SELECT status FROM posts WHERE id = %s", (post_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such post")
        check_move("post", row[0], "scheduled")
        conn.execute("UPDATE posts SET text = %s, send_at = COALESCE(%s, now()), status = 'scheduled', error = NULL "
                     "WHERE id = %s", (text, request.send_at, post_id))
    return {"status": "scheduled"}


@router.post("/jobs/social")
def run_social():
    """The scheduled job. Safe to run often: posts go out once, replies are saved once."""
    session = _login()  # one login per run (Bluesky allows 300 a day)
    try:
        sent = send_due_posts(session)
        new = fetch_replies(session)
        refresh_post_stats(session)
    except OSError as e:
        raise HTTPException(status_code=502, detail=f"Bluesky did not answer ({e})") from e
    try:
        drafted, error = draft_replies(), None
    except RuntimeError as e:
        print(e)
        drafted, error = 0, BUSY
    return {"posts_sent": sent, "new_replies": new, "replies_drafted": drafted, "error": error}


@router.get("/social")
def social_overview():
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT pg.slug, d.title, po.id AS post_id, po.text, po.status, po.send_at, po.uri, po.error, "
                    "po.sent_at FROM pages pg JOIN final_drafts d ON d.id = pg.draft_id "
                    "LEFT JOIN posts po ON po.page_id = pg.id ORDER BY pg.published_at DESC")
        posts = cur.fetchall()
        cur.execute("SELECT id, their_uri, their_text, reason, draft, final_text, decision, status, our_uri, created_at "
                    "FROM replies ORDER BY id DESC LIMIT 100")
        replies = cur.fetchall()
    return {"ready": bluesky.ready(), "posts": posts, "replies": replies}


@router.post("/replies/{reply_id}/decide")
def decide_reply(reply_id: int, request: ReplyDecision):
    """A person's decision on one suggested reply. Only this sends a reply, and only to someone who replied to
    or mentioned us (the only rows that exist)."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        # Lock the row: a double click waits here, then finds it already sent and is refused.
        cur.execute("SELECT * FROM replies WHERE id = %s FOR UPDATE", (reply_id,))
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such reply")
        if not request.send:
            check_move("reply", row["status"], "discarded")
            cur.execute("UPDATE replies SET status = 'discarded', decision = 'rejected', decided_at = now() "
                        "WHERE id = %s", (reply_id,))
            return {"status": "discarded"}

        check_move("reply", row["status"], "sent")
        try:
            text = check_text(request.text)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        session = _login()
        try:
            result = bluesky.create_post(session, make_post(text, reply=reply_refs(row)))
        except OSError as e:
            raise HTTPException(status_code=502, detail=f"Bluesky refused the reply ({e})") from e
        cur.execute("UPDATE replies SET status = 'sent', final_text = %s, decision = %s, our_uri = %s, "
                    "decided_at = now() WHERE id = %s",
                    (text, decision_for(row["draft"], text), result["uri"], reply_id))
    return {"status": "sent", "uri": result["uri"]}
