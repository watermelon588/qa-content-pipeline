"""Endpoints for the expert check.
- POST /drafts/{id}/send needs the admin secret, and names the expert the link is for.
- GET and POST /review/{token} need TWO things: the link's code (which answer; works once, expires) and the
  assigned expert's personal code in the X-Expert-Code header (who is reviewing). The web page keeps the personal
  code in a cookie and forwards it; the check itself happens here, on every request.
- GET /experts lists the reviewers' public names (for the desk and the About page)."""
import time

from fastapi import APIRouter, Depends, Header, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

from core.auth import require_secret
from core.config import SITE_URL
from core.db import get_conn
from core.status import check_move
from review.experts import EXPERTS, codes, who
from review.review import FIELDS, LINK_DAYS, check_decision, email_ready, hash_token, new_token, review_email, send_email

router = APIRouter()


class Decision(BaseModel):
    decision: str      # approved | edited | rejected
    body: str | None = None              # the expert's edited answer (only used for 'edited')
    title: str | None = None             # ... and title, search-result text, image description
    meta_description: str | None = None
    alt_text: str | None = None
    advice: str = ""   # 2-3 lines of first-hand advice
    note: str = ""     # why, for a rejection


class SendTo(BaseModel):
    expert: str        # "sanath" or "prince": the only person whose code will open this link


@router.get("/experts")
def list_experts():
    """{"sanath": "Sanath W, Senior DevOps Engineer", ...}. Public: these names appear on the pages anyway."""
    return EXPERTS


@router.post("/drafts/{draft_id}/send", dependencies=[Depends(require_secret)])
def send_to_expert(draft_id: int, request: SendTo):
    """Make a fresh one-time link for a pre-checked draft, assigned to one expert, and email it."""
    if request.expert not in EXPERTS:
        raise HTTPException(status_code=422, detail=f"expert must be one of {', '.join(EXPERTS)}")
    if request.expert not in codes():
        raise HTTPException(status_code=409, detail=f"{request.expert} has no code yet: add it to EXPERT_CODES")
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
            "INSERT INTO reviews (draft_id, token_hash, expires_at, expert) "
            "VALUES (%s, %s, now() + make_interval(days => %s), %s)",
            (draft_id, token_hash, LINK_DAYS, request.expert),
        )
        conn.execute("UPDATE drafts SET status = 'in_review' WHERE id = %s", (draft_id,))

    # The link always goes back to the admin screen too, so it can be copied whether or not the email arrived.
    link = f"{SITE_URL}/review/{token}"
    name = EXPERTS[request.expert]
    if not email_ready():  # no Resend key or address yet
        return {"emailed": False, "link": link, "expert": name}
    try:
        print("review email sent, resend id", send_email(*review_email(title, link, questions, name)))
    except OSError as e:   # Resend down or refused: the link still works
        print("review email failed:", e)
        return {"emailed": False, "link": link, "expert": name,
                "error": "the email could not be sent, so here is the link to send yourself"}
    return {"emailed": True, "link": link, "expert": name}


def _load(conn, token):
    """The review row and its draft for this link code, or None."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT r.id AS review_id, r.decision, r.expires_at < now() AS expired, r.expert, d.id AS draft_id, d.status, "
            "d.title, d.body, d.meta_description, d.alt_text, d.expert_questions "
            "FROM reviews r JOIN drafts d ON d.id = r.draft_id WHERE r.token_hash = %s",
            (hash_token(token),),
        )
        return cur.fetchone()


def _check_expert(review, code):
    """The link's code was right; now the person must be the expert this link was sent to. 401 = not a reviewer code
    at all, 403 = a real reviewer, but this answer belongs to the other one."""
    expert = who(code)
    if expert is None:
        time.sleep(1)  # each wrong guess costs a second
        # ponytail: the wait is per request, not per person. Enough for 8-character codes; add a counter if needed.
        raise HTTPException(status_code=401, detail="that reviewer code is not right")
    if expert != review["expert"]:
        raise HTTPException(status_code=403, detail="this answer was sent to another reviewer")
    return expert


@router.get("/review/{token}")
def read_review(token: str, x_expert_code: str = Header(default="")):
    """What the expert sees: the draft, its facts with their quotes, and our questions for them."""
    with get_conn() as conn:
        review = _load(conn, token)
        if review is None:
            raise HTTPException(status_code=404, detail="this review link is not valid")
        if review["expired"] and not review["decision"]:
            raise HTTPException(status_code=410, detail="this link has expired. Ask for a new one")
        expert = _check_expert(review, x_expert_code)
        conn.execute("UPDATE reviews SET opened_at = now() WHERE id = %s AND opened_at IS NULL", (review["review_id"],))
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT n, claim, source_url, snippet, checked_on FROM facts WHERE draft_id = %s ORDER BY n",
                        (review["draft_id"],))
            facts = cur.fetchall()
    keep = ("decision", "title", "body", "meta_description", "alt_text", "expert_questions")
    return {**{k: review[k] for k in keep}, "facts": facts, "expert": EXPERTS[expert]}


@router.post("/review/{token}")
def decide(token: str, request: Decision, x_expert_code: str = Header(default="")):
    """Record the expert's answer. Works once: the row is locked and must still be unanswered and unexpired."""
    with get_conn() as conn:
        review = _load(conn, token)
        if review is None or review["decision"] or review["expired"]:
            raise HTTPException(status_code=410, detail="this link was already used or has expired")
        _check_expert(review, x_expert_code)
        try:
            edits = {k: getattr(request, k) for k in FIELDS}
            fields = check_decision(request.decision, edits, request.advice, request.note, review)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        check_move("draft", review["status"], fields["decision"])
        # "AND decision IS NULL" makes the save itself one-time: if two answers race, only the first one updates.
        saved = conn.execute(
            "UPDATE reviews SET decision = %s, edited_body = %s, edited_title = %s, edited_meta_description = %s, "
            "edited_alt_text = %s, advice = %s, note = %s, decided_at = now() "
            "WHERE id = %s AND decision IS NULL",
            (fields["decision"], fields["edited_body"], fields["edited_title"], fields["edited_meta_description"],
             fields["edited_alt_text"], fields["advice"], fields["note"], review["review_id"]),
        ).rowcount
        if not saved:
            raise HTTPException(status_code=410, detail="this link was already used")
        conn.execute("UPDATE drafts SET status = %s WHERE id = %s", (fields["decision"], review["draft_id"]))
    return {"decision": fields["decision"]}
