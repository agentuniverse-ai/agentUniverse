# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_tool_node.py

"""Unit tests for the workflow ToolNode with ToolManager mocked."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

import agentuniverse.workflow.node.tool_node as tool_node_module
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.tool_node import ToolNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


class FakeTool:
    def __init__(self, output):
        self.output = output
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs
        return self.output


def build_tool_node(tool_param, input_param, outputs):
    return ToolNode(id="tool_1", name="tool",
                    data={"inputs": {"tool_param": tool_param,
                                     "input_param": input_param},
                          "outputs": outputs})


@pytest.fixture
def workflow_output():
    return WorkflowOutput()


class TestToolNode:
    """Test ToolNode tool lookup, invocation and output wiring."""

    def test_type_is_tool(self):
        node = build_tool_node([], [], [{"name": "result", "value": None}])
        assert node.type == NodeEnum.TOOL

    def test_string_output_goes_to_first_output_param(self, workflow_output):
        fake = FakeTool("str result")
        node = build_tool_node(
            [{"name": "id", "value": "tool1"}],
            [{"name": "x", "value": {"type": "direct", "content": "1"}}],
            [{"name": "result", "value": None}])
        with patch.object(tool_node_module, "ToolManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            result = node.run(workflow_output)
        assert result.status == NodeStatusEnum.SUCCEEDED
        assert result.result[0].value == "str result"
        assert fake.run_kwargs == {"x": "1"}

    def test_dict_output_maps_by_output_param_name(self, workflow_output):
        fake = FakeTool({"out_a": "va", "out_b": "vb"})
        node = build_tool_node(
            [{"name": "id", "value": {"content": "tool2"}}], [],
            [{"name": "out_a", "value": None},
             {"name": "out_b", "value": None}])
        with patch.object(tool_node_module, "ToolManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            result = node.run(workflow_output)
        assert [p.value for p in result.result] == ["va", "vb"]
        assert workflow_output.workflow_parameters["tool_1"][1].value == "vb"

    def test_unsupported_tool_output_type_raises(self, workflow_output):
        fake = FakeTool(42)
        node = build_tool_node(
            [{"name": "id", "value": "tool1"}], [],
            [{"name": "result", "value": None}])
        with patch.object(tool_node_module, "ToolManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            with pytest.raises(TypeError, match="not supported"):
                node.run(workflow_output)

    def test_missing_tool_raises(self, workflow_output):
        node = build_tool_node(
            [{"name": "id", "value": "ghost"}], [],
            [{"name": "result", "value": None}])
        with patch.object(tool_node_module, "ToolManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with pytest.raises(ValueError, match="No tool with id ghost"):
                node.run(workflow_output)
