#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import google_search_tool_v2 as google_v2_module
from agentuniverse.agent.action.tool.common_tool.google_search_tool_v2 import (
    GoogleScholarSearchTool,
    GoogleSearchTool,
)


class FakeGoogleSerperAPIWrapper:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, query):
        return f"result for {query}"

    async def arun(self, query):
        return self.run(query)


class TestGoogleSearchToolV2(unittest.IsolatedAsyncioTestCase):
    def test_missing_key_uses_mock_without_loading_serper_wrapper(self):
        tool = GoogleSearchTool(serper_api_key=None)

        with patch.object(
            google_v2_module,
            "_get_google_serper_api_wrapper",
            side_effect=AssertionError("wrapper should not be loaded"),
        ):
            result = tool.execute("agentUniverse")

        self.assertIn("未配置SERPER_API_KEY", result)

    def test_execute_loads_serper_wrapper_for_real_search(self):
        tool = GoogleSearchTool(serper_api_key="test-key")

        with patch.object(
            google_v2_module,
            "_get_google_serper_api_wrapper",
            return_value=FakeGoogleSerperAPIWrapper,
        ) as load_wrapper:
            result = tool.execute("agentUniverse", search_type="news", k=3)

        load_wrapper.assert_called_once_with()
        self.assertIn("agentUniverse", result)

    async def test_async_execute_loads_serper_wrapper_for_real_search(self):
        tool = GoogleSearchTool(serper_api_key="test-key")

        with patch.object(
            google_v2_module,
            "_get_google_serper_api_wrapper",
            return_value=FakeGoogleSerperAPIWrapper,
        ) as load_wrapper:
            result = await tool.async_execute("agentUniverse")

        load_wrapper.assert_called_once_with()
        self.assertIn("agentUniverse", result)

    def test_scholar_missing_key_uses_mock_without_loading_wrapper(self):
        tool = GoogleScholarSearchTool(serper_api_key=None)

        with patch.object(
            google_v2_module,
            "_get_google_serper_api_wrapper",
            side_effect=AssertionError("wrapper should not be loaded"),
        ):
            result = tool.execute("agentUniverse")

        self.assertIn("未配置SERPER_API_KEY", result)


if __name__ == "__main__":
    unittest.main()
