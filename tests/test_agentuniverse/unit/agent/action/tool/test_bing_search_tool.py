#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import bing_search_tool as bing_module
from agentuniverse.agent.action.tool.common_tool.bing_search_tool import BingSearchTool


class FakeBingSearchAPIWrapper:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, query):
        return {
            "query": query,
            "subscription_key": self.kwargs["bing_subscription_key"],
            "search_url": self.kwargs["bing_search_url"],
            "k": self.kwargs["k"],
        }


class TestBingSearchTool(unittest.TestCase):
    def test_missing_key_uses_mock_without_loading_bing_wrapper(self):
        tool = BingSearchTool(bing_subscription_key=None)

        with patch.object(
            bing_module,
            "_get_bing_search_api_wrapper",
            side_effect=AssertionError("wrapper should not be loaded"),
        ):
            result = tool.execute("BYD news")

        self.assertIn("比亚迪", result)

    def test_wrapper_is_loaded_only_for_real_bing_requests(self):
        tool = BingSearchTool(
            bing_subscription_key="test-key",
            bing_search_url="https://example.com/search",
        )

        with patch.object(
            bing_module,
            "_get_bing_search_api_wrapper",
            return_value=FakeBingSearchAPIWrapper,
        ) as load_wrapper:
            result = tool.execute("agentUniverse")

        load_wrapper.assert_called_once_with()
        self.assertEqual(result["query"], "agentUniverse")
        self.assertEqual(result["subscription_key"], "test-key")
        self.assertEqual(result["search_url"], "https://example.com/search")
        self.assertEqual(result["k"], 5)


if __name__ == "__main__":
    unittest.main()
