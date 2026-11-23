"""Publishing rules: the 20-answer cap and the page address (slug)."""
import re

from fastapi import HTTPException

MAX_PAGES = 20  # the guide's hard limit on published answers, in total, ever. We aim for 8 to 10.


def check_cap(published):
    """Raise 409 if `published` answers are already live, so the 21st can never go out."""
    if published >= MAX_PAGES:
        raise HTTPException(status_code=409, detail=f"the limit of {MAX_PAGES} published answers is reached")


def slugify(title):
    """'What does an H100 cost in India?' -> 'what-does-an-h100-cost-in-india'. At most 80 characters."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if len(slug) > 80:
        slug = slug[:80].rsplit("-", 1)[0]  # cut at a word, not mid-word
    return slug or "answer"
