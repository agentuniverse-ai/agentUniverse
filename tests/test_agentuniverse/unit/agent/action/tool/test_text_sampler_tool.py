#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_text_sampler_tool.py

"""Offline unit tests for TextSamplerTool.

The tool is built purely on the standard library and never touches
the network, so this suite runs fully offline. Every assertion is
deterministic: each mode is checked against hand-computed ground
truths (literal expected samples, spans, offsets, omission counts and
ratios derived by hand from fixed input strings), the evenly-spaced
offset formula is verified including the k=1 / k=2 edges and the
L-longer-than-text passthrough, the strategic middle window is
verified against the midpoint formula, and the outline mode is
verified against manually counted sentence spans including the
abbreviation / initial / decimal guards. Span invariants (samples are
byte-exact slices of the original at their reported offsets) and a
full strict-validation error matrix round out the suite.
"""

import unittest

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.common_tool import TextSamplerTool
from agentuniverse.agent.action.tool.common_tool.text_sampler_tool import (
    TextSamplerTool as DirectTextSamplerTool,
)

# 26 characters, positions 0..25: a=0 ... z=25.
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
DIGITS10 = "0123456789"
# Ten 4-6 char sentences; spans hand-counted below.
TEN_SENTENCES = "One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten."
TEN_SPANS = [
    [0, 4],    # "One."
    [5, 9],    # "Two."
    [10, 16],  # "Three."
    [17, 22],  # "Four."
    [23, 28],  # "Five."
    [29, 33],  # "Six."
    [34, 40],  # "Seven."
    [41, 47],  # "Eight."
    [48, 53],  # "Nine."
    [54, 58],  # "Ten."
]
ABBREV_TEXT = "Mr. Smith arrived. Dr. Jones left."
CJK_TEXT = "你好。再见！"


class TextSamplerToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextSamplerTool."""

    def setUp(self) -> None:
        self.tool = TextSamplerTool()

    # ------------------------------------------------------------------ #
    # head_tail mode
    # ------------------------------------------------------------------ #

    def test_head_tail_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="head_tail", text=ALPHABET, sample_size=5
        )
        self.assertEqual(
            result,
            {
                "mode": "head_tail",
                "sample_size": 5,
                "result": "abcde…[16 chars omitted]…vwxyz",
                "samples": ["abcde", "vwxyz"],
                "spans": [[0, 5], [21, 26]],
                "omitted_chars": 16,
                "truncated": True,
                "total_length": 26,
                "sampled_ratio": 0.3846,  # 10 / 26
            },
        )

    def test_head_tail_exact_fit_no_separator(self) -> None:
        # len == 2N: head and tail are contiguous, nothing omitted.
        result = self.tool.execute(
            mode="head_tail", text="abcdef", sample_size=3
        )
        self.assertEqual(result["result"], "abcdef")
        self.assertEqual(result["omitted_chars"], 0)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["samples"], ["abc", "def"])
        self.assertEqual(result["spans"], [[0, 3], [3, 6]])
        self.assertEqual(result["sampled_ratio"], 1.0)

    def test_head_tail_singular_omission_count(self) -> None:
        # 3 - 2*1 = 1 omitted character: "1 char omitted", not "chars".
        result = self.tool.execute(
            mode="head_tail", text="abc", sample_size=1
        )
        self.assertEqual(result["result"], "a…[1 char omitted]…c")
        self.assertEqual(result["omitted_chars"], 1)
        self.assertEqual(result["sampled_ratio"], 0.6667)  # 2 / 3

    def test_head_tail_short_text_passthrough(self) -> None:
        result = self.tool.execute(
            mode="head_tail", text="abcd", sample_size=3
        )
        self.assertEqual(result["samples"], ["abcd"])
        self.assertEqual(result["spans"], [[0, 4]])
        self.assertEqual(result["note"], (
            "text length 4 is below the requested head + tail size of 6 "
            "characters (2 x 3); the whole text is returned"
        ))
        self.assertEqual(result["sampled_ratio"], 1.0)
        self.assertNotIn("result", result)

    def test_head_tail_cjk_code_point_safe(self) -> None:
        # One CJK ideograph = one character; spans never split one.
        text = "天地玄黃宇宙洪荒"
        result = self.tool.execute(
            mode="head_tail", text=text, sample_size=3
        )
        self.assertEqual(result["samples"], ["天地玄", "宙洪荒"])
        self.assertEqual(result["spans"], [[0, 3], [5, 8]])
        self.assertEqual(result["result"], "天地玄…[2 chars omitted]…宙洪荒")
        self.assertEqual(result["total_length"], 8)
        self.assertEqual(result["sampled_ratio"], 0.75)  # 6 / 8

    def test_head_tail_astral_emoji_code_points(self) -> None:
        # Emoji outside the BMP are single Python code points, so a
        # span boundary can never cut one in half.
        text = "\U0001f600" * 5
        result = self.tool.execute(
            mode="head_tail", text=text, sample_size=2
        )
        self.assertEqual(result["total_length"], 5)
        self.assertEqual(
            result["samples"], ["\U0001f600" * 2, "\U0001f600" * 2]
        )
        self.assertEqual(result["spans"], [[0, 2], [3, 5]])
        self.assertEqual(result["result"], (
            "\U0001f600\U0001f600…[1 char omitted]…"
            "\U0001f600\U0001f600"
        ))
        self.assertEqual(result["sampled_ratio"], 0.8)  # 4 / 5

    # ------------------------------------------------------------------ #
    # evenly_spaced mode
    # ------------------------------------------------------------------ #

    def test_evenly_spaced_ground_truth(self) -> None:
        # offsets: i * (26 - 5) // (4 - 1) = i * 21 // 3 = 0, 7, 14, 21.
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=4,
            sample_length=5,
        )
        self.assertEqual(
            result,
            {
                "mode": "evenly_spaced",
                "sample_count": 4,
                "sample_length": 5,
                "offsets": [0, 7, 14, 21],
                "samples": ["abcde", "hijkl", "opqrs", "vwxyz"],
                "spans": [[0, 5], [7, 12], [14, 19], [21, 26]],
                "samples_returned": 4,
                "total_length": 26,
                "sampled_ratio": 0.7692,  # 20 / 26
            },
        )

    def test_evenly_spaced_k2_edge(self) -> None:
        # k=2: first window starts at 0, second ends at the last char.
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=2,
            sample_length=4,
        )
        self.assertEqual(result["offsets"], [0, 22])
        self.assertEqual(result["samples"], ["abcd", "wxyz"])
        self.assertEqual(result["spans"], [[0, 4], [22, 26]])
        self.assertEqual(result["sampled_ratio"], 0.3077)  # 8 / 26

    def test_evenly_spaced_k1_centered(self) -> None:
        # k=1: the single window is centered, (26 - 6) // 2 = 10.
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=1,
            sample_length=6,
        )
        self.assertEqual(result["offsets"], [10])
        self.assertEqual(result["samples"], ["klmnop"])
        self.assertEqual(result["spans"], [[10, 16]])
        self.assertEqual(result["sampled_ratio"], 0.2308)  # 6 / 26

    def test_evenly_spaced_overlapping_full_coverage(self) -> None:
        # k=3, L=10: offsets i * 16 // 2 = 0, 8, 16 — overlapping
        # windows whose union covers the whole text.
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=3,
            sample_length=10,
        )
        self.assertEqual(result["offsets"], [0, 8, 16])
        self.assertEqual(
            result["samples"],
            ["abcdefghij", "ijklmnopqr", "qrstuvwxyz"],
        )
        self.assertEqual(
            result["spans"], [[0, 10], [8, 18], [16, 26]]
        )
        self.assertEqual(result["sampled_ratio"], 1.0)

    def test_evenly_spaced_duplicate_offsets_merged(self) -> None:
        # len=10, k=5, L=8: offsets i * 2 // 4 = 0, 0, 1, 1, 2 — the
        # two duplicates merge and a note explains the drop.
        result = self.tool.execute(
            mode="evenly_spaced",
            text=DIGITS10,
            sample_count=5,
            sample_length=8,
        )
        self.assertEqual(result["offsets"], [0, 1, 2])
        self.assertEqual(
            result["samples"], ["01234567", "12345678", "23456789"]
        )
        self.assertEqual(result["samples_returned"], 3)
        self.assertEqual(result["spans"], [[0, 8], [1, 9], [2, 10]])
        self.assertIn("2 of the 5 requested samples", result["note"])
        self.assertIn("merged", result["note"])

    def test_evenly_spaced_length_equals_text(self) -> None:
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=2,
            sample_length=26,
        )
        self.assertEqual(result["samples"], [ALPHABET])
        self.assertEqual(result["spans"], [[0, 26]])
        self.assertEqual(result["sampled_ratio"], 1.0)
        self.assertIn("whole text is returned", result["note"])

    def test_evenly_spaced_length_exceeds_text(self) -> None:
        result = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=3,
            sample_length=30,
        )
        self.assertEqual(result["samples"], [ALPHABET])
        self.assertEqual(result["spans"], [[0, 26]])
        self.assertEqual(result["total_length"], 26)
        self.assertEqual(result["sampled_ratio"], 1.0)
        self.assertEqual(
            result["note"], (
                "sample_length 30 is >= the text length 26; the whole "
                "text is returned as one sample"
            ),
        )

    # ------------------------------------------------------------------ #
    # strategic mode
    # ------------------------------------------------------------------ #

    def test_strategic_ground_truth(self) -> None:
        # middle start = (26 - 4) // 2 = 11, centered on len / 2 = 13.
        result = self.tool.execute(
            mode="strategic", text=ALPHABET, sample_size=4
        )
        self.assertEqual(
            result,
            {
                "mode": "strategic",
                "sample_size": 4,
                "sections": ["head", "middle", "tail"],
                "samples": ["abcd", "lmno", "wxyz"],
                "spans": [[0, 4], [11, 15], [22, 26]],
                "total_length": 26,
                "sampled_ratio": 0.4615,  # 12 / 26
            },
        )

    def test_strategic_windows_cover_whole_text(self) -> None:
        # N=13: head [0,13), middle [6,19), tail [13,26) — the union
        # is the entire text even though each window is only half of it.
        result = self.tool.execute(
            mode="strategic", text=ALPHABET, sample_size=13
        )
        self.assertEqual(
            result["samples"],
            ["abcdefghijklm", "ghijklmnopqrs", "nopqrstuvwxyz"],
        )
        self.assertEqual(
            result["spans"], [[0, 13], [6, 19], [13, 26]]
        )
        self.assertEqual(result["sampled_ratio"], 1.0)

    def test_strategic_duplicate_middle_dropped(self) -> None:
        # len=5, N=4: middle start = (5 - 4) // 2 = 0, identical to the
        # head, so only head and tail remain.
        result = self.tool.execute(
            mode="strategic", text="abcde", sample_size=4
        )
        self.assertEqual(result["sections"], ["head", "tail"])
        self.assertEqual(result["samples"], ["abcd", "bcde"])
        self.assertEqual(result["spans"], [[0, 4], [1, 5]])
        self.assertEqual(result["sampled_ratio"], 1.0)

    def test_strategic_short_text_passthrough(self) -> None:
        result = self.tool.execute(
            mode="strategic", text="abc", sample_size=5
        )
        self.assertEqual(result["samples"], ["abc"])
        self.assertEqual(result["spans"], [[0, 3]])
        self.assertEqual(result["sampled_ratio"], 1.0)
        self.assertEqual(
            result["note"], (
                "sample_size 5 is >= the text length 3; the whole text "
                "is returned as one sample"
            ),
        )

    # ------------------------------------------------------------------ #
    # outline_sample mode
    # ------------------------------------------------------------------ #

    def test_outline_ground_truth(self) -> None:
        # every_n=3, k=4: keep sentence 0, then 3 and 6 (two of the
        # k-1=3 slots before the reserved last one), then sentence 9.
        result = self.tool.execute(
            mode="outline_sample",
            text=TEN_SENTENCES,
            sample_count=4,
            every_n=3,
        )
        self.assertEqual(
            result,
            {
                "mode": "outline_sample",
                "every_n": 3,
                "max_sentences": 4,
                "sentence_count": 10,
                "selected_indices": [0, 3, 6, 9],
                "samples": ["One.", "Four.", "Seven.", "Ten."],
                "spans": [[0, 4], [17, 22], [34, 40], [54, 58]],
                "total_length": 58,
                "sampled_ratio": 0.3276,  # (4+5+6+4) / 58
            },
        )

    def test_outline_keeps_last_sentence(self) -> None:
        # k=3, every_n=1: one every-stride slot (sentence 1), then the
        # reserved last-sentence slot (sentence 9).
        result = self.tool.execute(
            mode="outline_sample",
            text=TEN_SENTENCES,
            sample_count=3,
            every_n=1,
        )
        self.assertEqual(result["selected_indices"], [0, 1, 9])
        self.assertEqual(result["samples"], ["One.", "Two.", "Ten."])
        self.assertEqual(
            result["spans"], [[0, 4], [5, 9], [54, 58]]
        )
        self.assertEqual(result["sampled_ratio"], 0.2069)  # 12 / 58

    def test_outline_stride_beyond_end(self) -> None:
        # every_n=100 exceeds the sentence count: first + last only.
        result = self.tool.execute(
            mode="outline_sample",
            text=TEN_SENTENCES,
            sample_count=5,
            every_n=100,
        )
        self.assertEqual(result["selected_indices"], [0, 9])
        self.assertEqual(result["samples"], ["One.", "Ten."])

    def test_outline_k1_first_sentence_only(self) -> None:
        result = self.tool.execute(
            mode="outline_sample",
            text=TEN_SENTENCES,
            sample_count=1,
            every_n=2,
        )
        self.assertEqual(result["selected_indices"], [0])
        self.assertEqual(result["samples"], ["One."])
        self.assertEqual(result["spans"], [[0, 4]])

    def test_outline_k_above_sentence_count_returns_all(self) -> None:
        result = self.tool.execute(
            mode="outline_sample",
            text=TEN_SENTENCES,
            sample_count=20,
            every_n=1,
        )
        self.assertEqual(
            result["selected_indices"], list(range(10))
        )
        self.assertEqual(
            result["spans"],
            [[0, 4], [5, 9], [10, 16], [17, 22], [23, 28], [29, 33],
             [34, 40], [41, 47], [48, 53], [54, 58]],
        )
        self.assertEqual(result["sampled_ratio"], 0.8448)  # 49 / 58

    def test_outline_sentence_spans_partition_check(self) -> None:
        # The segmentation itself: ten sentences at the hand-counted
        # spans, byte-exact slices of the original.
        spans = DirectTextSamplerTool._split_sentences(TEN_SENTENCES)
        self.assertEqual([list(s) for s in spans], TEN_SPANS)
        for (start, end), expected in zip(spans, [
            "One.", "Two.", "Three.", "Four.", "Five.",
            "Six.", "Seven.", "Eight.", "Nine.", "Ten.",
        ]):
            self.assertEqual(TEN_SENTENCES[start:end], expected)

    def test_outline_abbreviation_guard(self) -> None:
        # "Mr." and "Dr." must not split their sentences.
        result = self.tool.execute(
            mode="outline_sample",
            text=ABBREV_TEXT,
            sample_count=5,
            every_n=1,
        )
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(
            result["samples"], ["Mr. Smith arrived.", "Dr. Jones left."]
        )
        self.assertEqual(result["selected_indices"], [0, 1])
        self.assertEqual(result["spans"], [[0, 18], [19, 34]])
        self.assertEqual(result["total_length"], 34)
        self.assertEqual(result["sampled_ratio"], 0.9706)  # 33 / 34

    def test_outline_dotted_abbreviation_interior_dots(self) -> None:
        # Both dots of "e.g." are guarded; the sentence continues.
        text = "Use fruits, e.g. apples and pears. They are healthy."
        result = self.tool.execute(
            mode="outline_sample", text=text, sample_count=5, every_n=1
        )
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(
            result["samples"],
            ["Use fruits, e.g. apples and pears.", "They are healthy."],
        )

    def test_outline_uppercase_initial_guard(self) -> None:
        # "J. R. R." are single uppercase initials, not boundaries.
        text = "J. R. R. Tolkien wrote books."
        result = self.tool.execute(
            mode="outline_sample", text=text, sample_count=5, every_n=1
        )
        self.assertEqual(result["sentence_count"], 1)
        self.assertEqual(result["samples"], [text])
        self.assertIn("only 1 sentence detected", result["note"])

    def test_outline_decimal_guard(self) -> None:
        # "3.14" and "2.71" never end a sentence (no whitespace after
        # the '.'), so the text is a single sentence.
        text = "Pi is 3.14 and e is 2.71 today."
        result = self.tool.execute(
            mode="outline_sample", text=text, sample_count=5, every_n=1
        )
        self.assertEqual(result["sentence_count"], 1)
        self.assertEqual(result["samples"], [text])

    def test_outline_closers_absorbed(self) -> None:
        # The closing quote after "Stop!" belongs to the sentence.
        text = 'He said "Stop!" Then left.'
        result = self.tool.execute(
            mode="outline_sample", text=text, sample_count=5, every_n=1
        )
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(
            result["samples"], ['He said "Stop!"', "Then left."]
        )
        self.assertEqual(result["spans"], [[0, 15], [16, 26]])

    def test_outline_cjk_no_inter_sentence_whitespace(self) -> None:
        # CJK terminators end a sentence regardless of the following
        # character; spans stay code-point aligned.
        result = self.tool.execute(
            mode="outline_sample",
            text=CJK_TEXT,
            sample_count=2,
            every_n=1,
        )
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(result["selected_indices"], [0, 1])
        self.assertEqual(result["samples"], ["你好。", "再见！"])
        self.assertEqual(result["spans"], [[0, 3], [3, 6]])
        self.assertEqual(result["total_length"], 6)
        self.assertEqual(result["sampled_ratio"], 1.0)

    def test_outline_single_sentence_passthrough(self) -> None:
        text = "no terminators at all"
        result = self.tool.execute(
            mode="outline_sample", text=text, sample_count=3, every_n=2
        )
        self.assertEqual(result["samples"], [text])
        self.assertEqual(result["spans"], [[0, 21]])
        self.assertEqual(result["sampled_ratio"], 1.0)
        self.assertIn("only 1 sentence detected", result["note"])

    def test_outline_whitespace_only_text(self) -> None:
        result = self.tool.execute(
            mode="outline_sample", text="   ", sample_count=3, every_n=2
        )
        self.assertEqual(result["samples"], ["   "])
        self.assertEqual(result["spans"], [[0, 3]])
        self.assertEqual(result["total_length"], 3)

    # ------------------------------------------------------------------ #
    # Span invariants and determinism on a longer input
    # ------------------------------------------------------------------ #

    def _assert_span_invariants(
        self, result: dict, text: str
    ) -> None:
        total = len(text)
        self.assertEqual(result["total_length"], total)
        self.assertEqual(len(result["samples"]), len(result["spans"]))
        previous_end = -1
        for sample, span in zip(result["samples"], result["spans"]):
            start, end = span
            self.assertEqual(len(span), 2)
            self.assertGreaterEqual(start, 0)
            self.assertLess(start, end)
            self.assertLessEqual(end, total)
            self.assertGreaterEqual(start, previous_end)  # sorted
            previous_end = end
            self.assertEqual(text[start:end], sample)  # exact slice
        # sampled_ratio is the union coverage over the total length.
        union = 0
        last_end = -1
        for start, end in sorted(map(tuple, result["spans"])):
            clamped = max(start, last_end)
            if end > clamped:
                union += end - clamped
                last_end = end
        self.assertEqual(result["sampled_ratio"], round(union / total, 4))

    def test_span_invariants_all_modes(self) -> None:
        text = "The quick brown fox jumps over the lazy dog. " * 12
        calls = [
            dict(mode="head_tail", text=text, sample_size=37),
            dict(mode="evenly_spaced", text=text, sample_count=7,
                 sample_length=41),
            dict(mode="evenly_spaced", text=text, sample_count=1,
                 sample_length=13),
            dict(mode="strategic", text=text, sample_size=53),
            dict(mode="outline_sample", text=text, sample_count=6,
                 every_n=4),
        ]
        for kwargs in calls:
            with self.subTest(**kwargs):
                result = self.tool.execute(**kwargs)
                self._assert_span_invariants(result, text)
                self.assertGreater(result["sampled_ratio"], 0.0)
                self.assertLessEqual(result["sampled_ratio"], 1.0)

    def test_evenly_spaced_endpoints_touch_text_bounds(self) -> None:
        # For k >= 2 the first window starts at 0 and the last ends
        # exactly at the final character (the formula's i=0 / i=k-1).
        text = "x" * 101 + "y"
        result = self.tool.execute(
            mode="evenly_spaced", text=text, sample_count=5,
            sample_length=9,
        )
        self.assertEqual(result["spans"][0][0], 0)
        self.assertEqual(result["spans"][-1][1], len(text))
        # offsets: i * (102 - 9) // 4 = 0, 23, 46, 69, 93.
        self.assertEqual(result["offsets"], [0, 23, 46, 69, 93])

    def test_determinism_same_input_same_output(self) -> None:
        text = "Able was I ere I saw Elba. " * 7
        for kwargs in (
            dict(mode="head_tail", text=text, sample_size=11),
            dict(mode="evenly_spaced", text=text, sample_count=6,
                 sample_length=17),
            dict(mode="strategic", text=text, sample_size=23),
            dict(mode="outline_sample", text=text, sample_count=9,
                 every_n=3),
        ):
            with self.subTest(mode=kwargs["mode"]):
                self.assertEqual(
                    self.tool.execute(**kwargs), self.tool.execute(**kwargs)
                )

    # ------------------------------------------------------------------ #
    # Strict validation error matrix
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="middle", text="abc", sample_size=1)
        self.assertIn("mode must be one of", str(ctx.exception))
        self.assertIn("head_tail", str(ctx.exception))

    def test_error_bad_text(self) -> None:
        for bad in (None, 123, "", "x" * 100_001):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="head_tail", text=bad, sample_size=3
                    )

    def test_error_head_tail_bad_sample_size(self) -> None:
        for bad in (None, True, False, 0, -1, 1.5, "abc", "", 100_001):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="head_tail", text=ALPHABET, sample_size=bad
                    )

    def test_error_evenly_spaced_bad_counts(self) -> None:
        cases = (
            dict(sample_count=None, sample_length=5),
            dict(sample_count=4, sample_length=None),
            dict(sample_count=0, sample_length=5),
            dict(sample_count=101, sample_length=5),
            dict(sample_count=True, sample_length=5),
            dict(sample_count=4, sample_length=0),
            dict(sample_count=4, sample_length=100_001),
        )
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="evenly_spaced", text=ALPHABET, **kwargs
                    )

    def test_error_outline_bad_params(self) -> None:
        cases = (
            dict(sample_count=None, every_n=2),
            dict(sample_count=4, every_n=None),
            dict(sample_count=4, every_n=0),
            dict(sample_count=4, every_n=10_001),
            dict(sample_count=0, every_n=2),
            dict(sample_count=101, every_n=2),
        )
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="outline_sample", text=TEN_SENTENCES, **kwargs
                    )

    def test_error_cross_mode_option_misuse(self) -> None:
        cases = (
            dict(mode="head_tail", text=ALPHABET, sample_size=3,
                 every_n=2),
            dict(mode="head_tail", text=ALPHABET, sample_size=3,
                 sample_count=2),
            dict(mode="head_tail", text=ALPHABET, sample_size=3,
                 sample_length=2),
            dict(mode="evenly_spaced", text=ALPHABET, sample_count=2,
                 sample_length=3, sample_size=5),
            dict(mode="evenly_spaced", text=ALPHABET, sample_count=2,
                 sample_length=3, every_n=2),
            dict(mode="strategic", text=ALPHABET, sample_size=3,
                 sample_count=2),
            dict(mode="strategic", text=ALPHABET, sample_size=3,
                 sample_length=2),
            dict(mode="strategic", text=ALPHABET, sample_size=3,
                 every_n=2),
            dict(mode="outline_sample", text=TEN_SENTENCES,
                 sample_count=2, every_n=2, sample_size=3),
            dict(mode="outline_sample", text=TEN_SENTENCES,
                 sample_count=2, every_n=2, sample_length=3),
        )
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(**kwargs)
                self.assertIn("is only used by the", str(ctx.exception))

    def test_error_messages_are_prefixed(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="head_tail", text=ALPHABET)
        self.assertTrue(
            str(ctx.exception).startswith("text_sampler_tool: ")
        )

    def test_integer_string_options_accepted(self) -> None:
        result = self.tool.execute(
            mode="head_tail", text=ALPHABET, sample_size="5"
        )
        self.assertEqual(
            result,
            self.tool.execute(
                mode="head_tail", text=ALPHABET, sample_size=5
            ),
        )
        spaced = self.tool.execute(
            mode="evenly_spaced",
            text=ALPHABET,
            sample_count=" 4 ",
            sample_length="5",
        )
        self.assertEqual(spaced["offsets"], [0, 7, 14, 21])

    # ------------------------------------------------------------------ #
    # Package plumbing
    # ------------------------------------------------------------------ #

    def test_package_export(self) -> None:
        self.assertIs(TextSamplerTool, DirectTextSamplerTool)
        self.assertTrue(issubclass(TextSamplerTool, Tool))
        self.assertEqual(TextSamplerTool().name, "text_sampler_tool")
        self.assertEqual(
            TextSamplerTool.MODES,
            ("head_tail", "evenly_spaced", "strategic", "outline_sample"),
        )


if __name__ == "__main__":
    unittest.main()
