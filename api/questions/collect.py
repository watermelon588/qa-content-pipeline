"""Run every question source and save the new questions. Safe to run again: known questions are skipped."""
from core.db import get_conn
from questions.sources import SOURCES

PER_RUN = 20  # new questions per run, shared equally by the sources. We publish 8 to 10 answers, so 20 well-ranked
              # questions a run is plenty; the next run picks up where this one stopped (saved ones are skipped).


def collect():
    """Return {source: {"found": n, "new": n}} per source, or {"error": ...} if that source failed.
    One source failing does not stop the others."""
    report = {}
    share = PER_RUN // len(SOURCES)
    with get_conn() as conn:
        for name, fetch in SOURCES.items():
            try:
                items = fetch()
            except Exception as e:  # network down, quota used up, API changed: report it and carry on
                report[name] = {"error": f"{type(e).__name__}: {e}"[:150]}
                continue
            new = 0
            for item in items:  # each source returns its most relevant first, so the cap keeps the best
                if new >= share:
                    break
                # The unique index on source_url makes this skip a question we already have.
                cur = conn.execute(
                    "INSERT INTO questions (text, source, source_url) VALUES (%s, %s, %s) "
                    "ON CONFLICT (source_url) DO NOTHING",
                    (item["text"], name, item["source_url"]),
                )
                new += cur.rowcount
            report[name] = {"found": len(items), "new": new}
    return report
