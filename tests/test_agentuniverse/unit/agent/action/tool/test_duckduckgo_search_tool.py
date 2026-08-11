# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool import (
    DuckDuckGoSearchTool,
    DDGS,
)


class TestDuckDuckGoSearchTool(unittest.TestCase):
    """Unit tests for DuckDuckGoSearchTool."""

    def setUp(self):
        self.tool = DuckDuckGoSearchTool(
            name="duckduckgo_search_tool",
            description="Free DuckDuckGo web search",
        )

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _mock_results(self):
        return [
            {
                "title": "Python Official Site",
                "href": "https://www.python.org",
                "body": "Welcome to Python.org, the official home of Python.",
            },
            {
                "title": "Python Tutorial",
                "href": "https://docs.python.org/3/tutorial/",
                "body": "Python is an easy to learn, powerful programming language.",
            },
        ]

    # ------------------------------------------------------------------
    #  Tests
    # ------------------------------------------------------------------
    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_execute_returns_formatted_results(self):
        """execute() should return formatted search results."""
        with patch.object(self.tool, "_search") as mock_search:
            mock_search.return_value = "1. Python\n   URL: https://python.org\n   body"
            result = self.tool.execute("python programming")
            mock_search.assert_called_once()
            self.assertIn("Python", result)
            self.assertIn("URL:", result)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_execute_with_tool_input(self):
        """execute() should accept a ToolInput object."""
        with patch.object(self.tool, "_search") as mock_search:
            mock_search.return_value = "results"
            tool_input = ToolInput({"input": "test query", "max_results": 3})
            self.tool.execute(tool_input)
            args = mock_search.call_args[0]
            self.assertEqual(args[0], "test query")
            self.assertEqual(args[1], 3)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_execute_clamps_max_results(self):
        """max_results should be clamped to [1, 20]."""
        with patch.object(self.tool, "_search") as mock_search:
            mock_search.return_value = "results"
            # Too large -> clamped to 20
            self.tool.execute("query", max_results=100)
            self.assertEqual(mock_search.call_args[0][1], 20)
            # Too small -> clamped to 1
            self.tool.execute("query", max_results=0)
            self.assertEqual(mock_search.call_args[0][1], 1)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_execute_falls_back_on_error(self):
        """execute() should fall back to MockSearchTool on search failure."""
        with patch.object(self.tool, "_search", side_effect=RuntimeError("network error")):
            result = self.tool.execute("python")
            self.assertIn("DuckDuckGo search failed", result)
            self.assertIn("Falling back to mock results", result)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_async_execute(self):
        """async_execute() should return results in an event loop."""
        with patch.object(self.tool, "_search") as mock_search:
            mock_search.return_value = "async results"
            tool_input = ToolInput({"input": "async query"})
            result = asyncio.get_event_loop().run_until_complete(
                self.tool.async_execute(tool_input)
            )
            self.assertEqual(result, "async results")
            self.assertEqual(mock_search.call_args[0][0], "async query")

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_search_formats_results(self):
        """_search() should format each result with title, URL and body."""
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = iter(self._mock_results())
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)

        with patch("agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DDGS", return_value=mock_ddgs):
            result = self.tool._search("python", 5, None, "moderate")
            self.assertIn("Python Official Site", result)
            self.assertIn("https://www.python.org", result)
            self.assertIn("Welcome to Python.org", result)
            self.assertIn("Python Tutorial", result)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_search_no_results(self):
        """_search() should return a no-results message when empty."""
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = iter([])
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)

        with patch("agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DDGS", return_value=mock_ddgs):
            result = self.tool._search("nonexistent query xyzzy", 5, None, "moderate")
            self.assertIn("No results found", result)

    @unittest.skipUnless(DDGS is not None, "duckduckgo_search not installed")
    def test_search_passes_region_and_proxy(self):
        """_search() should pass region and proxy to DDGS when provided."""
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = iter(self._mock_results())
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)

        tool = DuckDuckGoSearchTool(
            name="ddg",
            proxy="http://127.0.0.1:7890",
        )
        with patch("agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DDGS", return_value=mock_ddgs):
            tool._search("query", 5, "us", "on")
            call_kwargs = mock_ddgs.text.call_args[1]
            self.assertEqual(call_kwargs["region"], "us")
            self.assertEqual(call_kwargs["safesearch"], "on")
            self.assertEqual(call_kwargs["proxy"], "http://127.0.0.1:7890")

    def test_default_attributes(self):
        """Tool should have sensible defaults."""
        self.assertEqual(self.tool.max_results, 5)
        self.assertEqual(self.tool.safesearch, "moderate")
        self.assertIsNone(self.tool.region)

    @unittest.skipIf(DDGS is not None, "duckduckgo_search is installed -- skip fallback test")
    def test_fallback_when_not_installed(self):
        """When duckduckgo_search is not installed, execute() falls back to MockSearchTool."""
        result = self.tool.execute("python")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()