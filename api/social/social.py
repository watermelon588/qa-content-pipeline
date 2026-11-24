"""The rules of Level 5 as small functions with no network and no database, so tests/test_social.py can check them.
- Posts and replies fit Bluesky's 300-character limit.
- Links are made clickable (Bluesky needs their position in BYTES, not characters).
- We only ever answer replies and mentions, never our own posts, and a reply points at the right thread."""
import re

MAX_TEXT = 300  # Bluesky's limit is 300 graphemes (what you see as characters)
ANSWERABLE = ("reply", "mention")  # Bluesky's notification reasons we may respond to (the guide's rule)


def check_text(text):
    """The text to send, tidied, or ValueError saying what's wrong.
    ponytail: len() counts code points, which is never fewer than graphemes, so this can only be stricter than Bluesky."""
    text = text.replace("\r\n", "\n").strip()
    if not text:
        raise ValueError("the text is empty")
    if len(text) > MAX_TEXT:
        raise ValueError(f"the text is {len(text)} characters; Bluesky allows {MAX_TEXT}")
    return text


def link_facets(text):
    """Mark every https:// address in the text as a link. Bluesky wants UTF-8 byte positions, so a "₹" or an emoji
    before the link (several bytes each) would otherwise shift the link onto the wrong letters."""
    facets = []
    for m in re.finditer(r"https?://\S+", text):
        url = m.group().rstrip(".,;:!?)\"'")  # a full stop after a link isn't part of it
        start = len(text[: m.start()].encode())
        facets.append({
            "index": {"byteStart": start, "byteEnd": start + len(url.encode())},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
        })
    return facets


def make_post(text, card=None, reply=None):
    """A post record: the text, clickable links, and optionally a link card or the thread it answers."""
    record = {"text": text}
    if facets := link_facets(text):
        record["facets"] = facets
    if card:
        record["embed"] = card
    if reply:
        record["reply"] = reply
    return record


def page_card(slug, title, description, site_url):
    """The preview box (title and summary) Bluesky shows under a post, linking to our answer page. The utm tags let
    GA4 count visits from our posts; the page's canonical link stays the plain address."""
    return {"$type": "app.bsky.embed.external",
            "external": {"uri": f"{site_url}/q/{slug}?utm_source=bluesky&utm_medium=social", "title": title, "description": description}}


def to_answer(notifications, our_did):
    """Turn Bluesky notifications into rows for the replies table: only replies and mentions, never our own posts.
    Keeps only what a reply needs (their post's address, its text, and the thread's first post), no names."""
    rows = []
    for n in notifications:
        if n["reason"] not in ANSWERABLE or n["author"]["did"] == our_did:
            continue
        parent = {"uri": n["uri"], "cid": n["cid"]}
        # Replies point at the thread's first post (root) and the post they answer (parent). If their post is
        # itself a reply, its root is the thread's root; if not, their post starts the thread.
        root = n["record"].get("reply", {}).get("root", parent)
        rows.append({"their_uri": parent["uri"], "their_cid": parent["cid"], "root_uri": root["uri"],
                     "root_cid": root["cid"], "their_text": n["record"].get("text", ""), "reason": n["reason"]})
    return rows


def reply_refs(row):
    """The "reply" field for our answer to a stored row from to_answer()."""
    return {"root": {"uri": row["root_uri"], "cid": row["root_cid"]},
            "parent": {"uri": row["their_uri"], "cid": row["their_cid"]}}


def decision_for(draft, sent_text):
    """'approved' if the person sent the AI's suggestion as it was, 'edited' if they changed it."""
    return "approved" if (draft or "").replace("\r\n", "\n").strip() == sent_text else "edited"


def fill(template, values):
    """Fill {name} blanks in ONE pass, so a blank-like "{context}" inside someone's post stays plain text."""
    return re.sub(r"\{(\w+)\}", lambda m: str(values.get(m.group(1), m.group())), template)


def tidy(llm_text):
    """The LLM sometimes wraps its answer in quotes. Strip them and any spaces."""
    return llm_text.strip().strip('"“”').strip()
