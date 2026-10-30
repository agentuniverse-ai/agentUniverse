#!/usr/bin/env python3

import unittest
from copy import deepcopy

import networkx as nx

from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _start_node_config(node_id: str) -> dict:
    """Build a start node configuration exposing one output param named `input`."""
    return {
        "id": node_id,
        "type": "start",
        "data": {"outputs": [{"name": "input"}]},
    }


def _end_node_config(node_id: str, template: str = "result: {{input}}") -> dict:
    """Build an end node configuration rendering `template` with the start node output."""
    return {
        "id": node_id,
        "type": "end",
        "data": {
            "inputs": {
                "prompt": {"value": template},
                "input_param": [
                    {"name": "input", "value": {"type": "reference", "content": ["1", "input"]}},
                ],
            },
            "outputs": [{"name": "output"}],
        },
    }


def _condition_node_config(node_id: str, expected: str) -> dict:
    """Build an ifelse node comparing the start node output with `expected` on equality."""
    return {
        "id": node_id,
        "type": "ifelse",
        "data": {
            "inputs": {
                "branches": [
                    {
                        "name": "branch-1",
                        "conditions": [
                            {
                                "compare": "equal",
                                "left": {"name": "left", "value": {"type": "reference", "content": ["1", "input"]}},
                                "right": {"name": "right", "value": {"type": "constant", "content": expected}},
                            }
                        ],
                    }
                ],
            },
        },
    }


def _edge(source_node_id: str, target_node_id: str, source_handler: str | None = None) -> dict:
    """Build an edge configuration, optionally carrying a source handler."""
    edge = {"source_node_id": source_node_id, "target_node_id": target_node_id}
    if source_handler is not None:
        edge["source_handler"] = source_handler
    return edge


def _linear_config() -> dict:
    """Build a minimal start -> end workflow configuration."""
    return {
        "nodes": [_start_node_config("1"), _end_node_config("2")],
        "edges": [_edge("1", "2")],
    }


def _branching_config() -> dict:
    """Build a start -> ifelse -> (branch-1 / branch-default) workflow configuration."""
    return {
        "nodes": [
            _start_node_config("1"),
            _condition_node_config("2", "hello"),
            _end_node_config("3"),
            _end_node_config("4"),
        ],
        "edges": [
            _edge("1", "2"),
            _edge("2", "3", "branch-1"),
            _edge("2", "4", "branch-default"),
        ],
    }


class TestGraphBuild(unittest.TestCase):
    """Tests for Graph.build validation and node/edge registration."""

    def test_build_raises_when_nodes_empty(self):
        with self.assertRaises(ValueError) as ctx:
            Graph().build("wf", {"edges": [_edge("1", "2")]})
        self.assertIn("nodes configuration is empty", str(ctx.exception))

    def test_build_raises_when_edges_empty(self):
        config = {"nodes": [_start_node_config("1")]}
        with self.assertRaises(ValueError) as ctx:
            Graph().build("wf", config)
        self.assertIn("edges configuration is empty", str(ctx.exception))

    def test_build_raises_on_unsupported_node_type(self):
        config = {
            "nodes": [_start_node_config("1"), {"id": "2", "type": "unsupported"}],
            "edges": [_edge("1", "2")],
        }
        with self.assertRaises(ValueError) as ctx:
            Graph().build("wf", config)
        self.assertIn("node type is not supported", str(ctx.exception))

    def test_build_raises_on_cyclic_graph(self):
        config = {
            "nodes": [_start_node_config("1"), _end_node_config("2"), _end_node_config("3")],
            "edges": [_edge("1", "2"), _edge("2", "3"), _edge("3", "2")],
        }
        with self.assertRaises(ValueError) as ctx:
            Graph().build("wf", config)
        self.assertIn("does not form a DAG", str(ctx.exception))

    def test_build_registers_nodes_edges_and_instances(self):
        graph = Graph().build("wf", _linear_config())
        self.assertEqual(set(graph.nodes), {"1", "2"})
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.nodes["1"]["type"], NodeEnum.START.value)
        self.assertEqual(graph.nodes["2"]["type"], NodeEnum.END.value)
        self.assertIsInstance(graph.nodes["1"]["instance"], StartNode)
        self.assertEqual(graph.get_edge_data("1", "2").get("source_handler"), None)

    def test_build_does_not_mutate_node_config(self):
        config = _linear_config()
        original = deepcopy(config)
        Graph().build("wf", config)
        self.assertEqual(config, original)

    def test_build_skips_duplicate_node_id(self):
        config = {
            "nodes": [_start_node_config("1"), _end_node_config("2"), _end_node_config("2")],
            "edges": [_edge("1", "2")],
        }
        graph = Graph().build("wf", config)
        self.assertEqual(set(graph.nodes), {"1", "2"})


class TestGraphRun(unittest.TestCase):
    """Tests for the Graph.run scheduling loop."""

    def test_run_executes_start_to_end(self):
        graph = Graph().build("wf", _linear_config())
        workflow_output = WorkflowOutput(
            workflow_id="wf",
            workflow_start_params={"input": "hello"},
        )
        graph.run(workflow_output)

        self.assertEqual(set(workflow_output.workflow_node_results), {"1", "2"})
        self.assertEqual(workflow_output.workflow_end_params.get("output"), "result: hello")
        self.assertEqual(workflow_output.workflow_node_results["1"].status, NodeStatusEnum.SUCCEEDED)

    def test_run_routes_to_matching_branch(self):
        graph = Graph().build("wf", _branching_config())
        workflow_output = WorkflowOutput(
            workflow_id="wf",
            workflow_start_params={"input": "hello"},
        )
        graph.run(workflow_output)

        # The equal condition matches, so only the `branch-1` end node runs.
        self.assertIn("3", workflow_output.workflow_node_results)
        self.assertNotIn("4", workflow_output.workflow_node_results)
        self.assertEqual(workflow_output.workflow_end_params.get("output"), "result: hello")

    def test_run_routes_to_default_branch(self):
        graph = Graph().build("wf", _branching_config())
        workflow_output = WorkflowOutput(
            workflow_id="wf",
            workflow_start_params={"input": "world"},
        )
        graph.run(workflow_output)

        # The equal condition fails, so the `branch-default` end node runs.
        self.assertNotIn("3", workflow_output.workflow_node_results)
        self.assertIn("4", workflow_output.workflow_node_results)
        self.assertEqual(workflow_output.workflow_end_params.get("output"), "result: world")

    def test_run_stops_after_end_node(self):
        config = {
            "nodes": [
                _start_node_config("1"),
                _end_node_config("2"),
                _end_node_config("3"),
            ],
            "edges": [_edge("1", "2"), _edge("2", "3")],
        }
        graph = Graph().build("wf", config)
        workflow_output = WorkflowOutput(
            workflow_id="wf",
            workflow_start_params={"input": "hello"},
        )
        graph.run(workflow_output)

        # Execution terminates at the first END node.
        self.assertIn("2", workflow_output.workflow_node_results)
        self.assertNotIn("3", workflow_output.workflow_node_results)


class TestGraphInternals(unittest.TestCase):
    """Tests for the Graph internal helpers driving the scheduling loop."""

    def setUp(self):
        self.graph = Graph().build("wf", _linear_config())
        self.workflow_output = WorkflowOutput(
            workflow_id="wf",
            workflow_start_params={"input": "hello"},
        )

    def test_get_next_node_returns_start_without_predecessor(self):
        sorted_nodes = list(nx.topological_sort(self.graph))
        next_node = self.graph._get_next_node(self.workflow_output, sorted_nodes, None)
        self.assertEqual(next_node.type, NodeEnum.START)
        self.assertEqual(next_node.id, "1")

    def test_get_next_node_returns_first_successor_without_handler(self):
        start_instance = self.graph.nodes["1"]["instance"]
        self.graph._run_node(cur_node=start_instance, workflow_output=self.workflow_output)

        sorted_nodes = list(nx.topological_sort(self.graph))
        next_node = self.graph._get_next_node(self.workflow_output, sorted_nodes, start_instance)
        self.assertEqual(next_node.id, "2")

    def test_get_next_node_returns_none_without_successors(self):
        self.graph.run(self.workflow_output)
        end_instance = self.graph.nodes["2"]["instance"]

        sorted_nodes = list(nx.topological_sort(self.graph))
        self.assertIsNone(self.graph._get_next_node(self.workflow_output, sorted_nodes, end_instance))

    def test_run_node_records_node_output(self):
        start_instance = self.graph.nodes["1"]["instance"]
        self.graph._run_node(cur_node=start_instance, workflow_output=self.workflow_output)

        node_output = self.workflow_output.workflow_node_results.get("1")
        self.assertIsNotNone(node_output)
        self.assertEqual(node_output.node_id, "1")
        self.assertEqual(node_output.status, NodeStatusEnum.SUCCEEDED)
        self.assertEqual(self.workflow_output.workflow_parameters["1"][0].value, "hello")

    def test_has_node_been_executed(self):
        self.assertFalse(Graph._has_node_been_executed(self.workflow_output, "1"))
        self.workflow_output.workflow_node_results["1"] = None
        self.assertTrue(Graph._has_node_been_executed(self.workflow_output, "1"))


if __name__ == "__main__":
    unittest.main()
