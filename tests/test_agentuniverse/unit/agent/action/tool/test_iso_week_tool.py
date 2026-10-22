#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_iso_week_tool.py

"""Offline unit tests for IsoWeekTool.

The tool is built purely on the standard library ``datetime`` and
never touches the network or the clock, so this suite runs fully
offline and every assertion is deterministic.

Two kinds of ground truth are combined. Famous ISO-8601 boundary
dates are pinned as literal expected values (``2021-01-01`` is
``2020-W53-5``, ``2016-01-03`` is ``2015-W53-7``, ``2015-12-28`` is
``2015-W53-1``), and structural properties — week bounds, long-year
week 53 validity, cross-year shifts, inclusive counting — are
verified against ``datetime.date.isocalendar`` /
``datetime.date.fromisocalendar`` sweeps so nothing depends on a
hand-copied year table.
"""

import datetime
import unittest

from agentuniverse.agent.action.tool.common_tool import IsoWeekTool
from agentuniverse.agent.action.tool.common_tool.iso_week_tool import (
    IsoWeekTool as DirectIsoWeekTool,
    WEEKDAY_NAMES,
)


def iter_days(start: datetime.date, end: datetime.date):
    """Yield every date from start to end inclusive."""
    day = start
    one = datetime.timedelta(days=1)
    while day <= end:
        yield day
        day += one


class IsoWeekToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib IsoWeekTool."""

    def setUp(self) -> None:
        self.tool = IsoWeekTool()

    # ------------------------------------------------------------------ #
    # info mode — famous ISO boundary dates (literal ground truth)
    # ------------------------------------------------------------------ #

    def test_info_famous_boundary_dates(self) -> None:
        # Dec 29 - Jan 4 belongs to exactly one ISO year: these three
        # literals pin the rule at the most commonly mis-mapped spots.
        cases = [
            # (date, iso_year, iso_week, weekday, weekday_name)
            ("2021-01-01", 2020, 53, 5, "Friday"),
            ("2016-01-03", 2015, 53, 7, "Sunday"),
            ("2015-12-28", 2015, 53, 1, "Monday"),
        ]
        for date_str, iso_year, iso_week, weekday, weekday_name in cases:
            with self.subTest(date=date_str):
                self.assertEqual(
                    self.tool.execute(mode="info", date=date_str),
                    {
                        "mode": "info",
                        "input": date_str,
                        "iso_year": iso_year,
                        "iso_week": iso_week,
                        "weekday": weekday,
                        "weekday_name": weekday_name,
                        "iso_week_date": (
                            f"{iso_year:04d}-W{iso_week:02d}-{weekday}"
                        ),
                    },
                )

    def test_info_plain_date(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="info", date="2026-10-20"),
            {
                "mode": "info",
                "input": "2026-10-20",
                "iso_year": 2026,
                "iso_week": 43,
                "weekday": 2,
                "weekday_name": "Tuesday",
                "iso_week_date": "2026-W43-2",
            },
        )

    def test_info_iso_week_date_format(self) -> None:
        # The ISO week date is always YYYY-Www-d with zero padding.
        result = self.tool.execute(mode="info", date="2027-01-04")
        self.assertEqual(result["iso_week_date"], "2027-W01-1")

    def test_info_weekday_names_monday_to_sunday(self) -> None:
        # 2026-W43 runs Mon 2026-10-19 .. Sun 2026-10-25.
        for offset, expected_name in enumerate(WEEKDAY_NAMES):
            day = datetime.date(2026, 10, 19) + datetime.timedelta(days=offset)
            result = self.tool.execute(mode="info", date=day.isoformat())
            self.assertEqual(result["weekday"], offset + 1)
            self.assertEqual(result["weekday_name"], expected_name)

    def test_info_matches_isocalendar_sweep(self) -> None:
        # Ten years of every single day, checked against the stdlib
        # itself — covers both cross-year boundaries and long years
        # (2020, 2026) without any hardcoded table.
        for day in iter_days(
            datetime.date(2019, 1, 1), datetime.date(2028, 12, 31)
        ):
            iso_year, iso_week, weekday = day.isocalendar()
            result = self.tool.execute(mode="info", date=day.isoformat())
            self.assertEqual(result["iso_year"], iso_year)
            self.assertEqual(result["iso_week"], iso_week)
            self.assertEqual(result["weekday"], weekday)
            self.assertEqual(
                result["iso_week_date"],
                f"{iso_year:04d}-W{iso_week:02d}-{weekday}",
            )

    # ------------------------------------------------------------------ #
    # week_bounds mode
    # ------------------------------------------------------------------ #

    def test_week_bounds_from_week_spec(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="week_bounds", date="2026-W43"),
            {
                "mode": "week_bounds",
                "iso_year": 2026,
                "iso_week": 43,
                "monday": "2026-10-19",
                "sunday": "2026-10-25",
                "input": "2026-W43",
            },
        )

    def test_week_bounds_from_date_snaps_to_monday(self) -> None:
        # A mid-week date still resolves to the containing week's
        # Monday..Sunday span.
        self.assertEqual(
            self.tool.execute(mode="week_bounds", date="2026-10-22"),
            {
                "mode": "week_bounds",
                "iso_year": 2026,
                "iso_week": 43,
                "monday": "2026-10-19",
                "sunday": "2026-10-25",
                "input": "2026-10-22",
            },
        )

    def test_week_bounds_week_spanning_gregorian_new_year(self) -> None:
        # ISO weeks are Monday..Sunday regardless of the Gregorian
        # year: 2021-W01 starts Monday 2021-01-04 because Jan 1-3
        # still belong to 2020-W53.
        result = self.tool.execute(mode="week_bounds", date="2021-W01")
        self.assertEqual(result["monday"], "2021-01-04")
        self.assertEqual(result["sunday"], "2021-01-10")
        result = self.tool.execute(mode="week_bounds", date="2026-W53")
        self.assertEqual(result["monday"], "2026-12-28")
        self.assertEqual(result["sunday"], "2027-01-03")

    def test_week_bounds_matches_fromisocalendar_sweep(self) -> None:
        # Every week of five ISO years (including the long years 2015,
        # 2020 and 2026) against fromisocalendar ground truth.
        for year in (2014, 2015, 2020, 2025, 2026):
            last_week = datetime.date(year, 12, 28).isocalendar()[1]
            for week in range(1, last_week + 1):
                with self.subTest(year=year, week=week):
                    result = self.tool.execute(
                        mode="week_bounds", date=f"{year:04d}-W{week:02d}"
                    )
                    self.assertEqual(
                        result["monday"],
                        datetime.date.fromisocalendar(year, week, 1).isoformat(),
                    )
                    self.assertEqual(
                        result["sunday"],
                        datetime.date.fromisocalendar(year, week, 7).isoformat(),
                    )

    # ------------------------------------------------------------------ #
    # from_week mode — week 53 validity in long vs short years
    # ------------------------------------------------------------------ #

    def test_from_week_first_and_last_week_of_long_year(self) -> None:
        # 2026 starts on a Thursday -> long ISO year with 53 weeks.
        # The long-year property itself is re-derived below from
        # isocalendar, never assumed from a year table.
        result = self.tool.execute(mode="from_week", iso_year=2026, week=1)
        self.assertTrue(result["valid"])
        self.assertEqual(result["monday"], "2025-12-29")
        self.assertEqual(result["sunday"], "2026-01-04")
        result = self.tool.execute(mode="from_week", iso_year=2026, week=53)
        self.assertTrue(result["valid"])
        self.assertEqual(result["monday"], "2026-12-28")
        self.assertEqual(result["sunday"], "2027-01-03")
        result = self.tool.execute(mode="from_week", iso_year=2026, week=52)
        self.assertTrue(result["valid"])
        self.assertEqual(result["monday"], "2026-12-21")
        self.assertEqual(result["sunday"], "2026-12-27")

    def test_from_week_invalid_53_in_short_years(self) -> None:
        # 2016, 2021, 2025 and 2027 have only 52 ISO weeks: their
        # would-be week 53 Monday already falls into the next ISO
        # year's week 1 (e.g. 2025-12-29 is 2026-W01-1).
        for year in (2016, 2021, 2025, 2027):
            with self.subTest(year=year):
                result = self.tool.execute(
                    mode="from_week", iso_year=year, week=53
                )
                self.assertFalse(result["valid"])
                self.assertEqual(result["iso_year"], year)
                self.assertEqual(result["week"], 53)
                self.assertIn("52 weeks", result["reason"])
                self.assertNotIn("monday", result)
                self.assertNotIn("sunday", result)

    def test_from_week_validity_and_bounds_vs_isocalendar_sweep(self) -> None:
        # Fifty years: weeks 1..53 each. Ground truth comes from the
        # stdlib itself: fromisocalendar raises for a nonexistent
        # week, and Dec 28 always lies in the last week of an ISO
        # year, so it is in week 53 exactly for long years — no
        # hardcoded year table anywhere.
        for year in range(1990, 2040):
            has_53 = (
                datetime.date(year, 12, 28).isocalendar()[:2] == (year, 53)
            )
            for week in range(1, 54):
                with self.subTest(year=year, week=week):
                    try:
                        expected_monday = datetime.date.fromisocalendar(
                            year, week, 1
                        )
                        exists = expected_monday.isocalendar()[:2] == (
                            year,
                            week,
                        )
                    except ValueError:
                        exists = False
                    result = self.tool.execute(
                        mode="from_week", iso_year=year, week=week
                    )
                    self.assertEqual(result["valid"], exists)
                    if exists:
                        self.assertEqual(
                            result["monday"], expected_monday.isoformat()
                        )
                        self.assertEqual(
                            result["sunday"],
                            datetime.date.fromisocalendar(
                                year, week, 7
                            ).isoformat(),
                        )
            # A short year never reports week 53, a long year always
            # does — computed from the calendar, not hardcoded.
            result53 = self.tool.execute(
                mode="from_week", iso_year=year, week=53
            )
            self.assertEqual(result53["valid"], has_53)

    @staticmethod
    def _monday_of(iso_year: int, week: int) -> datetime.date:
        """Independent Monday computation (Jan 4 anchor)."""
        jan4 = datetime.date(iso_year, 1, 4)
        week1_monday = jan4 - datetime.timedelta(days=jan4.weekday())
        return week1_monday + datetime.timedelta(weeks=week - 1)

    def test_from_week_accepts_string_numbers(self) -> None:
        result = self.tool.execute(
            mode="from_week", iso_year="2026", week="42"
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["monday"], "2026-10-12")

    # ------------------------------------------------------------------ #
    # add_weeks mode
    # ------------------------------------------------------------------ #

    def test_add_weeks_forward_across_year_boundary(self) -> None:
        result = self.tool.execute(mode="add_weeks", date="2020-W53", weeks=1)
        self.assertEqual(result["iso_year"], 2021)
        self.assertEqual(result["iso_week"], 1)
        self.assertEqual(result["monday"], "2021-01-04")
        self.assertEqual(result["sunday"], "2021-01-10")

    def test_add_weeks_backward_across_year_boundary(self) -> None:
        result = self.tool.execute(mode="add_weeks", date="2021-W01", weeks=-1)
        self.assertEqual(result["iso_year"], 2020)
        self.assertEqual(result["iso_week"], 53)
        self.assertEqual(result["monday"], "2020-12-28")

    def test_add_weeks_from_date_uses_containing_week(self) -> None:
        # 2021-01-01 lives in 2020-W53; stepping back one week lands on
        # 2020-W52 whose Monday is 2020-12-21 (not the input date
        # minus seven days).
        result = self.tool.execute(mode="add_weeks", date="2021-01-01", weeks=-1)
        self.assertEqual(result["iso_year"], 2020)
        self.assertEqual(result["iso_week"], 52)
        self.assertEqual(result["monday"], "2020-12-21")

    def test_add_weeks_zero_shift_is_identity(self) -> None:
        result = self.tool.execute(mode="add_weeks", date="2026-W43", weeks=0)
        self.assertEqual(result["iso_week"], 43)
        self.assertEqual(result["monday"], "2026-10-19")

    def test_add_weeks_matches_isocalendar_sweep(self) -> None:
        # Every week around three ISO year transitions, ±5 weeks,
        # checked against fromisocalendar of (monday + N weeks).
        for year in (2020, 2021, 2026):
            for week in range(48, 54):
                monday = self._monday_of(year, week)
                if monday.isocalendar()[0] != year:
                    continue
                for shift in (-5, -1, 1, 5):
                    with self.subTest(year=year, week=week, shift=shift):
                        result = self.tool.execute(
                            mode="add_weeks",
                            date=f"{year:04d}-W{week:02d}",
                            weeks=shift,
                        )
                        shifted = monday + datetime.timedelta(weeks=shift)
                        self.assertEqual(
                            result["monday"], shifted.isoformat()
                        )
                        self.assertEqual(
                            result["sunday"],
                            (
                                shifted + datetime.timedelta(days=6)
                            ).isoformat(),
                        )
                        iso = shifted.isocalendar()
                        self.assertEqual(result["iso_year"], iso[0])
                        self.assertEqual(result["iso_week"], iso[1])

    def test_add_weeks_round_trip(self) -> None:
        for anchor in ("2026-W01", "2020-W53", "2015-W50"):
            for shift in (-60, -1, 1, 17, 60):
                with self.subTest(anchor=anchor, shift=shift):
                    forward = self.tool.execute(
                        mode="add_weeks", date=anchor, weeks=shift
                    )
                    back = self.tool.execute(
                        mode="add_weeks",
                        date=f"{forward['iso_year']:04d}-W"
                        f"{forward['iso_week']:02d}",
                        weeks=-shift,
                    )
                    self.assertEqual(
                        back["monday"],
                        self.tool.execute(
                            mode="week_bounds", date=anchor
                        )["monday"],
                    )

    # ------------------------------------------------------------------ #
    # weeks_between mode
    # ------------------------------------------------------------------ #

    def test_weeks_between_inclusive_semantics(self) -> None:
        # Same week counts as one; a four-week span counts four.
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2026-W42", end="2026-W42"
            )["weeks"],
            1,
        )
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2026-W40", end="2026-W43"
            )["weeks"],
            4,
        )

    def test_weeks_between_mixed_date_and_week_inputs(self) -> None:
        # Friday of W01 to Monday of W02 spans two weeks inclusively.
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2026-01-02", end="2026-01-05"
            )["weeks"],
            2,
        )
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2026-01-05", end="2026-01-11"
            )["weeks"],
            1,
        )

    def test_weeks_between_across_year_boundary(self) -> None:
        # Inclusive count across 2020-W53 -> 2021: W50..W52, W53,
        # 2021-W01..W05 = 9 weeks.
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2020-W50", end="2021-W05"
            )["weeks"],
            9,
        )
        self.assertEqual(
            self.tool.execute(
                mode="weeks_between", start="2021-01-01", end="2021-01-03"
            )["weeks"],
            1,
        )

    def test_weeks_between_matches_monday_diff_sweep(self) -> None:
        for year in (2020, 2025, 2026):
            for week_a, week_b in ((1, 2), (30, 31), (50, 53), (1, 52)):
                with self.subTest(year=year, a=week_a, b=week_b):
                    monday_a = self._monday_of(year, week_a)
                    monday_b = self._monday_of(year, week_b)
                    if monday_a.isocalendar()[:2] != (year, week_a):
                        continue
                    if monday_b.isocalendar()[:2] != (year, week_b):
                        continue
                    result = self.tool.execute(
                        mode="weeks_between",
                        start=f"{year:04d}-W{week_a:02d}",
                        end=f"{year:04d}-W{week_b:02d}",
                    )
                    self.assertEqual(
                        result["weeks"],
                        (monday_b - monday_a).days // 7 + 1,
                    )

    # ------------------------------------------------------------------ #
    # range_weeks mode
    # ------------------------------------------------------------------ #

    def test_range_weeks_basic_listing(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="range_weeks", start="2026-W42", end="2026-W44"
            ),
            {
                "mode": "range_weeks",
                "start": "2026-W42",
                "end": "2026-W44",
                "count": 3,
                "weeks": ["2026-W42", "2026-W43", "2026-W44"],
            },
        )

    def test_range_weeks_single_week(self) -> None:
        result = self.tool.execute(
            mode="range_weeks", start="2026-W42", end="2026-W42"
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["weeks"], ["2026-W42"])

    def test_range_weeks_across_year_boundary(self) -> None:
        result = self.tool.execute(
            mode="range_weeks", start="2020-W51", end="2021-W02"
        )
        self.assertEqual(
            result["weeks"],
            ["2020-W51", "2020-W52", "2020-W53", "2021-W01", "2021-W02"],
        )
        self.assertEqual(result["count"], 5)

    def test_range_weeks_accepts_dates(self) -> None:
        result = self.tool.execute(
            mode="range_weeks", start="2026-10-19", end="2026-11-01"
        )
        self.assertEqual(result["weeks"], ["2026-W43", "2026-W44"])

    def test_range_weeks_cap_at_500(self) -> None:
        # Exactly 500 entries is allowed; 501 raises.
        result = self.tool.execute(
            mode="range_weeks", start="2016-W01", end="2025-W31"
        )
        self.assertEqual(result["count"], 500)
        self.assertEqual(len(result["weeks"]), 500)
        self.assertEqual(result["weeks"][0], "2016-W01")
        self.assertEqual(result["weeks"][-1], "2025-W31")
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="range_weeks", start="2016-W01", end="2025-W32"
            )

    # ------------------------------------------------------------------ #
    # Error matrix — strict validation raises before any computation
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="week", date="2026-W42")
        with self.assertRaises(ValueError):
            self.tool.execute()  # mode missing entirely

    def test_error_info_rejects_week_spec(self) -> None:
        # info resolves a single day; a week spec is not a date.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", date="2026-W42")

    def test_error_malformed_dates(self) -> None:
        for bad in (
            None,
            "",
            "2026-13-01",
            "2026-02-30",
            "2026-1-1",
            "20260101",
            "2026/10/20",
            " 2026-10-20",
            "2026-10-20 ",
            "2026-W42-1",
            "2026-10-20T00:00:00",
            20261020,
            True,
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="info", date=bad)

    def test_error_malformed_week_specs(self) -> None:
        for bad in (
            "2026-w42",
            "2026-W4",
            "2026-W042",
            "26-W42",
            "2026W42",
            "2026-W42 ",
            "2026-W00",
            "2026-W54",
            "2026-W99",
            2026,
            None,
            ["2026-W42"],
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="week_bounds", date=bad)

    def test_error_nonexistent_week_53_as_anchor(self) -> None:
        # A short year's week 53 may be *asked about* (from_week)
        # but never *used* as an anchor.
        for mode_and_args in (
            {"mode": "week_bounds", "date": "2025-W53"},
            {"mode": "add_weeks", "date": "2025-W53", "weeks": 1},
            {"mode": "weeks_between", "start": "2025-W53", "end": "2026-W02"},
            {"mode": "range_weeks", "start": "2025-W53", "end": "2026-W02"},
        ):
            with self.subTest(args=mode_and_args):
                with self.assertRaises(ValueError):
                    self.tool.execute(**mode_and_args)

    def test_from_week_week_53_of_final_iso_year(self) -> None:
        self.assertFalse(
            datetime.date(9999, 12, 28).isocalendar()[:2] == (9999, 53)
        )
        result = self.tool.execute(mode="from_week", iso_year=9999, week=53)
        self.assertFalse(result["valid"])
        self.assertEqual(result["iso_year"], 9999)
        self.assertEqual(result["week"], 53)
        self.assertIn("52 weeks", result["reason"])
        self.assertNotIn("monday", result)
        self.assertNotIn("sunday", result)

    def test_error_week_53_of_final_iso_year_as_anchor(self) -> None:
        for mode_and_args in (
            {"mode": "week_bounds", "date": "9999-W53"},
            {"mode": "add_weeks", "date": "9999-W53", "weeks": 1},
            {"mode": "weeks_between", "start": "9999-W53", "end": "9999-W53"},
            {"mode": "range_weeks", "start": "9999-W53", "end": "9999-W53"},
            {"mode": "week_bounds", "date": "0001-W53"},
        ):
            with self.subTest(args=mode_and_args):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(**mode_and_args)
                self.assertTrue(
                    str(ctx.exception).startswith("iso_week_tool:")
                )

    def test_error_final_week_bounds_end_beyond_range(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="week_bounds", date="9999-W52")
        self.assertTrue(str(ctx.exception).startswith("iso_week_tool:"))

    def test_error_week_spec_year_out_of_range(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="week_bounds", date="0000-W01")
        self.assertTrue(str(ctx.exception).startswith("iso_week_tool:"))

    def test_error_non_ascii_digit_inputs(self) -> None:
        arabic_year_week = "٢٠٢٦-W٤٢"
        arabic_week_only = "2026-W٤٢"
        arabic_date = "٢٠٢٦-١٠-٢٠"
        for bad in (arabic_year_week, arabic_week_only):
            with self.subTest(spec=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="week_bounds", date=bad)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="info", date=arabic_date)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="from_week", iso_year="٢٠٢٦", week="٤٢")
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="add_weeks", date="2026-W42", weeks="٤٢"
            )

    def test_error_from_week_parameter_bounds(self) -> None:
        for bad_year in (0, -1, 10000, 1.5, "2026x", True, None):
            with self.subTest(iso_year=bad_year):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="from_week", iso_year=bad_year, week=10
                    )
        for bad_week in (0, -1, 54, 1.5, "w10", True, None):
            with self.subTest(week=bad_week):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="from_week", iso_year=2026, week=bad_week
                    )

    def test_error_add_weeks_parameter(self) -> None:
        for bad in (None, "two", 1.5, True, 520001, -520001):
            with self.subTest(weeks=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="add_weeks", date="2026-W42", weeks=bad
                    )
        with self.assertRaises(ValueError):
            self.tool.execute(mode="add_weeks", date="2026-W42")

    def test_error_add_weeks_leaves_date_range(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="add_weeks", date="9999-W51", weeks=52)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="add_weeks", date="0001-W02", weeks=-52)

    def test_error_reversed_ranges(self) -> None:
        for mode in ("weeks_between", "range_weeks"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode=mode, start="2026-W44", end="2026-W42"
                    )

    def test_error_missing_start_or_end(self) -> None:
        for mode in ("weeks_between", "range_weeks"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, start="2026-W42")
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, end="2026-W42")

    def test_error_messages_name_the_tool(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="nonsense")
        self.assertTrue(str(ctx.exception).startswith("iso_week_tool:"))

    # ------------------------------------------------------------------ #
    # Determinism and module surface
    # ------------------------------------------------------------------ #

    def test_deterministic_repeated_calls(self) -> None:
        first = self.tool.execute(mode="range_weeks", start="2026-W40",
                                  end="2026-W44")
        second = self.tool.execute(mode="range_weeks", start="2026-W40",
                                   end="2026-W44")
        self.assertEqual(first, second)

    def test_exported_from_package_init(self) -> None:
        self.assertIs(DirectIsoWeekTool, IsoWeekTool)
        from agentuniverse.agent.action.tool.common_tool import (  # noqa: F401
            __all__ as common_tool_all,
        )

        self.assertIn("IsoWeekTool", common_tool_all)


if __name__ == "__main__":
    unittest.main()
