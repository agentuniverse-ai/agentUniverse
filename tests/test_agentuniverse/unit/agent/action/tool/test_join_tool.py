#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_join_tool.py

"""Offline unit tests for JoinTool.

The tool is built purely on the standard library (string methods plus
``math.isfinite``) and never touches the network, so this suite runs
fully offline. Every assertion is deterministic: the join mode is
checked against literal ground-truth outputs for every style at 0, 1,
2, 3 and 5 items (including the oxford two-item no-comma rule and the
``and`` style without the final comma), drop_empty interactions are
pinned down end to end, both join_pairs input shapes and the int/bool
coercion rule are covered, numbered/bullet formatting is verified
with custom starts and bullet characters, and the validation matrix
covers every malformed parameter the tool rejects with ``ValueError``.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import JoinTool
from agentuniverse.agent.action.tool.common_tool.join_tool import (
    JoinTool as DirectJoinTool,
)

EMPTY_NOTE = "(no items to join)"
FIVE = ["a", "b", "c", "d", "e"]


class JoinToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib JoinTool."""

    def setUp(self) -> None:
        self.tool = JoinTool()

    # ------------------------------------------------------------------ #
    # join mode — plain style ground truths across item counts
    # ------------------------------------------------------------------ #

    def test_join_plain_ground_truth_dict(self) -> None:
        result = self.tool.execute(mode="join", items=["a", "b", "c"])
        self.assertEqual(
            result,
            {
                "mode": "join",
                "style": "plain",
                "delimiter": ", ",
                "drop_empty": False,
                "input_items": 3,
                "items_dropped": 0,
                "output_items": 3,
                "result": "a, b, c",
            },
        )

    def test_join_plain_counts_matrix(self) -> None:
        cases = {
            0: EMPTY_NOTE,
            1: "a",
            2: "a, b",
            3: "a, b, c",
            5: "a, b, c, d, e",
        }
        for count, expected in cases.items():
            with self.subTest(count=count):
                result = self.tool.execute(mode="join", items=FIVE[:count])
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["input_items"], count)
                self.assertEqual(result["output_items"], count)

    # ------------------------------------------------------------------ #
    # join mode — oxford style (a, b, and c)
    # ------------------------------------------------------------------ #

    def test_join_oxford_counts_matrix(self) -> None:
        cases = {
            0: EMPTY_NOTE,
            1: "a",
            2: "a and b",
            3: "a, b, and c",
            5: "a, b, c, d, and e",
        }
        for count, expected in cases.items():
            with self.subTest(count=count):
                result = self.tool.execute(
                    mode="join", items=FIVE[:count], style="oxford"
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["style"], "oxford")

    def test_join_oxford_two_items_have_no_comma(self) -> None:
        # The standard short form: exactly two items never take a
        # comma before the conjunction.
        result = self.tool.execute(mode="join", items=["x", "y"], style="oxford")
        self.assertEqual(result["result"], "x and y")
        self.assertNotIn(",", result["result"])

    def test_join_oxford_single_item_ignores_style(self) -> None:
        result = self.tool.execute(mode="join", items=["solo"], style="oxford")
        self.assertEqual(result["result"], "solo")
        self.assertEqual(result["output_items"], 1)

    # ------------------------------------------------------------------ #
    # join mode — and style (documented without the final comma)
    # ------------------------------------------------------------------ #

    def test_join_and_counts_matrix(self) -> None:
        cases = {
            0: EMPTY_NOTE,
            1: "a",
            2: "a and b",
            3: "a, b and c",
            5: "a, b, c, d and e",
        }
        for count, expected in cases.items():
            with self.subTest(count=count):
                result = self.tool.execute(
                    mode="join", items=FIVE[:count], style="and"
                )
                self.assertEqual(result["result"], expected)

    def test_join_and_three_items_no_final_comma(self) -> None:
        result = self.tool.execute(
            mode="join", items=["a", "b", "c"], style="and"
        )
        self.assertEqual(result["result"], "a, b and c")
        self.assertNotIn("and,", result["result"])

    # ------------------------------------------------------------------ #
    # join mode — or style (a, b, or c)
    # ------------------------------------------------------------------ #

    def test_join_or_counts_matrix(self) -> None:
        cases = {
            0: EMPTY_NOTE,
            1: "a",
            2: "a or b",
            3: "a, b, or c",
            5: "a, b, c, d, or e",
        }
        for count, expected in cases.items():
            with self.subTest(count=count):
                result = self.tool.execute(
                    mode="join", items=FIVE[:count], style="or"
                )
                self.assertEqual(result["result"], expected)

    # ------------------------------------------------------------------ #
    # join mode — custom delimiters
    # ------------------------------------------------------------------ #

    def test_join_custom_delimiter_every_style(self) -> None:
        cases = {
            "plain": "a; b; c",
            "oxford": "a; b; and c",
            "and": "a; b and c",
            "or": "a; b; or c",
        }
        for style, expected in cases.items():
            with self.subTest(style=style):
                result = self.tool.execute(
                    mode="join",
                    items=["a", "b", "c"],
                    delimiter="; ",
                    style=style,
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["delimiter"], "; ")

    def test_join_empty_delimiter_allowed_for_single_item(self) -> None:
        result = self.tool.execute(mode="join", items=["only"], delimiter="")
        self.assertEqual(result["result"], "only")
        self.assertEqual(result["delimiter"], "")

    def test_join_empty_delimiter_allowed_for_empty_list(self) -> None:
        result = self.tool.execute(mode="join", items=[], delimiter="")
        self.assertEqual(result["result"], EMPTY_NOTE)

    def test_join_empty_delimiter_rejected_for_two_items(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="join", items=["a", "b"], delimiter="")
        self.assertIn("delimiter must be a non-empty string", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # join mode — empty-string items and drop_empty
    # ------------------------------------------------------------------ #

    def test_join_keeps_empty_strings_by_default(self) -> None:
        result = self.tool.execute(mode="join", items=["a", "", "b"])
        self.assertEqual(result["result"], "a, , b")
        self.assertEqual(result["items_dropped"], 0)
        self.assertFalse(result["drop_empty"])

    def test_join_keeps_empty_string_with_oxford_by_default(self) -> None:
        # Ugly but documented: empty strings are items like any other
        # until drop_empty is asked for.
        result = self.tool.execute(
            mode="join", items=["a", "", "b"], style="oxford"
        )
        self.assertEqual(result["result"], "a, , and b")

    def test_join_drop_empty_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="join", items=["a", "", "b"], drop_empty=True
        )
        self.assertEqual(
            result,
            {
                "mode": "join",
                "style": "plain",
                "delimiter": ", ",
                "drop_empty": True,
                "input_items": 3,
                "items_dropped": 1,
                "output_items": 2,
                "result": "a, b",
            },
        )

    def test_join_drop_empty_then_oxford_two_items(self) -> None:
        # ["a", "", "b"] drops to two items, and the oxford short
        # form kicks in without a comma.
        result = self.tool.execute(
            mode="join", items=["a", "", "b"], style="oxford", drop_empty=True
        )
        self.assertEqual(result["result"], "a and b")
        self.assertEqual(result["items_dropped"], 1)

    def test_join_drop_empty_to_single_item(self) -> None:
        result = self.tool.execute(
            mode="join", items=["a", "", ""], drop_empty=True
        )
        self.assertEqual(result["result"], "a")
        self.assertEqual(result["items_dropped"], 2)
        self.assertEqual(result["output_items"], 1)

    def test_join_drop_empty_all_items_yields_note(self) -> None:
        result = self.tool.execute(
            mode="join", items=["", "", ""], drop_empty=True
        )
        self.assertEqual(result["result"], EMPTY_NOTE)
        self.assertEqual(result["items_dropped"], 3)
        self.assertEqual(result["output_items"], 0)

    def test_join_drop_empty_all_items_with_empty_as_empty(self) -> None:
        result = self.tool.execute(
            mode="join", items=["", ""], drop_empty=True, empty_as="empty"
        )
        self.assertEqual(result["result"], "")
        self.assertEqual(result["output_items"], 0)

    def test_join_drop_empty_leaves_two_items_rejects_empty_delimiter(self):
        # The delimiter emptiness rule applies to the items that
        # remain after drop_empty, not to the raw input.
        with self.assertRaises(ValueError):
            self.tool.execute(
                mode="join",
                items=["a", "", "b"],
                delimiter="",
                drop_empty=True,
            )

    # ------------------------------------------------------------------ #
    # empty list handling — every style and mode
    # ------------------------------------------------------------------ #

    def test_empty_list_note_for_every_style(self) -> None:
        for style in ("plain", "oxford", "and", "or"):
            with self.subTest(style=style):
                result = self.tool.execute(
                    mode="join", items=[], style=style
                )
                self.assertEqual(result["result"], EMPTY_NOTE)
                self.assertEqual(result["output_items"], 0)

    def test_empty_list_empty_string_per_option(self) -> None:
        for style in ("plain", "oxford", "and", "or"):
            with self.subTest(style=style):
                result = self.tool.execute(
                    mode="join", items=[], style=style, empty_as="empty"
                )
                self.assertEqual(result["result"], "")
                self.assertEqual(result["output_items"], 0)

    def test_empty_list_note_for_every_mode(self) -> None:
        calls = {
            "join": {"items": []},
            "join_pairs": {"items": []},
            "numbered": {"items": []},
            "bullet": {"items": []},
        }
        for mode, kwargs in calls.items():
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, **kwargs)
                self.assertEqual(result["result"], EMPTY_NOTE)
                self.assertEqual(result["output_items"], 0)

    def test_empty_list_empty_string_for_every_mode(self) -> None:
        calls = {
            "join": {"items": []},
            "join_pairs": {"items": []},
            "numbered": {"items": []},
            "bullet": {"items": []},
        }
        for mode, kwargs in calls.items():
            with self.subTest(mode=mode):
                result = self.tool.execute(
                    mode=mode, empty_as="empty", **kwargs
                )
                self.assertEqual(result["result"], "")

    # ------------------------------------------------------------------ #
    # scalar coercion (documented rule)
    # ------------------------------------------------------------------ #

    def test_join_coerces_ints_floats_bools(self) -> None:
        result = self.tool.execute(
            mode="join", items=["a", 1, 2.5, True, False]
        )
        self.assertEqual(result["result"], "a, 1, 2.5, true, false")

    def test_join_coerces_negative_int_and_integral_float(self) -> None:
        result = self.tool.execute(mode="join", items=[-3, 2.0])
        self.assertEqual(result["result"], "-3, 2.0")

    def test_join_rejects_non_finite_floats(self) -> None:
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(mode="join", items=[bad])
                self.assertIn("finite float", str(ctx.exception))

    # ------------------------------------------------------------------ #
    # join_pairs mode
    # ------------------------------------------------------------------ #

    def test_join_pairs_list_shape_ground_truth(self) -> None:
        result = self.tool.execute(
            mode="join_pairs", items=[["a", 1], ["b", 2]]
        )
        self.assertEqual(
            result,
            {
                "mode": "join_pairs",
                "kv_sep": "=",
                "item_delim": ", ",
                "input_items": 2,
                "output_items": 2,
                "result": "a=1, b=2",
            },
        )

    def test_join_pairs_dict_shape(self) -> None:
        result = self.tool.execute(
            mode="join_pairs", items=[{"a": 1}, {"b": 2}]
        )
        self.assertEqual(result["result"], "a=1, b=2")

    def test_join_pairs_mixed_shapes_and_tuple_pairs(self) -> None:
        result = self.tool.execute(
            mode="join_pairs", items=[["a", 1], {"b": 2}, ("c", 3)]
        )
        self.assertEqual(result["result"], "a=1, b=2, c=3")

    def test_join_pairs_custom_kv_sep_and_item_delim(self) -> None:
        result = self.tool.execute(
            mode="join_pairs",
            items=[["a", 1], ["b", 2]],
            kv_sep=": ",
            item_delim="; ",
        )
        self.assertEqual(result["result"], "a: 1; b: 2")
        self.assertEqual(result["kv_sep"], ": ")
        self.assertEqual(result["item_delim"], "; ")

    def test_join_pairs_formats_ints_bools_floats(self) -> None:
        # True becomes "true" — the documented JSON-style choice.
        result = self.tool.execute(
            mode="join_pairs",
            items=[["flag", True], ["off", False], ["ratio", 2.5], [7, "lucky"]],
        )
        self.assertEqual(result["result"], "flag=true, off=false, ratio=2.5, 7=lucky")

    def test_join_pairs_string_values_left_alone(self) -> None:
        result = self.tool.execute(
            mode="join_pairs", items=[["name", "au"], {"mode": "strict"}]
        )
        self.assertEqual(result["result"], "name=au, mode=strict")

    def test_join_pairs_single_pair(self) -> None:
        result = self.tool.execute(mode="join_pairs", items=[["a", 1]])
        self.assertEqual(result["result"], "a=1")
        self.assertEqual(result["output_items"], 1)

    # ------------------------------------------------------------------ #
    # numbered mode
    # ------------------------------------------------------------------ #

    def test_numbered_ground_truth_dict(self) -> None:
        result = self.tool.execute(mode="numbered", items=["a", "b"])
        self.assertEqual(
            result,
            {
                "mode": "numbered",
                "number_format": "dot",
                "start": 1,
                "input_items": 2,
                "output_items": 2,
                "result": "1. a\n2. b",
            },
        )

    def test_numbered_paren_format(self) -> None:
        result = self.tool.execute(
            mode="numbered", items=["a", "b", "c"], number_format="paren"
        )
        self.assertEqual(result["result"], "1) a\n2) b\n3) c")
        self.assertEqual(result["number_format"], "paren")

    def test_numbered_custom_start(self) -> None:
        result = self.tool.execute(mode="numbered", items=["a", "b"], start=0)
        self.assertEqual(result["result"], "0. a\n1. b")
        self.assertEqual(result["start"], 0)

    def test_numbered_start_five(self) -> None:
        result = self.tool.execute(mode="numbered", items=["a", "b"], start=5)
        self.assertEqual(result["result"], "5. a\n6. b")

    def test_numbered_digit_string_start_accepted(self) -> None:
        result = self.tool.execute(mode="numbered", items=["a"], start="3")
        self.assertEqual(result["result"], "3. a")
        self.assertEqual(result["start"], 3)

    def test_numbered_coerces_scalars(self) -> None:
        result = self.tool.execute(mode="numbered", items=[1, True])
        self.assertEqual(result["result"], "1. 1\n2. true")

    # ------------------------------------------------------------------ #
    # bullet mode
    # ------------------------------------------------------------------ #

    def test_bullet_ground_truth_dict(self) -> None:
        result = self.tool.execute(mode="bullet", items=["a", "b"])
        self.assertEqual(
            result,
            {
                "mode": "bullet",
                "bullet": "-",
                "input_items": 2,
                "output_items": 2,
                "result": "- a\n- b",
            },
        )

    def test_bullet_custom_character(self) -> None:
        result = self.tool.execute(
            mode="bullet", items=["alpha", "beta"], bullet="*"
        )
        self.assertEqual(result["result"], "* alpha\n* beta")
        self.assertEqual(result["bullet"], "*")

    def test_bullet_multi_character_and_unicode(self) -> None:
        arrow = self.tool.execute(
            mode="bullet", items=["x", "y"], bullet="->"
        )
        self.assertEqual(arrow["result"], "-> x\n-> y")
        dot = self.tool.execute(mode="bullet", items=["x"], bullet="•")
        self.assertEqual(dot["result"], "• x")

    def test_bullet_keeps_empty_string_items(self) -> None:
        result = self.tool.execute(mode="bullet", items=["a", ""])
        self.assertEqual(result["result"], "- a\n- ")

    # ------------------------------------------------------------------ #
    # Input caps
    # ------------------------------------------------------------------ #

    def test_item_cap_rejects_10001_items(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="join", items=["x"] * 10_001)
        self.assertIn("10,000-item limit", str(ctx.exception))

    def test_item_cap_accepts_exactly_10000_items(self) -> None:
        result = self.tool.execute(mode="join", items=["x"] * 10_000)
        self.assertEqual(result["input_items"], 10_000)
        self.assertEqual(result["output_items"], 10_000)
        self.assertEqual(result["result"].count("x"), 10_000)

    def test_item_cap_applies_to_every_mode(self) -> None:
        oversized = ["x"] * 10_001
        for mode in ("join_pairs", "numbered", "bullet"):
            with self.subTest(mode=mode):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode=mode, items=oversized)

    def test_delimiter_length_cap(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="join", items=["a", "b"], delimiter="x" * 10_001
            )
        self.assertIn("10,000-character limit", str(ctx.exception))

    def test_bullet_length_cap(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(mode="bullet", items=["a"], bullet="x" * 17)
        self.assertIn("16-character limit", str(ctx.exception))
        # Exactly 16 characters is fine.
        ok = self.tool.execute(mode="bullet", items=["a"], bullet="x" * 16)
        self.assertEqual(ok["result"], f"{'x' * 16} a")

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation matrix)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="joined", items=["a"])
        self.assert_invalid(mode="JOIN", items=["a"])
        self.assert_invalid(mode=None, items=["a"])
        self.assert_invalid(mode=123, items=["a"])

    def test_invalid_items_container(self) -> None:
        for bad in (None, "a,b", 123, True, b"ab", {"a": 1}, {"a"}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="join", items=bad)
                self.assert_invalid(mode="numbered", items=bad)

    def test_invalid_scalar_items(self) -> None:
        for bad in (None, b"ab", ["nested"], {"k": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="join", items=["a", bad])
                self.assert_invalid(mode="bullet", items=[bad])

    def test_invalid_style(self) -> None:
        for bad in ("Oxford", "comma", "serial", 1, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="join", items=["a", "b"], style=bad)

    def test_invalid_delimiter(self) -> None:
        for bad in (5, True, [" , "], None.__class__):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="join", items=["a", "b"], delimiter=bad
                )
        # Empty string is a valid type but invalid with 3 items.
        self.assert_invalid(mode="join", items=["a", "b", "c"], delimiter="")

    def test_invalid_drop_empty_flag(self) -> None:
        for bad in (1, 0, "yes", [True]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="join", items=["a"], drop_empty=bad
                )

    def test_invalid_empty_as(self) -> None:
        for bad in ("notes", "", "blank", 1, True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="join", items=["a"], empty_as=bad)

    def test_invalid_join_pairs_elements(self) -> None:
        bad_elements = (
            ["three", "element", "pair"],
            ["one"],
            [],
            {"a": 1, "b": 2},
            "scalar",
            None,
            [None, 1],
            ["ok", {"nested": 1}],
        )
        for bad in bad_elements:
            with self.subTest(bad=bad):
                self.assert_invalid(mode="join_pairs", items=[bad])

    def test_invalid_kv_sep_and_item_delim(self) -> None:
        self.assert_invalid(mode="join_pairs", items=[["a", 1]], kv_sep="")
        self.assert_invalid(mode="join_pairs", items=[["a", 1]], kv_sep=5)
        self.assert_invalid(
            mode="join_pairs", items=[["a", 1], ["b", 2]], item_delim=""
        )
        self.assert_invalid(
            mode="join_pairs", items=[["a", 1], ["b", 2]], item_delim=7
        )

    def test_item_delim_empty_allowed_for_single_pair(self) -> None:
        result = self.tool.execute(
            mode="join_pairs", items=[["a", 1]], item_delim=""
        )
        self.assertEqual(result["result"], "a=1")

    def test_invalid_number_format(self) -> None:
        for bad in ("bullet", "DOT", "dot ", "1", True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="numbered", items=["a"], number_format=bad
                )

    def test_invalid_start(self) -> None:
        for bad in (-1, 1_000_000, True, 1.5, "abc"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="numbered", items=["a"], start=bad)

    def test_invalid_bullet(self) -> None:
        for bad in ("", 5, ["-"], True):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="bullet", items=["a"], bullet=bad)

    def test_invalid_mode_specific_options_in_wrong_mode(self) -> None:
        # Options that only some modes understand are rejected when
        # passed with any other mode — including mistyped values such
        # as style=1 in the numbered mode, which would otherwise be
        # silently ignored.
        cases = [
            {"mode": "numbered", "style": "oxford"},
            {"mode": "numbered", "delimiter": ", "},
            {"mode": "numbered", "drop_empty": True},
            {"mode": "bullet", "style": "plain"},
            {"mode": "bullet", "delimiter": ", "},
            {"mode": "join_pairs", "drop_empty": True},
            {"mode": "join", "kv_sep": "="},
            {"mode": "join", "item_delim": ", "},
            {"mode": "join", "number_format": "dot"},
            {"mode": "bullet", "start": 1},
            {"mode": "join", "bullet": "-"},
            {"mode": "numbered", "style": 1},
        ]
        for kwargs in cases:
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(items=["a", "b"], **kwargs)
                self.assertIn("is only valid in the", str(ctx.exception))
                self.assertIn(f"with mode={kwargs['mode']!r}", str(ctx.exception))

    def test_valid_options_accepted_in_their_own_modes(self) -> None:
        # The wrong-mode rejection must not overreach: each option
        # still works in the mode that owns it.
        self.tool.execute(mode="join", items=["a", "b"], delimiter="; ")
        self.tool.execute(mode="join", items=["a", "b"], style="oxford")
        self.tool.execute(mode="join", items=["a", ""], drop_empty=True)
        self.tool.execute(mode="join_pairs", items=[["a", 1]], kv_sep=": ")
        self.tool.execute(mode="join_pairs", items=[["a", 1]], item_delim="; ")
        self.tool.execute(mode="numbered", items=["a"], number_format="paren")
        self.tool.execute(mode="numbered", items=["a"], start=0)
        self.tool.execute(mode="bullet", items=["a"], bullet="*")
        # empty_as stays valid in every mode.
        self.tool.execute(mode="join", items=["a"], empty_as="empty")
        self.tool.execute(
            mode="join_pairs", items=[["a", 1]], empty_as="empty"
        )
        self.tool.execute(mode="numbered", items=["a"], empty_as="empty")
        self.tool.execute(mode="bullet", items=["a"], empty_as="empty")

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_join_deterministic_across_calls(self) -> None:
        items = ["apples", "", "bananas", 1, True, 2.5, "cherries"]
        first = self.tool.execute(
            mode="join", items=items, style="oxford", drop_empty=True
        )
        for _ in range(5):
            repeat = self.tool.execute(
                mode="join", items=items, style="oxford", drop_empty=True
            )
            self.assertEqual(first, repeat)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectJoinTool, JoinTool)
        self.assertEqual(self.tool.name, "join_tool")
        self.assertIn("oxford", self.tool.description)
        self.assertIn("join_pairs", self.tool.description)
        self.assertEqual(
            JoinTool.MODES, ("join", "join_pairs", "numbered", "bullet")
        )
        self.assertEqual(
            JoinTool.STYLES, ("plain", "oxford", "and", "or")
        )
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("JoinTool", __all__)


if __name__ == "__main__":
    unittest.main()
