# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_end_node.py

"""Unit tests for the workflow EndNode."""

import pytest

from agentuniverse.workflow.node.end_node import EndNode
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.node_config import NodeOutputParams
from agentuniverse.workflow.workflow_output import WorkflowOutput


def build_end_node(inputs, outputs):
    return EndNode(id="end_1", name="end", data={"inputs": inputs,
                                                 "outputs": outputs})


class TestEndNode:
    """Test EndNode template resolution and output wiring."""

    def test_type_is_end(self):
        node = build_end_node(
            {"input_param": [], "prompt": {"value": "x"}},
            [{"name": "final", "value": None}])
        assert node.type == NodeEnum.END

    def test_prompt_template_substitution(self):
        node = build_end_node(
            {"input_param": [{"name": "user_name", "value": {
                "type": "direct", "content": "Alice"}}],
             "prompt": {"value": "Hello {{user_name}}!"}},
            [{"name": "final", "value": None}])
        workflow_output = WorkflowOutput()
        result = node.run(workflow_output)
        assert result.node_id == "end_1"
        assert result.status == NodeStatusEnum.SUCCEEDED
        assert result.result[0].value == "Hello Alice!"
        assert workflow_output.workflow_end_params == {
            "final": "Hello Alice!"}

    def test_prompt_value_can_be_dict(self):
        node = build_end_node(
            {"input_param": [], "prompt": {
                "value": {"content": "plain text"}}},
            [{"name": "final", "value": None}])
        workflow_output = WorkflowOutput()
        node.run(workflow_output)
        assert workflow_output.workflow_end_params == {
            "final": "plain text"}

    def test_reference_input_resolution(self):
        node = build_end_node(
            {"input_param": [{"name": "user_name", "value": {
                "type": "reference", "content": ["prev", "out"]}}],
             "prompt": {"value": "Hi {{user_name}}"}},
            [{"name": "final", "value": None}])
        workflow_output = WorkflowOutput()
        workflow_output.workflow_parameters["prev"] = [
            NodeOutputParams(name="out", value="Bob")]
        node.run(workflow_output)
        assert workflow_output.workflow_end_params == {"final": "Hi Bob"}

    def test_missing_variable_raises(self):
        node = build_end_node(
            {"input_param": [], "prompt": {"value": "Hi {{missing}}"}},
            [{"name": "final", "value": None}])
        with pytest.raises(ValueError, match="Error processing template"):
            node.run(WorkflowOutput())

    def test_output_parameter_recorded_in_workflow_output(self):
        node = build_end_node(
            {"input_param": [], "prompt": {"value": "done"}},
            [{"name": "final", "value": None}])
        workflow_output = WorkflowOutput()
        node.run(workflow_output)
        recorded = workflow_output.workflow_parameters["end_1"]
        assert recorded[0].name == "final"
        assert recorded[0].value == "done"
