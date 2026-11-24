"""The AI looks at the results and suggests what to answer next, and why. It only suggests: a person picks one by
selecting the question on the dashboard (the same Select button as Level 2)."""
from pathlib import Path

from psycopg.types.json import Jsonb

from core.db import get_conn
from core.llm.client import llm
from social.social import fill
from stats.stats import parse_suggestion

PROMPT = (Path(__file__).parent / "prompts" / "suggest.txt").read_text(encoding="utf-8")
CANDIDATES = 15     # best-ranked open questions the AI may choose from
EXPORT_ROWS = 15    # top rows of each uploaded export shown to the AI (keeps the prompt inside free limits)


def _lines(rows, empty):
    return "\n".join(rows) or empty


def gather(conn):
    """Everything the prompt needs, as text, plus the ids the AI is allowed to pick."""
    published = [t for (t,) in conn.execute("SELECT d.title FROM pages p JOIN final_drafts d ON d.id = p.draft_id")]
    posts = [f"- {t}: {likes}, {reposts}, {replies}, {quotes}" for t, likes, reposts, replies, quotes in conn.execute(
        "SELECT d.title, po.likes, po.reposts, po.replies, po.quotes FROM posts po JOIN pages pg ON pg.id = po.page_id "
        "JOIN final_drafts d ON d.id = pg.draft_id WHERE po.status = 'sent'")]
    traffic = [f"- {path}: {n} {kind} visits" for path, kind, n in conn.execute(
        "SELECT path, kind, sum(count) FROM hits WHERE day > current_date - 30 GROUP BY path, kind ORDER BY 3 DESC LIMIT 15")]
    exports = [f"{kind} / {name}:\n" + "\n".join(",".join(r) for r in [header] + rows[:EXPORT_ROWS])
               for kind, name, header, rows in conn.execute("SELECT kind, filename, header, rows FROM uploads ORDER BY uploaded_at DESC LIMIT 4")]
    candidates = conn.execute(
        "SELECT id, text, score FROM questions WHERE status = 'new' AND merged_into IS NULL AND score IS NOT NULL "
        "ORDER BY score DESC LIMIT %s", (CANDIDATES,)).fetchall()
    values = {
        "published": _lines([f"- {t}" for t in published], "(none yet)"),
        "posts": _lines(posts, "(no posts sent yet)"),
        "ai_traffic": _lines(traffic, "(none recorded yet)"),
        "exports": _lines(exports, "(nothing uploaded yet)"),
        "candidates": _lines([f"[{i}] {' '.join(t.split())[:200]} ({s:.1f})" for i, t, s in candidates], "(none)"),
    }
    return values, {i for i, _, _ in candidates}


def suggest():
    """Ask the LLM, store its suggestion, return it. Raises RuntimeError if every LLM is busy, ValueError if its
    reply can't be used, LookupError if there is nothing to choose from."""
    with get_conn() as conn:
        values, valid_ids = gather(conn)
    if not valid_ids:
        raise LookupError("no ranked questions left to choose from: collect and rank more first")
    result = parse_suggestion(llm(fill(PROMPT, values)), valid_ids)
    with get_conn() as conn:
        conn.execute("INSERT INTO suggestions (insight, picks) VALUES (%s, %s)", (result["insight"], Jsonb(result["picks"])))
    return result


if __name__ == "__main__":  # print the prompt as it would be sent, for the write-up
    with get_conn() as c:
        print(fill(PROMPT, gather(c)[0]))
