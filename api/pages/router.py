"""Publishing and the published answers.
- POST /drafts/{id}/publish needs the admin secret.
- GET /pages and GET /pages/{slug} are public: a published answer is public anyway, and the web pages read them."""
import re

from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row

from core.auth import require_secret
from core.config import SITE_URL
from core.db import get_conn
from core.status import check_move
from pages.pages import check_cap, slugify
from review.experts import EXPERTS

router = APIRouter()


@router.post("/drafts/{draft_id}/publish", dependencies=[Depends(require_secret)])
def publish(draft_id: int):
    """Publish an approved (or expert-edited) draft as a page. Refuses the 21st answer."""
    with get_conn() as conn:
        # Lock the pages table for this transaction, so two clicks at once can't both count 19 and both publish.
        conn.execute("LOCK TABLE pages IN SHARE ROW EXCLUSIVE MODE")
        row = conn.execute("SELECT status, title, question_id FROM drafts WHERE id = %s", (draft_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such draft")
        status, title, question_id = row
        check_move("draft", status, "published")  # only 'approved' or 'edited' may publish
        check_cap(conn.execute("SELECT count(*) FROM pages").fetchone()[0])
        if conn.execute("SELECT 1 FROM pages p JOIN final_drafts d ON d.id = p.draft_id WHERE d.question_id = %s",
                        (question_id,)).fetchone():
            raise HTTPException(status_code=409, detail="this question already has a published page")

        # the address comes from the title the expert approved (their edit, if they changed it)
        slug = slugify(conn.execute("SELECT title FROM final_drafts WHERE id = %s", (draft_id,)).fetchone()[0])
        if conn.execute("SELECT 1 FROM pages WHERE slug = %s", (slug,)).fetchone():
            slug = f"{slug}-{draft_id}"  # two answers with the same title still get different addresses
        conn.execute("INSERT INTO pages (draft_id, slug) VALUES (%s, %s)", (draft_id, slug))
        conn.execute("UPDATE drafts SET status = 'published' WHERE id = %s", (draft_id,))
    return {"slug": slug}


@router.get("/pages")
def list_pages():
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT p.slug, d.title, d.meta_description, p.published_at "
                    "FROM pages p JOIN final_drafts d ON d.id = p.draft_id ORDER BY p.published_at DESC")
        return cur.fetchall()


@router.get("/pages/{slug}")
def read_page(slug: str):
    """One published answer: the expert's version if they edited it, its sources, and their advice."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT p.slug, p.published_at, d.id AS draft_id, d.title, d.body, "
            "d.meta_description, d.alt_text, d.json_ld, r.decision, r.advice, r.decided_at, r.expert "
            "FROM pages p JOIN final_drafts d ON d.id = p.draft_id "
            "JOIN reviews r ON r.draft_id = d.id AND r.decision IN ('approved', 'edited') WHERE p.slug = %s",
            (slug,),
        )
        page = cur.fetchone()
        if page is None:
            raise HTTPException(status_code=404, detail="no such page")
        cur.execute("SELECT n, claim, source_url, checked_on FROM facts WHERE draft_id = %s ORDER BY n", (page["draft_id"],))
        cited = {int(n) for n in re.findall(r"\[(\d+)\]", page["body"])}  # the expert may have removed some
        page["facts"] = [f for f in cur.fetchall() if f["n"] in cited]
        # our Bluesky post about this answer, once it has been sent (public anyway, so the home page can link it)
        cur.execute("SELECT po.uri FROM posts po JOIN pages p ON p.id = po.page_id "
                    "WHERE p.slug = %s AND po.status = 'sent'", (slug,))
        post = cur.fetchone()
    page["bluesky_url"] = None
    if post:
        # at://did:plc:abc/app.bsky.feed.post/xyz -> https://bsky.app/profile/did:plc:abc/post/xyz
        _, _, did, _, rkey = post["uri"].split("/")
        page["bluesky_url"] = f"https://bsky.app/profile/{did}/post/{rkey}"
    page["reviewer"] = EXPERTS.get(page.pop("expert"))  # the expert who approved THIS answer (None for older links)

    url = f"{SITE_URL}/q/{page['slug']}"
    page["json_ld"] = {**page["json_ld"], "headline": page["title"], "description": page["meta_description"],
                       "url": url, "mainEntityOfPage": url,
                       "datePublished": page["published_at"].date().isoformat()}  # known only once it's live
    return page
