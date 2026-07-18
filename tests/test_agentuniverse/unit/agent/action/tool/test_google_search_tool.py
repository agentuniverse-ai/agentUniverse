#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import google_search_tool as google_module
from agentuniverse.agent.action.tool.common_tool.google_search_tool import GoogleSearchTool


class FakeGoogleSerperAPIWrapper:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, query):
        return {
            "query": query,
            "serper_api_key": self.kwargs["serper_api_key"],
            "k": self.kwargs["k"],
            "gl": self.kwargs["gl"],
            "hl": self.kwargs["hl"],
            "type": self.kwargs["type"],
        }

    async def arun(self, query):
        return self.run(query)


class TestGoogleSearchTool(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tool = GoogleSearchTool(serper_api_key="test-key")

    def test_execute_loads_serper_wrapper_lazily(self):
        with patch.object(
            google_module,
            "_get_google_serper_api_wrapper",
            return_value=FakeGoogleSerperAPIWrapper,
        ) as load_wrapper:
            result = self.tool.execute("agentUniverse")

        load_wrapper.assert_called_once_with()
        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["serper_api_key"], "test-key")
        self.assertEqual(result["k"], 10)
        self.assertEqual(result["gl"], "us")
        self.assertEqual(result["hl"], "en")
        self.assertEqual(result["type"], "search")

    async def test_async_execute_loads_serper_wrapper_lazily(self):
        with patch.object(
            google_module,
            "_get_google_serper_api_wrapper",
            return_value=FakeGoogleSerperAPIWrapper,
        ) as load_wrapper:
            result = await self.tool.async_execute("agentUniverse")

        load_wrapper.assert_called_once_with()
        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["serper_api_key"], "test-key")


if __name__ == "__main__":
    unittest.main()
