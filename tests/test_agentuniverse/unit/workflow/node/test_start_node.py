# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_start_node.py

"""Unit tests for the workflow StartNode."""

import pytest

from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.node.start_node import StartNode
from agentuniverse.workflow.workflow_output import WorkflowOutput


@pytest.fixture
def start_node():
    return StartNode(id="start_1", name="start",
                     data={"outputs": [{"name": "input", "value": None}]})


class TestStartNode:
    """Test StartNode startup input propagation."""

    def test_type_is_start(self, start_node):
        assert start_node.type == NodeEnum.START

    def test_run_propagates_start_input(self, start_node):
        workflow_output = WorkflowOutput()
        workflow_output.workflow_start_params = {"input": "hello world"}
        result = start_node.run(workflow_output)
        assert result.node_id == "start_1"
        assert result.status == NodeStatusEnum.SUCCEEDED
        assert result.result[0].value == "hello world"
        assert workflow_output.workflow_parameters["start_1"][0].value == \
            "hello world"

    def test_run_without_input_uses_empty_string(self, start_node):
        workflow_output = WorkflowOutput()
        start_node.run(workflow_output)
        assert workflow_output.workflow_parameters["start_1"][0].value == ""

    def test_run_with_empty_start_params(self, start_node):
        workflow_output = WorkflowOutput(workflow_start_params={})
        result = start_node.run(workflow_output)
        assert result.result[0].value == ""
