"""Which status changes are allowed, in ONE place. Anything else is refused with HTTP 409 (conflict).
This is how the hard rules are enforced: a question can't be drafted until a person has selected it, and a
draft can't go on until every fact is checked, and nothing is published unless the expert approved (or edited) it."""
from fastapi import HTTPException

ALLOWED = {
    "question": {
        "new": {"selected"},
        "selected": {"drafted"},
        "drafted": {"drafted"},  # drafting again makes a new version
    },
    "draft": {
        "draft": {"prechecked"},
        "prechecked": {"in_review"},                                  # sent to the expert
        "in_review": {"in_review", "approved", "edited", "rejected"},  # sending again makes a fresh link
        "approved": {"published"},
        "edited": {"published"},                                      # the expert's own version is their approval
        # 'rejected' and 'published' go nowhere: a rejected answer is redrafted as a new version.
    },
    "post": {
        "drafted": {"drafted", "scheduled"},     # write it again, or set its time
        "scheduled": {"scheduled", "sent", "failed"},   # change its text or time before it goes out
        "failed": {"scheduled"},                 # try again
    },
    "reply": {
        "fetched": {"drafted"},
        "drafted": {"sent", "discarded"},        # only a person's approval sends it
    },
}


def check_move(kind, current, new):
    """Do nothing if `kind` (question, draft, post or reply) may go from `current` to `new`; otherwise raise 409."""
    if new not in ALLOWED[kind].get(current, set()):
        raise HTTPException(status_code=409, detail=f"a {kind} that is '{current}' cannot become '{new}'")
