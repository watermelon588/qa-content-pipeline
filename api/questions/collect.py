"""Run every question source and save the new questions. Safe to run again: known questions are skipped."""
from core.db import get_conn
from questions.sources import SOURCES


def collect():
    """Return {source: {"found": n, "new": n}} per source, or {"error": ...} if that source failed.
    One source failing does not stop the others."""
    report = {}
    with get_conn() as conn:
        for name, fetch in SOURCES.items():
            try:
                items = fetch()
            except Exception as e:  # network down, quota used up, API changed: report it and carry on
                report[name] = {"error": f"{type(e).__name__}: {e}"[:150]}
                continue
            new = 0
            for item in items:
                # The unique index on source_url makes this skip a question we already have.
                cur = conn.execute(
                    "INSERT INTO questions (text, source, source_url) VALUES (%s, %s, %s) "
                    "ON CONFLICT (source_url) DO NOTHING",
                    (item["text"], name, item["source_url"]),
                )
                new += cur.rowcount
            report[name] = {"found": len(items), "new": new}
    return report
