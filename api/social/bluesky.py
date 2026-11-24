"""The only code that talks to Bluesky. Standard library, no SDK (same as the rest of the API, DECISIONS D20).
It can log in, post, reply, read notifications, read our posts' like/repost counts and label the account as a bot. Nothing else: there is
deliberately no follow, like, repost or DM function (the guide's rules).
Sources (read 22 Nov 2026): https://docs.bsky.app/docs/advanced-guides/posts (post record, link cards, replies)
and the lexicons in github.com/bluesky-social/atproto (packages/api/lexicons/app/bsky/...)."""
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from core.config import BLUESKY_APP_PASSWORD, BLUESKY_HANDLE
from core.http import USER_AGENT

HOST = "https://bsky.social"  # Bluesky's main server; it forwards requests to the right place


def ready():
    return bool(BLUESKY_HANDLE and BLUESKY_APP_PASSWORD)


def _call(name, session=None, body=None, params=None):
    """One XRPC call: GET with `params`, or POST with a JSON `body`. Returns the parsed JSON reply."""
    url = f"{HOST}/xrpc/{name}" + (f"?{urllib.parse.urlencode(params, doseq=True)}" if params else "")
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
    if session:
        headers["Authorization"] = f"Bearer {session['accessJwt']}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as e:  # Bluesky explains errors in the body, e.g. {"error": "RateLimitExceeded"}
        raise OSError(f"Bluesky {name} answered {e.code}: {e.read()[:200].decode(errors='replace')}") from e


def login():
    """Log in with the app password. Bluesky allows only 30 logins per 5 minutes and 300 a day,
    so each job run logs in once and reuses the session for everything it does."""
    return _call("com.atproto.server.createSession", body={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD})


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")  # the format Bluesky's docs use


def create_post(session, record):
    """Publish a post record (see social.make_post). Returns {"uri": ..., "cid": ...}."""
    record = {"$type": "app.bsky.feed.post", "createdAt": _now(), "langs": ["en"], **record}
    return _call("com.atproto.repo.createRecord", session,
                 body={"repo": session["did"], "collection": "app.bsky.feed.post", "record": record})


def notifications(session, limit=50):
    """Our newest notifications, only the replies and mentions (the only people we may answer)."""
    return _call("app.bsky.notification.listNotifications", session,
                 params={"limit": limit, "reasons": ["reply", "mention"]})["notifications"]


def post_counts(session, uris):
    """Like, repost, reply and quote counts for up to 25 of our posts (app.bsky.feed.getPosts takes 25 at most)."""
    return _call("app.bsky.feed.getPosts", session, params={"uris": uris[:25]})["posts"]


def mark_as_bot(session):
    """Add the "bot" self-label to our profile, as Bluesky asks automated accounts to do. Run once (social/setup.py)."""
    where = {"repo": session["did"], "collection": "app.bsky.actor.profile", "rkey": "self"}
    try:
        profile = _call("com.atproto.repo.getRecord", session, params=where)["value"]
    except OSError as e:
        if "RecordNotFound" not in str(e):
            raise  # any other failure: stop, rather than overwrite the profile (name, bio) with an empty one
        profile = {"$type": "app.bsky.actor.profile"}  # a brand-new account has no profile record yet
    profile["labels"] = {"$type": "com.atproto.label.defs#selfLabels", "values": [{"val": "bot"}]}
    _call("com.atproto.repo.putRecord", session, body={**where, "record": profile})
