#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_line_ops_tool.py

"""Offline unit tests for LineOpsTool.

The tool is built purely on the standard library (string methods plus
one ``re`` split) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: each mode is checked
against literal ground-truth outputs (natural sort puts ``file2``
before ``file10``, zero-padded numbering formats, first-occurrence
deduplication, head/tail counts and truncation flags), CRLF handling
is pinned down end to end, and the validation matrix covers every
malformed parameter the tool rejects with ``ValueError``.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import LineOpsTool
from agentuniverse.agent.action.tool.common_tool.line_ops_tool import (
    LineOpsTool as DirectLineOpsTool,
)

FIVE_LINES = "l1\nl2\nl3\nl4\nl5"


class LineOpsToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib LineOpsTool."""

    def setUp(self) -> None:
        self.tool = LineOpsTool()

    # ------------------------------------------------------------------ #
    # sort mode — lexicographic baseline
    # ------------------------------------------------------------------ #

    def test_sort_lexicographic_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="sort", text="banana\napple\ncherry"
        )
        self.assertEqual(
            result,
            {
                "mode": "sort",
                "newline": "lf",
                "input_lines": 3,
                "natural": False,
                "case_insensitive": False,
                "reverse": False,
                "unique": False,
                "duplicates_removed": 0,
                "output_lines": 3,
                "result": "apple\nbanana\ncherry",
            },
        )

    def test_sort_lexicographic_puts_file10_before_file2(self) -> None:
        # Without natural mode the comparison is plain code-point order.
        result = self.tool.execute(mode="sort", text="file1\nfile10\nfile2")
        self.assertEqual(result["result"], "file1\nfile10\nfile2")

    def test_sort_empty_line_sorts_first(self) -> None:
        result = self.tool.execute(mode="sort", text="b\n\na")
        self.assertEqual(result["result"], "\na\nb")
        self.assertEqual(result["input_lines"], 3)

    # ------------------------------------------------------------------ #
    # sort mode — natural (numeric-aware) ordering
    # ------------------------------------------------------------------ #

    def test_sort_natural_file2_before_file10(self) -> None:
        result = self.tool.execute(
            mode="sort", text="file1\nfile10\nfile2", natural=True
        )
        self.assertEqual(result["result"], "file1\nfile2\nfile10")
        self.assertTrue(result["natural"])

    def test_sort_natural_multiple_digit_runs(self) -> None:
        result = self.tool.execute(
            mode="sort", text="a10b2\na2b10\na2b11", natural=True
        )
        self.assertEqual(result["result"], "a2b10\na2b11\na10b2")

    def test_sort_natural_leading_zeros_compare_equal_stable(self) -> None:
        # v07 and v7 have equal natural keys, so the stable sort keeps
        # the input order in both directions.
        first = self.tool.execute(mode="sort", text="v7\nv07", natural=True)
        self.assertEqual(first["result"], "v7\nv07")
        second = self.tool.execute(mode="sort", text="v07\nv7", natural=True)
        self.assertEqual(second["result"], "v07\nv7")

    def test_sort_natural_arbitrary_precision_numbers(self) -> None:
        # Digit runs are compared as Python ints, beyond 64-bit range.
        result = self.tool.execute(
            mode="sort",
            text="v100000000000000000000\nv99999999999999999999",
            natural=True,
        )
        self.assertEqual(
            result["result"],
            "v99999999999999999999\nv100000000000000000000",
        )

    def test_sort_natural_zero_before_one_before_ten(self) -> None:
        result = self.tool.execute(
            mode="sort", text="item10\nitem0\nitem1\nitem9", natural=True
        )
        self.assertEqual(result["result"], "item0\nitem1\nitem9\nitem10")

    # ------------------------------------------------------------------ #
    # sort mode — case handling, reverse, unique
    # ------------------------------------------------------------------ #

    def test_sort_case_sensitive_code_point_order(self) -> None:
        result = self.tool.execute(mode="sort", text="b\nB\na")
        self.assertEqual(result["result"], "B\na\nb")

    def test_sort_case_insensitive_with_stability(self) -> None:
        # 'b' and 'B' tie under case folding; the stable sort keeps
        # 'b' (input position 0) before 'B' (input position 1).
        result = self.tool.execute(
            mode="sort", text="b\nB\na", case_insensitive=True
        )
        self.assertEqual(result["result"], "a\nb\nB")
        self.assertTrue(result["case_insensitive"])

    def test_sort_case_insensitive_reverse_keeps_stability(self) -> None:
        # reverse=True flips the ordering but equal keys still keep
        # their input order, so 'b' stays before 'B'.
        result = self.tool.execute(
            mode="sort",
            text="b\nB\na",
            case_insensitive=True,
            reverse=True,
        )
        self.assertEqual(result["result"], "b\nB\na")
        self.assertTrue(result["reverse"])

    def test_sort_natural_case_insensitive_combined(self) -> None:
        result = self.tool.execute(
            mode="sort", text="File10\nfile2", natural=True,
            case_insensitive=True,
        )
        self.assertEqual(result["result"], "file2\nFile10")

    def test_sort_reverse_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="sort", text="a\nb\nc", reverse=True
        )
        self.assertEqual(result["result"], "c\nb\na")

    def test_sort_unique_then_sort_with_removed_count(self) -> None:
        result = self.tool.execute(
            mode="sort", text="b\na\nb\na\nb", unique=True
        )
        self.assertEqual(result["result"], "a\nb")
        self.assertEqual(result["duplicates_removed"], 3)
        self.assertEqual(result["output_lines"], 2)
        self.assertTrue(result["unique"])

    # ------------------------------------------------------------------ #
    # unique mode
    # ------------------------------------------------------------------ #

    def test_unique_preserves_first_occurrence_order(self) -> None:
        result = self.tool.execute(
            mode="unique", text="x\ny\nx\nz\ny\nx"
        )
        self.assertEqual(
            result,
            {
                "mode": "unique",
                "newline": "lf",
                "input_lines": 6,
                "duplicates_removed": 3,
                "output_lines": 3,
                "result": "x\ny\nz",
            },
        )

    def test_unique_no_duplicates_is_identity(self) -> None:
        result = self.tool.execute(mode="unique", text="a\nb\nc")
        self.assertEqual(result["result"], "a\nb\nc")
        self.assertEqual(result["duplicates_removed"], 0)

    def test_unique_distinct_empty_lines_collapse(self) -> None:
        # "\n\n" normalizes to two empty lines; they dedupe to one.
        result = self.tool.execute(mode="unique", text="\n\n")
        self.assertEqual(result["input_lines"], 2)
        self.assertEqual(result["output_lines"], 1)
        self.assertEqual(result["result"], "")

    # ------------------------------------------------------------------ #
    # trim mode
    # ------------------------------------------------------------------ #

    def test_trim_strips_trailing_whitespace_only(self) -> None:
        result = self.tool.execute(
            mode="trim", text="alpha  \nbeta\t\t\n\ngamma  "
        )
        self.assertEqual(result["result"], "alpha\nbeta\n\ngamma")
        self.assertFalse(result["drop_empty"])
        self.assertEqual(result["lines_dropped"], 0)
        self.assertEqual(result["output_lines"], 4)

    def test_trim_preserves_leading_whitespace(self) -> None:
        result = self.tool.execute(mode="trim", text="  keep indent\ndone")
        self.assertEqual(result["result"], "  keep indent\ndone")

    def test_trim_drop_empty_lines(self) -> None:
        result = self.tool.execute(
            mode="trim", text="alpha  \nbeta\t\t\n\ngamma  ", drop_empty=True
        )
        self.assertEqual(result["result"], "alpha\nbeta\ngamma")
        self.assertTrue(result["drop_empty"])
        self.assertEqual(result["lines_dropped"], 1)
        self.assertEqual(result["output_lines"], 3)

    def test_trim_drop_empty_whitespace_only_line(self) -> None:
        # A line of only spaces is empty after stripping, so
        # drop_empty removes it too.
        result = self.tool.execute(
            mode="trim", text="a\n   \nb", drop_empty=True
        )
        self.assertEqual(result["result"], "a\nb")
        self.assertEqual(result["lines_dropped"], 1)

    # ------------------------------------------------------------------ #
    # number mode
    # ------------------------------------------------------------------ #

    def test_number_dot_format_ground_truth(self) -> None:
        result = self.tool.execute(mode="number", text="first\nsecond")
        self.assertEqual(
            result,
            {
                "mode": "number",
                "newline": "lf",
                "input_lines": 2,
                "number_format": "dot",
                "start": 1,
                "pad": 0,
                "output_lines": 2,
                "result": "1. first\n2. second",
            },
        )

    def test_number_paren_format(self) -> None:
        result = self.tool.execute(
            mode="number", text="first\nsecond", number_format="paren"
        )
        self.assertEqual(result["result"], "1) first\n2) second")

    def test_number_custom_start(self) -> None:
        result = self.tool.execute(mode="number", text="a\nb", start=0)
        self.assertEqual(result["result"], "0. a\n1. b")
        self.assertEqual(result["start"], 0)

    def test_number_zero_padding(self) -> None:
        result = self.tool.execute(mode="number", text="a\nb", pad=2)
        self.assertEqual(result["result"], "01. a\n02. b")
        padded_paren = self.tool.execute(
            mode="number", text="x\ny\nz", number_format="paren", start=9, pad=3
        )
        self.assertEqual(
            padded_paren["result"], "009) x\n010) y\n011) z"
        )

    def test_number_grows_beyond_pad_width(self) -> None:
        # zfill never truncates; numbers wider than pad are printed in
        # full.
        result = self.tool.execute(
            mode="number", text="a\nb\nc", start=98, pad=2
        )
        self.assertEqual(result["result"], "98. a\n99. b\n100. c")

    # ------------------------------------------------------------------ #
    # reverse mode
    # ------------------------------------------------------------------ #

    def test_reverse_ground_truth(self) -> None:
        result = self.tool.execute(mode="reverse", text="1\n2\n3")
        self.assertEqual(
            result,
            {
                "mode": "reverse",
                "newline": "lf",
                "input_lines": 3,
                "output_lines": 3,
                "result": "3\n2\n1",
            },
        )

    # ------------------------------------------------------------------ #
    # head / tail modes
    # ------------------------------------------------------------------ #

    def test_head_first_n_with_truncation_flag(self) -> None:
        result = self.tool.execute(mode="head", text=FIVE_LINES, n=2)
        self.assertEqual(
            result,
            {
                "mode": "head",
                "newline": "lf",
                "input_lines": 5,
                "n": 2,
                "truncated": True,
                "output_lines": 2,
                "result": "l1\nl2",
            },
        )

    def test_head_n_equal_to_total_not_truncated(self) -> None:
        result = self.tool.execute(mode="head", text=FIVE_LINES, n=5)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["output_lines"], 5)
        self.assertEqual(result["result"], FIVE_LINES)

    def test_head_n_beyond_total_returns_everything(self) -> None:
        result = self.tool.execute(mode="head", text="a\nb", n=100)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "a\nb")

    def test_head_default_n_is_ten(self) -> None:
        result = self.tool.execute(mode="head", text=FIVE_LINES)
        self.assertEqual(result["n"], 10)
        self.assertEqual(result["result"], FIVE_LINES)
        self.assertFalse(result["truncated"])

    def test_head_string_n_accepted(self) -> None:
        result = self.tool.execute(mode="head", text=FIVE_LINES, n="2")
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["result"], "l1\nl2")

    def test_tail_last_n_preserves_order(self) -> None:
        result = self.tool.execute(mode="tail", text=FIVE_LINES, n=2)
        self.assertEqual(
            result,
            {
                "mode": "tail",
                "newline": "lf",
                "input_lines": 5,
                "n": 2,
                "truncated": True,
                "output_lines": 2,
                "result": "l4\nl5",
            },
        )

    def test_tail_n_beyond_total_returns_everything(self) -> None:
        result = self.tool.execute(mode="tail", text="a\nb\nc", n=10)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["result"], "a\nb\nc")

    # ------------------------------------------------------------------ #
    # CRLF / line-ending handling
    # ------------------------------------------------------------------ #

    def test_crlf_input_normalized_default_lf_output(self) -> None:
        result = self.tool.execute(mode="sort", text="b\r\na\r\n")
        self.assertEqual(result["result"], "a\nb")
        self.assertEqual(result["newline"], "lf")

    def test_newline_crlf_output_joins_with_crlf(self) -> None:
        result = self.tool.execute(
            mode="sort", text="b\r\na\r\n", newline="crlf"
        )
        self.assertEqual(result["result"], "a\r\nb")
        self.assertEqual(result["newline"], "crlf")

    def test_lone_cr_treated_as_line_separator(self) -> None:
        result = self.tool.execute(mode="reverse", text="1\r2\r3")
        self.assertEqual(result["result"], "3\n2\n1")

    def test_trailing_newline_does_not_add_empty_line(self) -> None:
        with_trailing = self.tool.execute(mode="reverse", text="1\n2\n")
        without_trailing = self.tool.execute(mode="reverse", text="1\n2")
        self.assertEqual(with_trailing["input_lines"], 2)
        self.assertEqual(with_trailing["result"], without_trailing["result"])

    def test_single_newline_is_one_empty_line(self) -> None:
        result = self.tool.execute(mode="reverse", text="\n")
        self.assertEqual(result["input_lines"], 1)
        self.assertEqual(result["output_lines"], 1)
        self.assertEqual(result["result"], "")

    def test_crlf_output_with_number_mode(self) -> None:
        result = self.tool.execute(
            mode="number", text="a\nb", newline="crlf"
        )
        self.assertEqual(result["result"], "1. a\r\n2. b")

    # ------------------------------------------------------------------ #
    # Input caps
    # ------------------------------------------------------------------ #

    def test_line_cap_rejects_100001_lines(self) -> None:
        oversized = "\n".join(["x"] * 100_001)
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="sort", text=oversized)
        self.assertIn("100,000-line limit", str(ctx.exception))

    def test_line_cap_accepts_exactly_100000_lines(self) -> None:
        exact = "\n".join(["x"] * 100_000)
        result = self.tool.execute(mode="unique", text=exact)
        self.assertEqual(result["input_lines"], 100_000)
        self.assertEqual(result["output_lines"], 1)
        self.assertEqual(result["result"], "x")

    def test_char_cap_rejects_1000001_chars(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="reverse", text="a" * 1_000_001)
        self.assertIn("1,000,000-character limit", str(ctx.exception))

    def test_char_cap_accepts_exactly_1000000_chars(self) -> None:
        result = self.tool.execute(mode="reverse", text="a" * 1_000_000)
        self.assertEqual(len(result["result"]), 1_000_000)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation matrix)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="sorted", text="a")
        self.assert_invalid(mode="SORT", text="a")
        self.assert_invalid(mode=None, text="a")
        self.assert_invalid(mode=123, text="a")

    def test_invalid_text_type(self) -> None:
        for bad in (None, "", 123, True, b"line", ["line"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="sort", text=bad)
                self.assert_invalid(mode="head", text=bad, n=1)

    def test_invalid_boolean_flags(self) -> None:
        # Boolean options must be real booleans, not truthy values.
        self.assert_invalid(mode="sort", text="a", natural=1)
        self.assert_invalid(mode="sort", text="a", natural="true")
        self.assert_invalid(mode="sort", text="a", case_insensitive=1)
        self.assert_invalid(mode="sort", text="a", case_insensitive="yes")
        self.assert_invalid(mode="sort", text="a", reverse=0)
        self.assert_invalid(mode="sort", text="a", unique="1")
        self.assert_invalid(mode="trim", text="a", drop_empty=1)
        self.assert_invalid(mode="trim", text="a", drop_empty=[True])

    def test_invalid_number_format(self) -> None:
        for bad in ("bullet", "DOT", "dot ", "1", True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="number", text="a", number_format=bad)

    def test_invalid_newline(self) -> None:
        for bad in ("cr", "LF", "auto", 1, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="sort", text="a", newline=bad)

    def test_invalid_n_bounds_and_types(self) -> None:
        for bad in (0, -3, 100_001, 2.5, True, "many"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="head", text=FIVE_LINES, n=bad)
                self.assert_invalid(mode="tail", text=FIVE_LINES, n=bad)

    def test_invalid_start_and_pad(self) -> None:
        for bad in (-1, True, "abc", 1.5):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="number", text="a", start=bad)
        for bad in (-1, 10, "x", True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="number", text="a", pad=bad)

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_sort_deterministic_across_calls(self) -> None:
        text = "file10\nFile2\nfile2\nFILE10\nfile1"
        first = self.tool.execute(
            mode="sort", text=text, natural=True, case_insensitive=True
        )
        for _ in range(5):
            repeat = self.tool.execute(
                mode="sort", text=text, natural=True, case_insensitive=True
            )
            self.assertEqual(first, repeat)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectLineOpsTool, LineOpsTool)
        self.assertEqual(self.tool.name, "line_ops_tool")
        self.assertIn("sort", self.tool.description)
        self.assertIn("head", self.tool.description)
        self.assertEqual(
            LineOpsTool.MODES,
            ("sort", "unique", "trim", "number", "reverse", "head", "tail"),
        )
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("LineOpsTool", __all__)


if __name__ == "__main__":
    unittest.main()
