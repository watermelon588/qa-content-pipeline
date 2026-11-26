"""Get the provider pages we will draw facts from, as plain text.
You supply the addresses (or paste the text of pages we can't download). The AI sees only this text."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

from core.http import get_text

MAX_SOURCES = 4      # pages per draft
MAX_CHARS = 60_000    # text kept per page: whole provider pages (Google Cloud's GPU pricing page is ~51,000)
TOTAL_CHARS = 120_000 # text kept across ALL pages, about 30,000 tokens. Drafts use FALLBACK_BEST, whose main models
                      # read 1M tokens, so nothing is cut that the facts might need. (Groq, last in that list,
                      # refuses prompts over ~8,000 tokens, so it only helps with short pages.)
MIN_CHARS = 300       # less than this means we got an empty shell, not the real page
# ponytail: a page longer than its share of TOTAL_CHARS is cut at the end. Paste the part you need if that happens.
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

    with ThreadPoolExecutor() as pool:  # download all pages at once: 4 slow pages take 20 s, not 80 s
        texts = list(pool.map(fetch_text, urls))
    sources = [{"url": url, "text": text} for url, text in zip(urls, texts)]
    for page in pasted:
        _check_https(page["url"])
        text = " ".join(page["text"].split())[:MAX_CHARS]
        if not text:
            raise ValueError(f"the pasted text for {page['url']} is empty")
        sources.append({"url": page["url"], "text": text})

    share = min(MAX_CHARS, TOTAL_CHARS // len(sources))  # 1 or 2 pages: 60,000 each. 3: 40,000. 4: 30,000.
    return [{"url": s["url"], "text": s["text"][:share]} for s in sources]
