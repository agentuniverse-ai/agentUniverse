# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/12/6
# @Author  : sien75
# @Email   : shaoning.shao@antgroup.com
# @FileName: test_openrouter_openai_style_llm.py
import unittest
import asyncio
import os

from langchain.chains.conversation.base import ConversationChain

from agentuniverse.llm.default.openrouter_openai_style_llm import OpenRouterOpenAIStyleLLM
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger


class TestOpenRouterOpenAIStyleLLM(unittest.TestCase):
    """
    Test cases for OpenRouterOpenAIStyleLLM class
    """
    
    def setUp(self) -> None:
        # Initialize ApplicationConfigManager for each test
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer
        
        # Get API key from environment variable
        # Make sure to set OPENROUTER_API_KEY environment variable before running tests
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        api_base = os.environ.get('OPENROUTER_API_BASE', 'https://openrouter.ai/api/v1/chat/completions')
        
        if not api_key:
            self.skipTest("OPENROUTER_API_KEY environment variable is not set")
        
        self.llm = OpenRouterOpenAIStyleLLM(
            model_name='openai/gpt-5-mini',
            api_key=api_key,
            api_base=api_base
        )

    def test_call(self) -> None:
        """Test synchronous call."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = self.llm.call(messages=messages, streaming=False)
        print(output.__str__())
        self.assertIsNotNone(output.text)

    def test_acall(self) -> None:
        """Test asynchronous call."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        print(output.__str__())
        self.assertIsNotNone(output.text)

    def test_call_stream(self):
        """Test streaming call."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        chunks = []
        for chunk in self.llm.call(messages=messages, streaming=True):
            print(chunk.text, end='')
            chunks.append(chunk.text)
        print()
        self.assertGreater(len(chunks), 0)

    def test_acall_stream(self):
        """Test async streaming call."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        asyncio.run(self.call_stream(messages=messages))

    async def call_stream(self, messages: list):
        """Helper for async streaming test."""
        chunks = []
        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            print(chunk.text, end='')
            chunks.append(chunk.text)
        print()
        self.assertGreater(len(chunks), 0)

    def test_as_langchain(self):
        """Test conversion to LangChain."""
        langchain_llm = self.llm.as_langchain()
        llm_chain = ConversationChain(llm=langchain_llm)
        res = llm_chain.predict(input='hello')
        print(res)
        self.assertIsNotNone(res)

    def test_max_context_length(self):
        """Test max context length method."""
        length = self.llm.max_context_length()
        print(f"Max context length for {self.llm.model_name}: {length}")
        self.assertGreater(length, 0)
        
        # Test with different model names
        self.llm.model_name = 'anthropic/claude-sonnet-4.5'
        length = self.llm.max_context_length()
        print(f"Max context length for claude-sonnet-4.5: {length}")
        self.assertEqual(length, 1000000)
        
        # Test with unknown model (should return default)
        self.llm.model_name = 'unknown/model'
        length = self.llm.max_context_length()
        print(f"Max context length for unknown model: {length}")
        self.assertEqual(length, 128000)  # Default value


if __name__ == '__main__':
    unittest.main()

