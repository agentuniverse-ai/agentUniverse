#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Hugging Face Hub LLM implementation.

All tests run offline against mocked clients; no Hugging Face token or
network access is required.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.huggingface_hub_llm import HUGGINGFACE_ROUTER_API_BASE, HuggingFaceHubLLM
from agentuniverse.llm.llm_output import LLMOutput


def _chat_completion(text='hello from huggingface'):
    """Build an object shaped like an openai chat completion or stream chunk."""
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = text
    completion.model_dump.return_value = {'choices': [{'message': {'content': text}}]}
    completion.dict.return_value = {'choices': [{'delta': {'content': text}}]}
    return completion


class _AsyncStream:
    """Awaitable that resolves to an async iterator of chunks."""

    def __init__(self, chunks):
        self._chunks = chunks

    def __await__(self):
        async def _coro():
            return self
        return _coro().__await__()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._chunks:
            raise StopAsyncIteration
        return self._chunks.pop(0)


def _hf_llm(**overrides) -> HuggingFaceHubLLM:
    params = dict(
        model_name='meta-llama/Llama-3.1-8B-Instruct',
        api_key='hf-test-token',
    )
    params.update(overrides)
    return HuggingFaceHubLLM(**params)


class TestHuggingFaceHubLLM(unittest.TestCase):
    """Test suite for the Hugging Face Hub LLM."""

    def setUp(self) -> None:
        self.llm = _hf_llm()

    def test_initialization_defaults(self) -> None:
        """The endpoint defaults to the Inference Providers router."""
        self.assertEqual(self.llm.api_base, HUGGINGFACE_ROUTER_API_BASE)
        self.assertEqual(self.llm.model_name, 'meta-llama/Llama-3.1-8B-Instruct')
        self.assertEqual(self.llm.api_key, 'hf-test-token')

    def test_request_model_name(self) -> None:
        """A provider routing hint is appended to the model name."""
        self.assertEqual(self.llm.request_model_name(), 'meta-llama/Llama-3.1-8B-Instruct')
        routed = _hf_llm(provider='together')
        self.assertEqual(routed.request_model_name(), 'meta-llama/Llama-3.1-8B-Instruct:together')
        explicit = _hf_llm(model_name='meta-llama/Llama-3.1-8B-Instruct:sambanova')
        self.assertEqual(explicit.request_model_name(), 'meta-llama/Llama-3.1-8B-Instruct:sambanova')

    def test_call(self) -> None:
        """A non-streaming call returns an LLMOutput built from the response."""
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = _chat_completion()
            result = self.llm._call([{'role': 'user', 'content': 'hi'}])
        client_kwargs = openai_cls.call_args.kwargs
        self.assertEqual(client_kwargs['api_key'], 'hf-test-token')
        self.assertEqual(client_kwargs['base_url'], HUGGINGFACE_ROUTER_API_BASE)
        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'meta-llama/Llama-3.1-8B-Instruct')
        self.assertIsInstance(result, LLMOutput)
        self.assertEqual(result.text, 'hello from huggingface')

    def test_call_with_provider(self) -> None:
        """The routed model name is sent when a provider is configured."""
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = _chat_completion()
            _hf_llm(provider='fireworks')._call([{'role': 'user', 'content': 'hi'}])
        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'meta-llama/Llama-3.1-8B-Instruct:fireworks')

    def test_call_stream(self) -> None:
        """A streaming call yields one LLMOutput per chunk."""
        chunks = [_chat_completion('par'), _chat_completion('tial')]
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = iter(chunks)
            result = self.llm._call([{'role': 'user', 'content': 'hi'}], streaming=True)
        self.assertEqual([output.text for output in result], ['par', 'tial'])

    def test_acall(self) -> None:
        """A non-streaming async call returns an LLMOutput."""
        with patch('agentuniverse.llm.openai_style_llm.AsyncOpenAI') as openai_cls:
            async def _create(**kwargs):
                return _chat_completion('async hello')
            openai_cls.return_value.chat.completions.create = _create
            result = asyncio.run(self.llm._acall([{'role': 'user', 'content': 'hi'}]))
        self.assertIsInstance(result, LLMOutput)
        self.assertEqual(result.text, 'async hello')

    def test_acall_stream(self) -> None:
        """A streaming async call yields one LLMOutput per chunk."""

        async def _run():
            stream = await self.llm._acall([{'role': 'user', 'content': 'hi'}], streaming=True)
            return [output.text async for output in stream]

        with patch('agentuniverse.llm.openai_style_llm.AsyncOpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create = MagicMock(
                return_value=_AsyncStream([_chat_completion('par'), _chat_completion('tial')]))
            texts = asyncio.run(_run())
        self.assertEqual(texts, ['par', 'tial'])

    def test_max_context_length(self) -> None:
        """Context length is resolved from the model table with a fallback."""
        self.assertEqual(self.llm.max_context_length(), 131072)
        self.assertEqual(_hf_llm(model_name='Qwen/Qwen2.5-7B-Instruct').max_context_length(), 32768)
        self.assertEqual(_hf_llm(model_name='unknown/model').max_context_length(), 8192)
        configured = _hf_llm()
        configured._max_context_length = 999999
        self.assertEqual(configured.max_context_length(), 999999)

    def test_initialize_by_component_configer(self) -> None:
        """The provider attribute is read from the component configuration."""
        configer = Configer()
        configer.value = {
            'name': 'configured_hf_llm',
            'model_name': 'Qwen/Qwen2.5-72B-Instruct',
            'api_key': 'configured-token',
            'provider': 'cerebras',
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = HuggingFaceHubLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.provider, 'cerebras')
        self.assertEqual(llm.request_model_name(), 'Qwen/Qwen2.5-72B-Instruct:cerebras')
        self.assertEqual(llm.api_key, 'configured-token')

    def test_set_by_agent_model(self) -> None:
        """The provider attribute is forwarded by set_by_agent_model."""
        copied = self.llm.set_by_agent_model(provider='together')
        self.assertEqual(copied.provider, 'together')
        # the original instance stays untouched
        self.assertIsNone(self.llm.provider)


if __name__ == '__main__':
    unittest.main()
