#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the 01.AI Yi series LLM component.

These tests exercise the parts of :class:`YiLLM` that do not require a
live 01.AI API key: credential/base-url wiring, the per-model context
length table and the token estimator. The network-bound call/acall/stream
tests are kept but commented out so that the full suite can run in CI
without any external dependency.
"""

import asyncio
import os
import tempfile
import unittest
from unittest import mock

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.yi_llm import (
    YI_DEFAULT_CONTEXT_LENGTH,
    YI_MAX_CONTEXT_LENGTH,
    YiLLM,
)

_YI_ENV_KEYS = ('YI_API_KEY', 'YI_API_BASE', 'YI_PROXY', 'YI_ORGANIZATION')


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


class TestYiLLM(unittest.TestCase):
    """Test suite for the YiLLM component."""

    def setUp(self) -> None:
        """Build a YiLLM instance with dummy credentials."""
        self.llm = YiLLM(
            model_name='yi-large',
            api_key='dummy-yi-key',
            api_base='https://api.01.ai/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'yi-large')
        self.assertEqual(self.llm.api_key, 'dummy-yi-key')
        self.assertEqual(self.llm.api_base, 'https://api.01.ai/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the 01.AI endpoint must be used."""
        llm = YiLLM(model_name='yi-large', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://api.01.ai/v1')

    def test_max_context_length_known_models(self) -> None:
        """Known models must resolve to their documented context window."""
        known = [
            ('yi-large', 32768),
            ('yi-medium', 16384),
            ('yi-small', 16384),
            ('yi-vision', 16384),
            ('yi-medium-200k', 204800),
        ]
        for model_name, expected in known:
            llm = YiLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_unknown_model(self) -> None:
        """Unknown models must fall back to the default context length."""
        llm = YiLLM(model_name='some-future-yi-model', api_key='dummy')
        self.assertEqual(llm.max_context_length(), YI_DEFAULT_CONTEXT_LENGTH)

    def test_max_context_length_table_consistency(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in YI_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_get_num_tokens(self) -> None:
        """The token estimator must return a sensible positive count."""
        text = 'Hello Yi, please introduce yourself.'
        num_tokens = self.llm.get_num_tokens(text)
        self.assertIsInstance(num_tokens, int)
        self.assertGreater(num_tokens, 0)
        # The estimator must be deterministic for the same input.
        self.assertEqual(num_tokens, self.llm.get_num_tokens(text))

    def test_get_num_tokens_empty_string(self) -> None:
        """An empty string must cost zero tokens."""
        self.assertEqual(self.llm.get_num_tokens(''), 0)

    # ========== YAML ${VAR} placeholder handling ==========

    _EXAMPLE_YAML = (
        "name: 'default_yi_llm'\n"
        "description: 'yi llm'\n"
        "model_name: 'yi-large'\n"
        "api_key: '${YI_API_KEY}'\n"
        "api_base: '${YI_API_BASE}'\n"
        "organization: '${YI_ORGANIZATION}'\n"
        "proxy: '${YI_PROXY}'\n"
        "metadata:\n"
        "  type: 'LLM'\n"
        "  module: 'agentuniverse.llm.default.yi_llm'\n"
        "  class: 'YiLLM'\n"
    )

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _YI_ENV_KEYS}
        with mock.patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = YiLLM(model_name='yi-large')
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertIsNone(llm.organization)
            self.assertEqual(llm.api_base, 'https://api.01.ai/v1')
            self.assertEqual(llm.model_name, 'yi-large')
            self.assertEqual(llm.name, 'default_yi_llm')

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _YI_ENV_KEYS}
        env['YI_API_KEY'] = 'yi-test-key'
        env['YI_API_BASE'] = 'https://example.invalid/v1'
        env['YI_PROXY'] = 'http://proxy.invalid:8080'
        env['YI_ORGANIZATION'] = 'yi-org'
        with mock.patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = YiLLM(model_name='yi-large')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'yi-test-key')
            self.assertEqual(llm.api_base, 'https://example.invalid/v1')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')
            self.assertEqual(llm.organization, 'yi-org')

    # ========== Integration tests (require a real YI_API_KEY) ==========
    # Uncomment and set YI_API_KEY in the environment to exercise the
    # live 01.AI API.

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
