# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 00:00
# @Author  : AI Assistant
# @FileName: test_translation_by_token_agent.py

"""Unit tests for the translation_by_token_agent example module."""

import unittest
from queue import Queue

from agentuniverse.agent.input_object import InputObject

from examples.sample_apps.translation_agent_app.intelligence.agentic.agent.agent_instance.translation_agent_case.translation_by_token_agent import (
    TranslationAgent,
    calculate_chunk_size,
    output_middle_result,
)


class TestCalculateChunkSize(unittest.TestCase):
    """Test the pure chunk-size computation helper."""

    def test_chunk_size_below_limit_returns_count(self):
        """When the text fits the limit, the chunk size equals the token count."""
        self.assertEqual(calculate_chunk_size(10, 20), 10)

    def test_chunk_size_equal_to_limit(self):
        """A token count equal to the limit is returned unchanged."""
        self.assertEqual(calculate_chunk_size(20, 20), 20)

    def test_chunk_size_exact_multiple(self):
        """An exact multiple of the limit yields the limit as chunk size."""
        self.assertEqual(calculate_chunk_size(1000, 250), 250)

    def test_chunk_size_with_remainder(self):
        """A remainder is distributed across the computed chunk count."""
        self.assertEqual(calculate_chunk_size(100, 30), 27)
        self.assertEqual(calculate_chunk_size(1001, 250), 200)

    def test_chunk_size_large_input(self):
        """Large inputs still produce a positive chunk size."""
        self.assertEqual(calculate_chunk_size(5000, 300), 305)
        self.assertGreaterEqual(calculate_chunk_size(5000, 300), 1)


class TestTranslationByTokenAgent(unittest.TestCase):
    """Test deterministic methods of TranslationAgent without framework boot."""

    def setUp(self):
        """Create a plain agent instance for the tests."""
        self.agent = TranslationAgent()

    def test_output_middle_result_puts_into_stream(self):
        """output_middle_result should enqueue the data on the stream queue."""
        stream = Queue()
        output_middle_result(InputObject({'output_stream': stream}), {'step': 1})
        self.assertEqual(stream.get(), {'step': 1})
        self.assertTrue(stream.empty())

    def test_output_middle_result_without_stream_is_noop(self):
        """Without an output stream the helper should do nothing and not raise."""
        output_middle_result(InputObject({'other': 1}), {'step': 2})

    def test_parse_input_skips_output_stream(self):
        """parse_input should copy inputs but never forward the output_stream key."""
        input_object = InputObject({'source_text': 'hello', 'output_stream': Queue()})
        result = self.agent.parse_input(input_object, {'pre': 0})
        self.assertEqual(result, {'pre': 0, 'source_text': 'hello'})
        self.assertNotIn('output_stream', result)

    def test_parse_input_merges_all_inputs(self):
        """parse_input should merge every non-stream input into agent input."""
        input_object = InputObject({'source_lang': '英文', 'target_lang': '中文', 'source_text': 'text'})
        result = self.agent.parse_input(input_object, {})
        self.assertEqual(result, {'source_lang': '英文', 'target_lang': '中文', 'source_text': 'text'})

    def test_parse_result_passthrough(self):
        """parse_result should return the planner result unchanged."""
        planner_result = {'output': 'translated text'}
        self.assertEqual(self.agent.parse_result(planner_result), {'output': 'translated text'})


if __name__ == '__main__':
    unittest.main()
