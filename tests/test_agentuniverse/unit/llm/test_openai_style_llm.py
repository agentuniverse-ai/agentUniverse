#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestOpenAIStyleLLMMaxContextLength(unittest.TestCase):
    def test_returns_int_for_known_model_without_explicit_config(self) -> None:
        llm = OpenAIStyleLLM(name='test_llm', model_name='gpt-4o', api_key='ak')
        self.assertEqual(llm.max_context_length(), 128000)

    def test_returns_int_fallback_for_unknown_model(self) -> None:
        llm = OpenAIStyleLLM(name='test_llm', model_name='not-a-known-model', api_key='ak')
        self.assertEqual(llm.max_context_length(), 4096)

    def test_explicitly_configured_context_length_wins(self) -> None:
        llm = OpenAIStyleLLM(name='test_llm', model_name='gpt-4o', api_key='ak')
        llm._max_context_length = 8192
        self.assertEqual(llm.max_context_length(), 8192)


if __name__ == '__main__':
    unittest.main()
