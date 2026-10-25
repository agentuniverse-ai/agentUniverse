#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_mermaid_flow_tool.py

"""Offline unit tests for MermaidFlowTool.

The tool is built purely on the standard library and never renders
anything or touches the network, so this suite runs fully offline.
Every assertion is deterministic: the flowchart / sequence modes are
checked against exact expected Mermaid source strings (each shape
syntax form, each arrow style, label escaping including pipes and
Unicode, id sanitization with the reported mapping, the direction
option, sequence aliases / notes / dashed lines), and the lint mode
against exact issue payloads (including the classic bare 'end' node id
pitfall and dangling arrows).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import MermaidFlowTool
from agentuniverse.agent.action.tool.common_tool.mermaid_flow_tool import (
    MermaidFlowTool as DirectMermaidFlowTool,
)


class MermaidFlowToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib MermaidFlowTool."""

    def setUp(self) -> None:
        self.tool = MermaidFlowTool()

    # ------------------------------------------------------------------ #
    # flowchart mode
    # ------------------------------------------------------------------ #

    def test_flowchart_minimal_exact(self) -> None:
        result = self.tool.execute(
            mode="flowchart", nodes=[{"id": "a"}, {"id": "b"}]
        )
        self.assertEqual(
            result,
            {
                "mode": "flowchart",
                "direction": "TD",
                "result": "flowchart TD\n    a\n    b",
                "node_count": 2,
                "edge_count": 0,
            },
        )

    def test_flowchart_all_shapes_exact(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "r", "label": "n"},
                {"id": "ro", "label": "n", "shape": "round"},
                {"id": "st", "label": "n", "shape": "stadium"},
                {"id": "d", "label": "n", "shape": "diamond"},
                {"id": "h", "label": "n", "shape": "hexagon"},
                {"id": "c", "label": "n", "shape": "circle"},
                {"id": "p", "label": "n", "shape": "parallelogram"},
            ],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    r[n]\n"
            "    ro(n)\n"
            "    st([n])\n"
            "    d{n}\n"
            "    h{{n}}\n"
            "    c((n))\n"
            "    p[/n/]",
        )
        self.assertEqual(result["node_count"], 7)
        self.assertNotIn("id_mapping", result)

    def test_flowchart_arrow_styles_exact(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[
                {"from": "a", "to": "b"},
                {"from": "a", "to": "b", "arrow": "dotted"},
                {"from": "a", "to": "b", "arrow": "thick"},
                {"from": "a", "to": "b", "label": "x"},
                {"from": "a", "to": "b", "label": "y", "arrow": "dotted"},
                {"from": "a", "to": "b", "label": "z", "arrow": "thick"},
            ],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    a\n"
            "    b\n"
            "    a-->b\n"
            "    a-.->b\n"
            "    a==>b\n"
            "    a-->|x|b\n"
            "    a-.->|y|b\n"
            "    a==>|z|b",
        )
        self.assertEqual(result["edge_count"], 6)

    def test_flowchart_label_escaping_exact(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "n1", "label": "a|b"},
                {"id": "n2", "label": 'He said "hi"'},
                {"id": "n3", "label": "f(x) [y]"},
                {"id": "n4", "label": "héllo 世界 🌍"},
                {"id": "n5", "label": "a;b&c#d"},
            ],
            edges=[{"from": "n1", "to": "n4", "label": "yes|no"}],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    n1[a❘b]\n"
            '    n2["He said #quot;hi#quot;"]\n'
            '    n3["f(x) [y]"]\n'
            "    n4[héllo 世界 🌍]\n"
            '    n5["a;b&c#d"]\n'
            "    n1-->|yes❘no|n4",
        )

    def test_flowchart_id_sanitization_and_mapping(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "start node", "label": "Start"},
                {"id": "step-1"},
                {"id": "step.1", "label": "Step One", "shape": "round"},
                {"id": "end", "label": "Finish", "shape": "diamond"},
            ],
            edges=[
                {"from": "start node", "to": "step-1"},
                {"from": "step.1", "to": "end", "label": "done|ok"},
            ],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    start_node[Start]\n"
            "    step_1\n"
            "    step_1_2(Step One)\n"
            "    end_{Finish}\n"
            "    start_node-->step_1\n"
            "    step_1_2-->|done❘ok|end_",
        )
        self.assertEqual(
            result["id_mapping"],
            {
                "start node": "start_node",
                "step-1": "step_1",
                "step.1": "step_1_2",
                "end": "end_",
            },
        )

    def test_flowchart_shape_without_label_is_bare(self) -> None:
        result = self.tool.execute(
            mode="flowchart", nodes=[{"id": "a", "shape": "round"}]
        )
        self.assertEqual(result["result"], "flowchart TD\n    a")

    def test_flowchart_shape_none_defaults_to_rect(self) -> None:
        result = self.tool.execute(
            mode="flowchart", nodes=[{"id": "a", "label": "x", "shape": None}]
        )
        self.assertEqual(result["result"], "flowchart TD\n    a[x]")

    def test_flowchart_direction_lr(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            direction="LR",
            nodes=[{"id": "a", "label": "A"}, {"id": "b"}],
            edges=[{"from": "a", "to": "b"}],
        )
        self.assertEqual(result["direction"], "LR")
        self.assertEqual(
            result["result"],
            "flowchart LR\n    a[A]\n    b\n    a-->b",
        )

    def test_flowchart_self_loop_allowed(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[{"id": "a", "label": "A"}],
            edges=[{"from": "a", "to": "a", "label": "retry"}],
        )
        self.assertEqual(
            result["result"], "flowchart TD\n    a[A]\n    a-->|retry|a"
        )

    # ------------------------------------------------------------------ #
    # sequence mode
    # ------------------------------------------------------------------ #

    def test_sequence_minimal_exact(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Alice"}, {"name": "Bob"}],
            messages=[{"from": "Alice", "to": "Bob", "text": "hi"}],
        )
        self.assertEqual(
            result,
            {
                "mode": "sequence",
                "result": (
                    "sequenceDiagram\n"
                    "    participant Alice\n"
                    "    participant Bob\n"
                    "    Alice->Bob: hi"
                ),
                "participant_count": 2,
                "message_count": 1,
                "note_count": 0,
            },
        )

    def test_sequence_full_exact(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[
                {"name": "Alice"},
                {"name": "Bob", "as": "Bobby"},
                {"name": "Web Server"},
            ],
            messages=[
                {"from": "Alice", "to": "Bob", "text": "hi"},
                {"from": "Bob", "to": "Alice", "text": "ok", "kind": "dashed"},
                {"from": "Alice", "to": "Web Server", "text": "GET /api: v1"},
            ],
            notes=[
                {"over": "Alice", "text": "alone"},
                {"over": ["Alice", "Bob"], "text": "both"},
            ],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant Alice\n"
            "    participant Bob as Bobby\n"
            "    participant Web_Server as Web Server\n"
            "    Alice->Bob: hi\n"
            "    Bob-->Alice: ok\n"
            "    Alice->Web_Server: GET /api: v1\n"
            "    note over Alice: alone\n"
            "    note over Alice,Bob: both",
        )
        self.assertEqual(result["participant_count"], 3)
        self.assertEqual(result["message_count"], 3)
        self.assertEqual(result["note_count"], 2)
        self.assertEqual(result["id_mapping"], {"Web Server": "Web_Server"})

    def test_sequence_participant_named_end_sanitized(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "end"}, {"name": "Bob"}],
            messages=[{"from": "end", "to": "Bob", "text": "x"}],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant end_ as end\n"
            "    participant Bob\n"
            "    end_->Bob: x",
        )
        self.assertEqual(result["id_mapping"], {"end": "end_"})

    def test_sequence_explicit_alias_wins_over_auto_alias(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "Web Server", "as": "Srv"}],
            messages=[{"from": "Web Server", "to": "Web Server", "text": "x"}],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant Web_Server as Srv\n"
            "    Web_Server->Web_Server: x",
        )

    def test_sequence_notes_optional(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "B"}],
            messages=[{"from": "A", "to": "B", "text": "t"}],
        )
        self.assertEqual(result["note_count"], 0)
        self.assertNotIn("id_mapping", result)

    # ------------------------------------------------------------------ #
    # lint mode
    # ------------------------------------------------------------------ #

    def test_lint_valid_flowchart_ok(self) -> None:
        result = self.tool.execute(
            mode="lint", source="flowchart TD\n    a[Start]\n    b[End]\n    a-->|go|b"
        )
        self.assertEqual(
            result,
            {"mode": "lint", "ok": True, "lines_checked": 4, "issues": []},
        )

    def test_lint_graph_keyword_accepted(self) -> None:
        result = self.tool.execute(mode="lint", source="graph TD\n    a-->b")
        self.assertTrue(result["ok"])

    def test_lint_valid_sequence_with_alt_end_ok(self) -> None:
        # 'end' closes alt/loop blocks in sequence diagrams and is legal
        # there — the end check only applies to flowcharts.
        source = (
            "sequenceDiagram\n"
            "    Alice->Bob: hi\n"
            "    alt yes\n"
            "        Bob-->Alice: ok\n"
            "    end"
        )
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["lines_checked"], 5)

    def test_lint_missing_diagram_keyword(self) -> None:
        result = self.tool.execute(mode="lint", source="A-->B")
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["lines_checked"], 1)
        self.assertEqual(len(result["issues"]), 1)
        issue = result["issues"][0]
        self.assertEqual(issue["line"], 1)
        self.assertEqual(issue["check"], "diagram_keyword")
        self.assertIn("flowchart", issue["message"])

    def test_lint_comments_only_source(self) -> None:
        result = self.tool.execute(mode="lint", source="%% just a comment")
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["issues"][0]["check"], "diagram_keyword")
        self.assertEqual(result["issues"][0]["line"], 1)

    def test_lint_unbalanced_quotes_and_end_node_id_exact(self) -> None:
        result = self.tool.execute(
            mode="lint", source='flowchart TD\n    a["unclosed\n    end-->b'
        )
        self.assertEqual(
            result,
            {
                "mode": "lint",
                "ok": False,
                "lines_checked": 3,
                "issues": [
                    {
                        "line": 2,
                        "check": "unbalanced_quotes",
                        "message": (
                            "line has an odd number of double-quote "
                            "characters — quotes in mermaid must be paired"
                        ),
                    },
                    {
                        "line": 3,
                        "check": "end_node_id",
                        "message": (
                            "'end' is a reserved keyword in flowcharts and "
                            "cannot be used as a node id — rename the node "
                            "(e.g. 'end1')"
                        ),
                    },
                ],
            },
        )

    def test_lint_end_closing_subgraph_not_flagged(self) -> None:
        source = (
            "flowchart TD\n"
            "    subgraph s\n"
            "        a-->b\n"
            "    end\n"
            "    c-->d"
        )
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    def test_lint_extra_end_beyond_subgraph_flagged(self) -> None:
        source = (
            "flowchart TD\n"
            "    subgraph s\n"
            "        a-->b\n"
            "    end\n"
            "    end-->x"
        )
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["ok"], False)
        self.assertEqual(len(result["issues"]), 1)
        self.assertEqual(result["issues"][0]["line"], 5)
        self.assertEqual(result["issues"][0]["check"], "end_node_id")

    def test_lint_dangling_arrows(self) -> None:
        result = self.tool.execute(
            mode="lint", source="flowchart TD\n    a-->\n    -->b\n    a-->b"
        )
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["lines_checked"], 4)
        self.assertEqual(len(result["issues"]), 2)
        self.assertEqual(result["issues"][0]["line"], 2)
        self.assertEqual(result["issues"][0]["check"], "dangling_arrow")
        self.assertIn("no target endpoint", result["issues"][0]["message"])
        self.assertEqual(result["issues"][1]["line"], 3)
        self.assertEqual(result["issues"][1]["check"], "dangling_arrow")
        self.assertIn("no source endpoint", result["issues"][1]["message"])

    def test_lint_sequence_missing_source_arrow(self) -> None:
        result = self.tool.execute(
            mode="lint", source="sequenceDiagram\n    ->Bob: hi"
        )
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["issues"][0]["line"], 2)
        self.assertEqual(result["issues"][0]["check"], "dangling_arrow")

    def test_lint_comment_lines_ignored(self) -> None:
        source = "flowchart TD\n    %% end --> x\n    a-->b"
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["lines_checked"], 3)

    def test_lint_quoted_label_containing_end_not_flagged(self) -> None:
        source = 'flowchart TD\n    a["the end"]\n    a-->b'
        result = self.tool.execute(mode="lint", source=source)
        self.assertEqual(result["issues"], [])

    def test_lint_generated_output_is_clean(self) -> None:
        generated = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "start node", "label": 'Start "now"'},
                {"id": "end", "label": "a|b", "shape": "stadium"},
            ],
            edges=[{"from": "start node", "to": "end", "label": "go|run"}],
        )["result"]
        result = self.tool.execute(mode="lint", source=generated)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="diagram", nodes=[{"id": "a"}])
        self.assert_invalid(mode=None)
        self.assert_invalid(mode=123)

    def test_invalid_direction(self) -> None:
        nodes = [{"id": "a"}]
        for bad in ("TB", "td", "lr", "", "DOWN"):
            with self.subTest(direction=bad):
                self.assert_invalid(mode="flowchart", direction=bad, nodes=nodes)
        self.assert_invalid(mode="flowchart", direction=True, nodes=nodes)

    def test_invalid_nodes_container(self) -> None:
        for bad in (None, "a", {}, 42, [{"id": "a"}, "b"], [None], [5]):
            with self.subTest(nodes=bad):
                self.assert_invalid(mode="flowchart", nodes=bad)
        self.assert_invalid(mode="flowchart", nodes=[])

    def test_invalid_node_ids(self) -> None:
        for bad_id in (None, "", 5, True, "a\nb", "a\tb", "a" * 201):
            with self.subTest(node_id=bad_id):
                self.assert_invalid(
                    mode="flowchart", nodes=[{"id": bad_id, "label": "x"}]
                )
        self.assert_invalid(mode="flowchart", nodes=[{"label": "no id"}])

    def test_duplicate_node_id(self) -> None:
        self.assert_invalid(
            mode="flowchart", nodes=[{"id": "a"}, {"id": "a"}]
        )

    def test_invalid_shape(self) -> None:
        self.assert_invalid(
            mode="flowchart",
            nodes=[{"id": "a", "label": "x", "shape": "blob"}],
        )
        self.assert_invalid(
            mode="flowchart", nodes=[{"id": "a", "label": "x", "shape": 7}]
        )

    def test_invalid_labels(self) -> None:
        self.assert_invalid(mode="flowchart", nodes=[{"id": "a", "label": "x\ny"}])
        self.assert_invalid(mode="flowchart", nodes=[{"id": "a", "label": ""}])
        self.assert_invalid(mode="flowchart", nodes=[{"id": "a", "label": 9}])
        self.assert_invalid(
            mode="flowchart",
            nodes=[{"id": "a"}],
            edges=[{"from": "a", "to": "a", "label": "x\ny"}],
        )
        self.assert_invalid(
            mode="flowchart", nodes=[{"id": "a", "label": "a" * 2001}]
        )

    def test_edge_endpoints_must_reference_declared_ids(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="flowchart",
                nodes=[{"id": "a"}],
                edges=[
                    {"from": "x", "to": "a"},
                    {"from": "a", "to": "y"},
                    {"from": "x", "to": "y"},
                ],
            )
        message = str(ctx.exception)
        self.assertIn("'x'", message)
        self.assertIn("'y'", message)
        self.assertIn("undeclared node ids", message)

    def test_invalid_edges_container_and_fields(self) -> None:
        nodes = [{"id": "a"}, {"id": "b"}]
        self.assert_invalid(mode="flowchart", nodes=nodes, edges={"from": "a"})
        self.assert_invalid(mode="flowchart", nodes=nodes, edges=["a-->b"])
        self.assert_invalid(mode="flowchart", nodes=nodes, edges=[{"to": "a"}])
        self.assert_invalid(
            mode="flowchart", nodes=nodes, edges=[{"from": "a"}]
        )
        self.assert_invalid(
            mode="flowchart",
            nodes=nodes,
            edges=[{"from": "a", "to": "b", "arrow": "dashed-line"}],
        )
        self.assert_invalid(
            mode="flowchart",
            nodes=nodes,
            edges=[{"from": "a", "to": "b", "arrow": 4}],
        )

    def test_node_count_limit(self) -> None:
        self.assert_invalid(
            mode="flowchart", nodes=[{"id": f"n{i}"} for i in range(501)]
        )

    def test_invalid_participants(self) -> None:
        for bad in (None, [], "Alice", [{}], [5], [{"name": ""}], [{"name": 8}]):
            with self.subTest(participants=bad):
                self.assert_invalid(
                    mode="sequence",
                    participants=bad,
                    messages=[{"from": "A", "to": "B", "text": "t"}],
                )
        self.assert_invalid(
            mode="sequence",
            participants=[{"name": "A"}, {"name": "A"}],
            messages=[{"from": "A", "to": "A", "text": "t"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=[{"name": "A", "as": ""}],
            messages=[{"from": "A", "to": "A", "text": "t"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=[{"name": "A", "as": "x\ny"}],
            messages=[{"from": "A", "to": "A", "text": "t"}],
        )

    def test_invalid_messages(self) -> None:
        participants = [{"name": "A"}, {"name": "B"}]
        for bad in (None, [], "m", [{}], [5]):
            with self.subTest(messages=bad):
                self.assert_invalid(
                    mode="sequence", participants=participants, messages=bad
                )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=[{"to": "B", "text": "t"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=[{"from": "A", "to": "B", "text": ""}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=[{"from": "A", "to": "B", "text": "t", "kind": "solid-line"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=[{"from": "A", "to": "B", "text": "t", "kind": 1}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=[{"from": "A", "to": "B", "text": "a" * 2001}],
        )

    def test_message_endpoints_must_reference_declared_participants(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(
                mode="sequence",
                participants=[{"name": "A"}],
                messages=[
                    {"from": "B", "to": "A", "text": "x"},
                    {"from": "A", "to": "C", "text": "y"},
                ],
            )
        message = str(ctx.exception)
        self.assertIn("'B'", message)
        self.assertIn("'C'", message)
        self.assertIn("undeclared participants", message)

    def test_invalid_notes(self) -> None:
        participants = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        messages = [{"from": "A", "to": "B", "text": "t"}]
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=[{"over": "Z", "text": "n"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=[{"over": ["A", "B", "C"], "text": "n"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=[{"over": [], "text": "n"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=[{"over": ["A", 5], "text": "n"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=[{"over": "A"}],
        )
        self.assert_invalid(
            mode="sequence",
            participants=participants,
            messages=messages,
            notes=["note"],
        )

    def test_invalid_lint_source(self) -> None:
        for bad in (None, 123, True, b"flowchart TD"):
            with self.subTest(source=bad):
                self.assert_invalid(mode="lint", source=bad)
        self.assert_invalid(mode="lint", source="")
        self.assert_invalid(mode="lint", source="   \n  ")

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_generation_is_deterministic(self) -> None:
        kwargs = dict(
            mode="flowchart",
            nodes=[{"id": "a b", "label": "L"}, {"id": "end"}],
            edges=[{"from": "a b", "to": "end", "arrow": "dotted"}],
        )
        first = self.tool.execute(**kwargs)
        second = self.tool.execute(**kwargs)
        self.assertEqual(first, second)

    def test_id_map_deterministic_across_200_seeded_sets(self) -> None:
        import random
        import re

        rng = random.Random(20261020)
        alphabet = "ab-_ .9éZ|[]{}\"'#;汉字"
        for _ in range(200):
            raw_ids = [
                "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 10)))
                for _ in range(rng.randint(1, 12))
            ]
            raw_ids = [raw for raw in raw_ids if raw]
            if not raw_ids:
                continue
            with self.subTest(raw_ids=raw_ids):
                first = self.tool._build_id_map(raw_ids)
                second = self.tool._build_id_map(raw_ids)
                self.assertEqual(first, second)
                targets = list(first.values())
                self.assertEqual(len(set(targets)), len(targets))
                for sanitized in targets:
                    self.assertTrue(
                        re.fullmatch(r"[A-Za-z0-9_]+", sanitized), sanitized
                    )

    # ------------------------------------------------------------------ #
    # Reserved keyword ids (verified against the mermaid v11 parser)
    # ------------------------------------------------------------------ #

    def test_flowchart_reserved_keyword_ids_renamed(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "style", "label": "S"},
                {"id": "class"},
                {"id": "classDef"},
                {"id": "linkStyle"},
                {"id": "subgraph"},
                {"id": "graph"},
                {"id": "flowchart"},
                {"id": "Style"},  # capitalized variants are legal ids
            ],
            edges=[
                {"from": "style", "to": "class"},
                {"from": "graph", "to": "flowchart"},
            ],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    style_[S]\n"
            "    class_\n"
            "    classDef_\n"
            "    linkStyle_\n"
            "    subgraph_\n"
            "    graph_\n"
            "    flowchart_\n"
            "    Style\n"
            "    style_-->class_\n"
            "    graph_-->flowchart_",
        )
        self.assertEqual(
            result["id_mapping"],
            {
                "style": "style_",
                "class": "class_",
                "classDef": "classDef_",
                "linkStyle": "linkStyle_",
                "subgraph": "subgraph_",
                "graph": "graph_",
                "flowchart": "flowchart_",
            },
        )

    def test_sequence_reserved_keyword_names_renamed_case_insensitive(
            self) -> None:
        for name in ("note", "Note", "NOTE", "over", "loop", "actor",
                     "participant", "autonumber", "alt", "opt", "par",
                     "else", "option", "critical", "break", "box", "rect",
                     "activate", "deactivate", "and", "end"):
            with self.subTest(name=name):
                result = self.tool.execute(
                    mode="sequence",
                    participants=[{"name": name}, {"name": "B"}],
                    messages=[{"from": name, "to": "B", "text": "x"}],
                )
                # The sanitized id is the name plus an underscore and the
                # original spelling is kept as the display alias.
                lines = result["result"].split("\n")
                self.assertEqual(
                    lines[1], f"    participant {name}_ as {name}"
                )
                self.assertEqual(result["id_mapping"], {name: f"{name}_"})

    def test_edge_label_entity_escaping_exact(self) -> None:
        result = self.tool.execute(
            mode="flowchart",
            nodes=[{"id": "a"}, {"id": "b"}],
            edges=[
                {"from": "a", "to": "b", "label": 'say "hi"'},
                {"from": "b", "to": "a", "label": "arr[0]"},
                {"from": "a", "to": "b", "label": "{x}"},
                {"from": "b", "to": "a", "label": "f(x)"},
                {"from": "a", "to": "b", "label": "a|b"},
            ],
        )
        self.assertEqual(
            result["result"],
            "flowchart TD\n"
            "    a\n"
            "    b\n"
            "    a-->|say #quot;hi#quot;|b\n"
            "    b-->|arr#91;0#93;|a\n"
            "    a-->|#123;x#125;|b\n"
            "    b-->|f#40;x#41;|a\n"
            "    a-->|a❘b|b",
        )

    def test_sequence_semicolon_escaping_exact(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A", "as": "Foo;Bar"}],
            messages=[{"from": "A", "to": "A", "text": "one; two"}],
            notes=[{"over": "A", "text": "n; m"}],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant A as Foo#59;Bar\n"
            "    A->A: one#59; two\n"
            "    note over A: n#59; m",
        )

    def test_sequence_alias_quote_escaping_exact(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": "A", "as": 'Bob "The"'}],
            messages=[{"from": "A", "to": "A", "text": "x"}],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant A as Bob #quot;The#quot;\n"
            "    A->A: x",
        )

    def test_sequence_auto_alias_with_specials_escaped(self) -> None:
        result = self.tool.execute(
            mode="sequence",
            participants=[{"name": 'Bob "X"; Y'}],
            messages=[{"from": 'Bob "X"; Y', "to": 'Bob "X"; Y', "text": "x"}],
        )
        self.assertEqual(
            result["result"],
            "sequenceDiagram\n"
            "    participant Bob__X___Y as Bob #quot;X#quot;#59; Y\n"
            "    Bob__X___Y->Bob__X___Y: x",
        )
        self.assertEqual(
            result["id_mapping"], {'Bob "X"; Y': "Bob__X___Y"}
        )

    def test_generated_output_with_reserved_and_special_lints_clean(
            self) -> None:
        generated = self.tool.execute(
            mode="flowchart",
            nodes=[
                {"id": "style", "label": "The end"},
                {"id": "end", "label": "a|b"},
            ],
            edges=[
                {"from": "style", "to": "end", "label": 'the end "now"'},
                {"from": "end", "to": "style", "label": "f(x) [y]"},
            ],
        )["result"]
        result = self.tool.execute(mode="lint", source=generated)
        self.assertEqual(result["issues"], [])
        self.assertTrue(result["ok"])

    def test_generated_sequence_output_with_specials_lints_clean(
            self) -> None:
        tricky = 'Bob "The'  # quote and no terminator: hostile alias text
        generated = self.tool.execute(
            mode="sequence",
            participants=[{"name": "note"}, {"name": tricky}],
            messages=[
                {"from": "note", "to": tricky, "text": "see -->"},
                {"from": tricky, "to": "note", "text": 'say "hi'},
            ],
            notes=[{"over": "note", "text": "one; two ->"}],
        )["result"]
        result = self.tool.execute(mode="lint", source=generated)
        self.assertEqual(result["issues"], [])

    # ------------------------------------------------------------------ #
    # Lint: reserved keyword detection (beyond 'end')
    # ------------------------------------------------------------------ #

    def test_lint_reserved_flowchart_keyword_ids_flagged(self) -> None:
        for source, line in (
            ("flowchart TD\n    style-->b", 2),
            ("flowchart TD\n    style[label]", 2),
            ("flowchart TD\n    a-->class", 2),
            ("flowchart TD\n    a-->subgraph", 2),
            ("flowchart TD\n    graph-->b", 2),
            ("flowchart TD\n    a-->linkStyle", 2),
            ("flowchart TD\n    classDef-->b", 2),
            ("flowchart TD\n    flowchart-->b", 2),
        ):
            with self.subTest(source=source):
                result = self.tool.execute(mode="lint", source=source)
                self.assertFalse(result["ok"])
                self.assertEqual(result["issues"][0]["line"], line)
                self.assertEqual(
                    result["issues"][0]["check"], "reserved_word_id"
                )

    def test_lint_capitalized_keyword_ids_not_flagged(self) -> None:
        # Flowchart keyword matching is exact-case: capitalized variants
        # such as 'Style'/'Class'/'End' are legal Mermaid node ids.
        result = self.tool.execute(
            mode="lint",
            source="flowchart TD\n    Style-->b\n    a-->Class\n    End-->x",
        )
        self.assertEqual(result["issues"], [])

    def test_lint_reserved_sequence_actor_names_flagged(self) -> None:
        for source in (
            "sequenceDiagram\n    note->A: hi",
            "sequenceDiagram\n    Note->A: hi",
            "sequenceDiagram\n    END->A: hi",
            "sequenceDiagram\n    loop->A: hi",
            "sequenceDiagram\n    actor->A: hi",
            "sequenceDiagram\n    participant->A: hi",
            "sequenceDiagram\n    autonumber->A: hi",
        ):
            with self.subTest(source=source):
                result = self.tool.execute(mode="lint", source=source)
                self.assertFalse(result["ok"])
                self.assertEqual(
                    result["issues"][0]["check"], "reserved_word_id"
                )

    def test_lint_legit_keyword_statements_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint",
            source=(
                "sequenceDiagram\n"
                "    autonumber\n"
                "    participant A\n"
                "    actor Bob\n"
                "    note right of A: hi\n"
                "    loop check\n"
                "        A->Bob: ping\n"
                "    end\n"
                "    rect rgb(1,2,3)\n"
                "        A->A: ok\n"
                "    end"
            ),
        )
        self.assertEqual(result["issues"], [])

    def test_lint_flowchart_class_statements_not_flagged(self) -> None:
        result = self.tool.execute(
            mode="lint",
            source=(
                "flowchart TD\n"
                "    a-->b\n"
                "    class a,b fill:red\n"
                "    classDef default fill:#f9f\n"
                "    click a callback"
            ),
        )
        self.assertEqual(result["issues"], [])

    def test_lint_end_word_inside_labels_not_flagged(self) -> None:
        for source in (
            "flowchart TD\n    n1[The end]\n    n1 --> b2",
            "flowchart TD\n    a-->|the end|b",
            "flowchart TD\n    a[end label]\n    a-->|weekend trip|b",
        ):
            with self.subTest(source=source):
                result = self.tool.execute(mode="lint", source=source)
                self.assertEqual(result["issues"], [])

    def test_lint_sequence_free_text_quote_and_arrow_not_flagged(self) -> None:
        for source in (
            'sequenceDiagram\n    participant A\n    A->A: he said "hi',
            'sequenceDiagram\n    participant A\n    A->A: see -->',
            "sequenceDiagram\n    participant A\n    A->A: upgrade ->",
            'sequenceDiagram\n    participant A\n    note over A: so "called"',
        ):
            with self.subTest(source=source):
                result = self.tool.execute(mode="lint", source=source)
                self.assertEqual(result["issues"], [])

    def test_lint_reserved_word_check_requires_keyword_slot(self) -> None:
        # Words containing a keyword as a substring are fine.
        result = self.tool.execute(
            mode="lint",
            source="flowchart TD\n    styles-->classification\n    noting-->b",
        )
        self.assertEqual(result["issues"], [])

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectMermaidFlowTool, MermaidFlowTool)
        self.assertEqual(self.tool.name, "mermaid_flow_tool")
        self.assertIn("flowchart", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("MermaidFlowTool", __all__)


if __name__ == "__main__":
    unittest.main()
