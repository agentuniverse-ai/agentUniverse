# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 12:00
# @Author  : Yue Wang
# @FileName: test_param_converter.py
"""Unit tests for param_converter."""

import pytest

from examples.sample_apps.peer_agent_app.intelligence.agentic.tool.param_converter import (
    ParamConverterTool,
)


class TestParamConverterTool:
    """Test ParamConverterTool.execute."""

    @pytest.fixture
    def tool(self):
        return ParamConverterTool()

    def test_returns_empty_when_no_result_key(self, tool):
        assert tool.execute({"query": "q", "mode": "fast"}) == {}

    def test_single_result_key_wraps_rest(self, tool):
        result = tool.execute({"analysis_result": "x", "query": "q", "mode": "fast"})
        assert list(result.keys()) == ["analysis_result"]
        inner = result["analysis_result"]
        assert inner.get_data("query") == "q"
        assert inner.get_data("mode") == "fast"
        assert inner.get_data("analysis_result") is None

    def test_keeps_values_intact(self, tool):
        result = tool.execute({"summary_result": {"score": 3}, "query": "q"})
        assert result["summary_result"].get_data("query") == "q"
        assert result["summary_result"].get_data("summary_result") is None

    def test_only_result_key_wraps_original_params(self, tool):
        result = tool.execute({"only_result": "v"})
        assert list(result.keys()) == ["only_result"]
        assert result["only_result"].get_data("only_result") == "v"

    def test_first_result_key_wins(self, tool):
        result = tool.execute({"a_result": 1, "b_result": 2, "x": 3})
        assert list(result.keys()) == ["a_result"]
        inner = result["a_result"]
        assert inner.get_data("x") == 3
        assert inner.get_data("b_result") == 2

    def test_returns_output_object(self, tool):
        from agentuniverse.agent.output_object import OutputObject

        result = tool.execute({"analysis_result": "x", "query": "q"})
        assert isinstance(result["analysis_result"], OutputObject)

    def test_does_not_mutate_input(self, tool):
        params = {"analysis_result": "x", "query": "q"}
        tool.execute(params)
        assert params == {"analysis_result": "x", "query": "q"}
