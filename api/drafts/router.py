"""The web addresses (endpoints) of the drafts feature. Same secret as the questions routes."""
from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

from core.auth import require_secret
from core.db import get_conn
from core.status import check_move
from drafts.draft import generate, save_draft
from drafts.sources import gather
from drafts.timeline import timeline

router = APIRouter(dependencies=[Depends(require_secret)])


class PastedText(BaseModel):
    url: str   # where the text came from; becomes the fact's source link
    text: str


class DraftRequest(BaseModel):
    source_urls: list[str] = []            # pages we download
    source_texts: list[PastedText] = []    # pages you copy and paste (JavaScript pages, PDFs, blocked pages)


class PrecheckRequest(BaseModel):
    verified_fact_ids: list[int] = []      # facts you compared with their source and found correct


@router.post("/questions/{question_id}/draft")
def create_draft(question_id: int, request: DraftRequest):
    """Draft an answer to a SELECTED question from the sources you give. Calling it again makes a new version."""
    with get_conn() as conn:
        row = conn.execute("SELECT text, status FROM questions WHERE id = %s", (question_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="no such question")
    text, status = row
    check_move("question", status, "drafted")  # refuses a question nobody has selected

    # The slow part (downloads and LLM calls) runs with no database connection held open.
    try:
        sources = gather(request.source_urls, [p.model_dump() for p in request.source_texts])
        draft = generate(text, sources)
    except ValueError as e:      # a bad address, an empty page, or a draft we could not verify
        raise HTTPException(status_code=422, detail=str(e)) from e
    except RuntimeError as e:    # every LLM failed, twice. The full list of errors goes to the server log only:
        print(e)                 # it names our provider accounts, so it shouldn't reach the screen or a demo video.
        raise HTTPException(
            status_code=502,
            detail="Every AI model was busy or refused the request. Wait a minute and try again. "
            "The full error is in the API's terminal.",
        ) from e
    except OSError as e:         # a download failed (blocked, timed out, not found)
        raise HTTPException(status_code=502, detail=f"could not download a source ({e}). Paste its text instead.") from e

    with get_conn() as conn:
        draft_id, version = save_draft(conn, question_id, draft)
        conn.execute("UPDATE questions SET status = 'drafted' WHERE id = %s", (question_id,))
    return {"draft_id": draft_id, "version": version, "title": draft["title"], "facts": len(draft["facts"])}


@router.get("/drafts")
def list_drafts():
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, question_id, version, title, status FROM drafts ORDER BY id DESC LIMIT 200")
        return cur.fetchall()


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: int):
    """One draft with its facts, for the pre-check."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM drafts WHERE id = %s", (draft_id,))
        draft = cur.fetchone()
        if draft is None:
            raise HTTPException(status_code=404, detail="no such draft")
        cur.execute(
            "SELECT id, n, claim, source_url, snippet, checked_on, verified FROM facts WHERE draft_id = %s ORDER BY n",
            (draft_id,),
        )
        draft["facts"] = cur.fetchall()
        # Level 4: the expert's latest answer (their edit is the AFTER version) and the page, once published.
        cur.execute("SELECT decision, edited_body, advice, note, decided_at FROM reviews "
                    "WHERE draft_id = %s ORDER BY id DESC LIMIT 1", (draft_id,))
        draft["review"] = cur.fetchone()
        cur.execute("SELECT slug FROM pages WHERE draft_id = %s", (draft_id,))
        page = cur.fetchone()
        draft["slug"] = page["slug"] if page else None
        draft["timeline"] = timeline(cur, draft_id)  # when each step happened
        return draft


@router.post("/drafts/{draft_id}/precheck")
def precheck(draft_id: int, request: PrecheckRequest):
    """Tick the facts you checked against their sources. When every fact is ticked, the draft becomes 'prechecked'."""
    with get_conn() as conn:
        row = conn.execute("SELECT status FROM drafts WHERE id = %s", (draft_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such draft")
        check_move("draft", row[0], "prechecked")
        conn.execute(
            "UPDATE facts SET verified = true WHERE draft_id = %s AND id = ANY(%s)", (draft_id, request.verified_fact_ids)
        )
        left = [r[0] for r in conn.execute("SELECT id FROM facts WHERE draft_id = %s AND NOT verified ORDER BY n", (draft_id,))]
        if left:
            return {"status": row[0], "unverified_fact_ids": left}
        conn.execute("UPDATE drafts SET status = 'prechecked', prechecked_at = now() WHERE id = %s", (draft_id,))
    return {"status": "prechecked", "unverified_fact_ids": []}
# Older versions of a draft stay as they are; review/router.py sends only the newest version to the expert.
