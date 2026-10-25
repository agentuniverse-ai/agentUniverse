#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_cron_humanizer_tool.py

"""Offline unit tests for CronHumanizerTool.

The tool renders cron expressions as natural-language sentences using
only the standard library, so this suite runs fully offline.  Every
sentence assertion is a literal ground truth (English and Chinese,
all three styles) covering every field atom type — '*', single
values, lists, ranges, steps (*/n, a-b/n, a/n), month/day names and
@macros — plus the day-of-month/day-of-week OR semantics.  Warning
assertions pin the four smell patterns and their localized messages;
error assertions pin the full invalid-expression matrix (an invalid
expression is NEVER described) and the ValueError matrix for
malformed parameters.  Nothing here reads the clock or the network,
so results are deterministic.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import CronHumanizerTool
from agentuniverse.agent.action.tool.common_tool.cron_humanizer_tool import (
    CronHumanizerTool as DirectCronHumanizerTool,
)


class CronHumanizerEnFullTest(unittest.TestCase):
    """Ground-truth full-style English sentences."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def _text(self, expression: str) -> str:
        result = self.tool.execute(
            mode="describe", expression=expression, locale="en",
            style="full",
        )
        self.assertEqual(result["style"], "full")
        self.assertEqual(result["locale"], "en")
        return result["text"]

    def test_minute_single(self) -> None:
        self.assertEqual(self._text("30 * * * *"), "At minute 30 of every hour")

    def test_minute_step_star(self) -> None:
        self.assertEqual(self._text("*/15 * * * *"), "Every 15 minutes")

    def test_minute_step_from_value(self) -> None:
        self.assertEqual(
            self._text("10/20 * * * *"),
            "Every 20 minutes starting at minute 10",
        )

    def test_minute_stepped_range(self) -> None:
        self.assertEqual(
            self._text("10-50/10 * * * *"),
            "Every 10 minutes from minute 10 to minute 50",
        )

    def test_minute_list(self) -> None:
        self.assertEqual(
            self._text("5,15,45 * * * *"),
            "At minutes 5, 15 and 45 past every hour",
        )

    def test_minute_range(self) -> None:
        self.assertEqual(
            self._text("10-20 * * * *"),
            "At minutes 10 through 20 past every hour",
        )

    def test_every_minute(self) -> None:
        self.assertEqual(self._text("* * * * *"), "Every minute")

    def test_single_time(self) -> None:
        self.assertEqual(self._text("0 9 * * *"), "At 09:00")

    def test_time_list(self) -> None:
        self.assertEqual(
            self._text("30 9,17 * * *"), "At 09:30 and 17:30"
        )

    def test_minute_zero_across_hour_range(self) -> None:
        self.assertEqual(
            self._text("0 9-17 * * *"), "At minute 0 past hours 9 through 17"
        )

    def test_every_minute_during_hours(self) -> None:
        self.assertEqual(
            self._text("* 9-17 * * *"), "Every minute during hours 9 through 17"
        )

    def test_step_during_hours(self) -> None:
        self.assertEqual(
            self._text("*/15 9-17 * * *"),
            "Every 15 minutes during hours 9 through 17",
        )

    def test_dow_range(self) -> None:
        self.assertEqual(
            self._text("0 0 * * 1-5"), "At 00:00 on Monday through Friday"
        )

    def test_dow_list_names(self) -> None:
        self.assertEqual(
            self._text("0 0 * * mon,fri"), "At 00:00 on Monday and Friday"
        )

    def test_dow_seven_is_sunday(self) -> None:
        self.assertEqual(self._text("30 4 * * 7"), "At 04:30 on Sunday")

    def test_dom_single(self) -> None:
        self.assertEqual(
            self._text("0 0 1 * *"), "At 00:00 on day 1 of the month"
        )

    def test_dom_list(self) -> None:
        self.assertEqual(
            self._text("0 0 1,15 * *"),
            "At 00:00 on days 1 and 15 of the month",
        )

    def test_dom_range(self) -> None:
        self.assertEqual(
            self._text("0 0 1-5 * *"),
            "At 00:00 on days 1 through 5 of the month",
        )

    def test_month_single_and_names(self) -> None:
        self.assertEqual(self._text("0 9 * 3 *"), "At 09:00 in March")
        self.assertEqual(self._text("0 9 * mar *"), "At 09:00 in March")

    def test_month_range_names(self) -> None:
        self.assertEqual(
            self._text("0 9 * jan-mar *"), "At 09:00 in January through March"
        )

    def test_month_list_names(self) -> None:
        self.assertEqual(
            self._text("0 9 * jan,jun,jul *"),
            "At 09:00 in January, June and July",
        )

    def test_dom_dow_or_semantics(self) -> None:
        self.assertEqual(
            self._text("0 0 1 * 1"),
            "At 00:00 on day 1 of the month or on Monday "
            "(whichever matches)",
        )

    def test_macros(self) -> None:
        self.assertEqual(self._text("@daily"), "At 00:00")
        self.assertEqual(
            self._text("@hourly"), "At minute 0 of every hour"
        )
        self.assertEqual(self._text("@weekly"), "At 00:00 on Sunday")
        self.assertEqual(
            self._text("@monthly"), "At 00:00 on day 1 of the month"
        )
        self.assertEqual(
            self._text("@yearly"),
            "At 00:00 on day 1 of the month in January",
        )
        self.assertEqual(self._text("@midnight"), "At 00:00")
        self.assertEqual(
            self._text("@annually"),
            "At 00:00 on day 1 of the month in January",
        )

    def test_cartesian_times_bounded(self) -> None:
        self.assertEqual(
            self._text("15,45 8-18/4 * * *"),
            "At 08:15, 08:45, 12:15, 12:45, 16:15 and 16:45",
        )

    def test_month_step_expanded(self) -> None:
        self.assertEqual(
            self._text("0 0 15 */3 *"),
            "At 00:00 on day 15 of the month in January, April, "
            "July and October",
        )


class CronHumanizerEnShortVerboseTest(unittest.TestCase):
    """Ground-truth short/verbose-style English sentences."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def _text(self, expression: str, style: str) -> str:
        return self.tool.execute(
            mode="describe", expression=expression, locale="en", style=style
        )["text"]

    def test_short_hourly(self) -> None:
        self.assertEqual(self._text("30 * * * *", "short"), "Hourly at :30")

    def test_short_daily(self) -> None:
        self.assertEqual(self._text("0 9 * * *", "short"), "Daily at 09:00")

    def test_short_step(self) -> None:
        self.assertEqual(self._text("*/15 * * * *", "short"), "Every 15 min")

    def test_short_weekdays(self) -> None:
        self.assertEqual(
            self._text("0 9 * * 1-5", "short"), "Weekdays at 09:00"
        )

    def test_short_weekends(self) -> None:
        self.assertEqual(
            self._text("0 12 * * 0,6", "short"), "Weekends at 12:00"
        )

    def test_short_sundays(self) -> None:
        self.assertEqual(
            self._text("0 0 * * 0", "short"), "Sundays at 00:00"
        )

    def test_short_daily_time_list(self) -> None:
        self.assertEqual(
            self._text("30 9,17 * * *", "short"),
            "Daily at 09:30 and 17:30",
        )

    def test_short_every_minute_in_hours(self) -> None:
        self.assertEqual(
            self._text("* 9-17 * * *", "short"),
            "Every minute in hours 9-17",
        )

    def test_short_step_in_hours(self) -> None:
        self.assertEqual(
            self._text("*/15 9-17 * * *", "short"),
            "Every 15 min in hours 9-17",
        )

    def test_short_macros(self) -> None:
        self.assertEqual(self._text("@daily", "short"), "Daily at 00:00")
        self.assertEqual(self._text("@midnight", "short"), "Daily at 00:00")
        self.assertEqual(self._text("@hourly", "short"), "Hourly at :00")
        self.assertEqual(self._text("@monthly", "short"), "Monthly at 00:00")
        self.assertEqual(self._text("@yearly", "short"), "Yearly at 00:00")
        self.assertEqual(
            self._text("@annually", "short"), "Yearly at 00:00"
        )

    def test_verbose_annotation(self) -> None:
        self.assertEqual(
            self._text("30 * * * *", "verbose"),
            "At minute 30 of every hour "
            "(minute: 30; hour: *; day-of-month: *; month: *; "
            "day-of-week: *)",
        )

    def test_verbose_macro_annotation(self) -> None:
        self.assertEqual(
            self._text("@daily", "verbose"),
            "At 00:00 (@daily = minute: 0; hour: 0; day-of-month: *; "
            "month: *; day-of-week: *)",
        )


class CronHumanizerZhTest(unittest.TestCase):
    """Ground-truth Chinese sentences (all three styles)."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def _text(self, expression: str, style: str = "full") -> str:
        return self.tool.execute(
            mode="describe", expression=expression, locale="zh", style=style
        )["text"]

    def test_full_minute_single(self) -> None:
        self.assertEqual(self._text("30 * * * *"), "每小时的第30分钟")

    def test_full_step(self) -> None:
        self.assertEqual(self._text("*/15 * * * *"), "每15分钟")

    def test_full_step_from_value(self) -> None:
        self.assertEqual(self._text("10/20 * * * *"), "从第10分钟起每20分钟")

    def test_full_minute_list(self) -> None:
        self.assertEqual(
            self._text("5,15,45 * * * *"), "每小时的第5、15和45分钟"
        )

    def test_full_minute_range(self) -> None:
        self.assertEqual(self._text("10-20 * * * *"), "每小时的第10到20分钟")

    def test_full_every_minute(self) -> None:
        self.assertEqual(self._text("* * * * *"), "每分钟")

    def test_full_weekday_range(self) -> None:
        self.assertEqual(self._text("0 9 * * 1-5"), "每周一至周五的09:00")

    def test_full_weekday_list(self) -> None:
        self.assertEqual(
            self._text("0 9 * * mon,wed,fri"),
            "每周一、周三和周五的09:00",
        )

    def test_full_sunday_zero_and_name(self) -> None:
        self.assertEqual(self._text("0 0 * * 0"), "每周日的00:00")
        self.assertEqual(self._text("0 0 * * sun"), "每周日的00:00")

    def test_full_month_day(self) -> None:
        self.assertEqual(self._text("0 0 1 * *"), "每月1日的00:00")
        self.assertEqual(self._text("0 0 1 1 *"), "1月1日的00:00")

    def test_full_month_context(self) -> None:
        self.assertEqual(self._text("0 9 * 3 *"), "3月每天09:00")
        self.assertEqual(self._text("0 9 * jan-mar *"), "1月至3月每天09:00")

    def test_full_hours_range_minutes_all(self) -> None:
        self.assertEqual(self._text("* 9-17 * * *"), "每天9点至17点的每分钟")

    def test_full_dom_dow_or_semantics(self) -> None:
        self.assertEqual(
            self._text("0 0 1 * 1"), "每月1日或每周一（任一匹配）的00:00"
        )

    def test_full_macros(self) -> None:
        self.assertEqual(self._text("@daily"), "每天00:00")
        self.assertEqual(self._text("@hourly"), "每小时的第0分钟")
        self.assertEqual(self._text("@monthly"), "每月1日的00:00")
        self.assertEqual(self._text("@yearly"), "1月1日的00:00")

    def test_short_styles(self) -> None:
        self.assertEqual(self._text("30 * * * *", "short"), "每小时 :30")
        self.assertEqual(self._text("0 9 * * 1-5", "short"), "工作日09:00")
        self.assertEqual(self._text("@daily", "short"), "每天00:00")
        self.assertEqual(self._text("@monthly", "short"), "每月00:00")
        self.assertEqual(self._text("@yearly", "short"), "每年00:00")
        self.assertEqual(self._text("@hourly", "short"), "每小时 :00")

    def test_verbose_annotation(self) -> None:
        self.assertEqual(
            self._text("30 * * * *", "verbose"),
            "每小时的第30分钟 （分: 30；时: *；日: *；月: *；周: *）",
        )
        self.assertEqual(
            self._text("@daily", "verbose"),
            "每天00:00 （@daily 展开为 分: 0；时: 0；日: *；月: *；周: *）",
        )


class CronHumanizerFieldsTest(unittest.TestCase):
    """Per-field {field, raw, description} ground truths."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def test_english_breakdown(self) -> None:
        result = self.tool.execute(
            mode="describe_fields",
            expression="*/15 9-17/2 1,15 jan-mar mon-fri",
            locale="en",
        )
        self.assertEqual(result["mode"], "describe_fields")
        self.assertEqual(result["locale"], "en")
        self.assertEqual(
            [(f["field"], f["raw"]) for f in result["fields"]],
            [
                ("minute", "*/15"),
                ("hour", "9-17/2"),
                ("day-of-month", "1,15"),
                ("month", "jan-mar"),
                ("day-of-week", "mon-fri"),
            ],
        )
        self.assertEqual(
            [f["description"] for f in result["fields"]],
            [
                "every 15 minutes (0, 15, 30 and 45)",
                "every 2 hours from 9 to 17 (9, 11, 13, 15 and 17)",
                "on days 1 and 15 of the month",
                "in January through March",
                "on Monday through Friday",
            ],
        )

    def test_chinese_breakdown(self) -> None:
        result = self.tool.execute(
            mode="describe_fields",
            expression="*/15 9-17/2 1,15 jan-mar mon-fri",
            locale="zh",
        )
        self.assertEqual(
            [f["description"] for f in result["fields"]],
            [
                "每15分钟（0、15、30和45）",
                "9点到17点每2小时（9点、11点、13点、15点和17点）",
                "1日和15日",
                "1月至3月",
                "周一至周五",
            ],
        )

    def test_star_fields(self) -> None:
        result = self.tool.execute(
            mode="describe_fields", expression="* * * * *", locale="en"
        )
        self.assertEqual(
            [f["description"] for f in result["fields"]],
            [
                "every minute",
                "every hour",
                "every day of the month",
                "every month",
                "every day of the week",
            ],
        )
        zh = self.tool.execute(
            mode="describe_fields", expression="* * * * *", locale="zh"
        )
        self.assertEqual(
            [f["description"] for f in zh["fields"]],
            ["每分钟", "每小时", "每天", "每月", "每天"],
        )

    def test_macro_breakdown(self) -> None:
        result = self.tool.execute(
            mode="describe_fields", expression="@weekly", locale="en"
        )
        self.assertEqual(result["macro"], "@weekly")
        self.assertEqual(result["expanded"], "0 0 * * 0")
        self.assertEqual(
            [(f["field"], f["raw"], f["description"]) for f in result["fields"]],
            [
                ("minute", "0", "at minute 0"),
                ("hour", "0", "at hour 0"),
                ("day-of-month", "*", "every day of the month"),
                ("month", "*", "every month"),
                ("day-of-week", "0", "on Sunday"),
            ],
        )

    def test_name_and_list_fields(self) -> None:
        result = self.tool.execute(
            mode="describe_fields",
            expression="10-20 6,18 5-10 feb,dec sun,sat",
            locale="en",
        )
        self.assertEqual(
            [f["description"] for f in result["fields"]],
            [
                "at minutes 10 through 20",
                "at hours 6 and 18",
                "on days 5 through 10 of the month",
                "in February and December",
                "on Sunday and Saturday",
            ],
        )


class CronHumanizerWarningsTest(unittest.TestCase):
    """The four smell-warning patterns, English and Chinese."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def _warnings(self, expression: str, locale: str = "en"):
        return self.tool.execute(
            mode="describe", expression=expression, locale=locale
        )["warnings"]

    def test_day_never_occurs_in_restricted_month(self) -> None:
        warnings = self._warnings("0 0 31 2 *")
        self.assertEqual([w["type"] for w in warnings], ["day_month_mismatch"])
        self.assertEqual(
            warnings[0]["message"],
            "the day-of-month value(s) 31 never occur in February — "
            "this schedule can never fire",
        )
        # The expression itself is still valid and still described.
        result = self.tool.execute(mode="describe", expression="0 0 31 2 *")
        self.assertEqual(
            result["text"], "At 00:00 on day 31 of the month in February"
        )

    def test_day_never_occurs_in_short_month_list(self) -> None:
        warnings = self._warnings("0 0 31 4,6,9,11 *")
        self.assertEqual([w["type"] for w in warnings], ["day_month_mismatch"])
        self.assertIn("can never fire", warnings[0]["message"])

    def test_day_31_skips_short_months_when_month_unrestricted(self) -> None:
        warnings = self._warnings("0 0 31 * *")
        self.assertEqual([w["type"] for w in warnings], ["day_month_mismatch"])
        self.assertEqual(
            warnings[0]["message"],
            "day-of-month 31 does not exist in every month — the "
            "schedule silently skips February, April, June, September "
            "and November",
        )
        zh = self._warnings("0 0 31 * *", locale="zh")
        self.assertEqual(
            zh[0]["message"],
            "31日并非每个月都存在——该调度会在以下月份静默跳过："
            "2月、4月、6月、9月和11月",
        )

    def test_february_29_leap_year_only(self) -> None:
        warnings = self._warnings("0 0 29 2 *")
        self.assertEqual([w["type"] for w in warnings], ["day_month_mismatch"])
        self.assertEqual(
            warnings[0]["message"],
            "February 29 only exists in leap years — this schedule "
            "fires only in leap years",
        )
        zh = self._warnings("0 0 29 2 *", locale="zh")
        self.assertEqual(
            zh[0]["message"],
            "2月29日只在闰年存在——该调度仅在闰年触发",
        )

    def test_dom_dow_or_quirk(self) -> None:
        warnings = self._warnings("0 0 */2 * 1")
        self.assertEqual(
            [w["type"] for w in warnings], ["dom_dow_or_semantics"]
        )
        self.assertIn("OR semantics", warnings[0]["message"])
        zh = self._warnings("0 0 */2 * 1", locale="zh")
        self.assertIn("“或”语义", zh[0]["message"])

    def test_redundant_step_one(self) -> None:
        warnings = self._warnings("*/1 * * * *")
        self.assertEqual(
            [w["type"] for w in warnings], ["redundant_step_one"]
        )
        self.assertEqual(warnings[0]["field"], "minute")
        self.assertEqual(
            warnings[0]["message"],
            "the minute field step '/1' is redundant — '*/1' matches "
            "the same values as '*'",
        )
        dow = self._warnings("0 0 * * 1-5/1")
        self.assertEqual([w["type"] for w in dow], ["redundant_step_one"])
        self.assertEqual(dow[0]["field"], "day-of-week")
        zh = self._warnings("*/1 * * * *", locale="zh")
        self.assertEqual(
            zh[0]["message"],
            "分钟字段的“/1”步长是冗余的——“*/1”与“*”等价",
        )

    def test_step_exceeds_range(self) -> None:
        warnings = self._warnings("*/70 * * * *")
        self.assertEqual(
            [w["type"] for w in warnings], ["step_exceeds_range"]
        )
        self.assertEqual(warnings[0]["field"], "minute")
        self.assertEqual(
            warnings[0]["message"],
            "the minute field step 70 is wider than the span 0-59 — "
            "only value 0 can ever match",
        )
        dom = self._warnings("0 9 5/70 * *")
        self.assertEqual([w["type"] for w in dom], ["step_exceeds_range"])
        self.assertEqual(dom[0]["field"], "day-of-month")

    def test_multiple_warnings_stack(self) -> None:
        warnings = self._warnings("0 0 31 2 1")
        self.assertEqual(
            [w["type"] for w in warnings],
            ["day_month_mismatch", "dom_dow_or_semantics"],
        )

    def test_clean_expression_has_no_warnings(self) -> None:
        for expression in (
            "30 * * * *", "*/15 9-17 * * mon-fri", "0 0 1 1 *",
            "0 9 * * 0,6", "@daily",
        ):
            self.assertEqual(self._warnings(expression), [], expression)

    def test_describe_fields_also_carries_warnings(self) -> None:
        result = self.tool.execute(
            mode="describe_fields", expression="0 0 */2 * 1"
        )
        self.assertEqual(
            [w["type"] for w in result["warnings"]],
            ["dom_dow_or_semantics"],
        )


class CronHumanizerErrorTest(unittest.TestCase):
    """Invalid expressions are never described — structured errors."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def _error(self, expression: str, mode: str = "describe"):
        result = self.tool.execute(mode=mode, expression=expression)
        self.assertNotIn("text", result, expression)
        self.assertNotIn("fields", result, expression)
        return result["error"]

    def test_wrong_field_count(self) -> None:
        error = self._error("30 * *")
        self.assertEqual(error["type"], "invalid_expression")
        self.assertEqual(error["field_errors"][0]["field"], "expression")
        self.assertIn("exactly 5", error["field_errors"][0]["message"])

    def test_value_out_of_range(self) -> None:
        for expression, field in (
            ("60 * * * *", "minute"),
            ("0 24 * * *", "hour"),
            ("0 0 32 * *", "day-of-month"),
            ("0 0 1 13 *", "month"),
            ("0 0 * * 8", "day-of-week"),
        ):
            error = self._error(expression)
            self.assertEqual(error["type"], "invalid_expression", expression)
            self.assertEqual(error["field_errors"][0]["field"], field)

    def test_reversed_range(self) -> None:
        error = self._error("0 9-5 * * *")
        self.assertIn(
            "greater than the range end", error["field_errors"][0]["message"]
        )

    def test_unrecognized_names(self) -> None:
        error = self._error("0 0 * * foo")
        self.assertEqual(error["field_errors"][0]["field"], "day-of-week")
        self.assertIn("day names sun-sat", error["field_errors"][0]["message"])
        month = self._error("0 0 * frobnary *")
        self.assertEqual(month["field_errors"][0]["field"], "month")

    def test_non_positive_step(self) -> None:
        error = self._error("*/0 * * * *")
        self.assertIn(
            "positive integer", error["field_errors"][0]["message"]
        )

    def test_stray_comma(self) -> None:
        error = self._error("0 0 * * 1,,")
        self.assertIn(
            "empty list element", error["field_errors"][0]["message"]
        )

    def test_non_ascii_digit_forms_rejected(self) -> None:
        for expression, field in (
            ("+5 * * * *", "minute"),
            ("*/+3 * * * *", "minute"),
            ("* * 1_0 * *", "day-of-month"),
            ("*/1_0 * * * *", "minute"),
            ("0 0 1 １ *", "month"),
            ("0 0 １ * *", "day-of-month"),
            ("0 0 * * ７", "day-of-week"),
            ("0 0 * * +7", "day-of-week"),
            ("5-+10 * * * *", "minute"),
            ("0 0 * * ０", "day-of-week"),
        ):
            error = self._error(expression)
            self.assertEqual(
                error["type"], "invalid_expression", expression
            )
            self.assertEqual(
                error["field_errors"][0]["field"], field, expression
            )

    def test_ascii_zero_padded_forms_still_accepted(self) -> None:
        for expression in ("05 * * * *", "*/05 * * * *", "0 09 * * *"):
            result = self.tool.execute(
                mode="describe", expression=expression
            )
            self.assertNotIn("error", result, expression)

    def test_unknown_macro(self) -> None:
        error = self._error("@fortnightly")
        self.assertEqual(error["field_errors"][0]["field"], "macro")
        self.assertIn("unknown macro", error["field_errors"][0]["message"])

    def test_macro_with_extra_tokens(self) -> None:
        error = self._error("@daily extra")
        self.assertEqual(error["field_errors"][0]["field"], "macro")

    def test_describe_fields_mode_errors_too(self) -> None:
        error = self._error("60 * * * *", mode="describe_fields")
        self.assertEqual(error["type"], "invalid_expression")

    def test_error_payload_shape(self) -> None:
        result = self.tool.execute(
            mode="describe", expression="60 * * * *", locale="zh"
        )
        self.assertEqual(result["mode"], "describe")
        self.assertEqual(result["expression"], "60 * * * *")
        self.assertEqual(result["error"]["type"], "invalid_expression")
        self.assertTrue(result["error"]["field_errors"])


class CronHumanizerParamTest(unittest.TestCase):
    """Malformed parameters raise ValueError before any computation."""

    def setUp(self) -> None:
        self.tool = CronHumanizerTool()

    def test_unknown_mode(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="frob", expression="* * * * *")

    def test_unknown_locale(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="describe", expression="* * * * *", locale="fr"
            )

    def test_unknown_style(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="describe", expression="* * * * *", style="fancy"
            )

    def test_expression_type_errors(self) -> None:
        for bad in (None, "", 42, b"0 0 * * *", True):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="describe", expression=bad)

    def test_expression_length_limit(self) -> None:
        oversized = "0 " * 99 + "* * *"  # 201 characters
        self.assertGreater(len(oversized), 200)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="describe", expression=oversized)

    def test_locale_and_style_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="describe", expression="30 * * * *",
            locale="ZH", style="SHORT",
        )
        self.assertEqual(result["locale"], "zh")
        self.assertEqual(result["style"], "short")
        self.assertEqual(result["text"], "每小时 :30")

    def test_direct_import_identity(self) -> None:
        self.assertIs(CronHumanizerTool, DirectCronHumanizerTool)

    def test_deterministic_output(self) -> None:
        first = self.tool.execute(
            mode="describe", expression="*/15 9-17/2 1,15 jan-mar mon-fri",
            locale="zh", style="verbose",
        )
        second = self.tool.execute(
            mode="describe", expression="*/15 9-17/2 1,15 jan-mar mon-fri",
            locale="zh", style="verbose",
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
