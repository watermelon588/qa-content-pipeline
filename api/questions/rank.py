"""Ask the LLM to score each new question and spot near-duplicates. Saves the score and the reason."""
import json
import re
import time
from pathlib import Path

from core.db import get_conn
from core.llm.client import TIME_LIMIT, llm

# The prompt lives in its own file so it is easy to read, change and paste into the write-up.
PROMPT = (Path(__file__).parent / "prompts" / "rank.txt").read_text(encoding="utf-8")

BATCH = 20         # questions per LLM call (one collect run adds at most 20, so usually one call)
MAX_BATCHES = 5    # calls per run, so one run can't go on forever
# ponytail: duplicates are only spotted within one batch. A new question that repeats one ranked in an
# earlier run is not merged. Add the top-ranked existing questions to the prompt if that matters.


def _resolve_duplicates(dup):
    """dup maps id -> the id it duplicates. Follow chains (A->B->C becomes A->C); drop loops (A->B->A)."""
    resolved = {}
    for start in dup:
        seen, target = {start}, dup[start]
        while target in dup and target not in seen:
            seen.add(target)
            target = dup[target]
        resolved[start] = None if target in seen else target
    return resolved


def parse_ranking(raw, valid_ids):
    """Turn the LLM's reply into clean rows [{id, score, reason, duplicate_of}].
    The reply is untrusted: anything unusable is skipped, so a bad reply can't corrupt the table."""
    # The reply is {"ranking": [...]} (JSON mode only allows an object). From the first "[" to the last "]" is the
    # list, which also tolerates a bare list, ```json fences and chatter around it.
    match = re.search(r"\[.*\]", raw, re.S)
    if not match:
        raise ValueError("the LLM reply has no JSON list")
    try:
        items = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"the LLM reply is not valid JSON: {e}") from e

    rows = {}
    dup = {}
    for item in items:
        try:
            qid, score = int(item["id"]), float(item["score"])
        except (KeyError, TypeError, ValueError):
            continue
        if qid not in valid_ids or qid in rows:  # unknown id, or the same id twice
            continue
        rows[qid] = {"id": qid, "score": min(max(score, 0.0), 10.0), "reason": str(item.get("reason", ""))[:300]}
        try:
            target = int(item.get("duplicate_of"))
        except (TypeError, ValueError):
            continue
        if target in valid_ids and target != qid:
            dup[qid] = target

    resolved = _resolve_duplicates(dup)
    return [{**row, "duplicate_of": resolved.get(row["id"])} for row in rows.values()]


def _rank_batch(conn, deadline):
    """Rank the next unranked questions. Returns (saved, merged)."""
    unranked = conn.execute("SELECT id, text FROM questions WHERE score IS NULL ORDER BY id LIMIT %s", (BATCH,)).fetchall()
    if not unranked:
        return 0, 0
    listing = "\n".join(f"[{qid}] {' '.join(text.split())[:200]}" for qid, text in unranked)
    raw = llm(PROMPT.replace("{questions}", listing), json=True, best=True, deadline=deadline)
    rows = parse_ranking(raw, {qid for qid, _ in unranked})
    for row in rows:
        conn.execute(
            "UPDATE questions SET score = %s, rank_reason = %s, merged_into = %s WHERE id = %s",
            (row["score"], row["reason"], row["duplicate_of"], row["id"]),
        )
    conn.commit()  # keep this batch even if a later one fails
    return len(rows), sum(1 for row in rows if row["duplicate_of"])


def rank():
    """Rank every unranked question, one batch at a time. Returns a summary."""
    ranked = merged = 0
    error = None
    deadline = time.monotonic() + TIME_LIMIT  # all batches share one time limit (Vercel stops at 300 s)
    with get_conn() as conn:
        for _ in range(MAX_BATCHES):
            try:
                saved, dups = _rank_batch(conn, deadline)
            except RuntimeError as e:  # every model failed. Full errors go to the log (they name our accounts).
                print(e)
                error = "every AI model was busy. Wait a minute and rank again"
                break
            except ValueError as e:    # a reply we couldn't use
                error = str(e)[:300]
                break
            if saved == 0:  # nothing left, or the reply gave us nothing usable: stop, don't loop
                break
            ranked += saved
            merged += dups
    return {"ranked": ranked, "merged": merged, **({"error": error} if error else {})}
