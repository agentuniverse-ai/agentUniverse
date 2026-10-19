#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Tests for MistralLLM."""

import os
import tempfile
import unittest
from unittest.mock import patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.mistral_llm import MistralLLM

_MISTRAL_ENV_KEYS = ('MISTRAL_API_KEY', 'MISTRAL_API_BASE', 'MISTRAL_PROXY')

_EXAMPLE_YAML = (
    "name: 'mistral_llm'\n"
    "description: 'mistral llm'\n"
    "model_name: 'mistral-large-latest'\n"
    "api_key: '${MISTRAL_API_KEY}'\n"
    "api_base: '${MISTRAL_API_BASE}'\n"
    "proxy: '${MISTRAL_PROXY}'\n"
    "metadata:\n"
    "  type: 'LLM'\n"
    "  module: 'agentuniverse.llm.default.mistral_llm'\n"
    "  class: 'MistralLLM'\n"
)


def _build_llm_configer_from_yaml(yaml_text):
    """Load an inline YAML snippet into a real LLMConfiger so that the
    framework's `${VAR}` placeholder resolution (empty string when the
    environment variable is unset) is exercised end to end."""
    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
        f.write(yaml_text)
        path = f.name
    try:
        configer = Configer()
        configer.load_by_path(path)
        llm_configer = LLMConfiger()
        llm_configer.load_by_configer(configer)
        return llm_configer
    finally:
        os.unlink(path)


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

    def test_max_context_length_explicit_override(self):
        """A YAML-injected max_context_length must win over the model table.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which is what
        ``super().max_context_length()`` consults first.
        """
        llm = MistralLLM(model_name="mistral-large-latest", api_key="k")
        self.assertIsNone(llm._max_context_length)
        llm._max_context_length = 4096
        self.assertEqual(llm.max_context_length(), 4096)

    def test_get_num_tokens(self):
        llm = MistralLLM(model_name="mistral-large-latest", api_key="k")
        tokens = llm.get_num_tokens("hello world")
        self.assertGreater(tokens, 0)

    def test_unset_env_placeholders_fall_back_to_defaults(self):
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _MISTRAL_ENV_KEYS}
        with patch.dict("os.environ", env, clear=True):
            configer = _build_llm_configer_from_yaml(_EXAMPLE_YAML)
            llm = MistralLLM(model_name="mistral-large-latest")
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertEqual(llm.api_base, "https://api.mistral.ai/v1")
            self.assertEqual(llm.model_name, "mistral-large-latest")
            self.assertEqual(llm.name, "mistral_llm")

    def test_set_env_placeholder_values_survive_initialization(self):
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _MISTRAL_ENV_KEYS}
        env["MISTRAL_API_KEY"] = "test-key"
        env["MISTRAL_API_BASE"] = "https://example.invalid/v1"
        env["MISTRAL_PROXY"] = "http://proxy.invalid:8080"
        with patch.dict("os.environ", env, clear=True):
            configer = _build_llm_configer_from_yaml(_EXAMPLE_YAML)
            llm = MistralLLM(model_name="mistral-large-latest")
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, "test-key")
            self.assertEqual(llm.api_base, "https://example.invalid/v1")
            self.assertEqual(llm.proxy, "http://proxy.invalid:8080")


if __name__ == "__main__":
    unittest.main(verbosity=2)
