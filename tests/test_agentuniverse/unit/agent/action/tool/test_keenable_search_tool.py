#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.tool.common_tool import keenable_search_tool
from agentuniverse.agent.action.tool.common_tool.keenable_search_tool import KeenableSearchTool


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class KeenableSearchToolTest(unittest.TestCase):
    def test_uses_public_endpoint_without_key(self):
        tool = KeenableSearchTool(api_key=None)
        payload = {"results": [
            {"title": "A", "url": "https://a.example", "description": "short", "snippet": "long"},
            {"title": "B", "url": "https://b.example", "snippet": "x" * 2000},
            {"title": "no url", "description": "dropped"},
        ]}
        with patch.object(keenable_search_tool.requests, "post", return_value=_response(payload)) as post:
            result = tool.execute("agentUniverse", max_results=3)

        args, kwargs = post.call_args
        self.assertEqual(args[0], keenable_search_tool.KEENABLE_PUBLIC_SEARCH_URL)
        self.assertNotIn("X-API-Key", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["X-Keenable-Title"], "agentUniverse")
        self.assertEqual(kwargs["json"], {"query": "agentUniverse", "max_results": 3})
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["content"], "short")
        self.assertEqual(len(result["results"][1]["content"]), 1000)

    def test_uses_keyed_endpoint_with_key(self):
        tool = KeenableSearchTool(api_key="test-key")
        with patch.object(keenable_search_tool.requests, "post", return_value=_response({"results": []})) as post:
            tool.execute("agentUniverse")

        args, kwargs = post.call_args
        self.assertEqual(args[0], keenable_search_tool.KEENABLE_SEARCH_URL)
        self.assertEqual(kwargs["headers"]["X-API-Key"], "test-key")

    def test_blank_query_returns_error(self):
        self.assertIn("error", KeenableSearchTool(api_key=None).execute("  "))


if __name__ == "__main__":
    unittest.main()
