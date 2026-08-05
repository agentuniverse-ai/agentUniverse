#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio
import unittest

from agentuniverse.agent.action.tool.common_tool.search_api_tool import SearchAPITool
from agentuniverse.agent.action.tool.tool import ToolInput


class FakeSearchAPIWrapper:
    def run(self, query, **kwargs):
        return {"query": query, "params": kwargs}

    async def arun(self, query, **kwargs):
        return {"query": query, "params": kwargs}

    async def aresults(self, query, **kwargs):
        return {"query": query, "params": kwargs, "json": True}


class SearchAPIToolTest(unittest.TestCase):
    def test_async_run_accepts_keyword_input(self):
        tool = SearchAPITool(
            search_api_key="test-key",
            search_params={"num": 10},
        )
        tool.search_api_wrapper = FakeSearchAPIWrapper()

        result = asyncio.run(tool.async_run(input="agentUniverse", num=3))

        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["params"]["num"], 3)

    def test_async_run_accepts_json_result_type(self):
        tool = SearchAPITool(
            search_api_key="test-key",
            search_params={"num": 10},
            search_type="json",
        )
        tool.search_api_wrapper = FakeSearchAPIWrapper()

        result = asyncio.run(tool.async_run(input="agentUniverse", num=5))

        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["params"]["num"], 5)
        self.assertTrue(result["json"])

    def test_execute_accepts_tool_input(self):
        tool = SearchAPITool(
            search_api_key="test-key",
            search_params={"num": 10},
        )
        tool.search_api_wrapper = FakeSearchAPIWrapper()

        result = tool.execute(ToolInput({"input": "agentUniverse", "num": 5}))

        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["params"]["num"], 5)


if __name__ == "__main__":
    unittest.main()
