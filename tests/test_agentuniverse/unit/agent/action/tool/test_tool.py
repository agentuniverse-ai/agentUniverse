# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_tool.py
"""Unit tests for the base Tool and ToolInput classes."""

import asyncio

import pytest

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.annotation import trace


@pytest.fixture(autouse=True)
def disable_tool_tracing(monkeypatch):
    """Keep tool tracing (needs a configured app) out of these unit tests."""
    def passthrough(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(trace, '_tool_wrapper_sync', passthrough)
    monkeypatch.setattr(trace, '_tool_wrapper_async', passthrough)


class LegacyTool(Tool):
    """Tool whose execute accepts a ToolInput (deprecated call style)."""

    def execute(self, tool_input: ToolInput):
        return tool_input.get_data('value')


class UpperTool(Tool):
    """Tool whose execute takes keyword arguments."""

    def execute(self, input: str):
        return input.upper()


class TestToolInput:
    def test_to_dict_returns_origin_params(self):
        params = {'a': 1, 'b': 'x'}
        tool_input = ToolInput(params)
        assert tool_input.to_dict() == params

    def test_get_data_and_default(self):
        tool_input = ToolInput({'a': 1})
        assert tool_input.get_data('a') == 1
        assert tool_input.get_data('missing') is None
        assert tool_input.get_data('missing', 5) == 5

    def test_add_data_updates_origin_and_attribute(self):
        tool_input = ToolInput({'a': 1})
        tool_input.add_data('b', 2)
        assert tool_input.to_dict() == {'a': 1, 'b': 2}
        assert tool_input.get_data('b') == 2

    def test_to_json_str(self):
        tool_input = ToolInput({'a': '中文'})
        assert tool_input.to_json_str() == '{"a": "中文"}'


class TestToolRun:
    def test_run_dispatches_kwargs_style_execute(self):
        tool = UpperTool(name='upper')
        assert tool.run(input='hello') == 'HELLO'

    def test_run_dispatches_deprecated_tool_input_execute(self):
        tool = LegacyTool(name='legacy')
        assert tool.run(value=42) == 42

    def test_input_check_requires_declared_keys(self, monkeypatch):
        tool = UpperTool(name='upper', input_keys=['input'])
        monkeypatch.setattr(UpperTool, 'get_instance_code', lambda self: 'app.tool.upper')
        with pytest.raises(Exception, match='must include key'):
            tool.input_check({'other': 'x'})

    def test_async_run_kwargs_style(self):
        tool = UpperTool(name='upper')
        assert asyncio.run(tool.async_run(input='hi')) == 'HI'


class TestToolCopy:
    def test_create_copy_isolates_input_keys(self):
        tool = UpperTool(name='upper', input_keys=['a', 'b'])
        copied = tool.create_copy()
        copied.input_keys.append('c')
        assert tool.input_keys == ['a', 'b']
        assert copied.input_keys == ['a', 'b', 'c']

    def test_signature_detection(self):
        assert LegacyTool().check_execute_signature_deprecated() is True
        assert UpperTool().check_execute_signature_deprecated() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
