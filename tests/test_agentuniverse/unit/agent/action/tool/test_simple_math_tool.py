# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_simple_math_tool.py
"""Unit tests for the simple math tools."""

import asyncio

import pytest

from agentuniverse.agent.action.tool.common_tool.simple_math_tool import (
    AddTool,
    DivideTool,
    MultiplyTool,
    SubtractTool,
)


class TestSimpleMathTools:
    def test_add_integers(self):
        assert AddTool().execute('1,2') == 3

    def test_add_floats(self):
        assert AddTool().execute('1.5,2.5') == 4.0

    def test_subtract(self):
        assert SubtractTool().execute('10,4') == 6

    def test_multiply(self):
        assert MultiplyTool().execute('3,5') == 15

    def test_divide(self):
        assert DivideTool().execute('10,4') == 2.5

    def test_divide_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError):
            DivideTool().execute('1,0')

    def test_invalid_input_raises(self):
        with pytest.raises(ValueError):
            AddTool().execute('1,')

    def test_async_add(self):
        assert asyncio.run(AddTool().async_execute('2,3')) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
