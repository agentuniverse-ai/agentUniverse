# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the ParamConverterTool."""

from agentuniverse.agent.output_object import OutputObject
from examples.sample_apps.openai_protocol_app.intelligence.agentic.tool.param_converter import ParamConverterTool


class TestParamConverterTool:
    """Test parameter conversion behavior."""

    def test_groups_other_params_under_result_key(self):
        result = ParamConverterTool().execute(
            {"final_result": 1, "a": 2, "b": 3})
        assert list(result.keys()) == ["final_result"]
        inner = result["final_result"]
        assert isinstance(inner, OutputObject)
        assert inner.get_data("a") == 2
        assert inner.get_data("b") == 3

    def test_no_result_key_returns_empty(self):
        assert ParamConverterTool().execute({"x": 1}) == {}

    def test_only_result_key_uses_original_params(self):
        result = ParamConverterTool().execute({"final_result": 1})
        inner = result["final_result"]
        assert inner.to_dict() == {"final_result": 1}
