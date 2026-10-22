#!/usr/bin/env python3

# @Time    : 2026/10/19
# @FileName: test_datetime_tool.py

"""Tests for DateTimeTool.

All results are deterministic: the `now` mode and `diff` without an
explicit `end_datetime` read the tool's injectable clock (`frozen_now`)
instead of the wall clock, and every other assertion uses fixed dates
with fixed IANA timezones.
"""

import os
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, available_timezones

from agentuniverse.agent.action.tool.common_tool import datetime_tool as module
from agentuniverse.agent.action.tool.common_tool.datetime_tool import DateTimeTool

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "datetime_tool.yaml")

# Frozen instant used across tests: 2026-10-19 04:30:00 UTC (a Monday).
FROZEN_NOW = datetime(2026, 10, 19, 4, 30, 0, tzinfo=timezone.utc)


def make_tool(**overrides) -> DateTimeTool:
    return DateTimeTool(frozen_now=FROZEN_NOW, **overrides)


class DateTimeToolNowTest(unittest.TestCase):
    """mode=now: current datetime in a timezone, read from frozen_now."""

    def setUp(self):
        self.tool = make_tool()

    def test_now_utc(self):
        result = self.tool.execute(mode="now", timezone_str="UTC")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["datetime"], "2026-10-19 04:30:00")
        self.assertEqual(result["iso"], "2026-10-19T04:30:00+00:00")
        self.assertEqual(result["date"], "2026-10-19")
        self.assertEqual(result["time"], "04:30:00")
        self.assertEqual(result["weekday"], "Monday")
        self.assertEqual(result["utc_offset"], "+00:00")
        self.assertEqual(
            result["timestamp"],
            datetime(2026, 10, 19, 4, 30, tzinfo=timezone.utc).timestamp())

    def test_now_shanghai(self):
        result = self.tool.execute(mode="now", timezone_str="Asia/Shanghai")
        self.assertEqual(result["datetime"], "2026-10-19 12:30:00")
        self.assertEqual(result["utc_offset"], "+08:00")
        self.assertEqual(result["timezone"], "Asia/Shanghai")

    def test_now_half_hour_offset(self):
        result = self.tool.execute(mode="now", timezone_str="Asia/Kolkata")
        self.assertEqual(result["datetime"], "2026-10-19 10:00:00")
        self.assertEqual(result["utc_offset"], "+05:30")

    def test_now_uses_default_timezone(self):
        result = self.tool.execute(mode="now")
        self.assertEqual(result["datetime"], "2026-10-19 04:30:00")
        tool = make_tool(default_timezone="Asia/Shanghai")
        self.assertEqual(
            tool.execute(mode="now")["datetime"], "2026-10-19 12:30:00")

    def test_now_local(self):
        result = self.tool.execute(mode="now", timezone_str="local")
        self.assertEqual(result["status"], "success")
        self.assertIsNotNone(result["utc_offset"])

    def test_now_fixed_offsets(self):
        result = self.tool.execute(mode="now", timezone_str="+08:00")
        self.assertEqual(result["datetime"], "2026-10-19 12:30:00")
        result = self.tool.execute(mode="now", timezone_str="-0530")
        self.assertEqual(result["datetime"], "2026-10-18 23:00:00")

    def test_utc_aliases(self):
        for alias in ("utc", "Z", "Zulu"):
            result = self.tool.execute(mode="now", timezone_str=alias)
            self.assertEqual(result["utc_offset"], "+00:00")

    def test_now_custom_format(self):
        tool = make_tool(default_format="%Y/%m/%d %H:%M")
        result = tool.execute(mode="now", timezone_str="UTC")
        self.assertEqual(result["datetime"], "2026/10/19 04:30")

    def test_unknown_timezone_error_with_examples(self):
        result = self.tool.execute(mode="now", timezone_str="Mars/Olympus")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unknown timezone", result["error"])
        self.assertIn("Asia/Shanghai", result["error"])  # examples listed

    def test_unknown_timezone_suggests_close_matches(self):
        if not available_timezones():
            self.skipTest("no tzdata available on this platform")
        result = self.tool.execute(mode="now", timezone_str="Asia/Shangha")
        self.assertEqual(result["status"], "error")
        self.assertIn("Asia/Shanghai", result["error"])

    def test_invalid_fixed_offset(self):
        result = self.tool.execute(mode="now", timezone_str="+25:00")
        self.assertEqual(result["status"], "error")
        self.assertIn("offset", result["error"])


class DateTimeToolFormatTest(unittest.TestCase):
    """mode=format: parse (auto or explicit) and reformat."""

    def setUp(self):
        self.tool = make_tool()

    def test_auto_detected_space_form(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15 10:30:00",
            fmt="%d/%m/%Y %H:%M")
        self.assertEqual(result["formatted"], "15/01/2026 10:30")
        self.assertEqual(
            result["matched_input_format"], "%Y-%m-%d %H:%M:%S")

    def test_auto_detected_iso_t_form(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15T10:30:00")
        self.assertEqual(result["iso"], "2026-01-15T10:30:00+00:00")
        self.assertEqual(result["matched_input_format"], "%Y-%m-%dT%H:%M:%S")

    def test_iso8601_with_z_suffix(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15T10:30:00Z")
        self.assertEqual(result["iso"], "2026-01-15T10:30:00+00:00")
        self.assertEqual(result["matched_input_format"], "ISO 8601")

    def test_iso8601_with_explicit_offset_kept(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15T10:30:00+05:00",
            timezone_str="UTC")
        self.assertEqual(result["iso"], "2026-01-15T10:30:00+05:00")

    def test_explicit_input_fmt_day_first(self):
        result = self.tool.execute(
            mode="format", datetime_str="31/12/2026", input_fmt="%d/%m/%Y")
        self.assertEqual(result["iso"], "2026-12-31T00:00:00+00:00")

    def test_textual_dates_auto_detected(self):
        for text, expected in (
            ("January 15, 2026", "2026-01-15T00:00:00+00:00"),
            ("15 Jan 2026", "2026-01-15T00:00:00+00:00"),
        ):
            result = self.tool.execute(mode="format", datetime_str=text)
            self.assertEqual(result["iso"], expected)

    def test_naive_input_localised_to_timezone(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15 10:00:00",
            timezone_str="Asia/Shanghai")
        self.assertEqual(result["iso"], "2026-01-15T10:00:00+08:00")
        self.assertEqual(result["timezone"], "Asia/Shanghai")

    def test_default_output_format(self):
        result = self.tool.execute(mode="format", datetime_str="2026-01-15")
        self.assertEqual(result["formatted"], "2026-01-15 00:00:00")

    def test_unparseable_reports_formats_tried(self):
        result = self.tool.execute(mode="format", datetime_str="not-a-date")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Formats tried", result["error"])
        self.assertIn("%Y-%m-%d %H:%M:%S", result["error"])
        self.assertIn("ISO 8601", result["error"])

    def test_ambiguous_day_first_requires_input_fmt(self):
        result = self.tool.execute(mode="format", datetime_str="31/12/2026")
        self.assertEqual(result["status"], "error")

    def test_empty_and_non_string_inputs(self):
        for bad in ("", "   ", None, 20260115):
            result = self.tool.execute(mode="format", datetime_str=bad)
            self.assertEqual(result["status"], "error", msg=repr(bad))
            self.assertEqual(result["error_type"], "validation_error")

    def test_input_fmt_mismatch(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15", input_fmt="%d/%m/%Y")
        self.assertEqual(result["status"], "error")
        self.assertIn("input_fmt", result["error"])

    def test_output_fmt_too_long_rejected(self):
        result = self.tool.execute(
            mode="format", datetime_str="2026-01-15", fmt="%Y" * 201)
        self.assertEqual(result["status"], "error")
        self.assertIn("fmt", result["error"])


class DateTimeToolConvertTest(unittest.TestCase):
    """mode=convert: timezone conversion, DST-aware via zoneinfo."""

    def setUp(self):
        self.tool = make_tool()

    def test_utc_to_shanghai(self):
        result = self.tool.execute(
            mode="convert", datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC", target_timezone="Asia/Shanghai")
        self.assertEqual(result["converted"], "2026-01-15 18:00:00")
        self.assertEqual(result["original"], "2026-01-15 10:00:00")
        self.assertEqual(result["to_timezone"], "Asia/Shanghai")

    def test_new_york_dst_aware(self):
        # January: EST (UTC-5); July: EDT (UTC-4).
        winter = self.tool.execute(
            mode="convert", datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC", target_timezone="America/New_York")
        self.assertEqual(winter["converted"], "2026-01-15 05:00:00")
        summer = self.tool.execute(
            mode="convert", datetime_str="2026-07-15 10:00:00",
            timezone_str="UTC", target_timezone="America/New_York")
        self.assertEqual(summer["converted"], "2026-07-15 06:00:00")

    def test_naive_source_with_timezone_str(self):
        result = self.tool.execute(
            mode="convert", datetime_str="2026-01-15 10:00:00",
            timezone_str="Asia/Shanghai", target_timezone="Europe/London")
        self.assertEqual(result["converted"], "2026-01-15 02:00:00")

    def test_default_target_is_utc(self):
        result = self.tool.execute(
            mode="convert", datetime_str="2026-01-15T10:00:00+08:00")
        self.assertEqual(result["converted"], "2026-01-15 02:00:00")
        self.assertEqual(result["to_timezone"], "UTC")

    def test_custom_output_format(self):
        result = self.tool.execute(
            mode="convert", datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC", target_timezone="Asia/Shanghai",
            fmt="%H:%M on %d %b %Y")
        self.assertEqual(result["converted"], "18:00 on 15 Jan 2026")

    def test_invalid_target_timezone(self):
        result = self.tool.execute(
            mode="convert", datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC", target_timezone="Europe/Nowhere")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")


class DateTimeToolDiffTest(unittest.TestCase):
    """mode=diff: exact durations and relativedelta-style months/years."""

    def setUp(self):
        self.tool = make_tool()

    def test_exact_time_units(self):
        cases = [
            ("2026-01-01 00:00:00", "2026-01-11 00:00:00", "days", 10.0),
            ("2026-06-01", "2026-06-02", "hours", 24.0),
            ("2026-06-01 00:00:00", "2026-06-01 01:30:00", "minutes", 90.0),
            ("2026-06-01 00:00:00", "2026-06-01 00:01:30", "seconds", 90.0),
            ("2026-01-01", "2026-01-29", "weeks", 4.0),
        ]
        for start, end, unit, expected in cases:
            result = self.tool.execute(
                mode="diff", datetime_str=start, end_datetime=end, unit=unit)
            self.assertEqual(result["status"], "success", msg=unit)
            self.assertEqual(result["value"], expected, msg=unit)
            self.assertEqual(result["unit"], unit)

    def test_unit_aliases_normalised(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-01", end_datetime="2026-01-11",
            unit="d")
        self.assertEqual(result["unit"], "days")
        self.assertEqual(result["value"], 10.0)

    def test_month_end_clamping_counts_full_month(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-31",
            end_datetime="2026-02-28", unit="months")
        self.assertEqual(result["value"], 1)

    def test_partial_month_borrows(self):
        # 2025-02-28 + 1 month = 2025-03-28; three more days remain.
        result = self.tool.execute(
            mode="diff", datetime_str="2025-02-28",
            end_datetime="2025-03-31", unit="months")
        self.assertEqual(result["value"], 1)
        self.assertEqual(result["breakdown"]["months"], 1)
        self.assertEqual(result["breakdown"]["days"], 3)

    def test_leap_day_to_anniversary_is_one_year(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2024-02-29",
            end_datetime="2025-02-28", unit="years")
        self.assertEqual(result["value"], 1)
        self.assertEqual(result["breakdown"]["years"], 1)
        self.assertEqual(result["breakdown"]["months"], 0)

    def test_years_value_excludes_partial_year(self):
        # 22 months elapsed = 1 full year, 10 months remainder.
        result = self.tool.execute(
            mode="diff", datetime_str="2025-01-15",
            end_datetime="2026-11-15", unit="years")
        self.assertEqual(result["value"], 1)
        self.assertEqual(result["breakdown"]["years"], 1)
        self.assertEqual(result["breakdown"]["months"], 10)

    def test_breakdown_composition(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-15 10:00:00",
            end_datetime="2026-03-20 11:30:00", unit="days")
        self.assertEqual(result["breakdown"]["months"], 2)
        self.assertEqual(result["breakdown"]["days"], 5)
        self.assertEqual(result["breakdown"]["hours"], 1)
        self.assertEqual(result["breakdown"]["minutes"], 30)

    def test_negative_diff(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-06-15",
            end_datetime="2026-01-15", unit="days")
        self.assertEqual(result["value"], -151.0)
        months = self.tool.execute(
            mode="diff", datetime_str="2026-06-15",
            end_datetime="2026-01-15", unit="months")
        self.assertEqual(months["value"], -5)
        self.assertEqual(months["breakdown"]["years"], 0)
        self.assertEqual(months["breakdown"]["months"], -5)

    def test_diff_against_frozen_now(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-10-19 02:30:00",
            timezone_str="UTC", unit="hours")
        self.assertEqual(result["value"], 2.0)
        self.assertEqual(result["end"], "2026-10-19T04:30:00+00:00")

    def test_same_moments_are_zero(self):
        for unit in ("seconds", "days", "months", "years"):
            result = self.tool.execute(
                mode="diff", datetime_str="2026-01-15 10:00:00",
                end_datetime="2026-01-15 10:00:00", unit=unit)
            self.assertEqual(result["value"], 0, msg=unit)

    def test_cross_timezone_absolute_math(self):
        # 10:00 +08:00 is 02:00 UTC, i.e. 8 hours before 10:00 UTC.
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-15T10:00:00+08:00",
            end_datetime="2026-01-15 10:00:00", timezone_str="UTC",
            unit="hours")
        self.assertEqual(result["value"], 8.0)

    def test_add_then_diff_roundtrip(self):
        later = self.tool.execute(
            mode="add", datetime_str="2026-01-31", months=1)
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-31",
            end_datetime=later["datetime"], unit="months")
        self.assertEqual(result["value"], 1)

    def test_unsupported_unit(self):
        result = self.tool.execute(
            mode="diff", datetime_str="2026-01-01",
            end_datetime="2026-01-02", unit="fortnights")
        self.assertEqual(result["status"], "error")
        self.assertIn("months", result["error"])

    def test_missing_start_rejected(self):
        result = self.tool.execute(mode="diff", unit="days")
        self.assertEqual(result["status"], "error")


class DateTimeToolAddTest(unittest.TestCase):
    """mode=add: calendar-aware arithmetic with month-end clamping."""

    def setUp(self):
        self.tool = make_tool()

    def test_add_days(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-10-19 12:00:00", days=7)
        self.assertEqual(result["datetime"], "2026-10-26 12:00:00")
        self.assertEqual(result["iso"], "2026-10-26T12:00:00+00:00")

    def test_subtract_days_add_hours(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-10-19 12:00:00", days=-7, hours=3)
        self.assertEqual(result["datetime"], "2026-10-12 15:00:00")

    def test_month_end_clamping(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-01-31", months=1)
        self.assertEqual(result["datetime"], "2026-02-28 00:00:00")

    def test_month_end_clamping_leap_year(self):
        result = self.tool.execute(
            mode="add", datetime_str="2024-01-31", months=1)
        self.assertEqual(result["datetime"], "2024-02-29 00:00:00")

    def test_leap_day_plus_one_year(self):
        result = self.tool.execute(
            mode="add", datetime_str="2024-02-29 10:00:00", years=1)
        self.assertEqual(result["datetime"], "2025-02-28 10:00:00")

    def test_negative_months(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-03-31", months=-1)
        self.assertEqual(result["datetime"], "2026-02-28 00:00:00")

    def test_years_and_months_combined(self):
        result = self.tool.execute(
            mode="add", datetime_str="2025-06-15", years=1, months=2)
        self.assertEqual(result["datetime"], "2026-08-15 00:00:00")

    def test_days_cross_month_boundary(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-01-31", days=1)
        self.assertEqual(result["datetime"], "2026-02-01 00:00:00")

    def test_time_units_carry(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-01-01 00:00:00",
            hours=25, minutes=61)
        self.assertEqual(result["datetime"], "2026-01-02 02:01:00")

    def test_offsets_echoed_and_timezone_kept(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-01-15 10:00:00",
            timezone_str="Asia/Shanghai", days=1)
        self.assertEqual(result["iso"], "2026-01-16T10:00:00+08:00")
        self.assertEqual(result["timezone"], "Asia/Shanghai")
        self.assertEqual(result["offsets"]["days"], 1)

    def test_all_zero_offsets_rejected(self):
        result = self.tool.execute(mode="add", datetime_str="2026-01-15")
        self.assertEqual(result["status"], "error")
        self.assertIn("non-zero", result["error"])

    def test_boolean_and_float_offsets_rejected(self):
        for kwargs in ({"days": True}, {"days": 1.5}, {"months": "1"}):
            result = self.tool.execute(
                mode="add", datetime_str="2026-01-15", **kwargs)
            self.assertEqual(result["status"], "error", msg=kwargs)

    def test_offset_ceiling_enforced(self):
        result = self.tool.execute(
            mode="add", datetime_str="2026-01-15", days=200_000)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_unit_value", result["error"])

    def test_datetime_overflow_reported(self):
        result = self.tool.execute(mode="add", datetime_str="9999-12-31", days=1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")


class DateTimeToolValidationTest(unittest.TestCase):
    """Shared argument validation, error envelope and packaging."""

    def setUp(self):
        self.tool = DateTimeTool()

    def test_unknown_mode(self):
        result = self.tool.execute(mode="nope", datetime_str="2026-01-15")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unsupported mode", result["error"])
        self.assertEqual(result["mode"], "nope")

    def test_non_string_mode(self):
        result = self.tool.execute(mode=42)
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be a string", result["error"])

    def test_mode_case_and_whitespace_normalised(self):
        tool = make_tool()
        result = tool.execute(mode=" NOW ", timezone_str="UTC")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "now")

    def test_frozen_naive_datetime_treated_as_utc(self):
        tool = DateTimeTool(frozen_now=datetime(2026, 10, 19, 4, 30, 0))
        result = tool.execute(mode="now", timezone_str="Asia/Shanghai")
        self.assertEqual(result["datetime"], "2026-10-19 12:30:00")

    def test_real_clock_used_when_unfrozen(self):
        result = self.tool.execute(mode="now", timezone_str="UTC")
        self.assertEqual(result["status"], "success")
        self.assertLess(
            abs(result["timestamp"] - datetime.now(timezone.utc).timestamp()),
            300)

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import DateTimeTool as exported
        self.assertIs(exported, DateTimeTool)

    def test_yaml_exists_and_declares_component(self):
        self.assertTrue(os.path.isfile(YAML_PATH))
        with open(YAML_PATH, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("class: DateTimeTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool."
            "datetime_tool", content)

    def test_zoneinfo_shapes_are_used_directly(self):
        # Sanity: the tool rides on stdlib zoneinfo, no shim types.
        tool = make_tool()
        tz = tool._get_tz("Asia/Shanghai")
        self.assertIsInstance(tz, ZoneInfo)
        self.assertIs(tool._get_tz("UTC"), timezone.utc)


if __name__ == "__main__":
    unittest.main()
