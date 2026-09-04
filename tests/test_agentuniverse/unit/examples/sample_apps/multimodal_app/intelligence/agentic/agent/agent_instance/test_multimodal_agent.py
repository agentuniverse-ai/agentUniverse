# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/19 17:58
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_multimodal_agent.py

"""Unit tests for the pure logic of MultimodalAgent.

Only stateless key/parse helpers are exercised; no LLM or memory is used.
"""
import pytest

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.multimodal_app.intelligence.agentic.agent.agent_instance.multimodal_agent import (
    MultimodalAgent,
)


class TestMultimodalAgent:
    """Tests for MultimodalAgent key/parse helpers."""

    def setup_method(self):
        self.agent = MultimodalAgent()

    def test_input_keys(self):
        assert self.agent.input_keys() == ['input']

    def test_output_keys(self):
        assert self.agent.output_keys() == ['output']

    def test_parse_input_sets_input_key(self):
        input_object = InputObject({'input': 'hello'})
        agent_input = {'background': ''}
        result = self.agent.parse_input(input_object, agent_input)
        assert result == {'background': '', 'input': 'hello'}
        assert result is agent_input

    def test_parse_input_missing_input_key(self):
        input_object = InputObject({'other': 'x'})
        assert self.agent.parse_input(input_object, {}) == {'input': None}

    def test_parse_result_keeps_output(self):
        result = self.agent.parse_result({'output': 'answer', 'extra': 1})
        assert result == {'output': 'answer', 'extra': 1}

    def test_parse_result_does_not_mutate_input(self):
        agent_result = {'output': 'answer'}
        self.agent.parse_result(agent_result)
        assert agent_result == {'output': 'answer'}
