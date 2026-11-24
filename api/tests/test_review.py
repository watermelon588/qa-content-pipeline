"""Checks for the Level 4 rules: the expert's link, their decision, the status flow, and the 20-answer cap.
No network, no database. Run from the api/ folder:  .venv/Scripts/python -m unittest tests.test_review -v
"""
import unittest

from fastapi import HTTPException

from core.status import check_move
from pages.pages import MAX_PAGES, check_cap, slugify
from review.experts import clean, codes, new_code, who
from review.review import check_decision, hash_token, new_token, review_email


class StatusFlowTest(unittest.TestCase):
    def test_the_review_path_is_allowed(self):
        for a, b in (("prechecked", "in_review"), ("in_review", "in_review"), ("in_review", "approved"),
                     ("in_review", "edited"), ("in_review", "rejected"), ("approved", "published"), ("edited", "published")):
            check_move("draft", a, b)  # no exception

    def test_nothing_publishes_without_the_expert(self):
        for a in ("draft", "prechecked", "in_review", "rejected", "published"):
            with self.assertRaises(HTTPException) as ctx:
                check_move("draft", a, "published")
            self.assertEqual(ctx.exception.status_code, 409)

    def test_an_unchecked_draft_cannot_go_to_the_expert(self):
        with self.assertRaises(HTTPException):
            check_move("draft", "draft", "in_review")


class CapTest(unittest.TestCase):
    def test_the_twentieth_answer_may_publish(self):
        check_cap(MAX_PAGES - 1)  # 19 already live: one more is fine

    def test_the_twenty_first_is_refused(self):
        self.assertEqual(MAX_PAGES, 20)  # the rule in the guide; changing it should fail this test
        with self.assertRaises(HTTPException) as ctx:
            check_cap(MAX_PAGES)
        self.assertEqual(ctx.exception.status_code, 409)


class SlugTest(unittest.TestCase):
    def test_title_becomes_a_clean_address(self):
        self.assertEqual(slugify("What does an H100 cost in India? (2026)"), "what-does-an-h100-cost-in-india-2026")

    def test_long_titles_are_cut_at_a_word(self):
        slug = slugify("word " * 40)
        self.assertLessEqual(len(slug), 80)
        self.assertFalse(slug.endswith("-"))


class TokenTest(unittest.TestCase):
    def test_only_the_hash_is_kept_and_it_matches(self):
        token, token_hash = new_token()
        self.assertGreaterEqual(len(token), 40)          # 256 random bits: can't be guessed
        self.assertNotIn(token, token_hash)
        self.assertEqual(hash_token(token), token_hash)

    def test_every_link_is_different(self):
        self.assertNotEqual(new_token()[0], new_token()[0])


class DecisionTest(unittest.TestCase):
    ORIGINAL = {"body": "The AI's checked draft. " * 20, "title": "H100 prices in India",
                "meta_description": "What an H100 costs per hour from Indian GPU clouds.", "alt_text": "A price table"}

    def edits(self, **changes):
        """What the form sends: every field, as the AI wrote it, except the ones changed."""
        return {**self.ORIGINAL, **changes}

    def test_approve_keeps_the_draft_even_if_the_form_held_edits(self):
        self.assertEqual(check_decision("approved", self.edits(title="Ignored"), "  Use spot GPUs for training.  ", "", self.ORIGINAL),
                         {"decision": "approved", "edited_body": None, "edited_title": None, "edited_meta_description": None,
                          "edited_alt_text": None, "advice": "Use spot GPUs for training.", "note": None})

    def test_an_edit_must_change_something(self):
        with self.assertRaises(ValueError):
            check_decision("edited", self.edits(), "", "", self.ORIGINAL)   # nothing changed
        with self.assertRaises(ValueError):
            check_decision("edited", {}, "", "", self.ORIGINAL)              # nothing sent

    def test_browser_line_breaks_are_not_an_edit(self):
        original = {**self.ORIGINAL, "body": "## Cost\nAn H100 costs Rs 250 an hour [1].\n\nMore text."}
        with self.assertRaises(ValueError):  # a textarea sends the same text back with \r\n
            check_decision("edited", {**original, "body": original["body"].replace("\n", "\r\n")}, "", "", original)

    def test_only_the_changed_fields_are_kept_as_the_after_version(self):
        after = self.ORIGINAL["body"] + "One more line from the expert."
        got = check_decision("edited", self.edits(body=after), "", "", self.ORIGINAL)
        self.assertEqual((got["edited_body"], got["edited_title"], got["edited_meta_description"], got["edited_alt_text"]),
                         (after, None, None, None))

    def test_the_expert_can_edit_only_the_title_or_the_search_text_or_the_image_description(self):
        got = check_decision("edited", self.edits(title="  H100 hourly price in India  "), "", "", self.ORIGINAL)
        self.assertEqual((got["edited_title"], got["edited_body"]), ("H100 hourly price in India", None))
        got = check_decision("edited", self.edits(meta_description="New search text.", alt_text="A chart"), "", "", self.ORIGINAL)
        self.assertEqual((got["edited_meta_description"], got["edited_alt_text"]), ("New search text.", "A chart"))

    def test_a_cleared_or_oversized_field_is_refused(self):
        for field, value in (("title", "  "), ("meta_description", ""), ("alt_text", "x" * 301), ("title", "x" * 121)):
            with self.assertRaises(ValueError, msg=field):
                check_decision("edited", self.edits(**{field: value}), "", "", self.ORIGINAL)

    def test_a_rejection_needs_a_reason(self):
        with self.assertRaises(ValueError):
            check_decision("rejected", {}, "", "  ", self.ORIGINAL)

    def test_unknown_decisions_and_huge_text_are_refused(self):
        with self.assertRaises(ValueError):
            check_decision("published", {}, "", "", self.ORIGINAL)
        with self.assertRaises(ValueError):
            check_decision("approved", {}, "x" * 2001, "", self.ORIGINAL)


class EmailTest(unittest.TestCase):
    def test_email_has_the_link_and_escapes_the_title(self):
        subject, text, html = review_email("<b>H100</b> & prices", "https://x.example/review/abc", ["What surprised you?"], "Sanath W, Senior DevOps Engineer")
        self.assertIn("https://x.example/review/abc", text)
        self.assertIn("https://x.example/review/abc", html)
        self.assertIn("&lt;b&gt;H100&lt;/b&gt; &amp; prices", html)  # a title can't inject HTML into the email
        self.assertIn("What surprised you?", text)
        self.assertNotIn("$", html)  # every blank in the template was filled
        self.assertIn("Hello Sanath,", html)  # greets the expert the link was sent to
        self.assertIn("reviewer code", text)

    def test_email_escapes_questions_and_drops_the_empty_list(self):
        _, _, html = review_email("T", "https://x.example/review/abc", ['<a href="evil">x</a>'], "Prince Patel")
        self.assertIn("&lt;a href=&quot;evil&quot;&gt;", html)
        _, text, html = review_email("T", "https://x.example/review/abc", [], "Prince Patel")
        self.assertNotIn("view on", html + text)  # no questions, no empty heading


class ExpertCodeTest(unittest.TestCase):
    SETTING = "sanath:K7QM4XRT, prince:9WPD-3HJA"

    def test_each_code_names_its_expert(self):
        self.assertEqual(who("K7QM4XRT", self.SETTING), "sanath")
        self.assertEqual(who("9WPD3HJA", self.SETTING), "prince")

    def test_typing_slips_still_match(self):
        self.assertEqual(who(" k7qm-4xrt ", self.SETTING), "sanath")  # lower case, a dash, spaces

    def test_wrong_or_empty_codes_match_no_one(self):
        for code in ("", "K7QM4XRX", "K7QM4XR", "K7QM4XRTT", "9WPD3HJA K7QM4XRT"):
            self.assertIsNone(who(code, self.SETTING), code)

    def test_a_half_filled_setting_never_lets_an_empty_code_in(self):
        setting = "sanath:, prince:9WPD3HJA, stranger:AAAA1111"
        self.assertEqual(codes(setting), {"prince": "9WPD3HJA"})  # empty code and unknown names are dropped
        self.assertIsNone(who("", setting))
        self.assertIsNone(who("AAAA1111", setting))
        self.assertIsNone(who("anything", ""))

    def test_new_codes_are_clean_and_different(self):
        made = {new_code() for _ in range(50)}
        self.assertEqual(len(made), 50)
        self.assertTrue(all(len(c) == 8 and clean(c) == c and not set(c) & set("01OIL") for c in made))


if __name__ == "__main__":
    unittest.main()
