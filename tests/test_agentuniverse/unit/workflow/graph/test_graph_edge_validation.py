import pytest

from agentuniverse.workflow.graph.graph import Graph


def _graph_config(edge):
    return {
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "data": {"outputs": [{"name": "output", "type": "string"}]},
            },
            {
                "id": "end",
                "type": "end",
                "data": {
                    "inputs": {
                        "input_param": [],
                        "prompt": {"name": "input", "value": "done"},
                    },
                    "outputs": [{"name": "output", "type": "string"}],
                },
            },
        ],
        "edges": [edge],
    }


@pytest.mark.parametrize(
    ("edge", "missing_node"),
    [
        ({"source_node_id": "missing", "target_node_id": "end"}, "missing"),
        ({"source_node_id": "start", "target_node_id": "missing"}, "missing"),
    ],
)
def test_build_rejects_edges_with_undefined_nodes(edge, missing_node):
    with pytest.raises(ValueError, match=missing_node):
        Graph().build("workflow", _graph_config(edge))
