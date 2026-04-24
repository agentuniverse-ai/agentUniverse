#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for vLLM OpenAI-Style LLM implementation.

These tests verify the functionality of the vLLM LLM integration.
Note: Most tests are commented out by default since they require a running vLLM server.
To run tests, ensure you have a vLLM server running locally or update the api_base.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch

from agentuniverse.llm.default.vllm_openai_style_llm import VLLMOpenAIStyleLLM


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
