"""Source: Hacker News "Ask HN" posts (questions people put to the community).

Search API run by Algolia. The docs page (https://hn.algolia.com/api) is built with JavaScript, so the
endpoint and field names were confirmed by calling it on 2026-11-22; the item types ("ask_hn") and the
fields (title, points, created_at_i) are listed in https://github.com/algolia/hn-search
"""
from core.http import get_json
from questions.queries import QUERIES

URL = "https://hn.algolia.com/api/v1/search"


def fetch():
    """Return a list of {"text": ..., "source_url": ...}, one per Ask HN post found."""
    found = []
    for query in QUERIES:
        data = get_json(URL, {"query": query, "tags": "ask_hn", "hitsPerPage": 10})
        for hit in data["hits"]:
            if not hit.get("title"):
                continue
            found.append({
                "text": hit["title"].removeprefix("Ask HN:").strip(),  # the label is noise once we know the source
                "source_url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
            })
    return found
