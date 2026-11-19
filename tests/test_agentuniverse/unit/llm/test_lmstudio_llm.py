#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the LM Studio LLM component.

These tests exercise :class:`LMStudioLLM` fully offline: the network-bound
OpenAI-style client is replaced with fakes/mocks so that the sync call, the
async call, both streaming flavours, the component-configer initialisation,
the environment-variable fallback, the YAML ``${VAR}`` placeholder guard and
the context-length fallback / explicit override can all be verified in CI
without a running LM Studio desktop app.
"""

import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, Mock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.lmstudio_llm import (
    LMSTUDIO_DEFAULT_API_BASE,
    LMSTUDIO_DEFAULT_CONTEXT_LENGTH,
    LMSTUDIO_PLACEHOLDER_API_KEY,
    LMStudioLLM,
)

_LMSTUDIO_ENV_KEYS = ('LMSTUDIO_API_KEY', 'LMSTUDIO_API_BASE', 'LMSTUDIO_PROXY')


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


class TestLMStudioLLM(unittest.TestCase):
    """Test suite for the LMStudioLLM component."""

    def setUp(self) -> None:
        """Build a LMStudioLLM instance pointing at the local server."""
        self.llm = LMStudioLLM(
            model_name='qwen2.5-7b-instruct',
            api_key='lm-studio',
            api_base='http://localhost:1234/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'qwen2.5-7b-instruct')
        self.assertEqual(self.llm.api_key, 'lm-studio')
        self.assertEqual(self.llm.api_base, 'http://localhost:1234/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base_and_key(self) -> None:
        """Without any configuration the local LM Studio endpoint and the
        harmless placeholder key must be used (LM Studio needs no key)."""
        llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
        self.assertEqual(llm.api_base, 'http://localhost:1234/v1')
        self.assertEqual(llm.api_key, LMSTUDIO_PLACEHOLDER_API_KEY)

    def test_env_fallback(self) -> None:
        """api_key/api_base must fall back to the LMSTUDIO_* env variables."""
        env = {'LMSTUDIO_API_KEY': 'gateway-token-from-env',
               'LMSTUDIO_API_BASE': 'http://env.example:1235/v1'}
        with patch.dict(os.environ, env):
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            self.assertEqual(llm.api_key, 'gateway-token-from-env')
            self.assertEqual(llm.api_base, 'http://env.example:1235/v1')

    def test_no_env_defaults(self) -> None:
        """Without env variables api_key is the placeholder and api_base is
        the local LM Studio URL."""
        env = {k: v for k, v in os.environ.items() if k not in _LMSTUDIO_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            self.assertEqual(llm.api_key, LMSTUDIO_PLACEHOLDER_API_KEY)
            self.assertEqual(llm.api_base, LMSTUDIO_DEFAULT_API_BASE)

    def test_initialize_by_component_configer(self) -> None:
        """The component configer must override model/credential settings."""
        configer = Configer()
        configer.value = {
            'name': 'configured_lmstudio_llm',
            'description': 'lm studio llm configured through yaml',
            'model_name': 'llama-3.1-8b-instruct',
            'max_tokens': 256,
            'temperature': 0.3,
            'streaming': False,
            'api_key': 'lm-studio',
            'api_base': 'http://localhost:1234/v1',
            'max_context_length': 131072,
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = LMStudioLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.name, 'configured_lmstudio_llm')
        self.assertEqual(llm.model_name, 'llama-3.1-8b-instruct')
        self.assertEqual(llm.api_key, 'lm-studio')
        self.assertEqual(llm.api_base, 'http://localhost:1234/v1')
        self.assertEqual(llm.max_tokens, 256)
        self.assertEqual(llm.max_context_length(), 131072)

    def test_max_context_length_fallback(self) -> None:
        """Arbitrary local model names must fall back to the conservative
        8192-token default when nothing is configured."""
        for model_name in ('qwen2.5-7b-instruct', 'some-private-gguf-finetune', 'mistral-7b'):
            llm = LMStudioLLM(model_name=model_name)
            self.assertEqual(
                llm.max_context_length(),
                LMSTUDIO_DEFAULT_CONTEXT_LENGTH,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_explicit_override(self) -> None:
        """A YAML-injected max_context_length must win over the fallback.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which is what
        ``LMStudioLLM.max_context_length`` consults first.
        """
        llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
        self.assertIsNone(llm._max_context_length)
        self.assertEqual(llm.max_context_length(), LMSTUDIO_DEFAULT_CONTEXT_LENGTH)
        llm._max_context_length = 32768
        self.assertEqual(llm.max_context_length(), 32768)

    def test_max_context_length_default_is_safe(self) -> None:
        """The built-in fallback must be a positive integer."""
        self.assertIsInstance(LMSTUDIO_DEFAULT_CONTEXT_LENGTH, int)
        self.assertGreater(LMSTUDIO_DEFAULT_CONTEXT_LENGTH, 0)

    def test_call_with_mocked_client(self) -> None:
        """A non-streaming sync call must return the mocked completion."""
        llm = LMStudioLLM(
            model_name='qwen2.5-7b-instruct',
            client=_mock_client(_FakeChatCompletion('Hello from LM Studio!')),
        )
        messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
        output = llm._call(messages=messages, streaming=False)
        self.assertEqual(output.text, 'Hello from LM Studio!')
        self.assertEqual(output.raw['choices'][0]['message']['content'], 'Hello from LM Studio!')
        create_kwargs = llm.client.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'qwen2.5-7b-instruct')
        self.assertFalse(create_kwargs['stream'])
        self.assertEqual(llm.client.base_url, 'http://localhost:1234/v1')

    def test_call_stream_with_mocked_client(self) -> None:
        """A streaming sync call must yield the mocked chunks in order."""
        llm = LMStudioLLM(
            model_name='mistral-7b',
            client=_mock_client(_FakeStream(['Hello', ' ', 'local', '!'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
        chunks = [chunk.text for chunk in llm._call(messages=messages, streaming=True)]
        self.assertEqual(chunks, ['Hello', ' ', 'local', '!'])
        self.assertTrue(llm.client.chat.completions.create.call_args.kwargs['stream'])

    def test_acall_with_mocked_client(self) -> None:
        """A non-streaming async call must return the mocked completion."""
        llm = LMStudioLLM(
            model_name='qwen2.5-7b-instruct',
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
        llm = LMStudioLLM(
            model_name='llama-3.1-8b-instruct',
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
        text = 'Hello local model, please introduce yourself.'
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
        "name: 'lmstudio_llm'\n"
        "description: 'lm studio local llm'\n"
        "model_name: 'qwen2.5-7b-instruct'\n"
        "max_context_length: 32768\n"
        "api_key: '${LMSTUDIO_API_KEY}'\n"
        "api_base: '${LMSTUDIO_API_BASE}'\n"
        "proxy: '${LMSTUDIO_PROXY}'\n"
        "metadata:\n"
        "  type: 'LLM'\n"
        "  module: 'agentuniverse.llm.default.lmstudio_llm'\n"
        "  class: 'LMStudioLLM'\n"
    )

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (an empty api_base would silently target
        https://api.openai.com/v1, an empty api_key is silently sent)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _LMSTUDIO_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, LMSTUDIO_PLACEHOLDER_API_KEY)
            self.assertIsNone(llm.proxy)
            self.assertEqual(llm.api_base, LMSTUDIO_DEFAULT_API_BASE)
            self.assertEqual(llm.model_name, 'qwen2.5-7b-instruct')
            self.assertEqual(llm.name, 'lmstudio_llm')
            self.assertEqual(llm.max_context_length(), 32768)

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _LMSTUDIO_ENV_KEYS}
        env['LMSTUDIO_API_KEY'] = 'gateway-token'
        env['LMSTUDIO_API_BASE'] = 'http://127.0.0.1:1235/v1'
        env['LMSTUDIO_PROXY'] = 'http://proxy.invalid:8080'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'gateway-token')
            self.assertEqual(llm.api_base, 'http://127.0.0.1:1235/v1')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')

    def test_env_base_used_when_api_base_placeholder_empty(self) -> None:
        """With an empty api_base placeholder but a set LMSTUDIO_API_BASE
        the environment override must win over the hard-coded default."""
        env = {k: v for k, v in os.environ.items()
               if k not in _LMSTUDIO_ENV_KEYS}
        env['LMSTUDIO_API_BASE'] = 'http://192.168.1.10:1234/v1'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_base, 'http://192.168.1.10:1234/v1')

    def test_unset_env_key_placeholder_falls_back_to_lmstudio(self) -> None:
        """An empty api_key placeholder must fall back to the harmless
        'lm-studio' constant (not None) so the OpenAI client can still be
        built — the local LM Studio server accepts any bearer token."""
        env = {k: v for k, v in os.environ.items()
               if k not in _LMSTUDIO_ENV_KEYS}
        env['LMSTUDIO_API_BASE'] = 'http://localhost:1234/v1'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = LMStudioLLM(model_name='qwen2.5-7b-instruct')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, LMSTUDIO_PLACEHOLDER_API_KEY)

    # ========== Integration tests (require a running LM Studio app) ==========
    # Uncomment and start LM Studio's local server (default port 1234) with a
    # downloaded model to exercise the live local API.

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
