# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_choose_product_agent.py

"""Unit tests for the ChooseProductAgent example agent."""

import unittest

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.basic_sop_app.intelligence.agentic.agent.agent_instance.choose_product_agent import (
    ChooseProductAgent,
)


class TestChooseProductAgent(unittest.TestCase):
    """Test deterministic methods of ChooseProductAgent without framework boot."""

    def setUp(self):
        """Create a plain agent instance for the tests."""
        self.agent = ChooseProductAgent()

    def test_input_keys(self):
        """input_keys should declare the 'input' key."""
        self.assertEqual(self.agent.input_keys(), ['input'])

    def test_output_keys(self):
        """output_keys should declare the 'product_list' key."""
        self.assertEqual(self.agent.output_keys(), ['product_list'])

    def test_parse_input_merges_user_params(self):
        """parse_input should merge input object params into agent input."""
        input_object = InputObject({'input': 'medical insurance', 'user_id': 'u1'})
        result = self.agent.parse_input(input_object, {'pre': 1})
        self.assertEqual(result, {'pre': 1, 'input': 'medical insurance', 'user_id': 'u1'})

    def test_parse_input_overwrites_existing_values(self):
        """parse_input should let user params overwrite pre-existing keys."""
        input_object = InputObject({'input': 'new query'})
        result = self.agent.parse_input(input_object, {'input': 'old query'})
        self.assertEqual(result, {'input': 'new query'})

    def test_parse_result_extracts_fields(self):
        """parse_result should parse the JSON output into structured fields."""
        agent_result = {'output': '{"product_list": ["A", "B"], "reason": "cheap", "company": "acme"}'}
        result = self.agent.parse_result(agent_result)
        self.assertEqual(result['product_list'], ['A', 'B'])
        self.assertEqual(result['reason'], 'cheap')
        self.assertEqual(result['company'], 'acme')

    def test_parse_result_accepts_markdown_fence(self):
        """parse_result should accept markdown fenced JSON output."""
        agent_result = {'output': '```json\n{"product_list": ["C"], "reason": "fast", "company": "beta"}\n```'}
        result = self.agent.parse_result(agent_result)
        self.assertEqual(result['product_list'], ['C'])
        self.assertEqual(result['company'], 'beta')

    def test_parse_result_handles_missing_fields(self):
        """parse_result should leave absent JSON fields as None."""
        agent_result = {'output': '{"product_list": ["D"]}'}
        result = self.agent.parse_result(agent_result)
        self.assertEqual(result['product_list'], ['D'])
        self.assertIsNone(result['reason'])
        self.assertIsNone(result['company'])


if __name__ == '__main__':
    unittest.main()
