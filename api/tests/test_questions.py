"""Checks for the parts that must not break silently. No network, no database.
Run from the api/ folder:  .venv/Scripts/python -m unittest tests.test_questions -v
"""
import unittest
from unittest.mock import patch

from fastapi import HTTPException

from core.auth import require_secret
from questions import rank
from questions.sources import hackernews, stackexchange


class ParseRankingTest(unittest.TestCase):
    IDS = {1, 2, 3, 4}

    def test_clean_reply_with_code_fence(self):
        raw = '```json\n[{"id": 1, "score": 8, "reason": "Pricing question.", "duplicate_of": null}]\n```'
        self.assertEqual(rank.parse_ranking(raw, self.IDS),
                         [{"id": 1, "score": 8.0, "reason": "Pricing question.", "duplicate_of": None}])

    def test_score_is_clamped_to_0_10(self):
        raw = '[{"id": 1, "score": 99, "reason": "x"}, {"id": 2, "score": -5, "reason": "y"}]'
        self.assertEqual([r["score"] for r in rank.parse_ranking(raw, self.IDS)], [10.0, 0.0])

    def test_unknown_ids_repeats_and_junk_items_are_skipped(self):
        raw = '[{"id": 99, "score": 5}, {"id": 1, "score": 5}, {"id": 1, "score": 9}, "junk", {"id": 2}]'
        self.assertEqual([(r["id"], r["score"]) for r in rank.parse_ranking(raw, self.IDS)], [(1, 5.0)])

    def test_duplicate_chain_points_to_the_root(self):
        raw = ('[{"id": 1, "score": 5, "duplicate_of": 2}, {"id": 2, "score": 5, "duplicate_of": 3},'
               ' {"id": 3, "score": 5, "duplicate_of": null}]')
        self.assertEqual({r["id"]: r["duplicate_of"] for r in rank.parse_ranking(raw, self.IDS)}, {1: 3, 2: 3, 3: None})

    def test_duplicate_loop_and_self_reference_are_dropped(self):
        raw = ('[{"id": 1, "score": 5, "duplicate_of": 2}, {"id": 2, "score": 5, "duplicate_of": 1},'
               ' {"id": 3, "score": 5, "duplicate_of": 3}, {"id": 4, "score": 5, "duplicate_of": 99}]')
        self.assertTrue(all(r["duplicate_of"] is None for r in rank.parse_ranking(raw, self.IDS)))

    def test_reply_that_is_not_json_raises(self):
        for raw in ("Sorry, I cannot do that.", "[not json]"):
            with self.assertRaises(ValueError):
                rank.parse_ranking(raw, self.IDS)


class RequireSecretTest(unittest.TestCase):
    def test_right_secret_passes(self):
        with patch("core.auth.CRON_SECRET", "s3cret"):
            require_secret("Bearer s3cret")  # no exception

    def test_wrong_missing_or_malformed_secret_is_401(self):
        with patch("core.auth.CRON_SECRET", "s3cret"):
            for header in ("Bearer wrong", "", "s3cret", "bearer s3cret"):
                with self.assertRaises(HTTPException) as ctx:
                    require_secret(header)
                self.assertEqual(ctx.exception.status_code, 401)

    def test_empty_server_secret_never_lets_anyone_in(self):
        with patch("core.auth.CRON_SECRET", ""):
            with self.assertRaises(HTTPException):
                require_secret("Bearer ")


class SourcesTest(unittest.TestCase):
    def test_stackexchange_unescapes_titles_and_honours_backoff(self):
        reply = {"items": [{"title": "Won&#39;t it run &amp; scale?", "link": "https://x/1"}], "backoff": 2}
        with patch.object(stackexchange, "get_json", return_value=reply), \
             patch.object(stackexchange.time, "sleep") as sleep:
            found = stackexchange.fetch()
        self.assertEqual(found[0], {"text": "Won't it run & scale?", "source_url": "https://x/1"})
        sleep.assert_called_with(2)

    def test_hackernews_strips_label_and_skips_untitled_hits(self):
        reply = {"hits": [{"title": "Ask HN: Best GPU host?", "objectID": "42"}, {"title": None, "objectID": "43"}]}
        with patch.object(hackernews, "get_json", return_value=reply):
            found = hackernews.fetch()
        self.assertEqual(found[0], {"text": "Best GPU host?", "source_url": "https://news.ycombinator.com/item?id=42"})
        self.assertTrue(all("id=43" not in f["source_url"] for f in found))


if __name__ == "__main__":
    unittest.main()
