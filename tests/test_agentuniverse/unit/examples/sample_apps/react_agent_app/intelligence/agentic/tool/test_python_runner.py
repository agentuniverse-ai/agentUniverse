# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the PythonRunner demo tool."""

from examples.sample_apps.react_agent_app.intelligence.agentic.tool.python_runner import PythonRunner


class TestPythonRunner:
    """Test python code execution helper."""

    def test_execute_direct_expression(self):
        tool = PythonRunner()
        result = tool.execute("print(1 + 2)")
        assert "3" in result

    def test_execute_code_fence(self):
        tool = PythonRunner()
        result = tool.execute("```python\nprint(6 * 7)\n```")
        assert "42" in result

    def test_execute_without_output_returns_error(self):
        tool = PythonRunner()
        result = tool.execute("```python\nx = 1\n```")
        assert result.startswith("ERROR")
