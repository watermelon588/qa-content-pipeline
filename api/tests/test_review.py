"""Checks for the Level 4 rules: the expert's link, their decision, the status flow, and the 20-answer cap.
No network, no database. Run from the api/ folder:  .venv/Scripts/python -m unittest tests.test_review -v
"""
import unittest

from fastapi import HTTPException

from core.status import check_move
from pages.pages import MAX_PAGES, check_cap, slugify
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
    ORIGINAL = "The AI's checked draft. " * 20

    def test_approve_keeps_the_draft(self):
        self.assertEqual(check_decision("approved", "", "  Use spot GPUs for training.  ", "", self.ORIGINAL),
                         {"decision": "approved", "edited_body": None, "advice": "Use spot GPUs for training.", "note": None})

    def test_an_edit_must_change_the_text(self):
        with self.assertRaises(ValueError):
            check_decision("edited", self.ORIGINAL, "", "", self.ORIGINAL)
        with self.assertRaises(ValueError):
            check_decision("edited", "", "", "", self.ORIGINAL)

    def test_browser_line_breaks_are_not_an_edit(self):
        original = "## Cost\nAn H100 costs Rs 250 an hour [1].\n\nMore text."
        with self.assertRaises(ValueError):  # a textarea sends the same text back with \r\n
            check_decision("edited", original.replace("\n", "\r\n"), "", "", original)

    def test_an_edit_is_kept_as_the_after_version(self):
        after = self.ORIGINAL + "One more line from the expert."
        self.assertEqual(check_decision("edited", after, "", "", self.ORIGINAL)["edited_body"], after)

    def test_a_rejection_needs_a_reason(self):
        with self.assertRaises(ValueError):
            check_decision("rejected", "", "", "  ", self.ORIGINAL)

    def test_unknown_decisions_and_huge_text_are_refused(self):
        with self.assertRaises(ValueError):
            check_decision("published", "", "", "", self.ORIGINAL)
        with self.assertRaises(ValueError):
            check_decision("approved", "", "x" * 2001, "", self.ORIGINAL)


class EmailTest(unittest.TestCase):
    def test_email_has_the_link_and_escapes_the_title(self):
        subject, text, html = review_email("<b>H100</b> & prices", "https://x.example/review/abc", ["What surprised you?"])
        self.assertIn("https://x.example/review/abc", text)
        self.assertIn("https://x.example/review/abc", html)
        self.assertIn("&lt;b&gt;H100&lt;/b&gt; &amp; prices", html)  # a title can't inject HTML into the email
        self.assertIn("What surprised you?", text)


if __name__ == "__main__":
    unittest.main()
