"""Regression tests for workflow node output isolation across executions."""

from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


def _build_start_node():
    node = StartNode(id="start", type="start")
    node._data.outputs = [NodeOutputParams(name="out", type="str", value=None)]
    return node


def test_reused_workflow_start_node_outputs_are_isolated():
    node = _build_start_node()

    first = WorkflowOutput()
    first.workflow_start_params = {"input": "first"}
    result1 = node._run(first)

    second = WorkflowOutput()
    second.workflow_start_params = {"input": "second"}
    result2 = node._run(second)

    assert result1.result[0].value == "first"
    assert result2.result[0].value == "second"
    assert result1.result[0] is not result2.result[0]
    assert node._data.outputs[0].value is None
