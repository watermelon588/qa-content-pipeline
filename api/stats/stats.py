"""Level 6 helpers with no database or network, so the tests can run them offline:
reading an uploaded GA4 / Search Console CSV, adding up its count columns, and checking the AI's suggestion."""
import csv
import json
import re

MAX_ROWS = 500  # an export bigger than this is cut; the dashboard only shows the top rows anyway
# Columns that are counts, so adding them up makes sense. CTR, position and rates are averages: never summed.
SUMMABLE = re.compile(r"clicks|impressions|users|sessions|views|events", re.I)


def parse_csv(text):
    """An exported CSV -> (header, rows). GA4 puts '#' comment lines and blank lines around its table, and some
    exports hold more than one table; we keep the biggest one. "Total" rows are dropped so totals aren't doubled.
    ponytail: splits tables on blank lines, so a cell with a line break inside it would break the table."""
    lines = [line for line in text.lstrip("﻿").splitlines() if not line.startswith("#")]
    blocks, block = [], []
    for line in lines + [""]:  # the extra "" closes the last block
        if line.strip():
            block.append(line)
        elif block:
            blocks.append(block)
            block = []
    if not blocks:
        raise ValueError("no table found in the file")
    header, *rows = list(csv.reader(max(blocks, key=len)))
    rows = [r for r in rows if r and r[0].strip().lower() not in ("total", "grand total")]
    if not rows:
        raise ValueError("the table has a header but no rows")
    return header, rows[:MAX_ROWS]


def number(cell):
    """'1,234' -> 1234.0, '3.5%' -> 3.5, anything else -> None."""
    try:
        return float(cell.replace(",", "").replace("%", "").strip())
    except (ValueError, AttributeError):
        return None


def totals(header, rows):
    """{column: sum} for every count column (clicks, impressions, users...) whose cells are all numbers."""
    out = {}
    for i, name in enumerate(header):
        if not SUMMABLE.search(name):
            continue
        values = [number(r[i]) for r in rows if i < len(r) and r[i].strip()]
        if values and None not in values:
            out[name] = round(sum(values))
    return out


def parse_suggestion(raw, valid_ids, most=3):
    """The LLM's reply -> {"insight": str, "picks": [{"question_id", "reason"}]}. The reply is untrusted: only
    questions we offered can be picked, each once, at most `most` of them."""
    match = re.search(r"\{.*\}", raw, re.S)  # tolerate ```json fences and chatter around the object
    if not match:
        raise ValueError("the LLM reply has no JSON object")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"the LLM reply is not valid JSON: {e}") from e
    insight = str(data.get("insight") or "").strip()
    if not insight:
        raise ValueError("the LLM reply has no insight")
    picks, seen = [], set()
    for item in data.get("picks") or []:
        try:
            qid = int(item["question_id"])
        except (KeyError, TypeError, ValueError):
            continue
        if qid in valid_ids and qid not in seen:
            seen.add(qid)
            picks.append({"question_id": qid, "reason": str(item.get("reason", ""))[:300]})
    return {"insight": insight[:800], "picks": picks[:most]}
