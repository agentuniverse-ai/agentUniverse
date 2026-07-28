#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for DateTimeTool."""

import unittest

from agentuniverse.agent.action.tool.common_tool.datetime_tool import \
    DateTimeTool


class TestDateTimeToolNow(unittest.TestCase):

    def test_now_utc(self):
        tool = DateTimeTool()
        result = tool.execute(mode="now", timezone_str="UTC")
        self.assertEqual(result["status"], "success")
        self.assertIn("UTC", result["datetime"])

    def test_now_with_timezone(self):
        tool = DateTimeTool()
        result = tool.execute(mode="now", timezone_str="Asia/Shanghai")
        self.assertEqual(result["status"], "success")
        self.assertIn("Asia/Shanghai", result["timezone"])

    def test_invalid_timezone(self):
        tool = DateTimeTool()
        result = tool.execute(mode="now", timezone_str="Mars/Olympus")
        self.assertEqual(result["status"], "error")


class TestDateTimeToolConvert(unittest.TestCase):

    def test_convert_utc_to_shanghai(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="convert",
            datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC",
            target_timezone="Asia/Shanghai")
        self.assertEqual(result["status"], "success")
        self.assertIn("18:00:00", result["converted"])

    def test_convert_with_custom_format(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="convert",
            datetime_str="2026-01-15 10:00:00",
            timezone_str="UTC",
            target_timezone="UTC",
            fmt="%Y/%m/%d")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["converted"], "2026/01/15")


class TestDateTimeToolParse(unittest.TestCase):

    def test_parse_iso(self):
        tool = DateTimeTool()
        result = tool.execute(mode="parse", datetime_str="2026-01-15T10:30:00")
        self.assertEqual(result["status"], "success")

    def test_parse_slash_format(self):
        tool = DateTimeTool()
        result = tool.execute(mode="parse", datetime_str="2026/01/15")
        self.assertEqual(result["status"], "success")

    def test_parse_invalid_returns_error(self):
        tool = DateTimeTool()
        result = tool.execute(mode="parse", datetime_str="not-a-date")
        self.assertEqual(result["status"], "error")

    def test_parse_empty_string(self):
        tool = DateTimeTool()
        result = tool.execute(mode="parse", datetime_str="")
        self.assertEqual(result["status"], "error")


class TestDateTimeToolDiff(unittest.TestCase):

    def test_diff_days(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="diff",
            datetime_str="2026-01-01 00:00:00",
            end_datetime="2026-01-11 00:00:00",
            timezone_str="UTC",
            unit="days")
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["value"], 10.0)

    def test_diff_hours(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="diff",
            datetime_str="2026-01-01 00:00:00",
            end_datetime="2026-01-01 12:00:00",
            timezone_str="UTC",
            unit="hours")
        self.assertAlmostEqual(result["value"], 12.0)

    def test_diff_no_end_uses_now(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="diff",
            datetime_str="2020-01-01 00:00:00",
            timezone_str="UTC",
            unit="days")
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["value"], 0)

    def test_diff_invalid_unit(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="diff",
            datetime_str="2026-01-01",
            end_datetime="2026-01-02",
            unit="centuries")
        self.assertEqual(result["status"], "error")


class TestDateTimeToolFormat(unittest.TestCase):

    def test_format_with_custom(self):
        tool = DateTimeTool()
        result = tool.execute(
            mode="format",
            datetime_str="2026-03-15 14:30:00",
            timezone_str="UTC",
            fmt="%d %B %Y")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["formatted"], "15 March 2026")


class TestDateTimeToolValidation(unittest.TestCase):

    def test_unknown_mode(self):
        tool = DateTimeTool()
        result = tool.execute(mode="invalid")
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
