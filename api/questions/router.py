"""The web addresses (endpoints) of the questions feature."""
from fastapi import APIRouter, Depends, HTTPException
from psycopg.rows import dict_row

from core.auth import require_secret
from core.db import get_conn
from core.status import check_move
from questions.collect import collect
from questions.rank import rank

# Every route here needs the secret. (Admin login replaces this for people-facing screens later.)
router = APIRouter(dependencies=[Depends(require_secret)])


@router.post("/jobs/collect")
def run_collect():
    """Fetch new questions from every source and save them."""
    return collect()


@router.post("/jobs/rank")
def run_rank():
    """Score the questions that have no score yet, and mark near-duplicates."""
    return rank()


@router.get("/questions")
def list_questions():
    """Best-scored first; questions not scored yet come last."""
    with get_conn() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, text, source, source_url, score, rank_reason, merged_into, status "
            "FROM questions ORDER BY score DESC NULLS LAST, id LIMIT 200"
        )
        return cur.fetchall()


@router.post("/questions/{question_id}/select")
def select_question(question_id: int):
    """You choose this question to be answered. Only selected questions can be drafted."""
    with get_conn() as conn:
        row = conn.execute("SELECT status, merged_into FROM questions WHERE id = %s", (question_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="no such question")
        status, merged_into = row
        if merged_into is not None:  # answering a duplicate would publish the same page twice
            raise HTTPException(status_code=409, detail=f"this repeats question {merged_into}; select that one")
        check_move("question", status, "selected")
        conn.execute("UPDATE questions SET status = 'selected' WHERE id = %s", (question_id,))
    return {"id": question_id, "status": "selected"}
