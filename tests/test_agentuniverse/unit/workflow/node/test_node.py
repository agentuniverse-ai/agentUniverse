# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_node.py

"""Unit tests for the workflow Node base class."""

import pytest

from agentuniverse.workflow.node.enum import NodeStatusEnum
from agentuniverse.workflow.node.node import Node, NodeData
from agentuniverse.workflow.node.node_config import (
    InputValueParams,
    NodeInputParams,
    NodeOutputParams,
)
from agentuniverse.workflow.node.node_output import NodeOutput
from agentuniverse.workflow.workflow_output import WorkflowOutput


class StubNode(Node):
    """Concrete node used to test base Node behaviors."""

    def _run(self, workflow_output: WorkflowOutput) -> NodeOutput:
        return NodeOutput(node_id=self.id, status=NodeStatusEnum.SUCCEEDED)


@pytest.fixture
def workflow_output():
    output = WorkflowOutput()
    output.workflow_parameters["prev"] = [
        NodeOutputParams(name="out", value="value_from_prev")]
    return output


class TestNodeBase:
    """Test Node defaults, delegation and data construction."""

    def test_abstract_base_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            Node()

    def test_run_delegates_to_run(self):
        node = StubNode(id="n1", name="stub")
        result = node.run(WorkflowOutput())
        assert result.node_id == "n1"
        assert result.status == NodeStatusEnum.SUCCEEDED

    def test_default_fields(self):
        node = StubNode(id="n1")
        assert node.name is None
        assert node.description is None
        assert node.type is None
        assert node.workflow_id is None
        assert node._data.outputs is None

    def test_data_is_parsed_into_data_model(self):
        node = StubNode(id="n1", data={
            "outputs": [{"name": "out", "value": 7}]})
        assert isinstance(node._data, NodeData)
        assert node._data.outputs[0].name == "out"
        assert node._data.outputs[0].value == 7

    def test_resolve_input_params_direct(self, workflow_output):
        params = [NodeInputParams(name="a", value=InputValueParams(
            type="direct", content="hello"))]
        resolved = Node._resolve_input_params(params, workflow_output)
        assert resolved == {"a": "hello"}

    def test_resolve_input_params_reference(self, workflow_output):
        params = [NodeInputParams(name="b", value=InputValueParams(
            type="reference", content=["prev", "out"]))]
        resolved = Node._resolve_input_params(params, workflow_output)
        assert resolved == {"b": "value_from_prev"}

    def test_resolve_input_params_missing_reference(self, workflow_output):
        params = [NodeInputParams(name="c", value=InputValueParams(
            type="reference", content=["prev", "missing"]))]
        resolved = Node._resolve_input_params(params, workflow_output)
        assert resolved == {"c": None}
