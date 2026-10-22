#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_diff_tool.py

"""Offline unit tests for TextDiffTool.

The tool is built purely on the standard library ``difflib`` and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: unified diffs are checked against hand-computed
ground-truth strings and, for the no-options path, byte-for-byte
against ``difflib.unified_diff`` itself; summary and words results are
checked against exact payload dicts computed independently; validation
and cap cases check the exact failure modes.
"""

import difflib
import unittest

from agentuniverse.agent.action.tool.common_tool import TextDiffTool
from agentuniverse.agent.action.tool.common_tool.text_diff_tool import (
    TextDiffTool as DirectTextDiffTool,
)

A_THREE_LINES = "one\ntwo\nthree"
B_THREE_LINES = "one\nTWO\nthree"

UNIFIED_MODIFICATION_GROUND_TRUTH = (
    "--- text1\n"
    "+++ text2\n"
    "@@ -1,3 +1,3 @@\n"
    " one\n"
    "-two\n"
    "+TWO\n"
    " three\n"
)

UNIFIED_INSERTION_GROUND_TRUTH = (
    "--- text1\n"
    "+++ text2\n"
    "@@ -1,2 +1,3 @@\n"
    " alpha\n"
    "+new\n"
    " beta\n"
)

UNIFIED_DELETION_GROUND_TRUTH = (
    "--- text1\n"
    "+++ text2\n"
    "@@ -1,3 +1,2 @@\n"
    " alpha\n"
    "-new\n"
    " beta\n"
)


class TextDiffToolUnifiedTest(unittest.TestCase):
    """Ground-truth tests for the unified mode."""

    def setUp(self) -> None:
        self.tool = TextDiffTool()

    def _run(self, text1, text2, **kwargs):
        return self.tool.execute(mode="unified", text1=text1, text2=text2, **kwargs)

    def test_identical_texts_produce_empty_diff(self) -> None:
        result = self._run(A_THREE_LINES, A_THREE_LINES)
        self.assertEqual(
            result,
            {
                "mode": "unified",
                "ignore_case": False,
                "ignore_whitespace": False,
                "context_lines": 3,
                "added_lines": 0,
                "removed_lines": 0,
                "equal_lines": 3,
                "hunks": 0,
                "identical": True,
                "result": "",
            },
        )

    def test_modification_ground_truth(self) -> None:
        result = self._run(A_THREE_LINES, B_THREE_LINES)
        self.assertEqual(result["result"], UNIFIED_MODIFICATION_GROUND_TRUTH)
        self.assertEqual(result["hunks"], 1)
        self.assertEqual(result["added_lines"], 1)
        self.assertEqual(result["removed_lines"], 1)
        self.assertEqual(result["equal_lines"], 2)
        self.assertFalse(result["identical"])

    def test_insertion_ground_truth(self) -> None:
        result = self._run("alpha\nbeta", "alpha\nnew\nbeta")
        self.assertEqual(result["result"], UNIFIED_INSERTION_GROUND_TRUTH)
        self.assertEqual(result["added_lines"], 1)
        self.assertEqual(result["removed_lines"], 0)
        self.assertEqual(result["equal_lines"], 2)

    def test_deletion_ground_truth(self) -> None:
        result = self._run("alpha\nnew\nbeta", "alpha\nbeta")
        self.assertEqual(result["result"], UNIFIED_DELETION_GROUND_TRUTH)
        self.assertEqual(result["added_lines"], 0)
        self.assertEqual(result["removed_lines"], 1)
        self.assertEqual(result["equal_lines"], 2)

    def test_empty_vs_content_ground_truth(self) -> None:
        result = self._run("", "abc\ndef")
        self.assertEqual(
            result["result"],
            "--- text1\n+++ text2\n@@ -0,0 +1,2 @@\n+abc\n+def\n",
        )
        self.assertEqual(result["added_lines"], 2)
        self.assertEqual(result["removed_lines"], 0)
        self.assertFalse(result["identical"])

    def test_content_vs_empty_ground_truth(self) -> None:
        result = self._run("abc\ndef", "")
        self.assertEqual(
            result["result"],
            "--- text1\n+++ text2\n@@ -1,2 +0,0 @@\n-abc\n-def\n",
        )
        self.assertEqual(result["removed_lines"], 2)

    def test_both_empty(self) -> None:
        result = self._run("", "")
        self.assertEqual(result["result"], "")
        self.assertEqual(result["hunks"], 0)
        self.assertTrue(result["identical"])
        self.assertEqual(result["equal_lines"], 0)

    def test_matches_difflib_unified_diff_byte_for_byte(self) -> None:
        """The no-options output must equal ``difflib.unified_diff``."""
        long_a = [f"line {i}" for i in range(40)]
        long_b = list(long_a)
        for i in (3, 17, 18, 35):
            long_b[i] = f"CHANGED {i}"
        long_b.insert(8, "inserted")
        del long_b[25]
        cases = [
            (A_THREE_LINES, B_THREE_LINES, 3),
            ("alpha\nbeta", "alpha\nnew\nbeta", 3),
            ("alpha\nnew\nbeta", "alpha\nbeta", 3),
            ("a\nb\nc\nd\ne\nf\ng\nh", "X\nb\nc\nd\ne\nf\ng\nY", 1),
            ("a\nb\nc\nd\ne\nf\ng\nh", "X\nb\nc\nd\ne\nf\ng\nY", 3),
            ("a\nb\nc\nd\ne\nf\ng\nh", "X\nb\nc\nd\ne\nf\ng\nY", 0),
            ("", "abc\ndef", 3),
            ("abc\ndef", "", 3),
            ("", "", 3),
            ("same", "same", 3),
            ("héllo 世界\nsecond line", "héllo 世界\nsecond line", 2),
            ("héllo 世界\nsecond", "hello 世界\nsecond", 2),
            ("\n".join(long_a), "\n".join(long_b), 3),
            ("\n".join(long_a), "\n".join(long_b), 0),
        ]
        for text1, text2, n in cases:
            with self.subTest(n=n, text1=text1[:20], text2=text2[:20]):
                # difflib yields content lines without a terminator (the
                # newline comes from readlines()-style input), so feed it
                # newline-terminated lines to get the canonical text form.
                expected = "".join(
                    difflib.unified_diff(
                        [line + "\n" for line in text1.splitlines()],
                        [line + "\n" for line in text2.splitlines()],
                        fromfile="text1",
                        tofile="text2",
                        n=n,
                    )
                )
                result = self._run(text1, text2, context_lines=n)
                self.assertEqual(result["result"], expected)

    def test_context_lines_controls_hunk_splitting(self) -> None:
        text1 = "a\nb\nc\nd\ne\nf\ng\nh"
        text2 = "X\nb\nc\nd\ne\nf\ng\nY"
        # The two changes are six equal lines apart: one hunk with the
        # default window of 3, two separate hunks with a window of 1.
        wide = self._run(text1, text2)
        self.assertEqual(wide["hunks"], 1)
        narrow = self._run(text1, text2, context_lines=1)
        self.assertEqual(narrow["hunks"], 2)
        # Each hunk header starts with "@@ -".
        self.assertEqual(narrow["hunks"], narrow["result"].count("@@ -"))
        self.assertIn("@@ -1,2 +1,2 @@\n-a\n+X\n b\n", narrow["result"])
        self.assertIn("@@ -7,2 +7,2 @@\n g\n-h\n+Y\n", narrow["result"])

    def test_context_lines_zero_drops_all_context(self) -> None:
        result = self._run("l1\nl2\nl3\nl4\nl5", "l1\nX\nl3\nl4\nl5", context_lines=0)
        self.assertEqual(result["result"], "--- text1\n+++ text2\n@@ -2 +2 @@\n-l2\n+X\n")

    def test_context_lines_accepts_numeric_string_and_bounds(self) -> None:
        result = self._run("a\nb\nc", "a\nB\nc", context_lines="2")
        self.assertEqual(result["context_lines"], 2)
        self.assertEqual(
            self._run("a\nb\nc", "a\nB\nc", context_lines=50)["context_lines"], 50
        )

    def test_ignore_case_hides_case_only_changes(self) -> None:
        result = self._run("Hello\nWorld", "hello\nworld", ignore_case=True)
        self.assertEqual(result["result"], "")
        self.assertEqual(result["hunks"], 0)
        self.assertEqual(result["equal_lines"], 2)
        self.assertEqual(result["added_lines"], 0)
        self.assertEqual(result["removed_lines"], 0)
        # The raw texts still differ, so `identical` stays False.
        self.assertFalse(result["identical"])
        # Without the option the change is visible.
        plain = self._run("Hello\nWorld", "hello\nworld")
        self.assertEqual(plain["removed_lines"], 2)
        self.assertEqual(plain["added_lines"], 2)

    def test_ignore_whitespace_renders_original_lines(self) -> None:
        result = self._run("  old  \nnext", "new\nnext", ignore_whitespace=True)
        self.assertEqual(result["hunks"], 1)
        self.assertIn("-  old  \n", result["result"])
        self.assertIn("+new\n", result["result"])
        self.assertIn(" next\n", result["result"])
        # Without the option the padded line counts as changed
        # ("next" still matches).
        plain = self._run("  old  \nnext", "new\nnext")
        self.assertEqual(plain["removed_lines"], 1)
        self.assertEqual(plain["added_lines"], 1)
        self.assertEqual(plain["equal_lines"], 1)

    def test_trailing_newline_is_not_distinguished(self) -> None:
        # str.splitlines() drops the final boundary, so "one\ntwo\n"
        # and "one\ntwo" produce the same lines.
        result = self._run("one\ntwo\n", "one\ntwo")
        self.assertEqual(result["result"], "")
        self.assertEqual(result["hunks"], 0)
        self.assertFalse(result["identical"])

    def test_diff_too_large_returns_structured_error(self) -> None:
        lines_a = "\n".join(f"line{i:04d}" for i in range(11_000))
        lines_b = "\n".join(f"text{i:04d}" for i in range(11_000))
        self.assertLessEqual(len(lines_a), 100_000)
        result = self._run(lines_a, lines_b)
        self.assertEqual(result["mode"], "unified")
        self.assertEqual(result["error"]["type"], "diff_too_large")
        self.assertIn("summary", result["error"]["message"])
        self.assertIn("200,000", result["error"]["message"])
        self.assertEqual(result["removed_lines"], 11_000)
        self.assertEqual(result["added_lines"], 11_000)
        self.assertNotIn("result", result)
        # Summary mode stays usable on the same inputs.
        summary = self.tool.execute(
            mode="summary", text1=lines_a, text2=lines_b
        )
        self.assertNotIn("error", summary)
        self.assertEqual(summary["similarity_ratio"], 0.0)


class TextDiffToolSummaryTest(unittest.TestCase):
    """Ground-truth tests for the summary mode."""

    def setUp(self) -> None:
        self.tool = TextDiffTool()

    def _run(self, text1, text2, **kwargs):
        return self.tool.execute(mode="summary", text1=text1, text2=text2, **kwargs)

    def test_identical_texts(self) -> None:
        self.assertEqual(
            self._run("one\ntwo", "one\ntwo"),
            {
                "mode": "summary",
                "ignore_case": False,
                "ignore_whitespace": False,
                "identical": True,
                "equal_after_normalization": True,
                "similarity_ratio": 1.0,
                "added_lines": 0,
                "removed_lines": 0,
                "equal_lines": 2,
                "total_lines_text1": 2,
                "total_lines_text2": 2,
            },
        )

    def test_modification_counts_and_ratio(self) -> None:
        result = self._run(A_THREE_LINES, B_THREE_LINES)
        self.assertEqual(
            result,
            {
                "mode": "summary",
                "ignore_case": False,
                "ignore_whitespace": False,
                "identical": False,
                "equal_after_normalization": False,
                "similarity_ratio": 0.666667,  # 2 * 2 equal / 6 total
                "added_lines": 1,
                "removed_lines": 1,
                "equal_lines": 2,
                "total_lines_text1": 3,
                "total_lines_text2": 3,
            },
        )

    def test_insertion_and_deletion_counts(self) -> None:
        insertion = self._run("alpha\nbeta", "alpha\nnew\nbeta")
        self.assertEqual(insertion["added_lines"], 1)
        self.assertEqual(insertion["removed_lines"], 0)
        self.assertEqual(insertion["equal_lines"], 2)
        self.assertEqual(insertion["similarity_ratio"], 0.8)  # 2 * 2 / 5
        deletion = self._run("alpha\nnew\nbeta", "alpha\nbeta")
        self.assertEqual(deletion["added_lines"], 0)
        self.assertEqual(deletion["removed_lines"], 1)
        self.assertEqual(deletion["similarity_ratio"], 0.8)

    def test_empty_texts(self) -> None:
        empty_vs_content = self._run("", "a\nb")
        self.assertEqual(empty_vs_content["added_lines"], 2)
        self.assertEqual(empty_vs_content["removed_lines"], 0)
        self.assertEqual(empty_vs_content["equal_lines"], 0)
        self.assertEqual(empty_vs_content["similarity_ratio"], 0.0)
        self.assertEqual(empty_vs_content["total_lines_text1"], 0)
        self.assertFalse(empty_vs_content["identical"])
        both_empty = self._run("", "")
        self.assertEqual(both_empty["similarity_ratio"], 1.0)
        self.assertTrue(both_empty["identical"])

    def test_ignore_case_option(self) -> None:
        plain = self._run("Hello World", "hello world")
        self.assertEqual(plain["similarity_ratio"], 0.0)
        self.assertEqual(plain["added_lines"], 1)
        self.assertEqual(plain["removed_lines"], 1)
        self.assertFalse(plain["equal_after_normalization"])
        folded = self._run("Hello World", "hello world", ignore_case=True)
        self.assertEqual(folded["similarity_ratio"], 1.0)
        self.assertEqual(folded["added_lines"], 0)
        self.assertEqual(folded["removed_lines"], 0)
        self.assertEqual(folded["equal_lines"], 1)
        self.assertFalse(folded["identical"])
        self.assertTrue(folded["equal_after_normalization"])

    def test_ignore_whitespace_option(self) -> None:
        result = self._run("  spaced  \n\t tabbed", "spaced\ntabbed", ignore_whitespace=True)
        self.assertTrue(result["equal_after_normalization"])
        self.assertEqual(result["similarity_ratio"], 1.0)
        self.assertFalse(result["identical"])
        plain = self._run("  spaced  \n\t tabbed", "spaced\ntabbed")
        self.assertEqual(plain["equal_lines"], 0)


class TextDiffToolWordsTest(unittest.TestCase):
    """Ground-truth tests for the words mode."""

    def setUp(self) -> None:
        self.tool = TextDiffTool()

    def _run(self, text1, text2, **kwargs):
        return self.tool.execute(mode="words", text1=text1, text2=text2, **kwargs)

    def test_insert_and_delete_ground_truth(self) -> None:
        result = self._run("the quick brown fox", "the very quick fox")
        self.assertEqual(
            result,
            {
                "mode": "words",
                "ignore_case": False,
                "identical": False,
                "equal_after_normalization": False,
                "similarity_ratio": 0.75,  # 2 * 3 equal / 8 total words
                "word_count_text1": 4,
                "word_count_text2": 4,
                "added_words": 1,
                "removed_words": 1,
                "equal_words": 3,
                "changed_regions": 2,
                "opcodes": [
                    {
                        "tag": "insert",
                        "text1_start": 1,
                        "text1_end": 1,
                        "text2_start": 1,
                        "text2_end": 2,
                        "text1_words": [],
                        "text2_words": ["very"],
                    },
                    {
                        "tag": "delete",
                        "text1_start": 2,
                        "text1_end": 3,
                        "text2_start": 3,
                        "text2_end": 3,
                        "text1_words": ["brown"],
                        "text2_words": [],
                    },
                ],
                "opcodes_truncated": False,
            },
        )

    def test_replace_ground_truth(self) -> None:
        result = self._run("one two three", "one dos three")
        self.assertEqual(result["changed_regions"], 1)
        self.assertEqual(
            result["opcodes"],
            [
                {
                    "tag": "replace",
                    "text1_start": 1,
                    "text1_end": 2,
                    "text2_start": 1,
                    "text2_end": 2,
                    "text1_words": ["two"],
                    "text2_words": ["dos"],
                }
            ],
        )
        self.assertEqual(result["added_words"], 1)
        self.assertEqual(result["removed_words"], 1)
        self.assertEqual(result["equal_words"], 2)
        self.assertEqual(result["similarity_ratio"], 0.666667)

    def test_identical_and_empty(self) -> None:
        result = self._run("same words here", "same words here")
        self.assertEqual(result["opcodes"], [])
        self.assertEqual(result["changed_regions"], 0)
        self.assertEqual(result["similarity_ratio"], 1.0)
        self.assertTrue(result["identical"])
        self.assertEqual(result["equal_words"], 3)
        empty = self._run("", "")
        self.assertEqual(empty["opcodes"], [])
        self.assertEqual(empty["word_count_text1"], 0)
        self.assertEqual(empty["similarity_ratio"], 1.0)
        self.assertTrue(empty["identical"])

    def test_ignore_case_option(self) -> None:
        plain = self._run("The cat sat", "the CAT sat")
        self.assertEqual(plain["changed_regions"], 1)
        self.assertEqual(plain["opcodes"][0]["tag"], "replace")
        self.assertEqual(plain["opcodes"][0]["text1_words"], ["The", "cat"])
        self.assertEqual(plain["opcodes"][0]["text2_words"], ["the", "CAT"])
        folded = self._run("The cat sat", "the CAT sat", ignore_case=True)
        self.assertEqual(folded["opcodes"], [])
        self.assertEqual(folded["changed_regions"], 0)
        self.assertTrue(folded["equal_after_normalization"])
        self.assertFalse(folded["identical"])
        self.assertEqual(folded["equal_words"], 3)

    def test_whitespace_runs_are_not_words(self) -> None:
        result = self._run("well--known  extra", "well--known extra")
        self.assertEqual(result["opcodes"], [])
        self.assertTrue(result["equal_after_normalization"])
        self.assertEqual(result["word_count_text2"], 2)

    def test_opcode_word_listing_is_capped(self) -> None:
        words_a = " ".join(f"a{i:03d}" for i in range(30))
        words_b = " ".join(f"b{i:03d}" for i in range(30))
        result = self._run(words_a, words_b)
        self.assertEqual(result["changed_regions"], 1)
        self.assertEqual(len(result["opcodes"]), 1)
        entry = result["opcodes"][0]
        self.assertEqual(entry["tag"], "replace")
        self.assertEqual(len(entry["text1_words"]), 20)
        self.assertEqual(len(entry["text2_words"]), 20)
        self.assertTrue(entry["text1_words_truncated"])
        self.assertTrue(entry["text2_words_truncated"])
        self.assertEqual(entry["text1_end"], 30)
        self.assertEqual(entry["text2_end"], 30)
        # Exact counts are unaffected by the listing cap.
        self.assertEqual(result["added_words"], 30)
        self.assertEqual(result["removed_words"], 30)
        self.assertEqual(result["equal_words"], 0)

    def test_opcode_listing_is_capped_with_exact_totals(self) -> None:
        keep = [f"keep{i:03d}" for i in range(111)]
        drop = [f"drop{i:03d}" for i in range(110)]
        tokens_a = [token for pair in zip(keep, drop) for token in pair] + [keep[-1]]
        tokens_b = [
            f"add{token[4:]}" if token.startswith("drop") else token
            for token in tokens_a
        ]
        result = self._run(" ".join(tokens_a), " ".join(tokens_b))
        self.assertEqual(result["changed_regions"], 110)
        self.assertEqual(len(result["opcodes"]), 100)
        self.assertTrue(result["opcodes_truncated"])
        self.assertEqual(result["removed_words"], 110)
        self.assertEqual(result["added_words"], 110)
        self.assertEqual(result["equal_words"], 111)


class TextDiffToolValidationTest(unittest.TestCase):
    """Strict validation and input-cap tests."""

    def setUp(self) -> None:
        self.tool = TextDiffTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="patch", text1="a", text2="b")
        self.assert_invalid(mode=None, text1="a", text2="b")
        self.assert_invalid(mode=123, text1="a", text2="b")

    def test_invalid_text_types(self) -> None:
        for bad in (None, 123, True, b"text", ["text"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="unified", text1=bad, text2="b")
                self.assert_invalid(mode="unified", text1="a", text2=bad)
                self.assert_invalid(mode="words", text1=bad, text2=bad)

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="unified", text1=oversized, text2="b")
        self.assert_invalid(mode="unified", text1="a", text2=oversized)
        self.assert_invalid(mode="words", text1=oversized, text2=oversized)
        ok = self.tool.execute(
            mode="unified", text1="a" * 100_000, text2="a" * 100_000
        )
        self.assertEqual(ok["result"], "")

    def test_invalid_flags(self) -> None:
        for bad in ("true", 1, 0, [True]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="summary", text1="a", text2="b", ignore_case=bad
                )
                self.assert_invalid(
                    mode="summary", text1="a", text2="b", ignore_whitespace=bad
                )

    def test_flags_default_to_false(self) -> None:
        result = self.tool.execute(mode="summary", text1="a", text2="b")
        self.assertFalse(result["ignore_case"])
        self.assertFalse(result["ignore_whitespace"])

    def test_invalid_context_lines(self) -> None:
        for bad in (-1, 51, "abc", True, 3.5, [3]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="unified",
                    text1="a\nb",
                    text2="a\nc",
                    context_lines=bad,
                )

    def test_context_lines_ignored_outside_unified_mode(self) -> None:
        result = self.tool.execute(
            mode="summary", text1="a", text2="b", context_lines=999
        )
        self.assertNotIn("error", result)
        words = self.tool.execute(
            mode="words", text1="a b", text2="a c", context_lines="not a number"
        )
        self.assertNotIn("error", words)

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextDiffTool, TextDiffTool)
        self.assertEqual(self.tool.name, "text_diff_tool")
        self.assertIn("unified", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextDiffTool", __all__)


if __name__ == "__main__":
    unittest.main()
