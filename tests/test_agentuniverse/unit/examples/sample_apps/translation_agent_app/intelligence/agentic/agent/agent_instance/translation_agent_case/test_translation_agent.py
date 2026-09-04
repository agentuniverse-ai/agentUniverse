# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_translation_agent.py

"""Unit tests for the TranslationAgent example agent."""

import unittest

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.translation_agent_app.intelligence.agentic.agent.agent_instance.translation_agent_case.translation_agent import (
    TranslationAgent,
)


class _FakeAgentModel(object):
    """Minimal stand-in for agent_model exposing a profile dict."""

    def __init__(self):
        self.profile = {
            'input_keys': ['source_lang', 'target_lang', 'source_text'],
            'output_keys': ['output'],
        }


class TestTranslationAgent(unittest.TestCase):
    """Test deterministic methods of TranslationAgent without framework boot."""

    def setUp(self):
        """Create a plain agent instance for the tests."""
        self.agent = TranslationAgent()
        self.agent.agent_model = _FakeAgentModel()

    def test_input_keys_delegates_to_profile(self):
        """input_keys should come from the agent profile."""
        self.assertEqual(self.agent.input_keys(),
                         ['source_lang', 'target_lang', 'source_text'])

    def test_output_keys_delegates_to_profile(self):
        """output_keys should come from the agent profile."""
        self.assertEqual(self.agent.output_keys(), ['output'])

    def test_parse_input_copies_all_inputs(self):
        """parse_input should copy every input object param into agent input."""
        input_object = InputObject({'source_lang': '英文', 'target_lang': '中文', 'source_text': 'hello'})
        result = self.agent.parse_input(input_object, {})
        self.assertEqual(result, {'source_lang': '英文', 'target_lang': '中文', 'source_text': 'hello'})

    def test_parse_input_keeps_preexisting_keys(self):
        """parse_input should preserve keys already present in agent input."""
        input_object = InputObject({'source_text': 'hi'})
        result = self.agent.parse_input(input_object, {'country': 'CN'})
        self.assertEqual(result, {'country': 'CN', 'source_text': 'hi'})

    def test_parse_input_overwrites_colliding_keys(self):
        """parse_input should let input object params override pre-existing values."""
        input_object = InputObject({'source_text': 'new'})
        result = self.agent.parse_input(input_object, {'source_text': 'old'})
        self.assertEqual(result, {'source_text': 'new'})

    def test_parse_input_empty_input_object(self):
        """parse_input with no params should leave agent input untouched."""
        result = self.agent.parse_input(InputObject({}), {'keep': 1})
        self.assertEqual(result, {'keep': 1})

    def test_parse_result_passthrough(self):
        """parse_result should return the planner result unchanged."""
        planner_result = {'output': 'translated', 'extra': 1}
        self.assertEqual(self.agent.parse_result(planner_result), {'output': 'translated', 'extra': 1})

    def test_parse_result_does_not_mutate_input(self):
        """parse_result should not mutate the dict it receives."""
        planner_result = {'output': 'x'}
        self.agent.parse_result(planner_result)
        self.assertEqual(planner_result, {'output': 'x'})


if __name__ == '__main__':
    unittest.main()
