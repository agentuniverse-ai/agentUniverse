#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_bracket_balance_tool.py

"""Offline unit tests for BracketBalanceTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: balanced / mismatched / orphan cases are checked
against hand-computed ground truths with exact positions, lines and
columns, quote inertness and escaped quotes against literal expected
scans, CJK full-width brackets as their own pair types, the angle
bracket generics heuristic in both option states, the fix modes
against exact repaired outputs, and the stats / depth profiles against
exact dictionaries. A closing error matrix covers every error kind.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import BracketBalanceTool
from agentuniverse.agent.action.tool.common_tool.bracket_balance_tool import (
    BracketBalanceTool as DirectBracketBalanceTool,
)

PER_TYPE_SIX = {
    "()": {"open": 0, "close": 0},
    "[]": {"open": 0, "close": 0},
    "{}": {"open": 0, "close": 0},
    "（）": {"open": 0, "close": 0},
    "【】": {"open": 0, "close": 0},
    "《》": {"open": 0, "close": 0},
}


class BracketBalanceToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib BracketBalanceTool."""

    def setUp(self) -> None:
        self.tool = BracketBalanceTool()

    # ------------------------------------------------------------------ #
    # check mode — balanced ground truths
    # ------------------------------------------------------------------ #

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(BracketBalanceTool, DirectBracketBalanceTool)

    def test_check_balanced_full_result(self) -> None:
        # "hello (world) [x] {y}"
        # ( @6 ) @12 [ @14 ] @16 { @18 } @20
        result = self.tool.execute(mode="check", text="hello (world) [x] {y}")
        self.assertEqual(
            result,
            {
                "mode": "check",
                "string_aware": True,
                "angle_brackets": False,
                "balanced": True,
                "error_count": 0,
                "first_error": None,
                "per_type": {
                    "()": {"open": 1, "close": 1},
                    "[]": {"open": 1, "close": 1},
                    "{}": {"open": 1, "close": 1},
                    "（）": {"open": 0, "close": 0},
                    "【】": {"open": 0, "close": 0},
                    "《》": {"open": 0, "close": 0},
                },
                "stack_depth_max": 1,
            },
        )

    def test_check_nested_depth(self) -> None:
        result = self.tool.execute(mode="check", text="([{a}])")
        self.assertTrue(result["balanced"])
        self.assertEqual(result["stack_depth_max"], 3)
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 1})
        self.assertEqual(result["per_type"]["[]"], {"open": 1, "close": 1})
        self.assertEqual(result["per_type"]["{}"], {"open": 1, "close": 1})

    def test_check_plain_text_without_brackets(self) -> None:
        result = self.tool.execute(mode="check", text="no delimiters here")
        self.assertTrue(result["balanced"])
        self.assertIsNone(result["first_error"])
        self.assertEqual(result["per_type"], PER_TYPE_SIX)
        self.assertEqual(result["stack_depth_max"], 0)

    # ------------------------------------------------------------------ #
    # check mode — error ground truths (exact position / line / col)
    # ------------------------------------------------------------------ #

    def test_check_unmatched_open(self) -> None:
        # "def f(" — the "(" sits at index 5 (line 1, col 6).
        result = self.tool.execute(mode="check", text="def f(")
        self.assertFalse(result["balanced"])
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(
            result["first_error"],
            {
                "position": 5,
                "line": 1,
                "col": 6,
                "kind": "unmatched_open",
                "expected": ")",
            },
        )
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 0})

    def test_check_unmatched_close(self) -> None:
        # "ab)" — the ")" sits at index 2 (line 1, col 3).
        result = self.tool.execute(mode="check", text="ab)")
        self.assertFalse(result["balanced"])
        self.assertEqual(
            result["first_error"],
            {
                "position": 2,
                "line": 1,
                "col": 3,
                "kind": "unmatched_close",
                "found": ")",
            },
        )
        self.assertEqual(result["per_type"]["()"], {"open": 0, "close": 1})

    def test_check_mismatched_pair_full_result(self) -> None:
        # "(a]" — the "]" at index 2 mismatches the "(" at index 0; the
        # unmatched "(" is a second error reported after the mismatch.
        result = self.tool.execute(mode="check", text="(a]")
        self.assertEqual(
            result,
            {
                "mode": "check",
                "string_aware": True,
                "angle_brackets": False,
                "balanced": False,
                "error_count": 2,
                "first_error": {
                    "position": 2,
                    "line": 1,
                    "col": 3,
                    "kind": "mismatched_pair",
                    "expected": ")",
                    "found": "]",
                },
                "per_type": {
                    "()": {"open": 1, "close": 0},
                    "[]": {"open": 0, "close": 1},
                    "{}": {"open": 0, "close": 0},
                    "（）": {"open": 0, "close": 0},
                    "【】": {"open": 0, "close": 0},
                    "《》": {"open": 0, "close": 0},
                },
                "stack_depth_max": 1,
            },
        )

    def test_check_multiline_exact_line_and_col(self) -> None:
        # line 1: "line1\n" (newline at 5)
        # line 2: "  (ok\n" — "(" at 8 (line 2, col 3), newline at 11
        # line 3: "line3 ] done" — "]" at 18 (line 3, col 7)
        text = "line1\n  (ok\nline3 ] done"
        result = self.tool.execute(mode="check", text=text)
        self.assertEqual(result["error_count"], 2)
        self.assertEqual(
            result["first_error"],
            {
                "position": 18,
                "line": 3,
                "col": 7,
                "kind": "mismatched_pair",
                "expected": ")",
                "found": "]",
            },
        )

    def test_check_crlf_line_and_col(self) -> None:
        # "a\r\n)" — the ")" is at index 3, after the newline at 2.
        result = self.tool.execute(mode="check", text="a\r\n)")
        self.assertEqual(
            result["first_error"],
            {
                "position": 3,
                "line": 2,
                "col": 1,
                "kind": "unmatched_close",
                "found": ")",
            },
        )

    def test_check_first_error_is_first_encountered(self) -> None:
        # "([)" — the ")" at index 2 mismatches first (scan order);
        # the two unmatched openers only surface at end of text.
        result = self.tool.execute(mode="check", text="([)")
        self.assertEqual(result["error_count"], 3)
        self.assertEqual(result["first_error"]["kind"], "mismatched_pair")
        self.assertEqual(result["first_error"]["position"], 2)

    def test_check_error_matrix(self) -> None:
        cases = [
            # (text, kind, position, expected, found)
            ("(", "unmatched_open", 0, ")", None),
            ("}", "unmatched_close", 0, None, "}"),
            ("{]", "mismatched_pair", 1, "}", "]"),
            ("《)", "mismatched_pair", 1, "》", ")"),
            ("]", "unmatched_close", 0, None, "]"),
            ("【", "unmatched_open", 0, "】", None),
        ]
        for text, kind, position, expected, found in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="check", text=text)
                error = result["first_error"]
                self.assertFalse(result["balanced"])
                self.assertEqual(error["kind"], kind)
                self.assertEqual(error["position"], position)
                self.assertEqual(error.get("expected"), expected)
                self.assertEqual(error.get("found"), found)

    # ------------------------------------------------------------------ #
    # quote handling (string-aware mode)
    # ------------------------------------------------------------------ #

    def test_brackets_inside_quotes_are_inert(self) -> None:
        # The "]" inside the double-quoted span never counts.
        result = self.tool.execute(mode="check", text='("unbalanced ]" )')
        self.assertTrue(result["balanced"])
        self.assertIsNone(result["first_error"])
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 1})
        self.assertEqual(result["per_type"]["[]"], {"open": 0, "close": 0})

    def test_escaped_quote_does_not_close_the_span(self) -> None:
        # 'a\'b — the backslash escapes the inner quote; the span
        # closes at the final apostrophe, so the parens match.
        result = self.tool.execute(mode="check", text="x = 'a\\'b' + (1)")
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 1})

    def test_backtick_span_makes_brackets_inert(self) -> None:
        result = self.tool.execute(mode="check", text="`[inert(`")
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"], PER_TYPE_SIX)
        self.assertEqual(result["stack_depth_max"], 0)

    def test_mismatched_closing_quote_is_an_error(self) -> None:
        # "abc' — the apostrophe does not close the double-quoted span,
        # so the span runs to end of text: unterminated_string reported
        # at the opening quote (position 0).
        result = self.tool.execute(mode="check", text='"abc\'')
        self.assertFalse(result["balanced"])
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(
            result["first_error"],
            {
                "position": 0,
                "line": 1,
                "col": 1,
                "kind": "unterminated_string",
                "quote": '"',
            },
        )

    def test_quote_span_across_newlines(self) -> None:
        result = self.tool.execute(
            mode="check", text='a = ("[multi\nline]")'
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["[]"], {"open": 0, "close": 0})

    def test_string_aware_false_counts_every_bracket(self) -> None:
        # 'x = "((" y' — the parens are inert inside the quoted span
        # by default, but count as unmatched openers when the option
        # is turned off.
        balanced = self.tool.execute(mode="check", text='x = "((" y')
        self.assertTrue(balanced["balanced"])
        self.assertEqual(balanced["per_type"]["()"], {"open": 0, "close": 0})

        plain = self.tool.execute(
            mode="check", text='x = "((" y', string_aware=False
        )
        self.assertFalse(plain["balanced"])
        self.assertEqual(plain["error_count"], 2)
        self.assertEqual(
            plain["first_error"],
            {
                "position": 6,
                "line": 1,
                "col": 7,
                "kind": "unmatched_open",
                "expected": ")",
            },
        )
        self.assertEqual(plain["per_type"]["()"], {"open": 2, "close": 0})
        self.assertEqual(plain["stack_depth_max"], 2)

    # ------------------------------------------------------------------ #
    # CJK full-width brackets
    # ------------------------------------------------------------------ #

    def test_cjk_brackets_are_own_pair_types(self) -> None:
        result = self.tool.execute(mode="check", text="函数（参数【注】）")
        self.assertTrue(result["balanced"])
        self.assertEqual(
            result["per_type"]["（）"], {"open": 1, "close": 1}
        )
        self.assertEqual(
            result["per_type"]["【】"], {"open": 1, "close": 1}
        )
        self.assertEqual(result["stack_depth_max"], 2)

    def test_cjk_bracket_mismatch(self) -> None:
        result = self.tool.execute(mode="check", text="（】")
        self.assertEqual(
            result["first_error"],
            {
                "position": 1,
                "line": 1,
                "col": 2,
                "kind": "mismatched_pair",
                "expected": "）",
                "found": "】",
            },
        )

    def test_cjk_bracket_never_matches_ascii(self) -> None:
        # （ closed by ) is a mismatch, not a match.
        result = self.tool.execute(mode="check", text="（a)")
        self.assertFalse(result["balanced"])
        self.assertEqual(result["first_error"]["kind"], "mismatched_pair")
        self.assertEqual(result["first_error"]["expected"], "）")
        self.assertEqual(result["first_error"]["found"], ")")

    # ------------------------------------------------------------------ #
    # angle brackets (generics heuristic, off by default)
    # ------------------------------------------------------------------ #

    def test_angle_brackets_off_by_default(self) -> None:
        result = self.tool.execute(mode="check", text="List<Integer>")
        self.assertTrue(result["balanced"])
        self.assertNotIn("<>", result["per_type"])

    def test_angle_brackets_generics_match_when_enabled(self) -> None:
        result = self.tool.execute(
            mode="check", text="List<Integer>", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 1, "close": 1})

    def test_angle_bracket_heuristic_a_b_c(self) -> None:
        result = self.tool.execute(
            mode="check", text="a<b>c", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 1, "close": 1})

    def test_angle_bracket_spaced_comparison_stays_inert(self) -> None:
        result = self.tool.execute(
            mode="check", text="a < b and c > d", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 0, "close": 0})

    def test_angle_bracket_comparison_inside_parens_stays_inert(self) -> None:
        # The ">" follows a word character, but the innermost open
        # bracket is "(", not "<" — so it stays inert.
        result = self.tool.execute(
            mode="check", text="if (x > 2)", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 0, "close": 0})
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 1})

    def test_angle_bracket_at_start_of_text_stays_inert(self) -> None:
        result = self.tool.execute(
            mode="check", text="<start>", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 0, "close": 0})

    def test_angle_bracket_nested_generics(self) -> None:
        result = self.tool.execute(
            mode="check", text="List<List<int>>", angle_brackets=True
        )
        self.assertTrue(result["balanced"])
        self.assertEqual(result["per_type"]["<>"], {"open": 2, "close": 2})

    # ------------------------------------------------------------------ #
    # locate mode
    # ------------------------------------------------------------------ #

    def test_locate_lists_all_positions_sorted(self) -> None:
        # "(] ) (" — mismatched "]" at 1, unmatched "(" at 5.
        result = self.tool.execute(mode="locate", text="(] ) (")
        self.assertFalse(result["balanced"])
        self.assertEqual(result["total"], 2)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["cap"], 100)
        self.assertEqual(
            result["positions"],
            [
                {
                    "position": 1,
                    "line": 1,
                    "col": 2,
                    "kind": "mismatched_pair",
                    "expected": ")",
                    "found": "]",
                },
                {
                    "position": 5,
                    "line": 1,
                    "col": 6,
                    "kind": "unmatched_open",
                    "expected": ")",
                },
            ],
        )

    def test_locate_balanced_text(self) -> None:
        result = self.tool.execute(mode="locate", text="ok (fine)")
        self.assertTrue(result["balanced"])
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["positions"], [])

    def test_locate_caps_at_one_hundred(self) -> None:
        result = self.tool.execute(mode="locate", text=")" * 150)
        self.assertEqual(result["total"], 150)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["positions"]), 100)
        self.assertEqual(result["positions"][0]["position"], 0)
        self.assertEqual(result["positions"][-1]["position"], 99)
        for entry in result["positions"]:
            self.assertEqual(entry["kind"], "unmatched_close")
            self.assertEqual(entry["found"], ")")

    # ------------------------------------------------------------------ #
    # fix mode
    # ------------------------------------------------------------------ #

    def test_fix_append_missing_closers_innermost_first(self) -> None:
        result = self.tool.execute(
            mode="fix",
            text="[({",
            fix_modes=["append_missing_closers"],
        )
        self.assertEqual(result["fixed_text"], "[({})]")
        self.assertTrue(result["balanced_after_fix"])
        self.assertEqual(
            result["applied"],
            [
                {"action": "appended_closer", "position": 3, "char": "}"},
                {"action": "appended_closer", "position": 4, "char": ")"},
                {"action": "appended_closer", "position": 5, "char": "]"},
            ],
        )
        self.assertEqual(result["applied_count"], 3)

    def test_fix_drop_orphans_only(self) -> None:
        result = self.tool.execute(
            mode="fix", text="a)b(c", fix_modes=["drop_orphans"]
        )
        self.assertEqual(result["fixed_text"], "ab(c")
        self.assertEqual(
            result["applied"],
            [
                {
                    "action": "dropped_closer",
                    "position": 1,
                    "line": 1,
                    "col": 2,
                    "char": ")",
                }
            ],
        )
        self.assertFalse(result["balanced_after_fix"])
        self.assertEqual(result["remaining_error_count"], 1)

    def test_fix_default_applies_drop_then_append(self) -> None:
        result = self.tool.execute(mode="fix", text="a)b(c")
        self.assertEqual(result["fix_modes"], ["drop_orphans", "append_missing_closers"])
        self.assertEqual(result["fixed_text"], "ab(c)")
        self.assertTrue(result["balanced_after_fix"])
        self.assertEqual(result["remaining_error_count"], 0)
        self.assertEqual(result["applied_count"], 2)
        self.assertEqual(result["applied"][0]["action"], "dropped_closer")
        self.assertEqual(result["applied"][0]["position"], 1)
        self.assertEqual(result["applied"][1]["action"], "appended_closer")
        self.assertEqual(result["applied"][1]["char"], ")")

    def test_fix_mismatched_closer_is_dropped_then_closer_appended(self) -> None:
        # "(]" — the "]" at index 1 is an unmatched closer (dropped),
        # the "(" at index 0 is an unmatched opener (closed).
        result = self.tool.execute(mode="fix", text="(]")
        self.assertEqual(result["fixed_text"], "()")
        self.assertTrue(result["balanced_after_fix"])
        self.assertEqual(
            result["applied"],
            [
                {
                    "action": "dropped_closer",
                    "position": 1,
                    "line": 1,
                    "col": 2,
                    "char": "]",
                },
                {"action": "appended_closer", "position": 1, "char": ")"},
            ],
        )

    def test_fix_balanced_text_is_unchanged(self) -> None:
        result = self.tool.execute(mode="fix", text="(a)")
        self.assertEqual(result["fixed_text"], "(a)")
        self.assertEqual(result["applied"], [])
        self.assertEqual(result["applied_count"], 0)
        self.assertTrue(result["balanced_after_fix"])

    def test_fix_cannot_repair_unterminated_string(self) -> None:
        result = self.tool.execute(mode="fix", text='"abc')
        self.assertEqual(result["fixed_text"], '"abc')
        self.assertEqual(result["applied"], [])
        self.assertFalse(result["balanced_after_fix"])
        self.assertEqual(result["remaining_error_count"], 1)

    def test_fix_modes_duplicates_are_deduplicated(self) -> None:
        result = self.tool.execute(
            mode="fix",
            text="(",
            fix_modes=["append_missing_closers", "append_missing_closers"],
        )
        self.assertEqual(result["fix_modes"], ["append_missing_closers"])
        self.assertEqual(result["fixed_text"], "()")

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def test_stats_exact_profile(self) -> None:
        # "(([[]]))" — two of each, overall nesting depth four.
        result = self.tool.execute(mode="stats", text="(([[]]))")
        self.assertEqual(
            result,
            {
                "mode": "stats",
                "string_aware": True,
                "angle_brackets": False,
                "chars": 8,
                "lines": 1,
                "per_type": {
                    "()": {"open": 2, "close": 2, "max_depth": 2},
                    "[]": {"open": 2, "close": 2, "max_depth": 2},
                    "{}": {"open": 0, "close": 0, "max_depth": 0},
                    "（）": {"open": 0, "close": 0, "max_depth": 0},
                    "【】": {"open": 0, "close": 0, "max_depth": 0},
                    "《》": {"open": 0, "close": 0, "max_depth": 0},
                },
                "overall": {"open": 4, "close": 4, "max_depth": 4},
            },
        )

    def test_stats_lines_and_cjk(self) -> None:
        result = self.tool.execute(
            mode="stats", text="（【\n】）"
        )
        self.assertEqual(result["chars"], 5)
        self.assertEqual(result["lines"], 2)
        self.assertEqual(
            result["per_type"]["（）"],
            {"open": 1, "close": 1, "max_depth": 1},
        )
        self.assertEqual(
            result["per_type"]["【】"],
            {"open": 1, "close": 1, "max_depth": 1},
        )
        self.assertEqual(result["overall"], {"open": 2, "close": 2, "max_depth": 2})

    def test_stats_per_type_max_depth_independent(self) -> None:
        # "(()[])" — "()" nests two deep while "[]" stays one deep;
        # the overall stack peaks at two brackets at once.
        result = self.tool.execute(mode="stats", text="(()[])")
        self.assertEqual(
            result["per_type"]["()"], {"open": 2, "close": 2, "max_depth": 2}
        )
        self.assertEqual(
            result["per_type"]["[]"], {"open": 1, "close": 1, "max_depth": 1}
        )
        self.assertEqual(
            result["overall"], {"open": 3, "close": 3, "max_depth": 2}
        )

    def test_stats_quotes_do_not_count(self) -> None:
        result = self.tool.execute(mode="stats", text='x = ("[") y')
        self.assertEqual(result["per_type"]["[]"], {"open": 0, "close": 0, "max_depth": 0})
        self.assertEqual(result["per_type"]["()"], {"open": 1, "close": 1, "max_depth": 1})

    # ------------------------------------------------------------------ #
    # input validation (strict, raises before any computation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="zap", text="x")
        with self.assertRaises(ValueError):
            self.tool.execute(text="(())")

    def test_invalid_text_raises(self) -> None:
        for bad in (None, 123, "", ["("], True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="check", text=bad)

    def test_oversized_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="check", text="(" * 100_001)

    def test_non_boolean_flags_raise(self) -> None:
        for bad in ("yes", 1, 0, [True]):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="check", text="x", string_aware=bad
                    )
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="check", text="x", angle_brackets=bad
                    )

    def test_invalid_fix_modes_raise(self) -> None:
        # fix_modes is only valid for mode='fix'.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="check", text="x", fix_modes=["drop_orphans"])
        # A bare string must not be char-iterated silently.
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix", text="x", fix_modes="drop_orphans")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix", text="x", fix_modes=["bogus"])
        with self.assertRaises(ValueError):
            self.tool.execute(mode="fix", text="x", fix_modes=42)

    # ------------------------------------------------------------------ #
    # determinism
    # ------------------------------------------------------------------ #

    def test_results_are_deterministic(self) -> None:
        for mode in ("check", "locate", "fix", "stats"):
            first = self.tool.execute(
                mode=mode, text="a (b [c] 'd' {e}<f>) ]", angle_brackets=True
            )
            second = self.tool.execute(
                mode=mode, text="a (b [c] 'd' {e}<f>) ]", angle_brackets=True
            )
            self.assertEqual(first, second, mode)


if __name__ == "__main__":
    unittest.main()
