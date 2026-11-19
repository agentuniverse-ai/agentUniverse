#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_range_generator_tool.py

"""Offline unit tests for RangeGeneratorTool.

The tool is built purely on the standard library (arithmetic,
datetime.date, decimal.Decimal) and never touches the network, so this
suite runs fully offline. Every assertion is deterministic: number
ranges are checked against literal expected lists (including exact
Decimal-stepped 0.1 increments), date ranges against hand-verified
calendars spanning month, year and leap-day boundaries, weekday lists
against known weekdays (2024-02-29 and 2026-10-16 are Thursdays /
Fridays respectively), and letter ranges against the alphabet. Error
inputs are checked against the ValueError matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import RangeGeneratorTool
from agentuniverse.agent.action.tool.common_tool.range_generator_tool import (
    RangeGeneratorTool as DirectRangeGeneratorTool,
)


class RangeGeneratorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib RangeGeneratorTool."""

    def setUp(self) -> None:
        self.tool = RangeGeneratorTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    # ------------------------------------------------------------------ #
    # numbers mode — int stepping
    # ------------------------------------------------------------------ #

    def test_numbers_int_range_inclusive_end(self) -> None:
        result = self.tool.execute(mode="numbers", start=0, end=10, step=2)
        self.assertEqual(
            result,
            {
                "mode": "numbers",
                "start": 0,
                "end": 10,
                "step": 2,
                "format": "number",
                "count": 6,
                "total": 6,
                "truncated": False,
                "result": [0, 2, 4, 6, 8, 10],
            },
        )

    def test_numbers_default_step_is_one(self) -> None:
        result = self.tool.execute(mode="numbers", start=1, end=4)
        self.assertEqual(result["step"], 1)
        self.assertEqual(result["result"], [1, 2, 3, 4])

    def test_numbers_exclusive_end_remainder_dropped(self) -> None:
        result = self.tool.execute(mode="numbers", start=0, end=10, step=3)
        # 0, 3, 6, 9 — the next value 12 overshoots end, 10 is never hit.
        self.assertEqual(result["result"], [0, 3, 6, 9])
        self.assertEqual(result["total"], 4)

    def test_numbers_single_value_range(self) -> None:
        result = self.tool.execute(mode="numbers", start=7, end=7, step=5)
        self.assertEqual(result["result"], [7])
        self.assertFalse(result["truncated"])

    def test_numbers_descending_negative_step(self) -> None:
        result = self.tool.execute(mode="numbers", start=10, end=0, step=-2)
        self.assertEqual(result["result"], [10, 8, 6, 4, 2, 0])
        self.assertEqual(result["total"], 6)

    def test_numbers_descending_float_step(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=1.0, end=0.0, step=-0.25
        )
        self.assertEqual(
            result["result"], [1.0, 0.75, 0.5, 0.25, 0.0]
        )

    # ------------------------------------------------------------------ #
    # numbers mode — exact Decimal float stepping
    # ------------------------------------------------------------------ #

    def test_numbers_float_step_no_binary_drift(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0.0, end=1.0, step=0.1
        )
        # Decimal stepping: 0.3 stays 0.3, never 0.30000000000000004,
        # and the end 1.0 is hit exactly and included.
        self.assertEqual(
            result["result"],
            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        )
        self.assertEqual(result["total"], 11)

    def test_numbers_float_range_inclusive_end(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0.1, end=0.4, step=0.1
        )
        self.assertEqual(result["result"], [0.1, 0.2, 0.3, 0.4])

    def test_numbers_float_step_exclusive_end(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0.0, end=0.95, step=0.2
        )
        # 0.0, 0.2, 0.4, 0.6, 0.8 — 1.0 would overshoot 0.95.
        self.assertEqual(result["result"], [0.0, 0.2, 0.4, 0.6, 0.8])

    def test_numbers_mixed_int_float_uses_decimal(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=1, end=2, step=0.5
        )
        self.assertEqual(result["result"], [1.0, 1.5, 2.0])

    # ------------------------------------------------------------------ #
    # numbers mode — formats
    # ------------------------------------------------------------------ #

    def test_numbers_format_hex(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=250, end=255, format="hex"
        )
        self.assertEqual(
            result["result"], ["fa", "fb", "fc", "fd", "fe", "ff"]
        )

    def test_numbers_format_bin(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=5, end=7, format="bin"
        )
        self.assertEqual(result["result"], ["101", "110", "111"])

    def test_numbers_format_padded(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=7, end=9, format="padded-3"
        )
        self.assertEqual(result["result"], ["007", "008", "009"])
        wide = self.tool.execute(
            mode="numbers", start=42, end=42, format="padded-6"
        )
        self.assertEqual(wide["result"], ["000042"])

    def test_numbers_format_int(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=2, end=6, step=2, format="int"
        )
        self.assertEqual(result["result"], [2, 4, 6])
        self.assertEqual(result["format"], "int")

    def test_numbers_format_float2(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0, end=1, step=0.125, format="float2"
        )
        # Half-up rounding to two decimals: 0.125 -> 0.13, 0.375 -> 0.38.
        self.assertEqual(
            result["result"],
            [0.0, 0.13, 0.25, 0.38, 0.5, 0.63, 0.75, 0.88, 1.0],
        )

    def test_numbers_format_default_is_number(self) -> None:
        result = self.tool.execute(mode="numbers", start=1, end=3)
        self.assertEqual(result["format"], "number")
        self.assertEqual(result["result"], [1, 2, 3])

    # ------------------------------------------------------------------ #
    # dates mode
    # ------------------------------------------------------------------ #

    def test_dates_daily_range(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2024-12-30", end="2025-01-02"
        )
        self.assertEqual(
            result["result"],
            ["2024-12-30", "2024-12-31", "2025-01-01", "2025-01-02"],
        )
        self.assertEqual(result["step_days"], 1)
        self.assertFalse(result["truncated"])

    def test_dates_monthly_step_across_leap_february(self) -> None:
        # 2024 is a leap year: Jan 31 + 29 days lands on Feb 29.
        result = self.tool.execute(
            mode="dates", start="2024-01-31", end="2024-03-31", step_days=29
        )
        self.assertEqual(
            result["result"], ["2024-01-31", "2024-02-29", "2024-03-29"]
        )

    def test_dates_inclusive_end_exact_hit(self) -> None:
        # Feb 1 + 29 days = Mar 1 in 2024, so the end is hit exactly.
        result = self.tool.execute(
            mode="dates", start="2024-02-01", end="2024-03-01", step_days=29
        )
        self.assertEqual(result["result"], ["2024-02-01", "2024-03-01"])
        self.assertEqual(result["total"], 2)

    def test_dates_non_leap_year_boundary(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2023-02-27", end="2023-03-02"
        )
        # 2023 has no Feb 29 — the sequence walks straight past it.
        self.assertEqual(
            result["result"],
            ["2023-02-27", "2023-02-28", "2023-03-01", "2023-03-02"],
        )

    def test_dates_descending_step(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2024-03-01", end="2024-02-01", step_days=-7
        )
        self.assertEqual(
            result["result"],
            [
                "2024-03-01",
                "2024-02-23",
                "2024-02-16",
                "2024-02-09",
                "2024-02-02",
            ],
        )

    def test_dates_exclusive_end_remainder_dropped(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2024-01-01", end="2024-01-10", step_days=4
        )
        # Jan 1, 5, 9 — Jan 13 would overshoot the end.
        self.assertEqual(
            result["result"],
            ["2024-01-01", "2024-01-05", "2024-01-09"],
        )

    def test_dates_year_boundary_negative(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2024-01-01", end="2023-12-24", step_days=-4
        )
        self.assertEqual(
            result["result"],
            ["2024-01-01", "2023-12-28", "2023-12-24"],
        )

    # ------------------------------------------------------------------ #
    # letters mode
    # ------------------------------------------------------------------ #

    def test_letters_lowercase_range(self) -> None:
        result = self.tool.execute(mode="letters", start="a", end="e")
        self.assertEqual(
            result,
            {
                "mode": "letters",
                "start": "a",
                "end": "e",
                "count": 5,
                "total": 5,
                "truncated": False,
                "result": ["a", "b", "c", "d", "e"],
            },
        )

    def test_letters_full_alphabet(self) -> None:
        result = self.tool.execute(mode="letters", start="a", end="z")
        self.assertEqual(result["result"], list("abcdefghijklmnopqrstuvwxyz"))
        self.assertEqual(result["total"], 26)

    def test_letters_uppercase_range(self) -> None:
        result = self.tool.execute(mode="letters", start="X", end="Z")
        self.assertEqual(result["result"], ["X", "Y", "Z"])

    def test_letters_descending(self) -> None:
        result = self.tool.execute(mode="letters", start="z", end="w")
        self.assertEqual(result["result"], ["z", "y", "x", "w"])

    def test_letters_single_letter(self) -> None:
        result = self.tool.execute(mode="letters", start="m", end="m")
        self.assertEqual(result["result"], ["m"])

    # ------------------------------------------------------------------ #
    # weekday mode
    # ------------------------------------------------------------------ #

    def test_weekday_next_fridays_same_day_included(self) -> None:
        # 2026-10-16 is itself a Friday — the same-day rule includes it.
        result = self.tool.execute(
            mode="weekday", start="2026-10-16", weekday="Friday", count=3
        )
        self.assertEqual(
            result,
            {
                "mode": "weekday",
                "start": "2026-10-16",
                "weekday": "friday",
                "count": 3,
                "total": 3,
                "truncated": False,
                "result": ["2026-10-16", "2026-10-23", "2026-10-30"],
            },
        )

    def test_weekday_from_non_matching_start(self) -> None:
        # 2026-10-20 is a Tuesday — the list starts at the next Friday.
        result = self.tool.execute(
            mode="weekday", start="2026-10-20", weekday="friday", count=2
        )
        self.assertEqual(result["result"], ["2026-10-23", "2026-10-30"])

    def test_weekday_default_count_is_one(self) -> None:
        result = self.tool.execute(
            mode="weekday", start="2024-02-29", weekday="thu"
        )
        # 2024-02-29 (leap day) is a Thursday, so it is the first item.
        self.assertEqual(result["result"], ["2024-02-29"])
        self.assertEqual(result["count"], 1)

    def test_weekday_abbreviation_and_case(self) -> None:
        result = self.tool.execute(
            mode="weekday", start="2024-01-01", weekday="MON", count=3
        )
        # 2024-01-01 is a Monday.
        self.assertEqual(
            result["result"],
            ["2024-01-01", "2024-01-08", "2024-01-15"],
        )
        self.assertEqual(result["weekday"], "mon")

    def test_weekday_spans_month_and_year_boundary(self) -> None:
        # 2023-12-31 is a Sunday; the next Sundays cross into 2024.
        result = self.tool.execute(
            mode="weekday", start="2023-12-31", weekday="sunday", count=3
        )
        self.assertEqual(
            result["result"],
            ["2023-12-31", "2024-01-07", "2024-01-14"],
        )

    # ------------------------------------------------------------------ #
    # Cap and truncation reporting
    # ------------------------------------------------------------------ #

    def test_numbers_cap_default_500_reports_total(self) -> None:
        result = self.tool.execute(mode="numbers", start=0, end=10_000)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["count"], 500)
        self.assertEqual(result["total"], 10_001)
        self.assertEqual(len(result["result"]), 500)
        self.assertEqual(result["result"][:3], [0, 1, 2])
        self.assertEqual(result["result"][-1], 499)

    def test_numbers_huge_range_total_computed_arithmetically(self) -> None:
        # A 10**18-step range must not be materialized to report its total.
        result = self.tool.execute(mode="numbers", start=0, end=10**18)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["total"], 10**18 + 1)
        self.assertEqual(result["count"], 500)

    def test_numbers_max_count_override(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0, end=9, max_count=3
        )
        self.assertTrue(result["truncated"])
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["result"], [0, 1, 2])

    def test_numbers_max_count_larger_than_range(self) -> None:
        result = self.tool.execute(
            mode="numbers", start=0, end=5, max_count=1000
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(result["count"], 6)

    def test_dates_cap_reports_total(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2000-01-01", end="2001-12-31"
        )
        self.assertTrue(result["truncated"])
        self.assertEqual(result["total"], 731)
        self.assertEqual(result["count"], 500)
        self.assertEqual(result["result"][-1], "2001-05-14")

    def test_weekday_count_over_cap_truncates(self) -> None:
        result = self.tool.execute(
            mode="weekday", start="2026-10-16", weekday="friday", count=600
        )
        self.assertTrue(result["truncated"])
        self.assertEqual(result["total"], 600)
        self.assertEqual(result["count"], 500)
        self.assertEqual(result["result"][0], "2026-10-16")
        self.assertEqual(len(result["result"]), 500)

    def test_letters_under_cap_not_truncated(self) -> None:
        result = self.tool.execute(mode="letters", start="a", end="z")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["count"], 26)

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_all_modes_deterministic_across_calls(self) -> None:
        calls = [
            {"mode": "numbers", "start": 0.0, "end": 1.0, "step": 0.1},
            {"mode": "dates", "start": "2024-01-31", "end": "2024-03-31",
             "step_days": 29},
            {"mode": "letters", "start": "z", "end": "a"},
            {"mode": "weekday", "start": "2026-10-16", "weekday": "fri",
             "count": 4},
        ]
        for kwargs in calls:
            self.assertEqual(
                self.tool.execute(**kwargs), self.tool.execute(**kwargs)
            )

    # ------------------------------------------------------------------ #
    # Input-validation error matrix
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="range", start=0, end=1)
        self.assert_invalid(mode=None)
        self.assert_invalid(mode="NUMBERS", start=0, end=1)

    def test_invalid_number_inputs(self) -> None:
        self.assert_invalid(mode="numbers", start="0", end=1)
        self.assert_invalid(mode="numbers", start=0, end="1")
        self.assert_invalid(mode="numbers", start=True, end=1)
        self.assert_invalid(mode="numbers", end=1)
        self.assert_invalid(mode="numbers", start=0)
        self.assert_invalid(mode="numbers", start=0, end=1, step="2")

    def test_non_finite_numbers_rejected(self) -> None:
        self.assert_invalid(mode="numbers", start=float("nan"), end=1)
        self.assert_invalid(mode="numbers", start=0, end=float("inf"))
        self.assert_invalid(
            mode="numbers", start=0, end=1, step=float("-inf")
        )

    def test_zero_step_rejected(self) -> None:
        self.assert_invalid(mode="numbers", start=0, end=1, step=0)
        self.assert_invalid(mode="numbers", start=0, end=1, step=0.0)
        self.assert_invalid(mode="numbers", start=0, end=1, step=-0.0)

    def test_direction_violations_rejected(self) -> None:
        # start > end with a positive step is rejected, never swapped.
        self.assert_invalid(mode="numbers", start=5, end=1, step=2)
        self.assert_invalid(mode="numbers", start=1.5, end=0.5, step=0.5)
        self.assert_invalid(mode="numbers", start=1, end=5, step=-2)
        self.assert_invalid(mode="numbers", start=0.5, end=1.5, step=-0.5)

    def test_invalid_format(self) -> None:
        base = {"mode": "numbers", "start": 0, "end": 4}
        self.assert_invalid(**base, format="decimal")
        self.assert_invalid(**base, format="")
        self.assert_invalid(**base, format=5)
        self.assert_invalid(**base, format=True)
        self.assert_invalid(**base, format="padded-0")
        self.assert_invalid(**base, format="padded-65")
        self.assert_invalid(**base, format="padded-x")
        self.assert_invalid(**base, format="padded-")

    def test_int_only_formats_reject_float_ranges(self) -> None:
        base = {"mode": "numbers", "start": 0.0, "end": 1.0, "step": 0.5}
        for fmt in ("int", "hex", "bin", "padded-3"):
            self.assert_invalid(**base, format=fmt)

    def test_invalid_date_strings(self) -> None:
        self.assert_invalid(mode="dates", start="20240101", end="2024-01-31")
        self.assert_invalid(mode="dates", start="2024-1-1", end="2024-01-31")
        self.assert_invalid(mode="dates", start="2024/01/01", end="2024-01-31")
        self.assert_invalid(mode="dates", start="24-01-01", end="2024-01-31")
        self.assert_invalid(mode="dates", start=20240101, end="2024-01-31")
        self.assert_invalid(mode="dates", start=None, end="2024-01-31")
        self.assert_invalid(mode="dates", start="2024-01-01")
        self.assert_invalid(mode="dates", start="2024-01-01 10:00", end="2024-01-31")

    def test_calendar_invalid_dates_rejected(self) -> None:
        # 2023 is not a leap year and April has 30 days.
        self.assert_invalid(mode="dates", start="2023-02-29", end="2023-03-31")
        self.assert_invalid(mode="dates", start="2024-02-29", end="2024-04-31")
        self.assert_invalid(mode="dates", start="2024-01-01", end="2024-13-01")
        self.assert_invalid(mode="dates", start="2024-01-01", end="2024-01-32")

    def test_valid_leap_day_accepted(self) -> None:
        result = self.tool.execute(
            mode="dates", start="2024-02-28", end="2024-03-01"
        )
        self.assertEqual(
            result["result"], ["2024-02-28", "2024-02-29", "2024-03-01"]
        )

    def test_invalid_date_step(self) -> None:
        self.assert_invalid(
            mode="dates", start="2024-01-01", end="2024-01-31", step_days=0
        )
        self.assert_invalid(
            mode="dates", start="2024-01-01", end="2024-01-31", step_days=1.5
        )
        self.assert_invalid(
            mode="dates", start="2024-01-01", end="2024-01-31", step_days="7"
        )

    def test_date_direction_violations_rejected(self) -> None:
        self.assert_invalid(
            mode="dates", start="2024-02-01", end="2024-01-01"
        )
        self.assert_invalid(
            mode="dates", start="2024-01-01", end="2024-02-01", step_days=-1
        )

    def test_invalid_letter_bounds(self) -> None:
        self.assert_invalid(mode="letters", start="ab", end="e")
        self.assert_invalid(mode="letters", start="a", end="5")
        self.assert_invalid(mode="letters", start="1", end="5")
        self.assert_invalid(mode="letters", start="", end="e")
        self.assert_invalid(mode="letters", start="a")
        self.assert_invalid(mode="letters", end="e")
        self.assert_invalid(mode="letters", start=1, end=5)
        # Mixed case would cross the ord gap between 'Z' and 'a'.
        self.assert_invalid(mode="letters", start="a", end="Z")
        self.assert_invalid(mode="letters", start="Y", end="b")
        self.assert_invalid(mode="letters", start="é", end="ë")

    def test_invalid_weekday_inputs(self) -> None:
        base = {"mode": "weekday", "start": "2026-10-16"}
        self.assert_invalid(**base, weekday="funday", count=2)
        self.assert_invalid(**base, weekday="f", count=2)
        self.assert_invalid(**base, weekday=4, count=2)
        self.assert_invalid(**base, count=2)
        self.assert_invalid(**base, weekday="2026-10-16")
        self.assert_invalid(
            mode="weekday", weekday="friday", count=2
        )
        self.assert_invalid(
            mode="weekday", start="2026-13-16", weekday="friday", count=2
        )

    def test_invalid_count(self) -> None:
        base = {"mode": "weekday", "start": "2026-10-16", "weekday": "fri"}
        self.assert_invalid(**base, count=0)
        self.assert_invalid(**base, count=-3)
        self.assert_invalid(**base, count=2.0)
        self.assert_invalid(**base, count=True)
        self.assert_invalid(**base, count="3")

    def test_invalid_max_count(self) -> None:
        base = {"mode": "numbers", "start": 0, "end": 10}
        self.assert_invalid(**base, max_count=0)
        self.assert_invalid(**base, max_count=-1)
        self.assert_invalid(**base, max_count=10_001)
        self.assert_invalid(**base, max_count=2.5)
        self.assert_invalid(**base, max_count=True)
        self.assert_invalid(**base, max_count="100")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectRangeGeneratorTool, RangeGeneratorTool)
        self.assertEqual(self.tool.name, "range_generator_tool")
        self.assertIn("numbers", self.tool.description)
        self.assertEqual(self.tool.max_count, 500)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("RangeGeneratorTool", __all__)


if __name__ == "__main__":
    unittest.main()
