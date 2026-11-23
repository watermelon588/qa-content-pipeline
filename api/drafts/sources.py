"""Get the provider pages we will draw facts from, as plain text.
You supply the addresses (or paste the text of pages we can't download). The AI sees only this text."""
from html.parser import HTMLParser

from core.http import get_text

MAX_SOURCES = 4      # pages per draft
MAX_CHARS = 10_000   # text kept per page
TOTAL_CHARS = 18_000 # text kept across ALL pages. Groq's free plan refuses a request over 7,000-8,000 tokens,
                     # and 18,000 characters plus the prompt is about 6,000 tokens, so every model in the list can answer.
MIN_CHARS = 300      # less than this means we got an empty shell, not the real page
# ponytail: a long page is cut to its share of TOTAL_CHARS, so a price far down the page is lost. Paste the part you need.
# ponytail: any https address is fetched. Fine while only the owner (who holds the secret) can call this.


class _PageText(HTMLParser):
    """Collects the visible text of a page. Scripts, styles and the like are skipped."""
    SKIP = {"script", "style", "noscript", "svg", "template"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skipping += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skipping:
            self.skipping -= 1

    def handle_data(self, data):
        if not self.skipping:
            self.parts.append(data)


def html_to_text(html):
    """Visible text of a page with all spacing squeezed to single spaces."""
    parser = _PageText()
    parser.feed(html)
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def _check_https(url):
    if not url.startswith("https://"):
        raise ValueError(f"{url!r}: only https:// addresses are allowed")


def fetch_text(url):
    """Download one page and return its text. Raises ValueError (with advice) if the page is unusable."""
    _check_https(url)
    text = html_to_text(get_text(url))
    if len(text) < MIN_CHARS:
        raise ValueError(
            f"{url} has almost no readable text (it is probably drawn by JavaScript). "
            "Open it in your browser, copy the text, and send it in source_texts instead."
        )
    return text[:MAX_CHARS]


def gather(urls, pasted):
    """urls: addresses to download. pasted: [{"url", "text"}] for pages we can't download (url is where it came from).
    Returns [{"url", "text"}] ready for the prompt."""
    all_urls = list(urls) + [p["url"] for p in pasted]
    if not 1 <= len(all_urls) <= MAX_SOURCES:
        raise ValueError(f"send between 1 and {MAX_SOURCES} sources")
    if len(set(all_urls)) != len(all_urls):
        raise ValueError("each source address may appear only once")

    sources = [{"url": url, "text": fetch_text(url)} for url in urls]
    for page in pasted:
        _check_https(page["url"])
        text = " ".join(page["text"].split())[:MAX_CHARS]
        if not text:
            raise ValueError(f"the pasted text for {page['url']} is empty")
        sources.append({"url": page["url"], "text": text})

    share = min(MAX_CHARS, TOTAL_CHARS // len(sources))  # 1 page: 10,000. 2: 9,000 each. 3: 6,000. 4: 4,500.
    return [{"url": s["url"], "text": s["text"][:share]} for s in sources]
