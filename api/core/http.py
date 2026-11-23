"""Small helpers to GET a JSON API or a web page. Standard library only, so there is nothing new to install."""
import json
import urllib.parse
import urllib.request
import zlib

# Some APIs refuse Python's default agent name, and well-run ones ask clients to identify themselves.
# A generic name on purpose: no personal details go to outside services.
USER_AGENT = "ai-atlas-india-content-engine"


def _get(url, params=None, timeout=20, limit=None):
    """GET `url` and return (body bytes, headers). `limit` caps how much of a big page we keep."""
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body, headers = response.read(limit), response.headers
    # Stack Exchange guarantees gzip, but sends some errors uncompressed, so look at the bytes, not the header.
    # Source: https://api.stackexchange.com/docs/compression
    # zlib (wbits 31 = gzip) instead of gzip.decompress: it copes with a page we cut off at `limit`,
    # and its max_length stops a tiny file from unpacking into gigabytes. 0 means no cap.
    if body[:2] == b"\x1f\x8b":
        body = zlib.decompressobj(31).decompress(body, (limit or 0) * 4)
    return body, headers


def get_json(url, params=None, timeout=20):
    """GET `url` (with optional query `params`) and return the parsed JSON."""
    body, _ = _get(url, params, timeout)
    return json.loads(body)


def get_text(url, timeout=20, limit=2_000_000):
    """GET a web page and return its HTML as text. Refuses anything that is not a web page (a PDF, an image)."""
    body, headers = _get(url, timeout=timeout, limit=limit)
    kind = headers.get_content_type()
    if not (kind.startswith("text/") or kind == "application/xhtml+xml"):
        raise ValueError(f"{url} is '{kind}', not a web page. Open it, copy the text, and send it as pasted text.")
    return body.decode(headers.get_content_charset() or "utf-8", errors="replace")
