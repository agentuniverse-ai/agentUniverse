# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_demo_agent.py
"""Unit tests for the DemoAgent example agent.

Only the input/output contract helpers that do not require an LLM, a memory
component or a running framework are exercised here.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[9]))

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from examples.sample_standard_app.intelligence.agentic.agent.agent_instance.demo_agent import \
    DemoAgent


class TestDemoAgent:
    """Test the DemoAgent example agent contract helpers."""

    @pytest.fixture
    def agent(self) -> DemoAgent:
        return DemoAgent()

    def test_is_agent_template_subclass(self):
        assert issubclass(DemoAgent, AgentTemplate)

    def test_input_keys(self, agent):
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        assert agent.output_keys() == ['output']

    def test_parse_input_populates_input_key(self, agent):
        input_object = InputObject({'input': 'hello agent'})
        agent_input = {}
        result = agent.parse_input(input_object, agent_input)
        assert result['input'] == 'hello agent'

    def test_parse_input_returns_same_mapping(self, agent):
        input_object = InputObject({'input': 'hello'})
        agent_input = {}
        assert agent.parse_input(input_object, agent_input) is agent_input

    def test_parse_input_missing_key_yields_none(self, agent):
        input_object = InputObject({})
        agent_input = {}
        agent.parse_input(input_object, agent_input)
        assert agent_input['input'] is None

    def test_parse_result_keeps_output_and_extra_keys(self, agent):
        agent_result = {'output': 'final answer', 'trace': 't1'}
        result = agent.parse_result(agent_result)
        assert result['output'] == 'final answer'
        assert result['trace'] == 't1'

    def test_parse_result_without_output_raises_key_error(self, agent):
        with pytest.raises(KeyError):
            agent.parse_result({'trace': 't1'})
