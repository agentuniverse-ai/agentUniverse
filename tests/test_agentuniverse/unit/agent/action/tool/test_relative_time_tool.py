#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_relative_time_tool.py

"""Offline unit tests for RelativeTimeTool.

The tool is built purely on the standard library (datetime / re / math)
and never touches the network. Every assertion is deterministic: the
reference "now" is injected through the ``RelativeTimeTool._now`` class
attribute, so the ladder is checked against hand-computed ground truths
at every threshold boundary (44s / 45s / 89s / 90s / 44min / 45min /
90min / 22h / 36h / 25d / 45d / 345d / 548d) in both English and
Chinese, for both past and future directions. The only test that reads
the real clock does so explicitly (``_now = None``) and asserts a value
whose bucket is hours wide, so clock jitter of milliseconds cannot
change the outcome.
"""

import unittest
from datetime import datetime, timedelta, timezone

from agentuniverse.agent.action.tool.common_tool import RelativeTimeTool
from agentuniverse.agent.action.tool.common_tool.relative_time_tool import (
    RelativeTimeTool as DirectRelativeTimeTool,
)

UTC = timezone.utc
# Fixed reference "now" injected via the _now class attribute.
NOW = datetime(2026, 10, 19, 12, 0, 0, tzinfo=UTC)
NOW_STR = NOW.isoformat(sep=" ")


def iso(moment: datetime) -> str:
    """Render a datetime the way the tool renders results."""
    return moment.isoformat(sep=" ")


# --------------------------------------------------------------------- #
# Hand-computed ladder ground truths (absolute delta -> rendered text).
# Moment.js-style ladder: <45s, <90s, <45min, <90min, <22h, <36h, <25d,
# <45d, <345d, <548d; months count 30 days, years 365 days; values
# round half away from zero (moment's Math.round).
# --------------------------------------------------------------------- #
LADDER_PAST = [
    (timedelta(seconds=44), "44 seconds ago", "44秒前"),
    (timedelta(seconds=45), "a minute ago", "1分钟前"),
    (timedelta(seconds=89), "a minute ago", "1分钟前"),
    (timedelta(seconds=90), "2 minutes ago", "2分钟前"),  # round(1.5)=2 half-up
    (timedelta(minutes=44), "44 minutes ago", "44分钟前"),
    (timedelta(minutes=45), "an hour ago", "1小时前"),
    (timedelta(minutes=90), "2 hours ago", "2小时前"),
    (timedelta(hours=22), "a day ago", "1天前"),
    (timedelta(hours=36), "2 days ago", "2天前"),
    (timedelta(days=25), "a month ago", "1个月前"),
    (timedelta(days=45), "2 months ago", "2个月前"),  # 45/30=1.5 -> 2 half-up
    (timedelta(days=345), "a year ago", "1年前"),
    (timedelta(days=548), "2 years ago", "2年前"),  # 548/365~1.501 -> 2
]
LADDER_FUTURE = [
    (timedelta(seconds=44), "in 44 seconds", "44秒后"),
    (timedelta(seconds=45), "in a minute", "1分钟后"),
    (timedelta(seconds=89), "in a minute", "1分钟后"),
    (timedelta(seconds=90), "in 2 minutes", "2分钟后"),
    (timedelta(minutes=44), "in 44 minutes", "44分钟后"),
    (timedelta(minutes=45), "in an hour", "1小时后"),
    (timedelta(minutes=90), "in 2 hours", "2小时后"),
    (timedelta(hours=22), "in a day", "1天后"),
    (timedelta(hours=36), "in 2 days", "2天后"),
    (timedelta(days=25), "in a month", "1个月后"),
    (timedelta(days=45), "in 2 months", "2个月后"),
    (timedelta(days=345), "in a year", "1年后"),
    (timedelta(days=548), "in 2 years", "2年后"),
]
# Mid-bucket values, including two half-up rounding pins where Python's
# banker's round() would disagree with moment.js Math.round semantics.
LADDER_EXTRA_PAST = [
    (timedelta(seconds=30), "30 seconds ago", "30秒前"),
    (timedelta(seconds=44.5), "45 seconds ago", "45秒前"),  # half-up pin
    (timedelta(seconds=150), "3 minutes ago", "3分钟前"),  # 2.5 -> 3 half-up pin
    (timedelta(hours=3), "3 hours ago", "3小时前"),
    (timedelta(days=10), "10 days ago", "10天前"),
    (timedelta(days=60), "2 months ago", "2个月前"),  # 60/30 = 2 exact
    (timedelta(days=100), "3 months ago", "3个月前"),  # 100/30 = 3.33 -> 3
    (timedelta(days=400), "a year ago", "1年前"),
    (timedelta(days=730), "2 years ago", "2年前"),  # 730/365 = 2 exact
]


class RelativeTimeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib RelativeTimeTool."""

    def setUp(self) -> None:
        self.tool = RelativeTimeTool()
        RelativeTimeTool._now = NOW
        self.addCleanup(setattr, RelativeTimeTool, "_now", None)

    # ------------------------------------------------------------------ #
    # Export sanity
    # ------------------------------------------------------------------ #

    def test_package_export_matches_module_class(self) -> None:
        self.assertIs(RelativeTimeTool, DirectRelativeTimeTool)
        self.assertEqual(self.tool.MODES, ("to_relative", "from_relative"))
        self.assertEqual(self.tool.LANGUAGES, ("en", "zh"))

    # ------------------------------------------------------------------ #
    # to_relative: threshold ladder ground truths (past)
    # ------------------------------------------------------------------ #

    def test_to_relative_ladder_boundaries_past_english(self) -> None:
        for delta, expected, _zh in LADDER_PAST:
            target = NOW - delta
            result = self.tool.execute(mode="to_relative", datetime=iso(target), language="en")
            self.assertEqual(result["result"], expected, msg=str(delta))
            self.assertEqual(result["direction"], "past", msg=str(delta))

    def test_to_relative_ladder_boundaries_past_chinese(self) -> None:
        for delta, _en, expected in LADDER_PAST:
            target = NOW - delta
            result = self.tool.execute(mode="to_relative", datetime=iso(target), language="zh")
            self.assertEqual(result["result"], expected, msg=str(delta))

    def test_to_relative_ladder_boundaries_future_english(self) -> None:
        for delta, expected, _zh in LADDER_FUTURE:
            target = NOW + delta
            result = self.tool.execute(mode="to_relative", datetime=iso(target), language="en")
            self.assertEqual(result["result"], expected, msg=str(delta))
            self.assertEqual(result["direction"], "future", msg=str(delta))

    def test_to_relative_ladder_boundaries_future_chinese(self) -> None:
        for delta, _en, expected in LADDER_FUTURE:
            target = NOW + delta
            result = self.tool.execute(mode="to_relative", datetime=iso(target), language="zh")
            self.assertEqual(result["result"], expected, msg=str(delta))

    def test_to_relative_mid_bucket_values(self) -> None:
        for delta, expected_en, expected_zh in LADDER_EXTRA_PAST:
            target = NOW - delta
            en = self.tool.execute(mode="to_relative", datetime=iso(target))
            zh = self.tool.execute(mode="to_relative", datetime=iso(target), language="zh")
            self.assertEqual(en["result"], expected_en, msg=str(delta))
            self.assertEqual(zh["result"], expected_zh, msg=str(delta))

    def test_to_relative_zero_delta(self) -> None:
        result = self.tool.execute(mode="to_relative", datetime=NOW_STR)
        self.assertEqual(result["result"], "0 seconds ago")
        self.assertEqual(result["delta_seconds"], 0.0)
        self.assertEqual(result["direction"], "past")  # documented: 0 renders as past

    def test_to_relative_full_result_payload(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="to_relative",
                datetime="2026-10-19T09:00:00+00:00",
                reference_datetime="2026-10-19 12:00:00+00:00",
            ),
            {
                "mode": "to_relative",
                "language": "en",
                "datetime": "2026-10-19 09:00:00+00:00",
                "reference_datetime": "2026-10-19 12:00:00+00:00",
                "delta_seconds": -10800.0,
                "direction": "past",
                "unit": "hour",
                "value": 3,
                "result": "3 hours ago",
            },
        )

    def test_to_relative_reference_argument_overrides_injected_now(self) -> None:
        result = self.tool.execute(
            mode="to_relative",
            datetime="2020-01-01 00:00:00+00:00",
            reference_datetime="2020-01-01 06:00:00+00:00",
        )
        self.assertEqual(result["result"], "6 hours ago")
        self.assertEqual(result["delta_seconds"], -21600.0)

    def test_to_relative_chinese_full_result_payload(self) -> None:
        result = self.tool.execute(mode="to_relative", datetime="2026-10-21 12:00:00+00:00", language="ZH")
        self.assertEqual(result["result"], "2天后")
        self.assertEqual(result["direction"], "future")
        self.assertEqual(result["unit"], "day")
        self.assertEqual(result["value"], 2)

    def test_to_relative_non_utc_offsets(self) -> None:
        # 16:00+08:00 is 08:00 UTC — 4 hours before the injected now.
        result = self.tool.execute(mode="to_relative", datetime="2026-10-19 16:00:00+08:00")
        self.assertEqual(result["result"], "4 hours ago")
        self.assertEqual(result["delta_seconds"], -14400.0)

    def test_to_relative_naive_pair(self) -> None:
        RelativeTimeTool._now = datetime(2026, 10, 19, 12, 0, 0)
        result = self.tool.execute(mode="to_relative", datetime="2026-10-19 09:30:00")
        self.assertEqual(result["result"], "3 hours ago")

    def test_to_relative_mixed_awareness_is_structured_error(self) -> None:
        # Injected now is timezone-aware, the input datetime is naive.
        result = self.tool.execute(mode="to_relative", datetime="2026-10-19 09:00:00")
        self.assertEqual(result["error"]["type"], "inconsistent_awareness")
        self.assertIn("naive", result["error"]["message"])

    def test_to_relative_invalid_datetime_is_structured_error(self) -> None:
        result = self.tool.execute(mode="to_relative", datetime="not-a-date")
        self.assertEqual(result["error"]["type"], "invalid_datetime")
        self.assertIn("ISO 8601", result["error"]["message"])
        self.assertEqual(result["error"]["position"], 0)
        self.assertEqual(result["mode"], "to_relative")

    def test_to_relative_invalid_reference_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="to_relative",
            datetime="2026-10-19 09:00:00+00:00",
            reference_datetime="yesterday",
        )
        self.assertEqual(result["error"]["type"], "invalid_datetime")

    def test_to_relative_real_clock_when_now_not_injected(self) -> None:
        RelativeTimeTool._now = None
        target = datetime.now(UTC) + timedelta(hours=2)
        result = self.tool.execute(mode="to_relative", datetime=iso(target))
        # The bucket is 22 hours wide; millisecond jitter cannot move it.
        self.assertEqual(result["result"], "in 2 hours")

    # ------------------------------------------------------------------ #
    # from_relative: parsing English and Chinese expressions
    # ------------------------------------------------------------------ #

    def test_from_relative_english_past(self) -> None:
        cases = [
            ("3 hours ago", -3 * 3600.0),
            ("30s ago", -30.0),
            ("2 hrs ago", -7200.0),
            ("a minute ago", -60.0),
            ("an hour ago", -3600.0),
            ("3 weeks ago", -21 * 86400.0),
            ("1 year ago", -365 * 86400.0),
        ]
        for text, offset in cases:
            result = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(result["offset_seconds"], offset, msg=text)
            self.assertEqual(
                result["result"],
                iso(NOW + timedelta(seconds=offset)),
                msg=text,
            )
            self.assertEqual(result["direction"], "past", msg=text)

    def test_from_relative_english_future(self) -> None:
        cases = [
            ("in 2 days", 2 * 86400.0),
            ("2 days from now", 2 * 86400.0),
            ("in a minute", 60.0),
            ("in an hour", 3600.0),
            ("in 5 minutes", 300.0),
        ]
        for text, offset in cases:
            result = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(result["offset_seconds"], offset, msg=text)
            self.assertEqual(result["result"], iso(NOW + timedelta(seconds=offset)), msg=text)
            self.assertEqual(result["direction"], "future", msg=text)

    def test_from_relative_chinese(self) -> None:
        cases = [
            ("3小时前", -3 * 3600.0),
            ("2天后", 2 * 86400.0),
            ("5分钟后", 300.0),
            ("1天前", -86400.0),
            ("10个月前", -300 * 86400.0),
            ("3 小时前", -3 * 3600.0),  # optional space between number and unit
        ]
        for text, offset in cases:
            result = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(result["offset_seconds"], offset, msg=text)
            self.assertEqual(result["result"], iso(NOW + timedelta(seconds=offset)), msg=text)

    def test_from_relative_just_now_chinese(self) -> None:
        for text in ("刚刚", "刚才"):
            result = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(result["result"], NOW_STR, msg=text)
            self.assertEqual(result["offset_seconds"], 0.0, msg=text)
            self.assertEqual(result["direction"], "now", msg=text)
            self.assertEqual(result["value"], 0, msg=text)
            self.assertIsNone(result["unit"], msg=text)

    def test_from_relative_case_insensitive_and_whitespace_collapsed(self) -> None:
        result = self.tool.execute(mode="from_relative", text="  3   HOURS   AGO  ")
        self.assertEqual(result["text"], "3 HOURS AGO")
        self.assertEqual(result["result"], "2026-10-19 09:00:00+00:00")

    def test_from_relative_full_result_payload(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="from_relative", text="in 2 days"),
            {
                "mode": "from_relative",
                "text": "in 2 days",
                "reference_datetime": NOW_STR,
                "direction": "future",
                "offset_seconds": 172800.0,
                "value": 2,
                "unit": "day",
                "result": "2026-10-21 12:00:00+00:00",
            },
        )

    def test_from_relative_language_option_does_not_restrict_parsing(self) -> None:
        result = self.tool.execute(mode="from_relative", text="3小时前", language="en")
        self.assertEqual(result["result"], "2026-10-19 09:00:00+00:00")

    def test_from_relative_reference_argument_overrides_injected_now(self) -> None:
        result = self.tool.execute(
            mode="from_relative",
            text="3 hours ago",
            reference_datetime="2020-01-01 00:00:00+00:00",
        )
        self.assertEqual(result["result"], "2019-12-31 21:00:00+00:00")

    def test_from_relative_naive_reference(self) -> None:
        RelativeTimeTool._now = datetime(2026, 10, 19, 12, 0, 0)
        result = self.tool.execute(mode="from_relative", text="3 hours ago")
        self.assertEqual(result["result"], "2026-10-19 09:00:00")

    def test_from_relative_invalid_reference_is_structured_error(self) -> None:
        result = self.tool.execute(
            mode="from_relative",
            text="3 hours ago",
            reference_datetime="soon",
        )
        self.assertEqual(result["error"]["type"], "invalid_datetime")

    # ------------------------------------------------------------------ #
    # both_dirs: round trips between the two modes
    # ------------------------------------------------------------------ #

    def test_round_trip_renders_stable_for_every_boundary(self) -> None:
        for delta, expected_en, expected_zh in LADDER_PAST:
            target = NOW - delta
            for language, expected in (("en", expected_en), ("zh", expected_zh)):
                rendered = self.tool.execute(mode="to_relative", datetime=iso(target), language=language)["result"]
                self.assertEqual(rendered, expected, msg=f"{delta} {language}")
                parsed = self.tool.execute(mode="from_relative", text=rendered)
                again = self.tool.execute(mode="to_relative", datetime=parsed["result"], language=language)["result"]
                self.assertEqual(again, rendered, msg=f"{delta} {language}")

    def test_round_trip_recovers_unit_aligned_datetimes(self) -> None:
        # Inputs aligned to N whole units are recovered exactly.
        for delta in (
            timedelta(seconds=44),
            timedelta(minutes=2),
            timedelta(minutes=44),
            timedelta(hours=3),
            timedelta(days=10),
            timedelta(days=60),
            timedelta(days=730),
        ):
            target = iso(NOW - delta)
            rendered = self.tool.execute(mode="to_relative", datetime=target)["result"]
            parsed = self.tool.execute(mode="from_relative", text=rendered)
            self.assertEqual(parsed["result"], target, msg=str(delta))

    def test_round_trip_article_buckets_map_to_one_unit(self) -> None:
        cases = [
            ("a minute ago", -60.0, "en"),
            ("an hour ago", -3600.0, "en"),
            ("a day ago", -86400.0, "en"),
            ("a month ago", -30 * 86400.0, "en"),
            ("a year ago", -365 * 86400.0, "en"),
            ("2 years ago", -730 * 86400.0, "en"),
            ("in a minute", 60.0, "en"),
            ("3小时前", -10800.0, "zh"),
            ("2天后", 172800.0, "zh"),
        ]
        for text, offset, language in cases:
            parsed = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(parsed["offset_seconds"], offset, msg=text)
            self.assertEqual(parsed["result"], iso(NOW + timedelta(seconds=offset)), msg=text)
            # Re-rendering stays inside the same bucket.
            again = self.tool.execute(mode="to_relative", datetime=parsed["result"], language=language)["result"]
            self.assertEqual(again, text, msg=text)

    def test_round_trip_just_now_renders_as_zero_seconds(self) -> None:
        # 刚刚 parses to exactly 'now', which to_relative renders with
        # the seconds bucket of the ladder (documented, bucket-consistent).
        parsed = self.tool.execute(mode="from_relative", text="刚刚")
        self.assertEqual(parsed["offset_seconds"], 0.0)
        again = self.tool.execute(mode="to_relative", datetime=parsed["result"])["result"]
        self.assertEqual(again, "0 seconds ago")

    # ------------------------------------------------------------------ #
    # from_relative: unknown units and malformed expressions
    # ------------------------------------------------------------------ #

    def test_from_relative_unknown_unit_english(self) -> None:
        result = self.tool.execute(mode="from_relative", text="3 fortnights ago")
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertEqual(result["error"]["position"], 2)  # 'fortnights' at index 2
        self.assertIn("fortnights", result["error"]["message"])

    def test_from_relative_unknown_unit_english_future(self) -> None:
        result = self.tool.execute(mode="from_relative", text="in 3 parsecs")
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertEqual(result["error"]["position"], 5)  # 'parsecs' at index 5

    def test_from_relative_unknown_unit_chinese(self) -> None:
        result = self.tool.execute(mode="from_relative", text="3光年前")
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertEqual(result["error"]["position"], 1)  # '光年' at index 1

    def test_from_relative_unknown_unit_from_now_shape(self) -> None:
        result = self.tool.execute(mode="from_relative", text="10 somethings from now")
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertEqual(result["error"]["position"], 3)

    def test_from_relative_malformed_missing_direction(self) -> None:
        result = self.tool.execute(mode="from_relative", text="3 hours")
        self.assertEqual(result["error"]["type"], "malformed_expression")
        self.assertEqual(result["error"]["position"], 7)  # where 'ago' should start
        self.assertIn("direction", result["error"]["message"])

    def test_from_relative_malformed_trailing_text(self) -> None:
        result = self.tool.execute(mode="from_relative", text="3 hours ago ago")
        self.assertEqual(result["error"]["type"], "malformed_expression")
        self.assertEqual(result["error"]["position"], 7)
        self.assertIn("ago ago", result["error"]["message"])

    def test_from_relative_malformed_unknown_tail(self) -> None:
        result = self.tool.execute(mode="from_relative", text="2 days from yesterday")
        self.assertEqual(result["error"]["type"], "malformed_expression")
        self.assertEqual(result["error"]["position"], 6)  # just after 'days'
        self.assertIn("from yesterday", result["error"]["message"])

    def test_from_relative_malformed_structures(self) -> None:
        for text in (
            "hours ago",  # no leading number
            "ago 3 hours",  # direction first
            "in a",  # unit missing
            "3小时",  # Chinese without 前/后 marker
            "3小时 ago",  # mixed grammars
            "刚刚好",  # not one of 刚刚 / 刚才
            "-3 hours ago",  # signed numbers are rejected
        ):
            result = self.tool.execute(mode="from_relative", text=text)
            self.assertEqual(result["error"]["type"], "malformed_expression", msg=text)
            self.assertIn("position", result["error"], msg=text)

    def test_from_relative_out_of_range_offset(self) -> None:
        result = self.tool.execute(mode="from_relative", text="999999999999 years ago")
        self.assertEqual(result["error"]["type"], "out_of_range")
        self.assertIn("overflow", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # Parameter validation (ValueError before any computation)
    # ------------------------------------------------------------------ #

    def test_unknown_mode_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="humanize", datetime=NOW_STR)
        self.assertIn("mode must be one of", str(ctx.exception))

    def test_bad_language_raises(self) -> None:
        for language in ("fr", "english", True, 1):
            with self.assertRaises(ValueError, msg=repr(language)):
                self.tool.execute(mode="to_relative", datetime=NOW_STR, language=language)

    def test_to_relative_missing_or_mistyped_datetime_raises(self) -> None:
        for bad in (None, "", "   ", 123, True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.tool.execute(mode="to_relative", datetime=bad)

    def test_from_relative_missing_or_mistyped_text_raises(self) -> None:
        for bad in (None, "", "   ", 42, False):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.tool.execute(mode="from_relative", text=bad)

    def test_from_relative_oversized_text_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="from_relative", text="3 hours ago " + "x" * 500)
        self.assertIn("character limit", str(ctx.exception))

    def test_mistyped_reference_datetime_raises(self) -> None:
        for bad in (123, True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                self.tool.execute(
                    mode="to_relative",
                    datetime=NOW_STR,
                    reference_datetime=bad,
                )


if __name__ == "__main__":
    unittest.main()
