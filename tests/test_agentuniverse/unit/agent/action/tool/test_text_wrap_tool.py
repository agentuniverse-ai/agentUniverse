#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_text_wrap_tool.py

"""Offline unit tests for TextWrapTool.

The tool is built purely on the standard library (textwrap,
unicodedata, re) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic:

* pure-ASCII (single-paragraph, no hard newlines) wrap / fill /
  shorten results are checked against the stdlib ``textwrap``
  functions themselves across a battery of texts, widths and flag
  combinations — the tool must reproduce textwrap byte for byte where
  display width equals character count;
* east-asian width ground truths are hand-computed literals (wide
  characters count as two columns, combining marks as zero);
* hard newline preservation, indent / dedent / shorten modes,
  ``max_lines`` overflow markers, and the strict input-validation
  error matrix are each covered by exact expectations.
"""

import textwrap
import unittest

from agentuniverse.agent.action.tool.common_tool import TextWrapTool
from agentuniverse.agent.action.tool.common_tool.text_wrap_tool import (
    TextWrapTool as DirectTextWrapTool,
)

ASCII_TEXTS = [
    "hello world foo bar baz",
    "goof-ball -- yes",
    "a  b",
    "  a b",
    "aaaaaaaaaa bb",
    "12345678901234567890",
    "supercalifragilistic",
    "x" + " " * 102 + "y",
    "The quick brown fox jumps over the lazy dog and runs away",
    "em--dash pairs -- like this",
    "extra-extra-long-word here",
    "trailing spaces   ",
    "words with punctuation: hello, world! (really)",
    "tab\tseparated\twords here",
    "Hyphen-ated words like state-of-the-art machine-learning models",
]

CJK_TEN = "一二三四五六七八九十"


class TextWrapToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib TextWrapTool."""

    def setUp(self) -> None:
        self.tool = TextWrapTool()

    # ------------------------------------------------------------------ #
    # wrap mode — latin ground truths (match textwrap for pure-latin)
    # ------------------------------------------------------------------ #

    def test_wrap_known_vector(self) -> None:
        result = self.tool.execute(
            mode="wrap", text="hello world foo bar baz", width=20
        )
        self.assertEqual(
            result,
            {
                "mode": "wrap",
                "width": 20,
                "max_lines": None,
                "line_count": 2,
                "truncated": False,
                "dropped_chars": 0,
                "result": ["hello world foo bar", "baz"],
            },
        )

    def test_wrap_matches_textwrap_battery(self) -> None:
        """Pure-latin wrapping must be byte-identical to textwrap."""
        for text in ASCII_TEXTS:
            for width in (1, 2, 3, 5, 8, 10, 12, 20, 40, 80):
                for blw in (True, False):
                    for boh in (True, False):
                        with self.subTest(text=text[:20], width=width, blw=blw, boh=boh):
                            expected = textwrap.wrap(
                                text,
                                width=width,
                                break_long_words=blw,
                                break_on_hyphens=boh,
                            )
                            got = self.tool.execute(
                                mode="wrap",
                                text=text,
                                width=width,
                                break_long_words=blw,
                                break_on_hyphens=boh,
                            )["result"]
                            self.assertEqual(got, expected)

    def test_wrap_known_hyphen_and_long_word_vectors(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="goof-ball -- yes", width=10)["result"],
            ["goof-ball", "-- yes"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="supercalifragilistic", width=8)["result"],
            ["supercal", "ifragili", "stic"],
        )
        self.assertEqual(
            self.tool.execute(
                mode="wrap", text="ab cd", width=1, break_long_words=False
            )["result"],
            ["ab", "cd"],
        )
        self.assertEqual(
            self.tool.execute(
                mode="wrap", text="goof-ball stuff", width=9, break_on_hyphens=False
            )["result"],
            ["goof-ball", "stuff"],
        )

    def test_wrap_indents_match_textwrap(self) -> None:
        text = "the quick brown fox jumps over the lazy dog"
        for width in (6, 10, 14, 20, 80):
            with self.subTest(width=width):
                expected = textwrap.wrap(
                    text, width=width, initial_indent="* ", subsequent_indent="  "
                )
                got = self.tool.execute(
                    mode="wrap",
                    text=text,
                    width=width,
                    initial_indent="* ",
                    subsequent_indent="  ",
                )["result"]
                self.assertEqual(got, expected)
        self.assertEqual(
            self.tool.execute(
                mode="wrap",
                text="the quick brown fox",
                width=14,
                initial_indent="* ",
                subsequent_indent="  ",
            )["result"],
            ["* the quick", "  brown fox"],
        )

    def test_wrap_default_width_is_80(self) -> None:
        text = "word " * 40
        got = self.tool.execute(mode="wrap", text=text)["result"]
        self.assertEqual(got, textwrap.wrap(text, width=80))
        self.assertEqual(got, self.tool.execute(mode="wrap", text=text, width=80)["result"])

    def test_wrap_width_bounds_accepted(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="ab", width=1)["result"], ["a", "b"]
        )
        long_line = "a" * 400
        self.assertEqual(
            self.tool.execute(mode="wrap", text=long_line, width=200)["result"],
            ["a" * 200, "a" * 200],
        )

    # ------------------------------------------------------------------ #
    # wrap mode — east-asian width ground truths
    # ------------------------------------------------------------------ #

    def test_wrap_cjk_ten_wide_chars_five_per_line_at_width_10(self) -> None:
        result = self.tool.execute(mode="wrap", text=CJK_TEN, width=10)["result"]
        self.assertEqual(result, ["一二三四五", "六七八九十"])

    def test_wrap_cjk_width_8(self) -> None:
        result = self.tool.execute(mode="wrap", text=CJK_TEN, width=8)["result"]
        self.assertEqual(result, ["一二三四", "五六七八", "九十"])

    def test_wrap_cjk_better_than_textwrap_char_counting(self) -> None:
        # textwrap counts characters, not columns: it would put all ten
        # CJK characters (20 columns!) on a single width-10 line.
        self.assertEqual(textwrap.wrap(CJK_TEN, width=10), [CJK_TEN])
        self.assertEqual(
            self.tool.execute(mode="wrap", text=CJK_TEN, width=10)["result"],
            ["一二三四五", "六七八九十"],
        )

    def test_wrap_mixed_cjk_and_latin(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="abc一二三def", width=9)["result"],
            ["abc一二三", "def"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="一aa二bb三cc", width=8)["result"],
            ["一aa二bb", "三cc"],
        )

    def test_wrap_fullwidth_and_kana(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="ＡＢＣＤ", width=4)["result"],
            ["ＡＢ", "ＣＤ"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="あいうえおかきくけこ", width=10)["result"],
            ["あいうえお", "かきくけこ"],
        )

    def test_wrap_combining_marks_count_zero_and_never_split(self) -> None:
        # "cafe" + combining acute is 5 characters but 4 columns; the
        # mark stays glued to its base (textwrap would split them).
        text = "cafe\u0301 x"
        self.assertEqual(
            self.tool.execute(mode="wrap", text=text, width=4)["result"],
            ["cafe\u0301", "x"],
        )

    def test_wrap_emoji_zwj_sequence_stays_one_unit(self) -> None:
        family = "👨‍👩‍👧"
        result = self.tool.execute(mode="wrap", text=family + " and more text", width=8)
        self.assertEqual(result["result"][0], family)  # 6 columns, unbroken
        self.assertTrue(all(len(line) <= 8 for line in result["result"]))

    def test_wrap_wide_char_at_tiny_width_overlong_by_design(self) -> None:
        # A single wide character cannot fit a 1-column line; the tool
        # emits it whole rather than looping.
        self.assertEqual(
            self.tool.execute(mode="wrap", text="中中", width=1)["result"],
            ["中", "中"],
        )

    # ------------------------------------------------------------------ #
    # hard newline preservation
    # ------------------------------------------------------------------ #

    def test_wrap_hard_newlines_are_breaks_not_spaces(self) -> None:
        # textwrap converts newlines to spaces; this tool keeps them.
        self.assertEqual(textwrap.wrap("hello\nworld", width=80), ["hello world"])
        self.assertEqual(
            self.tool.execute(mode="wrap", text="hello\nworld", width=80)["result"],
            ["hello", "world"],
        )

    def test_wrap_blank_lines_preserved(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="para1\n\npara2", width=80)["result"],
            ["para1", "", "para2"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="a\n", width=80)["result"],
            ["a", ""],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="one two\n\nthree four", width=5)["result"],
            ["one", "two", "", "three", "four"],
        )

    def test_wrap_crlf_and_lone_cr_are_hard_breaks(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="a\r\nb", width=80)["result"],
            ["a", "b"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="a\rb", width=80)["result"],
            ["a", "b"],
        )

    def test_wrap_tabs_expanded_like_textwrap(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="ab\tcd", width=4)["result"],
            ["ab", "cd"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="tab\tseparated words", width=8)["result"],
            textwrap.wrap("tab\tseparated words", width=8),
        )

    def test_wrap_whitespace_only_line_emits_empty_line(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="wrap", text="a\n   \nb", width=80)["result"],
            ["a", "", "b"],
        )

    # ------------------------------------------------------------------ #
    # fill mode
    # ------------------------------------------------------------------ #

    def test_fill_matches_textwrap(self) -> None:
        for text in ASCII_TEXTS:
            for width in (5, 10, 20, 80):
                with self.subTest(text=text[:20], width=width):
                    expected = textwrap.fill(text, width=width)
                    got = self.tool.execute(mode="fill", text=text, width=width)
                    self.assertEqual(got["separator"], "\n")
                    self.assertEqual(got["result"], expected)

    def test_fill_known_vector(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="fill", text="hello world", width=10)["result"],
            "hello\nworld",
        )

    def test_fill_custom_separator(self) -> None:
        result = self.tool.execute(
            mode="fill", text="hello big world", width=10, separator=" | "
        )
        self.assertEqual(result["separator"], " | ")
        self.assertEqual(result["result"], "hello big | world")
        spacey = self.tool.execute(
            mode="fill", text="hello world", width=5, separator=""
        )
        self.assertEqual(spacey["result"], "helloworld")

    def test_fill_hard_newlines_preserved(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="fill", text="a\nb", width=80)["result"],
            "a\nb",
        )

    # ------------------------------------------------------------------ #
    # dedent mode
    # ------------------------------------------------------------------ #

    def test_dedent_known_vectors(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="dedent", text="  a\n    b")["result"],
            textwrap.dedent("  a\n    b"),
        )
        self.assertEqual(
            self.tool.execute(mode="dedent", text="  a\n    b")["result"],
            "a\n  b",
        )

    def test_dedent_no_common_margin(self) -> None:
        # A flush-left line means no margin can be removed.
        text = "  a\n    b\nc"
        self.assertEqual(
            self.tool.execute(mode="dedent", text=text)["result"],
            text,
        )

    def test_dedent_whitespace_only_lines_normalized(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="dedent", text="  a\n   \n    b")["result"],
            "a\n\n  b",
        )

    # ------------------------------------------------------------------ #
    # indent mode
    # ------------------------------------------------------------------ #

    def test_indent_prefixes_non_blank_lines(self) -> None:
        result = self.tool.execute(mode="indent", text="a\n \nb\n", prefix="> ")
        self.assertEqual(result["mode"], "indent")
        self.assertEqual(result["prefix"], "> ")
        self.assertEqual(result["result"], "> a\n \n> b\n")
        self.assertEqual(
            result["result"], textwrap.indent("a\n \nb\n", "> ")
        )

    def test_indent_blockquote_vector(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="indent", text="line1\nline2", prefix="  | ")["result"],
            "  | line1\n  | line2",
        )

    # ------------------------------------------------------------------ #
    # shorten mode
    # ------------------------------------------------------------------ #

    def test_shorten_matches_textwrap_battery(self) -> None:
        for text in ASCII_TEXTS:
            for width in range(1, 40):
                with self.subTest(text=text[:20], width=width):
                    expected = textwrap.shorten(text, width=width, placeholder="…")
                    got = self.tool.execute(mode="shorten", text=text, width=width)
                    self.assertEqual(got["result"], expected)

    def test_shorten_known_vector(self) -> None:
        result = self.tool.execute(
            mode="shorten",
            text="The quick brown fox jumps over the lazy dog",
            width=20,
        )
        self.assertEqual(
            result,
            {
                "mode": "shorten",
                "width": 20,
                "truncated": True,
                "dropped_chars": 24,
                "result": "The quick brown fox…",
            },
        )

    def test_shorten_fits_without_truncation(self) -> None:
        result = self.tool.execute(mode="shorten", text="short", width=10)
        self.assertEqual(
            result,
            {
                "mode": "shorten",
                "width": 10,
                "truncated": False,
                "dropped_chars": 0,
                "result": "short",
            },
        )

    def test_shorten_collapses_whitespace(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="shorten", text="Hello  \n world", width=30)["result"],
            "Hello world",
        )
        self.assertEqual(
            self.tool.execute(mode="shorten", text="  a  b  ", width=10)["result"],
            "a b",
        )

    def test_shorten_cjk_width_aware(self) -> None:
        # Ten wide characters are 20 columns: width 9 keeps four wide
        # characters (8 columns) plus the 1-column ellipsis.
        result = self.tool.execute(mode="shorten", text=CJK_TEN, width=9)
        self.assertEqual(result["result"], "一二三四…")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["dropped_chars"], 6)
        # textwrap counts characters, not columns: its width-9 pass
        # cannot keep even the sliced fragment, so it degrades to the
        # bare placeholder.
        self.assertEqual(
            textwrap.shorten(CJK_TEN, width=9, placeholder="…"), "…"
        )

    def test_shorten_placeholder_alone_when_first_word_too_long(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="shorten", text="supercalifragilistic", width=10)["result"],
            "…",
        )
        self.assertEqual(
            self.tool.execute(
                mode="shorten",
                text="supercalifragilistic",
                width=10,
                break_long_words=False,
            )["result"],
            "…",
        )

    # ------------------------------------------------------------------ #
    # max_lines overflow markers
    # ------------------------------------------------------------------ #

    def test_max_lines_marker_appended_without_popping(self) -> None:
        result = self.tool.execute(
            mode="wrap", text="aaaa\nbbbb\ncccc", width=20, max_lines=2
        )
        self.assertEqual(
            result,
            {
                "mode": "wrap",
                "width": 20,
                "max_lines": 2,
                "line_count": 2,
                "truncated": True,
                "dropped_chars": 4,
                "result": ["aaaa", "bbbb … [+4 chars]"],
            },
        )

    def test_max_lines_pops_words_to_fit_marker(self) -> None:
        result = self.tool.execute(
            mode="wrap", text="aa bb cc dd ee ff gg hh", width=20, max_lines=1
        )
        # Full wrap gives ['aa bb cc dd ee ff gg', 'hh']; the marker
        # (12 columns) pushes gg, ff, ee, dd and cc off the line.
        self.assertEqual(result["result"], ["aa bb … [+12 chars]"])
        self.assertTrue(result["truncated"])
        self.assertEqual(result["dropped_chars"], 12)
        self.assertEqual(result["line_count"], 1)

    def test_max_lines_cjk_marker(self) -> None:
        result = self.tool.execute(
            mode="wrap", text="一二三 甲乙丙丁戊己庚辛壬", width=19, max_lines=1
        )
        self.assertEqual(result["result"], ["一二三 … [+9 chars]"])
        self.assertEqual(result["dropped_chars"], 9)

    def test_max_lines_marker_alone_when_nothing_fits(self) -> None:
        # Width 10 cannot hold any wide character plus the marker, so
        # the marker replaces the content (overlong by design).
        result = self.tool.execute(mode="wrap", text=CJK_TEN, width=10, max_lines=1)
        self.assertEqual(result["result"], ["… [+10 chars]"])
        self.assertEqual(result["dropped_chars"], 10)

    def test_max_lines_blank_only_drop_has_no_marker(self) -> None:
        result = self.tool.execute(mode="wrap", text="aaaa\n\n\n", width=20, max_lines=1)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["dropped_chars"], 0)
        self.assertEqual(result["result"], ["aaaa"])

    def test_max_lines_no_truncation_when_it_fits(self) -> None:
        result = self.tool.execute(
            mode="wrap", text="aa bb cc", width=80, max_lines=5
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(result["dropped_chars"], 0)
        self.assertEqual(result["result"], ["aa bb cc"])

    def test_max_lines_fill_mode_marker(self) -> None:
        result = self.tool.execute(
            mode="fill", text="aaaa\nbbbb\ncccc", width=20, max_lines=2
        )
        self.assertEqual(result["result"], "aaaa\nbbbb … [+4 chars]")
        self.assertTrue(result["truncated"])

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="reflow", text="hello")
        self.assert_invalid(mode=None, text="hello")
        self.assert_invalid(mode=123, text="hello")
        self.assert_invalid(text="hello")  # mode is required

    def test_invalid_text(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="wrap", text=bad, width=20)
                self.assert_invalid(mode="dedent", text=bad)
        self.assert_invalid(mode="wrap", text="", width=20)
        self.assert_invalid(mode="shorten", text="", width=20)

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="wrap", text=oversized, width=20)
        self.assert_invalid(mode="indent", text=oversized, prefix="> ")
        ok = self.tool.execute(mode="wrap", text="a" * 100_000, width=200)
        self.assertEqual(ok["line_count"], 500)

    def test_invalid_width(self) -> None:
        for bad in (0, -1, 201, 1.5, "80", True, False):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="wrap", text="hello", width=bad)
        # Boundaries are accepted.
        self.assertEqual(
            self.tool.execute(mode="wrap", text="hello", width=1)["result"],
            ["h", "e", "l", "l", "o"],
        )
        self.assertEqual(
            self.tool.execute(mode="wrap", text="hello", width=200)["result"],
            ["hello"],
        )

    def test_invalid_break_flags(self) -> None:
        for bad in (1, 0, "yes"):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="wrap", text="hello", width=20, break_long_words=bad
                )
                self.assert_invalid(
                    mode="wrap", text="hello", width=20, break_on_hyphens=bad
                )

    def test_invalid_max_lines(self) -> None:
        for bad in (0, -3, 1.0, "5", True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="wrap", text="hello", width=20, max_lines=bad
                )

    def test_invalid_indents(self) -> None:
        self.assert_invalid(mode="wrap", text="hello", width=5, initial_indent=123)
        self.assert_invalid(mode="wrap", text="hello", width=5, subsequent_indent=True)
        self.assert_invalid(
            mode="wrap", text="hello", width=20, initial_indent="line\nbreak"
        )
        self.assert_invalid(
            mode="wrap", text="hello", width=20, subsequent_indent="\r"
        )
        # An indent as wide as (or wider than) the width is rejected.
        self.assert_invalid(mode="wrap", text="hello", width=5, initial_indent="abcdef")
        self.assert_invalid(mode="wrap", text="hello", width=4, subsequent_indent="一二")
        # Wide indents are measured in columns: two CJK columns need
        # width >= 3 to be valid.
        self.assert_invalid(mode="wrap", text="hello", width=2, initial_indent="一")
        got = self.tool.execute(
            mode="wrap", text="hello", width=3, initial_indent="一"
        )
        self.assertTrue(got["result"][0].startswith("一"))

    def test_invalid_separator(self) -> None:
        self.assert_invalid(mode="fill", text="hello", width=20, separator=5)
        self.assert_invalid(mode="fill", text="hello", width=20, separator=True)
        self.assert_invalid(
            mode="fill", text="hello", width=20, separator="x" * 1_001
        )

    def test_invalid_prefix(self) -> None:
        self.assert_invalid(mode="indent", text="hello", prefix=None)
        self.assert_invalid(mode="indent", text="hello", prefix="")
        self.assert_invalid(mode="indent", text="hello", prefix=42)
        self.assert_invalid(mode="indent", text="hello", prefix="x" * 201)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectTextWrapTool, TextWrapTool)
        self.assertEqual(self.tool.name, "text_wrap_tool")
        self.assertIn("wrap", self.tool.description)
        self.assertIn("dedent", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("TextWrapTool", __all__)


if __name__ == "__main__":
    unittest.main()
