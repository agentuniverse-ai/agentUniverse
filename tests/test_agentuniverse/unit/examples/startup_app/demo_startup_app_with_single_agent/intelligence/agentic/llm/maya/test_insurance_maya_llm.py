# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/04 00:00
# @Author  : AI Assistant
# @FileName: test_insurance_maya_llm.py

"""Unit tests for the InsuranceMayaLLM example llm."""

import unittest

from examples.startup_app.demo_startup_app_with_single_agent.intelligence.agentic.llm.maya.insurance_maya_llm import (
    InsuranceMayaLLM)


class TestInsuranceMayaLLM(unittest.TestCase):
    """Deterministic behaviors of InsuranceMayaLLM (no http / network)."""

    def setUp(self):
        self.llm = InsuranceMayaLLM()

    def test_parse_output_extracts_text_and_raw(self):
        result = {"result": {"output_string": "answer text"}}
        output = InsuranceMayaLLM.parse_output(result)
        self.assertEqual(output.text, "answer text")
        self.assertEqual(output.raw, result)

    def test_parse_output_missing_result_raises(self):
        with self.assertRaises(ValueError):
            InsuranceMayaLLM.parse_output({"foo": "bar"})

    def test_parse_stream_output_empty_line_returns_none(self):
        self.assertIsNone(InsuranceMayaLLM.parse_stream_output(''))
        self.assertIsNone(InsuranceMayaLLM.parse_stream_output(None))

    def test_parse_stream_output_parses_line(self):
        output = InsuranceMayaLLM.parse_stream_output('{"out_string": "token text"}')
        self.assertEqual(output.text, "token text")
        self.assertEqual(output.raw, {"out_string": "token text"})

    def test_no_streaming_call_returns_mock_response(self):
        output = self.llm.no_streaming_call(prompt="hello", stop=["\n"])
        self.assertEqual(output.text, "This is the llm mock response.")

    def test_request_data_payload_shape(self):
        payload = self.llm.request_data("question?", stop="STOP")
        self.assertEqual(payload["sceneName"], self.llm.sceneName)
        self.assertIn('"query": "question?"', payload["features"]["data"])
        self.assertEqual(payload["features"]["stop_words"], "STOP")

    def test_streaming_call_yields_chunk_texts(self):
        chunks = list(self.llm.streaming_call(prompt="hi"))
        self.assertEqual(''.join(c.text for c in chunks),
                         "This is the llm mock response.")

    def test_max_context_length(self):
        self.assertEqual(self.llm.max_context_length(), 128000)


if __name__ == '__main__':
    unittest.main()
