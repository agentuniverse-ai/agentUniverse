#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_pad_tool.py

"""Offline unit tests for TextPadTool.

The tool is built purely on the standard library (unicodedata) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: latin padding / zfill results are checked
against literal expected strings and against the stdlib str.ljust /
str.rjust / str.zfill counterparts, CJK and emoji expectations are
pinned to the documented east-asian width rules (W/F = 2 columns,
combining marks = 0, everything else including ambiguous-width
characters such as '…' = 1), and the center-mode odd-remainder rule
(extra column on the right), the unchanged-when-too-wide rules and the
full validation error matrix are exercised explicitly.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import TextPadTool
from agentuniverse.agent.action.tool.common_tool.text_pad_tool import (
    TextPadTool as DirectTextPadTool,
)

# Ground-truth width facts pinned by the tool's documented rules.
# '中' / 'あ' / '한' are east-asian W (2 columns); '！' is F (2);
# 'ｱ' is H (1); the astral emoji '🌍' is W (2); the combining acute
# accent U+0301 is Mn (0); '…' is ambiguous (1 under this tool).
CJK = "中文"
ASTRAL_EMOJI = "🌍"
COMBINING_ACUTE = "\u0301"


class TextPadToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextPadTool."""

    def setUp(self) -> None:
        self.tool = TextPadTool()

    # ------------------------------------------------------------------ #
    # pad mode — latin ground truths
    # ------------------------------------------------------------------ #

    def test_pad_default_align_and_fill(self) -> None:
        result = self.tool.execute(mode="pad", text="hi", width=5)
        self.assertEqual(
            result,
            {
                "mode": "pad",
                "width": 5,
                "align": "left",
                "fill_char": " ",
                "input_width": 2,
                "result": "hi   ",
            },
        )

    def test_pad_aligns_latin(self) -> None:
        left = self.tool.execute(mode="pad", text="hi", width=5, align="left")
        right = self.tool.execute(
            mode="pad", text="hi", width=5, align="right"
        )
        center = self.tool.execute(
            mode="pad", text="hi", width=5, align="center"
        )
        self.assertEqual(left["result"], "hi   ")
        self.assertEqual(right["result"], "   hi")
        self.assertEqual(center["result"], " hi  ")

    def test_pad_matches_str_ljust_rjust_for_latin(self) -> None:
        # Pure-latin text behaves byte-for-byte like the stdlib calls.
        for text in ("a", "hi", "hello world", "padding!", "0" * 40):
            for width in (0, 1, 5, len(text), len(text) + 1, len(text) + 17):
                with self.subTest(text=text[:8], width=width):
                    left = self.tool.execute(
                        mode="pad", text=text, width=width, align="left"
                    )["result"]
                    right = self.tool.execute(
                        mode="pad", text=text, width=width, align="right"
                    )["result"]
                    self.assertEqual(left, text.ljust(width))
                    self.assertEqual(right, text.rjust(width))

    def test_pad_center_odd_remainder_extra_column_on_right(self) -> None:
        # Documented rounding rule: left = floor(remaining / 2), the
        # odd column goes to the right side (unlike str.center, whose
        # quirky parity rule differs, so only literals are asserted).
        cases = [
            ("a", 4, " a  "),
            ("ab", 5, " ab  "),
            ("abc", 6, " abc  "),
            ("中", 5, " 中  "),
            ("中文", 7, " 中文  "),  # remaining 3 -> left 1, right 2
            ("·", 3, " · "),
        ]
        for text, width, expected in cases:
            with self.subTest(text=text, width=width):
                result = self.tool.execute(
                    mode="pad", text=text, width=width, align="center"
                )["result"]
                self.assertEqual(result, expected)

    # ------------------------------------------------------------------ #
    # pad mode — east-asian width awareness
    # ------------------------------------------------------------------ #

    def test_pad_cjk_width_4_to_8(self) -> None:
        left = self.tool.execute(mode="pad", text=CJK, width=8)
        self.assertEqual(left["input_width"], 4)
        self.assertEqual(left["result"], "中文    ")  # exactly 4 spaces
        right = self.tool.execute(mode="pad", text=CJK, width=8, align="right")
        self.assertEqual(right["result"], "    中文")
        center = self.tool.execute(
            mode="pad", text=CJK, width=8, align="center"
        )
        self.assertEqual(center["result"], "  中文  ")

    def test_pad_mixed_cjk_latin(self) -> None:
        result = self.tool.execute(mode="pad", text="a中b", width=6)
        self.assertEqual(result["input_width"], 4)
        self.assertEqual(result["result"], "a中b  ")

    def test_pad_emoji_counts_two_columns(self) -> None:
        result = self.tool.execute(mode="pad", text=ASTRAL_EMOJI, width=5)
        self.assertEqual(result["input_width"], 2)
        self.assertEqual(result["result"], ASTRAL_EMOJI + "   ")

    def test_pad_combining_marks_count_zero(self) -> None:
        # "e" + combining acute is 2 characters but 1 column.
        text = "e" + COMBINING_ACUTE
        result = self.tool.execute(mode="pad", text=text, width=3)
        self.assertEqual(result["input_width"], 1)
        self.assertEqual(result["result"], text + "  ")

    def test_pad_zero_width_only_text(self) -> None:
        result = self.tool.execute(
            mode="pad", text=COMBINING_ACUTE, width=3, align="right"
        )
        self.assertEqual(result["input_width"], 0)
        self.assertEqual(result["result"], "   " + COMBINING_ACUTE)

    # ------------------------------------------------------------------ #
    # pad mode — fill characters and boundary behavior
    # ------------------------------------------------------------------ #

    def test_pad_custom_fill_char(self) -> None:
        left = self.tool.execute(
            mode="pad", text="7", width=5, fill_char="*"
        )
        self.assertEqual(left["result"], "7****")
        right = self.tool.execute(
            mode="pad", text="42", width=6, align="right", fill_char="0"
        )
        self.assertEqual(right["result"], "000042")
        center = self.tool.execute(
            mode="pad", text=CJK, width=8, align="center", fill_char="·"
        )
        # '·' is ambiguous-width: one column, so it may fill.
        self.assertEqual(center["result"], "··中文··")

    def test_pad_exact_fit_returns_text(self) -> None:
        result = self.tool.execute(mode="pad", text="hello", width=5)
        self.assertEqual(result["result"], "hello")
        cjk = self.tool.execute(mode="pad", text=CJK, width=4)
        self.assertEqual(cjk["result"], CJK)

    def test_pad_text_wider_than_width_returns_text_unchanged(self) -> None:
        # Documented: pad never truncates and never errors here — it
        # mirrors str.ljust / str.rjust / str.center.
        for align in ("left", "right", "center"):
            result = self.tool.execute(
                mode="pad", text="hello", width=3, align=align
            )
            self.assertEqual(result["result"], "hello")
            self.assertEqual(result["input_width"], 5)
        cjk = self.tool.execute(mode="pad", text="中文中文", width=7)
        self.assertEqual(cjk["result"], "中文中文")

    def test_pad_width_boundaries_accepted(self) -> None:
        zero = self.tool.execute(mode="pad", text="a", width=0)
        self.assertEqual(zero["result"], "a")  # unchanged: 1 > 0
        top = self.tool.execute(mode="pad", text="a", width=10000)
        self.assertEqual(len(top["result"]), 10000)

    # ------------------------------------------------------------------ #
    # zfill mode
    # ------------------------------------------------------------------ #

    def test_zfill_basic(self) -> None:
        result = self.tool.execute(mode="zfill", text="42", width=5)
        self.assertEqual(
            result,
            {
                "mode": "zfill",
                "width": 5,
                "input_width": 2,
                "sign": None,
                "result": "00042",
            },
        )

    def test_zfill_preserves_sign(self) -> None:
        minus = self.tool.execute(mode="zfill", text="-42", width=5)
        self.assertEqual(minus["sign"], "-")
        self.assertEqual(minus["result"], "-0042")
        plus = self.tool.execute(mode="zfill", text="+42", width=5)
        self.assertEqual(plus["sign"], "+")
        self.assertEqual(plus["result"], "+0042")
        bare = self.tool.execute(mode="zfill", text="-", width=3)
        self.assertEqual(bare["result"], "-00")

    def test_zfill_sign_only_recognized_at_position_zero(self) -> None:
        result = self.tool.execute(mode="zfill", text="a-b", width=6)
        self.assertIsNone(result["sign"])
        self.assertEqual(result["result"], "000a-b")

    def test_zfill_matches_str_zfill_for_latin(self) -> None:
        for text in ("42", "-42", "+42", "0", "abc", "-", "a-b", "-0.5"):
            for width in (0, 1, 3, len(text), len(text) + 5):
                with self.subTest(text=text, width=width):
                    result = self.tool.execute(
                        mode="zfill", text=text, width=width
                    )["result"]
                    self.assertEqual(result, text.zfill(width))

    def test_zfill_width_aware_cjk(self) -> None:
        plain = self.tool.execute(mode="zfill", text="中", width=5)
        self.assertEqual(plain["input_width"], 2)
        self.assertEqual(plain["result"], "000中")
        signed = self.tool.execute(mode="zfill", text="-中", width=6)
        self.assertEqual(signed["sign"], "-")
        self.assertEqual(signed["input_width"], 3)
        self.assertEqual(signed["result"], "-000中")
        emoji = self.tool.execute(mode="zfill", text=ASTRAL_EMOJI, width=4)
        self.assertEqual(emoji["result"], "00" + ASTRAL_EMOJI)

    def test_zfill_text_wider_than_width_returns_text_unchanged(self) -> None:
        result = self.tool.execute(mode="zfill", text="-12345", width=4)
        self.assertEqual(result["sign"], "-")
        self.assertEqual(result["result"], "-12345")
        equal = self.tool.execute(mode="zfill", text="12345", width=5)
        self.assertEqual(equal["result"], "12345")

    # ------------------------------------------------------------------ #
    # truncate_to_width mode
    # ------------------------------------------------------------------ #

    def test_truncate_default_marker_within_width(self) -> None:
        result = self.tool.execute(
            mode="truncate_to_width", text="hello world", width=8
        )
        self.assertEqual(
            result,
            {
                "mode": "truncate_to_width",
                "width": 8,
                "marker": "…",
                "input_width": 11,
                "truncated": True,
                "dropped_chars": 4,
                "result": "hello w…",
            },
        )

    def test_truncate_plain_cut_without_marker(self) -> None:
        # An explicitly empty marker disables the truncation marker.
        result = self.tool.execute(
            mode="truncate_to_width", text="hello world", width=8, marker=""
        )
        self.assertIsNone(result["marker"])
        self.assertEqual(result["result"], "hello wo")
        self.assertEqual(result["dropped_chars"], 3)
        empty_marker = self.tool.execute(
            mode="truncate_to_width", text="abcd", width=2, marker=""
        )
        self.assertIsNone(empty_marker["marker"])
        self.assertEqual(empty_marker["result"], "ab")

    def test_truncate_custom_marker(self) -> None:
        dots = self.tool.execute(
            mode="truncate_to_width", text="hello world", width=8, marker="..."
        )
        self.assertEqual(dots["result"], "hello...")
        self.assertEqual(dots["dropped_chars"], 6)

    def test_truncate_cjk_exact_columns(self) -> None:
        result = self.tool.execute(
            mode="truncate_to_width", text="中文字", width=5
        )
        # 6 columns -> content cut to 4 ("中文") + 1-column marker.
        self.assertEqual(result["result"], "中文…")
        self.assertEqual(result["truncated"], True)
        self.assertEqual(result["dropped_chars"], 1)

    def test_truncate_never_splits_wide_character(self) -> None:
        # Plain cut at width 3 of "中中" (4 columns): the second wide
        # character would straddle the budget, so it is dropped whole
        # and the result is one column short of the request.
        plain = self.tool.execute(
            mode="truncate_to_width", text="中中", width=3, marker=""
        )
        self.assertEqual(plain["result"], "中")
        self.assertEqual(plain["dropped_chars"], 1)
        marked = self.tool.execute(
            mode="truncate_to_width", text="中中", width=3
        )
        self.assertEqual(marked["result"], "中…")

    def test_truncate_marker_takes_the_whole_width(self) -> None:
        result = self.tool.execute(
            mode="truncate_to_width", text="hello", width=1
        )
        self.assertEqual(result["result"], "…")
        self.assertEqual(result["dropped_chars"], 5)

    def test_truncate_width_zero_without_marker(self) -> None:
        result = self.tool.execute(
            mode="truncate_to_width", text="abc", width=0, marker=""
        )
        self.assertEqual(result["truncated"], True)
        self.assertEqual(result["dropped_chars"], 3)
        self.assertEqual(result["result"], "")

    def test_truncate_noop_when_text_fits(self) -> None:
        result = self.tool.execute(
            mode="truncate_to_width", text="hi", width=10
        )
        self.assertEqual(result["truncated"], False)
        self.assertEqual(result["dropped_chars"], 0)
        self.assertEqual(result["result"], "hi")
        exact = self.tool.execute(mode="truncate_to_width", text="中中", width=4)
        self.assertEqual(exact["truncated"], False)
        self.assertEqual(exact["result"], "中中")

    def test_truncate_keeps_combining_marks_glued(self) -> None:
        text = "e" + COMBINING_ACUTE + "abc"
        plain = self.tool.execute(
            mode="truncate_to_width", text=text, width=1, marker=""
        )
        self.assertEqual(plain["result"], "e" + COMBINING_ACUTE)
        marked = self.tool.execute(
            mode="truncate_to_width", text=text, width=2
        )
        self.assertEqual(marked["result"], "e" + COMBINING_ACUTE + "…")

    def test_truncate_emoji_and_mixed_widths(self) -> None:
        emoji = self.tool.execute(
            mode="truncate_to_width", text=ASTRAL_EMOJI * 2, width=3
        )
        self.assertEqual(emoji["result"], ASTRAL_EMOJI + "…")
        mixed = self.tool.execute(
            mode="truncate_to_width", text="a" + ASTRAL_EMOJI + "中!",
            width=5,
            marker="",
        )
        self.assertEqual(mixed["result"], "a" + ASTRAL_EMOJI + "中")

    # ------------------------------------------------------------------ #
    # width mode
    # ------------------------------------------------------------------ #

    def test_width_mode_latin(self) -> None:
        result = self.tool.execute(mode="width", text="hello")
        self.assertEqual(
            result,
            {
                "mode": "width",
                "width": 5,
                "character_count": 5,
                "result": 5,
            },
        )

    def test_width_mode_cjk_and_mixed(self) -> None:
        cases = [
            (CJK, 4, 2),
            ("a中b", 4, 3),
            ("中英文x", 7, 4),
            ("あ", 2, 1),
            ("한", 2, 1),
            ("！", 2, 1),
            ("!", 1, 1),
            ("ｱ", 1, 1),  # halfwidth katakana: H, one column
            ("a" + ASTRAL_EMOJI + "中!", 6, 4),
        ]
        for text, expected_width, expected_chars in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="width", text=text)
                self.assertEqual(result["width"], expected_width)
                self.assertEqual(result["result"], expected_width)
                self.assertEqual(result["character_count"], expected_chars)

    def test_width_mode_emoji_and_combining_pinned(self) -> None:
        # Astral-plane emoji are wide (2 columns) per the Unicode east
        # asian width tables; combining marks occupy zero columns.
        self.assertEqual(
            self.tool.execute(mode="width", text=ASTRAL_EMOJI)["result"], 2
        )
        self.assertEqual(
            self.tool.execute(mode="width", text=ASTRAL_EMOJI * 2)["result"],
            4,
        )
        self.assertEqual(
            self.tool.execute(mode="width", text="e" + COMBINING_ACUTE)[
                "result"
            ],
            1,
        )

    def test_width_mode_ambiguous_characters_are_one_column(self) -> None:
        for text in ("…", "·", "Ω"):
            with self.subTest(text=text):
                self.assertEqual(
                    self.tool.execute(mode="width", text=text)["result"], 1
                )

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="padding", text="hi", width=5)
        self.assert_invalid(mode=None, text="hi", width=5)
        self.assert_invalid(mode=123, text="hi", width=5)
        self.assert_invalid(mode="pad ", text="hi", width=5)

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hi", ["hi"], 3.14):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="pad", text=bad, width=5)
                self.assert_invalid(mode="width", text=bad)
                self.assert_invalid(mode="zfill", text=bad, width=5)

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="pad", text="", width=5)
        self.assert_invalid(mode="zfill", text="", width=5)
        self.assert_invalid(mode="truncate_to_width", text="", width=5)
        self.assert_invalid(mode="width", text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="pad", text=oversized, width=10)
        self.assert_invalid(mode="width", text=oversized)
        ok = self.tool.execute(mode="width", text="a" * 100_000)
        self.assertEqual(ok["result"], 100_000)

    def test_invalid_width(self) -> None:
        for bad in (None, True, False, "8", 8.0, -1, -100, 10001, 99999):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="pad", text="hi", width=bad)
                self.assert_invalid(mode="zfill", text="hi", width=bad)
                self.assert_invalid(
                    mode="truncate_to_width", text="hi", width=bad
                )

    def test_width_not_required_for_width_mode(self) -> None:
        # The width option is meaningless for (and ignored by) width
        # mode, whether absent or present.
        self.assertEqual(
            self.tool.execute(mode="width", text="hi", width=99)["result"], 2
        )

    def test_invalid_align(self) -> None:
        for bad in ("middle", "LEFT", "left ", "l", 5, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="pad", text="hi", width=5, align=bad
                )

    def test_invalid_fill_char(self) -> None:
        for bad in ("", "**", "  ", "中", "あ", COMBINING_ACUTE, "\u200d", 5, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="pad", text="hi", width=8, fill_char=bad
                )

    def test_invalid_marker(self) -> None:
        for bad in (5, True, "x" * 11, COMBINING_ACUTE, "中" * 6):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="truncate_to_width", text="hi", width=8, marker=bad
                )

    def test_marker_wider_than_width_rejected(self) -> None:
        self.assert_invalid(
            mode="truncate_to_width", text="hi", width=2, marker="..."
        )
        self.assert_invalid(
            mode="truncate_to_width", text="hi", width=1, marker="……"
        )
        # The default marker is one column: fine at width 1, but a
        # plain contradiction at width 0 (marker="" cuts to "").
        self.assertEqual(
            self.tool.execute(
                mode="truncate_to_width", text="hi", width=1
            )["result"],
            "…",
        )
        self.assert_invalid(
            mode="truncate_to_width", text="hi", width=0, marker="…"
        )

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextPadTool, TextPadTool)
        self.assertEqual(self.tool.name, "text_pad_tool")
        self.assertIn("pad", self.tool.description)
        self.assertIn("truncate_to_width", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextPadTool", __all__)


if __name__ == "__main__":
    unittest.main()
