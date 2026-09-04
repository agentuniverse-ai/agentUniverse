# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @Email   : ai-assistant@example.com
# @FileName: test_mock_search_tool.py

"""Unit tests for MockSearchTool's deterministic mock responses."""

import unittest

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.agentic.tool.custom.mock_search_tool import \
    MockSearchTool


class MockSearchToolTest(unittest.TestCase):
    """Unit tests for MockSearchTool."""

    def setUp(self):
        """Set up the tool instance under test."""
        self.tool = MockSearchTool(name='mock_search')

    def test_mock_api_res_returns_non_empty_string(self):
        result = self.tool.mock_api_res()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_mock_api_res_contains_expected_content(self):
        result = self.tool.mock_api_res()
        self.assertIn('巴菲特', result)
        self.assertIn('比亚迪', result)

    def test_mock_api_res_is_deterministic(self):
        self.assertEqual(self.tool.mock_api_res(), self.tool.mock_api_res())

    def test_execute_returns_mock_api_res(self):
        self.assertEqual(self.tool.execute('query'), self.tool.mock_api_res())

    def test_execute_result_is_non_empty_string(self):
        result = self.tool.execute('query')
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_execute_ignores_input_value(self):
        self.assertEqual(self.tool.execute('a'), self.tool.execute('b'))


if __name__ == '__main__':
    unittest.main()
