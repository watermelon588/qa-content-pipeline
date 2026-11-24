"""The expert check: a one-time secret link, the expert's decision, and the email that carries the link.
The expert never logs in. Whoever holds the link can review that one draft, once, until it expires."""
import hashlib
import html
import json
import secrets
import urllib.request
from pathlib import Path
from string import Template

from core.config import EXPERT_EMAIL, MAIL_FROM, RESEND_API_KEY
from core.http import USER_AGENT

LINK_DAYS = 14         # a link older than this stops working; send again for a fresh one
MAX_ADVICE = 2000      # characters of first-hand advice
MAX_BODY = 20_000      # same limit as the AI's draft body
DECISIONS = ("approved", "edited", "rejected")


def hash_token(token):
    """The database keeps only this fingerprint, so a leaked table can't be turned back into working links."""
    return hashlib.sha256(token.encode()).hexdigest()


def new_token():
    """A fresh link code (256 random bits, URL-safe) and its fingerprint for the database."""
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)


# What the expert may edit. A field they leave as the AI wrote it is not stored (it stays NULL = unchanged).
FIELDS = ("body", "title", "meta_description", "alt_text")
LIMITS = {"body": MAX_BODY, "title": 120, "meta_description": 300, "alt_text": 300}
LABELS = {"body": "answer", "title": "title", "meta_description": "search-result text", "alt_text": "image description"}


def check_decision(decision, edits, advice, note, original):
    """Validate what the expert sent. Returns the fields to save, or raises ValueError saying what is wrong.
    `edits` is what the expert's form held for each of FIELDS (a missing one counts as unchanged); `original` is the
    AI's draft with the same keys. 'edited' keeps only the fields they really changed as the AFTER version; the AI's
    draft stays untouched as the BEFORE version."""
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {', '.join(DECISIONS)}")
    advice, note = advice.strip(), note.strip()
    if len(advice) > MAX_ADVICE or len(note) > MAX_ADVICE:
        raise ValueError(f"advice and notes are limited to {MAX_ADVICE} characters")
    if decision == "rejected" and not note:
        raise ValueError("please say why, so the next version can fix it")

    changed = {}
    if decision == "edited":
        for key in FIELDS:
            if edits.get(key) is None:
                continue
            # Browsers send a textarea's line breaks as \r\n; without this, untouched text would count as an edit.
            new = edits[key].replace("\r\n", "\n").strip()
            if new != original[key].replace("\r\n", "\n").strip():
                changed[key] = new
        if not changed:
            raise ValueError("an edit needs a change. To keep the draft as it is, choose approve")
        for key, new in changed.items():
            if not new:
                raise ValueError(f"the {LABELS[key]} can't be empty")
            if len(new) > LIMITS[key]:
                raise ValueError(f"the {LABELS[key]} is limited to {LIMITS[key]} characters")
    return {
        "decision": decision,
        **{f"edited_{key}": changed.get(key) for key in FIELDS},
        "advice": advice or None,
        "note": note or None,
    }


EMAIL = Template((Path(__file__).parent / "email.html").read_text(encoding="utf-8"))
QUESTIONS_ROW = """  <tr><td style="padding:16px 28px 8px;font:400 15px/1.6 -apple-system,'Segoe UI',Roboto,Arial,sans-serif;color:#0f1b2d;">
    <p style="margin:0 0 8px;font:500 11px ui-monospace,Menlo,Consolas,monospace;letter-spacing:0.08em;text-transform:uppercase;color:#43536b;">We&rsquo;d value your view on</p>
    <ul style="margin:0;padding-left:20px;">$items</ul>
  </td></tr>
"""


def review_email(title, link, questions, expert):
    """Subject, plain text and HTML for the expert. The title and questions come from the AI, so every value is
    escaped before it goes into the HTML (a title can't inject markup or a different link). `expert` is the
    display name of the expert the link is assigned to; the email greets them by first name."""
    first = expert.split()[0]
    asks = "\n".join(f"- {q}" for q in questions)
    text = (
        f"Hello {first},\n\nA new answer is ready for you. Nothing goes live until you approve it.\n\n{title}\n\n"
        f"Review it here (about 10 minutes; the link works once and expires in {LINK_DAYS} days):\n{link}\n\n"
        "The first time, the page asks for your personal reviewer code (we sent it to you separately). "
        "This link is for you only: it opens with your code and no one else's.\n\n"
        "On the page: read everything that will be published (title, search-result text, image description, answer), "
        "check each fact (each links to the provider's page with the quote highlighted), then approve, edit or reject "
        "and add 2-3 lines of your own advice for readers.\n\n"
        + (f"We'd value your view on:\n{asks}\n\n" if questions else "")
        + "Thank you,\nAI Atlas India, GPU and cloud section"
    )
    items = "".join(f'<li style="margin:0 0 6px;">{html.escape(q)}</li>' for q in questions)
    body = EMAIL.substitute(
        title=html.escape(title), link=html.escape(link), days=LINK_DAYS, first=html.escape(first),
        questions=Template(QUESTIONS_ROW).substitute(items=items) if questions else "",
    )
    return f"Please review: {title}", text, body


def email_ready():
    return bool(RESEND_API_KEY and EXPERT_EMAIL)


def send_email(subject, text, body):
    """Send through Resend's API. Docs: https://resend.com/docs/api-reference/emails/send-email
    (POST /emails with a Bearer key; Resend refuses requests that have no User-Agent)."""
    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps({"from": MAIL_FROM, "to": [EXPERT_EMAIL], "subject": subject, "text": text, "html": body}).encode(),
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read())["id"]  # Resend's id for the email, kept in the log only
