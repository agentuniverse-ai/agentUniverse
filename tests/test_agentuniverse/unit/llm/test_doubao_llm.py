#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Doubao (Volcengine Ark) LLM component.

These tests exercise :class:`DoubaoLLM` fully offline: the network-bound
OpenAI-style client is replaced with fakes/mocks so that the sync call, the
async call, both streaming flavours, the component-configer initialisation,
the environment-variable fallback (``ARK_API_KEY`` with the ``DOUBAO_API_KEY``
alias), the YAML ``${VAR}`` placeholder guard and the per-model
context-length table (including dated Ark model-ID suffixes) can all be
verified in CI without a live Ark API key.
"""

import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, Mock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.doubao_llm import (
    DOUBAO_API_BASE_DEFAULT,
    DOUBAO_DEFAULT_CONTEXT_LENGTH,
    DOUBAO_MAX_CONTEXT_LENGTH,
    DoubaoLLM,
)

_DOUBAO_ENV_KEYS = ('ARK_API_KEY', 'DOUBAO_API_KEY', 'DOUBAO_API_BASE', 'DOUBAO_PROXY')


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


class _FakeMessage:
    """Mimics ``openai.types.chat.ChatCompletionMessage``."""

    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    """Mimics ``openai.types.chat.ChatCompletionChoice``."""

    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeChatCompletion:
    """Mimics a non-streaming ``openai.ChatCompletion`` response."""

    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]
        self._raw = {'id': 'chatcmpl-fake', 'choices': [{'message': {'role': 'assistant', 'content': content}}]}

    def model_dump(self) -> dict:
        return self._raw


class _FakeStreamChunk:
    """Mimics one chunk of an ``openai.Stream`` response."""

    def __init__(self, text: str) -> None:
        self._text = text

    def dict(self) -> dict:
        return {'choices': [{'delta': {'content': self._text}}]}

    def model_dump(self) -> dict:
        return self.dict()


class _FakeStream:
    """Synchronous iterable of :class:`_FakeStreamChunk`."""

    def __init__(self, texts: list) -> None:
        self._chunks = [_FakeStreamChunk(t) for t in texts]

    def __iter__(self):
        return iter(self._chunks)


class _FakeAsyncStream:
    """Asynchronous iterable of :class:`_FakeStreamChunk`."""

    def __init__(self, texts: list) -> None:
        self._chunks = [_FakeStreamChunk(t) for t in texts]
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self) -> _FakeStreamChunk:
        if self._index >= len(self._chunks):
            raise StopAsyncIteration
        chunk = self._chunks[self._index]
        self._index += 1
        return chunk


def _mock_client(completion) -> Mock:
    """Build a fake sync OpenAI-style client returning ``completion``."""
    client = Mock()
    client.chat.completions.create.return_value = completion
    return client


def _mock_async_client(completion) -> Mock:
    """Build a fake async OpenAI-style client returning ``completion``."""
    client = Mock()
    client.chat.completions.create = AsyncMock(return_value=completion)
    return client


class TestDoubaoLLM(unittest.TestCase):
    """Test suite for the DoubaoLLM component."""

    def setUp(self) -> None:
        """Build a DoubaoLLM instance with dummy credentials."""
        self.llm = DoubaoLLM(
            model_name='doubao-pro-32k',
            api_key='dummy-ark-key',
            api_base=DOUBAO_API_BASE_DEFAULT,
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'doubao-pro-32k')
        self.assertEqual(self.llm.api_key, 'dummy-ark-key')
        self.assertEqual(self.llm.api_base, DOUBAO_API_BASE_DEFAULT)
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the Ark endpoint must be used."""
        llm = DoubaoLLM(model_name='doubao-pro-32k', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://ark.cn-beijing.volces.com/api/v3')

    def test_env_fallback_ark_key(self) -> None:
        """api_key/api_base must fall back to the ARK_API_KEY / DOUBAO_API_BASE env variables."""
        env = {'ARK_API_KEY': 'ark-from-env', 'DOUBAO_API_BASE': 'https://env.example/api/v3'}
        with patch.dict(os.environ, env):
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            self.assertEqual(llm.api_key, 'ark-from-env')
            self.assertEqual(llm.api_base, 'https://env.example/api/v3')

    def test_env_fallback_doubao_key_alias(self) -> None:
        """With ARK_API_KEY unset the DOUBAO_API_KEY alias must be used."""
        env = {k: v for k, v in os.environ.items() if k not in _DOUBAO_ENV_KEYS}
        env['DOUBAO_API_KEY'] = 'doubao-from-env'
        with patch.dict(os.environ, env, clear=True):
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            self.assertEqual(llm.api_key, 'doubao-from-env')

    def test_ark_key_wins_over_doubao_alias(self) -> None:
        """When both variables are set ARK_API_KEY takes precedence."""
        env = {k: v for k, v in os.environ.items() if k not in _DOUBAO_ENV_KEYS}
        env['ARK_API_KEY'] = 'ark-primary'
        env['DOUBAO_API_KEY'] = 'doubao-alias'
        with patch.dict(os.environ, env, clear=True):
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            self.assertEqual(llm.api_key, 'ark-primary')

    def test_no_env_defaults(self) -> None:
        """Without env variables api_key is unset and api_base is the Ark URL."""
        env = {k: v for k, v in os.environ.items() if k not in _DOUBAO_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            self.assertIsNone(llm.api_key)
            self.assertEqual(llm.api_base, DOUBAO_API_BASE_DEFAULT)

    def test_initialize_by_component_configer(self) -> None:
        """The component configer must override model/credential settings."""
        configer = Configer()
        configer.value = {
            'name': 'configured_doubao_llm',
            'description': 'doubao llm configured through yaml',
            'model_name': 'doubao-lite-32k',
            'max_tokens': 256,
            'temperature': 0.3,
            'streaming': False,
            'api_key': 'ark-configured',
            'api_base': DOUBAO_API_BASE_DEFAULT,
            'max_context_length': 4096,
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = DoubaoLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.name, 'configured_doubao_llm')
        self.assertEqual(llm.model_name, 'doubao-lite-32k')
        self.assertEqual(llm.api_key, 'ark-configured')
        self.assertEqual(llm.api_base, DOUBAO_API_BASE_DEFAULT)
        self.assertEqual(llm.max_tokens, 256)
        self.assertEqual(llm.max_context_length(), 4096)

    def test_max_context_length_known_models(self) -> None:
        """Known models must resolve to their documented context window."""
        known = [
            ('doubao-pro-32k', 32768),
            ('doubao-pro-128k', 131072),
            ('doubao-1.5-pro-256k', 262144),
            ('doubao-lite-32k', 32768),
        ]
        for model_name, expected in known:
            llm = DoubaoLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_dated_suffix(self) -> None:
        """Dated Ark model IDs (e.g. ``doubao-pro-32k-250527``) must resolve
        to their family's context window."""
        dated = [
            ('doubao-pro-32k-250527', 32768),
            ('doubao-1.5-pro-256k-250115', 262144),
            ('doubao-lite-32k-241015', 32768),
        ]
        for model_name, expected in dated:
            llm = DoubaoLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_unknown_model(self) -> None:
        """Unknown models (incl. Ark endpoint IDs) must fall back to the default."""
        for model_name in ('some-future-doubao-model', 'ep-20250527-0000zz'):
            llm = DoubaoLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(llm.max_context_length(), DOUBAO_DEFAULT_CONTEXT_LENGTH)
        self.assertEqual(DOUBAO_DEFAULT_CONTEXT_LENGTH, 8192)

    def test_max_context_length_explicit_override(self) -> None:
        """A YAML-injected max_context_length must win over the table.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which must be
        consulted before the Doubao-specific table.
        """
        llm = DoubaoLLM(model_name='doubao-pro-32k', api_key='dummy')
        self.assertIsNone(llm._max_context_length)
        llm._max_context_length = 4096
        self.assertEqual(llm.max_context_length(), 4096)

    def test_max_context_length_table_consistency(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in DOUBAO_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_call_with_mocked_client(self) -> None:
        """A non-streaming sync call must return the mocked completion."""
        llm = DoubaoLLM(
            model_name='doubao-pro-32k',
            api_key='dummy',
            client=_mock_client(_FakeChatCompletion('Hello from Doubao!')),
        )
        messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
        output = llm._call(messages=messages, streaming=False)
        self.assertEqual(output.text, 'Hello from Doubao!')
        self.assertEqual(output.raw['choices'][0]['message']['content'], 'Hello from Doubao!')
        create_kwargs = llm.client.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'doubao-pro-32k')
        self.assertFalse(create_kwargs['stream'])
        self.assertEqual(llm.client.base_url, DOUBAO_API_BASE_DEFAULT)

    def test_call_stream_with_mocked_client(self) -> None:
        """A streaming sync call must yield the mocked chunks in order."""
        llm = DoubaoLLM(
            model_name='doubao-pro-128k',
            api_key='dummy',
            client=_mock_client(_FakeStream(['Hello', ' ', 'Doubao', '!'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
        chunks = [chunk.text for chunk in llm._call(messages=messages, streaming=True)]
        self.assertEqual(chunks, ['Hello', ' ', 'Doubao', '!'])
        self.assertTrue(llm.client.chat.completions.create.call_args.kwargs['stream'])

    def test_acall_with_mocked_client(self) -> None:
        """A non-streaming async call must return the mocked completion."""
        llm = DoubaoLLM(
            model_name='doubao-pro-32k',
            api_key='dummy',
            async_client=_mock_async_client(_FakeChatCompletion('Hello async!')),
        )
        messages = [{'role': 'user', 'content': 'Say hello in one word.'}]

        async def _run():
            return await llm._acall(messages=messages, streaming=False)

        output = asyncio.run(_run())
        self.assertEqual(output.text, 'Hello async!')
        self.assertEqual(output.raw['choices'][0]['message']['content'], 'Hello async!')

    def test_acall_stream_with_mocked_client(self) -> None:
        """A streaming async call must yield the mocked chunks in order."""
        llm = DoubaoLLM(
            model_name='doubao-lite-32k',
            api_key='dummy',
            async_client=_mock_async_client(_FakeAsyncStream(['Hi', ' ', 'there'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]

        async def _run():
            stream = await llm._acall(messages=messages, streaming=True)
            return [chunk.text async for chunk in stream]

        chunks = asyncio.run(_run())
        self.assertEqual(chunks, ['Hi', ' ', 'there'])

    def test_get_num_tokens(self) -> None:
        """The token estimator must return a sensible positive count."""
        text = 'Hello Doubao, please introduce yourself.'
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
        "name: 'doubao_llm'\n"
        "description: 'doubao llm on volcengine ark'\n"
        "model_name: 'doubao-pro-32k'\n"
        "api_key: '${ARK_API_KEY}'\n"
        "api_base: '${DOUBAO_API_BASE}'\n"
        "proxy: '${DOUBAO_PROXY}'\n"
        "metadata:\n"
        "  type: 'LLM'\n"
        "  module: 'agentuniverse.llm.default.doubao_llm'\n"
        "  class: 'DoubaoLLM'\n"
    )

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _DOUBAO_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertEqual(llm.api_base, DOUBAO_API_BASE_DEFAULT)
            self.assertEqual(llm.model_name, 'doubao-pro-32k')
            self.assertEqual(llm.name, 'doubao_llm')

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _DOUBAO_ENV_KEYS}
        env['ARK_API_KEY'] = 'ark-test-key'
        env['DOUBAO_API_BASE'] = 'https://example.invalid/api/v3'
        env['DOUBAO_PROXY'] = 'http://proxy.invalid:8080'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'ark-test-key')
            self.assertEqual(llm.api_base, 'https://example.invalid/api/v3')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')

    def test_doubao_key_alias_survives_placeholder_initialization(self) -> None:
        """With ARK_API_KEY unset but DOUBAO_API_KEY set the alias must fill
        the empty ``${ARK_API_KEY}`` placeholder during initialization."""
        env = {k: v for k, v in os.environ.items()
               if k not in _DOUBAO_ENV_KEYS}
        env['DOUBAO_API_KEY'] = 'doubao-alias-key'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'doubao-alias-key')

    def test_env_base_used_when_api_key_placeholder_empty(self) -> None:
        """With an empty api_base placeholder but a set DOUBAO_API_BASE the
        environment override must win over the hard-coded default."""
        env = {k: v for k, v in os.environ.items()
               if k not in _DOUBAO_ENV_KEYS}
        env['DOUBAO_API_BASE'] = 'https://ark.ap-southeast.bytepluses.com/api/v3'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = DoubaoLLM(model_name='doubao-pro-32k')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_base, 'https://ark.ap-southeast.bytepluses.com/api/v3')

    # ========== Integration tests (require a real ARK_API_KEY) ==========
    # Uncomment and set ARK_API_KEY in the environment to exercise the
    # live Volcengine Ark API.

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

    #     async def _run():
    #         result = []
    #         async for chunk in await self.llm.acall(messages=messages, streaming=True):
    #             result.append(chunk.text)
    #         return result

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
