# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/30 10:10
# @Author  : agentuniverse
# @FileName: test_workflow_agent.py
"""Unit tests for the WorkflowAgent default agent module."""

import pytest

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.default.workflow_agent.workflow_agent import WorkflowAgent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestWorkflowAgent:
    """Test the WorkflowAgent default agent."""

    @pytest.fixture
    def agent(self):
        """Create a WorkflowAgent instance without any configuration."""
        return WorkflowAgent()

    def test_class_hierarchy(self):
        """WorkflowAgent extends Agent directly and is a component."""
        assert issubclass(WorkflowAgent, Agent)
        assert issubclass(WorkflowAgent, ComponentBase)

    def test_instantiation(self, agent):
        """A WorkflowAgent can be created without a config and is an AGENT component."""
        assert isinstance(agent, WorkflowAgent)
        assert agent.component_type == ComponentEnum.AGENT
        assert agent.agent_model is None
        assert agent.is_default_object() is False

    def test_workflow_id_default(self, agent):
        """workflow_id defaults to None and is not wired to a workflow yet."""
        assert agent.workflow_id is None

    def test_input_keys_empty(self, agent):
        """WorkflowAgent declares no fixed input keys."""
        assert agent.input_keys() == []

    def test_output_keys_empty(self, agent):
        """WorkflowAgent declares no fixed output keys."""
        assert agent.output_keys() == []

    def test_parse_input_passthrough(self, agent):
        """parse_input returns the agent_input dict untouched."""
        agent_input = {'chat_history': 'hello'}
        input_object = InputObject({'input': 'run workflow'})
        parsed = agent.parse_input(input_object, agent_input)
        assert parsed is agent_input
        assert parsed == {'chat_history': 'hello'}

    def test_parse_result_passthrough(self, agent):
        """parse_result returns the raw agent result untouched."""
        result = {'workflow_end_params': {'data': 'ok'}}
        assert agent.parse_result(result) is result
        assert agent.parse_result(result) == {'workflow_end_params': {'data': 'ok'}}
