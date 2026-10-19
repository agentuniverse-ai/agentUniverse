#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the OpenRouter LLM component.

These tests exercise :class:`OpenRouterLLM` fully offline: the network-bound
OpenAI-style client is replaced with fakes/mocks so that the sync call, the
async call, both streaming flavours, the attribution-header forwarding, the
component-configer initialisation, the environment-variable fallback, the
YAML ``${VAR}`` placeholder guard and the conservative context-length
fallback can all be verified in CI without a live OpenRouter API key.
"""

import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, Mock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.openrouter_llm import (
    OPENROUTER_DEFAULT_API_BASE,
    OPENROUTER_DEFAULT_CONTEXT_LENGTH,
    OpenRouterLLM,
)

_OPENROUTER_ENV_KEYS = (
    'OPENROUTER_API_KEY',
    'OPENROUTER_API_BASE',
    'OPENROUTER_PROXY',
    'OPENROUTER_HTTP_REFERER',
    'OPENROUTER_APP_TITLE',
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


class TestOpenRouterLLM(unittest.TestCase):
    """Test suite for the OpenRouterLLM component."""

    def setUp(self) -> None:
        """Build a OpenRouterLLM instance with dummy credentials."""
        self.llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='sk-or-v1-dummy',
            api_base='https://openrouter.ai/api/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'openai/gpt-4o-mini')
        self.assertEqual(self.llm.api_key, 'sk-or-v1-dummy')
        self.assertEqual(self.llm.api_base, 'https://openrouter.ai/api/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the OpenRouter endpoint must be used."""
        llm = OpenRouterLLM(model_name='openai/gpt-4o-mini', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://openrouter.ai/api/v1')

    def test_env_fallback(self) -> None:
        """api_key/api_base must fall back to the OPENROUTER_* env variables."""
        env = {'OPENROUTER_API_KEY': 'or-from-env', 'OPENROUTER_API_BASE': 'https://env.example/v1'}
        with patch.dict(os.environ, env):
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            self.assertEqual(llm.api_key, 'or-from-env')
            self.assertEqual(llm.api_base, 'https://env.example/v1')

    def test_no_env_defaults(self) -> None:
        """Without env variables api_key is unset and api_base is the OpenRouter URL."""
        env = {k: v for k, v in os.environ.items() if k not in _OPENROUTER_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            self.assertIsNone(llm.api_key)
            self.assertEqual(llm.api_base, OPENROUTER_DEFAULT_API_BASE)
            self.assertIsNone(llm.http_referer)
            self.assertIsNone(llm.app_title)

    def test_initialize_by_component_configer(self) -> None:
        """The component configer must override model/credential settings."""
        configer = Configer()
        configer.value = {
            'name': 'configured_openrouter_llm',
            'description': 'openrouter llm configured through yaml',
            'model_name': 'anthropic/claude-3.5-sonnet',
            'max_tokens': 256,
            'temperature': 0.3,
            'streaming': False,
            'api_key': 'or-configured',
            'api_base': 'https://openrouter.ai/api/v1',
            'http_referer': 'https://my-app.example.com',
            'app_title': 'My App',
            'max_context_length': 200000,
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = OpenRouterLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.name, 'configured_openrouter_llm')
        self.assertEqual(llm.model_name, 'anthropic/claude-3.5-sonnet')
        self.assertEqual(llm.api_key, 'or-configured')
        self.assertEqual(llm.api_base, 'https://openrouter.ai/api/v1')
        self.assertEqual(llm.max_tokens, 256)
        self.assertEqual(llm.http_referer, 'https://my-app.example.com')
        self.assertEqual(llm.app_title, 'My App')
        self.assertEqual(llm.max_context_length(), 200000)

    def test_max_context_length_conservative_default(self) -> None:
        """Without configuration the conservative 8192 fallback applies."""
        self.assertIsNone(self.llm._max_context_length)
        self.assertEqual(self.llm.max_context_length(), OPENROUTER_DEFAULT_CONTEXT_LENGTH)
        self.assertEqual(OPENROUTER_DEFAULT_CONTEXT_LENGTH, 8192)

    def test_max_context_length_explicit_override(self) -> None:
        """A YAML-injected max_context_length must win over the fallback.

        ``OpenAIStyleLLM`` stores the value configured through the component
        YAML in the private ``_max_context_length`` attribute, which is what
        ``super().max_context_length()`` consults first.
        """
        llm = OpenRouterLLM(model_name='openai/gpt-4o-mini', api_key='dummy')
        self.assertIsNone(llm._max_context_length)
        llm._max_context_length = 1000000
        self.assertEqual(llm.max_context_length(), 1000000)

    def test_call_with_mocked_client(self) -> None:
        """A non-streaming sync call must return the mocked completion."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            client=_mock_client(_FakeChatCompletion('Hello from OpenRouter!')),
        )
        messages = [{'role': 'user', 'content': 'Say hello in one word.'}]
        output = llm._call(messages=messages, streaming=False)
        self.assertEqual(output.text, 'Hello from OpenRouter!')
        self.assertEqual(output.raw['choices'][0]['message']['content'], 'Hello from OpenRouter!')
        create_kwargs = llm.client.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'openai/gpt-4o-mini')
        self.assertFalse(create_kwargs['stream'])
        self.assertEqual(llm.client.base_url, 'https://openrouter.ai/api/v1')

    def test_call_stream_with_mocked_client(self) -> None:
        """A streaming sync call must yield the mocked chunks in order."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            client=_mock_client(_FakeStream(['Hello', ' ', 'router', '!'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]
        chunks = [chunk.text for chunk in llm._call(messages=messages, streaming=True)]
        self.assertEqual(chunks, ['Hello', ' ', 'router', '!'])
        self.assertTrue(llm.client.chat.completions.create.call_args.kwargs['stream'])

    def test_acall_with_mocked_client(self) -> None:
        """A non-streaming async call must return the mocked completion."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
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
        llm = OpenRouterLLM(
            model_name='anthropic/claude-3.5-sonnet',
            api_key='dummy',
            async_client=_mock_async_client(_FakeAsyncStream(['Hi', ' ', 'there'])),
        )
        messages = [{'role': 'user', 'content': 'Count from 1 to 5.'}]

        async def _run():
            stream = await llm._acall(messages=messages, streaming=True)
            return [chunk.text async for chunk in stream]

        chunks = asyncio.run(_run())
        self.assertEqual(chunks, ['Hi', ' ', 'there'])

    # ========== Attribution headers (HTTP-Referer / X-Title) ==========

    def test_attribution_headers_forwarded_when_set(self) -> None:
        """Configured attribution fields must reach the SDK call."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            http_referer='https://my-app.example.com',
            app_title='My App',
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('HTTP-Referer'), 'https://my-app.example.com')
        self.assertEqual(extra_headers.get('X-Title'), 'My App')

    def test_attribution_headers_absent_when_not_set(self) -> None:
        """Without attribution fields no HTTP-Referer/X-Title must be sent."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs.get('extra_headers') or {}
        self.assertNotIn('HTTP-Referer', extra_headers)
        self.assertNotIn('X-Title', extra_headers)

    def test_partial_attribution_headers(self) -> None:
        """Only the configured attribution header is sent."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            app_title='My App',
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('X-Title'), 'My App')
        self.assertNotIn('HTTP-Referer', extra_headers)

    def test_attribution_headers_forwarded_async(self) -> None:
        """Configured attribution fields must reach the async SDK call too."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            http_referer='https://my-app.example.com',
            async_client=_mock_async_client(_FakeChatCompletion('ok')),
        )

        async def _run():
            return await llm._acall(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)

        asyncio.run(_run())
        extra_headers = llm.async_client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('HTTP-Referer'), 'https://my-app.example.com')

    def test_attribution_headers_forwarded_stream(self) -> None:
        """Configured attribution fields must also be sent when streaming."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            http_referer='https://my-app.example.com',
            app_title='My App',
            client=_mock_client(_FakeStream(['ok'])),
        )
        list(llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=True))
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('HTTP-Referer'), 'https://my-app.example.com')
        self.assertEqual(extra_headers.get('X-Title'), 'My App')

    def test_explicit_extra_headers_kwarg_wins(self) -> None:
        """An explicit extra_headers kwarg must suppress the auto headers."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            http_referer='https://my-app.example.com',
            app_title='My App',
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        explicit = {'X-Custom': 'custom-value'}
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False, extra_headers=explicit)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers, {'X-Custom': 'custom-value'})
        self.assertNotIn('HTTP-Referer', extra_headers)

    def test_ext_headers_take_precedence_over_fields(self) -> None:
        """YAML extra_headers entries win over the dedicated fields."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            http_referer='https://my-app.example.com',
            ext_headers={'HTTP-Referer': 'https://override.example.com', 'X-Custom': 'keep-me'},
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('HTTP-Referer'), 'https://override.example.com')
        self.assertEqual(extra_headers.get('X-Custom'), 'keep-me')

    def test_app_title_ext_headers_merge(self) -> None:
        """A dedicated field must still be added next to ext_headers."""
        llm = OpenRouterLLM(
            model_name='openai/gpt-4o-mini',
            api_key='dummy',
            app_title='My App',
            ext_headers={'X-Custom': 'keep-me'},
            client=_mock_client(_FakeChatCompletion('ok')),
        )
        llm._call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)
        extra_headers = llm.client.chat.completions.create.call_args.kwargs['extra_headers']
        self.assertEqual(extra_headers.get('X-Title'), 'My App')
        self.assertEqual(extra_headers.get('X-Custom'), 'keep-me')

    def test_get_num_tokens(self) -> None:
        """The token estimator must return a sensible positive count."""
        text = 'Hello OpenRouter, please introduce yourself.'
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
        "name: 'openrouter_llm'\n"
        "description: 'openrouter llm'\n"
        "model_name: 'openai/gpt-4o-mini'\n"
        "api_key: '${OPENROUTER_API_KEY}'\n"
        "api_base: '${OPENROUTER_API_BASE}'\n"
        "proxy: '${OPENROUTER_PROXY}'\n"
        "http_referer: '${OPENROUTER_HTTP_REFERER}'\n"
        "app_title: '${OPENROUTER_APP_TITLE}'\n"
        "metadata:\n"
        "  type: 'LLM'\n"
        "  module: 'agentuniverse.llm.default.openrouter_llm'\n"
        "  class: 'OpenRouterLLM'\n"
    )

    def test_unset_env_placeholders_fall_back_to_defaults(self) -> None:
        """`${VAR}` resolves to '' when the variable is unset; the component
        must treat that like an omitted key instead of sending empty strings
        upstream (empty api_key fails late with an opaque 401, empty api_base
        would silently target https://api.openai.com/v1)."""
        env = {k: v for k, v in os.environ.items()
               if k not in _OPENROUTER_ENV_KEYS}
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            llm.initialize_by_component_configer(configer)
            self.assertIsNone(llm.api_key)
            self.assertIsNone(llm.proxy)
            self.assertIsNone(llm.http_referer)
            self.assertIsNone(llm.app_title)
            self.assertEqual(llm.api_base, 'https://openrouter.ai/api/v1')
            self.assertEqual(llm.model_name, 'openai/gpt-4o-mini')
            self.assertEqual(llm.name, 'openrouter_llm')

    def test_set_env_placeholder_values_survive_initialization(self) -> None:
        """Real placeholder values must not be clobbered by the guard."""
        env = {k: v for k, v in os.environ.items()
               if k not in _OPENROUTER_ENV_KEYS}
        env['OPENROUTER_API_KEY'] = 'sk-or-v1-test'
        env['OPENROUTER_API_BASE'] = 'https://example.invalid/v1'
        env['OPENROUTER_PROXY'] = 'http://proxy.invalid:8080'
        env['OPENROUTER_HTTP_REFERER'] = 'https://env.example.com'
        env['OPENROUTER_APP_TITLE'] = 'Env App'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_key, 'sk-or-v1-test')
            self.assertEqual(llm.api_base, 'https://example.invalid/v1')
            self.assertEqual(llm.proxy, 'http://proxy.invalid:8080')
            self.assertEqual(llm.http_referer, 'https://env.example.com')
            self.assertEqual(llm.app_title, 'Env App')

    def test_env_base_used_when_api_key_placeholder_empty(self) -> None:
        """With an empty api_base placeholder but a set OPENROUTER_API_BASE the
        environment override must win over the hard-coded default."""
        env = {k: v for k, v in os.environ.items()
               if k not in _OPENROUTER_ENV_KEYS}
        env['OPENROUTER_API_BASE'] = 'https://openrouter.ai/api/v2'
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(self._EXAMPLE_YAML)
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.api_base, 'https://openrouter.ai/api/v2')

    def test_direct_yaml_values_beat_env_defaults(self) -> None:
        """Attribution fields written directly into the YAML must override
        environment-derived defaults."""
        env = {k: v for k, v in os.environ.items()
               if k not in _OPENROUTER_ENV_KEYS}
        env['OPENROUTER_APP_TITLE'] = 'Env App'
        yaml_text = (
            "name: 'openrouter_llm'\n"
            "description: 'openrouter llm'\n"
            "model_name: 'openai/gpt-4o-mini'\n"
            "http_referer: 'https://yaml.example.com'\n"
            "app_title: 'Yaml App'\n"
            "metadata:\n"
            "  type: 'LLM'\n"
            "  module: 'agentuniverse.llm.default.openrouter_llm'\n"
            "  class: 'OpenRouterLLM'\n"
        )
        with patch.dict(os.environ, env, clear=True):
            configer = _build_llm_configer_from_yaml(yaml_text)
            llm = OpenRouterLLM(model_name='openai/gpt-4o-mini')
            llm.initialize_by_component_configer(configer)
            self.assertEqual(llm.http_referer, 'https://yaml.example.com')
            self.assertEqual(llm.app_title, 'Yaml App')

    # ========== Integration tests (require a real OPENROUTER_API_KEY) ==========
    # Uncomment and set OPENROUTER_API_KEY in the environment to exercise the
    # live OpenRouter API.

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
