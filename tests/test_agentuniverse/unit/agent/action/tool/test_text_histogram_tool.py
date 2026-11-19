#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_histogram_tool.py

"""Offline unit tests for TextHistogramTool.

The tool is built purely on the standard library (math, collections)
and never touches the network, so this suite runs fully offline. Every
assertion is deterministic: frequency tables are checked against
hand-computed ground truths, entropy values against hand-derived
results for uniform and skewed distributions (log2 of the alphabet
size for uniform inputs, 0 for single-symbol inputs), and tie-break
ordering against explicit count-desc / lexicographic expectations.
"""

import math
import unittest

from agentuniverse.agent.action.tool.common_tool import TextHistogramTool
from agentuniverse.agent.action.tool.common_tool.text_histogram_tool import (
    TextHistogramTool as DirectTextHistogramTool,
)


def expected_entropy(counts):
    """Independent Shannon entropy (bits) for an explicit distribution."""
    total = sum(counts)
    return round(
        -sum((c / total) * math.log2(c / total) for c in counts), 6
    )


class TextHistogramToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextHistogramTool."""

    def setUp(self) -> None:
        self.tool = TextHistogramTool()

    # ------------------------------------------------------------------ #
    # chars mode
    # ------------------------------------------------------------------ #

    def test_chars_banana_ground_truth(self) -> None:
        result = self.tool.execute(mode="chars", text="banana")
        self.assertEqual(
            result,
            {
                "mode": "chars",
                "case_insensitive": False,
                "ignore_whitespace": True,
                "total_counted": 6,
                "unique_count": 3,
                "top_n": 20,
                "histogram": [
                    {"value": "a", "count": 3, "percent": 50.0},
                    {"value": "n", "count": 2, "percent": 33.3333},
                    {"value": "b", "count": 1, "percent": 16.6667},
                ],
            },
        )

    def test_chars_case_insensitive_folding(self) -> None:
        result = self.tool.execute(
            mode="chars", text="AaBb!", case_insensitive=True
        )
        self.assertEqual(result["total_counted"], 5)
        self.assertEqual(result["unique_count"], 3)
        self.assertEqual(
            result["histogram"],
            [
                {"value": "a", "count": 2, "percent": 40.0},
                {"value": "b", "count": 2, "percent": 40.0},
                {"value": "!", "count": 1, "percent": 20.0},
            ],
        )

    def test_chars_case_sensitive_by_default(self) -> None:
        result = self.tool.execute(mode="chars", text="Aa")
        # Two distinct values, tie broken lexicographically: A < a.
        self.assertEqual(
            result["histogram"],
            [
                {"value": "A", "count": 1, "percent": 50.0},
                {"value": "a", "count": 1, "percent": 50.0},
            ],
        )

    def test_chars_ignore_whitespace_default_and_include(self) -> None:
        included = self.tool.execute(
            mode="chars", text="a b\nc", ignore_whitespace=False
        )
        # All five characters counted once; code-point order:
        # '\n' (0x0A) < ' ' (0x20) < a < b < c.
        self.assertEqual(included["total_counted"], 5)
        self.assertEqual(
            [row["value"] for row in included["histogram"]],
            ["\n", " ", "a", "b", "c"],
        )
        ignored = self.tool.execute(mode="chars", text="a b\nc")
        self.assertEqual(ignored["total_counted"], 3)
        self.assertEqual(
            ignored["histogram"],
            [
                {"value": "a", "count": 1, "percent": 33.3333},
                {"value": "b", "count": 1, "percent": 33.3333},
                {"value": "c", "count": 1, "percent": 33.3333},
            ],
        )

    def test_chars_top_n_cap_keeps_full_unique_count(self) -> None:
        result = self.tool.execute(mode="chars", text="abcdef", top_n=3)
        self.assertEqual(result["top_n"], 3)
        self.assertEqual(result["unique_count"], 6)
        self.assertEqual(result["total_counted"], 6)
        self.assertEqual(len(result["histogram"]), 3)
        self.assertEqual(
            [row["value"] for row in result["histogram"]], ["a", "b", "c"]
        )

    def test_chars_whitespace_only_text_yields_empty_table(self) -> None:
        result = self.tool.execute(mode="chars", text=" \n\t ")
        self.assertEqual(result["histogram"], [])
        self.assertEqual(result["total_counted"], 0)
        self.assertEqual(result["unique_count"], 0)

    def test_chars_tie_break_is_lexicographic(self) -> None:
        result = self.tool.execute(mode="chars", text="zzyyxw")
        # z,y tie at 2; w,x tie at 1 — each group in code-point order,
        # regardless of first appearance in the text.
        self.assertEqual(
            [row["value"] for row in result["histogram"]],
            ["y", "z", "w", "x"],
        )

    # ------------------------------------------------------------------ #
    # words mode
    # ------------------------------------------------------------------ #

    def test_words_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="words", text="the cat sat on the mat the end"
        )
        self.assertEqual(result["mode"], "words")
        self.assertEqual(result["min_length"], 1)
        self.assertEqual(result["stopwords"], "none")
        self.assertEqual(result["total_counted"], 8)
        self.assertEqual(result["unique_count"], 6)
        self.assertEqual(result["filtered_out"], 0)
        self.assertEqual(
            result["histogram"],
            [
                {"value": "the", "count": 3, "percent": 37.5},
                {"value": "cat", "count": 1, "percent": 12.5},
                {"value": "end", "count": 1, "percent": 12.5},
                {"value": "mat", "count": 1, "percent": 12.5},
                {"value": "on", "count": 1, "percent": 12.5},
                {"value": "sat", "count": 1, "percent": 12.5},
            ],
        )

    def test_words_min_length_filter(self) -> None:
        result = self.tool.execute(
            mode="words",
            text="the cat sat on the mat the end",
            min_length=3,
        )
        self.assertEqual(result["min_length"], 3)
        self.assertEqual(result["total_counted"], 7)
        self.assertEqual(result["filtered_out"], 1)
        self.assertEqual(
            result["histogram"],
            [
                {"value": "the", "count": 3, "percent": 42.8571},
                {"value": "cat", "count": 1, "percent": 14.2857},
                {"value": "end", "count": 1, "percent": 14.2857},
                {"value": "mat", "count": 1, "percent": 14.2857},
                {"value": "sat", "count": 1, "percent": 14.2857},
            ],
        )

    def test_words_builtin_stopwords(self) -> None:
        result = self.tool.execute(
            mode="words", text="the cat and the dog", stopwords="builtin"
        )
        self.assertEqual(result["stopwords"], "builtin")
        self.assertEqual(result["total_counted"], 2)
        self.assertEqual(result["filtered_out"], 3)
        self.assertEqual(
            result["histogram"],
            [
                {"value": "cat", "count": 1, "percent": 50.0},
                {"value": "dog", "count": 1, "percent": 50.0},
            ],
        )

    def test_words_builtin_stopwords_with_case_folding(self) -> None:
        result = self.tool.execute(
            mode="words",
            text="The cat and the dog",
            stopwords="builtin",
            case_insensitive=True,
        )
        self.assertEqual(
            [row["value"] for row in result["histogram"]], ["cat", "dog"]
        )
        self.assertEqual(result["total_counted"], 2)

    def test_words_builtin_stopwords_case_sensitive_by_default(self) -> None:
        # Without case folding, capitalised "The" is not in the
        # lowercase builtin list and is kept — documented behaviour.
        result = self.tool.execute(
            mode="words", text="The cat and the dog", stopwords="builtin"
        )
        self.assertEqual(
            [row["value"] for row in result["histogram"]],
            ["The", "cat", "dog"],
        )

    def test_words_language_scoped_stopwords(self) -> None:
        english = self.tool.execute(
            mode="words", text="the cat 的", stopwords="en"
        )
        self.assertEqual(
            [row["value"] for row in english["histogram"]], ["cat", "的"]
        )
        chinese = self.tool.execute(
            mode="words", text="the cat 的", stopwords="zh"
        )
        # the/cat tie at 1 — lexicographic order puts "cat" first.
        self.assertEqual(
            [row["value"] for row in chinese["histogram"]], ["cat", "the"]
        )

    def test_words_custom_stopword_list(self) -> None:
        result = self.tool.execute(
            mode="words", text="cat dog bird", stopwords=["cat", "dog"]
        )
        self.assertEqual(result["stopwords"], "custom(2)")
        self.assertEqual(
            result["histogram"],
            [{"value": "bird", "count": 1, "percent": 100.0}],
        )

    def test_words_cjk_single_char_fallback(self) -> None:
        result = self.tool.execute(mode="words", text="中文测试中文")
        self.assertEqual(result["total_counted"], 6)
        self.assertEqual(result["unique_count"], 4)
        self.assertEqual(
            result["histogram"],
            [
                {"value": "中", "count": 2, "percent": 33.3333},
                {"value": "文", "count": 2, "percent": 33.3333},
                {"value": "测", "count": 1, "percent": 16.6667},
                {"value": "试", "count": 1, "percent": 16.6667},
            ],
        )

    def test_words_mixed_cjk_and_latin(self) -> None:
        result = self.tool.execute(mode="words", text="hello 世界 hello!")
        self.assertEqual(
            result["histogram"],
            [
                {"value": "hello", "count": 2, "percent": 50.0},
                {"value": "世", "count": 1, "percent": 25.0},
                {"value": "界", "count": 1, "percent": 25.0},
            ],
        )

    def test_words_zh_stopwords_match_single_char_tokens(self) -> None:
        result = self.tool.execute(
            mode="words", text="我在家", stopwords="zh"
        )
        self.assertEqual(
            result["histogram"],
            [{"value": "家", "count": 1, "percent": 100.0}],
        )

    def test_words_apostrophes_keep_contractions_together(self) -> None:
        result = self.tool.execute(mode="words", text="don't don't do")
        self.assertEqual(
            result["histogram"],
            [
                {"value": "don't", "count": 2, "percent": 66.6667},
                {"value": "do", "count": 1, "percent": 33.3333},
            ],
        )
        quoted = self.tool.execute(mode="words", text="'quoted'")
        self.assertEqual(
            [row["value"] for row in quoted["histogram"]], ["quoted"]
        )

    # ------------------------------------------------------------------ #
    # ngrams mode
    # ------------------------------------------------------------------ #

    def test_ngrams_bigram_ground_truth(self) -> None:
        result = self.tool.execute(mode="ngrams", text="a b c d", n=2)
        self.assertEqual(
            result,
            {
                "mode": "ngrams",
                "n": 2,
                "case_insensitive": False,
                "total_counted": 3,
                "unique_count": 3,
                "top_n": 20,
                "histogram": [
                    {"value": "a b", "count": 1, "percent": 33.3333},
                    {"value": "b c", "count": 1, "percent": 33.3333},
                    {"value": "c d", "count": 1, "percent": 33.3333},
                ],
            },
        )

    def test_ngrams_trigram(self) -> None:
        result = self.tool.execute(mode="ngrams", text="a b c d", n=3)
        self.assertEqual(
            [row["value"] for row in result["histogram"]], ["a b c", "b c d"]
        )
        self.assertEqual(result["total_counted"], 2)

    def test_ngrams_tie_break_lexicographic(self) -> None:
        result = self.tool.execute(
            mode="ngrams", text="the cat the cat the", n=2
        )
        self.assertEqual(result["total_counted"], 4)
        self.assertEqual(result["unique_count"], 2)
        # Both bigrams occur twice; "cat the" < "the cat" lexicographically.
        self.assertEqual(
            result["histogram"],
            [
                {"value": "cat the", "count": 2, "percent": 50.0},
                {"value": "the cat", "count": 2, "percent": 50.0},
            ],
        )

    def test_ngrams_cjk_tokens(self) -> None:
        result = self.tool.execute(mode="ngrams", text="中文测试", n=2)
        self.assertEqual(
            [row["value"] for row in result["histogram"]],
            ["中 文", "文 测", "测 试"],
        )
        self.assertEqual(result["total_counted"], 3)

    def test_ngrams_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="ngrams", text="The cat the", n=2, case_insensitive=True
        )
        self.assertEqual(
            [row["value"] for row in result["histogram"]],
            ["cat the", "the cat"],
        )

    def test_ngrams_fewer_tokens_than_n(self) -> None:
        result = self.tool.execute(mode="ngrams", text="one two", n=5)
        self.assertEqual(result["histogram"], [])
        self.assertEqual(result["total_counted"], 0)
        self.assertEqual(result["unique_count"], 0)

    def test_ngrams_five_is_the_maximum(self) -> None:
        result = self.tool.execute(
            mode="ngrams", text="a b c d e", n=5, top_n=1
        )
        self.assertEqual(result["total_counted"], 1)
        self.assertEqual(result["histogram"][0]["value"], "a b c d e")

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def test_summary_ground_truth(self) -> None:
        result = self.tool.execute(mode="summary", text="hello world")
        self.assertEqual(result["mode"], "summary")
        self.assertEqual(result["total_chars"], 11)
        self.assertEqual(result["total_words"], 2)
        self.assertEqual(result["total_lines"], 1)
        self.assertEqual(result["unique_chars"], 8)
        self.assertEqual(result["unique_words"], 2)
        # Non-whitespace chars: l:3, o:2, d/e/h/r/w:1 each (total 10).
        self.assertEqual(
            result["top_5_chars"],
            [
                {"value": "l", "count": 3, "percent": 30.0},
                {"value": "o", "count": 2, "percent": 20.0},
                {"value": "d", "count": 1, "percent": 10.0},
                {"value": "e", "count": 1, "percent": 10.0},
                {"value": "h", "count": 1, "percent": 10.0},
            ],
        )
        self.assertEqual(
            result["top_5_words"],
            [
                {"value": "hello", "count": 1, "percent": 50.0},
                {"value": "world", "count": 1, "percent": 50.0},
            ],
        )
        # Entropy over the raw 11-character distribution.
        self.assertEqual(
            result["entropy_bits"],
            expected_entropy([3, 2, 1, 1, 1, 1, 1, 1]),
        )

    def test_summary_lines_and_words(self) -> None:
        result = self.tool.execute(mode="summary", text="one\ntwo\nthree")
        self.assertEqual(result["total_chars"], 13)
        self.assertEqual(result["total_lines"], 3)
        self.assertEqual(result["total_words"], 3)
        # Raw unique chars include '\n': o,n,e,\n,t,w,h,r.
        self.assertEqual(result["unique_chars"], 8)
        self.assertEqual(result["unique_words"], 3)
        self.assertEqual(
            result["top_5_chars"],
            [
                {"value": "e", "count": 3, "percent": 27.2727},
                {"value": "o", "count": 2, "percent": 18.1818},
                {"value": "t", "count": 2, "percent": 18.1818},
                {"value": "h", "count": 1, "percent": 9.0909},
                {"value": "n", "count": 1, "percent": 9.0909},
            ],
        )
        self.assertEqual(
            [row["value"] for row in result["top_5_words"]],
            ["one", "three", "two"],
        )
        self.assertEqual(
            result["entropy_bits"],
            expected_entropy([3, 2, 2, 1, 1, 1, 1, 2]),  # e,o,t,n,w,h,r,\n
        )

    def test_summary_cjk_counts_each_char_as_a_word(self) -> None:
        result = self.tool.execute(mode="summary", text="你好你好")
        self.assertEqual(result["total_chars"], 4)
        self.assertEqual(result["total_words"], 4)
        self.assertEqual(result["total_lines"], 1)
        self.assertEqual(result["unique_chars"], 2)
        self.assertEqual(result["unique_words"], 2)
        self.assertEqual(
            result["top_5_words"],
            [
                {"value": "你", "count": 2, "percent": 50.0},
                {"value": "好", "count": 2, "percent": 50.0},
            ],
        )
        self.assertEqual(result["entropy_bits"], 1.0)

    def test_summary_trailing_newline_counts_as_one_line(self) -> None:
        single = self.tool.execute(mode="summary", text="a\n")
        self.assertEqual(single["total_lines"], 1)
        self.assertEqual(single["total_chars"], 2)
        self.assertEqual(single["total_words"], 1)
        self.assertEqual(single["entropy_bits"], 1.0)
        blank = self.tool.execute(mode="summary", text="\n\n")
        # Each newline terminates an (empty) line; nothing follows the
        # second one, so splitlines() yields two entries.
        self.assertEqual(blank["total_lines"], 2)
        self.assertEqual(blank["total_words"], 0)
        self.assertEqual(blank["unique_words"], 0)
        self.assertEqual(blank["top_5_words"], [])
        self.assertEqual(blank["entropy_bits"], 0.0)

    # ------------------------------------------------------------------ #
    # Entropy: uniform vs skewed (hand-computed exact values)
    # ------------------------------------------------------------------ #

    def assert_entropy(self, text: str, expected: float) -> None:
        result = self.tool.execute(mode="summary", text=text)
        self.assertEqual(result["entropy_bits"], expected)

    def test_entropy_hand_computed_values(self) -> None:
        self.assert_entropy("aaaa", 0.0)  # single symbol: no uncertainty
        self.assert_entropy("ab", 1.0)  # fair coin
        self.assert_entropy("aabb", 1.0)
        self.assert_entropy("abcd", 2.0)  # uniform over 4
        self.assert_entropy("abcdefgh", 3.0)  # uniform over 8
        self.assert_entropy("abcde", 2.321928)  # log2(5), rounded to 6
        self.assert_entropy("aaab", 0.811278)
        # p(a)=0.9: 0.9*log2(10/9) + 0.1*log2(10) = 0.468996 (6 d.p.)
        self.assert_entropy("aaaaaaaaab", 0.468996)

    def test_entropy_uniform_exceeds_skewed(self) -> None:
        uniform = self.tool.execute(
            mode="summary", text="abcdefghij"
        )["entropy_bits"]
        skewed = self.tool.execute(
            mode="summary", text="aaaaaaaaab"
        )["entropy_bits"]
        self.assertEqual(uniform, round(math.log2(10), 6))
        self.assertGreater(uniform, skewed)
        self.assertGreater(skewed, 0.0)

    # ------------------------------------------------------------------ #
    # Determinism and input caps
    # ------------------------------------------------------------------ #

    def test_results_are_deterministic(self) -> None:
        text = "Zebra apple zebra Apple 柠檬 柠檬 lemon!"
        for mode_kwargs in (
            {"mode": "chars"},
            {"mode": "words"},
            {"mode": "ngrams", "n": 2},
            {"mode": "summary"},
        ):
            with self.subTest(**mode_kwargs):
                first = self.tool.execute(text=text, **mode_kwargs)
                second = self.tool.execute(text=text, **mode_kwargs)
                self.assertEqual(first, second)

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        with self.assertRaises(ValueError):
            self.tool.execute(mode="chars", text=oversized)
        ok = self.tool.execute(mode="chars", text="a" * 100_000)
        self.assertEqual(ok["histogram"][0]["count"], 100_000)
        self.assertEqual(ok["histogram"][0]["percent"], 100.0)

    # ------------------------------------------------------------------ #
    # Error matrix (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="char", text="hello")
        self.assert_invalid(mode="CHARS", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123, text="hello")

    def test_invalid_text(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"], ""):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="chars", text=bad)
                self.assert_invalid(mode="summary", text=bad)

    def test_invalid_top_n(self) -> None:
        for bad in (0, -1, 501, "20", 2.5, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="chars", text="abc", top_n=bad)
        # Validated in every mode, including summary (which ignores it).
        self.assert_invalid(mode="summary", text="abc", top_n=0)
        self.assertEqual(
            self.tool.execute(mode="chars", text="abc", top_n=500)["top_n"],
            500,
        )

    def test_invalid_case_insensitive_flag(self) -> None:
        for bad in ("yes", 1, "true"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="chars", text="abc", case_insensitive=bad
                )

    def test_invalid_ignore_whitespace_flag(self) -> None:
        for bad in ("yes", 1, "true"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="chars", text="abc", ignore_whitespace=bad
                )

    def test_invalid_min_length(self) -> None:
        for bad in (0, -1, 51, "3", 2.5, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="words", text="hello", min_length=bad
                )

    def test_invalid_stopwords(self) -> None:
        for bad in (123, "english", "", ["the", 123], ["the", ""], [True]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="words", text="hello", stopwords=bad)

    def test_invalid_n(self) -> None:
        for bad in (None, 1, 6, "2", 2.5, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="ngrams", text="a b c", n=bad)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextHistogramTool, TextHistogramTool)
        self.assertEqual(self.tool.name, "text_histogram_tool")
        self.assertIn("histogram", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextHistogramTool", __all__)


if __name__ == "__main__":
    unittest.main()
