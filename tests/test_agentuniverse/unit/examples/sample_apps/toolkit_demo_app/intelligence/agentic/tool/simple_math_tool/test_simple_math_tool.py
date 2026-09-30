# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the simple math demo tools."""

import asyncio

from examples.sample_apps.toolkit_demo_app.intelligence.agentic.tool.simple_math_tool.simple_math_tool import (
    AddTool,
    DivideTool,
    MultiplyTool,
    SubtractTool,
)


class TestMathTools:
    """Test the four arithmetic tool classes."""

    def test_add(self):
        assert AddTool().execute(2.0, 3.0) == 5.0

    def test_subtract(self):
        assert SubtractTool().execute(5.0, 2.0) == 3.0

    def test_multiply(self):
        assert MultiplyTool().execute(4.0, 3.0) == 12.0

    def test_divide(self):
        assert DivideTool().execute(8.0, 2.0) == 4.0

    def test_async_execute(self):
        result = asyncio.run(AddTool().async_execute(1.0, 2.0))
        assert result == 3.0
        result = asyncio.run(MultiplyTool().async_execute(3.0, 3.0))
        assert result == 9.0
