"""The expert check: a one-time secret link, the expert's decision, and the email that carries the link.
The expert never logs in. Whoever holds the link can review that one draft, once, until it expires."""
import hashlib
import html
import json
import secrets
import urllib.request

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


def check_decision(decision, body, advice, note, original):
    """Validate what the expert sent. Returns the fields to save, or raises ValueError saying what is wrong.
    'edited' keeps their new text as the AFTER version; the AI's draft stays untouched as the BEFORE version."""
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of {', '.join(DECISIONS)}")
    # Browsers send a textarea's line breaks as \r\n; without this, untouched text would count as an edit.
    advice, note, body = advice.strip(), note.strip(), body.replace("\r\n", "\n").strip()
    if len(advice) > MAX_ADVICE or len(note) > MAX_ADVICE:
        raise ValueError(f"advice and notes are limited to {MAX_ADVICE} characters")
    if decision == "edited" and (not body or body == original.strip()):
        raise ValueError("an edit needs changed text. To keep the draft as it is, choose approve")
    if decision == "edited" and len(body) > MAX_BODY:
        raise ValueError(f"the edited text is limited to {MAX_BODY} characters")
    if decision == "rejected" and not note:
        raise ValueError("please say why, so the next version can fix it")
    return {
        "decision": decision,
        "edited_body": body if decision == "edited" else None,
        "advice": advice or None,
        "note": note or None,
    }


def review_email(title, link, questions):
    """Subject, plain text and HTML for the expert. The title comes from the AI, so it is escaped for HTML."""
    asks = "\n".join(f"- {q}" for q in questions)
    text = (
        f"Hello,\n\nA new answer is ready for your review: {title}\n\n"
        f"Open it here (the link works once and expires in {LINK_DAYS} days):\n{link}\n\n"
        "You can approve it, edit it, or reject it. Please also add 2-3 lines of your own advice; "
        f"they appear on the page (with your name only if you have agreed to be named).\n\nQuestions we would love your view on:\n{asks}\n\n"
        "Thank you,\nAI Atlas India (GPU and cloud section)"
    )
    items = "".join(f"<li>{html.escape(q)}</li>" for q in questions)
    body = (
        f"<p>Hello,</p><p>A new answer is ready for your review: <strong>{html.escape(title)}</strong></p>"
        f'<p><a href="{html.escape(link)}">Open the review page</a> (works once, expires in {LINK_DAYS} days)</p>'
        "<p>You can approve it, edit it, or reject it. Please also add 2-3 lines of your own advice; "
        f"they appear on the page (with your name only if you have agreed to be named).</p><p>Questions we would love your view on:</p><ul>{items}</ul>"
        "<p>Thank you,<br>AI Atlas India (GPU and cloud section)</p>"
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
