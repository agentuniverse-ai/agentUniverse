# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @Email   : ai-assistant@example.com
# @FileName: test_demo_agent.py

"""Unit tests for the pure input/output helpers of DemoAgent."""

import unittest

from agentuniverse.agent.input_object import InputObject
from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.agentic.agent.agent_instance.demo_agent import \
    DemoAgent


class DemoAgentTest(unittest.TestCase):
    """Unit tests for DemoAgent's deterministic helpers."""

    def setUp(self):
        """Set up the agent instance under test."""
        self.agent = DemoAgent()

    def test_input_keys_returns_input(self):
        self.assertEqual(self.agent.input_keys(), ['input'])

    def test_output_keys_returns_output(self):
        self.assertEqual(self.agent.output_keys(), ['output'])

    def test_parse_input_writes_input_from_input_object(self):
        agent_input = {}
        result = self.agent.parse_input(InputObject({'input': 'hello'}), agent_input)
        self.assertIs(result, agent_input)
        self.assertEqual(agent_input['input'], 'hello')

    def test_parse_input_keeps_existing_fields(self):
        agent_input = {'background': 'ctx'}
        self.agent.parse_input(InputObject({'input': 'hi'}), agent_input)
        self.assertEqual(agent_input['background'], 'ctx')

    def test_parse_input_uses_default_when_key_missing(self):
        agent_input = {}
        self.agent.parse_input(InputObject({'other': 1}), agent_input)
        self.assertIsNone(agent_input.get('input'))

    def test_parse_result_keeps_original_fields_and_output(self):
        result = self.agent.parse_result({'output': 'answer', 'extra': 1})
        self.assertEqual(result['output'], 'answer')
        self.assertEqual(result['extra'], 1)


if __name__ == '__main__':
    unittest.main()
