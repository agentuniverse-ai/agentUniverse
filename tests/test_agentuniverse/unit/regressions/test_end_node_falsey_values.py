"""Regression tests for end-node template rendering of falsey values."""

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.node_config import EndNodeInputParams, NodeInfoParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _run_end_node(value):
    node = EndNode(id="end", type="end")
    node._data.inputs = EndNodeInputParams(
        prompt=NodeInfoParams(name="prompt", type="str", value={"content": "result={{value}}"}),
        input_param=[],
    )
    node._resolve_input_params = lambda inputs, wf: {"value": value}
    workflow_output = WorkflowOutput()
    result = node._run(workflow_output)
    return result.result[0].value


def test_zero_value_is_rendered():
    assert _run_end_node(0) == "result=0"


def test_false_value_is_rendered():
    assert _run_end_node(False) == "result=False"


def test_none_value_is_rendered_as_empty():
    assert _run_end_node(None) == "result="
