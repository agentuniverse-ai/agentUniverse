# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : Yue Wang
# @FileName: test_insurance_maya_llm.py
import json
import unittest

from examples.startup_app.demo_startup_app_with_multi_agents.intelligence.agentic.llm.maya.insurance_maya_llm import (
    InsuranceMayaLLM,
)


class InsuranceMayaLLMParseTest(unittest.TestCase):
    """Test cases for the pure static parse helpers of InsuranceMayaLLM."""

    def test_parse_output_returns_text_from_result(self):
        output = InsuranceMayaLLM.parse_output(
            {"success": True, "result": {"output_string": "mock answer"}})
        self.assertEqual(output.text, "mock answer")

    def test_parse_output_keeps_raw_result(self):
        result = {"success": True, "result": {"output_string": "raw text"}}
        output = InsuranceMayaLLM.parse_output(result)
        self.assertEqual(output.raw, result)

    def test_parse_output_raises_without_result_key(self):
        with self.assertRaises(ValueError):
            InsuranceMayaLLM.parse_output({"success": False})

    def test_parse_stream_output_parses_line(self):
        output = InsuranceMayaLLM.parse_stream_output(
            json.dumps({"out_string": "hello"}))
        self.assertEqual(output.text, "hello")

    def test_parse_stream_output_returns_none_for_empty_line(self):
        self.assertIsNone(InsuranceMayaLLM.parse_stream_output(""))


class InsuranceMayaLLMInstanceTest(unittest.TestCase):
    """Test cases for deterministic instance methods of InsuranceMayaLLM."""

    def setUp(self):
        self.llm = InsuranceMayaLLM(
            sceneName='scene-x',
            chainName='chain-y',
            serviceId='svc-1',
            temperature=0.3,
            max_tokens=512,
        )

    def test_max_context_length(self):
        self.assertEqual(self.llm.max_context_length(), 128000)

    def test_request_data_contains_model_metadata(self):
        request = self.llm.request_data('what is insurance?', stop='END')
        self.assertEqual(request['sceneName'], 'scene-x')
        self.assertEqual(request['chainName'], 'chain-y')
        self.assertEqual(request['serviceId'], 'svc-1')
        self.assertEqual(request['features']['temperature'], 0.3)
        self.assertEqual(request['features']['stop_words'], 'END')

    def test_request_data_embeds_query_as_json(self):
        request = self.llm.request_data('what is insurance?')
        payload = json.loads(request['features']['data'])
        self.assertEqual(payload['query'], 'what is insurance?')
        self.assertFalse(payload['sync'])
        self.assertEqual(request['features']['max_output_length'], 512)

    def test_request_stream_data_matches_request_data(self):
        stream_request = self.llm.request_stream_data('question', stop='STOP')
        plain_request = self.llm.request_data('question', stop='STOP')
        self.assertEqual(stream_request, plain_request)

    def test_no_streaming_call_returns_mock_text(self):
        output = self.llm.no_streaming_call('hello')
        self.assertEqual(output.text, 'This is the llm mock response.')

    def test_streaming_call_yields_joined_mock_text(self):
        chunks = [output.text for output in self.llm.streaming_call('hello')]
        self.assertEqual(''.join(chunks), 'This is the llm mock response.')
