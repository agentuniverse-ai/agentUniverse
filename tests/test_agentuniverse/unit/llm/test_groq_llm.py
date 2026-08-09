#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Unit tests for the Groq Cloud LLM component.

These tests exercise the parts of :class:`GroqLLM` that do not require a
live Groq API key: credential/base-url wiring, the per-model context length
table and the token estimator. The network-bound call/acall/stream tests
are kept but commented out so that the full suite can run in CI without
any external dependency.
"""

import asyncio
import unittest

from agentuniverse.llm.default.groq_llm import (
    GROQ_DEFAULT_CONTEXT_LENGTH,
    GROQ_MAX_CONTEXT_LENGTH,
    GroqLLM,
)


class TestGroqLLM(unittest.TestCase):
    """Test suite for the GroqLLM component."""

    def setUp(self) -> None:
        """Build a GroqLLM instance with dummy credentials."""
        self.llm = GroqLLM(
            model_name='llama-3.3-70b-versatile',
            api_key='dummy-groq-key',
            api_base='https://api.groq.com/openai/v1',
            max_tokens=512,
            temperature=0.7,
        )

    def test_initialization(self) -> None:
        """LLM must accept and persist the constructor parameters."""
        self.assertEqual(self.llm.model_name, 'llama-3.3-70b-versatile')
        self.assertEqual(self.llm.api_key, 'dummy-groq-key')
        self.assertEqual(self.llm.api_base, 'https://api.groq.com/openai/v1')
        self.assertEqual(self.llm.max_tokens, 512)
        self.assertEqual(self.llm.temperature, 0.7)

    def test_default_api_base(self) -> None:
        """When no api_base is provided the Groq endpoint must be used."""
        llm = GroqLLM(model_name='llama-3.3-70b-versatile', api_key='dummy')
        self.assertEqual(llm.api_base, 'https://api.groq.com/openai/v1')

    def test_max_context_length_known_models(self) -> None:
        """Known models must resolve to their documented context window."""
        known = [
            ('llama-3.3-70b-versatile', 131072),
            ('llama-3.1-8b-instant', 131072),
            ('mixtral-8x7b-32768', 32768),
            ('gemma2-9b-it', 8192),
        ]
        for model_name, expected in known:
            llm = GroqLLM(model_name=model_name, api_key='dummy')
            self.assertEqual(
                llm.max_context_length(),
                expected,
                f'Context length mismatch for {model_name}',
            )

    def test_max_context_length_unknown_model(self) -> None:
        """Unknown models must fall back to the default context length."""
        llm = GroqLLM(model_name='some-future-groq-model', api_key='dummy')
        self.assertEqual(llm.max_context_length(), GROQ_DEFAULT_CONTEXT_LENGTH)

    def test_max_context_length_table_consistency(self) -> None:
        """Every entry in the table must be a positive integer."""
        for model_name, length in GROQ_MAX_CONTEXT_LENGTH.items():
            self.assertIsInstance(length, int, f'{model_name} length not int')
            self.assertGreater(length, 0, f'{model_name} length not positive')

    def test_get_num_tokens(self) -> None:
        """The token estimator must return a sensible positive count."""
        text = 'Hello Groq, please introduce yourself.'
        num_tokens = self.llm.get_num_tokens(text)
        self.assertIsInstance(num_tokens, int)
        self.assertGreater(num_tokens, 0)
        # The estimator must be deterministic for the same input.
        self.assertEqual(num_tokens, self.llm.get_num_tokens(text))

    def test_get_num_tokens_empty_string(self) -> None:
        """An empty string must cost zero tokens."""
        self.assertEqual(self.llm.get_num_tokens(''), 0)

    # ========== Integration tests (require a real GROQ_API_KEY) ==========
    # Uncomment and set GROQ_API_KEY in the environment to exercise the
    # live Groq API.

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
