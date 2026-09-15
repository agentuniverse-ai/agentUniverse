#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for vLLM OpenAI-Style LLM implementation.

Request contract tests use the real OpenAI SDK with a mocked HTTP transport.
They require no running vLLM server, GPU, or provider credentials.
Commented examples below remain available for live-server validation.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch, sentinel

import httpx
from openai import AsyncOpenAI, OpenAI

from agentuniverse.llm.default.vllm_openai_style_llm import VLLMOpenAIStyleLLM
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestVLLMOpenAIStyleLLM(unittest.TestCase):
    """Test suite for vLLM OpenAI-Style LLM."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Initialize with mock configuration
        # In production, api_base should point to your vLLM server
        self.llm = VLLMOpenAIStyleLLM(
            model_name='meta-llama/Llama-3.1-8B-Instruct',
            api_base='http://localhost:8000/v1',
            api_key='EMPTY',  # vLLM doesn't require API key by default
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """Test LLM initialization with correct parameters."""
        self.assertEqual(self.llm.model_name, 'meta-llama/Llama-3.1-8B-Instruct')
        self.assertEqual(self.llm.api_base, 'http://localhost:8000/v1')
        self.assertEqual(self.llm.api_key, 'EMPTY')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_max_context_length(self) -> None:
        """Test max context length retrieval."""
        # Test known model
        context_length = self.llm.max_context_length()
        self.assertIsInstance(context_length, int)
        self.assertGreater(context_length, 0)
        # Llama 3.1 should have 128K context
        self.assertEqual(context_length, 131072)

        # Test unknown model falls back to default
        llm_unknown = VLLMOpenAIStyleLLM(
            model_name='unknown/model',
            api_base='http://localhost:8000/v1',
        )
        self.assertEqual(llm_unknown.max_context_length(), 4096)

    def test_vllm_specific_parameters(self) -> None:
        """Test vLLM-specific parameters are properly set."""
        llm_with_params = VLLMOpenAIStyleLLM(
            model_name='meta-llama/Llama-3.1-8B-Instruct',
            api_base='http://localhost:8000/v1',
            use_beam_search=True,
            best_of=3,
            length_penalty=1.2,
            early_stopping=True,
        )
        self.assertTrue(llm_with_params.use_beam_search)
        self.assertEqual(llm_with_params.best_of, 3)
        self.assertEqual(llm_with_params.length_penalty, 1.2)
        self.assertTrue(llm_with_params.early_stopping)

    def test_call_moves_configured_vllm_parameters_to_extra_body(self) -> None:
        """Configured vLLM extensions are not sent as OpenAI SDK keywords."""
        llm = VLLMOpenAIStyleLLM(
            model_name='meta-llama/Llama-3.1-8B-Instruct',
            use_beam_search=False,
            best_of=3,
            length_penalty=1.2,
            early_stopping=True,
        )
        messages = [{'role': 'user', 'content': 'Hello'}]

        with patch.object(OpenAIStyleLLM, '_call', return_value=sentinel.result) as parent_call:
            result = llm._call(messages)

        self.assertIs(result, sentinel.result)
        parent_call.assert_called_once_with(
            messages,
            extra_body={
                'use_beam_search': False,
                'best_of': 3,
                'length_penalty': 1.2,
                'early_stopping': True,
            },
        )

    def test_call_parameters_override_extra_body_and_instance_configuration(self) -> None:
        """Per-call vLLM parameters have the highest precedence."""
        llm = VLLMOpenAIStyleLLM(
            model_name='meta-llama/Llama-3.1-8B-Instruct',
            best_of=3,
            early_stopping=True,
        )
        messages = [{'role': 'user', 'content': 'Hello'}]
        supplied_extra_body = {'best_of': 5, 'custom_sampling_option': 0.8}

        with patch.object(OpenAIStyleLLM, '_call', return_value=sentinel.result) as parent_call:
            llm._call(
                messages,
                best_of=7,
                early_stopping=False,
                extra_body=supplied_extra_body,
            )

        parent_call.assert_called_once_with(
            messages,
            extra_body={
                'best_of': 7,
                'early_stopping': False,
                'custom_sampling_option': 0.8,
            },
        )
        self.assertEqual(supplied_extra_body, {'best_of': 5, 'custom_sampling_option': 0.8})

    def test_call_rejects_a_non_mapping_extra_body(self) -> None:
        """Invalid extension payloads fail before a client request is made."""
        with self.assertRaisesRegex(TypeError, 'extra_body must be a mapping'):
            self.llm._call(
                [{'role': 'user', 'content': 'Hello'}],
                extra_body=['not', 'a', 'mapping'],
            )

    def test_none_call_parameter_keeps_existing_value(self) -> None:
        """None does not erase either an instance or an extra-body default."""
        self.llm.best_of = 3
        self.llm.length_penalty = 1.2
        supplied_extra_body = {'best_of': 5}

        with patch.object(OpenAIStyleLLM, '_call', return_value=sentinel.result) as parent_call:
            self.llm._call(
                [],
                best_of=None,
                length_penalty=None,
                extra_body=supplied_extra_body,
            )

        parent_call.assert_called_once_with([], extra_body={'best_of': 5, 'length_penalty': 1.2})
        self.assertEqual(supplied_extra_body, {'best_of': 5})

    def test_none_extra_body_keeps_instance_configuration(self) -> None:
        """A None extra-body payload is equivalent to omitting it."""
        self.llm.best_of = 3
        with patch.object(OpenAIStyleLLM, '_call', return_value=sentinel.result) as parent_call:
            self.llm._call([], extra_body=None)
        parent_call.assert_called_once_with([], extra_body={'best_of': 3})

    def test_acall_moves_runtime_vllm_parameters_to_extra_body(self) -> None:
        """Async calls use the same request-body contract as sync calls."""
        messages = [{'role': 'user', 'content': 'Hello'}]

        async def run_test() -> None:
            with patch.object(
                OpenAIStyleLLM,
                '_acall',
                new=AsyncMock(return_value=sentinel.result),
            ) as parent_acall:
                result = await self.llm._acall(
                    messages,
                    length_penalty=0.0,
                    use_beam_search=False,
                )

            self.assertIs(result, sentinel.result)
            parent_acall.assert_awaited_once_with(
                messages,
                extra_body={
                    'length_penalty': 0.0,
                    'use_beam_search': False,
                },
            )

        asyncio.run(run_test())

    def test_get_num_tokens(self) -> None:
        """Test token counting."""
        text = "Hello, how are you today?"
        num_tokens = self.llm.get_num_tokens(text)
        self.assertIsInstance(num_tokens, int)
        self.assertGreater(num_tokens, 0)

    # ========== Integration Tests ==========
    # The following tests require a running vLLM server
    # Uncomment to run when vLLM server is available

    # def test_call(self) -> None:
    #     """Test synchronous call to vLLM server."""
    #     messages = [
    #         {
    #             "role": "user",
    #             "content": "Say 'Hello, World!' and nothing else.",
    #         }
    #     ]
    #     output = self.llm.call(messages=messages, streaming=False)
    #     print(f"\nSync response: {output.text}")
    #     self.assertIsNotNone(output.text)
    #     self.assertGreater(len(output.text), 0)

    # def test_acall(self) -> None:
    #     """Test asynchronous call to vLLM server."""
    #     messages = [
    #         {
    #             "role": "user",
    #             "content": "Say 'Hello, World!' and nothing else.",
    #         }
    #     ]
    #     output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
    #     print(f"\nAsync response: {output.text}")
    #     self.assertIsNotNone(output.text)
    #     self.assertGreater(len(output.text), 0)

    # def test_call_stream(self):
    #     """Test streaming call to vLLM server."""
    #     messages = [
    #         {
    #             "role": "user",
    #             "content": "Count from 1 to 5.",
    #         }
    #     ]
    #     print("\nStreaming response:")
    #     chunks = []
    #     for chunk in self.llm.call(messages=messages, streaming=True):
    #         print(chunk.text, end='', flush=True)
    #         chunks.append(chunk.text)
    #     print()
    #     self.assertGreater(len(chunks), 0)
    #     full_text = ''.join(chunks)
    #     self.assertGreater(len(full_text), 0)

    # def test_acall_stream(self):
    #     """Test asynchronous streaming call to vLLM server."""
    #     messages = [
    #         {
    #             "role": "user",
    #             "content": "Count from 1 to 5.",
    #         }
    #     ]
    #     asyncio.run(self._acall_stream_helper(messages=messages))

    # async def _acall_stream_helper(self, messages: list):
    #     """Helper method for async streaming test."""
    #     print("\nAsync streaming response:")
    #     chunks = []
    #     async for chunk in await self.llm.acall(messages=messages, streaming=True):
    #         print(chunk.text, end='', flush=True)
    #         chunks.append(chunk.text)
    #     print()
    #     self.assertGreater(len(chunks), 0)

    # def test_vllm_beam_search(self):
    #     """Test vLLM-specific beam search parameters."""
    #     llm_beam = VLLMOpenAIStyleLLM(
    #         model_name='meta-llama/Llama-3.1-8B-Instruct',
    #         api_base='http://localhost:8000/v1',
    #         use_beam_search=True,
    #         best_of=3,
    #         length_penalty=1.2,
    #     )
    #     messages = [
    #         {
    #             "role": "user",
    #             "content": "Write a creative sentence.",
    #         }
    #     ]
    #     output = llm_beam.call(messages=messages, streaming=False)
    #     print(f"\nBeam search response: {output.text}")
    #     self.assertIsNotNone(output.text)

    # def test_as_langchain(self):
    #     """Test LangChain integration."""
    #     from langchain.chains.conversation.base import ConversationChain
    #     langchain_llm = self.llm.as_langchain()
    #     llm_chain = ConversationChain(llm=langchain_llm)
    #     res = llm_chain.predict(input='Say hello')
    #     print(f"\nLangChain response: {res}")
    #     self.assertIsNotNone(res)


class TestVLLMRequestBody(unittest.IsolatedAsyncioTestCase):
    """Exercise the adapter, parent implementation, SDK and HTTP serialization."""

    def setUp(self) -> None:
        self.requests = []
        self.messages = [{'role': 'user', 'content': 'Hello'}]
        self.llm = VLLMOpenAIStyleLLM(
            model_name='test-model',
            api_base='http://vllm.test/v1',
            api_key='EMPTY',
            use_beam_search=False,
            best_of=3,
            length_penalty=0.0,
            ext_params={'top_k': 20, 'best_of': 5},
        )

    def _handle_request(self, request: httpx.Request) -> httpx.Response:
        self.assertEqual(request.url.path, '/v1/chat/completions')
        body = json.loads(request.content)
        self.requests.append(body)
        if body['stream']:
            chunk = {
                'id': 'test-completion',
                'object': 'chat.completion.chunk',
                'created': 0,
                'model': 'test-model',
                'choices': [{'index': 0, 'delta': {'content': 'ok'}, 'finish_reason': 'stop'}],
            }
            return httpx.Response(
                200,
                headers={'content-type': 'text/event-stream'},
                text=f'data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n',
            )
        return httpx.Response(200, json={
            'id': 'test-completion',
            'object': 'chat.completion',
            'created': 0,
            'model': 'test-model',
            'choices': [{
                'index': 0,
                'message': {'role': 'assistant', 'content': 'ok'},
                'finish_reason': 'stop',
            }],
        })

    def test_sync_sdk_serializes_extensions_and_existing_defaults(self) -> None:
        with OpenAI(
            api_key='EMPTY',
            base_url=self.llm.api_base,
            http_client=httpx.Client(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            self.llm.client = client
            output = self.llm._call(self.messages, best_of=None)

        self.assertEqual(output.text, 'ok')
        self.assertEqual(len(self.requests), 1)
        body = self.requests[0]
        self.assertEqual(body['messages'], self.messages)
        self.assertEqual(body['best_of'], 3)
        self.assertIs(body['use_beam_search'], False)
        self.assertEqual(body['length_penalty'], 0.0)
        self.assertEqual(body['top_k'], 20)
        self.assertNotIn('early_stopping', body)
        self.assertNotIn('extra_body', body)
        self.assertEqual(self.llm.ext_params, {'top_k': 20, 'best_of': 5})

    def test_sync_sdk_applies_overrides_without_mutating_configuration(self) -> None:
        supplied_extra_body = {'best_of': 7, 'top_k': 10}
        with OpenAI(
            api_key='EMPTY',
            base_url=self.llm.api_base,
            http_client=httpx.Client(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            self.llm.client = client
            self.llm._call(self.messages, best_of=9, extra_body=supplied_extra_body)

        self.assertEqual(self.requests[0]['best_of'], 9)
        self.assertEqual(self.requests[0]['top_k'], 10)
        self.assertEqual(supplied_extra_body, {'best_of': 7, 'top_k': 10})
        self.assertEqual(self.llm.best_of, 3)
        self.assertEqual(self.llm.ext_params, {'top_k': 20, 'best_of': 5})

    def test_sync_sdk_omits_unconfigured_extensions(self) -> None:
        llm = VLLMOpenAIStyleLLM(model_name='test-model', api_base=self.llm.api_base, api_key='EMPTY')
        with OpenAI(
            api_key='EMPTY',
            base_url=llm.api_base,
            http_client=httpx.Client(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            llm.client = client
            output = llm._call(self.messages)

        self.assertEqual(output.text, 'ok')
        for parameter in ('use_beam_search', 'best_of', 'length_penalty', 'early_stopping'):
            self.assertNotIn(parameter, self.requests[0])

    async def test_async_sdk_serializes_extensions_and_call_overrides(self) -> None:
        supplied_extra_body = {'best_of': 7, 'top_k': 10}
        async with AsyncOpenAI(
            api_key='EMPTY',
            base_url=self.llm.api_base,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            self.llm.async_client = client
            output = await self.llm._acall(self.messages, best_of=9, extra_body=supplied_extra_body)

        self.assertEqual(output.text, 'ok')
        self.assertEqual(len(self.requests), 1)
        body = self.requests[0]
        self.assertEqual(body['best_of'], 9)
        self.assertIs(body['use_beam_search'], False)
        self.assertEqual(body['length_penalty'], 0.0)
        self.assertEqual(body['top_k'], 10)
        self.assertNotIn('early_stopping', body)
        self.assertEqual(supplied_extra_body, {'best_of': 7, 'top_k': 10})
        self.assertEqual(self.llm.ext_params, {'top_k': 20, 'best_of': 5})

    def test_sync_streaming_sdk_preserves_extensions(self) -> None:
        with OpenAI(
            api_key='EMPTY',
            base_url=self.llm.api_base,
            http_client=httpx.Client(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            self.llm.client = client
            output = self.llm._call(self.messages, streaming=True)
            self.assertEqual(''.join(chunk.text for chunk in output), 'ok')

        self.assertIs(self.requests[0]['stream'], True)
        self.assertEqual(self.requests[0]['best_of'], 3)
        self.assertEqual(self.requests[0]['top_k'], 20)
        self.assertEqual(self.requests[0]['stream_options'], {'include_usage': True})
        self.assertEqual(self.llm.ext_params, {'top_k': 20, 'best_of': 5})

    async def test_async_streaming_sdk_preserves_extensions(self) -> None:
        async with AsyncOpenAI(
            api_key='EMPTY',
            base_url=self.llm.api_base,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(self._handle_request)),
            max_retries=0,
        ) as client:
            self.llm.async_client = client
            output = await self.llm._acall(self.messages, streaming=True)
            self.assertEqual(''.join([chunk.text async for chunk in output]), 'ok')

        self.assertIs(self.requests[0]['stream'], True)
        self.assertEqual(self.requests[0]['best_of'], 3)
        self.assertEqual(self.requests[0]['top_k'], 20)
        self.assertEqual(self.requests[0]['stream_options'], {'include_usage': True})


class TestVLLMContextLengths(unittest.TestCase):
    """Test context length retrieval for various models."""

    def test_llama_context_lengths(self):
        """Test Llama model context lengths."""
        models = [
            ('meta-llama/Llama-2-7b-chat-hf', 4096),
            ('meta-llama/Llama-3.1-8B-Instruct', 131072),
            ('meta-llama/Llama-3.1-70B-Instruct', 131072),
        ]
        for model_name, expected_length in models:
            llm = VLLMOpenAIStyleLLM(
                model_name=model_name,
                api_base='http://localhost:8000/v1',
            )
            self.assertEqual(
                llm.max_context_length(),
                expected_length,
                f"Context length mismatch for {model_name}"
            )

    def test_mistral_context_lengths(self):
        """Test Mistral model context lengths."""
        models = [
            ('mistralai/Mistral-7B-Instruct-v0.1', 8192),
            ('mistralai/Mistral-7B-Instruct-v0.2', 32768),
            ('mistralai/Mixtral-8x7B-Instruct-v0.1', 32768),
        ]
        for model_name, expected_length in models:
            llm = VLLMOpenAIStyleLLM(
                model_name=model_name,
                api_base='http://localhost:8000/v1',
            )
            self.assertEqual(
                llm.max_context_length(),
                expected_length,
                f"Context length mismatch for {model_name}"
            )

    def test_qwen_context_lengths(self):
        """Test Qwen model context lengths."""
        models = [
            ('Qwen/Qwen2-7B-Instruct', 32768),
            ('Qwen/Qwen2.5-72B-Instruct', 32768),
        ]
        for model_name, expected_length in models:
            llm = VLLMOpenAIStyleLLM(
                model_name=model_name,
                api_base='http://localhost:8000/v1',
            )
            self.assertEqual(
                llm.max_context_length(),
                expected_length,
                f"Context length mismatch for {model_name}"
            )


if __name__ == '__main__':
    unittest.main()
