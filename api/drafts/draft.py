"""Ask the LLM to draft an answer from the sources, check its work, and save it.
The reply is untrusted: parse_draft() rejects anything we can't verify, so a made-up fact never reaches the table."""
import json
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from psycopg.types.json import Jsonb

from core.llm.client import TIME_LIMIT, llm

PROMPT = (Path(__file__).parent / "prompts" / "draft.txt").read_text(encoding="utf-8")

IST = timezone(timedelta(hours=5, minutes=30))  # India has no daylight saving, so a fixed offset is exact
PUBLISHER = {"@type": "Organization", "name": "AI Atlas India", "url": "https://aiatlasindia.com"}
MIN_SNIPPET = 10   # a 3-character "quote" would match almost any page
MAX_SNIPPET = 300
MAX_CITES = 3      # times one fact may be cited in the body
TRIES = 3          # drafts per request; each retry is told why the last one was rejected


def today_ist():
    return datetime.now(IST).date()


# Curly quotes and long dashes count as their plain forms: models often "tidy" them when copying, and the words
# are still the same.
_PLAIN = str.maketrans("‘’“”–—", "''\"\"--")


def _norm(text):
    """Squeeze spacing, ignore capitals and quote/dash styles, so a quote still matches if only those differ."""
    return " ".join(text.translate(_PLAIN).split()).lower()


def build_prompt(question, sources):
    """Fill the three blanks in one pass, so text inside a page or the question can't be mistaken for a blank."""
    block = "\n".join(
        f'<source url="{s["url"]}">\n{s["text"].replace("</source>", "")}\n</source>' for s in sources
    )
    today = today_ist()
    values = {"question": question, "sources": block, "today": f"{today.day} {today:%B %Y}"}  # "22 November 2026"
    return re.sub(r"\{(question|sources|today)\}", lambda m: values[m.group(1)], PROMPT)


def parse_draft(raw, sources):
    """Turn the LLM's reply into a clean draft dict, or raise ValueError saying what is wrong (the message is
    shown to the LLM on the retry). Facts must quote a real source word for word; body markers must have facts."""
    match = re.search(r"\{.*\}", raw, re.S)  # tolerate ```json fences and chatter around the object
    if not match:
        raise ValueError("the reply has no JSON object")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"the reply is not valid JSON: {e}") from e

    draft = {}
    for key, low, high in (("title", 1, 110), ("meta_description", 1, 200), ("alt_text", 1, 200), ("body", 200, 20_000)):
        value = data.get(key)
        value = value.strip() if isinstance(value, str) else ""
        if not low <= len(value) <= high:
            raise ValueError(f"'{key}' must be {low} to {high} characters (it is {len(value)})")
        draft[key] = value

    pages = {s["url"]: _norm(s["text"]) for s in sources}
    facts, numbers = [], set()
    for item in data.get("facts") if isinstance(data.get("facts"), list) else []:
        try:
            n = int(item["n"])
            claim, url, snippet = (str(item[k]).strip() for k in ("claim", "source_url", "snippet"))
        except (KeyError, TypeError, ValueError):
            raise ValueError("every fact needs n, claim, source_url and snippet") from None
        if n in numbers:
            raise ValueError(f"fact number {n} is used twice")
        if url not in pages:
            raise ValueError(f"fact {n} cites {url!r}, which is not one of the sources")
        if not claim:
            raise ValueError(f"fact {n} has no claim")
        if not MIN_SNIPPET <= len(snippet) <= MAX_SNIPPET:  # say how far off, so the retry can fix exactly this
            raise ValueError(f"fact {n}'s snippet is {len(snippet)} characters; it must be {MIN_SNIPPET} to {MAX_SNIPPET}. "
                             "Quote only the shortest exact part of the source that states the fact")
        if _norm(snippet) not in pages[url]:
            raise ValueError(f"fact {n}: the snippet is not word for word in {url}. Copy it exactly from the source")
        numbers.add(n)
        facts.append({"n": n, "claim": claim, "source_url": url, "snippet": snippet})

    counts = Counter(int(m) for m in re.findall(r"\[(\d+)\]", draft["body"]))
    cited = set(counts)
    if not cited:
        raise ValueError("the body must cite its facts with markers like [1]")
    if cited - numbers:
        raise ValueError(f"the body cites {sorted(cited - numbers)} but there are no facts with those numbers")
    # One quote can't back many different claims (code can't judge meaning, so it limits how far one fact stretches).
    overused = sorted(n for n, times in counts.items() if times > MAX_CITES)
    if overused:
        raise ValueError(f"fact(s) {overused} are cited more than {MAX_CITES} times. "
                         "Give each separate claim its own fact with its own snippet")
    draft["facts"] = [f for f in facts if f["n"] in cited]  # a fact the body never uses is dropped

    questions = data.get("expert_questions")
    questions = questions if isinstance(questions, list) else []
    draft["expert_questions"] = [str(q).strip() for q in questions if str(q).strip()][:3]
    return draft


def generate(question, sources):
    """Draft, check, and (once) retry with the reason if the check failed. Returns the clean draft dict.
    Raises ValueError if both tries were rejected, RuntimeError if every model is down."""
    prompt = build_prompt(question, sources)
    feedback = ""
    deadline = time.monotonic() + TIME_LIMIT  # both tries share one time limit, so the request ends before Vercel's
    for _ in range(TRIES):
        try:
            return parse_draft(llm(prompt + feedback, json=True, best=True, deadline=deadline), sources)
        except ValueError as e:
            error = str(e)
            feedback = (f"\n\nYOUR PREVIOUS REPLY WAS REJECTED: {error}\nCheck EVERY fact for the same problem, not only "
                        "the one named. Reply again with the corrected JSON object only.")
    raise ValueError(f"the draft was rejected {TRIES} times, last reason: {error}")


def build_json_ld(draft):
    """Structured data for search engines (schema.org Article). Built by code from the checked fields, never
    taken from the LLM, so it is always valid and says nothing the page doesn't. Level 4 adds the page address,
    publish date and the expert reviewer once those exist."""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": draft["title"],
        "description": draft["meta_description"],
        "inLanguage": "en-IN",
        "dateModified": today_ist().isoformat(),
        "author": PUBLISHER,
        "publisher": PUBLISHER,
        "citation": sorted({f["source_url"] for f in draft["facts"]}),
    }


def save_draft(conn, question_id, draft):
    """Save the draft as the next version for this question, plus its facts. Returns (draft_id, version)."""
    version = conn.execute(
        "SELECT COALESCE(MAX(version), 0) + 1 FROM drafts WHERE question_id = %s", (question_id,)
    ).fetchone()[0]
    draft_id = conn.execute(
        "INSERT INTO drafts (question_id, version, title, body, meta_description, alt_text, json_ld, expert_questions) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
        (question_id, version, draft["title"], draft["body"], draft["meta_description"], draft["alt_text"],
         Jsonb(build_json_ld(draft)), draft["expert_questions"]),
    ).fetchone()[0]
    for fact in draft["facts"]:
        conn.execute(
            "INSERT INTO facts (draft_id, n, claim, source_url, snippet, checked_on) VALUES (%s, %s, %s, %s, %s, %s)",
            (draft_id, fact["n"], fact["claim"], fact["source_url"], fact["snippet"], today_ist()),
        )
    return draft_id, version
