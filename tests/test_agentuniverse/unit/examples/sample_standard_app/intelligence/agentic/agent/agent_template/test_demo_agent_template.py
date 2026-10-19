# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: test_demo_agent_template.py
"""Unit tests for the DemoAgentTemplate example agent template.

The template is a skeleton with fixed input/output key contracts and a stub
``execute`` implementation, all of which are deterministic and pure.
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[9]))

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.agent_template import AgentTemplate
from examples.sample_standard_app.intelligence.agentic.agent.agent_template.demo_agent_template import \
    DemoAgentTemplate


class TestDemoAgentTemplate:
    """Test the DemoAgentTemplate example template contract."""

    @pytest.fixture
    def template(self) -> DemoAgentTemplate:
        return DemoAgentTemplate()

    def test_is_agent_template_subclass(self):
        assert issubclass(DemoAgentTemplate, AgentTemplate)

    def test_input_keys(self, template):
        assert template.input_keys() == ['input']

    def test_output_keys(self, template):
        assert template.output_keys() == ['output']

    def test_parse_input_populates_input_key(self, template):
        input_object = InputObject({'input': 'demo'})
        agent_input = {}
        result = template.parse_input(input_object, agent_input)
        assert result['input'] == 'demo'

    def test_parse_input_returns_same_mapping(self, template):
        input_object = InputObject({'input': 'demo'})
        agent_input = {}
        assert template.parse_input(input_object, agent_input) is agent_input

    def test_parse_result_passes_through(self, template):
        agent_result = {'output': 'raw', 'extra': 1}
        assert template.parse_result(agent_result) is agent_result

    def test_execute_returns_demo_output(self, template):
        agent_input = {}
        result = template.execute(InputObject({'input': 'demo'}), agent_input)
        assert result == {'output': 'demo output.'}
        assert agent_input == {}
