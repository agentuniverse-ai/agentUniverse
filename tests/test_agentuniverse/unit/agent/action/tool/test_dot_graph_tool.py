#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_dot_graph_tool.py

"""Offline unit tests for DotGraphTool.

The tool is built purely on the standard library and never renders
anything or touches the network, so this suite runs fully offline.
Every assertion is deterministic: the digraph / graph modes are
checked against exact expected DOT source strings (every shape,
node style, edge style and arrow direction, attribute order
stability, quote / backslash / newline escaping, ports, cluster
wrapping with proper indentation and brace nesting, id sanitization
with the reported mapping, the undirected variant), the validate
mode against exact issue payloads (lint matrix), the stats mode
against exact parse-back counts, and the error matrix covers every
strict-validation branch.
"""

import asyncio
import unittest

from agentuniverse.agent.action.tool.common_tool import DotGraphTool
from agentuniverse.agent.action.tool.common_tool.dot_graph_tool import (
    DotGraphTool as DirectDotGraphTool,
)


class DotGraphToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib DotGraphTool."""

    def setUp(self) -> None:
        self.tool = DotGraphTool()

    def _expect_value_error(self, fragment: str, **kwargs) -> None:
        """Assert execute raises ValueError whose message contains fragment."""
        with self.assertRaises(ValueError) as caught:
            self.tool.execute(**kwargs)
        self.assertIn(fragment, str(caught.exception))

    # ------------------------------------------------------------------ #
    # digraph mode — exact source ground truths
    # ------------------------------------------------------------------ #

    def test_digraph_minimal_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph", nodes=[{"id": "a"}, {"id": "b"}]
        )
        self.assertEqual(
            result,
            {
                "mode": "digraph",
                "graph_name": "G",
                "result": (
                    "digraph G {\n"
                    "    a [shape=box];\n"
                    "    b [shape=box];\n"
                    "}"
                ),
                "node_count": 2,
                "edge_count": 0,
                "cluster_count": 0,
            },
        )

    def test_digraph_custom_name_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph", name="pipeline", nodes=[{"id": "a"}]
        )
        self.assertEqual(
            result["result"], "digraph pipeline {\n    a [shape=box];\n}"
        )
        self.assertEqual(result["graph_name"], "pipeline")
        self.assertNotIn("id_mapping", result)

    def test_digraph_all_shapes_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "n1", "label": "n", "shape": "box"},
                {"id": "n2", "label": "n", "shape": "ellipse"},
                {"id": "n3", "label": "n", "shape": "diamond"},
                {"id": "n4", "label": "n", "shape": "circle"},
                {"id": "n5", "label": "n", "shape": "hexagon"},
                {"id": "n6", "label": "n", "shape": "cylinder"},
                {"id": "n7", "label": "n", "shape": "record"},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    n1 [label="n", shape=box];\n'
            '    n2 [label="n", shape=ellipse];\n'
            '    n3 [label="n", shape=diamond];\n'
            '    n4 [label="n", shape=circle];\n'
            '    n5 [label="n", shape=hexagon];\n'
            '    n6 [label="n", shape=cylinder];\n'
            '    n7 [label="n", shape=record];\n'
            "}",
        )

    def test_digraph_node_styling_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {
                    "id": "db",
                    "label": "Postgres",
                    "shape": "cylinder",
                    "style": "filled",
                    "fillcolor": "#2196f3",
                    "fontsize": 14,
                },
                {"id": "api", "label": "API", "fontsize": 10.5},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    db [label="Postgres", shape=cylinder, style=filled, '
            "fillcolor=#2196f3, fontsize=14];\n"
            '    api [label="API", shape=box, fontsize=10.5];\n'
            "}",
        )

    def test_digraph_edge_styles_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[
                {"from": "a", "to": "b"},
                {"from": "a", "to": "b", "style": "solid"},
                {"from": "a", "to": "b", "style": "dashed"},
                {"from": "a", "to": "b", "style": "dotted"},
                {"from": "a", "to": "b", "style": "bold"},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            "    a [shape=box];\n"
            "    b [shape=box];\n"
            "    a -> b;\n"
            "    a -> b [style=solid];\n"
            "    a -> b [style=dashed];\n"
            "    a -> b [style=dotted];\n"
            "    a -> b [style=bold];\n"
            "}",
        )

    def test_digraph_edge_dirs_and_weight_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[
                {"from": "a", "to": "b", "dir": "none"},
                {"from": "a", "to": "b", "dir": "both"},
                {"from": "a", "to": "b", "dir": "back"},
                {"from": "a", "to": "b", "weight": 2},
                {"from": "a", "to": "b", "weight": 0.5},
                {"from": "a", "to": "b", "weight": -1},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            "    a [shape=box];\n"
            "    b [shape=box];\n"
            "    a -> b [dir=none];\n"
            "    a -> b [dir=both];\n"
            "    a -> b [dir=back];\n"
            "    a -> b [weight=2];\n"
            "    a -> b [weight=0.5];\n"
            "    a -> b [weight=-1];\n"
            "}",
        )

    def test_digraph_edge_full_attribute_order_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[
                {
                    "weight": 3,
                    "dir": "both",
                    "style": "dotted",
                    "label": "uses",
                    "to": "b",
                    "from": "a",
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            "    a [shape=box];\n"
            "    b [shape=box];\n"
            '    a -> b [label="uses", style=dotted, dir=both, weight=3];\n'
            "}",
        )

    def test_digraph_node_attribute_order_stability(self) -> None:
        """Key insertion order in the spec dict must not affect output."""
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {
                    "fontsize": 12,
                    "fillcolor": "lightblue",
                    "style": "filled",
                    "shape": "ellipse",
                    "label": "A",
                    "id": "a",
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    a [label="A", shape=ellipse, style=filled, '
            "fillcolor=lightblue, fontsize=12];\n"
            "}",
        )

    def test_digraph_label_escaping_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "q", "label": 'He said "hi"'},
                {"id": "p", "label": "C:\\path\\graph"},
                {"id": "n", "label": "line1\nline2"},
                {"id": "r", "label": "line1\r\nline2"},
                {"id": "c", "label": "line1\rline2"},
                {"id": "m", "label": 'a"b\\c\nd'},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    q [label="He said \\"hi\\"", shape=box];\n'
            '    p [label="C:\\\\path\\\\graph", shape=box];\n'
            '    n [label="line1\\nline2", shape=box];\n'
            '    r [label="line1\\nline2", shape=box];\n'
            '    c [label="line1\\nline2", shape=box];\n'
            '    m [label="a\\"b\\\\c\\nd", shape=box];\n'
            "}",
        )

    def test_digraph_ports_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "tbl", "label": "<p1> A | <p2> B", "shape": "record"},
                {"id": "out", "label": "Out"},
            ],
            edges=[
                {"from": "tbl:p1", "to": "out:s"},
                {"from": "tbl:p2", "to": "out"},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    tbl [label="<p1> A | <p2> B", shape=record];\n'
            '    out [label="Out", shape=box];\n'
            "    tbl:p1 -> out:s;\n"
            "    tbl:p2 -> out;\n"
            "}",
        )

    def test_digraph_cluster_wrapping_exact(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "cli", "label": "CLI"},
                {"id": "api", "label": "API"},
                {"id": "db", "label": "DB", "shape": "cylinder"},
            ],
            edges=[
                {"from": "cli", "to": "api", "label": "call"},
                {"from": "api", "to": "db"},
            ],
            clusters=[
                {
                    "name": "backend",
                    "label": "Backend Services",
                    "node_ids": ["api", "db"],
                }
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            '    cli [label="CLI", shape=box];\n'
            "    subgraph cluster_backend {\n"
            '        label="Backend Services";\n'
            '        api [label="API", shape=box];\n'
            '        db [label="DB", shape=cylinder];\n'
            "    }\n"
            '    cli -> api [label="call"];\n'
            "    api -> db;\n"
            "}",
        )
        self.assertEqual(result["cluster_count"], 1)
        self.assertEqual(result["id_mapping"], {"backend": "cluster_backend"})

    def test_digraph_cluster_without_label_and_prefixed_name(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            nodes=[{"id": "a"}, {"id": "b"}, {"id": "c"}],
            clusters=[
                {"name": "cluster_main", "node_ids": ["a"]},
                {"name": "side", "node_ids": ["b"]},
            ],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            "    c [shape=box];\n"
            "    subgraph cluster_main {\n"
            "        a [shape=box];\n"
            "    }\n"
            "    subgraph cluster_side {\n"
            "        b [shape=box];\n"
            "    }\n"
            "}",
        )
        self.assertEqual(result["id_mapping"], {"side": "cluster_side"})
        self.assertEqual(result["cluster_count"], 2)

    def test_digraph_id_sanitization_and_mapping(self) -> None:
        result = self.tool.execute(
            mode="digraph",
            name="my pipeline",
            nodes=[
                {"id": "my node", "label": "A"},
                {"id": "2fa", "label": "B"},
                {"id": "node", "label": "C"},
                {"id": "graph-1", "label": "D"},
            ],
            edges=[{"from": "my node", "to": "2fa"}],
        )
        self.assertEqual(
            result["result"],
            "digraph my_pipeline {\n"
            '    my_node [label="A", shape=box];\n'
            '    _2fa [label="B", shape=box];\n'
            '    node_ [label="C", shape=box];\n'
            '    graph_1 [label="D", shape=box];\n'
            "    my_node -> _2fa;\n"
            "}",
        )
        self.assertEqual(
            result["id_mapping"],
            {
                "my pipeline": "my_pipeline",
                "my node": "my_node",
                "2fa": "_2fa",
                "node": "node_",
                "graph-1": "graph_1",
            },
        )

    def test_digraph_sanitized_id_in_edge_endpoints(self) -> None:
        """Edges reference raw ids; the sanitized form is emitted."""
        result = self.tool.execute(
            mode="digraph",
            nodes=[{"id": "start here"}, {"id": "end now"}],
            edges=[{"from": "start here", "to": "end now", "style": "bold"}],
        )
        self.assertEqual(
            result["result"],
            "digraph G {\n"
            "    start_here [shape=box];\n"
            "    end_now [shape=box];\n"
            "    start_here -> end_now [style=bold];\n"
            "}",
        )

    def test_digraph_deterministic(self) -> None:
        kwargs = {
            "mode": "digraph",
            "name": "net",
            "nodes": [{"id": "a", "label": "A"}],
            "edges": [{"from": "a", "to": "a", "label": "loop"}],
            "clusters": [],
        }
        first = self.tool.execute(**kwargs)
        second = self.tool.execute(**kwargs)
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # graph (undirected) mode
    # ------------------------------------------------------------------ #

    def test_graph_mode_undirected_exact(self) -> None:
        result = self.tool.execute(
            mode="graph",
            nodes=[{"id": "a"}, {"id": "b", "label": "B", "shape": "circle"}],
            edges=[{"from": "a", "to": "b", "style": "dotted"}],
        )
        self.assertEqual(
            result["result"],
            "graph G {\n"
            "    a [shape=box];\n"
            '    b [label="B", shape=circle];\n'
            "    a -- b [style=dotted];\n"
            "}",
        )
        self.assertEqual(result["mode"], "graph")

    # ------------------------------------------------------------------ #
    # validate mode — lint matrix
    # ------------------------------------------------------------------ #

    def test_validate_clean_generated_source(self) -> None:
        generated = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "a", "label": 'say "hi"'},
                {"id": "b", "label": "two\nlines"},
            ],
            edges=[{"from": "a", "to": "b", "label": "x--y"}],
        )
        result = self.tool.execute(mode="validate", source=generated["result"])
        self.assertEqual(
            result,
            {"mode": "validate", "ok": True, "lines_checked": 5, "issues": []},
        )

    def test_validate_unterminated_quote(self) -> None:
        result = self.tool.execute(
            mode="validate", source='digraph G {\n    a [label="oops];\n}'
        )
        self.assertEqual(
            result["issues"],
            [
                {
                    "line": 2,
                    "check": "quotes",
                    "severity": "error",
                    "message": "unterminated double quote (quotes do not "
                               "span lines in this lint)",
                }
            ],
        )
        self.assertFalse(result["ok"])

    def test_validate_escaped_quotes_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source='digraph G {\n    a [label="say \\"hi\\" now"];\n}',
        )
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    def test_validate_missing_closing_brace(self) -> None:
        result = self.tool.execute(
            mode="validate", source="digraph G {\n    a [shape=box];"
        )
        self.assertEqual(
            result["issues"],
            [
                {
                    "line": 2,
                    "check": "balanced_braces",
                    "severity": "error",
                    "message": "unbalanced braces: 1 '{' never closed",
                }
            ],
        )
        self.assertFalse(result["ok"])

    def test_validate_extra_closing_brace(self) -> None:
        result = self.tool.execute(
            mode="validate", source="digraph G {\n}\n}\n"
        )
        self.assertEqual(
            result["issues"],
            [
                {
                    "line": 3,
                    "check": "balanced_braces",
                    "severity": "error",
                    "message": "unbalanced braces: more '}' than '{'",
                }
            ],
        )
        self.assertFalse(result["ok"])

    def test_validate_unclosed_bracket(self) -> None:
        result = self.tool.execute(
            mode="validate", source="digraph G {\n    a [shape=box;\n}"
        )
        self.assertEqual(
            result["issues"],
            [
                {
                    "line": 3,
                    "check": "balanced_brackets",
                    "severity": "error",
                    "message": "unbalanced brackets: 1 '[' never closed",
                }
            ],
        )
        self.assertFalse(result["ok"])

    def test_validate_missing_declaration(self) -> None:
        result = self.tool.execute(
            mode="validate", source="a -> b;\n}"
        )
        self.assertEqual(result["issues"][0]["check"], "declaration")
        self.assertEqual(result["issues"][0]["severity"], "error")
        self.assertEqual(result["issues"][0]["line"], 1)
        self.assertFalse(result["ok"])

    def test_validate_strict_declaration_accepted(self) -> None:
        result = self.tool.execute(
            mode="validate", source="strict digraph G {\n    a;\n}"
        )
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    def test_validate_missing_semicolons_warned(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source="digraph G {\n    a [shape=box]\n    a -> b\n}",
        )
        warnings = [
            i for i in result["issues"] if i["check"] == "semicolons"
        ]
        self.assertEqual([w["line"] for w in warnings], [2, 3])
        self.assertTrue(
            all(w["severity"] == "warning" for w in warnings)
        )
        # Semicolons are optional in DOT — warnings alone keep ok True.
        self.assertTrue(result["ok"])

    def test_validate_semicolons_silent_when_present(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source="digraph G {\n    a [shape=box];\n    b [shape=box];\n"
                   "    a -> b;\n}",
        )
        self.assertEqual(result["issues"], [])

    def test_validate_unknown_edge_endpoints_warned_once(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source="digraph G {\n    a -> b;\n    a -> c;\n    b -> c;\n}",
        )
        endpoint_warnings = [
            i for i in result["issues"] if i["check"] == "edge_endpoints"
        ]
        self.assertEqual(
            [(i["line"], i["message"]) for i in endpoint_warnings],
            [
                (2, "edge references node 'a' that is never declared"),
                (2, "edge references node 'b' that is never declared"),
                (3, "edge references node 'c' that is never declared"),
            ],
        )
        self.assertTrue(result["ok"])

    def test_validate_declared_endpoints_silent(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source="digraph G {\n    a;\n    b [shape=box];\n    a -> b;\n}",
        )
        self.assertEqual(result["issues"], [])

    def test_validate_comments_ignored(self) -> None:
        result = self.tool.execute(
            mode="validate",
            source=(
                "digraph G {\n"
                "    // sketch of \"a\"\n"
                "    a [label=\"https://x.io\"]; // trailing note\n"
                "}"
            ),
        )
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["lines_checked"], 4)

    def test_validate_subgraph_cluster_source(self) -> None:
        source = (
            "digraph G {\n"
            "    a;\n"
            "    subgraph cluster_backend {\n"
            '        label="Back";\n'
            "        b;\n"
            "    }\n"
            "    a -> b;\n"
            "}"
        )
        result = self.tool.execute(mode="validate", source=source)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    # ------------------------------------------------------------------ #
    # stats mode — parse-back counts
    # ------------------------------------------------------------------ #

    def test_stats_parse_back_generated_source(self) -> None:
        generated = self.tool.execute(
            mode="digraph",
            nodes=[
                {"id": "a", "label": "A"},
                {"id": "b", "label": "B"},
                {"id": "c", "label": "C"},
            ],
            edges=[
                {"from": "a", "to": "b"},
                {"from": "b", "to": "c"},
            ],
            clusters=[{"name": "grp", "node_ids": ["c"]}],
        )
        self.assertEqual(
            self.tool.execute(mode="stats", source=generated["result"]),
            {
                "mode": "stats",
                "node_count": 3,
                "edge_count": 2,
                "cluster_count": 1,
                "graph_type": "digraph",
            },
        )

    def test_stats_undirected_source(self) -> None:
        source = "graph G {\n    a;\n    b;\n    a -- b;\n}"
        self.assertEqual(
            self.tool.execute(mode="stats", source=source),
            {
                "mode": "stats",
                "node_count": 2,
                "edge_count": 1,
                "cluster_count": 0,
                "graph_type": "graph",
            },
        )

    def test_stats_ignores_comments_blanks_and_attr_lines(self) -> None:
        source = (
            "digraph G {\n"
            "    // a comment\n"
            "\n"
            "    node [shape=box];\n"
            '    a [label="x"];\n'
            "    subgraph cluster_x {\n"
            '        label="X";\n'
            "        b;\n"
            "    }\n"
            "    a -> b;\n"
            "}"
        )
        self.assertEqual(
            self.tool.execute(mode="stats", source=source),
            {
                "mode": "stats",
                "node_count": 2,
                "edge_count": 1,
                "cluster_count": 1,
                "graph_type": "digraph",
            },
        )

    # ------------------------------------------------------------------ #
    # async delegation (base-class async_execute -> execute)
    # ------------------------------------------------------------------ #

    def test_async_execute_matches_execute(self) -> None:
        kwargs = {
            "mode": "digraph",
            "nodes": [{"id": "a"}, {"id": "b"}],
            "edges": [{"from": "a", "to": "b"}],
        }
        sync_result = self.tool.execute(**kwargs)
        async_result = asyncio.run(self.tool.async_execute(**kwargs))
        self.assertEqual(sync_result, async_result)

    # ------------------------------------------------------------------ #
    # error matrix — strict validation
    # ------------------------------------------------------------------ #

    def test_error_unknown_mode(self) -> None:
        self._expect_value_error(
            "mode must be one of", mode="flowchart", nodes=[{"id": "a"}]
        )

    def test_error_nodes_required_and_list(self) -> None:
        self._expect_value_error(
            "nodes is required", mode="digraph", nodes=None
        )
        self._expect_value_error(
            "must contain at least one spec", mode="digraph", nodes=[]
        )
        self._expect_value_error(
            "must be a list of specs", mode="digraph", nodes="a"
        )
        self._expect_value_error(
            "must be a list of specs", mode="graph", nodes={"id": "a"}
        )

    def test_error_node_id_validation(self) -> None:
        self._expect_value_error(
            "nodes[0].id is required", mode="digraph", nodes=[{"label": "x"}],
        )
        self._expect_value_error(
            "nodes[0].id must be a non-empty string", mode="digraph",
            nodes=[{"id": ""}],
        )
        self._expect_value_error(
            "nodes[0].id must be a non-empty string", mode="digraph",
            nodes=[{"id": 7}],
        )
        self._expect_value_error(
            "exceeds the 200-character limit", mode="digraph",
            nodes=[{"id": "a" * 201}],
        )
        self._expect_value_error(
            "must not contain control characters", mode="digraph",
            nodes=[{"id": "a\nb"}],
        )

    def test_error_duplicate_node_id(self) -> None:
        self._expect_value_error(
            "duplicate node id: 'a'", mode="digraph",
            nodes=[{"id": "a"}, {"id": "a"}],
        )

    def test_error_sanitization_collision(self) -> None:
        self._expect_value_error(
            "ids collide after sanitization", mode="digraph",
            nodes=[{"id": "a-b"}, {"id": "a b"}],
        )

    def test_error_unknown_shape_style_color_fontsize(self) -> None:
        self._expect_value_error(
            "nodes[0].shape must be one of", mode="digraph",
            nodes=[{"id": "a", "shape": "star"}],
        )
        self._expect_value_error(
            "nodes[0].style must be one of", mode="digraph",
            nodes=[{"id": "a", "style": "solid"}],
        )
        self._expect_value_error(
            "must be a hex color", mode="digraph",
            nodes=[{"id": "a", "fillcolor": "22ff"}],
        )
        self._expect_value_error(
            "must be a hex color", mode="digraph",
            nodes=[{"id": "a", "fillcolor": "#12"}],
        )
        self._expect_value_error(
            "must be > 0", mode="digraph",
            nodes=[{"id": "a", "fontsize": 0}],
        )
        self._expect_value_error(
            "must be a number", mode="digraph",
            nodes=[{"id": "a", "fontsize": "14"}],
        )
        self._expect_value_error(
            "must be a number", mode="digraph",
            nodes=[{"id": "a", "fontsize": True}],
        )
        self._expect_value_error(
            "exceeds the 1000.0 limit", mode="digraph",
            nodes=[{"id": "a", "fontsize": 1001}],
        )

    def test_error_unknown_spec_keys(self) -> None:
        self._expect_value_error(
            "unknown key(s): colour", mode="digraph",
            nodes=[{"id": "a", "colour": "red"}],
        )
        self._expect_value_error(
            "unknown key(s): arrow", mode="digraph",
            nodes=[{"id": "a"}],
            edges=[{"from": "a", "to": "a", "arrow": "->"}],
        )
        self._expect_value_error(
            "nodes[0] must be a dict", mode="digraph", nodes=["a"],
        )

    def test_error_edge_endpoints_must_be_declared(self) -> None:
        self._expect_value_error(
            "references unknown node id(s): 'x', 'y'", mode="digraph",
            nodes=[{"id": "a"}],
            edges=[{"from": "x", "to": "y"}],
        )

    def test_error_required_keys(self) -> None:
        self._expect_value_error(
            "edges[0].from is required", mode="digraph",
            nodes=[{"id": "a"}], edges=[{"to": "a"}],
        )
        self._expect_value_error(
            "edges[0].to is required", mode="digraph",
            nodes=[{"id": "a"}], edges=[{"from": "a"}],
        )
        self._expect_value_error(
            "clusters[0].name is required", mode="digraph",
            nodes=[{"id": "a"}], clusters=[{"node_ids": ["a"]}],
        )

    def test_error_edge_style_dir_weight(self) -> None:
        base = {"mode": "digraph", "nodes": [{"id": "a"}, {"id": "b"}]}
        self._expect_value_error(
            "edges[0].style must be one of",
            edges=[{"from": "a", "to": "b", "style": "thick"}], **base,
        )
        self._expect_value_error(
            "edges[0].dir must be one of",
            edges=[{"from": "a", "to": "b", "dir": "forward"}], **base,
        )
        self._expect_value_error(
            "must be a number",
            edges=[{"from": "a", "to": "b", "weight": "2"}], **base,
        )
        self._expect_value_error(
            "exceeds the 10000.0 limit",
            edges=[{"from": "a", "to": "b", "weight": 10**6}], **base,
        )

    def test_error_dir_only_in_digraph(self) -> None:
        self._expect_value_error(
            "dir is only valid in the digraph mode", mode="graph",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[{"from": "a", "to": "b", "dir": "both"}],
        )

    def test_error_port_validation(self) -> None:
        base = {"mode": "digraph", "nodes": [{"id": "a"}, {"id": "b"}]}
        self._expect_value_error(
            "empty port after ':'",
            edges=[{"from": "a:", "to": "b"}], **base,
        )
        self._expect_value_error(
            "port must match [A-Za-z0-9_]+",
            edges=[{"from": "a:p-1", "to": "b"}], **base,
        )

    def test_error_cluster_validation(self) -> None:
        base = {"mode": "digraph", "nodes": [{"id": "a"}, {"id": "b"}]}
        self._expect_value_error(
            "node_ids must be a non-empty list",
            clusters=[{"name": "g"}], **base,
        )
        self._expect_value_error(
            "node_ids must be a non-empty list",
            clusters=[{"name": "g", "node_ids": []}], **base,
        )
        self._expect_value_error(
            "node_ids must be a non-empty list",
            clusters=[{"name": "g", "node_ids": "a"}], **base,
        )
        self._expect_value_error(
            "is not a declared node id",
            clusters=[{"name": "g", "node_ids": ["zz"]}], **base,
        )
        self._expect_value_error(
            "is already in another cluster",
            clusters=[
                {"name": "g1", "node_ids": ["a"]},
                {"name": "g2", "node_ids": ["a"]},
            ], **base,
        )

    def test_error_cluster_name_collisions(self) -> None:
        # cluster vs node id after the cluster_ prefix
        self._expect_value_error(
            "collides with a node id", mode="digraph",
            nodes=[{"id": "cluster_x"}],
            clusters=[{"name": "x", "node_ids": ["cluster_x"]}],
        )
        # two cluster names converging on cluster_a
        self._expect_value_error(
            "cluster names collide after sanitization", mode="digraph",
            nodes=[{"id": "a"}, {"id": "b"}],
            clusters=[
                {"name": "g", "node_ids": ["a"]},
                {"name": "cluster_g", "node_ids": ["b"]},
            ],
        )

    def test_error_caps(self) -> None:
        self._expect_value_error(
            "exceeds the 500-item limit", mode="digraph",
            nodes=[{"id": f"n{i}"} for i in range(501)],
        )
        self._expect_value_error(
            "exceeds the 1000-item limit", mode="digraph",
            nodes=[{"id": "a"}],
            edges=[{"from": "a", "to": "a"}] * 1001,
        )
        self._expect_value_error(
            "exceeds the 100-item limit", mode="digraph",
            nodes=[{"id": f"n{i}"} for i in range(2)],
            clusters=[
                {"name": f"c{i}", "node_ids": ["n0" if i == 0 else "n1"]}
                for i in range(101)
            ],
        )

    def test_error_name_validation(self) -> None:
        self._expect_value_error(
            "name must be a non-empty string", mode="digraph",
            name=123, nodes=[{"id": "a"}],
        )
        self._expect_value_error(
            "must not contain control characters", mode="digraph",
            name="a\nb", nodes=[{"id": "a"}],
        )

    def test_error_label_validation(self) -> None:
        self._expect_value_error(
            "nodes[0].label must be a non-empty string", mode="digraph",
            nodes=[{"id": "a", "label": ""}],
        )
        self._expect_value_error(
            "must not contain control characters other than newlines",
            mode="digraph", nodes=[{"id": "a", "label": "a\x00b"}],
        )
        self._expect_value_error(
            "exceeds the 2000-character limit", mode="digraph",
            nodes=[{"id": "a", "label": "x" * 2001}],
        )

    def test_error_source_validation(self) -> None:
        self._expect_value_error(
            "source must be a non-empty string", mode="validate", source=None
        )
        self._expect_value_error(
            "source must be a non-empty string", mode="validate", source=""
        )
        self._expect_value_error(
            "source must be a non-empty string", mode="validate", source=7
        )
        self._expect_value_error(
            "exceeds the 100000-character limit", mode="validate",
            source="digraph G {" + "a;" * 60_000 + "}",
        )
        self._expect_value_error(
            "source must be a non-empty string", mode="stats", source=None
        )

    # ------------------------------------------------------------------ #
    # package export parity
    # ------------------------------------------------------------------ #

    def test_direct_import_matches_package_export(self) -> None:
        self.assertIs(DotGraphTool, DirectDotGraphTool)


if __name__ == "__main__":
    unittest.main()
