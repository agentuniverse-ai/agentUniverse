#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_date_range_tool.py

"""Offline unit tests for DateRangeTool.

The tool is built purely on the standard library (datetime.date) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: all day counts are hand-computed under the
documented INCLUSIVE-ends convention (a range [2026-01-01, 2026-01-03]
covers three days), including adjacent/touching ranges, nested ranges,
boundary-only overlaps, subtract splitting into two sub-ranges, and
leap-February spans (2024-02-29 exists, 2023-02-29 does not).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import DateRangeTool
from agentuniverse.agent.action.tool.common_tool.date_range_tool import (
    DateRangeTool as DirectDateRangeTool,
)


class DateRangeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib DateRangeTool."""

    def setUp(self) -> None:
        self.tool = DateRangeTool()

    # ------------------------------------------------------------------ #
    # intersect mode
    # ------------------------------------------------------------------ #

    def test_intersect_partial_overlap(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-20"],
        )
        # Shared days: Jan 5..10 = 6 days inclusive.
        self.assertEqual(
            result,
            {
                "mode": "intersect",
                "range_a": ["2026-01-01", "2026-01-10"],
                "range_b": ["2026-01-05", "2026-01-20"],
                "intersection": ["2026-01-05", "2026-01-10"],
                "days": 6,
                "gap_days": 0,
            },
        )

    def test_intersect_nested_range(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-01", "2026-01-31"],
            range_b=["2026-01-10", "2026-01-20"],
        )
        self.assertEqual(result["intersection"], ["2026-01-10", "2026-01-20"])
        # Jan 10..20 = 11 days inclusive.
        self.assertEqual(result["days"], 11)
        self.assertEqual(result["gap_days"], 0)

    def test_intersect_identical_ranges(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-03-01", "2026-03-05"],
            range_b=["2026-03-01", "2026-03-05"],
        )
        self.assertEqual(result["intersection"], ["2026-03-01", "2026-03-05"])
        self.assertEqual(result["days"], 5)

    def test_intersect_boundary_single_day(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-03-01", "2026-03-10"],
            range_b=["2026-03-10", "2026-03-20"],
        )
        # Inclusive ends: Mar 10 belongs to both ranges.
        self.assertEqual(result["intersection"], ["2026-03-10", "2026-03-10"])
        self.assertEqual(result["days"], 1)

    def test_intersect_disjoint_reports_gap(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-06", "2026-01-10"],
        )
        # Missing days between: Jan 4 and Jan 5 = 2 days.
        self.assertIsNone(result["intersection"])
        self.assertEqual(result["days"], 0)
        self.assertEqual(result["gap_days"], 2)

    def test_intersect_adjacent_touching_no_overlap(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-04", "2026-01-10"],
        )
        # Adjacent ranges share no calendar day, and no day is missing.
        self.assertIsNone(result["intersection"])
        self.assertEqual(result["gap_days"], 0)

    def test_intersect_argument_order_symmetric(self) -> None:
        first = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-05", "2026-01-20"],
            range_b=["2026-01-01", "2026-01-10"],
        )
        second = self.tool.execute(
            mode="intersect",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-20"],
        )
        self.assertEqual(first["intersection"], second["intersection"])
        self.assertEqual(first["days"], second["days"])
        self.assertEqual(first["gap_days"], second["gap_days"])

    def test_intersect_leap_february_span(self) -> None:
        result = self.tool.execute(
            mode="intersect",
            range_a=["2024-02-27", "2024-03-02"],
            range_b=["2024-02-28", "2024-03-01"],
        )
        # Shared days: Feb 28, Feb 29 (leap), Mar 1 = 3 days.
        self.assertEqual(result["intersection"], ["2024-02-28", "2024-03-01"])
        self.assertEqual(result["days"], 3)

    # ------------------------------------------------------------------ #
    # union mode
    # ------------------------------------------------------------------ #

    def test_union_overlapping_merges(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-20"],
        )
        self.assertEqual(
            result,
            {
                "mode": "union",
                "range_a": ["2026-01-01", "2026-01-10"],
                "range_b": ["2026-01-05", "2026-01-20"],
                "union": [["2026-01-01", "2026-01-20"]],
                "merged": True,
                "gap_days": 0,
            },
        )

    def test_union_adjacent_touching_merges(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-04", "2026-01-10"],
        )
        # No calendar hole between Jan 3 and Jan 4, so they merge.
        self.assertEqual(result["union"], [["2026-01-01", "2026-01-10"]])
        self.assertTrue(result["merged"])
        self.assertEqual(result["gap_days"], 0)

    def test_union_disjoint_keeps_both_with_gap(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-06", "2026-01-10"],
        )
        self.assertEqual(
            result["union"],
            [["2026-01-01", "2026-01-03"], ["2026-01-06", "2026-01-10"]],
        )
        self.assertFalse(result["merged"])
        self.assertEqual(result["gap_days"], 2)

    def test_union_nested_merges_to_outer(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2026-01-01", "2026-01-31"],
            range_b=["2026-01-10", "2026-01-20"],
        )
        self.assertEqual(result["union"], [["2026-01-01", "2026-01-31"]])
        self.assertTrue(result["merged"])

    def test_union_argument_order_symmetric(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2026-01-06", "2026-01-10"],
            range_b=["2026-01-01", "2026-01-03"],
        )
        # Output is normalized: the earlier range first.
        self.assertEqual(
            result["union"],
            [["2026-01-01", "2026-01-03"], ["2026-01-06", "2026-01-10"]],
        )
        self.assertEqual(result["gap_days"], 2)

    def test_union_leap_february_chain(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=["2024-02-27", "2024-02-28"],
            range_b=["2024-02-29", "2024-03-01"],
        )
        # Feb 29 2024 exists, so the two ranges touch and merge.
        self.assertEqual(result["union"], [["2024-02-27", "2024-03-01"]])
        self.assertTrue(result["merged"])

    # ------------------------------------------------------------------ #
    # contains mode
    # ------------------------------------------------------------------ #

    def test_contains_mixed_verdicts_preserve_order(self) -> None:
        result = self.tool.execute(
            mode="contains",
            range_a=["2026-01-10", "2026-01-20"],
            dates=[
                "2026-01-09",
                "2026-01-10",
                "2026-01-15",
                "2026-01-20",
                "2026-01-21",
            ],
        )
        self.assertEqual(
            result["results"],
            [
                {"date": "2026-01-09", "contained": False},
                {"date": "2026-01-10", "contained": True},
                {"date": "2026-01-15", "contained": True},
                {"date": "2026-01-20", "contained": True},
                {"date": "2026-01-21", "contained": False},
            ],
        )
        self.assertEqual(result["contained_count"], 3)
        self.assertEqual(result["total"], 5)

    def test_contains_leap_day(self) -> None:
        result = self.tool.execute(
            mode="contains",
            range_a=["2024-02-01", "2024-03-01"],
            dates=["2024-02-28", "2024-02-29", "2024-03-01"],
        )
        self.assertEqual(
            [item["contained"] for item in result["results"]], [True, True, True]
        )

    def test_contains_single_day_range(self) -> None:
        result = self.tool.execute(
            mode="contains",
            range_a=["2026-05-01", "2026-05-01"],
            dates=["2026-04-30", "2026-05-01", "2026-05-02"],
        )
        self.assertEqual(
            [item["contained"] for item in result["results"]], [False, True, False]
        )

    def test_contains_accepts_tuple_inputs(self) -> None:
        result = self.tool.execute(
            mode="contains",
            range_a=("2026-01-01", "2026-01-31"),
            dates=("2026-01-15",),
        )
        self.assertEqual(result["contained_count"], 1)

    # ------------------------------------------------------------------ #
    # overlaps mode
    # ------------------------------------------------------------------ #

    def test_overlaps_partial(self) -> None:
        result = self.tool.execute(
            mode="overlaps",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-20"],
        )
        self.assertTrue(result["overlaps"])
        self.assertEqual(result["overlap_days"], 6)

    def test_overlaps_boundary_single_day(self) -> None:
        result = self.tool.execute(
            mode="overlaps",
            range_a=["2026-03-01", "2026-03-10"],
            range_b=["2026-03-10", "2026-03-20"],
        )
        self.assertTrue(result["overlaps"])
        self.assertEqual(result["overlap_days"], 1)

    def test_overlaps_nested(self) -> None:
        result = self.tool.execute(
            mode="overlaps",
            range_a=["2026-01-01", "2026-01-31"],
            range_b=["2026-01-10", "2026-01-20"],
        )
        self.assertTrue(result["overlaps"])
        self.assertEqual(result["overlap_days"], 11)

    def test_overlaps_disjoint(self) -> None:
        result = self.tool.execute(
            mode="overlaps",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-06", "2026-01-10"],
        )
        self.assertFalse(result["overlaps"])
        self.assertEqual(result["overlap_days"], 0)

    def test_overlaps_adjacent_is_not_overlap(self) -> None:
        result = self.tool.execute(
            mode="overlaps",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-04", "2026-01-10"],
        )
        # Adjacent ranges share no calendar day.
        self.assertFalse(result["overlaps"])
        self.assertEqual(result["overlap_days"], 0)

    # ------------------------------------------------------------------ #
    # gap mode
    # ------------------------------------------------------------------ #

    def test_gap_disjoint(self) -> None:
        result = self.tool.execute(
            mode="gap",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-06", "2026-01-10"],
        )
        # Jan 4 and Jan 5 are uncovered between the two ranges.
        self.assertEqual(result["gap_days"], 2)
        self.assertFalse(result["overlaps"])

    def test_gap_single_missing_day(self) -> None:
        result = self.tool.execute(
            mode="gap",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-05", "2026-01-10"],
        )
        # Only Jan 4 is missing.
        self.assertEqual(result["gap_days"], 1)

    def test_gap_adjacent_is_zero(self) -> None:
        result = self.tool.execute(
            mode="gap",
            range_a=["2026-01-01", "2026-01-03"],
            range_b=["2026-01-04", "2026-01-10"],
        )
        self.assertEqual(result["gap_days"], 0)
        self.assertFalse(result["overlaps"])

    def test_gap_overlapping_is_zero(self) -> None:
        result = self.tool.execute(
            mode="gap",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-20"],
        )
        self.assertEqual(result["gap_days"], 0)
        self.assertTrue(result["overlaps"])

    def test_gap_argument_order_symmetric(self) -> None:
        first = self.tool.execute(
            mode="gap",
            range_a=["2026-01-06", "2026-01-10"],
            range_b=["2026-01-01", "2026-01-03"],
        )
        self.assertEqual(first["gap_days"], 2)

    def test_gap_across_leap_day(self) -> None:
        result = self.tool.execute(
            mode="gap",
            range_a=["2024-02-27", "2024-02-28"],
            range_b=["2024-03-01", "2024-03-05"],
        )
        # Only Feb 29 (leap) is missing between the two ranges.
        self.assertEqual(result["gap_days"], 1)

    # ------------------------------------------------------------------ #
    # subtract mode
    # ------------------------------------------------------------------ #

    def test_subtract_inner_splits_into_two(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-01", "2026-01-31"],
            range_b=["2026-01-10", "2026-01-20"],
        )
        self.assertEqual(
            result["difference"],
            [["2026-01-01", "2026-01-09"], ["2026-01-21", "2026-01-31"]],
        )
        # Removed: Jan 10..20 = 11 days.
        self.assertEqual(result["removed_days"], 11)

    def test_subtract_bites_right(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-05", "2026-01-31"],
        )
        self.assertEqual(result["difference"], [["2026-01-01", "2026-01-04"]])
        self.assertEqual(result["removed_days"], 6)

    def test_subtract_bites_left(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-05", "2026-01-31"],
            range_b=["2026-01-01", "2026-01-10"],
        )
        self.assertEqual(result["difference"], [["2026-01-11", "2026-01-31"]])
        self.assertEqual(result["removed_days"], 6)

    def test_subtract_identical_ranges(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-02-01", "2026-02-10"],
            range_b=["2026-02-01", "2026-02-10"],
        )
        self.assertEqual(result["difference"], [])
        self.assertEqual(result["removed_days"], 10)

    def test_subtract_b_covers_a_entirely(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-02-05", "2026-02-08"],
            range_b=["2026-01-01", "2026-03-01"],
        )
        self.assertEqual(result["difference"], [])
        self.assertEqual(result["removed_days"], 4)

    def test_subtract_b_disjoint_before(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-10", "2026-01-20"],
            range_b=["2026-01-01", "2026-01-05"],
        )
        self.assertEqual(result["difference"], [["2026-01-10", "2026-01-20"]])
        self.assertEqual(result["removed_days"], 0)

    def test_subtract_b_disjoint_after(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-10", "2026-01-20"],
            range_b=["2026-02-01", "2026-02-10"],
        )
        self.assertEqual(result["difference"], [["2026-01-10", "2026-01-20"]])
        self.assertEqual(result["removed_days"], 0)

    def test_subtract_b_shares_start_with_a(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-01", "2026-01-03"],
        )
        # The left sub-range is empty, only the right remainder stays.
        self.assertEqual(result["difference"], [["2026-01-04", "2026-01-10"]])
        self.assertEqual(result["removed_days"], 3)

    def test_subtract_b_shares_end_with_a(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2026-01-01", "2026-01-10"],
            range_b=["2026-01-08", "2026-01-10"],
        )
        self.assertEqual(result["difference"], [["2026-01-01", "2026-01-07"]])
        self.assertEqual(result["removed_days"], 3)

    def test_subtract_leap_february(self) -> None:
        result = self.tool.execute(
            mode="subtract",
            range_a=["2024-02-27", "2024-03-02"],
            range_b=["2024-02-28", "2024-02-29"],
        )
        self.assertEqual(
            result["difference"],
            [["2024-02-27", "2024-02-27"], ["2024-03-01", "2024-03-02"]],
        )
        self.assertEqual(result["removed_days"], 2)

    # ------------------------------------------------------------------ #
    # multi_merge mode
    # ------------------------------------------------------------------ #

    def test_multi_merge_adjacent_chain_coalesces(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-01-01", "2026-01-02"],
                ["2026-01-03", "2026-01-04"],
                ["2026-01-05", "2026-01-06"],
            ],
        )
        self.assertEqual(result["merged"], [["2026-01-01", "2026-01-06"]])
        self.assertEqual(result["merged_count"], 1)
        self.assertEqual(result["input_count"], 3)

    def test_multi_merge_overlap_and_disjoint(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-01-01", "2026-01-05"],
                ["2026-01-04", "2026-01-10"],
                ["2026-02-01", "2026-02-10"],
            ],
        )
        self.assertEqual(
            result["merged"],
            [["2026-01-01", "2026-01-10"], ["2026-02-01", "2026-02-10"]],
        )
        self.assertEqual(result["merged_count"], 2)

    def test_multi_merge_unsorted_input_is_sorted(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-02-01", "2026-02-10"],
                ["2026-01-04", "2026-01-10"],
                ["2026-01-01", "2026-01-05"],
            ],
        )
        # Deterministic output regardless of the input order.
        self.assertEqual(
            result["merged"],
            [["2026-01-01", "2026-01-10"], ["2026-02-01", "2026-02-10"]],
        )

    def test_multi_merge_duplicates_collapse(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-01-01", "2026-01-05"],
                ["2026-01-01", "2026-01-05"],
            ],
        )
        self.assertEqual(result["merged"], [["2026-01-01", "2026-01-05"]])
        self.assertEqual(result["merged_count"], 1)

    def test_multi_merge_nested_chain(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-01-01", "2026-01-31"],
                ["2026-01-05", "2026-01-10"],
                ["2026-01-20", "2026-03-05"],
            ],
        )
        self.assertEqual(result["merged"], [["2026-01-01", "2026-03-05"]])

    def test_multi_merge_single_range(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[["2026-06-01", "2026-06-01"]],
        )
        self.assertEqual(result["merged"], [["2026-06-01", "2026-06-01"]])
        self.assertEqual(result["merged_count"], 1)

    def test_multi_merge_disjoint_stay_sorted(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2026-02-01", "2026-02-02"],
                ["2026-01-10", "2026-01-11"],
                ["2026-01-01", "2026-01-02"],
            ],
        )
        self.assertEqual(
            result["merged"],
            [
                ["2026-01-01", "2026-01-02"],
                ["2026-01-10", "2026-01-11"],
                ["2026-02-01", "2026-02-02"],
            ],
        )
        self.assertEqual(result["merged_count"], 3)

    def test_multi_merge_leap_february_chain(self) -> None:
        result = self.tool.execute(
            mode="multi_merge",
            ranges=[
                ["2024-02-27", "2024-02-28"],
                ["2024-02-29", "2024-03-01"],
                ["2024-03-02", "2024-03-02"],
            ],
        )
        # Feb 29 2024 glues the chain into a single contiguous block.
        self.assertEqual(result["merged"], [["2024-02-27", "2024-03-02"]])
        self.assertEqual(result["merged_count"], 1)

    # ------------------------------------------------------------------ #
    # Class surface
    # ------------------------------------------------------------------ #

    def test_direct_module_import_and_export(self) -> None:
        self.assertIs(DateRangeTool, DirectDateRangeTool)
        self.assertEqual(self.tool.name, "date_range_tool")
        self.assertIn("intersect", self.tool.MODES)
        self.assertIn("multi_merge", self.tool.MODES)

    def test_tuple_ranges_accepted(self) -> None:
        result = self.tool.execute(
            mode="union",
            range_a=("2026-01-01", "2026-01-03"),
            range_b=("2026-01-04", "2026-01-10"),
        )
        self.assertEqual(result["union"], [["2026-01-01", "2026-01-10"]])

    # ------------------------------------------------------------------ #
    # Error matrix (strict validation, precise messages)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, message_part: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn("date_range_tool:", str(ctx.exception))
        self.assertIn(message_part, str(ctx.exception))

    def test_error_unknown_mode(self) -> None:
        self.assert_invalid(
            "mode must be one of",
            mode="merge",
            range_a=["2026-01-01", "2026-01-02"],
            range_b=["2026-01-03", "2026-01-04"],
        )

    def test_error_missing_mode(self) -> None:
        self.assert_invalid("mode must be one of", mode=None)

    def test_error_range_a_wrong_element_count(self) -> None:
        self.assert_invalid(
            "exactly 2 elements",
            mode="gap",
            range_a=["2026-01-01"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_range_three_elements(self) -> None:
        self.assert_invalid(
            "exactly 2 elements",
            mode="gap",
            range_a=["2026-01-01", "2026-01-02", "2026-01-03"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_range_is_string_not_pair(self) -> None:
        self.assert_invalid(
            "must be a [start, end] pair",
            mode="gap",
            range_a="2026-01-01/2026-01-05",
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_non_string_start(self) -> None:
        self.assert_invalid(
            "range_a[0] (start) must be an ISO date string",
            mode="gap",
            range_a=[20260101, "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_bool_element(self) -> None:
        self.assert_invalid(
            "must be an ISO date string",
            mode="gap",
            range_a=[True, "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_slash_format_rejected(self) -> None:
        self.assert_invalid(
            "YYYY-MM-DD form",
            mode="gap",
            range_a=["2026/01/01", "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_padded_format_required(self) -> None:
        self.assert_invalid(
            "YYYY-MM-DD form",
            mode="gap",
            range_a=["2026-1-1", "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_compact_iso_rejected(self) -> None:
        # Python 3.11 date.fromisoformat accepts 20260101; the tool is
        # stricter and requires the padded YYYY-MM-DD form.
        self.assert_invalid(
            "YYYY-MM-DD form",
            mode="gap",
            range_a=["20260101", "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_impossible_calendar_date(self) -> None:
        self.assert_invalid(
            "not a valid calendar date",
            mode="gap",
            range_a=["2026-02-30", "2026-03-05"],
            range_b=["2026-04-01", "2026-04-02"],
        )

    def test_error_month_out_of_range(self) -> None:
        self.assert_invalid(
            "not a valid calendar date",
            mode="gap",
            range_a=["2026-13-01", "2026-12-05"],
            range_b=["2026-04-01", "2026-04-02"],
        )

    def test_error_feb_29_non_leap_year(self) -> None:
        self.assert_invalid(
            "not a valid calendar date",
            mode="gap",
            range_a=["2023-02-29", "2023-03-05"],
            range_b=["2026-04-01", "2026-04-02"],
        )

    def test_error_start_after_end(self) -> None:
        self.assert_invalid(
            "start must not be after end",
            mode="gap",
            range_a=["2026-01-10", "2026-01-05"],
            range_b=["2026-02-01", "2026-02-02"],
        )

    def test_error_start_after_end_in_range_b(self) -> None:
        self.assert_invalid(
            "start must not be after end",
            mode="gap",
            range_a=["2026-01-01", "2026-01-05"],
            range_b=["2026-02-10", "2026-02-02"],
        )

    def test_error_missing_range_b(self) -> None:
        self.assert_invalid(
            "range_b must be a [start, end] pair",
            mode="intersect",
            range_a=["2026-01-01", "2026-01-05"],
        )

    def test_error_missing_range_a(self) -> None:
        self.assert_invalid(
            "range_a must be a [start, end] pair",
            mode="overlaps",
            range_b=["2026-01-01", "2026-01-05"],
        )

    def test_error_contains_missing_dates(self) -> None:
        self.assert_invalid(
            "dates must be a list",
            mode="contains",
            range_a=["2026-01-01", "2026-01-31"],
        )

    def test_error_contains_empty_dates(self) -> None:
        self.assert_invalid(
            "at least one ISO date string",
            mode="contains",
            range_a=["2026-01-01", "2026-01-31"],
            dates=[],
        )

    def test_error_contains_bad_date_indexed(self) -> None:
        self.assert_invalid(
            "dates[2] must be an ISO date string",
            mode="contains",
            range_a=["2026-01-01", "2026-01-31"],
            dates=["2026-01-05", "2026-01-06", 42],
        )

    def test_error_dates_over_cap(self) -> None:
        self.assert_invalid(
            "1,000-item limit",
            mode="contains",
            range_a=["2026-01-01", "2026-01-31"],
            dates=["2026-01-05"] * 1001,
        )

    def test_error_multi_merge_missing_ranges(self) -> None:
        self.assert_invalid(
            "ranges must be a list",
            mode="multi_merge",
        )

    def test_error_multi_merge_empty_ranges(self) -> None:
        self.assert_invalid(
            "at least one range",
            mode="multi_merge",
            ranges=[],
        )

    def test_error_multi_merge_bad_inner_range_indexed(self) -> None:
        self.assert_invalid(
            "ranges[2][0] (start) must be an ISO date string",
            mode="multi_merge",
            ranges=[
                ["2026-01-01", "2026-01-05"],
                ["2026-02-01", "2026-02-05"],
                [None, "2026-03-05"],
            ],
        )

    def test_error_multi_merge_ranges_over_cap(self) -> None:
        self.assert_invalid(
            "1,000-range limit",
            mode="multi_merge",
            ranges=[["2026-01-01", "2026-01-05"]] * 1001,
        )


if __name__ == "__main__":
    unittest.main()
