# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_search_context_tool.py
"""Unit tests for the SearchContextTool demo knowledge-retrieval tool."""

from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.agentic.tool.insurance_search_context_tool import (
    MockAPI,
    MockResponse,
    SearchContextTool,
)


class TestMockApi:
    """Test the mock API helpers used by the tool."""

    def test_mock_response_returns_json(self):
        response = MockResponse({"result": {}})
        assert response.json() == {"result": {}}

    def test_mock_api_post_returns_recall_tuples(self):
        response = MockAPI().post('url', {'Content-Type': 'application/json'}, '{}')
        tuples = response.json()['result']['recallResultTuples']
        assert len(tuples) == 3


class TestSearchContextTool:
    """Test SearchContextTool.execute output assembly."""

    def test_execute_with_top_k_two_limits_results(self):
        result = SearchContextTool().execute('保险产品A升级规则', top_k=2)
        assert '提出的问题是:保险产品A升级规则' in result
        assert 'mock data: 保险产品A升级规则' in result
        assert 'mock data: 保险产品A简介' in result
        assert '保障期限12个月' not in result

    def test_execute_with_top_k_one_returns_single_block(self):
        result = SearchContextTool().execute('保险产品A升级规则', top_k=1)
        assert result.count('knowledgeTitle:') == 1
        assert '不支持升级' in result
        assert '免费体验版' not in result

    def test_execute_with_large_top_k_returns_all_blocks(self):
        result = SearchContextTool().execute('保险产品A', top_k=10)
        assert result.count('knowledgeTitle:') == 3
        assert '保障期限12个月' in result

    def test_execute_with_zero_top_k_returns_header_only(self):
        result = SearchContextTool().execute('question', top_k=0)
        assert '提出的问题是:question' in result
        assert 'knowledgeTitle:' not in result

    def test_execute_includes_question_and_content_fields(self):
        result = SearchContextTool().execute('保险产品A简介', top_k=2)
        assert 'knowledgeTitle: mock data: 保险产品A简介' in result
        assert 'knowledgeContent:' in result
