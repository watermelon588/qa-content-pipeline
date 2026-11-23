"""Endpoints for the expert check.
- POST /drafts/{id}/send needs the admin secret.
- GET and POST /review/{token} need only the link's code. That code IS the expert's permission: it opens one draft,
  works once, and expires."""
from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

from core.auth import require_secret
from core.config import SITE_URL
from core.db import get_conn
from core.status import check_move
from review.review import LINK_DAYS, check_decision, email_ready, hash_token, new_token, review_email, send_email

router = APIRouter()


class Decision(BaseModel):
    decision: str      # approved | edited | rejected
    body: str = ""     # the expert's edited text (only for 'edited')
    advice: str = ""   # 2-3 lines of first-hand advice
    note: str = ""     # why, for a rejection


@router.post("/drafts/{draft_id}/send", dependencies=[Depends(require_secret)])
def send_to_expert(draft_id: int):
    """Make a fresh one-time link for a pre-checked draft and email it to the expert."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT status, title, expert_questions, version, "
            "(SELECT MAX(version) FROM drafts WHERE question_id = d.question_id) FROM drafts d WHERE id = %s",
            (draft_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such draft")
        status, title, questions, version, newest = row
        if version != newest:
            raise HTTPException(status_code=409, detail=f"only the newest version (v{newest}) can go to the expert")
        check_move("draft", status, "in_review")  # pre-checked first; sending again is allowed

        token, token_hash = new_token()
        # Sending again replaces any earlier unanswered link, so only one link per draft works at a time.
        conn.execute("UPDATE reviews SET expires_at = now() WHERE draft_id = %s AND decision IS NULL", (draft_id,))
        conn.execute(
            "INSERT INTO reviews (draft_id, token_hash, expires_at) VALUES (%s, %s, now() + make_interval(days => %s))",
            (draft_id, token_hash, LINK_DAYS),
        )
        conn.execute("UPDATE drafts SET status = 'in_review' WHERE id = %s", (draft_id,))

    # The link always goes back to the admin screen too, so it can be copied whether or not the email arrived.
    link = f"{SITE_URL}/review/{token}"
    if not email_ready():  # no Resend key or address yet
        return {"emailed": False, "link": link}
    try:
        print("review email sent, resend id", send_email(*review_email(title, link, questions)))
    except OSError as e:   # Resend down or refused: the link still works
        print("review email failed:", e)
        return {"emailed": False, "link": link, "error": "the email could not be sent, so here is the link to send yourself"}
    return {"emailed": True, "link": link}


def _load(conn, token):
    """The review row and its draft for this link code, or None."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT r.id AS review_id, r.decision, r.expires_at < now() AS expired, d.id AS draft_id, d.status, "
            "d.title, d.body, d.meta_description, d.alt_text, d.expert_questions "
            "FROM reviews r JOIN drafts d ON d.id = r.draft_id WHERE r.token_hash = %s",
            (hash_token(token),),
        )
        return cur.fetchone()


@router.get("/review/{token}")
def read_review(token: str):
    """What the expert sees: the draft, its facts with their quotes, and our questions for them."""
    with get_conn() as conn:
        review = _load(conn, token)
        if review is None:
            raise HTTPException(status_code=404, detail="this review link is not valid")
        if review["expired"] and not review["decision"]:
            raise HTTPException(status_code=410, detail="this link has expired. Ask for a new one")
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT n, claim, source_url, snippet, checked_on FROM facts WHERE draft_id = %s ORDER BY n",
                        (review["draft_id"],))
            facts = cur.fetchall()
    keep = ("decision", "title", "body", "meta_description", "alt_text", "expert_questions")
    return {**{k: review[k] for k in keep}, "facts": facts}


@router.post("/review/{token}")
def decide(token: str, request: Decision):
    """Record the expert's answer. Works once: the row is locked and must still be unanswered and unexpired."""
    with get_conn() as conn:
        review = _load(conn, token)
        if review is None or review["decision"] or review["expired"]:
            raise HTTPException(status_code=410, detail="this link was already used or has expired")
        try:
            fields = check_decision(request.decision, request.body, request.advice, request.note, review["body"])
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        check_move("draft", review["status"], fields["decision"])
        # "AND decision IS NULL" makes the save itself one-time: if two answers race, only the first one updates.
        saved = conn.execute(
            "UPDATE reviews SET decision = %s, edited_body = %s, advice = %s, note = %s, decided_at = now() "
            "WHERE id = %s AND decision IS NULL",
            (fields["decision"], fields["edited_body"], fields["advice"], fields["note"], review["review_id"]),
        ).rowcount
        if not saved:
            raise HTTPException(status_code=410, detail="this link was already used")
        conn.execute("UPDATE drafts SET status = %s WHERE id = %s", (fields["decision"], review["draft_id"]))
    return {"decision": fields["decision"]}
