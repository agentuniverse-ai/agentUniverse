# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 14:00
# @Author  : yuewang
# @FileName: test_google_search_tool.py
"""Unit tests for GoogleSearchTool."""

import asyncio
import pytest
from types import SimpleNamespace

import agentuniverse.agent.action.tool.common_tool.google_search_tool as gst
from agentuniverse.agent.action.tool.common_tool.google_search_tool import (
    GoogleSearchTool,
)


def _fake_wrapper(holder):
    """Build a fake GoogleSerperAPIWrapper capturing init kwargs."""

    class _Wrapper:
        def __init__(self, serper_api_key=None, k=None, gl=None, hl=None, type=None):
            holder['init'] = {'serper_api_key': serper_api_key, 'k': k,
                              'gl': gl, 'hl': hl, 'type': type}

        def run(self, query=None):
            holder['query'] = query
            return 'search-result'

        async def arun(self, query=None):
            holder['query'] = query
            return 'async-result'

    return _Wrapper


class TestGoogleSearchTool:
    """Test GoogleSearchTool with a mocked search wrapper."""

    def test_serper_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv('SERPER_API_KEY', 'env-key')
        assert GoogleSearchTool().serper_api_key == 'env-key'

    def test_execute(self, monkeypatch):
        holder = {}
        monkeypatch.setattr(gst, 'GoogleSerperAPIWrapper', _fake_wrapper(holder))
        tool = GoogleSearchTool(serper_api_key='sk')
        assert tool.execute('q1') == 'search-result'
        assert holder['query'] == 'q1'
        assert holder['init'] == {'serper_api_key': 'sk', 'k': 10, 'gl': 'us',
                                  'hl': 'en', 'type': 'search'}

    def test_async_execute(self, monkeypatch):
        holder = {}
        monkeypatch.setattr(gst, 'GoogleSerperAPIWrapper', _fake_wrapper(holder))
        tool = GoogleSearchTool(serper_api_key='sk')
        assert asyncio.run(tool.async_execute('q2')) == 'async-result'
        assert holder['query'] == 'q2'

    def test_execute_returns_wrapper_output_verbatim(self, monkeypatch):
        payload = SimpleNamespace(run=lambda query: f'hit-{query}')

        class _Wrapper:
            def __init__(self, **kw):
                self._p = payload

            def run(self, query=None):
                return self._p.run(query)

        monkeypatch.setattr(gst, 'GoogleSerperAPIWrapper', _Wrapper)
        assert GoogleSearchTool(serper_api_key='sk').execute('x') == 'hit-x'
