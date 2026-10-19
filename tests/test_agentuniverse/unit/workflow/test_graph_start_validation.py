"""Malformed graphs must not silently produce an empty workflow result."""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.start_node import StartNode


def load_graph():
    # Avoid optional Agent/Knowledge/LLM imports from the full node registry.
    registry = ModuleType("agentuniverse.workflow.node.node_constant")
    registry.NODE_CLS_MAPPING = {"start": StartNode, "end": EndNode}
    graph_path = Path(__file__).parents[4] / "agentuniverse/workflow/graph/graph.py"
    spec = importlib.util.spec_from_file_location("_graph_start_test", graph_path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"agentuniverse.workflow.node.node_constant": registry}):
        spec.loader.exec_module(module)
    return module.Graph


@pytest.mark.parametrize("types", [["end", "end"], ["start", "start"]])
def test_graph_rejects_missing_or_ambiguous_start_nodes(types):
    graph = load_graph()()
    config = {"nodes": [{"id": str(index), "type": kind} for index, kind in enumerate(types)],
              "edges": [{"source_node_id": "0", "target_node_id": "1"}]}

    with pytest.raises(ValueError, match="start node"):
        graph.build("workflow", config)


def test_graph_accepts_single_start_node():
    graph = load_graph()()
    config = {"nodes": [{"id": "0", "type": "start"}, {"id": "1", "type": "end"}],
              "edges": [{"source_node_id": "0", "target_node_id": "1"}]}

    assert graph.build("workflow", config) is graph


def test_graph_rejects_incoming_edge_to_start_node():
    graph = load_graph()()
    config = {"nodes": [{"id": "0", "type": "end"}, {"id": "1", "type": "start"}],
              "edges": [{"source_node_id": "0", "target_node_id": "1"}]}

    with pytest.raises(ValueError, match="start node.*incoming"):
        graph.build("workflow", config)
