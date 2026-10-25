#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Azure OpenAI LLM implementation.

All tests run offline against mocked clients; no Azure resource is required.
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.config.configer import Configer
from agentuniverse.llm.default.azure_openai_llm import AzureOpenAIStyleLLM
from agentuniverse.llm.llm_output import LLMOutput

AZURE_ENDPOINT = 'https://demo-resource.openai.azure.com/'
API_VERSION = '2024-08-01-preview'


def _chat_completion(text='hello from azure'):
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


def _azure_llm(**overrides) -> AzureOpenAIStyleLLM:
    params = dict(
        model_name='gpt-4o',
        api_base=AZURE_ENDPOINT,
        api_key='test-key',
        api_version=API_VERSION,
    )
    params.update(overrides)
    return AzureOpenAIStyleLLM(**params)


class TestAzureOpenAIStyleLLM(unittest.TestCase):
    """Test suite for the Azure OpenAI LLM."""

    def setUp(self) -> None:
        self.llm = _azure_llm()

    def test_initialization(self) -> None:
        """Test LLM initialization with correct parameters."""
        self.assertEqual(self.llm.model_name, 'gpt-4o')
        self.assertEqual(self.llm.api_base, AZURE_ENDPOINT)
        self.assertEqual(self.llm.api_key, 'test-key')
        self.assertEqual(self.llm.api_version, API_VERSION)

    def test_deployment_name_fallback(self) -> None:
        """The deployment name falls back to model_name when not configured."""
        self.assertEqual(self.llm.deployment_name(), 'gpt-4o')
        llm_with_deployment = _azure_llm(azure_deployment='my-gpt-4o-deployment')
        self.assertEqual(llm_with_deployment.deployment_name(), 'my-gpt-4o-deployment')

    def test_new_client_uses_azure_client(self) -> None:
        """The sync client is an AzureOpenAI instance bound to the endpoint."""
        with patch('agentuniverse.llm.default.azure_openai_llm.AzureOpenAI') as azure_cls:
            client = self.llm._new_client()
            azure_cls.assert_called_once()
            kwargs = azure_cls.call_args.kwargs
            self.assertEqual(kwargs['azure_endpoint'], AZURE_ENDPOINT)
            self.assertEqual(kwargs['azure_deployment'], 'gpt-4o')
            self.assertEqual(kwargs['api_version'], API_VERSION)
        self.assertIs(client, azure_cls.return_value)

    def test_new_async_client_uses_azure_client(self) -> None:
        """The async client is an AsyncAzureOpenAI instance."""
        with patch('agentuniverse.llm.default.azure_openai_llm.AsyncAzureOpenAI') as azure_cls:
            async_client = self.llm._new_async_client()
            kwargs = azure_cls.call_args.kwargs
            self.assertEqual(kwargs['azure_endpoint'], AZURE_ENDPOINT)
            self.assertEqual(kwargs['azure_deployment'], 'gpt-4o')
        self.assertIs(async_client, azure_cls.return_value)

    def test_call(self) -> None:
        """A non-streaming call returns an LLMOutput built from the response."""
        completion = _chat_completion()
        with patch('agentuniverse.llm.default.azure_openai_llm.AzureOpenAI') as azure_cls:
            azure_cls.return_value.chat.completions.create.return_value = completion
            result = self.llm._call([{'role': 'user', 'content': 'hi'}])
        create_kwargs = azure_cls.return_value.chat.completions.create.call_args.kwargs
        # the request model must be the deployment name
        self.assertEqual(create_kwargs['model'], 'gpt-4o')
        self.assertIsInstance(result, LLMOutput)
        self.assertEqual(result.text, 'hello from azure')

    def test_call_does_not_mutate_client_base_url(self) -> None:
        """The azure client base_url must stay untouched by _call."""
        with patch('agentuniverse.llm.default.azure_openai_llm.AzureOpenAI') as azure_cls:
            client = azure_cls.return_value
            client.chat.completions.create.return_value = _chat_completion()
            base_url_before = client.base_url
            self.llm._call([{'role': 'user', 'content': 'hi'}])
            self.assertEqual(client.base_url, base_url_before)

    def test_call_stream(self) -> None:
        """A streaming call yields one LLMOutput per chunk."""
        chunks = [_chat_completion('par'), _chat_completion('tial')]
        with patch('agentuniverse.llm.default.azure_openai_llm.AzureOpenAI') as azure_cls:
            azure_cls.return_value.chat.completions.create.return_value = iter(chunks)
            result = self.llm._call([{'role': 'user', 'content': 'hi'}], streaming=True)
        self.assertEqual([output.text for output in result], ['par', 'tial'])

    def test_acall(self) -> None:
        """A non-streaming async call returns an LLMOutput."""
        with patch('agentuniverse.llm.default.azure_openai_llm.AsyncAzureOpenAI') as azure_cls:
            async def _create(**kwargs):
                return _chat_completion('async hello')
            azure_cls.return_value.chat.completions.create = _create
            result = asyncio.run(self.llm._acall([{'role': 'user', 'content': 'hi'}]))
        self.assertIsInstance(result, LLMOutput)
        self.assertEqual(result.text, 'async hello')

    def test_acall_stream(self) -> None:
        """A streaming async call yields one LLMOutput per chunk."""

        async def _run():
            stream = await self.llm._acall([{'role': 'user', 'content': 'hi'}], streaming=True)
            return [output.text async for output in stream]

        with patch('agentuniverse.llm.default.azure_openai_llm.AsyncAzureOpenAI') as azure_cls:
            azure_cls.return_value.chat.completions.create = MagicMock(
                return_value=_AsyncStream([_chat_completion('par'), _chat_completion('tial')]))
            texts = asyncio.run(_run())
        self.assertEqual(texts, ['par', 'tial'])

    def test_max_context_length(self) -> None:
        """Context length is resolved from the deployment table with a fallback."""
        self.assertEqual(self.llm.max_context_length(), 128000)
        self.assertEqual(_azure_llm(model_name='gpt-4').max_context_length(), 8192)
        self.assertEqual(_azure_llm(model_name='unknown-deploy').max_context_length(), 8192)
        configured = _azure_llm()
        configured._max_context_length = 999999
        self.assertEqual(configured.max_context_length(), 999999)

    def test_initialize_by_component_configer(self) -> None:
        """Azure attributes are read from the component configuration."""
        configer = Configer()
        configer.value = {
            'name': 'configured_azure_llm',
            'model_name': 'gpt-4o-mini',
            'api_base': AZURE_ENDPOINT,
            'api_key': 'configured-key',
            'api_version': '2024-10-21',
            'azure_deployment': 'deployed-mini',
        }
        llm_configer = LLMConfiger().load_by_configer(configer)
        llm = AzureOpenAIStyleLLM()
        llm.initialize_by_component_configer(llm_configer)
        self.assertEqual(llm.api_version, '2024-10-21')
        self.assertEqual(llm.azure_deployment, 'deployed-mini')
        self.assertEqual(llm.deployment_name(), 'deployed-mini')
        self.assertEqual(llm.api_key, 'configured-key')

    def test_set_by_agent_model(self) -> None:
        """Azure attributes are forwarded by set_by_agent_model."""
        copied = self.llm.set_by_agent_model(
            api_version='2025-01-01',
            azure_deployment='agent-deployment',
        )
        self.assertEqual(copied.api_version, '2025-01-01')
        self.assertEqual(copied.azure_deployment, 'agent-deployment')
        # the original instance stays untouched
        self.assertIsNone(self.llm.azure_deployment)


if __name__ == '__main__':
    unittest.main()
