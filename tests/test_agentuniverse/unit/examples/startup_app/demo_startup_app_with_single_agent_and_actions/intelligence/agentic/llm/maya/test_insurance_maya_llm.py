# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_maya_llm.py
"""Unit tests for the InsuranceMayaLLM demo LLM implementation."""

import json

import pytest

from agentuniverse.llm.llm_output import LLMOutput
from examples.startup_app.demo_startup_app_with_single_agent_and_actions.intelligence.agentic.llm.maya.insurance_maya_llm import (
    InsuranceMayaLLM,
)


class TestInsuranceMayaLLM:
    """Test InsuranceMayaLLM static helpers and request payload builders."""

    @pytest.fixture
    def llm(self):
        instance = InsuranceMayaLLM()
        instance.sceneName = 'scene-1'
        instance.chainName = 'chain-1'
        instance.serviceId = 'service-1'
        return instance

    def test_parse_output_extracts_text(self):
        result = {"success": True, "result": {"output_string": "hello"}}
        output = InsuranceMayaLLM.parse_output(result)
        assert isinstance(output, LLMOutput)
        assert output.text == 'hello'
        assert output.raw == result

    def test_parse_output_raises_without_result(self):
        with pytest.raises(ValueError, match='No output found'):
            InsuranceMayaLLM.parse_output({"success": True})

    def test_parse_stream_output(self):
        output = InsuranceMayaLLM.parse_stream_output(json.dumps({"out_string": "This "}))
        assert isinstance(output, LLMOutput)
        assert output.text == 'This '
        assert output.raw == {"out_string": "This "}

    def test_parse_stream_output_handles_blank_line(self):
        assert InsuranceMayaLLM.parse_stream_output('') is None
        assert InsuranceMayaLLM.parse_stream_output(None) is None

    def test_request_data_payload(self, llm):
        payload = llm.request_data('tell me', stop='\n')
        assert payload['sceneName'] == 'scene-1'
        assert payload['chainName'] == 'chain-1'
        assert payload['serviceId'] == 'service-1'
        features = payload['features']
        assert json.loads(features['data']) == {'query': 'tell me', 'sync': False}
        assert features['stop_words'] == '\n'
        assert features['max_output_length'] == llm.max_tokens

    def test_request_stream_data_payload(self, llm):
        payload = llm.request_stream_data('hi', stop='')
        features = payload['features']
        assert json.loads(features['data']) == {'query': 'hi', 'sync': False}
        assert features['temperature'] == llm.temperature

    def test_no_streaming_call_returns_mock_output(self, llm):
        output = llm.no_streaming_call('question')
        assert isinstance(output, LLMOutput)
        assert 'mock response' in output.text

    def test_streaming_call_yields_chunks(self, llm):
        chunks = [c.text for c in llm.streaming_call('question')]
        assert chunks == ['This ', 'is ', 'the ', 'llm ', 'mock ', 'response', '.']
