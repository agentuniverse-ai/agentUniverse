#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_multi_text_search_tool.py

"""Offline unit tests for MultiTextSearchTool.

The tool is built purely on the standard library (``re``) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: each mode is checked against literal expected values
computed by hand, and context windows are additionally verified
against the defining formula ``text[max(0, s - N) : min(len, e + N)]``
with edge clamping at both ends of the entry.
"""

import re
import unittest

from agentuniverse.agent.action.tool.common_tool import MultiTextSearchTool
from agentuniverse.agent.action.tool.common_tool.multi_text_search_tool import (
    MultiTextSearchTool as DirectMultiTextSearchTool,
)

LOG_LINES = [
    "ERROR: database connection lost",
    "info: user logged in",
    "WARN: retrying ERROR again",
    "trace: noop",
]

CJK_TEXTS = ["你好世界", "hello 世界 world", "再见"]


class MultiTextSearchToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MultiTextSearchTool."""

    def setUp(self) -> None:
        self.tool = MultiTextSearchTool()

    def assert_invalid(self, **kwargs) -> None:
        """Assert the call is rejected by strict input validation."""
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    @staticmethod
    def context_of(text: str, start: int, end: int, chars: int) -> str:
        """The defining formula for the context window (edge-clamped)."""
        return text[max(0, start - chars): min(len(text), end + chars)]

    # ------------------------------------------------------------------ #
    # search mode ground truths
    # ------------------------------------------------------------------ #

    def test_search_regex_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="search",
            texts=LOG_LINES,
            pattern="ERROR",
            context_chars=3,
        )
        self.assertEqual(
            result,
            {
                "mode": "search",
                "regex": True,
                "case_sensitive": True,
                "pattern": "ERROR",
                "context_chars": 3,
                "total_entries": 4,
                "entries_scanned": 4,
                "matching_indices": [0, 2],
                "entry_count": 2,
                "match_count": 2,
                "matches": [
                    {
                        "index": 0,
                        "start": 0,
                        "end": 5,
                        "matched": "ERROR",
                        "context": "ERROR: d",
                    },
                    {
                        "index": 2,
                        "start": 15,
                        "end": 20,
                        "matched": "ERROR",
                        "context": "ng ERROR ag",
                    },
                ],
                "truncated": False,
                "truncation_reason": None,
            },
        )

    def test_search_literal_ground_truth(self) -> None:
        texts = ["literal a.c here", "abc not matched", "a.c twice a.c"]
        result = self.tool.execute(
            mode="search",
            texts=texts,
            pattern="a.c",
            regex=False,
            context_chars=4,
        )
        self.assertEqual(result["matching_indices"], [0, 2])
        self.assertEqual(result["match_count"], 3)
        spans = [(m["index"], m["start"], m["end"]) for m in result["matches"]]
        self.assertEqual(spans, [(0, 8, 11), (2, 0, 3), (2, 10, 13)])
        for match in result["matches"]:
            self.assertEqual(match["matched"], "a.c")
            self.assertEqual(
                match["context"],
                self.context_of(
                    texts[match["index"]],
                    match["start"],
                    match["end"],
                    4,
                ),
            )
        self.assertEqual(result["matches"][0]["context"], "ral a.c her")
        self.assertEqual(result["matches"][2]["context"], "ice a.c")
        self.assertFalse(result["truncated"])

    def test_search_case_insensitive_regex(self) -> None:
        result = self.tool.execute(
            mode="search",
            texts=["error here", "nope", "Error mixed", "ERROR loud"],
            pattern="error",
            case_sensitive=False,
            context_chars=0,
        )
        self.assertEqual(result["matching_indices"], [0, 2, 3])
        self.assertEqual(result["match_count"], 3)
        for match, expected in zip(
            result["matches"], ["error", "Error", "ERROR"]
        ):
            self.assertEqual(match["matched"], expected)

    def test_search_case_insensitive_literal(self) -> None:
        result = self.tool.execute(
            mode="search",
            texts=["error here", "ERROR here", "nope"],
            pattern="ERROR",
            regex=False,
            case_sensitive=False,
        )
        self.assertEqual(result["matching_indices"], [0, 1])

    def test_search_no_matches(self) -> None:
        result = self.tool.execute(mode="search", texts=LOG_LINES, pattern="zzz")
        self.assertEqual(
            result["matching_indices"],
            [],
        )
        self.assertEqual(result["matches"], [])
        self.assertEqual(result["match_count"], 0)
        self.assertFalse(result["truncated"])

    def test_search_context_clamping_and_formula(self) -> None:
        text = "0123456789"
        texts = [text, "mid needle mid", "needle"]
        for chars in (0, 1, 4, 40, 1000):
            result = self.tool.execute(
                mode="search",
                texts=texts,
                pattern="needle",
                context_chars=chars,
            )
            self.assertEqual(result["context_chars"], chars)
            for match in result["matches"]:
                self.assertEqual(
                    match["context"],
                    self.context_of(
                        texts[match["index"]],
                        match["start"],
                        match["end"],
                        chars,
                    ),
                )
        # Match at the very start of an entry: left side is clamped to 0,
        # and the default 40-char window covers the whole 16-char entry.
        result = self.tool.execute(
            mode="search", texts=["needle at start"], pattern="needle"
        )
        self.assertEqual(result["matches"][0]["start"], 0)
        self.assertEqual(result["matches"][0]["context"], "needle at start")
        # Match at the very end: right side is clamped to len(text).
        result = self.tool.execute(
            mode="search", texts=["ends with needle"], pattern="needle"
        )
        last = result["matches"][0]
        self.assertEqual((last["start"], last["end"]), (10, 16))
        self.assertEqual(last["context"], "ends with needle")

    def test_search_multi_match_entry(self) -> None:
        text = "ab ab ab"
        result = self.tool.execute(
            mode="search", texts=[text], pattern="ab", context_chars=2
        )
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(result["match_count"], 3)
        self.assertEqual(
            [(m["start"], m["end"]) for m in result["matches"]],
            [(0, 2), (3, 5), (6, 8)],
        )
        for match in result["matches"]:
            self.assertEqual(
                match["context"],
                self.context_of(text, match["start"], match["end"], 2),
            )

    def test_search_regex_flags_multiline(self) -> None:
        # Without MULTILINE, ^ only matches at the start of the entry.
        result = self.tool.execute(
            mode="search", texts=["a\nb"], pattern="^b"
        )
        self.assertEqual(result["match_count"], 0)
        result = self.tool.execute(
            mode="search", texts=["a\nb"], pattern="^b", flags="MULTILINE"
        )
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["matches"][0]["start"], 2)
        self.assertEqual(result["flags"], ["MULTILINE"])

    def test_search_regex_flags_dotall_and_list(self) -> None:
        result = self.tool.execute(
            mode="search", texts=["a\nb"], pattern="a.b"
        )
        self.assertEqual(result["match_count"], 0)
        result = self.tool.execute(
            mode="search", texts=["a\nb"], pattern="a.b", flags=["DOTALL", "i"]
        )
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["matches"][0]["start"], 0)
        self.assertEqual(result["matches"][0]["end"], 3)
        self.assertEqual(result["flags"], ["DOTALL", "I"])

    def test_search_zero_width_matches(self) -> None:
        # "x*" matches empty at every non-x position plus each "x" run;
        # ground truth mirrored from the stdlib scanner the tool wraps.
        text = "abc"
        expected = [m.span() for m in re.finditer("x*", text)]
        result = self.tool.execute(mode="search", texts=[text], pattern="x*")
        self.assertEqual(
            [(m["start"], m["end"]) for m in result["matches"]], expected
        )
        self.assertEqual(
            result["match_count"],
            len(list(re.finditer("x*", text))),
        )

    def test_search_cjk_texts(self) -> None:
        result = self.tool.execute(
            mode="search", texts=CJK_TEXTS, pattern="世界", context_chars=2
        )
        self.assertEqual(result["matching_indices"], [0, 1])
        # "你好世界": 世 at code point 2, 界 at 3, right edge clamped to 4.
        self.assertEqual(
            result["matches"][0],
            {
                "index": 0,
                "start": 2,
                "end": 4,
                "matched": "世界",
                "context": "你好世界",
            },
        )
        # "hello 世界 world": span (6, 8), context (4, 10).
        self.assertEqual(result["matches"][1]["start"], 6)
        self.assertEqual(result["matches"][1]["end"], 8)
        self.assertEqual(result["matches"][1]["context"], "o 世界 w")
        for match in result["matches"]:
            self.assertEqual(
                match["context"],
                self.context_of(
                    CJK_TEXTS[match["index"]],
                    match["start"],
                    match["end"],
                    2,
                ),
            )

    def test_search_astral_plane_offsets_are_code_points(self) -> None:
        text = "🌍星球🌍"
        result = self.tool.execute(
            mode="search", texts=[text], pattern="🌍", context_chars=1
        )
        self.assertEqual(
            [(m["start"], m["end"]) for m in result["matches"]],
            [(0, 1), (3, 4)],
        )
        self.assertEqual(result["matches"][0]["context"], "🌍星")
        self.assertEqual(result["matches"][1]["context"], "球🌍")

    # ------------------------------------------------------------------ #
    # filter mode
    # ------------------------------------------------------------------ #

    def test_filter_ground_truth(self) -> None:
        result = self.tool.execute(mode="filter", texts=LOG_LINES, pattern="ERROR")
        self.assertEqual(
            result,
            {
                "mode": "filter",
                "regex": True,
                "case_sensitive": True,
                "pattern": "ERROR",
                "invert": False,
                "total_entries": 4,
                "entries_scanned": 4,
                "matching_indices": [0, 2],
                "entry_count": 2,
                "match_count": 2,
                "results": [
                    {
                        "index": 0,
                        "text": LOG_LINES[0],
                        "match_count": 1,
                    },
                    {
                        "index": 2,
                        "text": LOG_LINES[2],
                        "match_count": 1,
                    },
                ],
                "truncated": False,
                "truncation_reason": None,
            },
        )

    def test_filter_per_entry_match_count(self) -> None:
        result = self.tool.execute(
            mode="filter", texts=["ab ab", "none", "ab"], pattern="ab"
        )
        self.assertEqual(
            [r["match_count"] for r in result["results"]], [2, 1]
        )
        self.assertEqual(result["match_count"], 3)

    def test_filter_invert(self) -> None:
        result = self.tool.execute(
            mode="filter", texts=LOG_LINES, pattern="ERROR", invert=True
        )
        self.assertEqual(
            result,
            {
                "mode": "filter",
                "regex": True,
                "case_sensitive": True,
                "pattern": "ERROR",
                "invert": True,
                "total_entries": 4,
                "entries_scanned": 4,
                "non_matching_indices": [1, 3],
                "entry_count": 2,
                "match_count": 0,
                "results": [
                    {"index": 1, "text": LOG_LINES[1]},
                    {"index": 3, "text": LOG_LINES[3]},
                ],
                "truncated": False,
                "truncation_reason": None,
            },
        )
        self.assertNotIn("matching_indices", result)

    def test_filter_literal_and_case(self) -> None:
        result = self.tool.execute(
            mode="filter",
            texts=["fn a.c()", "abc", "A.C"],
            pattern="a.c",
            regex=False,
            case_sensitive=False,
        )
        self.assertEqual(result["matching_indices"], [0, 2])

    # ------------------------------------------------------------------ #
    # count mode
    # ------------------------------------------------------------------ #

    def test_count_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="count", texts=["ab ab", "ab", ""], pattern="ab"
        )
        self.assertEqual(
            result,
            {
                "mode": "count",
                "regex": True,
                "case_sensitive": True,
                "pattern": "ab",
                "total_entries": 3,
                "entries_scanned": 3,
                "entries_with_matches": 2,
                "match_count": 3,
                "counts": [
                    {"index": 0, "count": 2},
                    {"index": 1, "count": 1},
                    {"index": 2, "count": 0},
                ],
                "truncated": False,
                "truncation_reason": None,
            },
        )

    def test_count_regex_word_boundary(self) -> None:
        result = self.tool.execute(
            mode="count",
            texts=["an apple and an apricot", "banana"],
            pattern=r"\ban\b",
        )
        self.assertEqual(
            result["counts"],
            [{"index": 0, "count": 2}, {"index": 1, "count": 0}],
        )
        self.assertEqual(result["match_count"], 2)

    def test_count_cjk(self) -> None:
        result = self.tool.execute(mode="count", texts=CJK_TEXTS, pattern="世界")
        self.assertEqual(
            result["counts"],
            [{"index": 0, "count": 1}, {"index": 1, "count": 1}, {"index": 2, "count": 0}],
        )

    # ------------------------------------------------------------------ #
    # index_of mode
    # ------------------------------------------------------------------ #

    def test_index_of_ground_truth(self) -> None:
        texts = ["alpha one", "beta two", "gamma three", "beta again"]
        result = self.tool.execute(
            mode="index_of",
            texts=texts,
            patterns=["beta", "gamma", "delta", "^alpha"],
        )
        self.assertEqual(
            result,
            {
                "mode": "index_of",
                "regex": True,
                "case_sensitive": True,
                "patterns": ["beta", "gamma", "delta", "^alpha"],
                "invert": False,
                "total_entries": 4,
                "pattern_count": 4,
                "found_count": 3,
                "results": [
                    {"pattern": "beta", "index": 1},
                    {"pattern": "gamma", "index": 2},
                    {"pattern": "delta", "index": None},
                    {"pattern": "^alpha", "index": 0},
                ],
                "truncated": False,
                "truncation_reason": None,
            },
        )

    def test_index_of_invert(self) -> None:
        texts = ["beta two", "beta again", "gamma three"]
        result = self.tool.execute(
            mode="index_of", texts=texts, patterns=["beta"], invert=True
        )
        self.assertEqual(result["results"], [{"pattern": "beta", "index": 2}])
        self.assertEqual(result["found_count"], 1)
        # Every entry matches → no non-matching index exists.
        result = self.tool.execute(
            mode="index_of", texts=["beta a", "beta b"], patterns=["beta"], invert=True
        )
        self.assertEqual(result["results"], [{"pattern": "beta", "index": None}])
        self.assertEqual(result["found_count"], 0)

    def test_index_of_literal_and_case(self) -> None:
        result = self.tool.execute(
            mode="index_of",
            texts=["x = 1", "a*b", "star"],
            patterns=["a*b", "STAR"],
            regex=False,
            case_sensitive=False,
        )
        self.assertEqual(
            result["results"],
            [{"pattern": "a*b", "index": 1}, {"pattern": "STAR", "index": 2}],
        )

    # ------------------------------------------------------------------ #
    # Result caps and truncation flags
    # ------------------------------------------------------------------ #

    def test_search_truncates_on_max_entries(self) -> None:
        texts = [f"hit number {i}" for i in range(150)]
        result = self.tool.execute(mode="search", texts=texts, pattern="hit")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["truncation_reason"], "max_entries")
        self.assertEqual(result["entry_count"], 100)
        self.assertEqual(result["match_count"], 100)
        self.assertEqual(result["matching_indices"], list(range(100)))
        self.assertEqual(result["total_entries"], 150)
        self.assertEqual(result["entries_scanned"], 101)

    def test_search_truncates_on_max_matches(self) -> None:
        # 2400 'x' characters → 1200 non-overlapping "xx" matches > cap.
        texts = ["x" * 2400]
        result = self.tool.execute(mode="search", texts=texts, pattern="xx")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["truncation_reason"], "max_matches")
        self.assertEqual(result["match_count"], 1000)
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(len(result["matches"]), 1000)
        self.assertEqual(result["matches"][0]["start"], 0)
        self.assertEqual(result["matches"][999]["start"], 1998)
        self.assertEqual(result["entries_scanned"], 1)

    def test_filter_truncates_on_max_entries(self) -> None:
        texts = [f"hit number {i}" for i in range(150)]
        result = self.tool.execute(mode="filter", texts=texts, pattern="hit")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["truncation_reason"], "max_entries")
        self.assertEqual(result["entry_count"], 100)
        self.assertEqual(
            [r["index"] for r in result["results"]], list(range(100))
        )
        self.assertEqual(result["total_entries"], 150)
        self.assertEqual(result["entries_scanned"], 101)

    def test_filter_truncates_on_max_matches(self) -> None:
        texts = ["x" * 2400, "unreached xx"]
        result = self.tool.execute(mode="filter", texts=texts, pattern="xx")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["truncation_reason"], "max_matches")
        self.assertEqual(result["entry_count"], 1)
        self.assertEqual(result["results"][0]["match_count"], 1000)
        self.assertEqual(result["match_count"], 1000)
        # The match cap is consumed inside entry 0, so scanning stops there.
        self.assertEqual(result["entries_scanned"], 1)

    def test_filter_invert_truncates_on_max_entries(self) -> None:
        texts = [f"miss number {i}" for i in range(150)]
        result = self.tool.execute(
            mode="filter", texts=texts, pattern="hit", invert=True
        )
        self.assertTrue(result["truncated"])
        self.assertEqual(result["truncation_reason"], "max_entries")
        self.assertEqual(result["entry_count"], 100)
        self.assertEqual(result["non_matching_indices"], list(range(100)))

    def test_count_is_never_truncated(self) -> None:
        texts = ["x" * 2400]
        result = self.tool.execute(mode="count", texts=texts, pattern="xx")
        self.assertFalse(result["truncated"])
        self.assertIsNone(result["truncation_reason"])
        self.assertEqual(result["counts"], [{"index": 0, "count": 1200}])
        self.assertEqual(result["match_count"], 1200)

    # ------------------------------------------------------------------ #
    # Invalid regex → structured error payload
    # ------------------------------------------------------------------ #

    def test_invalid_regex_returns_structured_error(self) -> None:
        result = self.tool.execute(
            mode="search", texts=LOG_LINES, pattern="(unclosed"
        )
        self.assertEqual(result["mode"], "search")
        self.assertNotIn("matches", result)
        self.assertEqual(result["error"]["type"], "invalid_regex")
        self.assertIn("(unclosed", result["error"]["message"])
        self.assertIn("unterminated subpattern", result["error"]["message"])

    def test_invalid_regex_in_pattern_batch(self) -> None:
        result = self.tool.execute(
            mode="index_of", texts=LOG_LINES, patterns=["ok", "["]
        )
        self.assertEqual(result["error"]["type"], "invalid_regex")
        self.assertIn("'['", result["error"]["message"])
        self.assertIn("unterminated character set", result["error"]["message"])

    def test_invalid_regex_literal_mode_never_compiles_raw(self) -> None:
        # A metacharacter storm is a valid literal pattern.
        result = self.tool.execute(
            mode="search",
            texts=["a (b) [c] d", "plain"],
            pattern="(b) [c]",
            regex=False,
        )
        self.assertEqual(result["matching_indices"], [0])

    # ------------------------------------------------------------------ #
    # Strict input validation
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="grep", texts=["a"], pattern="a")
        self.assert_invalid(mode=None, texts=["a"], pattern="a")

    def test_invalid_texts(self) -> None:
        self.assert_invalid(mode="search", texts=[], pattern="a")
        self.assert_invalid(mode="search", pattern="a")
        self.assert_invalid(mode="search", texts="one string", pattern="a")
        self.assert_invalid(mode="search", texts=("a", "b"), pattern="a")
        self.assert_invalid(mode="search", texts=123, pattern="a")
        self.assert_invalid(mode="search", texts=[None], pattern="a")
        self.assert_invalid(mode="search", texts=["a", 42], pattern="a")
        self.assert_invalid(mode="search", texts=["a", True], pattern="a")
        self.assert_invalid(mode="search", texts=[["a"]], pattern="a")
        self.assert_invalid(mode="search", texts=["a", b"bytes"], pattern="a")

    def test_texts_size_caps(self) -> None:
        many = ["x"] * 5001
        self.assert_invalid(mode="count", texts=many, pattern="x")
        long_entry = "x" * 100001
        self.assert_invalid(mode="count", texts=[long_entry], pattern="x")

    def test_invalid_pattern(self) -> None:
        self.assert_invalid(mode="search", texts=["a"])
        self.assert_invalid(mode="search", texts=["a"], pattern="")
        self.assert_invalid(mode="search", texts=["a"], pattern=None)
        self.assert_invalid(mode="search", texts=["a"], pattern=123)
        self.assert_invalid(mode="search", texts=["a"], pattern=True)

    def test_invalid_patterns_batch(self) -> None:
        self.assert_invalid(mode="index_of", texts=["a"])
        self.assert_invalid(mode="index_of", texts=["a"], patterns="a")
        self.assert_invalid(mode="index_of", texts=["a"], patterns=[])
        self.assert_invalid(mode="index_of", texts=["a"], patterns=[""])
        self.assert_invalid(mode="index_of", texts=["a"], patterns=[1])
        self.assert_invalid(mode="index_of", texts=["a"], patterns=["a", None])
        too_many = ["p"] * 101
        self.assert_invalid(mode="index_of", texts=["a"], patterns=too_many)

    def test_pattern_and_patterns_are_mode_exclusive(self) -> None:
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", patterns=["a"]
        )
        self.assert_invalid(
            mode="index_of", texts=["a"], pattern="a", patterns=["a"]
        )

    def test_invalid_boolean_options(self) -> None:
        self.assert_invalid(mode="search", texts=["a"], pattern="a", regex="true")
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", regex=None
        )
        self.assert_invalid(
            mode="search",
            texts=["a"],
            pattern="a",
            case_sensitive="yes",
        )
        self.assert_invalid(mode="filter", texts=["a"], pattern="a", invert=1)

    def test_invert_only_for_filter_and_index_of(self) -> None:
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", invert=True
        )
        self.assert_invalid(
            mode="count", texts=["a"], pattern="a", invert=True
        )

    def test_invalid_context_chars(self) -> None:
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", context_chars=-1
        )
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", context_chars=1001
        )
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", context_chars=True
        )
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", context_chars="40"
        )

    def test_invalid_flags(self) -> None:
        # flags are regex-mode only.
        self.assert_invalid(
            mode="search",
            texts=["a"],
            pattern="a",
            regex=False,
            flags="IGNORECASE",
        )
        self.assert_invalid(mode="search", texts=["a"], pattern="a", flags="VERBOSE")
        self.assert_invalid(mode="search", texts=["a"], pattern="a", flags=42)
        self.assert_invalid(mode="search", texts=["a"], pattern="a", flags=[])
        self.assert_invalid(
            mode="search", texts=["a"], pattern="a", flags=["MULTILINE", 7]
        )

    # ------------------------------------------------------------------ #
    # Determinism and packaging / registration
    # ------------------------------------------------------------------ #

    def test_deterministic_output(self) -> None:
        first = self.tool.execute(
            mode="search", texts=LOG_LINES, pattern="E\\w+", context_chars=5
        )
        second = self.tool.execute(
            mode="search", texts=LOG_LINES, pattern="E\\w+", context_chars=5
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["matching_indices"], [0, 2]
        )
        self.assertEqual(first["matches"][0]["matched"], "ERROR")
        self.assertEqual(first["matches"][1]["matched"], "ERROR")

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectMultiTextSearchTool, MultiTextSearchTool)
        self.assertEqual(self.tool.name, "multi_text_search_tool")
        self.assertIn("grep", self.tool.description)
        self.assertEqual(
            MultiTextSearchTool().max_entries,
            100,
        )
        self.assertEqual(MultiTextSearchTool().max_matches, 1000)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("MultiTextSearchTool", __all__)


if __name__ == "__main__":
    unittest.main()
