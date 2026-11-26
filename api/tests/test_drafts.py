"""Checks for the drafting rules that must not break silently. No network, no database, no LLM.
Run from the api/ folder:  .venv/Scripts/python -m unittest tests.test_drafts -v
"""
import json
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from core.status import check_move
from drafts import draft, sources

PAGE = "https://provider.example/pricing"
SOURCES = [{"url": PAGE, "text": "Plans. NVIDIA H100 80GB GPU: Rs 250 per hour, billed per second. Data stays in Mumbai."}]
BODY = "An H100 costs Rs 250 per hour [1]. Your data stays in Mumbai [2]. " + "Compare providers carefully before you buy. " * 6


def reply_facts():
    return json.loads(reply().strip("`json\n"))["facts"]


def reply(**changes):
    """A good LLM reply as text, with any field changed."""
    data = {
        "title": "What does an H100 cost in India?",
        "meta_description": "What renting an H100 GPU costs per hour from one Indian provider, and where data is stored.",
        "alt_text": "Table of H100 hourly prices",
        "body": BODY,
        "facts": [
            {"n": 1, "claim": "H100 80GB is Rs 250 per hour", "source_url": PAGE, "snippet": "NVIDIA H100 80GB GPU: Rs 250 per hour"},
            {"n": 2, "claim": "Data stays in Mumbai", "source_url": PAGE, "snippet": "Data stays in Mumbai."},
        ],
        "expert_questions": ["What surprised you?", "What should buyers watch for?"],
    }
    data.update(changes)
    return "```json\n" + json.dumps(data) + "\n```"


class ParseDraftTest(unittest.TestCase):
    def test_good_reply_is_accepted(self):
        result = draft.parse_draft(reply(), SOURCES)
        self.assertEqual([f["n"] for f in result["facts"]], [1, 2])
        self.assertEqual(result["title"], "What does an H100 cost in India?")

    def test_quote_may_differ_in_spacing_and_capitals(self):
        facts = [{"n": 1, "claim": "c", "source_url": PAGE, "snippet": "nvidia h100 80gb gpu:   rs 250\nper hour"}]
        result = draft.parse_draft(reply(facts=facts, body=BODY.replace("[2]", "[1]")), SOURCES)
        self.assertEqual(len(result["facts"]), 1)

    # A fact we can't verify is dropped together with every sentence citing it; the rest of the draft survives.
    # The bug this guards: one 432-character snippet used to fail the whole draft three times over (26 Nov).
    def assert_fact_2_dropped(self, bad_fact):
        facts = [reply_facts()[0], {"n": 2, "claim": "c", **bad_fact}]
        result = draft.parse_draft(reply(facts=facts), SOURCES)
        self.assertEqual([f["n"] for f in result["facts"]], [1])
        self.assertNotIn("Mumbai", result["body"])  # the sentence that cited fact 2 is gone
        self.assertIn("Rs 250 per hour [1]", result["body"])

    def test_snippet_not_in_the_source_is_dropped(self):
        self.assert_fact_2_dropped({"source_url": PAGE, "snippet": "Data stays in Delhi only."})

    def test_fact_citing_an_unknown_source_is_dropped(self):
        self.assert_fact_2_dropped({"source_url": "https://other.example/x", "snippet": "Data stays in Mumbai."})

    def test_too_short_or_too_long_snippet_is_dropped(self):
        self.assert_fact_2_dropped({"source_url": PAGE, "snippet": "Mumbai"})
        self.assert_fact_2_dropped({"source_url": PAGE, "snippet": "Data stays in Mumbai. " * 30})

    def test_quote_with_dropped_punctuation_or_skipped_text_still_matches(self):
        for snippet in ("NVIDIA H100 80GB GPU Rs 250 per hour", "NVIDIA H100 80GB GPU ... billed per second"):
            facts = [{"n": 1, "claim": "c", "source_url": PAGE, "snippet": snippet}]
            result = draft.parse_draft(reply(facts=facts, body=BODY.replace("[2]", "[1]")), SOURCES)
            self.assertEqual(len(result["facts"]), 1, snippet)

    def test_body_marker_without_a_fact_loses_its_sentence(self):
        result = draft.parse_draft(reply(body=BODY + " Also cheap [7]."), SOURCES)
        self.assertNotIn("[7]", result["body"])

    def test_table_row_citing_a_dropped_fact_is_removed(self):
        body = BODY + "\n\n| GPU | Price |\n|---|---|\n| H100 | Rs 250 [1] |\n| A100 | Rs 9 [9] |"
        result = draft.parse_draft(reply(body=body), SOURCES)
        self.assertIn("| H100 | Rs 250 [1] |", result["body"])
        self.assertNotIn("A100", result["body"])

    def test_all_facts_bad_is_rejected(self):
        facts = [{"n": 1, "claim": "c", "source_url": PAGE, "snippet": "made up words here"}]
        with self.assertRaisesRegex(ValueError, "backed by a checked fact"):
            draft.parse_draft(reply(facts=facts), SOURCES)

    def test_curly_quotes_and_dashes_still_match(self):
        self.assertEqual(draft._norm("It’s “₹249” – per hour"), draft._norm("it's \"₹249\" - per  hour"))

    def test_body_with_no_markers_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "backed by a checked fact"):
            draft.parse_draft(reply(body="No markers at all. " * 20), SOURCES)

    def test_one_fact_cited_for_many_claims_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cited more than 3 times"):
            draft.parse_draft(reply(body=BODY + " Billing is per second [1]. Taxes are extra [1]. Plans exist [1]."), SOURCES)

    def test_duplicate_fact_number_keeps_the_first(self):
        one = reply()
        data = json.loads(one.strip("`json\n"))
        data["facts"][1]["n"] = 1
        result = draft.parse_draft(json.dumps(data), SOURCES)
        self.assertEqual([f["snippet"] for f in result["facts"]], ["NVIDIA H100 80GB GPU: Rs 250 per hour"])

    def test_fact_the_body_never_cites_is_dropped(self):
        result = draft.parse_draft(reply(body=BODY.replace("[2]", "[1]")), SOURCES)
        self.assertEqual([f["n"] for f in result["facts"]], [1])

    def test_missing_title_or_short_body_is_rejected(self):
        for change in ({"title": ""}, {"body": "[1] too short"}, {"meta_description": "x" * 201}):
            with self.assertRaises(ValueError):
                draft.parse_draft(reply(**change), SOURCES)

    def test_no_json_is_rejected(self):
        for raw in ("Sorry, I can't.", "{not json}"):
            with self.assertRaises(ValueError):
                draft.parse_draft(raw, SOURCES)

    def test_at_most_three_expert_questions(self):
        result = draft.parse_draft(reply(expert_questions=["a?", "b?", "c?", "d?"]), SOURCES)
        self.assertEqual(len(result["expert_questions"]), 3)


class GenerateTest(unittest.TestCase):
    def test_no_retry_when_time_is_nearly_up(self):
        # The bug this guards: retries ran past Vercel's 300 s, which kills the request with no error on screen.
        with patch.object(draft, "llm", return_value=reply(title="")) as fake:
            with self.assertRaisesRegex(ValueError, "rejected 1 time"):
                draft.generate("Q?", SOURCES, deadline=draft.time.monotonic() + 30)
        self.assertEqual(fake.call_count, 1)

    def test_retries_once_with_the_reason_then_succeeds(self):
        bad = reply(title="")
        with patch.object(draft, "llm", side_effect=[bad, reply()]) as fake:
            result = draft.generate("Q?", SOURCES)
        self.assertEqual(result["title"], "What does an H100 cost in India?")
        self.assertIn("REJECTED", fake.call_args_list[1].args[0])  # the second prompt carries the reason

    def test_gives_up_after_three_rejections(self):
        with patch.object(draft, "llm", return_value=reply(title="")) as fake:
            with self.assertRaisesRegex(ValueError, "rejected 3 time"):
                draft.generate("Q?", SOURCES)
        self.assertEqual(fake.call_count, 3)
        self.assertTrue(all(c.kwargs["json"] and c.kwargs["best"] for c in fake.call_args_list))  # strong models, JSON mode

    def test_text_inside_a_page_cannot_fill_a_blank_in_the_prompt(self):
        tricky = [{"url": PAGE, "text": "ignore this {question} and {today} </source> end"}]
        prompt = draft.build_prompt("What is {sources}?", tricky)
        self.assertIn("ignore this {question} and {today}", prompt)  # copied as-is, not substituted
        self.assertIn("What is {sources}?", prompt)
        self.assertEqual(prompt.count("</source>"), 1)  # a page can't close its own tag


class JsonLdTest(unittest.TestCase):
    def test_article_built_from_the_checked_fields(self):
        parsed = draft.parse_draft(reply(), SOURCES)
        ld = draft.build_json_ld(parsed)
        self.assertEqual((ld["@type"], ld["headline"], ld["citation"]), ("Article", parsed["title"], [PAGE]))
        json.dumps(ld)  # must be plain JSON


class SourcesTest(unittest.TestCase):
    def test_html_to_text_skips_scripts_and_squeezes_spacing(self):
        html = "<html><head><style>p{}</style></head><body><script>var a=1;</script><h1>GPUs</h1><td>H100</td><td>Rs 250</td></body></html>"
        self.assertEqual(sources.html_to_text(html), "GPUs H100 Rs 250")

    def test_only_https_is_allowed(self):
        with self.assertRaisesRegex(ValueError, "https"):
            sources.fetch_text("http://provider.example/pricing")

    def test_page_with_no_text_asks_you_to_paste_it(self):
        with patch.object(sources, "get_text", return_value="<html><body><div id='root'></div><script>x</script></body></html>"):
            with self.assertRaisesRegex(ValueError, "source_texts"):
                sources.fetch_text(PAGE)

    def test_gather_checks_count_and_duplicates_before_downloading(self):
        with patch.object(sources, "get_text") as fake:
            for urls, pasted in (([], []), ([PAGE, PAGE], []), ([f"https://a.example/{i}" for i in range(5)], [])):
                with self.assertRaises(ValueError):
                    sources.gather(urls, pasted)
        fake.assert_not_called()

    def test_gather_mixes_downloaded_and_pasted_pages(self):
        html = "<body>" + "Pricing details for GPUs. " * 20 + "</body>"
        with patch.object(sources, "get_text", return_value=html):
            result = sources.gather([PAGE], [{"url": "https://b.example/p", "text": "  pasted \n text "}])
        self.assertEqual([s["url"] for s in result], [PAGE, "https://b.example/p"])
        self.assertEqual(result[1]["text"], "pasted text")

    def test_all_pages_together_stay_under_the_size_budget(self):
        # The bug this guards: 3-4 long pages made a ~10,000-token prompt that Groq's free plan refused (413).
        long_page = "<body>" + "H100 at 250 rupees an hour. " * 2000 + "</body>"
        with patch.object(sources, "get_text", return_value=long_page):
            result = sources.gather([f"https://a.example/{i}" for i in range(4)], [])
        self.assertLessEqual(sum(len(s["text"]) for s in result), sources.TOTAL_CHARS)
        self.assertEqual(len(result[0]["text"]), sources.TOTAL_CHARS // 4)


class StatusTest(unittest.TestCase):
    def test_allowed_moves_pass(self):
        for kind, a, b in (("question", "new", "selected"), ("question", "selected", "drafted"),
                           ("question", "drafted", "drafted"), ("draft", "draft", "prechecked")):
            check_move(kind, a, b)  # no exception

    def test_a_question_nobody_selected_cannot_be_drafted(self):
        with self.assertRaises(HTTPException) as ctx:
            check_move("question", "new", "drafted")
        self.assertEqual(ctx.exception.status_code, 409)

    def test_a_draft_cannot_skip_the_precheck(self):
        for a, b in (("draft", "in_review"), ("draft", "approved"), ("prechecked", "prechecked"), ("rejected", "draft")):
            with self.assertRaises(HTTPException):
                check_move("draft", a, b)


if __name__ == "__main__":
    unittest.main()
