import pytest

from agentuniverse.workflow.graph.graph import Graph


def test_graph_rejects_duplicate_node_ids():
    config = {
        "nodes": [
            {
                "id": "duplicate",
                "name": "start",
                "type": "start",
                "data": {"outputs": [{"name": "input"}]},
            },
            {
                "id": "duplicate",
                "name": "end",
                "type": "end",
                "data": {
                    "inputs": {
                        "input_param": [],
                        "prompt": {"value": "done"},
                    },
                    "outputs": [{"name": "answer"}],
                },
            },
        ],
        "edges": [
            {
                "source_node_id": "duplicate",
                "target_node_id": "duplicate",
            }
        ],
    }

    with pytest.raises(ValueError, match="Duplicate workflow node id: duplicate"):
        Graph().build("workflow", config)
