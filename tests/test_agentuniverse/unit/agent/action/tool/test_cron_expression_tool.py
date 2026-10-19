#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_cron_expression_tool.py

"""Offline unit tests for CronExpressionTool.

The tool is built purely on the standard library (datetime, typing)
and never touches the network, so this suite runs fully offline.
Every assertion is deterministic: field expansions are checked against
literal expected sets, describe output against fixed English ground
truths, and next-run sequences against hand-verified calendar facts
(for example: 2026-01-01 is a Thursday, February 2026 has 28 days,
2028 is a leap year, and 2028-02-29 is a Tuesday).  The only
clock-dependent path — omitting ``now`` — is asserted by shape, never
by value.
"""

import unittest
from datetime import datetime

from agentuniverse.agent.action.tool.common_tool import CronExpressionTool
from agentuniverse.agent.action.tool.common_tool.cron_expression_tool import (
    CronExpressionTool as DirectCronExpressionTool,
)

# Fixed reference times used across the next-mode tests.
NOW_2026_01_15_10_20 = "2026-01-15T10:20:00"
NOW_2026_01_01 = "2026-01-01T00:00:00"


class CronExpressionToolValidateTest(unittest.TestCase):
    """Validation and field-expansion test cases."""

    def setUp(self) -> None:
        self.tool = CronExpressionTool()

    # ------------------------------------------------------------------ #
    # Valid expressions covering every field atom type
    # ------------------------------------------------------------------ #

    def test_validate_star_and_step_fields(self) -> None:
        result = self.tool.execute(mode="validate", expression="*/15 0-5 * * *")
        self.assertEqual(
            result["fields"],
            {
                "minute": [0, 15, 30, 45],
                "hour": [0, 1, 2, 3, 4, 5],
                "day-of-month": list(range(1, 32)),
                "month": list(range(1, 13)),
                "day-of-week": list(range(7)),
            },
        )
        self.assertEqual(result["normalized"], "0,15,30,45 0-5 * * *")
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_validate_lists_ranges_names_and_steps(self) -> None:
        result = self.tool.execute(
            mode="validate", expression="*/15 1-5 10,20,31 jan-mar mon-fri"
        )
        self.assertEqual(
            result["fields"],
            {
                "minute": [0, 15, 30, 45],
                "hour": [1, 2, 3, 4, 5],
                "day-of-month": [10, 20, 31],
                "month": [1, 2, 3],
                "day-of-week": [1, 2, 3, 4, 5],
            },
        )
        # The stepped minute set is not consecutive, so the normalized
        # form lists the values; the day-of-week range stays a range.
        self.assertEqual(result["normalized"], "0,15,30,45 1-5 10,20,31 1-3 1-5")

    def test_validate_stepped_range(self) -> None:
        result = self.tool.execute(mode="validate", expression="0 9-17/2 * * *")
        self.assertEqual(result["fields"]["hour"], [9, 11, 13, 15, 17])
        self.assertEqual(result["normalized"], "0 9,11,13,15,17 * * *")

    def test_validate_step_from_single_value(self) -> None:
        # 'a/n' means "from a to the end of the field, stepped".
        result = self.tool.execute(mode="validate", expression="5/15 * * * *")
        self.assertEqual(result["fields"]["minute"], [5, 20, 35, 50])
        result = self.tool.execute(mode="validate", expression="10/20 * * * *")
        self.assertEqual(result["fields"]["minute"], [10, 30, 50])

    def test_validate_names_are_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="validate", expression="0 0 1 JAN-MAR Sun,SAT"
        )
        self.assertEqual(result["fields"]["month"], [1, 2, 3])
        self.assertEqual(result["fields"]["day-of-week"], [0, 6])

    def test_validate_dow_seven_means_sunday(self) -> None:
        result = self.tool.execute(mode="validate", expression="0 0 * * 7")
        self.assertEqual(result["fields"]["day-of-week"], [0])
        result = self.tool.execute(mode="validate", expression="0 0 * * 0,7")
        self.assertEqual(result["fields"]["day-of-week"], [0])
        # 5-7 is Friday, Saturday, Sunday — normalized to 0,5,6.
        result = self.tool.execute(mode="validate", expression="0 0 * * 5-7")
        self.assertEqual(result["fields"]["day-of-week"], [0, 5, 6])

    def test_validate_dow_step_from_value_wraps_to_sunday(self) -> None:
        # '5/2' steps from Friday through the field end (7 = Sunday),
        # so the expanded set is Friday and Sunday.
        result = self.tool.execute(mode="validate", expression="0 0 * * 5/2")
        self.assertEqual(result["fields"]["day-of-week"], [0, 5])
        result = self.tool.execute(mode="validate", expression="0 0 * * 1/2")
        self.assertEqual(result["fields"]["day-of-week"], [0, 1, 3, 5])

    def test_validate_quartz_extensions_rejected_honestly(self) -> None:
        # L / W / # / ? and six-field seconds syntax are not supported;
        # they must fail validation with a field error, not misparse.
        for expression, field in (
            ("0 0 L * *", "day-of-month"),
            ("0 0 15W * *", "day-of-month"),
            ("0 0 * * 1#2", "day-of-week"),
            ("0 0 ? * 1", "day-of-month"),
            ("0 */5 * * * *", "expression"),
            ("@reboot", "macro"),
        ):
            result = self.tool.execute(mode="validate", expression=expression)
            self.assertFalse(result["valid"], expression)
            self.assertEqual(
                result["errors"][0]["field"], field, expression
            )

    def test_validate_macros(self) -> None:
        expected = {
            "@daily": ("0 0 * * *", None, None),
            "@midnight": ("0 0 * * *", None, None),
            "@hourly": ("0 * * * *", None, None),
            "@weekly": ("0 0 * * 0", None, None),
            "@monthly": ("0 0 1 * *", [1], None),
            "@yearly": ("0 0 1 1 *", [1], [1]),
            "@annually": ("0 0 1 1 *", [1], [1]),
        }
        for macro, (expanded, dom, month) in expected.items():
            result = self.tool.execute(mode="validate", expression=macro)
            self.assertTrue(result["valid"], macro)
            self.assertEqual(result["macro"], macro)
            self.assertEqual(result["expanded"], expanded)
            self.assertEqual(result["normalized"], expanded)
            if dom is not None:
                self.assertEqual(result["fields"]["day-of-month"], dom, macro)
            if month is not None:
                self.assertEqual(result["fields"]["month"], month, macro)

    def test_validate_macro_uppercase(self) -> None:
        result = self.tool.execute(mode="validate", expression="@DAILY")
        self.assertTrue(result["valid"])
        self.assertEqual(result["expanded"], "0 0 * * *")

    # ------------------------------------------------------------------ #
    # Invalid expressions — precise per-field errors
    # ------------------------------------------------------------------ #

    def assert_field_error(self, expression: str, field: str, *fragments: str):
        result = self.tool.execute(mode="validate", expression=expression)
        self.assertFalse(result["valid"], expression)
        self.assertEqual(len(result["errors"]), 1, expression)
        error = result["errors"][0]
        self.assertEqual(error["field"], field, expression)
        for fragment in fragments:
            self.assertIn(fragment, error["message"], expression)
        self.assertNotIn("fields", result)
        self.assertNotIn("normalized", result)

    def test_validate_wrong_field_count(self) -> None:
        self.assert_field_error("* * *", "expression", "exactly 5", "got 3")
        self.assert_field_error("* * * * * *", "expression", "exactly 5", "got 6")

    def test_validate_out_of_range_values(self) -> None:
        self.assert_field_error("60 * * * *", "minute", "out of range 0-59")
        self.assert_field_error("* 24 * * *", "hour", "out of range 0-23")
        self.assert_field_error("* * 0 * *", "day-of-month", "out of range 1-31")
        self.assert_field_error("* * 32 * *", "day-of-month", "out of range 1-31")
        self.assert_field_error("* * * 13 *", "month", "out of range 1-12")
        self.assert_field_error("* * * * 8", "day-of-week", "out of range 0-7")

    def test_validate_unrecognized_tokens(self) -> None:
        self.assert_field_error("abc * * * *", "minute", "not a valid integer")
        self.assert_field_error(
            "* * * foo *", "month", "not a valid integer", "jan-dec"
        )
        self.assert_field_error(
            "* * * * sunn", "day-of-week", "not a valid integer", "sun-sat"
        )
        # A step with trailing garbage fails as a step error.
        self.assert_field_error("*/15a * * * *", "minute", "step must be a positive integer")

    def test_validate_reversed_range(self) -> None:
        self.assert_field_error(
            "0 5-2 * * *", "hour", "range start 5", "greater than", "end 2"
        )
        self.assert_field_error(
            "0 0 * * fri-mon", "day-of-week", "greater than the range end"
        )

    def test_validate_bad_steps(self) -> None:
        self.assert_field_error("*/0 * * * *", "minute", "positive integer")
        self.assert_field_error("*/-2 * * * *", "minute", "positive integer")
        self.assert_field_error("*/a * * * *", "minute", "step must be a positive integer")

    def test_validate_rejects_non_plain_digit_tokens(self) -> None:
        # int() alone would accept underscore separators, signs and
        # non-ASCII digit characters; none of them are cron syntax.
        self.assert_field_error("1_0 * * * *", "minute", "not a valid integer")
        self.assert_field_error("*/1_5 * * * *", "minute", "positive integer")
        self.assert_field_error("+5 * * * *", "minute", "not a valid integer")
        self.assert_field_error("*/+15 * * * *", "minute", "positive integer")
        self.assert_field_error("٥ * * * *", "minute", "not a valid integer")
        self.assert_field_error("*/٥ * * * *", "minute", "positive integer")

    def test_validate_stray_commas_and_slashes(self) -> None:
        self.assert_field_error("1,,2 * * * *", "minute", "empty list element")
        self.assert_field_error("*/ * * * *", "minute", "'/' with no step value")
        self.assert_field_error("/15 * * * *", "minute", "empty value")

    def test_validate_unknown_macro(self) -> None:
        self.assert_field_error("@secondly", "macro", "unknown macro", "@daily")
        self.assert_field_error("@daily extra", "macro", "single token")

    def test_validate_collects_multiple_field_errors(self) -> None:
        result = self.tool.execute(mode="validate", expression="60 24 * 13 8")
        self.assertFalse(result["valid"])
        self.assertEqual(
            [error["field"] for error in result["errors"]],
            ["minute", "hour", "month", "day-of-week"],
        )

    def test_validate_bad_field_after_valid_fields_keeps_going(self) -> None:
        result = self.tool.execute(mode="validate", expression="*/5 9 32 * *")
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["field"], "day-of-month")


class CronExpressionToolDescribeTest(unittest.TestCase):
    """Human-readable description ground truths."""

    def setUp(self) -> None:
        self.tool = CronExpressionTool()

    def assert_description(self, expression: str, description: str):
        result = self.tool.execute(mode="describe", expression=expression)
        self.assertEqual(
            result, {"mode": "describe", "expression": expression,
                     "description": description},
        )

    def test_describe_time_shapes(self) -> None:
        self.assert_description("* * * * *", "Every minute")
        self.assert_description("30 * * * *", "At 30 minutes past every hour")
        self.assert_description("1 * * * *", "At 1 minute past every hour")
        self.assert_description("0 * * * *", "At 0 minutes past every hour")
        self.assert_description("*/15 * * * *", "Every 15 minutes")
        self.assert_description("*/30 * * * *", "Every 30 minutes")
        self.assert_description(
            "5,20,35,50 * * * *", "At minutes 5, 20, 35 and 50 past every hour"
        )
        self.assert_description("* 8 * * *", "Every minute during hour 08")
        self.assert_description(
            "* 8,20 * * *", "Every minute during hour 08 and hour 20"
        )

    def test_describe_clock_times(self) -> None:
        self.assert_description("0 0 * * *", "At 00:00")
        self.assert_description("15,45 8 * * *", "At 08:15 and 08:45")
        self.assert_description("30 8,20 * * *", "At 08:30 and 20:30")
        self.assert_description(
            "0 9-17/2 * * *", "At 09:00, 11:00, 13:00, 15:00 and 17:00"
        )

    def test_describe_long_time_enumeration_is_bounded(self) -> None:
        self.assert_description(
            "0 0-7 * * *",
            "At 00:00, 01:00, 02:00, 03:00, 04:00, 05:00, … and 2 more",
        )

    def test_describe_days_and_months(self) -> None:
        self.assert_description("0 12 * * 1-5", "At 12:00, on Monday through Friday")
        self.assert_description(
            "0 12 * * 0,6", "At 12:00, on Sunday and Saturday"
        )
        self.assert_description(
            "0 12 * * mon,wed,fri", "At 12:00, on Monday, Wednesday and Friday"
        )
        self.assert_description("0 0 1 * *", "At 00:00, on day 1 of the month")
        self.assert_description(
            "0 0 1,15 * *",
            "At 00:00, on day 1 of the month and day 15 of the month",
        )
        # A consecutive day pair reads as "day X and day Y of the month".
        self.assert_description(
            "0 0 1,2 * *", "At 00:00, on day 1 and day 2 of the month"
        )
        self.assert_description(
            "0 0 1-5 * *", "At 00:00, on day 1 through day 5 of the month"
        )
        self.assert_description(
            "0 0 29 2 *", "At 00:00, on day 29 of the month, in February"
        )
        self.assert_description(
            "0 0 1 jan-mar *", "At 00:00, on day 1 of the month, in January through March"
        )
        self.assert_description(
            "0 0 1 1,6 *",
            "At 00:00, on day 1 of the month, in January and June",
        )

    def test_describe_dom_dow_or_semantics(self) -> None:
        self.assert_description(
            "0 12 1 * 1",
            "At 12:00, on day 1 of the month or on Monday (whichever matches)",
        )

    def test_describe_macros(self) -> None:
        self.assert_description("@daily", "At 00:00")
        self.assert_description("@midnight", "At 00:00")
        self.assert_description("@hourly", "At 0 minutes past every hour")
        self.assert_description("@weekly", "At 00:00, on Sunday")
        self.assert_description("@monthly", "At 00:00, on day 1 of the month")
        self.assert_description(
            "@yearly", "At 00:00, on day 1 of the month, in January"
        )

    def test_describe_invalid_expression_returns_error_payload(self) -> None:
        result = self.tool.execute(mode="describe", expression="60 24 * * *")
        self.assertEqual(result["mode"], "describe")
        error = result["error"]
        self.assertEqual(error["type"], "invalid_expression")
        self.assertIn("minute", error["message"])
        self.assertIn("hour", error["message"])
        self.assertEqual(
            [e["field"] for e in error["field_errors"]], ["minute", "hour"]
        )
        self.assertNotIn("description", result)


class CronExpressionToolNextTest(unittest.TestCase):
    """Next-run projection tests from fixed, injected reference times."""

    def setUp(self) -> None:
        self.tool = CronExpressionTool()

    def assert_matches(self, expression, now, expected, count=None, **kwargs):
        params = {"mode": "next", "expression": expression, "now": now}
        if count is not None:
            params["count"] = count
        else:
            count = len(expected)
        params.update(kwargs)
        result = self.tool.execute(**params)
        self.assertEqual(result["matches"], expected, expression)
        self.assertEqual(result["count"], count)
        self.assertEqual(result["expression"], expression)
        return result

    def test_next_hourly_scope(self) -> None:
        self.assert_matches(
            "30 * * * *",
            NOW_2026_01_15_10_20,
            [
                "2026-01-15T10:30:00",
                "2026-01-15T11:30:00",
                "2026-01-15T12:30:00",
            ],
            count=3,
        )

    def test_next_is_strictly_after_now(self) -> None:
        # A run exactly at `now` is not "after" it.
        self.assert_matches(
            "30 * * * *",
            "2026-01-15T10:30:00",
            ["2026-01-15T11:30:00"],
        )
        # Now is floored to the minute before advancing.
        self.assert_matches(
            "30 * * * *",
            "2026-01-15T10:29:59",
            ["2026-01-15T10:30:00"],
        )

    def test_next_minute_step(self) -> None:
        self.assert_matches(
            "*/15 * * * *",
            "2026-01-15T10:07:00",
            [
                "2026-01-15T10:15:00",
                "2026-01-15T10:30:00",
                "2026-01-15T10:45:00",
                "2026-01-15T11:00:00",
            ],
            count=4,
        )

    def test_next_step_from_single_value(self) -> None:
        self.assert_matches(
            "5/15 * * * *",
            "2026-01-15T10:00:00",
            [
                "2026-01-15T10:05:00",
                "2026-01-15T10:20:00",
                "2026-01-15T10:35:00",
                "2026-01-15T10:50:00",
                "2026-01-15T11:05:00",
            ],
            count=5,
        )

    def test_next_stepped_hour_range_crosses_days(self) -> None:
        self.assert_matches(
            "0 9-17/2 * * *",
            "2026-01-15T10:30:00",
            [
                "2026-01-15T11:00:00",
                "2026-01-15T13:00:00",
                "2026-01-15T15:00:00",
                "2026-01-15T17:00:00",
                "2026-01-16T09:00:00",
            ],
            count=5,
        )

    def test_next_respects_month_lengths(self) -> None:
        # 2026: February has 28 days, April/June 30 — the 31st only
        # fires on months long enough (January, March, May, July,
        # August, ...).
        self.assert_matches(
            "0 0 31 * *",
            NOW_2026_01_01,
            [
                "2026-01-31T00:00:00",
                "2026-03-31T00:00:00",
                "2026-05-31T00:00:00",
                "2026-07-31T00:00:00",
                "2026-08-31T00:00:00",
            ],
            count=5,
        )

    def test_next_leap_day(self) -> None:
        # From 2026 the next February 29ths are 2028 and 2032.
        self.assert_matches(
            "0 0 29 2 *",
            NOW_2026_01_01,
            ["2028-02-29T00:00:00", "2032-02-29T00:00:00"],
            count=2,
        )
        self.assert_matches(
            "0 0 29 2 *",
            "2027-03-01T00:00:00",
            ["2028-02-29T00:00:00"],
        )

    def test_next_dom_dow_or_semantics(self) -> None:
        # '0 12 1 * 1' — noon on the 1st of the month OR on Mondays.
        # 2026-01-01 is a Thursday; the first Monday is January 5;
        # February 1 is a Sunday (day-of-month match) and February 2
        # is a Monday.
        self.assert_matches(
            "0 12 1 * 1",
            NOW_2026_01_01,
            [
                "2026-01-01T12:00:00",  # day-of-month 1
                "2026-01-05T12:00:00",  # Monday
                "2026-01-12T12:00:00",
                "2026-01-19T12:00:00",
                "2026-01-26T12:00:00",
                "2026-02-01T12:00:00",  # day-of-month 1
                "2026-02-02T12:00:00",  # Monday
            ],
            count=7,
        )

    def test_next_or_semantics_matches_dow_when_dom_impossible(self) -> None:
        # Day 29 of February OR any Sunday of February: February 2026
        # starts on a Sunday, so Sundays fire even though day 29 of
        # February 2026 does not exist.
        self.assert_matches(
            "0 0 29 2 0",
            NOW_2026_01_01,
            ["2026-02-01T00:00:00", "2026-02-08T00:00:00"],
            count=2,
        )

    def test_next_weekday_names_skip_weekend(self) -> None:
        # 2026-01-16 is a Friday; 09:00 already passed at 10:00.
        self.assert_matches(
            "0 9 * * mon-fri",
            "2026-01-16T10:00:00",
            [
                "2026-01-19T09:00:00",
                "2026-01-20T09:00:00",
                "2026-01-21T09:00:00",
            ],
            count=3,
        )

    def test_next_macro(self) -> None:
        self.assert_matches(
            "@hourly", NOW_2026_01_15_10_20, ["2026-01-15T11:00:00"]
        )
        self.assert_matches(
            "@daily", NOW_2026_01_15_10_20, ["2026-01-16T00:00:00"]
        )

    def test_next_month_names_and_day_ranges(self) -> None:
        self.assert_matches(
            "0 0 1 jan-mar *",
            NOW_2026_01_01,
            ["2026-02-01T00:00:00", "2026-03-01T00:00:00", "2027-01-01T00:00:00"],
            count=3,
        )

    def test_next_now_as_bare_date_and_datetime_object(self) -> None:
        # A bare date means midnight of that day, so 00:30 matches.
        self.assert_matches(
            "30 * * * *", "2026-01-15", ["2026-01-15T00:30:00"]
        )
        self.assert_matches(
            "30 * * * *",
            datetime(2026, 1, 15, 10, 20),
            ["2026-01-15T10:30:00"],
        )

    def test_next_timezone_aware_now_keeps_offset(self) -> None:
        result = self.tool.execute(
            mode="next",
            expression="30 * * * *",
            now="2026-01-15T10:20:00+00:00",
        )
        self.assertEqual(result["matches"], ["2026-01-15T10:30:00+00:00"])
        self.assertEqual(result["now"], "2026-01-15T10:20:00+00:00")

    def test_next_result_shape_and_iteration_checks(self) -> None:
        result = self.tool.execute(
            mode="next", expression="*/15 * * * *",
            now=NOW_2026_01_15_10_20, count=4,
        )
        self.assertEqual(result["mode"], "next")
        self.assertEqual(result["now"], NOW_2026_01_15_10_20)
        self.assertIsInstance(result["iteration_checks"], int)
        self.assertGreaterEqual(result["iteration_checks"], 4)
        self.assertNotIn("error", result)

    def test_next_default_now_smoke(self) -> None:
        # Omitting `now` uses the system clock; assert shape only so
        # the test stays deterministic.
        result = self.tool.execute(mode="next", expression="* * * * *", count=2)
        self.assertEqual(len(result["matches"]), 2)
        for match in result["matches"]:
            datetime.fromisoformat(match)  # must parse back

    def test_next_iteration_cap_on_unmatchable_expression(self) -> None:
        # February 31st never exists — the hard cap must stop the
        # search and return a structured error, not hang.
        result = self.tool.execute(
            mode="next",
            expression="0 0 31 2 *",
            now=NOW_2026_01_01,
            count=1,
            max_iterations=500,
        )
        self.assertEqual(result["error"]["type"], "iteration_cap_exceeded")
        self.assertIn("500", result["error"]["message"])
        self.assertEqual(result["matches"], [])
        self.assertEqual(result["iteration_checks"], 500)

    def test_next_iteration_cap_reports_partial_matches(self) -> None:
        # A dense expression matches every examined minute, so a tiny
        # cap yields exactly cap many matches of the requested count.
        result = self.tool.execute(
            mode="next",
            expression="* * * * *",
            now="2026-01-15T10:20:00",
            count=10,
            max_iterations=3,
        )
        self.assertEqual(result["error"]["type"], "iteration_cap_exceeded")
        self.assertEqual(
            result["matches"],
            [
                "2026-01-15T10:21:00",
                "2026-01-15T10:22:00",
                "2026-01-15T10:23:00",
            ],
        )

    def test_next_invalid_expression_returns_error_payload(self) -> None:
        result = self.tool.execute(
            mode="next", expression="60 * * * *", now=NOW_2026_01_01
        )
        self.assertEqual(result["mode"], "next")
        self.assertEqual(result["error"]["type"], "invalid_expression")
        self.assertEqual(
            result["error"]["field_errors"][0]["field"], "minute"
        )
        self.assertNotIn("matches", result)


class CronExpressionToolParameterTest(unittest.TestCase):
    """Malformed parameters raise ValueError before any computation."""

    def setUp(self) -> None:
        self.tool = CronExpressionTool()

    def assert_invalid(self, **params):
        with self.assertRaises(ValueError):
            self.tool.execute(**params)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="explain", expression="* * * * *")
        self.assert_invalid(mode=None, expression="* * * * *")
        self.assert_invalid(mode=True, expression="* * * * *")

    def test_invalid_expression_parameter(self) -> None:
        self.assert_invalid(mode="validate")
        self.assert_invalid(mode="validate", expression=None)
        self.assert_invalid(mode="validate", expression=123)
        self.assert_invalid(mode="validate", expression="")
        self.assert_invalid(mode="validate", expression="   ")
        self.assert_invalid(mode="validate", expression=True)
        self.assert_invalid(mode="validate", expression="*" * 201)

    def test_invalid_count(self) -> None:
        for bad in (0, -1, 101, "3", 1.5, True):
            self.assert_invalid(
                mode="next", expression="* * * * *",
                now=NOW_2026_01_01, count=bad,
            )

    def test_invalid_max_iterations(self) -> None:
        for bad in (0, -1, 5_000_001, "100", 1.5, True):
            self.assert_invalid(
                mode="next", expression="* * * * *",
                now=NOW_2026_01_01, max_iterations=bad,
            )

    def test_invalid_now(self) -> None:
        self.assert_invalid(mode="next", expression="* * * * *", now=12345)
        self.assert_invalid(mode="next", expression="* * * * *", now=True)
        self.assert_invalid(mode="next", expression="* * * * *", now="notadate")
        self.assert_invalid(
            mode="next", expression="* * * * *", now="2026-13-45T99:00:00"
        )

    def test_parameter_validation_precedes_expression_parsing(self) -> None:
        # Malformed parameters raise before any computation, even when
        # the expression is also invalid (documented contract).
        self.assert_invalid(
            mode="next", expression="60 * * * *", now=NOW_2026_01_01, count=0
        )
        self.assert_invalid(
            mode="next", expression="60 * * * *", now="notadate"
        )
        self.assert_invalid(
            mode="next", expression="60 * * * *",
            now=NOW_2026_01_01, max_iterations=0,
        )

    def test_unused_next_parameters_are_ignored_by_other_modes(self) -> None:
        # validate/describe never consult now/count/max_iterations.
        result = self.tool.execute(
            mode="validate", expression="* * * * *",
            now="notadate", count=0, max_iterations=-1,
        )
        self.assertTrue(result["valid"])

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectCronExpressionTool, CronExpressionTool)
        self.assertEqual(self.tool.name, "cron_expression_tool")
        self.assertIn("cron", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("CronExpressionTool", __all__)


if __name__ == "__main__":
    unittest.main()
