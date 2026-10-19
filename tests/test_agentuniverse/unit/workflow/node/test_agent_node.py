# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_agent_node.py

"""Unit tests for the workflow AgentNode with AgentManager mocked."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

import agentuniverse.workflow.node.agent_node as agent_node_module
from agentuniverse.workflow.node.agent_node import AgentNode
from agentuniverse.workflow.node.enum import NodeEnum, NodeStatusEnum
from agentuniverse.workflow.workflow_output import WorkflowOutput


def fake_output(payload):
    return SimpleNamespace(to_dict=lambda: payload)


class FakeAgent:
    def __init__(self, payload):
        self.payload = payload
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs
        return fake_output(self.payload)


def build_agent_node(agent_param, input_param, outputs):
    return AgentNode(id="agent_1", name="agent",
                     data={"inputs": {"agent_param": agent_param,
                                      "input_param": input_param},
                           "outputs": outputs})


@pytest.fixture
def workflow_output():
    return WorkflowOutput()


class TestAgentNode:
    """Test AgentNode routing to an agent and output wiring."""

    def test_type_is_agent(self):
        node = build_agent_node(
            [{"name": "id", "value": "agent1"}], [],
            [{"name": "content", "value": None}])
        assert node.type == NodeEnum.AGENT

    def test_run_invokes_agent_and_wires_outputs(self, workflow_output):
        fake = FakeAgent({"content": "agent answer"})
        node = build_agent_node(
            [{"name": "id", "value": "agent1"}],
            [{"name": "topic", "value": {"type": "direct",
                                         "content": "ml"}}],
            [{"name": "content", "value": None}])
        with patch.object(agent_node_module, "AgentManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            result = node.run(workflow_output)
        assert result.status == NodeStatusEnum.SUCCEEDED
        assert result.result[0].value == "agent answer"
        assert fake.run_kwargs == {"topic": "ml"}
        assert workflow_output.workflow_parameters["agent_1"][0].value == \
            "agent answer"

    def test_agent_param_value_dict_uses_content(self, workflow_output):
        fake = FakeAgent({"content": "ok"})
        node = build_agent_node(
            [{"name": "id", "value": {"content": "agent2"}}], [],
            [{"name": "content", "value": None}])
        with patch.object(agent_node_module, "AgentManager") as manager:
            manager.return_value.get_instance_obj.return_value = fake
            node.run(workflow_output)
        manager.return_value.get_instance_obj.assert_called_once_with(
            "agent2")

    def test_missing_agent_raises(self, workflow_output):
        node = build_agent_node(
            [{"name": "id", "value": "ghost"}], [],
            [{"name": "content", "value": None}])
        with patch.object(agent_node_module, "AgentManager") as manager:
            manager.return_value.get_instance_obj.return_value = None
            with pytest.raises(ValueError, match="No agent with id ghost"):
                node.run(workflow_output)
