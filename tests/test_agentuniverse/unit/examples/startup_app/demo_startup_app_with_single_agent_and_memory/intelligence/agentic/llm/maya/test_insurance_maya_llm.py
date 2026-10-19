# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
"""Unit tests for the InsuranceMayaLLM output parsing helpers."""

import pytest

from examples.startup_app.demo_startup_app_with_single_agent_and_memory.intelligence.agentic.llm.maya.insurance_maya_llm import InsuranceMayaLLM
from agentuniverse.llm.llm_output import LLMOutput


class TestInsuranceMayaLLMParsing:
    """Test pure output parsing of the maya llm wrapper."""

    def test_parse_output_success(self):
        result = InsuranceMayaLLM.parse_output(
            {"result": {"output_string": "hello"}})
        assert isinstance(result, LLMOutput)
        assert result.text == "hello"

    def test_parse_output_missing_result_raises(self):
        with pytest.raises(ValueError, match="No output found"):
            InsuranceMayaLLM.parse_output({"other": 1})

    def test_parse_stream_output(self):
        result = InsuranceMayaLLM.parse_stream_output(
            '{"out_string": "token"}')
        assert result.text == "token"

    def test_parse_stream_output_empty_returns_none(self):
        assert InsuranceMayaLLM.parse_stream_output("") is None
