# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_demo_search_tool.py

"""Unit tests for the DemoSearchTool example tool."""

import os
import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.tool import Tool, ToolTypeEnum

from examples.third_party_examples.apps.app_with_goole_search_tool.intelligence.agentic.tool.custom.demo_search_tool import (
    DemoSearchTool,
)


class TestDemoSearchTool(unittest.TestCase):
    """Unit tests for DemoSearchTool."""

    def setUp(self):
        """Set up test fixtures."""
        os.environ.pop("SERPER_API_KEY", None)
        self.tool = DemoSearchTool(name="demo_search", description="demo google search tool")

    def test_is_tool_subclass(self):
        """DemoSearchTool should inherit from the base Tool class."""
        self.assertTrue(issubclass(DemoSearchTool, Tool))

    def test_instance_attributes(self):
        """Constructed instance keeps the provided name and description."""
        self.assertEqual(self.tool.name, "demo_search")
        self.assertEqual(self.tool.description, "demo google search tool")

    def test_default_tool_type(self):
        """The tool type defaults to FUNC."""
        self.assertEqual(self.tool.tool_type, ToolTypeEnum.FUNC)

    def test_serper_api_key_none_without_env(self):
        """Without SERPER_API_KEY in the environment the key field is None."""
        self.assertIsNone(self.tool.serper_api_key)

    def test_serper_api_key_reads_env(self):
        """The key field reads the SERPER_API_KEY env var at instantiation."""
        with patch.dict(os.environ, {"SERPER_API_KEY": "test-key-123"}, clear=False):
            tool = DemoSearchTool(name="demo_search")
            self.assertEqual(tool.serper_api_key, "test-key-123")

    def test_serper_api_key_is_optional(self):
        """The tool can be built without supplying serper_api_key explicitly."""
        self.assertIsNone(DemoSearchTool().serper_api_key)

    def test_input_keys_none_by_default(self):
        """No input keys are enforced by default."""
        self.assertIsNone(self.tool.input_keys)


if __name__ == "__main__":
    unittest.main()
