#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for ConditionNode multi-branch evaluation and Graph dead-end.

1. ConditionNode previously read only branches[0].conditions[0]; every other
   branch was dead configuration. Now evaluates each branch in order and
   picks the first whose conditions ALL match (AND semantics).
2. Graph._get_next_node previously fell through to an implicit `return None`
   when a node emitted a source_handler no successor edge matched, silently
   ending the workflow with empty output. Now raises ValueError naming the
   unmatched handler and the available ones.
"""

import unittest
from unittest.mock import MagicMock


def _literal_input(value) -> "NodeInputParams":
    """Build a NodeInputParams whose value is a literal (not a reference).

    InputValueParams.content is typed as Optional[Union[List, str]], so
    coerce scalars to str (comparators still work on str equality). None is
    preserved for the 'blank' comparator case.
    """
    from agentuniverse.workflow.node.node_config import NodeInputParams, InputValueParams
    if value is None:
        content = None
    elif isinstance(value, (list, str)):
        content = value
    else:
        content = str(value)
    return NodeInputParams(value=InputValueParams(type='literal', content=content))


def _condition(compare: str, left, right=None):
    from agentuniverse.workflow.node.node_config import ConditionParams
    return ConditionParams(
        compare=compare,
        left=_literal_input(left),
        right=_literal_input(right) if right is not None else None,
    )


def _branch(name: str, conditions):
    from agentuniverse.workflow.node.node_config import ConditionBranchParams
    return ConditionBranchParams(name=name, conditions=conditions)


def _build_node(branches):
    from agentuniverse.workflow.node.condition_node import ConditionNode
    from agentuniverse.workflow.node.node_config import ConditionNodeInputParams
    # Build via the normal constructor: Node.__init__ reads kwargs['data'].
    node = ConditionNode(id="cond1", data={
        "inputs": ConditionNodeInputParams(branches=branches).model_dump(),
    })
    return node


class TestConditionNodeMultiBranch(unittest.TestCase):

    def _run(self, node, workflow_output=None):
        wo = workflow_output or MagicMock()
        wo.workflow_parameters = {}
        return node._run(wo)

    def test_first_branch_matches_when_first_condition_true(self):
        node = _build_node([
            _branch("a", [_condition("equal", 1, 1)]),
            _branch("b", [_condition("equal", 2, 2)]),
        ])
        out = self._run(node)
        self.assertEqual(out.edge_source_handler, "a")

    def test_second_branch_is_reachable_when_first_does_not_match(self):
        # The bug: only branches[0] was evaluated, so "b" was dead and the
        # node fell through to branch-default even though b's condition held.
        node = _build_node([
            _branch("a", [_condition("equal", 1, 999)]),
            _branch("b", [_condition("equal", 2, 2)]),
        ])
        out = self._run(node)
        self.assertEqual(out.edge_source_handler, "b",
                         "second branch must be reachable when first does not match")

    def test_no_branch_matches_falls_through_to_default(self):
        node = _build_node([
            _branch("a", [_condition("equal", 1, 2)]),
            _branch("b", [_condition("equal", 3, 4)]),
        ])
        out = self._run(node)
        self.assertEqual(out.edge_source_handler, "branch-default")

    def test_branch_requires_all_conditions_to_match(self):
        # AND semantics: a branch with two conditions matches only when both hold.
        node = _build_node([
            _branch("a", [_condition("equal", 1, 1), _condition("equal", 2, 999)]),
            _branch("b", [_condition("equal", 3, 3)]),
        ])
        out = self._run(node)
        # a's second condition is false, so b wins.
        self.assertEqual(out.edge_source_handler, "b")

    def test_unknown_comparator_fails_closed(self):
        # An unknown compare value must NOT silently match; the branch falls
        # through to default instead of producing a wrong routing.
        node = _build_node([
            _branch("a", [_condition("not_a_real_comparator", 1, 1)]),
        ])
        out = self._run(node)
        self.assertEqual(out.edge_source_handler, "branch-default")

    def test_not_equal_and_blank_comparators(self):
        node = _build_node([
            _branch("a", [_condition("not_equal", "x", "y")]),
        ])
        self.assertEqual(self._run(node).edge_source_handler, "a")

        node = _build_node([
            _branch("a", [_condition("blank", None, None)]),
        ])
        self.assertEqual(self._run(node).edge_source_handler, "a")


class TestGraphDeadEndRaises(unittest.TestCase):
    """_get_next_node must raise when a source_handler matches no successor."""

    def _build_graph(self):
        from agentuniverse.workflow.graph.graph import Graph
        graph = Graph()
        n1 = MagicMock(id="n1")
        n2 = MagicMock(id="n2")
        graph.add_node("n1", instance=n1, type="condition")
        graph.add_node("n2", instance=n2, type="end")
        graph.add_edge("n1", "n2", source_handler="branch-a")
        return graph

    def test_unmatched_source_handler_raises_value_error(self):
        graph = self._build_graph()
        workflow_output = MagicMock()
        node_output = MagicMock()
        node_output.edge_source_handler = "branch-z"  # not "branch-a"
        workflow_output.workflow_node_results = {"n1": node_output}

        predecessor = MagicMock()
        predecessor.id = "n1"

        with self.assertRaises(ValueError) as ctx:
            graph._get_next_node(workflow_output, nodes=["n1", "n2"],
                                 predecessor_node=predecessor)
        self.assertIn("branch-z", str(ctx.exception))
        self.assertIn("branch-a", str(ctx.exception))

    def test_matched_source_handler_returns_successor(self):
        graph = self._build_graph()
        n2 = graph.nodes["n2"]["instance"]
        workflow_output = MagicMock()
        node_output = MagicMock()
        node_output.edge_source_handler = "branch-a"
        workflow_output.workflow_node_results = {"n1": node_output}

        predecessor = MagicMock()
        predecessor.id = "n1"
        result = graph._get_next_node(workflow_output, nodes=["n1", "n2"],
                                      predecessor_node=predecessor)
        self.assertIs(result, n2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
