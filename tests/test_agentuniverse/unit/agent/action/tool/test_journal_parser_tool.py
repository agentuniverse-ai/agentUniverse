#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_journal_parser_tool.py

"""Offline unit tests for JournalParserTool.

The tool is built purely on the standard library (datetime, re) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic and checked against ground truths computed
by hand from the 2026 calendar (2026-01-01 is a Thursday and
2026-10-19 is a Monday): each delimiter format, the weekday
resolution heuristics, preamble handling, gap arithmetic including
out-of-order dates, summary statistics, the filter modes, and the
strict input-validation error matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import JournalParserTool
from agentuniverse.agent.action.tool.common_tool.journal_parser_tool import (
    JournalParserTool as DirectJournalParserTool,
)

# --------------------------------------------------------------------- #
# Ground-truth journals (calendar facts verified by hand for 2026:
# 2026-01-01 is a Thursday; 2026-10-19 is a Monday)
# --------------------------------------------------------------------- #

JOURNAL_MULTI = (
    "Worklog — kept weekly.\n"
    "\n"
    "2026-10-19 - Sprint planning\n"
    "- agreed on the API shape\n"
    "- filed three follow-up tickets\n"
    "\n"
    "2026/10/20\n"
    "pair programming on the parser all day\n"
    "\n"
    "10/21/2026: bug fixing\n"
    "shipped the hotfix\n"
    "\n"
    "## 2026-10-22\n"
    "wrote the regression tests\n"
)

JOURNAL_CJK = (
    "2026年10月19日 周会\n"
    "讨论了发布计划\n"
    "2026年11月1日 复盘\n"
    "检查了线上指标\n"
)

JOURNAL_WEEKDAY = (
    "2026-10-19 kickoff standup\n"
    "Tuesday follow-up with the team\n"
    "Friday release cut\n"
    "Sunday retro\n"
)

JOURNAL_WEEKDAY_UNANCHORED = (
    "Monday no anchor yet\n"
    "2026-10-21 midweek note\n"
)

JOURNAL_REFYEAR = "Monday plan\nTuesday build\nMonday ship\n"

JOURNAL_REFYEAR_THEN_EXPLICIT = (
    "Monday early note\n"
    "2026-10-19 real start\n"
    "Tuesday first task\n"
)

JOURNAL_OUT_OF_ORDER_EXPLICIT = "2026-10-19 first\n2026-10-18 second\n"

JOURNAL_OUT_OF_ORDER_WEEKDAY = (
    "2026-10-21 wed note\n"
    "Monday earlier-in-week note\n"
)

JOURNAL_TOLERANCE = (
    "journal start\n"
    "2026-13-01 bad month\n"
    "2026-02-30 bad day\n"
    "13/45/2026 bad us date\n"
    "2026年13月1日 bad cjk month\n"
    "2026-10-19abc glued letters\n"
    "2026-10-19 real entry\n"
    "done\n"
)

JOURNAL_FILTER = (
    "2026-10-19 alpha\n"
    "notes about the deploy pipeline\n"
    "\n"
    "2026-10-20 beta\n"
    "Deployed the hotfix\n"
    "\n"
    "2026-10-23 gamma\n"
    "unrelated content\n"
)

JOURNAL_NO_DELIMITER = "just prose, no dated headings here at all\n"

JOURNAL_HEADING_WEEKDAY = "2026-10-20 base\n## Friday wrap\n"

JOURNAL_DEEP_INDENT = "    2026-10-19 indented like a code block\n"

JOURNAL_SINGLE_LINE = "2026-10-21 one-liner entry"


class JournalParserToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib JournalParserTool."""

    def setUp(self) -> None:
        self.tool = JournalParserTool()

    # ------------------------------------------------------------------ #
    # parse mode — delimiter formats
    # ------------------------------------------------------------------ #

    def test_parse_multi_format_entries(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_MULTI)
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["entry_count"], 4)
        self.assertEqual(result["total_lines"], 14)
        self.assertEqual(result["ignored_delimiters"], [])

        first, second, third, fourth = result["entries"]

        self.assertEqual(
            first,
            {
                "index": 1,
                "line_start": 3,
                "line_end": 6,
                "date": "2026-10-19",
                "raw_date": "2026-10-19",
                "inferred": False,
                "title": "Sprint planning",
                "lines": 4,
                "text": (
                    "2026-10-19 - Sprint planning\n"
                    "- agreed on the API shape\n"
                    "- filed three follow-up tickets\n"
                ),
                "next_date_gap_days": 1,
            },
        )
        self.assertEqual(
            (second["date"], second["raw_date"], second["title"]),
            ("2026-10-20", "2026/10/20", ""),
        )
        self.assertEqual((second["line_start"], second["line_end"]), (7, 9))
        self.assertEqual(second["lines"], 3)
        self.assertEqual(second["next_date_gap_days"], 1)
        self.assertEqual(
            (third["date"], third["raw_date"], third["title"]),
            ("2026-10-21", "10/21/2026", "bug fixing"),
        )
        self.assertEqual((third["line_start"], third["line_end"]), (10, 12))
        self.assertEqual(third["lines"], 3)
        self.assertEqual(third["next_date_gap_days"], 1)
        self.assertEqual(
            (fourth["date"], fourth["raw_date"], fourth["inferred"]),
            ("2026-10-22", "2026-10-22", False),
        )
        self.assertEqual((fourth["line_start"], fourth["line_end"]), (13, 14))
        self.assertIsNone(fourth["next_date_gap_days"])
        self.assertEqual(
            fourth["text"], "## 2026-10-22\nwrote the regression tests"
        )

    def test_parse_preamble_reported_separately(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_MULTI)
        self.assertEqual(result["preamble_lines"], 2)
        self.assertEqual(result["preamble"], "Worklog — kept weekly.\n")

    def test_parse_cjk_delimiter(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_CJK)
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["preamble_lines"], 0)
        self.assertEqual(result["preamble"], "")
        first, second = result["entries"]
        self.assertEqual(
            (first["date"], first["raw_date"], first["title"]),
            ("2026-10-19", "2026年10月19日", "周会"),
        )
        self.assertEqual(first["lines"], 2)
        self.assertEqual(
            (second["date"], second["raw_date"], second["title"]),
            ("2026-11-01", "2026年11月1日", "复盘"),
        )
        # October has 31 days: 2026-10-19 -> 2026-11-01 is 13 days.
        self.assertEqual(first["next_date_gap_days"], 13)
        self.assertIsNone(second["next_date_gap_days"])

    def test_parse_single_line_entry_at_eof(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_SINGLE_LINE)
        self.assertEqual(result["entry_count"], 1)
        entry = result["entries"][0]
        self.assertEqual((entry["line_start"], entry["line_end"]), (1, 1))
        self.assertEqual(entry["lines"], 1)
        self.assertEqual(entry["text"], "2026-10-21 one-liner entry")
        self.assertIsNone(entry["next_date_gap_days"])

    def test_parse_no_delimiters_is_all_preamble(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_NO_DELIMITER)
        self.assertEqual(result["entry_count"], 0)
        self.assertEqual(result["entries"], [])
        self.assertEqual(result["preamble_lines"], 1)
        self.assertEqual(result["preamble"], JOURNAL_NO_DELIMITER.rstrip("\n"))

    def test_parse_deep_indented_date_is_not_a_delimiter(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_DEEP_INDENT)
        self.assertEqual(result["entry_count"], 0)
        self.assertEqual(result["ignored_delimiters"], [])

    def test_parse_round_trips_exactly(self) -> None:
        # preamble + all entry texts reconstruct the input (modulo the
        # final trailing newline, which splitlines never returns).
        result = self.tool.execute(mode="parse", text=JOURNAL_MULTI)
        chunks = [result["preamble"]] + [e["text"] for e in result["entries"]]
        self.assertEqual("\n".join(chunks), JOURNAL_MULTI.rstrip("\n"))

    # ------------------------------------------------------------------ #
    # parse mode — weekday heuristic (ground truths for 2026)
    # ------------------------------------------------------------------ #

    def test_parse_weekday_attaches_to_recent_explicit_week(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_WEEKDAY)
        self.assertEqual(result["entry_count"], 4)
        first, tuesday, friday, sunday = result["entries"]
        self.assertEqual(
            (first["date"], first["raw_date"], first["inferred"]),
            ("2026-10-19", "2026-10-19", False),
        )
        # 2026-10-19 is a Monday; that week runs 10-19 .. 10-25.
        self.assertEqual(
            (tuesday["date"], tuesday["raw_date"], tuesday["inferred"]),
            ("2026-10-20", "Tuesday", True),
        )
        self.assertEqual(first["next_date_gap_days"], 1)
        self.assertEqual(tuesday["next_date_gap_days"], 3)
        self.assertEqual(friday["date"], "2026-10-23")
        self.assertEqual(friday["next_date_gap_days"], 2)
        self.assertEqual(sunday["date"], "2026-10-25")
        self.assertIsNone(sunday["next_date_gap_days"])

    def test_parse_weekday_heading_marker(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_HEADING_WEEKDAY)
        self.assertEqual(result["entry_count"], 2)
        base, wrap = result["entries"]
        self.assertEqual(base["date"], "2026-10-20")
        # 2026-10-20 is a Tuesday, so its week starts Monday 10-19 and
        # Friday of that week is 2026-10-23.
        self.assertEqual(wrap["date"], "2026-10-23")
        self.assertEqual(wrap["raw_date"], "Friday")
        self.assertEqual(wrap["title"], "wrap")

    def test_parse_unanchored_weekday_tolerated_as_content(self) -> None:
        result = self.tool.execute(
            mode="parse", text=JOURNAL_WEEKDAY_UNANCHORED
        )
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(result["entries"][0]["date"], "2026-10-21")
        self.assertEqual(len(result["ignored_delimiters"]), 1)
        ignored = result["ignored_delimiters"][0]
        self.assertEqual(ignored["line_number"], 1)
        self.assertEqual(ignored["reason"], "unresolvable_weekday")
        self.assertIn("Monday no anchor yet", result["preamble"])

    def test_parse_weekday_with_reference_year(self) -> None:
        # 2026-01-01 is a Thursday: first Monday is 01-05, Tuesday is
        # 01-06, and the next Monday after that Tuesday is 01-12.
        result = self.tool.execute(
            mode="parse", text=JOURNAL_REFYEAR, reference_year=2026
        )
        self.assertEqual(result["entry_count"], 3)
        first, second, third = result["entries"]
        self.assertEqual(
            (first["date"], first["raw_date"], first["inferred"]),
            ("2026-01-05", "Monday", True),
        )
        self.assertEqual(first["next_date_gap_days"], 1)
        self.assertEqual(second["date"], "2026-01-06")
        self.assertEqual(second["next_date_gap_days"], 6)
        self.assertEqual(third["date"], "2026-01-12")
        self.assertIsNone(third["next_date_gap_days"])
        self.assertEqual(result["ignored_delimiters"], [])

    def test_parse_reference_year_string_accepted(self) -> None:
        result = self.tool.execute(
            mode="parse", text=JOURNAL_REFYEAR, reference_year="2026"
        )
        self.assertEqual(
            [e["date"] for e in result["entries"]],
            ["2026-01-05", "2026-01-06", "2026-01-12"],
        )

    def test_parse_reference_year_superseded_by_explicit_date(self) -> None:
        result = self.tool.execute(
            mode="parse", text=JOURNAL_REFYEAR_THEN_EXPLICIT, reference_year=2026
        )
        self.assertEqual(result["entry_count"], 3)
        early, start, task = result["entries"]
        # Day-of-year: Jan 5 = 5, Oct 19 = 292 -> 287 days apart.
        self.assertEqual(early["date"], "2026-01-05")
        self.assertEqual(early["next_date_gap_days"], 287)
        self.assertEqual(start["date"], "2026-10-19")
        self.assertEqual(start["inferred"], False)
        self.assertEqual(start["next_date_gap_days"], 1)
        self.assertEqual(task["date"], "2026-10-20")
        self.assertIsNone(task["next_date_gap_days"])

    def test_parse_weekday_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="parse", text="2026-10-19 base\nMONDAY same week\n"
        )
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["entries"][1]["raw_date"], "MONDAY")
        self.assertEqual(result["entries"][1]["date"], "2026-10-19")
        self.assertEqual(result["entries"][0]["next_date_gap_days"], 0)
        self.assertIsNone(result["entries"][1]["next_date_gap_days"])

    # ------------------------------------------------------------------ #
    # parse mode — tolerance for delimiter look-alikes
    # ------------------------------------------------------------------ #

    def test_parse_lookalike_lines_tolerated_and_reported(self) -> None:
        result = self.tool.execute(mode="parse", text=JOURNAL_TOLERANCE)
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(result["entries"][0]["date"], "2026-10-19")
        self.assertEqual(result["entries"][0]["lines"], 2)
        ignored = result["ignored_delimiters"]
        self.assertEqual(
            [(i["line_number"], i["reason"]) for i in ignored],
            [
                (2, "invalid_date"),
                (3, "invalid_date"),
                (4, "invalid_date"),
                (5, "invalid_date"),
                (6, "ambiguous_boundary"),
            ],
        )
        # Tolerated lines stay as content (they precede the first real
        # delimiter, so they are part of the preamble).
        self.assertEqual(result["preamble_lines"], 6)
        for line in (
            "2026-13-01 bad month",
            "2026-02-30 bad day",
            "13/45/2026 bad us date",
            "2026年13月1日 bad cjk month",
            "2026-10-19abc glued letters",
        ):
            self.assertIn(line, result["preamble"])

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def test_summary_multi_format_stats(self) -> None:
        result = self.tool.execute(mode="summary", text=JOURNAL_MULTI)
        self.assertEqual(result["mode"], "summary")
        self.assertEqual(result["entry_count"], 4)
        self.assertEqual(result["total_lines"], 14)
        self.assertEqual(result["preamble_lines"], 2)
        self.assertEqual(result["date_min"], "2026-10-19")
        self.assertEqual(result["date_max"], "2026-10-22")
        self.assertEqual(result["date_range_days"], 3)
        self.assertEqual(result["mean_gap_days"], 1.0)
        self.assertEqual(result["max_gap_days"], 1)
        self.assertEqual(result["out_of_order_count"], 0)
        self.assertEqual(result["out_of_order_entries"], [])
        self.assertEqual(result["ignored_delimiter_count"], 0)
        self.assertEqual(
            result["per_entry_lines"],
            [
                {"index": 1, "date": "2026-10-19", "raw_date": "2026-10-19", "lines": 4},
                {"index": 2, "date": "2026-10-20", "raw_date": "2026/10/20", "lines": 3},
                {"index": 3, "date": "2026-10-21", "raw_date": "10/21/2026", "lines": 3},
                {"index": 4, "date": "2026-10-22", "raw_date": "2026-10-22", "lines": 2},
            ],
        )

    def test_summary_weekday_gaps(self) -> None:
        result = self.tool.execute(mode="summary", text=JOURNAL_WEEKDAY)
        self.assertEqual(result["date_min"], "2026-10-19")
        self.assertEqual(result["date_max"], "2026-10-25")
        self.assertEqual(result["date_range_days"], 6)
        # gaps are [1, 3, 2]
        self.assertEqual(result["mean_gap_days"], 2.0)
        self.assertEqual(result["max_gap_days"], 3)
        self.assertEqual(result["out_of_order_count"], 0)

    def test_summary_flags_out_of_order_explicit_dates(self) -> None:
        result = self.tool.execute(
            mode="summary", text=JOURNAL_OUT_OF_ORDER_EXPLICIT
        )
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["out_of_order_count"], 1)
        self.assertEqual(
            result["out_of_order_entries"],
            [
                {
                    "index": 2,
                    "date": "2026-10-18",
                    "previous_date": "2026-10-19",
                    "gap_days": -1,
                }
            ],
        )

    def test_summary_flags_out_of_order_weekday_resolution(self) -> None:
        # 2026-10-21 is a Wednesday; "Monday" attaches to the week
        # starting 2026-10-19, i.e. two days BEFORE the anchor.
        result = self.tool.execute(
            mode="summary", text=JOURNAL_OUT_OF_ORDER_WEEKDAY
        )
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["out_of_order_entries"][0]["gap_days"], -2)
        self.assertEqual(result["out_of_order_entries"][0]["date"], "2026-10-19")

    def test_summary_no_entries(self) -> None:
        result = self.tool.execute(mode="summary", text=JOURNAL_NO_DELIMITER)
        self.assertEqual(result["entry_count"], 0)
        self.assertIsNone(result["date_min"])
        self.assertIsNone(result["date_max"])
        self.assertIsNone(result["date_range_days"])
        self.assertIsNone(result["mean_gap_days"])
        self.assertIsNone(result["max_gap_days"])
        self.assertEqual(result["per_entry_lines"], [])
        self.assertEqual(result["out_of_order_count"], 0)

    def test_summary_single_entry(self) -> None:
        result = self.tool.execute(mode="summary", text=JOURNAL_SINGLE_LINE)
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(result["date_range_days"], 0)
        self.assertIsNone(result["mean_gap_days"])
        self.assertIsNone(result["max_gap_days"])

    def test_summary_counts_ignored_delimiters(self) -> None:
        result = self.tool.execute(mode="summary", text=JOURNAL_TOLERANCE)
        self.assertEqual(result["ignored_delimiter_count"], 5)

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def test_filter_substring_case_insensitive_by_default(self) -> None:
        result = self.tool.execute(
            mode="filter", text=JOURNAL_FILTER, substring="deploy"
        )
        self.assertEqual(result["mode"], "filter")
        self.assertEqual(result["entry_count"], 3)
        self.assertEqual(result["match_count"], 2)
        self.assertEqual([e["index"] for e in result["entries"]], [1, 2])
        self.assertEqual(
            result["criteria"],
            {
                "start_date": None,
                "end_date": None,
                "substring": "deploy",
                "case_sensitive": False,
            },
        )

    def test_filter_substring_case_sensitive(self) -> None:
        result = self.tool.execute(
            mode="filter",
            text=JOURNAL_FILTER,
            substring="Deploy",
            case_sensitive=True,
        )
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["entries"][0]["index"], 2)

    def test_filter_inclusive_date_range(self) -> None:
        result = self.tool.execute(
            mode="filter",
            text=JOURNAL_FILTER,
            start_date="2026-10-20",
            end_date="2026-10-20",
        )
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["entries"][0]["date"], "2026-10-20")

    def test_filter_start_only(self) -> None:
        result = self.tool.execute(
            mode="filter", text=JOURNAL_FILTER, start_date="2026-10-20"
        )
        self.assertEqual([e["index"] for e in result["entries"]], [2, 3])

    def test_filter_end_only(self) -> None:
        result = self.tool.execute(
            mode="filter", text=JOURNAL_FILTER, end_date="2026-10-19"
        )
        self.assertEqual([e["index"] for e in result["entries"]], [1])

    def test_filter_range_and_substring_combine_with_and(self) -> None:
        result = self.tool.execute(
            mode="filter",
            text=JOURNAL_FILTER,
            start_date="2026-10-20",
            end_date="2026-10-23",
            substring="hotfix",
        )
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["entries"][0]["index"], 2)

    def test_filter_no_match_is_not_an_error(self) -> None:
        result = self.tool.execute(
            mode="filter", text=JOURNAL_FILTER, substring="vacation"
        )
        self.assertEqual(result["match_count"], 0)
        self.assertEqual(result["entries"], [])

    def test_filter_text_without_delimiters(self) -> None:
        result = self.tool.execute(
            mode="filter", text=JOURNAL_NO_DELIMITER, substring="dates"
        )
        self.assertEqual(result["entry_count"], 0)
        self.assertEqual(result["match_count"], 0)

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_parse_is_deterministic(self) -> None:
        first = self.tool.execute(mode="parse", text=JOURNAL_MULTI)
        second = self.tool.execute(mode="parse", text=JOURNAL_MULTI)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="split", text=JOURNAL_MULTI)
        self.assert_invalid(mode=None, text=JOURNAL_MULTI)
        self.assert_invalid(mode=123, text=JOURNAL_MULTI)

    def test_invalid_text(self) -> None:
        for bad in (None, 123, True, b"journal", ["journal"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)
        self.assert_invalid(mode="parse", text="")
        self.assert_invalid(mode="parse", text="   \n  ")

    def test_text_length_limit(self) -> None:
        oversized = "2026-10-19 entry\n" + "line\n" * 40_000
        self.assert_invalid(mode="parse", text=oversized)
        # 5,000 one-line entries = 65,000 characters, still allowed.
        ok = self.tool.execute(mode="summary", text="2026-10-19 x\n" * 5_000)
        self.assertEqual(ok["entry_count"], 5_000)

    def test_invalid_reference_year(self) -> None:
        for bad in (True, 12.5, "abc", 0, 10000, ["2026"]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="parse", text=JOURNAL_REFYEAR, reference_year=bad
                )

    def test_invalid_filter_criteria(self) -> None:
        self.assert_invalid(mode="filter", text=JOURNAL_FILTER)
        self.assert_invalid(
            mode="filter", text=JOURNAL_FILTER, substring=""
        )
        self.assert_invalid(
            mode="filter", text=JOURNAL_FILTER, substring=123
        )
        self.assert_invalid(
            mode="filter", text=JOURNAL_FILTER, case_sensitive="yes"
        )

    def test_invalid_filter_bounds(self) -> None:
        for bad in ("2026/10/19", "2026-1-9", "20261019", "not-a-date", 20261019):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="filter", text=JOURNAL_FILTER, start_date=bad
                )
        self.assert_invalid(
            mode="filter", text=JOURNAL_FILTER, start_date="2026-02-30"
        )
        self.assert_invalid(
            mode="filter",
            text=JOURNAL_FILTER,
            start_date="2026-10-21",
            end_date="2026-10-19",
        )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectJournalParserTool, JournalParserTool)
        self.assertEqual(self.tool.name, "journal_parser_tool")
        self.assertIn("journal", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("JournalParserTool", __all__)


if __name__ == "__main__":
    unittest.main()
