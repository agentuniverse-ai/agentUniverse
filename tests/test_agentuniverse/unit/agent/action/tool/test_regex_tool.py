#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for RegexTool."""

import unittest

from agentuniverse.agent.action.tool.common_tool.regex_tool import RegexTool


class TestRegexMatch(unittest.TestCase):

    def test_match_found(self):
        tool = RegexTool()
        result = tool.execute(mode="match", pattern=r"(\d+)-(\w+)", text="123-abc")
        self.assertTrue(result["matched"])
        self.assertEqual(result["match"], "123-abc")
        self.assertEqual(result["groups"], ["123", "abc"])

    def test_match_not_found(self):
        tool = RegexTool()
        result = tool.execute(mode="match", pattern="xyz", text="hello")
        self.assertFalse(result["matched"])

    def test_match_case_insensitive(self):
        tool = RegexTool()
        result = tool.execute(mode="match", pattern="hello", text="HELLO", flags="i")
        self.assertTrue(result["matched"])


class TestRegexExtract(unittest.TestCase):

    def test_extract_all_emails(self):
        tool = RegexTool()
        result = tool.execute(
            mode="extract",
            pattern=r"[\w.]+@[\w.]+",
            text="alice@test.com bob@example.org")
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["matches"][0]["match"], "alice@test.com")

    def test_extract_truncates_at_max(self):
        tool = RegexTool(max_matches=3)
        result = tool.execute(mode="extract", pattern=r"\d", text="123456789")
        self.assertEqual(result["count"], 3)
        self.assertTrue(result["truncated"])


class TestRegexReplace(unittest.TestCase):

    def test_replace_simple(self):
        tool = RegexTool()
        result = tool.execute(mode="replace", pattern=r"cat", text="cat dog cat", replacement="bird")
        self.assertEqual(result["result"], "bird dog bird")
        self.assertEqual(result["replacements_made"], 2)

    def test_replace_with_groups(self):
        tool = RegexTool()
        result = tool.execute(mode="replace", pattern=r"(\w+)@(\w+)", text="alice@test", replacement=r"\2.\1")
        self.assertEqual(result["result"], "test.alice")


class TestRegexSplit(unittest.TestCase):

    def test_split_by_comma(self):
        tool = RegexTool()
        result = tool.execute(mode="split", pattern=r",\s*", text="a, b,c,  d")
        self.assertEqual(result["parts"], ["a", "b", "c", "d"])


class TestRegexValidation(unittest.TestCase):

    def test_empty_pattern(self):
        tool = RegexTool()
        result = tool.execute(mode="match", pattern="", text="x")
        self.assertEqual(result["status"], "error")

    def test_invalid_pattern(self):
        tool = RegexTool()
        result = tool.execute(mode="match", pattern="[invalid", text="x")
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid regex", result["error"])

    def test_unknown_mode(self):
        tool = RegexTool()
        result = tool.execute(mode="fuzzy", pattern="x", text="x")
        self.assertEqual(result["status"], "error")

    def test_max_input_chars(self):
        tool = RegexTool(max_input_chars=10)
        result = tool.execute(mode="match", pattern="x", text="x" * 100)
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main(verbosity=2)
