# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/13 00:00
# @Author  : Yue Wang
# @FileName: test_choose_product_info_agent.py

import unittest

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.basic_sop_app.intelligence.agentic.agent.agent_instance.choose_product_info_agent import (
    ChooseProductInfoAgent,
)


class TestChooseProductInfoAgent(unittest.TestCase):
    """Unit tests for ChooseProductInfoAgent's pure parse helpers."""

    def setUp(self):
        """Create an agent instance for the tests."""
        self.agent = ChooseProductInfoAgent()

    def test_input_keys(self):
        """The agent accepts a single 'input' key."""
        self.assertEqual(self.agent.input_keys(), ['input'])

    def test_output_keys(self):
        """The agent outputs the 'item_list' key."""
        self.assertEqual(self.agent.output_keys(), ['item_list'])

    def test_parse_input_copies_input_object_items(self):
        """parse_input forwards every InputObject item into agent_input."""
        input_object = InputObject({'input': '帮我选医疗险', 'extra': 'value'})
        agent_input = {'input': 'default'}
        result = self.agent.parse_input(input_object, agent_input)
        self.assertEqual(result['input'], '帮我选医疗险')
        self.assertEqual(result['extra'], 'value')
        self.assertIs(result, agent_input)

    def test_parse_input_returns_updated_dict(self):
        """parse_input returns the same dict enriched with parsed keys."""
        input_object = InputObject({'question': '医疗险推荐'})
        agent_input = {}
        result = self.agent.parse_input(input_object, agent_input)
        self.assertEqual(result, {'question': '医疗险推荐'})

    def test_parse_result_extracts_item_list(self):
        """parse_result reads the item_list from a JSON output string."""
        result = self.agent.parse_result({'output': '{"item_list": ["B", "C"]}'})
        self.assertEqual(result, {'item_list': ['B', 'C']})

    def test_parse_result_accepts_markdown_fenced_json(self):
        """parse_result tolerates markdown code fences around the JSON."""
        result = self.agent.parse_result(
            {'output': '```json\n{"item_list": ["C"]}\n```'})
        self.assertEqual(result, {'item_list': ['C']})

    def test_parse_result_missing_item_list_returns_none(self):
        """parse_result yields None when the JSON has no item_list field."""
        result = self.agent.parse_result({'output': '{"other": 1}'})
        self.assertEqual(result, {'item_list': None})


if __name__ == '__main__':
    unittest.main()
