import pytest

from agentuniverse.workflow.graph import graph as graph_module
from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.node.enum import NodeEnum


def test_add_graph_node_preserves_config_when_initialization_fails(monkeypatch):
    class NodeInitializationError(RuntimeError):
        pass

    class FailingNode:
        def __init__(self, **kwargs):
            raise NodeInitializationError

    node_config = {
        "id": "start_node",
        "type": NodeEnum.START.value,
        "name": "Start",
    }
    original_config = node_config.copy()
    monkeypatch.setitem(
        graph_module.NODE_CLS_MAPPING,
        NodeEnum.START.value,
        FailingNode,
    )

    with pytest.raises(NodeInitializationError):
        Graph()._add_graph_node("workflow", node_config)

    assert node_config == original_config


def test_add_graph_node_builds_from_copy_without_mutating_config(monkeypatch):
    class CapturingNode:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    node_config = {
        "id": "start_node",
        "type": NodeEnum.START.value,
        "name": "Start",
    }
    original_config = node_config.copy()
    monkeypatch.setitem(
        graph_module.NODE_CLS_MAPPING,
        NodeEnum.START.value,
        CapturingNode,
    )

    graph = Graph()
    graph._add_graph_node("workflow", node_config)

    assert node_config == original_config
    assert graph.nodes["start_node"]["instance"].kwargs == {
        "id": "start_node",
        "name": "Start",
        "type": NodeEnum.START,
        "workflow_id": "workflow",
    }
