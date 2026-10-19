#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_summarizer_tool.py

"""Offline unit tests for TextSummarizerTool.

The tool is built purely on the standard library (re, collections) and
never touches the network or an LLM, so this suite runs fully offline.
Every assertion is deterministic: the summarize mode is checked against
hand-derived ground truths (sentence scores computed by the documented
formula — mean term frequency of content tokens times the position
weight 1 + 0.2 * (1 - idx / total)), the keywords mode against term
counts divided by the total content-token count, and the error matrix
against the documented ValueError / structured-error contract.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TextSummarizerTool
from agentuniverse.agent.action.tool.common_tool.text_summarizer_tool import (
    TextSummarizerTool as DirectTextSummarizerTool,
)

# --------------------------------------------------------------------- #
# Ground-truth fixtures
# --------------------------------------------------------------------- #
EN_TEXT = (
    "Quantum computers use qubits to store information. "
    "Coffee contains caffeine and antioxidants. "
    "The weather was pleasant yesterday afternoon. "
    "Qubits store quantum information as qubits do. "
    "Rain fell quietly over the hills. "
    "Bread is baked every morning."
)
# Content tokens (stop words removed) and document term frequencies:
#   S0 [quantum computers use qubits store information]  -> 11/6  raw
#   S1 [coffee contains caffeine antioxidants]           -> 4/4
#   S2 [weather pleasant yesterday afternoon]            -> 4/4
#   S3 [qubits store quantum information qubits]         -> 12/5
#   S4 [rain fell quietly hills]                         -> 4/4
#   S5 [bread baked every morning]                       -> 4/4
# Position weights over 6 sentences: 1.2, 7/6, 17/15, 1.1, 16/15, 31/30.
# Final scores: S0 2.2, S1 7/6, S2 17/15, S3 2.64, S4 16/15, S5 31/30.
# Top-3 by score: S3 (2.64), S0 (2.2), S1 (7/6) -> presented as [0, 1, 3].
EN_SENTENCES = [
    "Quantum computers use qubits to store information.",
    "Coffee contains caffeine and antioxidants.",
    "The weather was pleasant yesterday afternoon.",
    "Qubits store quantum information as qubits do.",
    "Rain fell quietly over the hills.",
    "Bread is baked every morning.",
]
# Total content tokens: 6 + 4 + 4 + 5 + 4 + 4 = 27.
# tf: qubits 3; quantum/store/information 2; everything else 1.

ZH_TEXT = (
    "量子计算机使用量子比特存储信息。"
    "咖啡含有抗氧化物质。"
    "量子比特同时处于零和一。"
    "今天天气宜人。"
    "量子算法利用纠缠加速计算。"
    "面包新鲜出炉。"
)
# Content tokens per sentence (CJK single ideographs, stop words
# removed): S0 15, S1 9, S2 9, S3 6, S4 12, S5 6 (total 57).
# Final scores: S0 2.64, S1 7/6, S2 2.140741, S3 1.466667,
# S4 2.133333, S5 31/30 -> top-3 S0, S2, S4.

ABBREV_TEXT = (
    "Dr. Smith met Mr. Lee and Prof. Ada, e.g. at noon. " "They left at 3 p.m. after the talk. " "It ended well!"
)
DECIMAL_TEXT = "Pi is about 3.14159 and docs live at example.com. " "Newton was born in the U.K. long ago."
ELLIPSIS_TEXT = "Wait... then it happened. Wow!"
NEWLINE_TEXT = "First line.\nSecond line.\n\nThird line."


class TextSummarizerToolTest(unittest.TestCase):
    """Offline deterministic test cases for the pure-Python tool."""

    def setUp(self) -> None:
        self.tool = TextSummarizerTool()

    # ------------------------------------------------------------------ #
    # summarize mode — English ground truth
    # ------------------------------------------------------------------ #

    def test_summarize_english_ground_truth(self) -> None:
        result = self.tool.execute(mode="summarize", text=EN_TEXT)
        self.assertEqual(
            result,
            {
                "mode": "summarize",
                "language": "en",
                "strategy": "max_sentences",
                "sentence_count": 6,
                "selected_count": 3,
                "selected_indices": [0, 1, 3],
                "scores": [2.2, 1.166667, 2.64],
                "summary": " ".join([EN_SENTENCES[i] for i in (0, 1, 3)]),
            },
        )

    def test_summarize_scores_match_documented_formula(self) -> None:
        result = self.tool.execute(mode="summarize", text=EN_TEXT, max_sentences=6)
        # Every sentence is selected, so scores come back in document
        # order and can be checked against the formula directly.
        expected = [2.2, 7 / 6, 17 / 15, 2.64, 16 / 15, 31 / 30]
        self.assertEqual(result["selected_indices"], [0, 1, 2, 3, 4, 5])
        for got, want in zip(result["scores"], expected, strict=True):
            self.assertAlmostEqual(got, want, places=5)

    def test_summarize_reorders_selection_by_original_position(self) -> None:
        # S3 has the highest score (2.64) but the summary must still
        # start with sentence 0 and keep document order.
        result = self.tool.execute(mode="summarize", text=EN_TEXT)
        self.assertEqual(result["selected_indices"], [0, 1, 3])
        self.assertTrue(result["summary"].startswith(EN_SENTENCES[0]))
        self.assertIn(EN_SENTENCES[3], result["summary"])
        self.assertLess(
            result["summary"].index(EN_SENTENCES[0]),
            result["summary"].index(EN_SENTENCES[3]),
        )

    def test_summarize_max_sentences_over_count_returns_all(self) -> None:
        result = self.tool.execute(mode="summarize", text=EN_TEXT, max_sentences=10)
        self.assertEqual(result["selected_count"], 6)
        self.assertEqual(result["selected_indices"], [0, 1, 2, 3, 4, 5])
        self.assertEqual(result["sentence_count"], 6)

    def test_summarize_single_sentence_text(self) -> None:
        result = self.tool.execute(mode="summarize", text="Only one sentence here.")
        self.assertEqual(result["sentence_count"], 1)
        self.assertEqual(result["selected_indices"], [0])
        self.assertEqual(result["summary"], "Only one sentence here.")
        # raw score 1.0 (four content tokens of tf 1) * 1.2 position weight
        self.assertAlmostEqual(result["scores"][0], 1.2, places=5)

    # ------------------------------------------------------------------ #
    # ratio vs max_sentences interplay
    # ------------------------------------------------------------------ #

    def test_ratio_half_matches_max_sentences(self) -> None:
        by_ratio = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.5)
        by_count = self.tool.execute(mode="summarize", text=EN_TEXT, max_sentences=3)
        self.assertEqual(by_ratio["strategy"], "ratio")
        self.assertEqual(by_count["strategy"], "max_sentences")
        self.assertEqual(by_ratio["selected_indices"], by_count["selected_indices"])
        self.assertEqual(by_ratio["summary"], by_count["summary"])

    def test_ratio_rounds_down_with_minimum_one(self) -> None:
        # int(0.1 * 6) == 0 -> clamped to 1 -> the single best sentence.
        result = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.1)
        self.assertEqual(result["selected_indices"], [3])
        self.assertEqual(result["selected_count"], 1)
        self.assertAlmostEqual(result["scores"][0], 2.64, places=5)

    def test_ratio_takes_precedence_over_max_sentences(self) -> None:
        result = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.1, max_sentences=5)
        self.assertEqual(result["strategy"], "ratio")
        self.assertEqual(result["selected_count"], 1)

    def test_ratio_partial_floor(self) -> None:
        # int(0.34 * 6) == 2 -> the two best sentences, document order.
        result = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.34)
        self.assertEqual(result["selected_indices"], [0, 3])

    def test_ratio_floor_immune_to_float_rounding(self) -> None:
        # 0.29 * 100 is exactly 29 in decimal but 28.999999999999996 as a
        # binary float; a naive int() truncation would keep 28 sentences.
        text = " ".join(f"Sentence number {i} talks about topics." for i in range(100))
        result = self.tool.execute(mode="summarize", text=text, ratio=0.29)
        self.assertEqual(result["sentence_count"], 100)
        self.assertEqual(result["selected_count"], 29)
        # 0.35 * 180 is exactly 63 in decimal but 62.99999999999999 as a
        # binary float.
        text = " ".join(f"Sentence number {i} talks about topics." for i in range(180))
        result = self.tool.execute(mode="summarize", text=text, ratio=0.35)
        self.assertEqual(result["sentence_count"], 180)
        self.assertEqual(result["selected_count"], 63)
        # A true non-integer product still floors: 0.34 * 6 = 2.04 -> 2.
        result = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.34)
        self.assertEqual(result["selected_count"], 2)

    # ------------------------------------------------------------------ #
    # summarize mode — Chinese ground truth
    # ------------------------------------------------------------------ #

    def test_summarize_chinese_ground_truth(self) -> None:
        result = self.tool.execute(mode="summarize", text=ZH_TEXT, max_sentences=3, language="zh")
        self.assertEqual(result["language"], "zh")
        self.assertEqual(result["sentence_count"], 6)
        self.assertEqual(result["selected_indices"], [0, 2, 4])
        for got, want in zip(result["scores"], [2.64, 2.140741, 2.133333], strict=True):
            self.assertAlmostEqual(got, want, places=5)
        # Chinese sentences are concatenated without a separator.
        self.assertEqual(
            result["summary"],
            "量子计算机使用量子比特存储信息。" "量子比特同时处于零和一。" "量子算法利用纠缠加速计算。",
        )

    def test_summarize_chinese_cjk_terminators(self) -> None:
        # The fullwidth exclamation/question marks are intentional CJK
        # terminators.
        text = "今天很好！明天下雨？后天晴。"  # noqa: RUF001
        result = self.tool.execute(mode="summarize", text=text, language="zh")
        self.assertEqual(result["sentence_count"], 3)

    # ------------------------------------------------------------------ #
    # Sentence segmentation — abbreviations and guards
    # ------------------------------------------------------------------ #

    def test_abbreviations_do_not_split_sentences(self) -> None:
        result = self.tool.execute(mode="summarize", text=ABBREV_TEXT)
        self.assertEqual(result["sentence_count"], 3)
        best = self.tool.execute(mode="summarize", text=ABBREV_TEXT, max_sentences=1)
        self.assertEqual(best["summary"], "Dr. Smith met Mr. Lee and Prof. Ada, e.g. at noon.")

    def test_company_and_etc_abbreviations(self) -> None:
        text = "Apple Inc. released Swift. " "It replaced Objective-C, etc. quickly."
        result = self.tool.execute(mode="summarize", text=text)
        self.assertEqual(result["sentence_count"], 2)
        self.assertTrue(result["summary"].startswith("Apple Inc. released Swift."))

    def test_decimals_domains_and_initials_stay_intact(self) -> None:
        result = self.tool.execute(mode="summarize", text=DECIMAL_TEXT)
        self.assertEqual(result["sentence_count"], 2)
        self.assertIn("3.14159", result["summary"])
        self.assertIn("example.com", result["summary"])
        self.assertIn("U.K.", result["summary"])

    def test_ellipsis_terminates_sentence(self) -> None:
        # '...' collapses to a single ellipsis terminator.
        result = self.tool.execute(mode="summarize", text=ELLIPSIS_TEXT, max_sentences=5)
        self.assertEqual(result["sentence_count"], 3)

    def test_newlines_segment_sentences(self) -> None:
        result = self.tool.execute(mode="summarize", text=NEWLINE_TEXT)
        self.assertEqual(result["sentence_count"], 3)
        self.assertEqual(result["selected_count"], 3)

    def test_text_without_terminator_is_one_sentence(self) -> None:
        result = self.tool.execute(mode="summarize", text="no terminator here")
        self.assertEqual(result["sentence_count"], 1)
        self.assertEqual(result["summary"], "no terminator here")

    # ------------------------------------------------------------------ #
    # keywords mode
    # ------------------------------------------------------------------ #

    def test_keywords_english_ground_truth(self) -> None:
        result = self.tool.execute(mode="keywords", text=EN_TEXT, top_k=5)
        self.assertEqual(result["mode"], "keywords")
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["top_k"], 5)
        terms = [entry["term"] for entry in result["keywords"]]
        counts = [entry["count"] for entry in result["keywords"]]
        weights = [entry["weight"] for entry in result["keywords"]]
        # 'qubits' dominates; the count-2 ties break alphabetically.
        self.assertEqual(terms, ["qubits", "information", "quantum", "store", "afternoon"])
        self.assertEqual(counts, [3, 2, 2, 2, 1])
        self.assertEqual(weights, [0.111111, 0.074074, 0.074074, 0.074074, 0.037037])

    def test_keywords_weights_sorted_and_normalized(self) -> None:
        result = self.tool.execute(mode="keywords", text=EN_TEXT, top_k=20)
        weights = [entry["weight"] for entry in result["keywords"]]
        self.assertEqual(weights, sorted(weights, reverse=True))
        self.assertLessEqual(sum(weights), 1.0 + 1e-9)

    def test_keywords_chinese_ground_truth(self) -> None:
        result = self.tool.execute(mode="keywords", text=ZH_TEXT, language="zh", top_k=3)
        terms = [entry["term"] for entry in result["keywords"]]
        counts = [entry["count"] for entry in result["keywords"]]
        # 57 content tokens in total; count-4 ties break alphabetically
        # by Unicode order ('子' < '量').
        self.assertEqual(terms, ["子", "量", "算"])
        self.assertEqual(counts, [4, 4, 3])
        self.assertAlmostEqual(result["keywords"][0]["weight"], 4 / 57, places=5)

    def test_keywords_top_k_capped_by_vocabulary(self) -> None:
        result = self.tool.execute(mode="keywords", text=EN_TEXT, top_k=50)
        self.assertLessEqual(len(result["keywords"]), 50)
        self.assertTrue(result["keywords"])

    def test_keywords_exclude_stop_words(self) -> None:
        result = self.tool.execute(mode="keywords", text=EN_TEXT, top_k=50)
        terms = {entry["term"] for entry in result["keywords"]}
        self.assertNotIn("the", terms)
        self.assertNotIn("and", terms)
        self.assertNotIn("was", terms)

    def test_keywords_mixed_script_under_en_language(self) -> None:
        result = self.tool.execute(mode="keywords", text="Quantum 量子 computers.", top_k=3)
        self.assertEqual(
            [entry["term"] for entry in result["keywords"]],
            ["computers", "quantum", "子"],
        )

    def test_language_hint_case_insensitive(self) -> None:
        result = self.tool.execute(mode="summarize", text=ZH_TEXT, language="ZH", max_sentences=1)
        self.assertEqual(result["language"], "zh")
        result = self.tool.execute(mode="keywords", text=EN_TEXT, language="EN")
        self.assertEqual(result["language"], "en")

    # ------------------------------------------------------------------ #
    # Structured content-level errors
    # ------------------------------------------------------------------ #

    def test_error_no_sentences_for_punctuation_only_text(self) -> None:
        for text in ("!!! ???", "。。。", "?!.."):
            result = self.tool.execute(mode="summarize", text=text)
            self.assertEqual(result["mode"], "summarize")
            self.assertEqual(result["error"]["type"], "no_sentences")

    def test_error_no_content_terms_for_stop_word_only_text(self) -> None:
        result = self.tool.execute(mode="summarize", text="The and of the.")
        self.assertEqual(result["error"]["type"], "no_content_terms")
        result = self.tool.execute(mode="keywords", text="The and of the.")
        self.assertEqual(result["error"]["type"], "no_content_terms")

    def test_error_no_content_terms_chinese(self) -> None:
        result = self.tool.execute(mode="keywords", text="的和了。", language="zh")
        self.assertEqual(result["error"]["type"], "no_content_terms")

    # ------------------------------------------------------------------ #
    # Input validation error matrix (ValueError before computation)
    # ------------------------------------------------------------------ #

    def _assert_invalid(self, regex: str, **kwargs) -> None:
        with self.assertRaisesRegex(ValueError, regex):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self._assert_invalid("mode must be one of", mode="summariz", text="Hello world.")
        self._assert_invalid("mode must be one of", mode=None, text="Hello world.")

    def test_invalid_text(self) -> None:
        self._assert_invalid("text must be a non-empty string", mode="summarize")
        self._assert_invalid("text must be a non-empty string", mode="summarize", text="")
        self._assert_invalid("text must contain non-whitespace", mode="summarize", text="   \n\t ")
        self._assert_invalid("text must be a non-empty string", mode="summarize", text=123)
        self._assert_invalid("text must be a non-empty string", mode="keywords", text=True)

    def test_invalid_text_too_long(self) -> None:
        self._assert_invalid(
            "exceeds the 100,000-character limit",
            mode="summarize",
            text="word. " * 40_000,
        )

    def test_max_text_chars_is_honored_when_configured(self) -> None:
        # The documented max_text_chars field must actually gate the
        # input length when instantiated with a non-default bound.
        capped = TextSummarizerTool(max_text_chars=50)
        self.assertEqual(capped.max_text_chars, 50)
        long_text = "word. " * 12  # 72 characters
        self.assertGreater(len(long_text), 50)
        with self.assertRaisesRegex(ValueError, "exceeds the 50-character limit"):
            capped.execute(mode="summarize", text=long_text)
        # Text within the configured bound is accepted.
        ok = capped.execute(mode="summarize", text="word. " * 8)
        self.assertEqual(ok["sentence_count"], 8)

    def test_invalid_max_sentences(self) -> None:
        for bad in (0, -1, 101, 2.5, "3", True, [3]):
            self._assert_invalid(
                "max_sentences must be an integer between 1 and 100",
                mode="summarize",
                text="Hello world.",
                max_sentences=bad,
            )

    def test_invalid_ratio(self) -> None:
        for bad in (0.05, 0.6, 0.0, 1.0, "0.3", True):
            self._assert_invalid(
                "ratio must be a number between 0.1 and 0.5",
                mode="summarize",
                text="Hello world.",
                ratio=bad,
            )

    def test_invalid_language(self) -> None:
        for bad in ("fr", 123, True):
            self._assert_invalid(
                "language must be one of",
                mode="summarize",
                text="Hello world.",
                language=bad,
            )

    def test_invalid_top_k(self) -> None:
        for bad in (0, 51, 2.5, "5", True):
            self._assert_invalid(
                "top_k must be an integer between 1 and 50",
                mode="keywords",
                text="Hello world.",
                top_k=bad,
            )

    # ------------------------------------------------------------------ #
    # Determinism and exports
    # ------------------------------------------------------------------ #

    def test_determinism_same_input_same_output(self) -> None:
        first = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.5)
        second = self.tool.execute(mode="summarize", text=EN_TEXT, ratio=0.5)
        self.assertEqual(first, second)
        third = self.tool.execute(mode="keywords", text=ZH_TEXT, language="zh")
        fourth = self.tool.execute(mode="keywords", text=ZH_TEXT, language="zh")
        self.assertEqual(third, fourth)

    def test_package_export_matches_direct_class(self) -> None:
        self.assertIs(TextSummarizerTool, DirectTextSummarizerTool)

    def test_tool_metadata(self) -> None:
        self.assertEqual(self.tool.name, "text_summarizer_tool")
        self.assertIn("extractive", self.tool.description)
        self.assertIn("no LLM", self.tool.description)


if __name__ == "__main__":
    unittest.main()
