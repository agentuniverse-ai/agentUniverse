#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_indent_tree_tool.py

"""Offline unit tests for IndentTreeTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: trees are compared against literal ground-truth
structures, flattened rows / leaf paths / depth statistics against
exact expected values, markdown rendering against golden strings, and
the round trip ``parse(to_markdown(tree)) == tree`` is checked for
clean input. Malformed indentation is asserted through the exact
tolerant warning entries it produces.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import IndentTreeTool
from agentuniverse.agent.action.tool.common_tool.indent_tree_tool import (
    IndentTreeTool as DirectIndentTreeTool,
)

# --------------------------------------------------------------------- #
# Ground-truth inputs and expected structures (literal, independent of
# the implementation under test)
# --------------------------------------------------------------------- #
SPACE_TREE_TEXT = "\n".join(
    [
        "Company",
        "  Engineering",
        "    Platform",
        "    Search",
        "  Sales",
        "    Enterprise",
    ]
)

SPACE_TREE_EXPECTED = [
    {
        "text": "Company",
        "level": 1,
        "children": [
            {
                "text": "Engineering",
                "level": 2,
                "children": [
                    {"text": "Platform", "level": 3, "children": []},
                    {"text": "Search", "level": 3, "children": []},
                ],
            },
            {
                "text": "Sales",
                "level": 2,
                "children": [
                    {"text": "Enterprise", "level": 3, "children": []},
                ],
            },
        ],
    }
]

TAB_TREE_TEXT = "Company\n\tEngineering\n\t\tPlatform"

DEDENT_TREE_TEXT = "\n".join(
    [
        "a",
        "  b",
        "    c",
        "  d",
        "e",
    ]
)

DEDENT_TREE_EXPECTED = [
    {
        "text": "a",
        "level": 1,
        "children": [
            {
                "text": "b",
                "level": 2,
                "children": [{"text": "c", "level": 3, "children": []}],
            },
            {"text": "d", "level": 2, "children": []},
        ],
    },
    {"text": "e", "level": 1, "children": []},
]

FILTER_TREE = [
    {
        "text": "A",
        "children": [
            {"text": "B", "children": []},
            {"text": "C", "children": [{"text": "D", "children": []}]},
        ],
    }
]

SPACE_TREE_MARKDOWN = (
    "# Company\n"
    "## Engineering\n"
    "### Platform\n"
    "### Search\n"
    "## Sales\n"
    "### Enterprise\n"
)


class IndentTreeToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib IndentTreeTool."""

    def setUp(self) -> None:
        self.tool = IndentTreeTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    # ------------------------------------------------------------------ #
    # parse mode — clean structures
    # ------------------------------------------------------------------ #

    def test_parse_space_tree_ground_truth(self) -> None:
        result = self.tool.execute(mode="parse", text=SPACE_TREE_TEXT)
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "input_format": "indentation",
                "indent_unit": {"requested": "auto", "unit_columns": 2},
                "node_count": 6,
                "max_depth": 3,
                "warning_count": 0,
                "warnings": [],
                "tree": SPACE_TREE_EXPECTED,
            },
        )

    def test_parse_explicit_units_match_auto_on_space_tree(self) -> None:
        for unit in ("2", 2):
            result = self.tool.execute(
                mode="parse", text=SPACE_TREE_TEXT, indent_unit=unit
            )
            self.assertEqual(result["tree"], SPACE_TREE_EXPECTED)
            self.assertEqual(
                result["indent_unit"], {"requested": "2", "unit_columns": 2}
            )

    def test_parse_tab_tree_auto_detects_four_columns(self) -> None:
        result = self.tool.execute(mode="parse", text=TAB_TREE_TEXT)
        self.assertEqual(result["indent_unit"], {"requested": "auto", "unit_columns": 4})
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(result["tree"][0]["children"][0]["text"], "Engineering")

    def test_parse_tab_tree_explicit_tab_unit(self) -> None:
        result = self.tool.execute(mode="parse", text=TAB_TREE_TEXT, indent_unit="tab")
        self.assertEqual(
            result["indent_unit"], {"requested": "tab", "unit_columns": 4}
        )
        self.assertEqual(result["warnings"], [])

    def test_parse_mixed_spaces_and_tabs(self) -> None:
        # Two spaces then one tab: 2 + 4 = 6 columns; smallest observed
        # indent of 2 divides 4 and 6, giving unit 2.
        text = "Root\n  Child\n  \tGrandchild"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["indent_unit"]["unit_columns"], 2)
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(
            [node["text"] for node in result["tree"]],
            ["Root"],
        )
        self.assertEqual(
            result["tree"][0]["children"][0]["children"][0]["text"],
            "Grandchild",
        )

    def test_parse_auto_detects_observed_unit_not_divisor(self) -> None:
        # A single nested indent of 4 is detected as unit 4 (the
        # observed width), not the divisor 2.
        result = self.tool.execute(mode="parse", text="a\n    b")
        self.assertEqual(result["indent_unit"], {"requested": "auto", "unit_columns": 4})

    def test_parse_auto_detects_three_column_unit(self) -> None:
        result = self.tool.execute(mode="parse", text="a\n   b\n      c")
        self.assertEqual(result["indent_unit"]["unit_columns"], 3)
        self.assertEqual(result["max_depth"], 3)
        self.assertEqual(result["warnings"], [])

    def test_parse_auto_defaults_to_four_without_nested_lines(self) -> None:
        result = self.tool.execute(mode="parse", text="a\nb\nc")
        self.assertEqual(result["indent_unit"], {"requested": "auto", "unit_columns": 4})
        self.assertEqual(result["node_count"], 3)
        self.assertEqual(result["max_depth"], 1)

    def test_parse_dedent_promotes_siblings(self) -> None:
        result = self.tool.execute(mode="parse", text=DEDENT_TREE_TEXT)
        self.assertEqual(result["tree"], DEDENT_TREE_EXPECTED)
        self.assertEqual(result["warning_count"], 0)

    def test_parse_strips_trailing_whitespace_and_handles_crlf(self) -> None:
        result = self.tool.execute(mode="parse", text="a   \r\n  b\t\r\n")
        self.assertEqual(result["tree"][0]["text"], "a")
        self.assertEqual(result["tree"][0]["children"][0]["text"], "b")

    def test_parse_skips_blank_lines(self) -> None:
        result = self.tool.execute(
            mode="parse", text="a\n\n   \n\t\n  b\n\n"
        )
        self.assertEqual(result["node_count"], 2)
        self.assertEqual(
            result["tree"][0]["children"][0]["text"], "b"
        )

    def test_parse_unicode_text(self) -> None:
        result = self.tool.execute(mode="parse", text="根\n  子节点")
        self.assertEqual(result["tree"][0]["children"][0]["text"], "子节点")

    # ------------------------------------------------------------------ #
    # parse mode — tolerant clamping with exact warnings
    # ------------------------------------------------------------------ #

    def test_parse_level_jump_clamped_with_warning(self) -> None:
        text = "a\n  b\n        c"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(result["tree"][0]["children"][0]["children"][0]["text"], "c")
        self.assertEqual(
            result["warnings"],
            [
                {
                    "line": 3,
                    "text": "c",
                    "type": "level_jump_clamped",
                    "message": (
                        "line 3: jumps from level 2 to level 5; clamped to "
                        "parent + 1 (level 3)"
                    ),
                }
            ],
        )

    def test_parse_indent_not_multiple_of_explicit_unit(self) -> None:
        text = "a\n   b"
        result = self.tool.execute(mode="parse", text=text, indent_unit="4")
        self.assertEqual(
            result["warnings"],
            [
                {
                    "line": 2,
                    "text": "b",
                    "type": "indent_not_multiple",
                    "message": (
                        "line 2: indent of 3 columns is not a multiple of "
                        "the 4-column indent unit; treated as depth 0 "
                        "(level 1)"
                    ),
                }
            ],
        )
        self.assertEqual(
            [node["text"] for node in result["tree"]], ["a", "b"]
        )

    def test_parse_auto_unit_fallback_with_inconsistent_indents(self) -> None:
        text = "a\n  b\n c"
        result = self.tool.execute(mode="parse", text=text)
        self.assertEqual(
            result["indent_unit"], {"requested": "auto", "unit_columns": 4}
        )
        self.assertEqual(result["warnings"][0]["type"], "auto_unit_fallback")
        self.assertEqual(
            [w["type"] for w in result["warnings"][1:]],
            ["indent_not_multiple", "indent_not_multiple"],
        )
        self.assertEqual(result["warning_count"], 3)
        # All three lines fall back to level-1 roots.
        self.assertEqual(
            [node["text"] for node in result["tree"]], ["a", "b", "c"]
        )

    def test_parse_leading_indent_ignored_with_warning(self) -> None:
        text = "    alpha\n      beta"
        result = self.tool.execute(mode="parse", text=text, indent_unit="4")
        self.assertEqual(
            result["warnings"][0],
            {
                "line": 1,
                "text": "alpha",
                "type": "leading_indent_ignored",
                "message": (
                    "line 1: the first entry is indented by 1 unit(s); "
                    "treated as level 1"
                ),
            },
        )
        self.assertEqual(result["tree"][0]["level"], 1)
        self.assertEqual(result["tree"][0]["children"][0]["text"], "beta")

    def test_parse_warnings_truncated_at_cap(self) -> None:
        text = "a\n" + " b\n" * 102
        result = self.tool.execute(mode="parse", text=text, indent_unit="4")
        self.assertEqual(result["warning_count"], 102)
        self.assertEqual(len(result["warnings"]), 101)
        self.assertEqual(result["warnings"][-1]["type"], "warnings_truncated")

    # ------------------------------------------------------------------ #
    # parse mode — ATX heading input (re-ingesting to_markdown output)
    # ------------------------------------------------------------------ #

    def test_parse_atx_headings(self) -> None:
        result = self.tool.execute(
            mode="parse", text="# Alpha\n## Beta\n### Gamma\n## Delta"
        )
        self.assertEqual(result["input_format"], "atx_headings")
        self.assertIsNone(result["indent_unit"])
        self.assertEqual(result["warnings"], [])
        expected = [
            {
                "text": "Alpha",
                "level": 1,
                "children": [
                    {
                        "text": "Beta",
                        "level": 2,
                        "children": [{"text": "Gamma", "level": 3, "children": []}],
                    },
                    {"text": "Delta", "level": 2, "children": []},
                ],
            }
        ]
        self.assertEqual(result["tree"], expected)

    def test_parse_atx_ranks_normalized_to_level_one(self) -> None:
        result = self.tool.execute(mode="parse", text="## A\n### B\n## C")
        self.assertEqual(result["input_format"], "atx_headings")
        self.assertEqual(result["tree"][0]["level"], 1)
        self.assertEqual(result["tree"][0]["children"][0]["level"], 2)

    def test_parse_atx_rank_jump_clamped(self) -> None:
        result = self.tool.execute(mode="parse", text="# A\n### B")
        self.assertEqual(result["tree"][0]["children"][0]["level"], 2)
        self.assertEqual(result["warnings"][0]["type"], "level_jump_clamped")

    def test_parse_atx_mixed_lines_rejected(self) -> None:
        self.assert_invalid(mode="parse", text="# A\nplain line")

    def test_parse_hash_without_space_is_indentation_mode(self) -> None:
        result = self.tool.execute(mode="parse", text="#nospace\n  child")
        self.assertEqual(result["input_format"], "indentation")
        self.assertEqual(result["tree"][0]["text"], "#nospace")

    # ------------------------------------------------------------------ #
    # flatten mode
    # ------------------------------------------------------------------ #

    def test_flatten_rows_ground_truth(self) -> None:
        result = self.tool.execute(mode="flatten", tree=SPACE_TREE_EXPECTED)
        self.assertEqual(
            result,
            {
                "mode": "flatten",
                "row_count": 6,
                "rows": [
                    {"text": "Company", "level": 1, "path": "/Company", "order": 0},
                    {
                        "text": "Engineering",
                        "level": 2,
                        "path": "/Company/Engineering",
                        "order": 1,
                    },
                    {
                        "text": "Platform",
                        "level": 3,
                        "path": "/Company/Engineering/Platform",
                        "order": 2,
                    },
                    {
                        "text": "Search",
                        "level": 3,
                        "path": "/Company/Engineering/Search",
                        "order": 3,
                    },
                    {"text": "Sales", "level": 2, "path": "/Company/Sales", "order": 4},
                    {
                        "text": "Enterprise",
                        "level": 3,
                        "path": "/Company/Sales/Enterprise",
                        "order": 5,
                    },
                ],
            },
        )

    def test_flatten_levels_recomputed_from_nesting(self) -> None:
        # A stale 'level' field must not influence the computed rows.
        tree = [
            {
                "text": "A",
                "level": 9,
                "children": [{"text": "B", "level": 2, "children": []}],
            }
        ]
        result = self.tool.execute(mode="flatten", tree=tree)
        self.assertEqual(
            [row["level"] for row in result["rows"]], [1, 2]
        )

    def test_flatten_multi_root_document_order(self) -> None:
        result = self.tool.execute(mode="flatten", tree=DEDENT_TREE_EXPECTED)
        self.assertEqual(
            [row["text"] for row in result["rows"]], ["a", "b", "c", "d", "e"]
        )
        self.assertEqual(result["rows"][2]["path"], "/a/b/c")

    # ------------------------------------------------------------------ #
    # paths mode
    # ------------------------------------------------------------------ #

    def test_paths_leaf_paths_only(self) -> None:
        result = self.tool.execute(mode="paths", tree=SPACE_TREE_EXPECTED)
        self.assertEqual(
            result,
            {
                "mode": "paths",
                "min_depth": 1,
                "max_depth": None,
                "count": 3,
                "paths": [
                    "/Company/Engineering/Platform",
                    "/Company/Engineering/Search",
                    "/Company/Sales/Enterprise",
                ],
            },
        )

    def test_paths_min_depth_filter(self) -> None:
        result = self.tool.execute(
            mode="paths", tree=FILTER_TREE, min_depth=3
        )
        self.assertEqual(result["paths"], ["/A/C/D"])

    def test_paths_max_depth_filter(self) -> None:
        result = self.tool.execute(
            mode="paths", tree=FILTER_TREE, max_depth=2
        )
        self.assertEqual(result["paths"], ["/A/B"])

    def test_paths_min_and_max_depth_filters(self) -> None:
        result = self.tool.execute(
            mode="paths", tree=FILTER_TREE, min_depth=2, max_depth=2
        )
        self.assertEqual(result["paths"], ["/A/B"])
        self.assertEqual(result["min_depth"], 2)
        self.assertEqual(result["max_depth"], 2)

    def test_paths_filter_can_exclude_everything(self) -> None:
        result = self.tool.execute(
            mode="paths", tree=SPACE_TREE_EXPECTED, max_depth=2
        )
        self.assertEqual(result["paths"], [])
        self.assertEqual(result["count"], 0)

    # ------------------------------------------------------------------ #
    # depth_stats mode
    # ------------------------------------------------------------------ #

    def test_depth_stats_ground_truth(self) -> None:
        result = self.tool.execute(mode="depth_stats", tree=SPACE_TREE_EXPECTED)
        self.assertEqual(
            result,
            {
                "mode": "depth_stats",
                "node_count": 6,
                "max_depth": 3,
                "level_counts": {"1": 1, "2": 2, "3": 3},
                "widest_level": 3,
                "widest_level_count": 3,
            },
        )

    def test_depth_stats_tie_resolved_to_smallest_level(self) -> None:
        tree = [
            {"text": "A", "children": [{"text": "B", "children": []}]},
            {"text": "C", "children": [{"text": "D", "children": []}]},
        ]
        result = self.tool.execute(mode="depth_stats", tree=tree)
        self.assertEqual(result["widest_level"], 1)
        self.assertEqual(result["widest_level_count"], 2)

    # ------------------------------------------------------------------ #
    # to_markdown mode
    # ------------------------------------------------------------------ #

    def test_to_markdown_golden_output(self) -> None:
        result = self.tool.execute(mode="to_markdown", tree=SPACE_TREE_EXPECTED)
        self.assertEqual(
            result,
            {
                "mode": "to_markdown",
                "min_level": 1,
                "line_count": 6,
                "warning_count": 0,
                "warnings": [],
                "markdown": SPACE_TREE_MARKDOWN,
            },
        )

    def test_to_markdown_min_level_option(self) -> None:
        result = self.tool.execute(
            mode="to_markdown", tree=SPACE_TREE_EXPECTED, min_level=2
        )
        self.assertEqual(result["min_level"], 2)
        self.assertEqual(
            result["markdown"],
            "## Company\n"
            "### Engineering\n"
            "#### Platform\n"
            "#### Search\n"
            "### Sales\n"
            "#### Enterprise\n",
        )

    def test_to_markdown_rank_clamped_at_six(self) -> None:
        node = {"text": "n8", "children": []}
        for index in (7, 6, 5, 4, 3, 2, 1):
            node = {"text": f"n{index}", "children": [node]}
        result = self.tool.execute(mode="to_markdown", tree=[node])
        self.assertEqual(result["warning_count"], 2)
        self.assertEqual(
            [w["type"] for w in result["warnings"]],
            ["heading_rank_clamped"] * 2,
        )
        self.assertEqual(
            result["markdown"],
            "# n1\n## n2\n### n3\n#### n4\n##### n5\n###### n6\n"
            "###### n7\n###### n8\n",
        )

    # ------------------------------------------------------------------ #
    # Round trip: parse(to_markdown(tree)) == tree for clean input
    # ------------------------------------------------------------------ #

    def test_markdown_round_trip(self) -> None:
        markdown = self.tool.execute(
            mode="to_markdown", tree=SPACE_TREE_EXPECTED
        )["markdown"]
        reparsed = self.tool.execute(mode="parse", text=markdown)
        self.assertEqual(reparsed["tree"], SPACE_TREE_EXPECTED)
        self.assertEqual(reparsed["input_format"], "atx_headings")
        self.assertEqual(reparsed["warnings"], [])

    def test_markdown_round_trip_with_min_level(self) -> None:
        markdown = self.tool.execute(
            mode="to_markdown", tree=SPACE_TREE_EXPECTED, min_level=3
        )["markdown"]
        reparsed = self.tool.execute(mode="parse", text=markdown)
        self.assertEqual(reparsed["tree"], SPACE_TREE_EXPECTED)

    def test_full_pipeline_parse_flatten_markdown(self) -> None:
        parsed = self.tool.execute(mode="parse", text=SPACE_TREE_TEXT)
        flattened = self.tool.execute(mode="flatten", tree=parsed["tree"])
        self.assertEqual(flattened["row_count"], 6)
        rendered = self.tool.execute(mode="to_markdown", tree=parsed["tree"])
        self.assertEqual(rendered["markdown"], SPACE_TREE_MARKDOWN)

    # ------------------------------------------------------------------ #
    # Empty / blank handling
    # ------------------------------------------------------------------ #

    def test_parse_empty_text_yields_empty_tree(self) -> None:
        result = self.tool.execute(mode="parse", text="")
        self.assertEqual(result["node_count"], 0)
        self.assertEqual(result["tree"], [])
        self.assertEqual(result["max_depth"], 0)
        self.assertEqual(result["warnings"], [])

    def test_parse_blank_text_yields_empty_tree(self) -> None:
        result = self.tool.execute(mode="parse", text="   \n\t\n\n \t \n")
        self.assertEqual(result["node_count"], 0)
        self.assertEqual(result["tree"], [])

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="parseit", text="a")
        self.assert_invalid(mode=None, text="a")
        self.assert_invalid(mode=123, text="a")
        self.assert_invalid(mode=["parse"], text="a")

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, b"a", ["a"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text=bad)

    def test_parse_missing_text(self) -> None:
        self.assert_invalid(mode="parse")
        self.assert_invalid(mode="parse", tree=[{"text": "a", "children": []}])

    def test_text_length_limit(self) -> None:
        oversized = "a\n" * 60_000
        self.assert_invalid(mode="parse", text=oversized)

    def test_invalid_indent_unit(self) -> None:
        for bad in ("3", 3, 0, 1, True, " 2", 2.0, ["2"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", text="a\n  b", indent_unit=bad)

    def test_invalid_tree_type(self) -> None:
        for bad in (None, "a", 123, True, {"text": "a"}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="flatten", tree=bad)

    def test_invalid_empty_tree(self) -> None:
        for mode in ("flatten", "paths", "depth_stats", "to_markdown"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, tree=[])

    def test_invalid_node_shapes(self) -> None:
        base_cases = [
            [{"children": []}],
            [{"text": "", "children": []}],
            [{"text": "   ", "children": []}],
            [{"text": 123, "children": []}],
            [{"text": "a", "children": "no"}],
            [{"text": "a", "children": None}],
            ["a"],
            [True],
            [{"text": "a", "children": [["b"]]}],
        ]
        for bad in base_cases:
            with self.subTest(bad=bad):
                self.assert_invalid(mode="flatten", tree=bad)

    def test_invalid_node_level_field(self) -> None:
        for bad in ("1", True, 0, 1.5):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="flatten", tree=[{"text": "a", "level": bad, "children": []}]
                )

    def test_tree_extra_keys_ignored(self) -> None:
        tree = [{"text": "a", "level": 1, "children": [], "note": "extra"}]
        result = self.tool.execute(mode="flatten", tree=tree)
        self.assertEqual(result["row_count"], 1)

    def test_tree_cycle_rejected(self) -> None:
        node = {"text": "A", "children": []}
        node["children"].append(node)
        self.assert_invalid(mode="flatten", tree=[node])

    def test_tree_shared_node_rejected(self) -> None:
        shared = {"text": "B", "children": []}
        tree = [shared, {"text": "R", "children": [shared]}]
        self.assert_invalid(mode="depth_stats", tree=tree)

    def test_tree_node_limit(self) -> None:
        tree = [
            {"text": "root", "children": [{"text": f"c{i}"} for i in range(10_001)]}
        ]
        self.assert_invalid(mode="flatten", tree=tree)

    def test_tree_depth_limit(self) -> None:
        node = {"text": "leaf", "children": []}
        for _ in range(257):
            node = {"text": "n", "children": [node]}
        self.assert_invalid(mode="to_markdown", tree=[node])

    def test_invalid_depth_filters(self) -> None:
        tree = [{"text": "a", "children": []}]
        for bad in (0, -1, True, "2", 2.5):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="paths", tree=tree, min_depth=bad)
                self.assert_invalid(mode="paths", tree=tree, max_depth=bad)

    def test_min_depth_greater_than_max_depth_rejected(self) -> None:
        tree = [{"text": "a", "children": []}]
        self.assert_invalid(mode="paths", tree=tree, min_depth=3, max_depth=2)

    def test_invalid_min_level(self) -> None:
        tree = [{"text": "a", "children": []}]
        for bad in (0, 7, -1, True, "1", 1.5):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="to_markdown", tree=tree, min_level=bad)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectIndentTreeTool, IndentTreeTool)
        self.assertEqual(self.tool.name, "indent_tree_tool")
        self.assertIn("parse", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("IndentTreeTool", __all__)


if __name__ == "__main__":
    unittest.main()
