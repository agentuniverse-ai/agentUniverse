#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for MistralLLM."""

import unittest
from unittest.mock import patch

from agentuniverse.llm.default.mistral_llm import MistralLLM


class TestMistralLLMConfig(unittest.TestCase):

    def test_defaults_from_env(self):
        with patch.dict("os.environ", {
            "MISTRAL_API_KEY": "test-key",
            "MISTRAL_API_BASE": "https://api.mistral.ai/v1",
        }):
            llm = MistralLLM(model_name="mistral-large-latest")
            self.assertEqual(llm.api_key, "test-key")
            self.assertEqual(llm.api_base, "https://api.mistral.ai/v1")

    def test_api_base_default(self):
        with patch.dict("os.environ", {}, clear=True):
            llm = MistralLLM(model_name="mistral-large-latest", api_key="k")
            self.assertEqual(llm.api_base, "https://api.mistral.ai/v1")

    def test_max_context_length_large(self):
        llm = MistralLLM(model_name="mistral-large-latest", api_key="k")
        self.assertEqual(llm.max_context_length(), 128000)

    def test_max_context_length_nemo(self):
        llm = MistralLLM(model_name="open-mistral-nemo", api_key="k")
        self.assertEqual(llm.max_context_length(), 128000)

    def test_max_context_length_fallback(self):
        llm = MistralLLM(model_name="unknown-model", api_key="k")
        self.assertEqual(llm.max_context_length(), 32000)

    def test_get_num_tokens(self):
        llm = MistralLLM(model_name="mistral-large-latest", api_key="k")
        tokens = llm.get_num_tokens("hello world")
        self.assertGreater(tokens, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
