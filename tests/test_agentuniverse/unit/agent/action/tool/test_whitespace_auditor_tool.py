#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_whitespace_auditor_tool.py

"""Offline unit tests for WhitespaceAuditorTool.

The tool is built purely on the standard library, never touches the
network, and is strictly report-only, so this suite runs fully
offline. Every assertion is deterministic: the ground truths below
are computed BY HAND from the character-level layout of each
hand-crafted sample (offsets are 0-based, line numbers 1-based),
including the dirty corpus that exercises every category, mixed line
endings, invisible spaces (U+00A0 / U+3000 / U+200B), blank-run
counting, BOM, and the locate cap. The suite also pins the two core
guarantees: the input text is never modified, and no text is ever
returned by any mode.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import WhitespaceAuditorTool
from agentuniverse.agent.action.tool.common_tool.whitespace_auditor_tool import (
    WhitespaceAuditorTool as DirectWhitespaceAuditorTool,
)

BOM = "\ufeff"
NBSP = "\u00a0"
IDEO = "\u3000"
ZWSP = "\u200b"

# Hand-crafted dirty corpus. Character map (0-based offsets):
#   0        BOM
#   1-8      "def f():"            line 1, LF at 9
#   10-18    "  x = 1  "           line 2 (leading 2 spaces, trailing 2), LF at 19
#   20-27    "\t y = 2\t"          line 3 (mixed indent \t+' ', trailing \t), LF at 28
#   29-31    three bare LFs        lines 4-6 (blank run of 3)
#   32-40    "print(x)" + NBSP     line 7, NBSP at offset 40, LF at 41
#   42-49    " " + IDEO + "z" + ZWSP + " = 3"
#                                  line 8, IDEO at 43, ZWSP at 45, LF at 50
#   51-55    "line5"               line 9, CRLF at 56-57
#   58-61    "last"                line 10, no terminator
DIRTY = (
    BOM + "def f():\n"
    "  x = 1  \n"
    "\t y = 2\t\n"
    "\n"
    "\n"
    "\n"
    "print(x)" + NBSP + "\n"
    " " + IDEO + "z" + ZWSP + " = 3\n"
    "line5\r\n"
    "last"
)

DIRTY_COUNTS = {
    "trailing_space": 2,
    "leading_space": 2,
    "tabs": 2,
    "mixed_indent": 1,
    "crlf": 1,
    "lf": 8,
    "cr": 0,
    "nbsp": 1,
    "ideographic_space": 1,
    "zero_width_space": 1,
    "blank_run": 1,
}

DIRTY_POSITIONS = {
    "trailing_space": [2, 3],
    "leading_space": [2, 8],
    "tabs": [20, 27],
    "mixed_indent": [3],
    "crlf": [9],
    "lf": [1, 2, 3, 4, 5, 6, 7, 8],
    "cr": [],
    "nbsp": [40],
    "ideographic_space": [43],
    "zero_width_space": [45],
    "blank_run": [4],
}

CLEAN = "hello world\nsecond line\n"

LINE_KINDS = (
    "trailing_space",
    "leading_space",
    "mixed_indent",
    "crlf",
    "lf",
    "cr",
    "blank_run",
)
OFFSET_KINDS = ("tabs", "nbsp", "ideographic_space", "zero_width_space")
ALL_COUNT_CATEGORIES = LINE_KINDS + OFFSET_KINDS


class WhitespaceAuditorToolTest(unittest.TestCase):
    """Offline deterministic test cases for WhitespaceAuditorTool."""

    def setUp(self) -> None:
        self.tool = WhitespaceAuditorTool()

    # ------------------------------------------------------------------ #
    # audit mode — dirty corpus ground truth
    # ------------------------------------------------------------------ #

    def test_audit_dirty_corpus_counts(self) -> None:
        result = self.tool.execute(mode="audit", text=DIRTY)
        self.assertEqual(result["mode"], "audit")
        self.assertEqual(result["text_length"], 62)
        self.assertEqual(result["line_count"], 10)
        self.assertEqual(result["counts"], DIRTY_COUNTS)

    def test_audit_dirty_corpus_flags(self) -> None:
        flags = self.tool.execute(mode="audit", text=DIRTY)["flags"]
        self.assertEqual(
            flags,
            {
                "mixed_line_endings": True,
                "final_newline": False,
                "bom": True,
            },
        )

    def test_audit_dirty_corpus_positions_first_three(self) -> None:
        positions = self.tool.execute(mode="audit", text=DIRTY)["positions"]
        self.assertEqual(set(positions), set(ALL_COUNT_CATEGORIES))
        for category in ALL_COUNT_CATEGORIES:
            expected_kind = "line" if category in LINE_KINDS else "offset"
            self.assertEqual(positions[category]["kind"], expected_kind)
            self.assertEqual(
                positions[category]["first"],
                DIRTY_POSITIONS[category][:3],
                category,
            )

    def test_audit_positions_capped_at_three(self) -> None:
        text = "\n".join(f"l{i} " for i in range(10))
        result = self.tool.execute(mode="audit", text=text)
        self.assertEqual(result["counts"]["trailing_space"], 10)
        self.assertEqual(
            result["positions"]["trailing_space"]["first"], [1, 2, 3]
        )

    def test_audit_dirty_corpus_total_issues(self) -> None:
        result = self.tool.execute(mode="audit", text=DIRTY)
        # 2 trailing + 2 leading + 1 mixed indent + 3 invisible spaces +
        # 1 blank run + mixed endings + missing final newline + BOM.
        self.assertEqual(result["total_issues"], 12)
        self.assertFalse(result["clean"])

    def test_audit_clean_text_all_zeros(self) -> None:
        result = self.tool.execute(mode="audit", text=CLEAN)
        self.assertEqual(
            result["counts"],
            {c: 0 for c in ALL_COUNT_CATEGORIES if c != "lf"}
            | {"lf": 2},
        )
        self.assertEqual(
            result["flags"],
            {
                "mixed_line_endings": False,
                "final_newline": True,
                "bom": False,
            },
        )
        for category in ALL_COUNT_CATEGORIES:
            expected_first = [1, 2] if category == "lf" else []
            self.assertEqual(
                result["positions"][category]["first"], expected_first, category
            )
        self.assertEqual(result["total_issues"], 0)
        self.assertTrue(result["clean"])

    # ------------------------------------------------------------------ #
    # audit mode — line endings, blank runs, special characters
    # ------------------------------------------------------------------ #

    def test_audit_mixed_endings(self) -> None:
        result = self.tool.execute(mode="audit", text="a\r\nb\nc\rd")
        self.assertEqual(result["line_count"], 4)
        self.assertEqual(result["counts"]["crlf"], 1)
        self.assertEqual(result["counts"]["lf"], 1)
        self.assertEqual(result["counts"]["cr"], 1)
        self.assertTrue(result["flags"]["mixed_line_endings"])
        self.assertFalse(result["flags"]["final_newline"])
        self.assertEqual(result["total_issues"], 2)

    def test_audit_cr_only_endings_are_not_an_issue(self) -> None:
        result = self.tool.execute(mode="audit", text="a\rb\rc\r")
        self.assertEqual(result["counts"]["cr"], 3)
        self.assertFalse(result["flags"]["mixed_line_endings"])
        self.assertTrue(result["flags"]["final_newline"])
        self.assertEqual(result["total_issues"], 0)
        self.assertTrue(result["clean"])

    def test_audit_uniform_crlf_is_clean(self) -> None:
        result = self.tool.execute(mode="audit", text="a\r\nb\r\n")
        self.assertEqual(result["counts"]["crlf"], 2)
        self.assertTrue(result["flags"]["final_newline"])
        self.assertEqual(result["total_issues"], 0)
        self.assertTrue(result["clean"])

    def test_audit_final_newline_variants(self) -> None:
        for text in ("a\n", "a\r\n", "a\r"):
            with self.subTest(text=repr(text)):
                self.assertTrue(
                    self.tool.execute(mode="audit", text=text)["flags"][
                        "final_newline"
                    ]
                )
        self.assertFalse(
            self.tool.execute(mode="audit", text="a")["flags"]["final_newline"]
        )

    def test_audit_blank_runs_with_whitespace_only_lines(self) -> None:
        # Blank lines whose content is spaces / tabs still form a run,
        # and each is also a trailing-space line.
        result = self.tool.execute(mode="audit", text="a\n   \n\t\n\nb\n")
        self.assertEqual(result["counts"]["blank_run"], 1)
        self.assertEqual(result["positions"]["blank_run"]["first"], [2])
        self.assertEqual(result["counts"]["trailing_space"], 2)
        self.assertEqual(result["positions"]["trailing_space"]["first"], [2, 3])
        self.assertEqual(result["counts"]["leading_space"], 1)
        self.assertEqual(result["counts"]["tabs"], 1)
        self.assertEqual(result["positions"]["tabs"]["first"], [6])

    def test_audit_two_blank_runs(self) -> None:
        text = "top\r\n\n\n\rmid\n\n\n\nend"
        result = self.tool.execute(mode="audit", text=text)
        self.assertEqual(result["line_count"], 9)
        self.assertEqual(result["counts"]["blank_run"], 2)
        self.assertEqual(result["positions"]["blank_run"]["first"], [2, 6])
        self.assertEqual(result["counts"]["crlf"], 1)
        self.assertEqual(result["counts"]["cr"], 1)
        self.assertEqual(result["counts"]["lf"], 6)
        self.assertTrue(result["flags"]["mixed_line_endings"])

    def test_audit_blank_run_at_end_of_text(self) -> None:
        result = self.tool.execute(mode="audit", text="a\n\n\n\n")
        self.assertEqual(result["counts"]["blank_run"], 1)
        self.assertEqual(result["positions"]["blank_run"]["first"], [2])

    def test_audit_blank_run_requires_three_lines(self) -> None:
        result = self.tool.execute(mode="audit", text="a\n\nb\n")
        self.assertEqual(result["counts"]["blank_run"], 0)

    def test_audit_bom_only_issue(self) -> None:
        result = self.tool.execute(mode="audit", text=BOM + "hi\n")
        self.assertTrue(result["flags"]["bom"])
        self.assertEqual(result["total_issues"], 1)
        self.assertFalse(result["clean"])

    def test_audit_single_line_without_newline(self) -> None:
        result = self.tool.execute(mode="audit", text="hello")
        self.assertEqual(result["line_count"], 1)
        self.assertEqual(result["counts"]["lf"], 0)
        self.assertFalse(result["flags"]["final_newline"])
        self.assertEqual(result["total_issues"], 1)

    def test_audit_tab_inside_line_content(self) -> None:
        result = self.tool.execute(mode="audit", text="a\tb\n")
        self.assertEqual(result["counts"]["tabs"], 1)
        self.assertEqual(result["positions"]["tabs"]["first"], [1])
        self.assertEqual(result["counts"]["leading_space"], 0)
        self.assertEqual(result["counts"]["mixed_indent"], 0)
        self.assertTrue(result["clean"])

    def test_audit_trailing_space_detects_tab_not_nbsp(self) -> None:
        # NBSP at line end is its own category, not trailing_space.
        result = self.tool.execute(mode="audit", text="a \nb\t\nc" + NBSP + "\n")
        self.assertEqual(result["positions"]["trailing_space"]["first"], [1, 2])
        self.assertEqual(result["counts"]["nbsp"], 1)

    def test_audit_leading_space_is_u0020_only(self) -> None:
        result = self.tool.execute(mode="audit", text=" x\n\ty\n")
        self.assertEqual(result["counts"]["leading_space"], 1)
        self.assertEqual(result["positions"]["leading_space"]["first"], [1])

    # ------------------------------------------------------------------ #
    # fix_preview mode — change plan arithmetic
    # ------------------------------------------------------------------ #

    def test_fix_preview_dirty_corpus_change_plan(self) -> None:
        result = self.tool.execute(mode="fix_preview", text=DIRTY)
        self.assertEqual(result["mode"], "fix_preview")
        self.assertEqual(result["text_length"], 62)
        self.assertEqual(result["line_count"], 10)
        self.assertEqual(
            result["changes"],
            {
                "trailing_space": 2,
                "leading_space": 2,
                "tabs": 2,
                "mixed_indent": 1,
                "crlf": 1,
                "lf": 0,
                "cr": 0,
                "mixed_line_endings": 1,
                "nbsp": 1,
                "ideographic_space": 1,
                "zero_width_space": 1,
                "blank_run": 2,
                "final_newline": 1,
                "bom": 1,
            },
        )
        self.assertEqual(result["total_changes"], 16)
        self.assertTrue(result["would_change"])

    def test_fix_preview_matches_audit_counts(self) -> None:
        audit = self.tool.execute(mode="audit", text=DIRTY)
        plan = self.tool.execute(mode="fix_preview", text=DIRTY)
        for category in (
            "trailing_space",
            "leading_space",
            "tabs",
            "mixed_indent",
            "crlf",
            "cr",
            "nbsp",
            "ideographic_space",
            "zero_width_space",
        ):
            self.assertEqual(
                plan["changes"][category],
                audit["counts"][category],
                category,
            )
        self.assertEqual(plan["total_changes"], sum(plan["changes"].values()))

    def test_fix_preview_blank_run_arithmetic(self) -> None:
        # Two runs of 3 blank lines each collapse to one blank line
        # per run: 2 + 2 = 4 blank lines removed.
        text = "a\n\n\n\nb\n\n\n\nc\n"
        plan = self.tool.execute(mode="fix_preview", text=text)
        self.assertEqual(plan["changes"]["blank_run"], 4)
        # A run of 5 blanks (lines 2-6) removes 4 lines.
        plan = self.tool.execute(mode="fix_preview", text="a\n\n\n\n\n\nb\n")
        self.assertEqual(plan["changes"]["blank_run"], 4)
        # A run of exactly 3 removes 2; shorter runs remove nothing.
        plan = self.tool.execute(mode="fix_preview", text="a\n\n\n\nb\n\n c\n")
        self.assertEqual(plan["changes"]["blank_run"], 2)

    def test_fix_preview_clean_text_no_changes(self) -> None:
        plan = self.tool.execute(mode="fix_preview", text=CLEAN)
        self.assertTrue(all(value == 0 for value in plan["changes"].values()))
        self.assertEqual(plan["total_changes"], 0)
        self.assertFalse(plan["would_change"])

    def test_fix_preview_uniform_crlf_converts_without_mixed_flag(self) -> None:
        # Uniform CRLF has no mixed-endings issue, but the LF-target
        # change plan still counts the two ending rewrites.
        plan = self.tool.execute(mode="fix_preview", text="a\r\nb\r\n")
        self.assertEqual(plan["changes"]["crlf"], 2)
        self.assertEqual(plan["changes"]["mixed_line_endings"], 0)
        self.assertEqual(plan["total_changes"], 2)
        self.assertTrue(plan["would_change"])

    def test_fix_preview_tab_conversion_is_a_change_not_an_issue(self) -> None:
        audit = self.tool.execute(mode="audit", text="a\tb\n")
        plan = self.tool.execute(mode="fix_preview", text="a\tb\n")
        self.assertTrue(audit["clean"])
        self.assertEqual(plan["changes"]["tabs"], 1)
        self.assertTrue(plan["would_change"])

    # ------------------------------------------------------------------ #
    # locate mode — full position lists
    # ------------------------------------------------------------------ #

    def test_locate_every_category_on_dirty_corpus(self) -> None:
        for category in ALL_COUNT_CATEGORIES:
            with self.subTest(category=category):
                result = self.tool.execute(
                    mode="locate", text=DIRTY, category=category
                )
                expected = DIRTY_POSITIONS[category]
                self.assertEqual(result["mode"], "locate")
                self.assertEqual(result["category"], category)
                self.assertEqual(
                    result["kind"],
                    "line" if category in LINE_KINDS else "offset",
                )
                self.assertEqual(result["count"], len(expected))
                self.assertEqual(result["returned"], len(expected))
                self.assertFalse(result["truncated"])
                self.assertEqual(result["positions"], expected)

    def test_locate_empty_category_returns_empty_positions(self) -> None:
        result = self.tool.execute(mode="locate", text=DIRTY, category="cr")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["returned"], 0)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["positions"], [])

    def test_locate_cap_at_one_hundred(self) -> None:
        text = "\n".join(f"l{i} " for i in range(150))
        result = self.tool.execute(
            mode="locate", text=text, category="trailing_space"
        )
        self.assertEqual(result["count"], 150)
        self.assertEqual(result["returned"], 100)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["positions"], list(range(1, 101)))

    def test_locate_under_cap_not_truncated(self) -> None:
        text = "\n".join(f"l{i} " for i in range(100))
        result = self.tool.execute(
            mode="locate", text=text, category="trailing_space"
        )
        self.assertEqual(result["count"], 100)
        self.assertEqual(result["returned"], 100)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["positions"], list(range(1, 101)))

    def test_locate_invisible_space_offsets(self) -> None:
        result = self.tool.execute(
            mode="locate", text="a" + NBSP + "b" + NBSP, category="nbsp"
        )
        self.assertEqual(result["kind"], "offset")
        self.assertEqual(result["positions"], [1, 3])

    def test_locate_bom_occupies_offset_zero_but_is_not_counted(self) -> None:
        result = self.tool.execute(
            mode="locate", text=BOM + "a\t", category="tabs"
        )
        self.assertEqual(result["positions"], [2])

    # ------------------------------------------------------------------ #
    # Report-only guarantees: text never modified, never returned
    # ------------------------------------------------------------------ #

    def assert_no_string_value_longer_than(self, value: object, cap: int) -> None:
        if isinstance(value, str):
            self.assertLessEqual(len(value), cap, repr(value[:50]))
        elif isinstance(value, dict):
            for inner in value.values():
                self.assert_no_string_value_longer_than(inner, cap)
        elif isinstance(value, (list, tuple)):
            for inner in value:
                self.assert_no_string_value_longer_than(inner, cap)

    def test_text_never_modified_by_any_mode(self) -> None:
        snapshot = DIRTY
        for mode in ("audit", "fix_preview"):
            self.tool.execute(mode=mode, text=DIRTY)
            self.assertEqual(DIRTY, snapshot)
        for category in ALL_COUNT_CATEGORIES:
            self.tool.execute(mode="locate", text=DIRTY, category=category)
            self.assertEqual(DIRTY, snapshot)

    def test_no_text_returned_by_any_mode(self) -> None:
        for mode in ("audit", "fix_preview"):
            result = self.tool.execute(mode=mode, text=DIRTY)
            self.assertNotIn("text", result)
            # DIRTY is 62 chars; no returned string may exceed 20 chars,
            # so no slice of the input can leak out either.
            self.assert_no_string_value_longer_than(result, 20)
        result = self.tool.execute(mode="locate", text=DIRTY, category="tabs")
        self.assertNotIn("text", result)
        self.assert_no_string_value_longer_than(result, 20)

    def test_results_are_deterministic(self) -> None:
        for mode in ("audit", "fix_preview"):
            first = self.tool.execute(mode=mode, text=DIRTY)
            second = self.tool.execute(mode=mode, text=DIRTY)
            self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="scan", text="a\n")
        self.assert_invalid(mode=None, text="a\n")
        self.assert_invalid(mode=123, text="a\n")
        self.assert_invalid(mode="AUDIT", text="a\n")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="audit", text=bad)
                self.assert_invalid(mode="fix_preview", text=bad)
                self.assert_invalid(mode="locate", text=bad, category="tabs")

    def test_empty_text_rejected(self) -> None:
        for mode in ("audit", "fix_preview", "locate"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, text="")

    def test_text_length_limit(self) -> None:
        oversized = "a" * 100_001
        self.assert_invalid(mode="audit", text=oversized)
        self.assert_invalid(mode="fix_preview", text=oversized)
        self.assert_invalid(mode="locate", text=oversized, category="tabs")
        ok = self.tool.execute(mode="audit", text="a\n" * 50_000)
        self.assertEqual(ok["text_length"], 100_000)
        self.assertTrue(ok["clean"])

    def test_locate_requires_category(self) -> None:
        self.assert_invalid(mode="locate", text=DIRTY)
        self.assert_invalid(mode="locate", text=DIRTY, category="")
        self.assert_invalid(mode="locate", text=DIRTY, category=123)
        self.assert_invalid(mode="locate", text=DIRTY, category=True)
        self.assert_invalid(mode="locate", text=DIRTY, category=["tabs"])

    def test_locate_unknown_category(self) -> None:
        for bad in ("bogus", "trailing", "whitespace", "TAB"):
            with self.subTest(category=bad):
                self.assert_invalid(mode="locate", text=DIRTY, category=bad)

    def test_locate_flags_are_not_locatable(self) -> None:
        # The three boolean flags carry no positions.
        for flag in ("mixed_line_endings", "final_newline", "bom"):
            with self.subTest(flag=flag):
                with self.assertRaises(ValueError) as raised:
                    self.tool.execute(
                        mode="locate", text=DIRTY, category=flag
                    )
                self.assertIn("flag", str(raised.exception))

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectWhitespaceAuditorTool, WhitespaceAuditorTool)
        self.assertEqual(self.tool.name, "whitespace_auditor_tool")
        self.assertIn("report-only", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("WhitespaceAuditorTool", __all__)


if __name__ == "__main__":
    unittest.main()
