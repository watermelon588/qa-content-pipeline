"""Source: Stack Exchange (technical Q&A sites).

Official API: https://api.stackexchange.com/docs/advanced-search
Limits: https://api.stackexchange.com/docs/throttle
  - Without an app key the daily quota is ~300 requests (the reply's `quota_remaining` showed 299 on
    2026-11-22; the docs' 10,000 is for apps with a key), so keep SITES x QUERIES small.
  - If a reply has a `backoff` number, wait that many seconds before calling the same method again.
"""
import html
import time

from core.http import get_json
from questions.queries import QUERIES

URL = "https://api.stackexchange.com/2.3/search/advanced"
# Sites where people ask about GPUs and cloud servers. Names are the API's `site` values.
SITES = ["ai", "devops", "serverfault", "datascience"]


def fetch():
    """Return a list of {"text": ..., "source_url": ...}, one per question found."""
    found = []
    for site in SITES:
        for query in QUERIES:
            data = get_json(URL, {"site": site, "q": query, "sort": "relevance", "order": "desc", "pagesize": 10})
            for item in data["items"]:
                # Titles come HTML-escaped (&#39; for an apostrophe), so unescape them.
                found.append({"text": html.unescape(item["title"]), "source_url": item["link"]})
            time.sleep(data.get("backoff", 0))
    # ponytail: if one request fails, the whole source fails and the next run retries it. Add
    # per-request retries only if that happens often.
    return found
