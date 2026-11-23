"""What POST /jobs/social does each time the scheduler (or the "Check Bluesky now" button) calls it:
1. send every scheduled post whose time has come;
2. fetch new replies and mentions;
3. let the LLM suggest an answer to a few of them (a person still approves each one in the admin)."""
from psycopg.rows import dict_row

from core.config import SITE_URL
from core.db import get_conn
from social import bluesky
from social.social import make_post, page_card, to_answer
from social.write import write_reply

DRAFTS_PER_RUN = 5  # keeps one run inside the free LLM limits; the rest wait for the next run

PAGE_SQL = ("SELECT pg.slug, d.title, d.meta_description, COALESCE(r.edited_body, d.body) AS body "
            "FROM pages pg JOIN drafts d ON d.id = pg.draft_id "
            "JOIN reviews r ON r.draft_id = d.id AND r.decision IN ('approved', 'edited') ")


def send_due_posts(session):
    """Send each scheduled post whose time has passed. Returns how many went out."""
    with get_conn() as conn:
        due = [r[0] for r in conn.execute("SELECT id FROM posts WHERE status = 'scheduled' AND send_at <= now()")]
    sent = 0
    for post_id in due:
        # One transaction per post. FOR UPDATE SKIP LOCKED: if two runs overlap, only one of them gets the row,
        # so a post can't go out twice.
        with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT po.text, pg.slug, d.title, d.meta_description FROM posts po "
                        "JOIN pages pg ON pg.id = po.page_id JOIN drafts d ON d.id = pg.draft_id "
                        "WHERE po.id = %s AND po.status = 'scheduled' FOR UPDATE OF po SKIP LOCKED", (post_id,))
            row = cur.fetchone()
            if row is None:
                continue
            card = page_card(row["slug"], row["title"], row["meta_description"], SITE_URL)
            try:
                result = bluesky.create_post(session, make_post(row["text"], card=card))
            except OSError as e:
                cur.execute("UPDATE posts SET status = 'failed', error = %s WHERE id = %s", (str(e)[:500], post_id))
                continue
            cur.execute("UPDATE posts SET status = 'sent', uri = %s, sent_at = now(), error = NULL WHERE id = %s",
                        (result["uri"], post_id))
            sent += 1
    return sent


def fetch_replies(session):
    """Save new replies and mentions (ones we have already saved are skipped). Returns how many were new."""
    rows = to_answer(bluesky.notifications(session), session["did"])
    new = 0
    with get_conn() as conn:
        for r in rows:
            new += conn.execute(
                "INSERT INTO replies (their_uri, their_cid, root_uri, root_cid, their_text, reason) "
                "VALUES (%(their_uri)s, %(their_cid)s, %(root_uri)s, %(root_cid)s, %(their_text)s, %(reason)s) "
                "ON CONFLICT (their_uri) DO NOTHING", r).rowcount
    return new


def draft_replies():
    """Ask the LLM for a suggested answer to up to DRAFTS_PER_RUN new replies. Returns how many it drafted.
    Raises RuntimeError if every LLM is busy (the router turns that into a short message)."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, their_text, root_uri FROM replies WHERE status = 'fetched' ORDER BY id LIMIT %s",
                    (DRAFTS_PER_RUN,))
        todo = cur.fetchall()
        cur.execute(PAGE_SQL + "ORDER BY pg.published_at DESC")
        pages = cur.fetchall()
    drafted = 0
    for r in todo:
        with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
            # If they replied under one of our posts, give the LLM that answer; a plain mention gets the list.
            cur.execute(PAGE_SQL + "JOIN posts po ON po.page_id = pg.id WHERE po.uri = %s", (r["root_uri"],))
            page = cur.fetchone()
        text = write_reply(r["their_text"], page, pages)
        with get_conn() as conn:
            conn.execute("UPDATE replies SET draft = %s, status = 'drafted' WHERE id = %s AND status = 'fetched'",
                         (text, r["id"]))
        drafted += 1
    return drafted
