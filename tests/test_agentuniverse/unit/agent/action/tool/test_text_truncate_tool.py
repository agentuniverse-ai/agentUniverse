#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_truncate_tool.py

"""Offline unit tests for TextTruncateTool.

The tool is built purely on the standard library (re, typing, pydantic
models already used by the Tool base) and never touches the network,
so this suite runs fully offline. Every assertion is deterministic:
each mode is checked against hand-computed ground truths — exact
result strings, exact result lengths, exact payload dictionaries —
including word-boundary snap-back cases (cut at a word edge, cut
mid-word, cut inside a long word with no nearby boundary), CJK
sentences and CJK word counting, abbreviation-aware sentence counts,
ellipsis variants (en/cjk, counted and not counted), min_length
behaviors (refusal returning the original vs structured error),
already-short inputs returned unchanged byte-identically, and the
full input-validation error matrix.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TextTruncateTool
from agentuniverse.agent.action.tool.common_tool.text_truncate_tool import (
    TextTruncateTool as DirectTextTruncateTool,
)

UNICODE_TEXT = "héllo 世界 🌍\ttabs kept"
CJK_SENTENCES = "今天天气很好。我们去了公园！真的吗？是的。"
ABBREV_TEXT = (
    "Dr. Wong and Mr. Lee met J. R. R. Tolkien in Washington. "
    "They talked about 3.14 and e.g. numbers. Fun!"
)


class TextTruncateToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextTruncateTool."""

    def setUp(self) -> None:
        self.tool = TextTruncateTool()

    # ------------------------------------------------------------------ #
    # chars mode
    # ------------------------------------------------------------------ #

    def test_chars_hard_cap_exact_result(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="chars", text="hello world", max=5),
            {
                "mode": "chars",
                "max": 5,
                "ellipsis": None,
                "word_boundary": False,
                "truncated": True,
                "original_length": 11,
                "result_length": 5,
                "result": "hello",
            },
        )

    def test_chars_hard_cap_cut_is_byte_exact_prefix(self) -> None:
        result = self.tool.execute(mode="chars", text="ab\tcd\nef", max=4)
        self.assertEqual(result["result"], "ab\tc")
        self.assertEqual(result["result_length"], 4)

    def test_chars_already_short_returned_byte_identical(self) -> None:
        result = self.tool.execute(mode="chars", text=UNICODE_TEXT, max=500)
        self.assertFalse(result["truncated"])
        self.assertIs(result["result"], UNICODE_TEXT)
        self.assertEqual(result["result_length"], len(UNICODE_TEXT))
        self.assertEqual(result["original_length"], len(UNICODE_TEXT))
        self.assertEqual(result["ellipsis"], None)

    def test_chars_counts_code_points_cjk_and_emoji(self) -> None:
        # Six code points exactly: three ideographs, one emoji, two
        # combining-free latin letters.
        result = self.tool.execute(mode="chars", text="世界🌍ab", max=4)
        self.assertEqual(result["result"], "世界🌍a")
        self.assertEqual(result["result_length"], 4)

    def test_chars_word_boundary_snap_back_mid_word(self) -> None:
        # Budget 9 lands inside 'three'; the cut snaps back to the
        # whitespace before 'three' and lands after the whole word
        # 'two' with trailing whitespace stripped.
        result = self.tool.execute(
            mode="chars", text="one two three", max=9, word_boundary=True
        )
        self.assertEqual(result["result"], "one two")
        self.assertEqual(result["result_length"], 7)
        self.assertTrue(result["truncated"])

    def test_chars_word_boundary_already_on_word_edge(self) -> None:
        # Budget 7 cuts right after 'two' (next char is a space): the
        # result still ends after the whole word.
        result = self.tool.execute(
            mode="chars", text="one two three", max=7, word_boundary=True
        )
        self.assertEqual(result["result"], "one two")
        # Budget 3 ends exactly at 'one' followed by a space.
        result = self.tool.execute(
            mode="chars", text="one two three", max=3, word_boundary=True
        )
        self.assertEqual(result["result"], "one")

    def test_chars_word_boundary_cut_inside_long_word(self) -> None:
        # The budget lands inside a very long word; snapping back to
        # the previous boundary leaves only 'abc'.
        result = self.tool.execute(
            mode="chars",
            text="abc supercalifragilistic one",
            max=7,
            word_boundary=True,
        )
        self.assertEqual(result["result"], "abc")
        self.assertEqual(result["result_length"], 3)

    def test_chars_word_boundary_no_whitespace_keeps_hard_cut(self) -> None:
        # A CJK run has no whitespace to snap back to: the hard cut
        # is kept (documented CJK behavior for the chars mode).
        result = self.tool.execute(
            mode="chars", text="人工智能很好", max=4, word_boundary=True
        )
        self.assertEqual(result["result"], "人工智能")
        self.assertEqual(result["result_length"], 4)
        # Same for a single long latin 'word' like a URL.
        result = self.tool.execute(
            mode="chars",
            text="https://example.com/very/long/path",
            max=10,
            word_boundary=True,
        )
        self.assertEqual(result["result"], "https://ex")

    def test_chars_word_boundary_snap_never_empties_result(self) -> None:
        # The only whitespace sits at index 0: snapping there would
        # produce an empty string, so the hard cut is kept instead.
        result = self.tool.execute(
            mode="chars", text=" longword", max=4, word_boundary=True
        )
        self.assertEqual(result["result"], " lon")

    def test_chars_exact_boundary_no_truncation(self) -> None:
        # len(text) == max: returned unchanged even with the
        # word_boundary option switched on.
        result = self.tool.execute(
            mode="chars", text="hello", max=5, word_boundary=True
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "hello")

    # ------------------------------------------------------------------ #
    # words mode
    # ------------------------------------------------------------------ #

    def test_words_normalize_rejoins_with_single_spaces(self) -> None:
        result = self.tool.execute(
            mode="words", text="The quick   brown\tfox", max=3
        )
        self.assertEqual(
            result,
            {
                "mode": "words",
                "max": 3,
                "ellipsis": None,
                "whitespace": "normalize",
                "words_total": 4,
                "words_kept": 3,
                "truncated": True,
                "original_length": 21,
                "result_length": 15,
                "result": "The quick brown",
            },
        )

    def test_words_preserve_keeps_original_spacing(self) -> None:
        result = self.tool.execute(
            mode="words", text="The quick   brown\tfox", max=3,
            whitespace="preserve",
        )
        self.assertEqual(result["result"], "The quick   brown")
        self.assertEqual(result["whitespace"], "preserve")

    def test_words_already_few_words_unchanged(self) -> None:
        result = self.tool.execute(mode="words", text="one two", max=5)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "one two")
        self.assertEqual(result["words_total"], 2)
        self.assertEqual(result["words_kept"], 2)

    def test_words_cjk_characters_count_one_word_each(self) -> None:
        # 'hello' + 4 ideographs + 'world' = 6 words; keeping 4 words
        # keeps 'hello' and the first three ideographs, re-joined
        # without inserting spaces between CJK characters.
        result = self.tool.execute(
            mode="words", text="hello 世界你好 world", max=4
        )
        self.assertEqual(result["words_total"], 6)
        self.assertEqual(result["words_kept"], 4)
        self.assertEqual(result["result"], "hello 世界你")

    def test_words_pure_cjk_falls_back_to_character_budget(self) -> None:
        # Pure-CJK input: max words == max characters, and no spaces
        # are inserted between the ideographs.
        result = self.tool.execute(
            mode="words", text="人工智能很好", max=4
        )
        self.assertEqual(result["words_total"], 6)
        self.assertEqual(result["result"], "人工智能")
        result = self.tool.execute(
            mode="words", text="人工智能很好", max=6
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "人工智能很好")

    def test_words_preserve_cjk_cut_offset(self) -> None:
        result = self.tool.execute(
            mode="words", text="人工智能很好", max=2, whitespace="preserve"
        )
        self.assertEqual(result["result"], "人工")

    def test_words_ellipsis_appended_after_kept_words(self) -> None:
        result = self.tool.execute(
            mode="words", text="one two three four", max=2, add_ellipsis=True
        )
        self.assertEqual(result["result"], "one two...")
        self.assertEqual(result["result_length"], 10)

    # ------------------------------------------------------------------ #
    # sentences mode
    # ------------------------------------------------------------------ #

    def test_sentences_basic_first_n(self) -> None:
        result = self.tool.execute(
            mode="sentences", text="One. Two. Three.", max=2
        )
        self.assertEqual(
            result,
            {
                "mode": "sentences",
                "max": 2,
                "ellipsis": None,
                "sentences_total": 3,
                "sentences_kept": 2,
                "truncated": True,
                "original_length": 16,
                "result_length": 9,
                "result": "One. Two.",
            },
        )

    def test_sentences_result_is_byte_exact_prefix(self) -> None:
        result = self.tool.execute(
            mode="sentences", text="One.  Two.\nThree.", max=2
        )
        # Original inter-sentence spacing between kept sentences is
        # preserved; the cut lands right after the 2nd terminator.
        self.assertEqual(result["result"], "One.  Two.")
        self.assertEqual(result["result_length"], 10)

    def test_sentences_abbreviation_guard(self) -> None:
        # Dr., Mr., the initials J. R. R., the decimal 3.14 and e.g.
        # never end a sentence: three sentences in total.
        result = self.tool.execute(mode="sentences", text=ABBREV_TEXT, max=9)
        self.assertEqual(result["sentences_total"], 3)
        self.assertFalse(result["truncated"])
        result = self.tool.execute(mode="sentences", text=ABBREV_TEXT, max=2)
        self.assertEqual(result["sentences_kept"], 2)
        self.assertEqual(
            result["result"],
            "Dr. Wong and Mr. Lee met J. R. R. Tolkien in Washington. "
            "They talked about 3.14 and e.g. numbers.",
        )

    def test_sentences_abbreviation_examples(self) -> None:
        for guarded, expected_total in [
            ("Mr. Smith went to Washington. He did nothing.", 2),
            ("Use tools, e.g. hammers. They work.", 2),
            ("J. Smith arrived. It was late.", 2),
            ("Pi is 3.14 exactly. Yes.", 2),
            ("See Fig. 3 and eq. 7. Then leave.", 2),
        ]:
            result = self.tool.execute(
                mode="sentences", text=guarded, max=10
            )
            self.assertEqual(result["sentences_total"], expected_total)

    def test_sentences_conservative_merge_documented(self) -> None:
        # A sentence that genuinely ends with the guarded word 'no.'
        # is conservatively merged into the next one.
        result = self.tool.execute(
            mode="sentences", text="The answer is no. Start over.", max=5
        )
        self.assertEqual(result["sentences_total"], 1)
        self.assertFalse(result["truncated"])

    def test_sentences_cjk_terminators(self) -> None:
        # 。！？ all count, with no inter-sentence whitespace needed.
        result = self.tool.execute(mode="sentences", text=CJK_SENTENCES, max=2)
        self.assertEqual(result["sentences_total"], 4)
        self.assertEqual(result["sentences_kept"], 2)
        self.assertEqual(result["result"], "今天天气很好。我们去了公园！")
        result = self.tool.execute(mode="sentences", text=CJK_SENTENCES, max=4)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], CJK_SENTENCES)

    def test_sentences_unterminated_tail_counts_as_sentence(self) -> None:
        result = self.tool.execute(
            mode="sentences", text="One. Two", max=1
        )
        self.assertEqual(result["sentences_total"], 2)
        self.assertEqual(result["result"], "One.")

    def test_sentences_no_terminator_single_sentence(self) -> None:
        result = self.tool.execute(
            mode="sentences", text="just some words here", max=1
        )
        self.assertEqual(result["sentences_total"], 1)
        self.assertFalse(result["truncated"])

    def test_sentences_closing_quote_stays_attached(self) -> None:
        result = self.tool.execute(
            mode="sentences",
            text='He said "stop." Then left! Really? Yes.',
            max=2,
        )
        self.assertEqual(result["sentences_total"], 4)
        self.assertEqual(result["result"], 'He said "stop." Then left!')

    def test_sentences_bang_without_space_ends_sentence(self) -> None:
        result = self.tool.execute(mode="sentences", text="One!Two!Three.", max=2)
        self.assertEqual(result["sentences_total"], 3)
        self.assertEqual(result["result"], "One!Two!")

    # ------------------------------------------------------------------ #
    # head_chars_keep_sentences mode
    # ------------------------------------------------------------------ #

    HEAD_TEXT = "First sentence here. Second one follows. Third sentence now."

    def test_head_chars_boundary_exactly_at_budget(self) -> None:
        # 'First sentence here.' ends exactly at character 20.
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=20
        )
        self.assertEqual(
            result,
            {
                "mode": "head_chars_keep_sentences",
                "max": 20,
                "ellipsis": None,
                "tolerance": 10,
                "boundary": "sentence",
                "truncated": True,
                "original_length": 60,
                "result_length": 20,
                "result": "First sentence here.",
            },
        )

    def test_head_chars_shrinks_back_to_boundary(self) -> None:
        # Budget 15 shrinks back to the boundary at 20 (|20-15|=5
        # within the default tolerance 10).
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=15
        )
        self.assertEqual(result["boundary"], "sentence")
        self.assertEqual(result["result"], "First sentence here.")

    def test_head_chars_extends_forward_to_boundary(self) -> None:
        # Budget 25 extends to 20 rather than 40 (nearest wins).
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=25
        )
        self.assertEqual(result["result"], "First sentence here.")
        # Budget 38 reaches forward to the boundary at 40.
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=38
        )
        self.assertEqual(result["boundary"], "sentence")
        self.assertEqual(
            result["result"], "First sentence here. Second one follows."
        )
        self.assertEqual(result["result_length"], 40)

    def test_head_chars_char_fallback_when_outside_tolerance(self) -> None:
        # With tolerance 0 only an exact boundary qualifies.
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT,
            max=22, tolerance=0,
        )
        self.assertEqual(result["boundary"], "char_fallback")
        self.assertEqual(result["result"], "First sentence here. S")
        self.assertEqual(result["result_length"], 22)

    def test_head_chars_explicit_tolerance_widens_snap(self) -> None:
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT,
            max=22, tolerance=20,
        )
        # Boundaries at 20 and 40: |20-22|=2 beats |40-22|=18.
        self.assertEqual(result["boundary"], "sentence")
        self.assertEqual(result["result"], "First sentence here.")

    def test_head_chars_cjk_boundary_selection(self) -> None:
        # Boundaries at 7, 14 and 18; the nearest to the budget 8 is
        # the one at 7.
        result = self.tool.execute(
            mode="head_chars_keep_sentences",
            text="今天天气很好。我们去了公园！真的吗？",
            max=8,
        )
        self.assertEqual(result["boundary"], "sentence")
        self.assertEqual(result["result"], "今天天气很好。")

    def test_head_chars_already_short_unchanged(self) -> None:
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text="Short text.", max=50
        )
        self.assertEqual(result["boundary"], "none")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "Short text.")

    # ------------------------------------------------------------------ #
    # ellipsis behavior (shared)
    # ------------------------------------------------------------------ #

    def test_ellipsis_en_default_not_counted(self) -> None:
        result = self.tool.execute(
            mode="chars", text="hello world", max=5, add_ellipsis=True
        )
        self.assertEqual(result["ellipsis"], "...")
        self.assertEqual(result["result"], "hello...")
        # Not counted: the result exceeds max by the ellipsis length.
        self.assertEqual(result["result_length"], 8)

    def test_ellipsis_cjk_style_not_counted(self) -> None:
        result = self.tool.execute(
            mode="chars", text="人工智能很好", max=4,
            add_ellipsis=True, language="cjk",
        )
        self.assertEqual(result["ellipsis"], "…")
        self.assertEqual(result["result"], "人工智能…")
        self.assertEqual(result["result_length"], 5)

    def test_ellipsis_counted_shrinks_text_budget(self) -> None:
        result = self.tool.execute(
            mode="chars", text="hello world", max=8,
            add_ellipsis=True, count_ellipsis=True,
        )
        self.assertEqual(result["result"], "hello...")
        # Counted: the result never exceeds max.
        self.assertEqual(result["result_length"], 8)

    def test_ellipsis_counted_cjk_never_exceeds_max(self) -> None:
        result = self.tool.execute(
            mode="chars", text="人工智能很好啊", max=5,
            add_ellipsis=True, count_ellipsis=True, language="cjk",
        )
        self.assertEqual(result["result"], "人工智能…")
        self.assertEqual(result["result_length"], 5)

    def test_ellipsis_never_added_when_nothing_truncated(self) -> None:
        result = self.tool.execute(
            mode="chars", text="hi", max=10, add_ellipsis=True
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "hi")
        self.assertEqual(result["ellipsis"], None)

    def test_ellipsis_after_word_boundary_snap(self) -> None:
        result = self.tool.execute(
            mode="chars", text="one two three", max=9,
            word_boundary=True, add_ellipsis=True,
        )
        self.assertEqual(result["result"], "one two...")

    def test_ellipsis_after_sentence_cut(self) -> None:
        result = self.tool.execute(
            mode="sentences", text="One. Two.", max=1, add_ellipsis=True,
            language="cjk",
        )
        self.assertEqual(result["result"], "One.…")

    def test_ellipsis_counted_with_head_chars(self) -> None:
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT,
            max=20, add_ellipsis=True, count_ellipsis=True,
        )
        # Text budget 17: no boundary within tolerance of 17 (the
        # boundary at 20 is |20-17|=3 <= 10, so it snaps to 20).
        self.assertEqual(result["boundary"], "sentence")
        self.assertEqual(result["result"], "First sentence here....")
        self.assertEqual(result["result_length"], 23)

    # ------------------------------------------------------------------ #
    # min_length behavior (shared)
    # ------------------------------------------------------------------ #

    def test_min_length_passes_when_cut_is_long_enough(self) -> None:
        result = self.tool.execute(
            mode="chars", text="one two three", max=9,
            word_boundary=True, min_length=5,
        )
        self.assertEqual(result["result"], "one two")

    def test_min_length_refusal_returns_original_when_close(self) -> None:
        # The snap-back would leave 'aa' (2 chars < min_length 4),
        # but the original (9 chars) fits within 1.5x the budget
        # (6 -> 9): the original is returned unchanged.
        result = self.tool.execute(
            mode="chars", text="aa bbbb c", max=6,
            word_boundary=True, min_length=4,
        )
        self.assertEqual(
            result,
            {
                "mode": "chars",
                "max": 6,
                "ellipsis": None,
                "word_boundary": True,
                "refusal": "min_length",
                "truncated": False,
                "original_length": 9,
                "result_length": 9,
                "result": "aa bbbb c",
            },
        )

    def test_min_length_refusal_structured_error_when_far(self) -> None:
        # Same refusal, but the original (17 chars) is far beyond
        # 1.5x the budget: a structured error payload is returned.
        result = self.tool.execute(
            mode="chars", text="aa bbbbbbbbbb ccc", max=6,
            word_boundary=True, min_length=4,
        )
        self.assertEqual(result["mode"], "chars")
        self.assertEqual(result["max"], 6)
        self.assertEqual(result["error"]["type"], "min_length_violation")
        self.assertIn("min_length=4", result["error"]["message"])
        self.assertNotIn("result", result)

    def test_min_length_words_mode_measured_in_words(self) -> None:
        # Truncating to 1 word leaves 2 characters < min_length 3.
        # The original has 4 words > 1.5x1, so a structured error.
        result = self.tool.execute(
            mode="words", text="a b c d", max=1, min_length=3
        )
        self.assertEqual(result["error"]["type"], "min_length_violation")
        # One long word + a tiny word: 2 words total <= 1.5*1? No,
        # 2 > 1.5, so also an error; use 1 word to check the
        # return-original branch.
        result = self.tool.execute(
            mode="words", text="abcdef", max=1, min_length=3
        )
        # Single word of 6 chars: no cut needed at all.
        self.assertEqual(result["result"], "abcdef")
        self.assertFalse(result["truncated"])
        # Two words where the first alone satisfies min_length.
        result = self.tool.execute(
            mode="words", text="abcd efgh", max=1, min_length=3
        )
        self.assertEqual(result["result"], "abcd")
        self.assertTrue(result["truncated"])

    def test_min_length_words_mode_return_original_branch(self) -> None:
        # Cutting to 2 words leaves 'ab cd' (5 chars) < min_length 6,
        # but the original has 3 words which fits within 1.5x the
        # budget (2 -> 3): the original is returned unchanged.
        result = self.tool.execute(
            mode="words", text="ab cd ef", max=2, min_length=6
        )
        self.assertEqual(result["refusal"], "min_length")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "ab cd ef")

    def test_min_length_applies_via_counted_ellipsis_shrink(self) -> None:
        # The counted ellipsis shrinks the text budget to 4; snapping
        # back to the word boundary leaves 'aaaa' (4 chars) which is
        # below min_length 5, and the original (19 chars) exceeds
        # 1.5x4: structured error.
        result = self.tool.execute(
            mode="chars", text="aaaa bbbb cccc dddd", max=7,
            add_ellipsis=True, count_ellipsis=True,
            word_boundary=True, min_length=5,
        )
        self.assertEqual(result["error"]["type"], "min_length_violation")

    def test_min_length_hard_cut_can_also_violate(self) -> None:
        # min_length above the ellipsis-shrunk budget: even the hard
        # cut violates it. Original 10 chars > 1.5*2: error.
        result = self.tool.execute(
            mode="chars", text="abcdefghij", max=5,
            add_ellipsis=True, count_ellipsis=True, min_length=4,
        )
        self.assertEqual(result["error"]["type"], "min_length_violation")

    def test_min_length_no_guard_when_unset(self) -> None:
        result = self.tool.execute(
            mode="chars", text="abc supercalifragilistic", max=7,
            word_boundary=True,
        )
        self.assertEqual(result["result"], "abc")
        self.assertNotIn("error", result)
        self.assertNotIn("refusal", result)

    # ------------------------------------------------------------------ #
    # input validation error matrix
    # ------------------------------------------------------------------ #

    def _assert_invalid(self, message_fragment: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn(message_fragment, str(ctx.exception))

    def test_validation_matrix(self) -> None:
        """Every malformed parameter raises before any computation."""
        # mode
        self._assert_invalid(
            "mode must be one of", mode="bogus", text="x", max=1
        )
        # text
        self._assert_invalid(
            "text must be a non-empty string", mode="chars", max=1
        )
        self._assert_invalid(
            "text must be a non-empty string (got '')",
            mode="chars", text="", max=1,
        )
        self._assert_invalid(
            "text must be a non-empty string (got True)",
            mode="chars", text=True, max=1,
        )
        self._assert_invalid(
            "text must be a non-empty string (got 123)",
            mode="chars", text=123, max=1,
        )
        self._assert_invalid(
            "text exceeds the 100,000-character limit",
            mode="chars", text="x" * 100_001, max=1,
        )
        # max
        self._assert_invalid(
            "max is required", mode="chars", text="x"
        )
        self._assert_invalid(
            "max must be an integer >= 1 (got True)",
            mode="chars", text="x", max=True,
        )
        self._assert_invalid(
            "max must be an integer >= 1 (got 0)",
            mode="chars", text="x", max=0,
        )
        self._assert_invalid(
            "max must be an integer >= 1 (got -3)",
            mode="chars", text="x", max=-3,
        )
        self._assert_invalid(
            "max must be an integer >= 1 (got '5')",
            mode="chars", text="x", max="5",
        )
        self._assert_invalid(
            "max must be an integer >= 1 (got 1.5)",
            mode="chars", text="x", max=1.5,
        )
        self._assert_invalid(
            "max exceeds the 1,000,000 limit",
            mode="chars", text="x", max=1_000_001,
        )
        # add_ellipsis / language / count_ellipsis
        self._assert_invalid(
            "add_ellipsis must be a boolean (got 1)",
            mode="chars", text="x", max=5, add_ellipsis=1,
        )
        self._assert_invalid(
            "language must be one of: en, cjk (got 'fr')",
            mode="chars", text="x", max=5, language="fr",
        )
        self._assert_invalid(
            "language must be one of: en, cjk (got True)",
            mode="chars", text="x", max=5, language=True,
        )
        self._assert_invalid(
            "count_ellipsis=True requires add_ellipsis=True",
            mode="chars", text="x", max=5, count_ellipsis=True,
        )
        # min_length
        self._assert_invalid(
            "min_length (6) cannot exceed max (5)",
            mode="chars", text="x", max=5, min_length=6,
        )
        self._assert_invalid(
            "min_length must be an integer >= 1 (got True)",
            mode="chars", text="x", max=5, min_length=True,
        )
        self._assert_invalid(
            "min_length must be an integer >= 1 (got 0)",
            mode="chars", text="x", max=5, min_length=0,
        )
        # mode-specific options in the wrong mode / bad types
        self._assert_invalid(
            "word_boundary must be a boolean (got 1)",
            mode="chars", text="x", max=5, word_boundary=1,
        )
        self._assert_invalid(
            "word_boundary is only valid in the 'chars' mode",
            mode="words", text="x y", max=2, word_boundary=True,
        )
        self._assert_invalid(
            "whitespace is only valid in the 'words' mode",
            mode="chars", text="x y", max=2, whitespace="preserve",
        )
        self._assert_invalid(
            "whitespace must be one of: normalize, preserve",
            mode="words", text="x y", max=2, whitespace="tight",
        )
        self._assert_invalid(
            "tolerance is only valid in the "
            "'head_chars_keep_sentences' mode",
            mode="sentences", text="a. b.", max=1, tolerance=5,
        )
        self._assert_invalid(
            "tolerance must be an integer >= 0 (got -1)",
            mode="head_chars_keep_sentences", text="a. b.", max=1,
            tolerance=-1,
        )
        self._assert_invalid(
            "tolerance must be an integer >= 0 (got True)",
            mode="head_chars_keep_sentences", text="a. b.", max=1,
            tolerance=True,
        )
        # budget too small for a counted ellipsis
        self._assert_invalid(
            "is too small to fit the 'en' ellipsis",
            mode="chars", text="x", max=1,
            add_ellipsis=True, count_ellipsis=True,
        )

    def test_validation_happens_before_any_computation(self) -> None:
        # Even a text that would need no truncation at all is
        # rejected when max is malformed.
        self._assert_invalid(
            "max must be an integer >= 1",
            mode="chars", text="ok", max="bad",
        )

    # ------------------------------------------------------------------ #
    # default tolerance value
    # ------------------------------------------------------------------ #

    def test_default_tolerance_is_ten_percent_min_ten(self) -> None:
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=200
        )
        # max(10, 200 // 10) = 20.
        self.assertEqual(result["tolerance"], 20)
        result = self.tool.execute(
            mode="head_chars_keep_sentences", text=self.HEAD_TEXT, max=15
        )
        # max(10, 15 // 10) = 10.
        self.assertEqual(result["tolerance"], 10)

    # ------------------------------------------------------------------ #
    # export sanity
    # ------------------------------------------------------------------ #

    def test_package_export_is_same_class(self) -> None:
        self.assertIs(TextTruncateTool, DirectTextTruncateTool)
        self.assertEqual(self.tool.name, "text_truncate_tool")


if __name__ == "__main__":
    unittest.main()
