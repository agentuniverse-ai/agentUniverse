# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_google_search_tool.py
"""Unit tests for GoogleSearchTool configuration."""

import pytest

from agentuniverse.agent.action.tool.common_tool.google_search_tool import GoogleSearchTool
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import Tool


class TestGoogleSearchTool:
    def test_is_tool_subclass(self):
        tool = GoogleSearchTool(name='google_search')
        assert isinstance(tool, Tool)
        assert tool.name == 'google_search'
        assert tool.tool_type == ToolTypeEnum.FUNC

    def test_serper_key_default_none(self, monkeypatch):
        monkeypatch.delenv('SERPER_API_KEY', raising=False)
        tool = GoogleSearchTool()
        assert tool.serper_api_key is None

    def test_serper_key_reads_env(self, monkeypatch):
        monkeypatch.setenv('SERPER_API_KEY', 'sk-test-value')
        tool = GoogleSearchTool()
        assert tool.serper_api_key == 'sk-test-value'

    def test_explicit_key_wins_over_env(self, monkeypatch):
        monkeypatch.setenv('SERPER_API_KEY', 'sk-env-value')
        tool = GoogleSearchTool(serper_api_key='sk-explicit')
        assert tool.serper_api_key == 'sk-explicit'

    def test_default_description_is_none(self):
        tool = GoogleSearchTool()
        assert tool.description is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
