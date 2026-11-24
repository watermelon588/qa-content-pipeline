"""Level 6 endpoints. All need the admin secret.
- POST /hits           web/proxy.ts reports one AI-crawler or AI-assistant visit (counted per page per day)
- POST /uploads        a GA4 or Search Console CSV export, uploaded by hand on the dashboard
- GET  /stats          everything the dashboard shows
- POST /jobs/suggest   the AI says what the audience responds to and what to answer next (a person picks)"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from core.auth import require_secret
from core.db import get_conn
from stats.stats import parse_csv, totals
from stats.suggest import suggest

router = APIRouter(dependencies=[Depends(require_secret)])

SHOW_ROWS = 10  # rows of each export shown on the dashboard


class Hit(BaseModel):
    kind: Literal["crawler", "referral"]
    name: str = Field(min_length=1, max_length=40)
    path: str = Field(min_length=1, max_length=200)


class Upload(BaseModel):
    kind: Literal["ga4", "gsc", "gsc_ai"]
    filename: str = Field(min_length=1, max_length=120)
    text: str = Field(max_length=2_000_000)  # about 2 MB of CSV


@router.post("/hits")
def add_hit(hit: Hit):
    with get_conn() as conn:
        conn.execute("INSERT INTO hits (kind, name, path, day) VALUES (%s, %s, %s, (now() AT TIME ZONE 'Asia/Kolkata')::date) "
                     "ON CONFLICT (kind, name, path, day) DO UPDATE SET count = hits.count + 1",
                     (hit.kind, hit.name, hit.path))
    return {"ok": True}


@router.post("/uploads")
def add_upload(upload: Upload):
    try:
        header, rows = parse_csv(upload.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"couldn't read that CSV: {e}") from e
    with get_conn() as conn:
        conn.execute("INSERT INTO uploads (kind, filename, header, rows) VALUES (%s, %s, %s, %s) "
                     "ON CONFLICT (kind, filename) DO UPDATE SET header = EXCLUDED.header, rows = EXCLUDED.rows, "
                     "uploaded_at = now()", (upload.kind, upload.filename, header, Jsonb(rows)))
    return {"rows": len(rows)}


@router.get("/stats")
def stats():
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT kind, name, sum(count)::int AS visits FROM hits WHERE day > current_date - 30 "
                    "GROUP BY kind, name ORDER BY visits DESC")
        ai = cur.fetchall()
        cur.execute("SELECT path, sum(count) FILTER (WHERE kind = 'referral')::int AS referrals, "
                    "sum(count) FILTER (WHERE kind = 'crawler')::int AS crawls FROM hits WHERE day > current_date - 30 "
                    "GROUP BY path ORDER BY sum(count) DESC LIMIT 10")
        ai_pages = cur.fetchall()
        cur.execute("SELECT kind, filename, header, rows, uploaded_at FROM uploads ORDER BY uploaded_at DESC")
        uploads = [{**u, "totals": totals(u["header"], u["rows"]), "row_count": len(u["rows"]), "rows": u["rows"][:SHOW_ROWS]}
                   for u in cur.fetchall()]
        cur.execute("SELECT pg.slug, d.title, po.uri, po.sent_at, po.likes, po.reposts, po.replies, po.quotes, po.stats_at "
                    "FROM posts po JOIN pages pg ON pg.id = po.page_id JOIN drafts d ON d.id = pg.draft_id "
                    "WHERE po.status = 'sent' ORDER BY po.likes + po.reposts + po.replies + po.quotes DESC, po.sent_at DESC")
        posts = cur.fetchall()
        published = cur.execute("SELECT count(*) AS n FROM pages").fetchone()["n"]
        cur.execute("SELECT insight, picks, created_at FROM suggestions ORDER BY id DESC LIMIT 1")
        suggestion = cur.fetchone()
        if suggestion:  # add each picked question's text and whether someone has selected it yet
            cur.execute("SELECT id, text, status FROM questions WHERE id = ANY(%s)",
                        ([p["question_id"] for p in suggestion["picks"]],))
            found = {q["id"]: q for q in cur.fetchall()}
            suggestion["picks"] = [{**p, **found[p["question_id"]]} for p in suggestion["picks"] if p["question_id"] in found]
    return {"ai": ai, "ai_pages": ai_pages, "uploads": uploads, "posts": posts, "published": published,
            "suggestion": suggestion}


@router.post("/jobs/suggest")
def run_suggest():
    try:
        return suggest()
    except LookupError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except (RuntimeError, ValueError) as e:
        print(e)  # the full provider errors name our accounts: terminal only
        raise HTTPException(status_code=502, detail="The AI couldn't give a usable answer. Try again in a minute.") from e
