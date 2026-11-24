"""When each step happened for one draft, oldest first: collected, selected, drafted, facts checked, sent to the
expert, opened by them, their decision, published, posted. Every time already sits in its own table; this query
lines them up. A step that hasn't happened yet (its time is NULL) is left out."""
from review.experts import EXPERTS

TIMELINE_SQL = """
SELECT step, at, expert FROM (
    SELECT 'Question collected' AS step, q.created_at AS at, NULL AS expert FROM drafts d JOIN questions q ON q.id = d.question_id WHERE d.id = %(id)s
    UNION ALL SELECT 'Question selected', q.selected_at, NULL FROM drafts d JOIN questions q ON q.id = d.question_id WHERE d.id = %(id)s
    UNION ALL SELECT 'Draft v' || version || ' written', created_at, NULL FROM drafts WHERE id = %(id)s
    UNION ALL SELECT 'Every fact checked', prechecked_at, NULL FROM drafts WHERE id = %(id)s
    UNION ALL SELECT 'Sent for review to', created_at, expert FROM reviews WHERE draft_id = %(id)s
    UNION ALL SELECT 'Opened with their code by', opened_at, expert FROM reviews WHERE draft_id = %(id)s
    UNION ALL SELECT initcap(decision) || ' by', decided_at, expert FROM reviews WHERE draft_id = %(id)s
    UNION ALL SELECT 'Published', published_at, NULL FROM pages WHERE draft_id = %(id)s
    UNION ALL SELECT 'Posted on Bluesky', po.sent_at, NULL FROM posts po JOIN pages p ON p.id = po.page_id WHERE p.draft_id = %(id)s
) steps WHERE at IS NOT NULL ORDER BY at
"""


def timeline(cur, draft_id):
    """[{"step": "Approved by Sanath W, ...", "at": datetime}, ...] for one draft. `cur` is an open dict_row cursor.
    Review steps name the expert (links sent before experts had codes have none, so they say "the expert")."""
    cur.execute(TIMELINE_SQL, {"id": draft_id})
    return [
        {"step": f"{row['step']} {EXPERTS.get(row['expert'], 'the expert')}" if row["step"].endswith((" to", " by"))
         else row["step"], "at": row["at"]}
        for row in cur.fetchall()
    ]
