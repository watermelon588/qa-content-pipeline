"""The two things the LLM writes for Level 5: a post about one of our answers, and a suggested reply.
Neither is sent by this file. A person edits and schedules every post and approves every reply."""
from pathlib import Path

from core.config import SITE_URL
from core.llm.client import llm
from social.social import fill, tidy

PROMPTS = Path(__file__).parent / "prompts"
POST_PROMPT = (PROMPTS / "post.txt").read_text(encoding="utf-8")
REPLY_PROMPT = (PROMPTS / "reply.txt").read_text(encoding="utf-8")
BODY_CHARS = 2000  # enough of the answer for the LLM to reply from, small enough for the free model limits


def write_post(page):
    """page: title, meta_description, advice (from the published answer)."""
    return tidy(llm(fill(POST_PROMPT, {"title": page["title"], "description": page["meta_description"],
                                       "advice": page["advice"] or ""})))


def write_reply(their_text, page, pages):
    """`page` is the answer their post replied under (or None for a mention); `pages` lists every published answer,
    so a mention can still be pointed at the right one."""
    if page:
        context = (f'Our answer "{page["title"]}" ({SITE_URL}/q/{page["slug"]}):\n'
                   f'{page["body"][:BODY_CHARS]}')
    else:
        context = "\n".join(f'- "{p["title"]}": {SITE_URL}/q/{p["slug"]}' for p in pages) or "(nothing yet)"
    return tidy(llm(fill(REPLY_PROMPT, {"their_text": their_text, "context": context})))
