# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @Email   : ai-assistant@example.com
# @FileName: test_demo_agent_template.py

"""Unit tests for the pure input/output helpers of DemoAgentTemplate."""

import unittest

from agentuniverse.agent.input_object import InputObject
from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.agentic.agent.agent_template.demo_agent_template import \
    DemoAgentTemplate


class DemoAgentTemplateTest(unittest.TestCase):
    """Unit tests for DemoAgentTemplate's deterministic behaviors."""

    def setUp(self):
        """Set up the template instance under test."""
        self.template = DemoAgentTemplate()

    def test_input_keys_returns_input(self):
        self.assertEqual(self.template.input_keys(), ['input'])

    def test_output_keys_returns_output(self):
        self.assertEqual(self.template.output_keys(), ['output'])

    def test_parse_input_writes_input_from_input_object(self):
        agent_input = {}
        result = self.template.parse_input(InputObject({'input': 'question'}), agent_input)
        self.assertIs(result, agent_input)
        self.assertEqual(agent_input['input'], 'question')

    def test_parse_input_keeps_existing_fields(self):
        agent_input = {'session_id': 's1'}
        self.template.parse_input(InputObject({'input': 'q'}), agent_input)
        self.assertEqual(agent_input['session_id'], 's1')
        self.assertEqual(agent_input['input'], 'q')

    def test_parse_result_returns_agent_result_unchanged(self):
        agent_result = {'output': 'answer'}
        self.assertIs(self.template.parse_result(agent_result), agent_result)

    def test_execute_returns_fixed_demo_output(self):
        self.assertEqual(self.template.execute(None, {}), {'output': 'demo output.'})


if __name__ == '__main__':
    unittest.main()
