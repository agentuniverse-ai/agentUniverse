from agentuniverse.workflow.graph.graph import Graph
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _end_node(node_id: str, label: str) -> dict:
    """A minimal end node whose prompt is a plain label (no template vars).

    EndNode._run requires a configured `prompt`, so each branch target needs
    one; we give it a constant label just so the node can run and leave a
    trace in `workflow_node_results`.
    """
    return {
        "id": node_id,
        "type": "end",
        "data": {
            "inputs": {
                "prompt": {"name": "input", "type": "string",
                           "value": {"type": "value", "content": label}},
                "input_param": [],
            },
            "outputs": [{"name": "output", "type": "string"}],
        },
    }


def _ref_equal(ref_node: str, ref_param: str, const_val: str) -> dict:
    """An 'equal' condition comparing an upstream node output to a constant."""
    return {
        "compare": "equal",
        "left": {"value": {"type": "reference", "content": [ref_node, ref_param]}},
        "right": {"value": {"type": "const", "content": const_val}},
    }


def _config(branches: list) -> dict:
    """start(1) -> ifelse(2) -> end(3)=branch-1 / end(4)=branch-2 / end(5)=default."""
    return {
        "nodes": [
            {"id": "1", "type": "start",
             "data": {"outputs": [{"name": "input", "type": "string"}]}},
            {"id": "2", "type": "ifelse", "data": {"inputs": {"branches": branches}}},
            _end_node("3", "end-A"),
            _end_node("4", "end-B"),
            _end_node("5", "end-C"),
        ],
        "edges": [
            {"source_node_id": "1", "target_node_id": "2"},
            {"source_node_id": "2", "target_node_id": "3", "source_handler": "branch-1"},
            {"source_node_id": "2", "target_node_id": "4", "source_handler": "branch-2"},
            {"source_node_id": "2", "target_node_id": "5", "source_handler": "branch-default"},
        ],
    }


def _run(input_val: str, branches: list) -> set:
    """Build and run the graph; return the set of executed node ids."""
    workflow_output = WorkflowOutput(workflow_id='wf', workflow_start_params={'input': input_val})
    Graph().build('wf', _config(branches)).run(workflow_output)
    return set(workflow_output.workflow_node_results.keys())


def test_multi_branch_routes_to_the_matching_branch_end():
    # branches: input=='no' (branch-1), input=='yes' (branch-2). With 'yes' the
    # 2nd branch must win and route to end(4); before the fix only branch-1 was
    # evaluated and the flow wrongly fell through to default.
    branches = [
        {"name": "branch-1", "conditions": [_ref_equal("1", "input", "no")]},
        {"name": "branch-2", "conditions": [_ref_equal("1", "input", "yes")]},
    ]
    executed = _run("yes", branches)
    assert "4" in executed          # end-B (branch-2) executed
    assert "3" not in executed      # end-A (branch-1) not executed
    assert "5" not in executed      # end-C (default) not executed


def test_no_branch_matches_falls_through_to_default_end():
    branches = [
        {"name": "branch-1", "conditions": [_ref_equal("1", "input", "no")]},
        {"name": "branch-2", "conditions": [_ref_equal("1", "input", "yes")]},
    ]
    executed = _run("maybe", branches)   # matches neither branch
    assert "5" in executed           # end-C (default)
    assert "3" not in executed
    assert "4" not in executed


def test_multiple_conditions_within_a_branch_are_combined_with_and():
    # branch-2 has two conditions; AND must fail when one is false, so the flow
    # falls through to default even though the first condition is true.
    branches = [
        {"name": "branch-1", "conditions": [_ref_equal("1", "input", "no")]},
        {"name": "branch-2", "conditions": [
            _ref_equal("1", "input", "yes"),   # true
            _ref_equal("1", "input", "no"),    # false -> AND fails
        ]},
    ]
    executed = _run("yes", branches)
    assert "5" in executed           # falls to default
    assert "4" not in executed       # branch-2 not taken
