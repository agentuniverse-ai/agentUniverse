# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the SearchContextTool demo tool (mock api)."""

from examples.startup_app.demo_startup_app_with_agent_templates.intelligence.agentic.tool.insurance_search_context_tool import MockAPI, MockResponse, SearchContextTool


class TestMockResponse:
    """Test the mock response object."""

    def test_json_returns_stored_payload(self):
        response = MockResponse({"a": 1})
        assert response.json() == {"a": 1}

    def test_post_returns_mock_response(self):
        response = MockAPI().post("http://x", headers={}, data="")
        assert response.json()["result"]["recallResultTuples"]


class TestSearchContextTool:
    """Test the search context tool execution."""

    def test_execute_returns_context_string(self):
        tool = SearchContextTool()
        result = tool.execute("保险产品A", top_k=1)
        assert "提出的问题是:" in result

    def test_execute_includes_recalled_content(self):
        tool = SearchContextTool()
        result = tool.execute("保险产品A", top_k=5)
        assert "knowledgeTitle:" in result
        assert "knowledgeContent:" in result

    def test_execute_top_k_limits_results(self):
        tool = SearchContextTool()
        result = tool.execute("保险产品A", top_k=1)
        assert result.count("knowledgeTitle:") == 1
