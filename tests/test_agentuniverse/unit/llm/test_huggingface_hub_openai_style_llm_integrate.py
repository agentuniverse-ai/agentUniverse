# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/13 20:01
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_huggingface_hub_openai_style_llm_integrate.py

import asyncio
import unittest

from langchain.chains.conversation.base import ConversationChain

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.huggingface_hub_openai_style_llm import HuggingFaceHubLLM
from agentuniverse.llm.llm_output import LLMOutput


class TestHuggingFaceHubLLMIntegration(unittest.TestCase):
    """Integration tests for HuggingFaceHubLLM (requires network access)."""

    def setUp(self) -> None:
        """Set up test fixtures for integration tests."""
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer

        # Configuration for real API calls - update these with your actual credentials
        self.model_name = 'Qwen/Qwen3-8B'  # or any other available model
        self.api_key = 'your-huggingface-api-key'  # Replace with real API key
        self.api_base = 'https://router.huggingface.co/v1'
        self.proxy = 'socks5://127.0.0.1:13659'  # Set if you need proxy

        self.test_messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]

        # Skip tests if credentials are not provided
        self.skip_tests = self.api_key == 'your-huggingface-api-key'

    def test_real_sync_call(self) -> None:
        """Test real synchronous API call to HuggingFace Hub."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        try:
            output = llm.call(messages=self.test_messages, streaming=False)
            self.assertIsInstance(output, LLMOutput)
            self.assertIsNotNone(output.text)
            self.assertGreater(len(output.text), 0)
            print(f"Sync call response: {output.text[:100]}...")
        except Exception as e:
            self.fail(f"Synchronous API call failed: {str(e)}")

    def test_real_async_call(self) -> None:
        """Test real asynchronous API call to HuggingFace Hub."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        async def run_async_test():
            try:
                output = await llm.acall(messages=self.test_messages, streaming=False)
                self.assertIsInstance(output, LLMOutput)
                self.assertIsNotNone(output.text)
                self.assertGreater(len(output.text), 0)
                print(f"Async call response: {output.text[:100]}...")
                return output
            except Exception as e:
                self.fail(f"Asynchronous API call failed: {str(e)}")

        asyncio.run(run_async_test())

    def test_real_sync_stream_call(self) -> None:
        """Test real synchronous streaming API call to HuggingFace Hub."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        try:
            chunks = []
            for chunk in llm.call(messages=self.test_messages, streaming=True):
                self.assertIsNotNone(chunk)
                self.assertIsNotNone(chunk.text)
                chunks.append(chunk.text)
                print(chunk.text, end='')

            print()  # New line after streaming
            self.assertGreater(len(chunks), 0)
            full_response = ''.join(chunks)
            self.assertGreater(len(full_response), 0)
            print(f"Sync stream completed. Total chunks: {len(chunks)}")

        except Exception as e:
            self.fail(f"Synchronous streaming API call failed: {str(e)}")

    def test_real_async_stream_call(self) -> None:
        """Test real asynchronous streaming API call to HuggingFace Hub."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        async def run_async_stream_test():
            try:
                chunks = []
                async for chunk in await llm.acall(messages=self.test_messages, streaming=True):
                    self.assertIsNotNone(chunk)
                    self.assertIsNotNone(chunk.text)
                    chunks.append(chunk.text)
                    print(chunk.text, end='')

                print()  # New line after streaming
                self.assertGreater(len(chunks), 0)
                full_response = ''.join(chunks)
                self.assertGreater(len(full_response), 0)
                print(f"Async stream completed. Total chunks: {len(chunks)}")

            except Exception as e:
                self.fail(f"Asynchronous streaming API call failed: {str(e)}")

        asyncio.run(run_async_stream_test())

    def test_real_langchain_integration(self) -> None:
        """Test real integration with langchain."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        try:
            langchain_llm = llm.as_langchain()
            llm_chain = ConversationChain(llm=langchain_llm)

            # Test simple conversation
            response = llm_chain.predict(input="Hello, how are you?")
            self.assertIsNotNone(response)
            self.assertGreater(len(response), 0)
            print(f"LangChain response: {response[:100]}...")

        except Exception as e:
            self.fail(f"LangChain integration test failed: {str(e)}")

    def test_real_get_num_tokens(self) -> None:
        """Test real token counting functionality."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        try:
            test_text = "Hello, world! This is a test message for token counting."
            token_count = llm.get_num_tokens(test_text)

            self.assertIsInstance(token_count, int)
            self.assertGreater(token_count, 0)
            print(f"Token count for '{test_text}': {token_count}")

        except Exception as e:
            self.fail(f"Token counting test failed: {str(e)}")

    def test_real_conversation_flow(self) -> None:
        """Test a complete conversation flow with multiple messages."""
        if self.skip_tests:
            self.skipTest("Real API credentials not provided")

        llm = HuggingFaceHubLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base,
            proxy=self.proxy
        )

        conversation_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"},
        ]

        try:
            output = llm.call(messages=conversation_messages, streaming=False)
            self.assertIsInstance(output, LLMOutput)
            self.assertIsNotNone(output.text)
            self.assertIn("4", output.text)  # Should contain the answer
            print(f"Conversation response: {output.text}")

        except Exception as e:
            self.fail(f"Conversation flow test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
