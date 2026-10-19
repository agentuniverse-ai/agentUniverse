#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Together AI LLM component.

These tests exercise the parts of :class:`TogetherLLM` that do not require a
live Together AI API key: credential/base-url wiring, the per-model context
length table and the token estimator. The network-bound call/acall/stream
tests are kept but commented out so the full suite runs in CI without any
external dependency.
"""

import asyncio
import os
import tempfile
import unittest
from unittest import mock

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.together_llm import (
    TOGETHER_DEFAULT_CONTEXT_LENGTH,
    TOGETHER_MAX_CONTEXT_LENGTH,
    TogetherLLM,
)

_TOGETHER_ENV_KEYS = ('TOGETHER_API_KEY', 'TOGETHER_API_BASE',
                      'TOGETHER_PROXY', 'TOGETHER_ORGANIZATION')

_EXAMPLE_YAML = (
    "name: 'default_together_llm'\n"
    "description: 'together llm'\n"
    "model_name: 'meta-llama/Llama-3.3-70B-Instruct-Turbo'\n"
    "api_key: '${TOGETHER_API_KEY}'\n"
    "api_base: '${TOGETHER_API_BASE}'\n"
    "organization: '${TOGETHER_ORGANIZATION}'\n"
    "proxy: '${TOGETHER_PROXY}'\n"
    "metadata:\n"
    "  type: 'LLM'\n"
    "  module: 'agentuniverse.llm.default.together_llm'\n"
    "  class: 'TogetherLLM'\n"
)


def _build_llm_configer_from_yaml(yaml_text: str) -> LLMConfiger:
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


class TestTogetherLLM(unittest.TestCase):
    """Test suite for the TogetherLLM component."""

    def setUp(self) -> None:
        """Build a TogetherLLM instance with dummy credentials."""
        self.llm = TogetherLLM(
            model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo',
            api_key='dummy-together-key',
            api_base='https://api.together.xyz/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'meta-llama/Llama-3.3-70B-Instruct-Turbo')
        self.assertEqual(self.llm.api_key, 'dummy-together-key')
        self.assertEqual(self.llm.api_base, 'https://api.together.xyz/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the Together endpoint must be used."""
        llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://api.together.xyz/v1')

    def test_max_context_length_known_models(self) -> None:
        """Known models must resolve to their documented context window."""
        known = [
            ('meta-llama/Llama-3.3-70B-Instruct-Turbo', 131072),
            ('meta-llama/Meta-Llama-3-8B-Instruct-Lite', 8192),
            ('mistralai/Mixtral-8x7B-Instruct-v0.1', 32768),
            ('Qwen/Qwen2.5-72B-Instruct-Turbo', 131072),
            ('deepseek-ai/DeepSeek-V3', 131072),
        ]
        for model_name, expected in known:
            llm = TogetherLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_unknown_model(self) -> None:
        """Unknown models must fall back to the default context length."""
        llm = TogetherLLM(model_name='some-future-together-model', api_key='dummy')
        self.assertEqual(llm.max_context_length(), TOGETHER_DEFAULT_CONTEXT_LENGTH)

    def test_max_context_length_explicit_override(self) -> None:
        """A YAML-injected max_context_length must win over the table.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which is what
        ``super().max_context_length()`` consults first.
        """
        llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo', api_key='dummy')
        self.assertIsNone(llm._max_context_length)
        llm._max_context_length = 4096
        self.assertEqual(llm.max_context_length(), 4096)

    def test_max_context_length_table_consistency(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in TOGETHER_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_get_num_tokens(self) -> None:
        """The token estimator must return a sensible positive count."""
        text = 'Hello Together AI, please introduce yourself.'
        num_tokens = self.llm.get_num_tokens(text)
        self.assertIsInstance(num_tokens, int)
        self.assertGreater(num_tokens, 0)
        # The estimator must be deterministic for the same input.
        self.assertEqual(num_tokens, self.llm.get_num_tokens(text))

    def test_get_num_tokens_empty_string(self) -> None:
        """An empty string must cost zero tokens."""
        self.assertEqual(self.llm.get_num_tokens(''), 0)

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _TOGETHER_ENV_KEYS}
        with mock.patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(_EXAMPLE_YAML)
            llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertIsNone(llm.organization)
            self.assertEqual(llm.api_base, 'https://api.together.xyz/v1')
            self.assertEqual(llm.model_name, 'meta-llama/Llama-3.3-70B-Instruct-Turbo')
            self.assertEqual(llm.name, 'default_together_llm')

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _TOGETHER_ENV_KEYS}
        env['TOGETHER_API_KEY'] = 'together-test-key'
        env['TOGETHER_API_BASE'] = 'https://example.invalid/v1'
        env['TOGETHER_PROXY'] = 'http://proxy.invalid:8080'
        env['TOGETHER_ORGANIZATION'] = 'org-123'
        with mock.patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(_EXAMPLE_YAML)
            llm = TogetherLLM(model_name='meta-llama/Llama-3.3-70B-Instruct-Turbo')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'together-test-key')
            self.assertEqual(llm.api_base, 'https://example.invalid/v1')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')
            self.assertEqual(llm.organization, 'org-123')

    # ========== Integration tests (require a real TOGETHER_API_KEY) ==========
    # Uncomment and set TOGETHER_API_KEY in the environment to exercise the
    # live Together AI API.

    # def test_call(self) -> None:
    #     messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
    #     output = self.llm.call(messages=messages, streaming=False)
    #     print(output.__str__())
    #     self.assertIsNotNone(output.text)

    # def test_acall(self) -> None:
    #     messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
    #     output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
    #     print(output.__str__())
    #     self.assertIsNotNone(output.text)

    # def test_call_stream(self) -> None:
    #     messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
    #     chunks = []
    #     for chunk in self.llm.call(messages=messages, streaming=True):
    #         chunks.append(chunk.text)
    #     self.assertGreater(len(''.join(chunks)), 0)

    # def test_acall_stream(self) -> None:
    #     messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
    #
    #     async def _run():
    #         result = []
    #         async for chunk in await self.llm.acall(messages=messages, streaming=True):
    #             result.append(chunk.text)
    #         return result
    #
    #     chunks = asyncio.run(_run())
    #     self.assertGreater(len(''.join(chunks)), 0)

    # def test_as_langchain(self) -> None:
    #     from langchain.chains.conversation.base import ConversationChain
    #     langchain_llm = self.llm.as_langchain()
    #     llm_chain = ConversationChain(llm=langchain_llm)
    #     res = llm_chain.predict(input='Say hello')
    #     self.assertIsNotNone(res)


if __name__ == '__main__':
    unittest.main()
