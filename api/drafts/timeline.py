"""When each step happened for one draft, oldest first: collected, selected, drafted, facts checked, sent to the
expert, their decision, published, posted. Every time already sits in its own table; this query lines them up.
A step that hasn't happened yet (its time is NULL) is left out."""

TIMELINE_SQL = """
SELECT step, at FROM (
    SELECT 'Question collected' AS step, q.created_at AS at FROM drafts d JOIN questions q ON q.id = d.question_id WHERE d.id = %(id)s
    UNION ALL SELECT 'Question selected', q.selected_at FROM drafts d JOIN questions q ON q.id = d.question_id WHERE d.id = %(id)s
    UNION ALL SELECT 'Draft v' || version || ' written', created_at FROM drafts WHERE id = %(id)s
    UNION ALL SELECT 'Every fact checked', prechecked_at FROM drafts WHERE id = %(id)s
    UNION ALL SELECT 'Sent to the expert', created_at FROM reviews WHERE draft_id = %(id)s
    UNION ALL SELECT 'Expert ' || decision, decided_at FROM reviews WHERE draft_id = %(id)s
    UNION ALL SELECT 'Published', published_at FROM pages WHERE draft_id = %(id)s
    UNION ALL SELECT 'Posted on Bluesky', po.sent_at FROM posts po JOIN pages p ON p.id = po.page_id WHERE p.draft_id = %(id)s
) steps WHERE at IS NOT NULL ORDER BY at
"""


def timeline(cur, draft_id):
    """[{"step": "Published", "at": datetime}, ...] for one draft. `cur` is an open dict_row cursor."""
    cur.execute(TIMELINE_SQL, {"id": draft_id})
    return cur.fetchall()
