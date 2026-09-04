# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_agent.py
"""Unit tests for the InsuranceAgent demo agent instance."""

import pytest

from agentuniverse.agent.input_object import InputObject
from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.agentic.agent.agent_instance.insurance_agent import (
    InsuranceAgent,
)


class TestInsuranceAgent:
    """Test InsuranceAgent key and input/output handling helpers."""

    @pytest.fixture
    def agent(self):
        return InsuranceAgent()

    def test_input_keys(self, agent):
        assert agent.input_keys() == ['input']

    def test_output_keys(self, agent):
        assert agent.output_keys() == ['output']

    def test_parse_input_fills_input_key(self, agent):
        input_object = InputObject({'input': 'user question'})
        result = agent.parse_input(input_object, {'input': None})
        assert result == {'input': 'user question'}

    def test_parse_input_with_default_key_value(self, agent):
        input_object = InputObject({'other': 'value'})
        result = agent.parse_input(input_object, {'input': 'unset'})
        assert result['input'] is None

    def test_parse_result_keeps_output(self, agent):
        result = agent.parse_result({'input': 'q', 'output': 'answer'})
        assert result['output'] == 'answer'
        assert result['input'] == 'q'

    def test_parse_result_round_trips_agent_input(self, agent):
        input_object = InputObject({'input': 'q'})
        parsed = agent.parse_input(input_object, {})
        assert 'input' in parsed
