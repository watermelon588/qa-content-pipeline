"""Level 6 checks that need no database or network: reading exports and checking the AI's suggestion.
Run from api/: .venv/Scripts/python -m unittest tests.test_stats -v"""
import unittest

from stats.stats import parse_csv, parse_suggestion, totals

# The shape of a GA4 export: comment lines, blank lines, a small table, then the real one with a total row.
GA4 = """﻿# ----------------------------------------
# Reports snapshot
# Start date: 20261123
# End date: 20261130
# ----------------------------------------

Nth day,Active users
0000,3

Page path,Views,Active users,Average engagement time
/q/h100-price,"1,204",310,42.5
/about,96,40,12.0
Grand total,"1,300",350,40.0
"""

GSC = """Top queries,Clicks,Impressions,CTR,Position
h100 price india,4,210,1.9%,8.2
gpu cloud india,1,95,1.05%,14.1
"""


class ParseCsv(unittest.TestCase):
    def test_ga4_keeps_the_biggest_table_and_drops_comments_and_totals(self):
        header, rows = parse_csv(GA4)
        self.assertEqual(header, ["Page path", "Views", "Active users", "Average engagement time"])
        self.assertEqual([r[0] for r in rows], ["/q/h100-price", "/about"])

    def test_empty_file_is_refused(self):
        with self.assertRaises(ValueError):
            parse_csv("# only a comment\n\n")
        with self.assertRaises(ValueError):
            parse_csv("Query,Clicks\n")

    def test_totals_add_counts_but_never_averages(self):
        self.assertEqual(totals(*parse_csv(GA4)), {"Views": 1300, "Active users": 350})
        self.assertEqual(totals(*parse_csv(GSC)), {"Clicks": 5, "Impressions": 305})  # no CTR, no Position


class ParseSuggestion(unittest.TestCase):
    def test_only_offered_questions_once_each_at_most_three(self):
        raw = """```json
        {"insight": "Price pages get the clicks.", "picks": [
          {"question_id": 1, "reason": "a"}, {"question_id": 99, "reason": "not offered"},
          {"question_id": 1, "reason": "twice"}, {"question_id": "2", "reason": "b"},
          {"question_id": 3, "reason": "c"}, {"question_id": 4, "reason": "d"}]}
        ```"""
        result = parse_suggestion(raw, {1, 2, 3, 4})
        self.assertEqual(result["insight"], "Price pages get the clicks.")
        self.assertEqual([p["question_id"] for p in result["picks"]], [1, 2, 3])

    def test_reply_without_insight_is_refused(self):
        with self.assertRaises(ValueError):
            parse_suggestion('{"picks": []}', {1})
        with self.assertRaises(ValueError):
            parse_suggestion("sorry, I can't help", {1})


if __name__ == "__main__":
    unittest.main()
