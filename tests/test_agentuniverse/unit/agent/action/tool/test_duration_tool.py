#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_duration_tool.py

"""Offline unit tests for DurationTool.

The tool is built purely on the standard library (re-free scanners over
``decimal`` and ``datetime``) and never touches the network, so this
suite runs fully offline. Every assertion is deterministic: parse
results are checked against hand-computed ground truths (including the
fixed 1y=365d / 1mo=30d / 1w=7d conversions and the half-to-even
microsecond rounding rule), humanize outputs against the exact strings
documented for the compact / long / clock formats, ``between`` against
known timestamps, and ``add`` against exact arithmetic. Error handling
is covered by a full matrix: malformed parameters raise ``ValueError``
while content-level failures come back as structured ``error`` payloads.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import DurationTool
from agentuniverse.agent.action.tool.common_tool.duration_tool import (
    DurationTool as DirectDurationTool,
)

ZERO_PARTS = {
    "days": 0,
    "hours": 0,
    "minutes": 0,
    "seconds": 0,
    "milliseconds": 0,
    "microseconds": 0,
}


def parts(**overrides) -> dict:
    """A canonical parts dict with the given nonzero fields."""
    return {**ZERO_PARTS, **overrides}


class DurationToolParseTest(unittest.TestCase):
    """Offline deterministic test cases for the parse mode."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    # ------------------------------------------------------------------ #
    # ISO-8601 ground truths
    # ------------------------------------------------------------------ #

    def test_parse_iso_basic(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT1H30M")
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "input": "PT1H30M",
                "style": "iso8601",
                "negative": False,
                "total_seconds": 5400,
                "total_microseconds": 5_400_000_000,
                "parts": parts(hours=1, minutes=30),
                "iso8601": "PT1H30M",
                "humanized": "1h 30m",
                "result": 5400,
            },
        )

    def test_parse_iso_day_and_time(self) -> None:
        result = self.tool.execute(mode="parse", duration="P1DT2H")
        self.assertEqual(result["total_seconds"], 93600)
        self.assertEqual(result["parts"], parts(days=1, hours=2))
        self.assertEqual(result["iso8601"], "P1DT2H")

    def test_parse_iso_full_component_set(self) -> None:
        # 365d + 2*30d + 3*7d + 4d = 450 days; plus 5h 6m 7s.
        result = self.tool.execute(
            mode="parse", duration="P1Y2M3W4DT5H6M7S"
        )
        self.assertEqual(result["total_seconds"], 38_898_367)
        self.assertEqual(
            result["parts"], parts(days=450, hours=5, minutes=6, seconds=7)
        )
        self.assertEqual(result["iso8601"], "P450DT5H6M7S")

    def test_parse_iso_weeks(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P2W")["total_seconds"],
            14 * 86_400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P1W2D")["total_seconds"],
            9 * 86_400,
        )

    def test_parse_iso_month_is_not_minute(self) -> None:
        # 'P1M' is one nominal month (30 days); 'PT1M' is one minute.
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P1M")["total_seconds"],
            30 * 86_400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="PT1M")["total_seconds"],
            60,
        )

    def test_parse_iso_year_month_fixed_conversions(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P1Y")["total_seconds"],
            365 * 86_400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P1M2D")["total_seconds"],
            32 * 86_400,
        )

    def test_parse_iso_zero(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT0S")
        self.assertEqual(result["total_seconds"], 0)
        self.assertEqual(result["parts"], ZERO_PARTS)
        self.assertEqual(result["iso8601"], "PT0S")
        self.assertEqual(result["humanized"], "0s")

    def test_parse_iso_fractional_with_dot_and_comma(self) -> None:
        for text in ("PT1.5H", "PT1,5H"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", duration=text)
                self.assertEqual(result["total_seconds"], 5400)
                self.assertEqual(result["parts"], parts(hours=1, minutes=30))
        self.assertEqual(
            self.tool.execute(mode="parse", duration="P0.5D")["total_seconds"],
            43_200,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="PT0.5S")["total_seconds"],
            0.5,
        )

    def test_parse_iso_case_insensitive_and_surrounding_space(self) -> None:
        result = self.tool.execute(mode="parse", duration="  pt1h30m  ")
        self.assertEqual(result["total_seconds"], 5400)
        self.assertEqual(result["style"], "iso8601")
        self.assertEqual(result["iso8601"], "PT1H30M")

    def test_parse_iso_normalizes_canonical_form(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT90M")
        self.assertEqual(result["total_seconds"], 5400)
        self.assertEqual(result["parts"], parts(hours=1, minutes=30))
        self.assertEqual(result["iso8601"], "PT1H30M")

    def test_parse_iso_leading_plus(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="+PT1H")["total_seconds"],
            3600,
        )

    # ------------------------------------------------------------------ #
    # Shorthand ground truths
    # ------------------------------------------------------------------ #

    def test_parse_shorthand_units(self) -> None:
        result = self.tool.execute(mode="parse", duration="1d 2h 3m")
        self.assertEqual(result["total_seconds"], 93_780)
        self.assertEqual(result["style"], "shorthand")
        self.assertEqual(result["parts"], parts(days=1, hours=2, minutes=3))
        self.assertEqual(result["iso8601"], "P1DT2H3M")

    def test_parse_shorthand_without_spaces(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1d2h3m")["total_seconds"],
            93_780,
        )

    def test_parse_shorthand_single_unit(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="90m")["total_seconds"],
            5400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1.5h")["total_seconds"],
            5400,
        )

    def test_parse_shorthand_long_unit_words(self) -> None:
        result = self.tool.execute(
            mode="parse", duration="2 hours 15 minutes"
        )
        self.assertEqual(result["total_seconds"], 8100)
        self.assertEqual(result["parts"], parts(hours=2, minutes=15))

    def test_parse_shorthand_space_between_number_and_unit(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1 h 30 m")[
                "total_seconds"
            ],
            5400,
        )

    def test_parse_shorthand_subsecond_units(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="500ms")["total_seconds"],
            0.5,
        )
        result = self.tool.execute(mode="parse", duration="1500us")
        self.assertEqual(result["total_seconds"], 0.0015)
        self.assertEqual(result["total_microseconds"], 1500)
        self.assertEqual(
            result["parts"], parts(milliseconds=1, microseconds=500)
        )

    def test_parse_shorthand_micro_sign_and_greek_mu(self) -> None:
        # Both U+00B5 (micro sign) and U+03BC (Greek mu) mean microseconds.
        for text in ("1500µs", "1500μs"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", duration=text)
                self.assertEqual(result["total_microseconds"], 1500)

    def test_parse_shorthand_calendar_units(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1y")["total_seconds"],
            365 * 86_400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1mo")["total_seconds"],
            30 * 86_400,
        )
        self.assertEqual(
            self.tool.execute(mode="parse", duration="1w")["total_seconds"],
            7 * 86_400,
        )

    # ------------------------------------------------------------------ #
    # CJK units
    # ------------------------------------------------------------------ #

    def test_parse_cjk_full_expression(self) -> None:
        result = self.tool.execute(
            mode="parse", duration="3天2小时15分30秒"
        )
        self.assertEqual(result["total_seconds"], 267_330)
        self.assertEqual(
            result["parts"],
            parts(days=3, hours=2, minutes=15, seconds=30),
        )
        self.assertEqual(result["iso8601"], "P3DT2H15M30S")

    def test_parse_cjk_single_units(self) -> None:
        cases = [
            ("1天", 86_400),
            ("2时", 7_200),
            ("45分", 2_700),
            ("90秒", 90),
            ("30分钟", 1_800),
            ("45秒钟", 45),
            ("500毫秒", 0.5),
            ("1500微秒", 0.0015),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", duration=text)
                self.assertEqual(result["total_seconds"], expected)
                self.assertEqual(result["style"], "shorthand")

    def test_parse_cjk_matches_latin(self) -> None:
        cjk = self.tool.execute(mode="parse", duration="1天2小时")
        latin = self.tool.execute(mode="parse", duration="1d 2h")
        self.assertEqual(cjk["total_seconds"], latin["total_seconds"])
        self.assertEqual(cjk["parts"], latin["parts"])
        self.assertEqual(cjk["iso8601"], latin["iso8601"])

    # ------------------------------------------------------------------ #
    # ISO vs shorthand equivalence
    # ------------------------------------------------------------------ #

    def test_parse_iso_shorthand_equivalence(self) -> None:
        cases = [
            ("P1D", "1d"),
            ("PT2H", "2h"),
            ("PT90M", "90m"),
            ("PT1.5H", "1.5h"),
            ("P1DT2H", "1d 2h"),
            ("PT0.5S", "500ms"),
            ("P2W", "2w"),
            ("P1M", "1mo"),
        ]
        for iso, short in cases:
            with self.subTest(iso=iso, short=short):
                left = self.tool.execute(mode="parse", duration=iso)
                right = self.tool.execute(mode="parse", duration=short)
                self.assertEqual(
                    left["total_seconds"], right["total_seconds"]
                )
                self.assertEqual(left["parts"], right["parts"])
                self.assertEqual(left["iso8601"], right["iso8601"])
                self.assertEqual(left["humanized"], right["humanized"])

    # ------------------------------------------------------------------ #
    # Negative durations
    # ------------------------------------------------------------------ #

    def test_parse_negative_iso_with_flag(self) -> None:
        result = self.tool.execute(
            mode="parse", duration="-PT1H", allow_negative=True
        )
        self.assertEqual(result["negative"], True)
        self.assertEqual(result["total_seconds"], -3600)
        self.assertEqual(result["total_microseconds"], -3_600_000_000)
        self.assertEqual(result["parts"], parts(hours=1))
        self.assertEqual(result["iso8601"], "-PT1H")
        self.assertEqual(result["humanized"], "-1h")

    def test_parse_negative_shorthand_with_flag(self) -> None:
        result = self.tool.execute(
            mode="parse", duration="-1h 30m", allow_negative=True
        )
        self.assertEqual(result["total_seconds"], -5400)
        self.assertEqual(result["iso8601"], "-PT1H30M")
        self.assertEqual(result["humanized"], "-1h 30m")

    def test_parse_negative_without_flag_is_structured_error(self) -> None:
        for text in ("-PT1H", "-1h"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", duration=text)
                self.assertEqual(result["mode"], "parse")
                self.assertEqual(result["error"]["type"], "negative_duration")
                self.assertIn("allow_negative", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Rounding rules (half-to-even at microsecond granularity)
    # ------------------------------------------------------------------ #

    def test_parse_rounding_half_to_even(self) -> None:
        # 0.5us rounds to 0 (even); 1.5us rounds to 2 (even).
        result = self.tool.execute(mode="parse", duration="PT0.0000005S")
        self.assertEqual(result["total_microseconds"], 0)
        self.assertEqual(result["total_seconds"], 0)
        result = self.tool.execute(mode="parse", duration="PT0.0000015S")
        self.assertEqual(result["total_microseconds"], 2)
        self.assertEqual(result["total_seconds"], 2e-06)

    def test_parse_exact_microseconds_no_rounding(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT0.000001S")
        self.assertEqual(result["total_microseconds"], 1)
        self.assertEqual(result["parts"], parts(microseconds=1))
        self.assertEqual(result["humanized"], "1us")

    # ------------------------------------------------------------------ #
    # Magnitude caps
    # ------------------------------------------------------------------ #

    def test_parse_per_component_cap(self) -> None:
        result = self.tool.execute(
            mode="parse", duration="PT999999999999999S"
        )
        self.assertEqual(result["error"]["type"], "duration_too_large")

    def test_parse_total_cap(self) -> None:
        # 9 components near the per-component cap sum far above the
        # 10**12-second total cap.
        result = self.tool.execute(
            mode="parse",
            duration="P999999999999Y999999999999M999999999999W999999999999D"
            "T999999999999H999999999999M999999999999S",
        )
        self.assertEqual(result["error"]["type"], "duration_too_large")
        self.assertIn("cap", result["error"]["message"])

    def test_parse_just_under_total_cap(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT999999999999S")
        self.assertEqual(result["total_seconds"], 999_999_999_999)

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_parse_deterministic(self) -> None:
        first = self.tool.execute(mode="parse", duration="P1DT2H30M0.5S")
        second = self.tool.execute(mode="parse", duration="P1DT2H30M0.5S")
        self.assertEqual(first, second)


class DurationToolHumanizeTest(unittest.TestCase):
    """Offline deterministic test cases for the humanize mode."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    def assert_humanized(self, seconds, fmt, expected) -> None:
        result = self.tool.execute(
            mode="humanize", seconds=seconds, format=fmt
        )
        self.assertEqual(result["humanized"], expected)
        self.assertEqual(result["result"], result["total_seconds"])

    def test_humanize_reference_trio(self) -> None:
        # 26.5 hours rendered in every documented format.
        self.assert_humanized(95400, "compact", "26h 30m")
        self.assert_humanized(95400, "long", "1 day, 2:30:00")
        self.assert_humanized(95400, "clock", "26:30:00")

    def test_humanize_compact_never_folds_days(self) -> None:
        self.assert_humanized(86_400, "compact", "24h")
        self.assert_humanized(172_800, "compact", "48h")
        self.assert_humanized(2_673_30, "compact", "74h 15m 30s")

    def test_humanize_compact_keeps_intermediate_zero_units(self) -> None:
        # From the first nonzero unit down to the last, zeros stay.
        self.assert_humanized(3605, "compact", "1h 0m 5s")
        self.assert_humanized(95400.5, "compact", "26h 30m 0s 500ms")

    def test_humanize_compact_small_values(self) -> None:
        self.assert_humanized(1, "compact", "1s")
        self.assert_humanized(61, "compact", "1m 1s")
        self.assert_humanized(0.5, "compact", "500ms")
        self.assert_humanized(0.042, "compact", "42ms")
        self.assert_humanized(1.5, "compact", "1s 500ms")
        self.assert_humanized(0.000001, "compact", "1us")

    def test_humanize_long_below_one_day(self) -> None:
        self.assert_humanized(61, "long", "1 minute, 1 second")
        self.assert_humanized(3600, "long", "1 hour")
        self.assert_humanized(95400 - 86_400, "long", "2 hours, 30 minutes")
        self.assert_humanized(1.5, "long", "1 second, 500 milliseconds")
        self.assert_humanized(0.000001, "long", "1 microsecond")
        self.assert_humanized(0.5, "long", "500 milliseconds")

    def test_humanize_long_day_and_clock_remainder(self) -> None:
        self.assert_humanized(86_400, "long", "1 day")
        self.assert_humanized(86_401, "long", "1 day, 0:00:01")
        self.assert_humanized(90_061, "long", "1 day, 1:01:01")
        self.assert_humanized(172_800, "long", "2 days")

    def test_humanize_clock_format(self) -> None:
        self.assert_humanized(0, "clock", "0:00:00")
        self.assert_humanized(65, "clock", "0:01:05")
        self.assert_humanized(3600, "clock", "1:00:00")
        self.assert_humanized(86_400, "clock", "24:00:00")
        self.assert_humanized(0.5, "clock", "0:00:00.5")
        self.assert_humanized(0.042, "clock", "0:00:00.042")
        self.assert_humanized(1.5, "clock", "0:00:01.5")
        self.assert_humanized(0.000001, "clock", "0:00:00.000001")

    def test_humanize_zero(self) -> None:
        self.assert_humanized(0, "compact", "0s")
        self.assert_humanized(0, "long", "0 seconds")
        self.assert_humanized(0, "clock", "0:00:00")

    def test_humanize_default_format_is_compact(self) -> None:
        result = self.tool.execute(mode="humanize", seconds=95400)
        self.assertEqual(result["format"], "compact")
        self.assertEqual(result["humanized"], "26h 30m")

    def test_humanize_parts(self) -> None:
        result = self.tool.execute(mode="humanize", seconds=95400)
        self.assertEqual(
            result["parts"], parts(days=1, hours=2, minutes=30)
        )
        self.assertNotIn("iso8601", result)

    def test_humanize_accepts_string_and_float_seconds(self) -> None:
        self.assert_humanized("95400", "compact", "26h 30m")
        self.assert_humanized(95400.0, "clock", "26:30:00")

    def test_humanize_negative_with_flag(self) -> None:
        result = self.tool.execute(
            mode="humanize", seconds=-95400, allow_negative=True
        )
        self.assertEqual(result["negative"], True)
        self.assertEqual(result["humanized"], "-26h 30m")
        result = self.tool.execute(
            mode="humanize", seconds=-5, allow_negative=True, format="long"
        )
        self.assertEqual(result["humanized"], "-5 seconds")

    def test_humanize_negative_without_flag_is_structured_error(self) -> None:
        result = self.tool.execute(mode="humanize", seconds=-5)
        self.assertEqual(result["error"]["type"], "negative_duration")

    def test_humanize_magnitude_cap(self) -> None:
        result = self.tool.execute(mode="humanize", seconds=10 ** 13)
        self.assertEqual(result["error"]["type"], "duration_too_large")

    def test_humanize_rounding_half_to_even(self) -> None:
        # 0.5us -> 0us (even); 1.5us -> 2us (even).
        self.assert_humanized(0.0000005, "compact", "0s")
        self.assert_humanized(0.0000015, "compact", "2us")


class DurationToolBetweenTest(unittest.TestCase):
    """Offline deterministic test cases for the between mode."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    def test_between_naive_datetimes(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T10:00:00",
            end="2026-01-01T12:30:00",
        )
        self.assertEqual(result["total_seconds"], 9000)
        self.assertEqual(result["parts"], parts(hours=2, minutes=30))
        self.assertEqual(result["iso8601"], "PT2H30M")
        self.assertEqual(result["humanized"], "2h 30m")

    def test_between_dates(self) -> None:
        result = self.tool.execute(
            mode="between", start="2026-01-01", end="2026-01-02"
        )
        self.assertEqual(result["total_seconds"], 86_400)
        self.assertEqual(result["iso8601"], "P1D")

    def test_between_z_suffix_and_offsets(self) -> None:
        # 02:00+01:00 is 01:00Z, one hour after midnight Z.
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T00:00:00Z",
            end="2026-01-01T02:00:00+01:00",
        )
        self.assertEqual(result["total_seconds"], 3600)

    def test_between_aware_same_offset(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T00:00:00+08:00",
            end="2026-01-01T01:30:00+08:00",
        )
        self.assertEqual(result["total_seconds"], 5400)

    def test_between_fractional_seconds(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T00:00:00.5",
            end="2026-01-01T00:00:01",
            format="long",
        )
        self.assertEqual(result["total_seconds"], 0.5)
        self.assertEqual(result["humanized"], "500 milliseconds")

    def test_between_same_instant_is_zero(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T00:00:00",
            end="2026-01-01T00:00:00",
        )
        self.assertEqual(result["total_seconds"], 0)
        self.assertEqual(result["humanized"], "0s")

    def test_between_format_option(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T10:00:00",
            end="2026-01-01T12:30:00",
            format="long",
        )
        self.assertEqual(result["humanized"], "2 hours, 30 minutes")

    def test_between_end_before_start_without_flag(self) -> None:
        result = self.tool.execute(
            mode="between", start="2026-01-02", end="2026-01-01"
        )
        self.assertEqual(result["error"]["type"], "negative_duration")

    def test_between_end_before_start_with_flag(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-02T00:00:00",
            end="2026-01-01T00:00:00",
            allow_negative=True,
            format="long",
        )
        self.assertEqual(result["total_seconds"], -86_400)
        self.assertEqual(result["iso8601"], "-P1D")
        self.assertEqual(result["humanized"], "-1 day")

    def test_between_mixed_timezone_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="between",
            start="2026-01-01T00:00:00",
            end="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(result["error"]["type"], "mixed_timezone")
        self.assertIn("naive", result["error"]["message"])

    def test_between_invalid_datetime_is_structured_error(self) -> None:
        for bad in ("2026-13-01", "not a date", "2026-02-30"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="between", start=bad, end="2026-01-02"
                )
                self.assertEqual(result["error"]["type"], "invalid_datetime")


class DurationToolAddTest(unittest.TestCase):
    """Offline deterministic test cases for the add mode."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    def test_add_iso_hours_and_minutes(self) -> None:
        result = self.tool.execute(
            mode="add", duration="PT1H30M", other="PT45M"
        )
        self.assertEqual(result["operation"], "add")
        self.assertEqual(result["total_seconds"], 8100)
        self.assertEqual(result["parts"], parts(hours=2, minutes=15))
        self.assertEqual(result["iso8601"], "PT2H15M")
        self.assertEqual(result["humanized"], "2h 15m")

    def test_subtract_folds_into_canonical_form(self) -> None:
        result = self.tool.execute(
            mode="add", duration="1d 2h", other="3h", operation="subtract"
        )
        self.assertEqual(result["total_seconds"], 82_800)
        self.assertEqual(result["parts"], parts(hours=23))
        self.assertEqual(result["iso8601"], "PT23H")

    def test_subtract_negative_result_with_flag(self) -> None:
        result = self.tool.execute(
            mode="add",
            duration="1h",
            other="1h30m",
            operation="subtract",
            allow_negative=True,
        )
        self.assertEqual(result["total_seconds"], -1800)
        self.assertEqual(result["iso8601"], "-PT30M")
        self.assertEqual(result["humanized"], "-30m")

    def test_subtract_negative_result_without_flag(self) -> None:
        result = self.tool.execute(
            mode="add", duration="1h", other="1h30m", operation="subtract"
        )
        self.assertEqual(result["error"]["type"], "negative_duration")

    def test_add_negative_operand_with_flag(self) -> None:
        result = self.tool.execute(
            mode="add",
            duration="2h",
            other="-30m",
            allow_negative=True,
        )
        self.assertEqual(result["total_seconds"], 5400)

    def test_add_negative_operand_without_flag(self) -> None:
        result = self.tool.execute(mode="add", duration="2h", other="-30m")
        self.assertEqual(result["error"]["type"], "negative_duration")

    def test_add_mixed_styles(self) -> None:
        result = self.tool.execute(mode="add", duration="90m", other="1.5h")
        self.assertEqual(result["total_seconds"], 10_800)
        self.assertEqual(result["iso8601"], "PT3H")

    def test_add_zero(self) -> None:
        result = self.tool.execute(mode="add", duration="PT0S", other="PT0S")
        self.assertEqual(result["total_seconds"], 0)
        self.assertEqual(result["iso8601"], "PT0S")
        self.assertEqual(result["humanized"], "0s")

    def test_add_subsecond_precision(self) -> None:
        result = self.tool.execute(mode="add", duration="1ms", other="1500us")
        self.assertEqual(result["total_seconds"], 0.0025)
        self.assertEqual(result["total_microseconds"], 2500)
        self.assertEqual(result["iso8601"], "PT0.0025S")
        self.assertEqual(result["humanized"], "2ms 500us")

    def test_add_milliseconds_to_seconds(self) -> None:
        result = self.tool.execute(
            mode="add", duration="500ms", other="500ms"
        )
        self.assertEqual(result["total_seconds"], 1)
        self.assertEqual(result["iso8601"], "PT1S")
        self.assertEqual(result["humanized"], "1s")

    def test_add_format_option(self) -> None:
        result = self.tool.execute(
            mode="add",
            duration="PT1H30M",
            other="PT45M",
            format="clock",
        )
        self.assertEqual(result["humanized"], "2:15:00")


class DurationToolErrorMatrixTest(unittest.TestCase):
    """Content-level structured errors and parameter-level ValueErrors."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    # ---------------------- structured payloads ---------------------- #

    def assert_error(self, error_type: str, **kwargs) -> None:
        result = self.tool.execute(**kwargs)
        self.assertEqual(result["error"]["type"], error_type)

    def test_parse_iso_unknown_unit_position(self) -> None:
        result = self.tool.execute(mode="parse", duration="PT1X")
        self.assertEqual(result["error"]["type"], "invalid_duration")
        self.assertIn("position 2", result["error"]["message"])

    def test_parse_shorthand_unknown_unit_position(self) -> None:
        result = self.tool.execute(mode="parse", duration="1x")
        self.assertEqual(result["error"]["type"], "invalid_duration")
        self.assertIn("unknown unit 'x' at position 1", result["error"]["message"])

    def test_parse_missing_unit_at_end(self) -> None:
        for text in ("PT1H30", "1h 30", "1h30"):
            with self.subTest(text=text):
                self.assert_error("invalid_duration", mode="parse", duration=text)

    def test_parse_malformed_number(self) -> None:
        for text in ("1.5.5h", "PT1.H", "1.h"):
            with self.subTest(text=text):
                self.assert_error("invalid_duration", mode="parse", duration=text)

    def test_parse_duplicate_units(self) -> None:
        cases = [
            ("P1D1D", "iso duplicate letter"),
            ("PT1H1H", "iso duplicate time letter"),
            ("1s 1s", "shorthand duplicate token"),
            ("1m 1min", "shorthand duplicate canonical"),
            ("1h 30m 15m", "shorthand duplicate later"),
        ]
        for text, why in cases:
            with self.subTest(why=why):
                self.assert_error("invalid_duration", mode="parse", duration=text)

    def test_parse_iso_out_of_order(self) -> None:
        result = self.tool.execute(mode="parse", duration="P2D1M")
        self.assertEqual(result["error"]["type"], "invalid_duration")
        self.assertIn("order", result["error"]["message"])

    def test_parse_iso_time_unit_in_date_section(self) -> None:
        self.assert_error("invalid_duration", mode="parse", duration="PT1H2D")

    def test_parse_iso_empty_sections(self) -> None:
        for text in ("P", "PT", "P1DT", "PTS", "P1DT2H3M4S5"):
            with self.subTest(text=text):
                self.assert_error("invalid_duration", mode="parse", duration=text)

    def test_parse_iso_trailing_garbage(self) -> None:
        self.assert_error("invalid_duration", mode="parse", duration="PT1HX")
        self.assert_error("invalid_duration", mode="parse", duration="PT1H30MX")

    def test_parse_sign_only(self) -> None:
        self.assert_error("invalid_duration", mode="parse", duration="-")

    def test_parse_shorthand_embedded_sign(self) -> None:
        self.assert_error("invalid_duration", mode="parse", duration="1h -30m")

    def test_parse_fullwidth_digits_rejected(self) -> None:
        # '１' (fullwidth one) is not an ASCII digit.
        self.assert_error("invalid_duration", mode="parse", duration="１h")

    def test_between_invalid_datetimes(self) -> None:
        self.assert_error(
            "invalid_datetime",
            mode="between",
            start="2026-01-01T10:00:00",
            end="tomorrow",
        )

    # -------------------------- ValueError --------------------------- #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="format")
        self.assert_invalid(mode=None)
        self.assert_invalid(mode=123)

    def test_invalid_duration_type(self) -> None:
        for bad in (None, 123, True, b"1h", ["1h"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", duration=bad)

    def test_invalid_duration_empty(self) -> None:
        self.assert_invalid(mode="parse", duration="")
        self.assert_invalid(mode="parse", duration="   ")

    def test_invalid_duration_length(self) -> None:
        self.assert_invalid(mode="parse", duration="a" * 1001)

    def test_invalid_seconds(self) -> None:
        for bad in (None, True, "abc", float("nan"), float("inf"), [5]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="humanize", seconds=bad)

    def test_invalid_datetime_parameters(self) -> None:
        self.assert_invalid(mode="between", start="2026-01-01")
        self.assert_invalid(mode="between", end="2026-01-01")
        self.assert_invalid(mode="between", start=1, end="2026-01-01")
        self.assert_invalid(mode="between", start="2026-01-01", end=2)

    def test_invalid_other(self) -> None:
        self.assert_invalid(mode="add", duration="1h")
        self.assert_invalid(mode="add", duration="1h", other=5)

    def test_invalid_operation(self) -> None:
        self.assert_invalid(
            mode="add", duration="1h", other="2h", operation="multiply"
        )
        self.assert_invalid(mode="add", duration="1h", other="2h", operation="")
        # None is allowed and defaults to 'add'.
        result = self.tool.execute(mode="add", duration="1h", other="2h")
        self.assertEqual(result["operation"], "add")

    def test_invalid_format(self) -> None:
        self.assert_invalid(mode="humanize", seconds=5, format="verbose")
        self.assert_invalid(mode="humanize", seconds=5, format="COMPACT")

    def test_invalid_allow_negative(self) -> None:
        self.assert_invalid(mode="parse", duration="1h", allow_negative="yes")
        self.assert_invalid(mode="parse", duration="1h", allow_negative=1)


class DurationToolPackagingTest(unittest.TestCase):
    """Class defaults, exports and the yaml sidecar."""

    def setUp(self) -> None:
        self.tool = DurationTool()

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectDurationTool, DurationTool)
        self.assertEqual(self.tool.name, "duration_tool")
        self.assertIn("parse", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("DurationTool", __all__)

    def test_mode_and_format_constants(self) -> None:
        self.assertEqual(
            DurationTool.MODES, ("parse", "humanize", "between", "add")
        )
        self.assertEqual(
            DurationTool.FORMATS, ("compact", "long", "clock")
        )
        self.assertEqual(DurationTool.OPERATIONS, ("add", "subtract"))

    def test_yaml_sidecar_matches_class(self) -> None:
        import os
        import sys

        module_file = sys.modules[DirectDurationTool.__module__].__file__
        module_path = os.path.abspath(module_file)
        self.assertTrue(module_path.endswith("duration_tool.py"))
        self.assertTrue(
            os.path.isfile(
                os.path.join(os.path.dirname(module_path), "duration_tool.yaml")
            )
        )


if __name__ == "__main__":
    unittest.main()
