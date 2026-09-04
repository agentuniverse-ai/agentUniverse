#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.agent.action.tool.common_tool import tavily_tool


class TavilyToolTest(unittest.TestCase):
    """Unit tests for TavilyTool behavior."""
    def test_missing_optional_dependency_is_reported_when_used(self):
        """Verify executing the tool without the optional tavily dependency reports a clear error mentioning tavily-python."""
        tool = tavily_tool.TavilyTool(api_key="test-key")

        with patch.object(tavily_tool, "TavilyClient", None), patch.object(
            tavily_tool, "_TAVILY_IMPORT_ERROR", ImportError("missing tavily")
        ):
            result = tool.execute("agentUniverse")

        self.assertIn("error", result)
        self.assertIn("tavily-python", result["error"])


if __name__ == "__main__":
    unittest.main()
