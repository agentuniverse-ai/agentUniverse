"""Regression tests for duplicate workflow node ids."""

import pytest

from agentuniverse.workflow.graph.graph import Graph


def test_duplicate_node_id_raises_value_error():
    graph = Graph()
    config = {
        "nodes": [
            {"id": "same", "type": "start", "name": "first"},
            {"id": "same", "type": "end", "name": "second"},
        ],
        "edges": [{"source_node_id": "same", "target_node_id": "same"}],
    }
    with pytest.raises(ValueError):
        graph.build(workflow_id="wf_duplicate", config=config)


def test_unique_node_ids_build_successfully():
    graph = Graph()
    config = {
        "nodes": [
            {"id": "start", "type": "start", "name": "first"},
            {"id": "end", "type": "end", "name": "second"},
        ],
        "edges": [{"source_node_id": "start", "target_node_id": "end"}],
    }
    graph.build(workflow_id="wf_unique", config=config)
    assert graph.has_node("start")
    assert graph.has_node("end")
