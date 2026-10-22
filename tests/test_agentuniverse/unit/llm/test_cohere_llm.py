#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Cohere LLM component.

These tests exercise :class:`CohereLLM` fully offline: the network-bound
OpenAI-style client is replaced with fakes/mocks so that the sync call, the
async call, both streaming flavours, the component-configer initialisation,
the environment-variable fallback, the YAML ``${VAR}`` placeholder guard and
the per-model context-length table can all be verified in CI without a live
Cohere API key.
"""

import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, Mock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.cohere_llm import (
    COHERE_DEFAULT_CONTEXT_LENGTH,
    COHERE_MAX_CONTEXT_LENGTH,
    CohereLLM,
)

_COHERE_ENV_KEYS = ('COHERE_API_KEY', 'COHERE_API_BASE', 'COHERE_PROXY')


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


class TestCohereLLM(unittest.TestCase):
    """Test suite for the CohereLLM component."""

    def setUp(self) -> None:
        """Build a CohereLLM instance with dummy credentials."""
        self.llm = CohereLLM(
            model_name='command-a-03-2025',
            api_key='dummy-cohere-key',
            api_base='https://api.cohere.com/compatibility/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'command-a-03-2025')
        self.assertEqual(self.llm.api_key, 'dummy-cohere-key')
        self.assertEqual(self.llm.api_base, 'https://api.cohere.com/compatibility/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the Cohere compatibility endpoint
        must be used."""
        llm = CohereLLM(model_name='command-a-03-2025', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://api.cohere.com/compatibility/v1')

    def test_env_fallback(self) -> None:
        """api_key/api_base must fall back to the COHERE_* env variables."""
        env = {'COHERE_API_KEY': 'cohere-from-env', 'COHERE_API_BASE': 'https://env.example/v1'}
        with patch.dict(os.environ, env):
            llm = CohereLLM(model_name='command-a-03-2025')
            self.assertEqual(llm.api_key, 'cohere-from-env')
            self.assertEqual(llm.api_base, 'https://env.example/v1')

    def test_no_env_defaults(self) -> None:
        """Without env variables api_key is unset and api_base is the Cohere
        compatibility URL."""
        env = {k: v for k, v in os.environ.items() if k not in _COHERE_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            llm = CohereLLM(model_name='command-a-03-2025')
            self.assertIsNone(llm.api_key)
            self.assertEqual(llm.api_base, 'https://api.cohere.com/compatibility/v1')

    def test_initialize_by_component_configer(self) -> None:
        """The component configer must override model/credential settings."""
        configer = Configer()
        configer.value = {
            'name': 'configured_cohere_llm',
            'description': 'cohere llm configured through yaml',
            'model_name': 'command-r-plus',
            'max_tokens': 256,
            'temperature': 0.3,
            'streaming': False,
            'api_key': 'cohere-configured',
            'api_base': 'https://api.cohere.com/compatibility/v1',
            'max_context_length': 4096,
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = CohereLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.name, 'configured_cohere_llm')
        self.assertEqual(llm.model_name, 'command-r-plus')
        self.assertEqual(llm.api_key, 'cohere-configured')
        self.assertEqual(llm.api_base, 'https://api.cohere.com/compatibility/v1')
        self.assertEqual(llm.max_tokens, 256)
        self.assertEqual(llm.max_context_length(), 4096)

    def test_max_context_length_known_models(self) -> None:
        """Known models must resolve to their documented context window."""
        known = [
            ('command-a-03-2025', 256000),
            ('command-r-plus', 128000),
            ('command-r', 128000),
            ('command-r7b', 128000),
        ]
        for model_name, expected in known:
            llm = CohereLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_dated_alias(self) -> None:
        """Cohere's dated ``<model>-<month>-<year>`` releases must resolve
        to the base family entry."""
        for alias, base in [
            ('command-r-plus-08-2024', 'command-r-plus'),
            ('command-r7b-12-2024', 'command-r7b'),
            ('command-r-08-2024', 'command-r'),
        ]:
            llm = CohereLLM(model_name=alias, api_key='dummy')
            expected = COHERE_MAX_CONTEXT_LENGTH[base]
            self.assertEqual(llm.max_context_length(), expected)

    def test_max_context_length_unknown_model(self) -> None:
        """Unknown models must fall back to the default context length."""
        llm = CohereLLM(model_name='some-future-command-model', api_key='dummy')
        self.assertEqual(llm.max_context_length(), COHERE_DEFAULT_CONTEXT_LENGTH)
        # A dated suffix of an unknown family must not raise either.
        llm = CohereLLM(model_name='some-future-command-model-04-2031', api_key='dummy')
        self.assertEqual(llm.max_context_length(), COHERE_DEFAULT_CONTEXT_LENGTH)

    def test_max_context_length_explicit_override(self) -> None:
        """A YAML-injected max_context_length must win over the table.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which is what
        ``super().max_context_length()`` consults first.
        """
        llm = CohereLLM(model_name='command-a-03-2025', api_key='dummy')
        self.assertIsNone(llm._max_context_length)
        llm._max_context_length = 4096
        self.assertEqual(llm.max_context_length(), 4096)

    def test_max_context_length_table_consistency(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in COHERE_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_call_with_mocked_client(self) -> None:
        """A non-streaming sync call must return the mocked completion."""
        llm = CohereLLM(
            model_name='command-a-03-2025',
            api_key='dummy',
            client=_mock_client(_FakeChatCompletion('Hello from Command!')),
        )
        messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
        output = llm._call(messages=messages, streaming=False)
        self.assertEqual(output.text, 'Hello from Command!')
        self.assertEqual(output.raw['choices'][0]['message']['content'], 'Hello from Command!')
        create_kwargs = llm.client.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'command-a-03-2025')
        self.assertFalse(create_kwargs['stream'])
        self.assertEqual(llm.client.base_url, 'https://api.cohere.com/compatibility/v1')

    def test_call_stream_with_mocked_client(self) -> None:
        """A streaming sync call must yield the mocked chunks in order."""
        llm = CohereLLM(
            model_name='command-r-plus',
            api_key='dummy',
            client=_mock_client(_FakeStream(['Hello', ' ', 'Command', '!'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
        chunks = [chunk.text for chunk in llm._call(messages=messages, streaming=True)]
        self.assertEqual(chunks, ['Hello', ' ', 'Command', '!'])
        self.assertTrue(llm.client.chat.completions.create.call_args.kwargs['stream'])

    def test_acall_with_mocked_client(self) -> None:
        """A non-streaming async call must return the mocked completion."""
        llm = CohereLLM(
            model_name='command-a-03-2025',
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
        llm = CohereLLM(
            model_name='command-r7b',
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
        text = 'Hello Command, please introduce yourself.'
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
        "name: 'cohere_llm'\n"
        "description: 'cohere command llm'\n"
        "model_name: 'command-a-03-2025'\n"
        "api_key: '${COHERE_API_KEY}'\n"
        "api_base: '${COHERE_API_BASE}'\n"
        "proxy: '${COHERE_PROXY}'\n"
        "metadata:\n"
        "  type: 'LLM'\n"
        "  module: 'agentuniverse.llm.default.cohere_llm'\n"
        "  class: 'CohereLLM'\n"
    )

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _COHERE_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = CohereLLM(model_name='command-a-03-2025')
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertEqual(llm.api_base, 'https://api.cohere.com/compatibility/v1')
            self.assertEqual(llm.model_name, 'command-a-03-2025')
            self.assertEqual(llm.name, 'cohere_llm')

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _COHERE_ENV_KEYS}
        env['COHERE_API_KEY'] = 'cohere-test-key'
        env['COHERE_API_BASE'] = 'https://example.invalid/v1'
        env['COHERE_PROXY'] = 'http://proxy.invalid:8080'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = CohereLLM(model_name='command-a-03-2025')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'cohere-test-key')
            self.assertEqual(llm.api_base, 'https://example.invalid/v1')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')

    def test_env_base_used_when_api_key_placeholder_empty(self) -> None:
        """With an empty api_base placeholder but a set COHERE_API_BASE the
        environment override must win over the hard-coded default."""
        env = {k: v for k, v in os.environ.items()
               if k not in _COHERE_ENV_KEYS}
        env['COHERE_API_BASE'] = 'https://api.cohere.example/compatibility/v1'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = CohereLLM(model_name='command-a-03-2025')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_base, 'https://api.cohere.example/compatibility/v1')

    # ========== Integration tests (require a real COHERE_API_KEY) ==========
    # Uncomment and set COHERE_API_KEY in the environment to exercise the
    # live Cohere API.

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
