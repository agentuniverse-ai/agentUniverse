# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/11/13 19:48
# @Author  : pengqingsong.pqs
# @Email   : pengqingsong.pqs@antgroup.com
# @FileName: test_huggingface_hub_openai_style_llm.py

import asyncio
import unittest
from unittest.mock import patch

from langchain.chains.conversation.base import ConversationChain

from agentuniverse.llm.default.huggingface_hub_openai_style_llm import HuggingFaceHubLLM
from agentuniverse.llm.llm_output import LLMOutput


class TestHuggingFaceHubOpenAIStyleLLM(unittest.TestCase):
    """Test cases for HuggingFaceHubLLM class."""

    def setUp(self) -> None:
        """Set up test fixtures with valid HuggingFace Hub configuration."""
        self.llm = HuggingFaceHubLLM(
            model_name='Qwen/Qwen3-8B',
            api_key='test-api-key',
            api_base='https://router.huggingface.co/v1',
            proxy='http://127.0.0.1:10808'
        )

        # Standard test messages for consistent testing
        self.test_messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]

    def test_initialization_with_valid_params(self) -> None:
        """Test that HuggingFaceHubLLM can be initialized with valid parameters."""
        self.assertIsNotNone(self.llm)
        self.assertEqual(self.llm.model_name, 'Qwen/Qwen3-8B')
        self.assertEqual(self.llm.api_key, 'test-api-key')
        self.assertEqual(self.llm.api_base, 'https://router.huggingface.co/v1')
        self.assertEqual(self.llm.proxy, 'http://127.0.0.1:10808')

    def test_api_base_validation_invalid_urls(self) -> None:
        """Test that invalid API base URLs are handled during validation."""
        # Test empty API base during call validation
        llm_empty_base = HuggingFaceHubLLM(
            model_name='test-model',
            api_key='test-key',
            api_base=""
        )

        with self.assertRaises(ValueError) as context:
            llm_empty_base._validate_call_params(self.test_messages)
        self.assertIn("API base URL cannot be empty string", str(context.exception))

        # Test None API base during call validation
        llm_none_base = HuggingFaceHubLLM(
            model_name='test-model',
            api_key='test-key',
            api_base=None
        )

        with self.assertRaises(ValueError) as context:
            llm_none_base._validate_call_params(self.test_messages)
        self.assertIn("API base URL is required but not provided", str(context.exception))

    def test_api_key_validation(self) -> None:
        """Test API key validation logic during call validation."""
        # Test during call validation, not initialization
        llm_empty_key = HuggingFaceHubLLM(
            model_name='test-model',
            api_key='   ',  # Whitespace only
            api_base='https://router.huggingface.co/v1'
        )

        with self.assertRaises(ValueError) as context:
            llm_empty_key._validate_call_params(self.test_messages)
        self.assertIn("API key cannot be empty string", str(context.exception))

    def test_missing_api_key_validation(self) -> None:
        """Test that missing API key is properly detected during validation."""
        llm_no_key = HuggingFaceHubLLM(
            model_name='test-model',
            api_base='https://router.huggingface.co/v1'
        )

        with self.assertRaises(ValueError) as context:
            llm_no_key._validate_call_params(self.test_messages)
        self.assertIn("API key is required but not provided", str(context.exception))

    def test_message_validation_empty_messages(self) -> None:
        """Test that empty messages list raises appropriate error."""
        with self.assertRaises(ValueError) as context:
            self.llm._validate_call_params([])
        self.assertIn("Messages cannot be empty", str(context.exception))

    def test_message_validation_invalid_type(self) -> None:
        """Test that non-list messages raise appropriate error."""
        with self.assertRaises(ValueError) as context:
            self.llm._validate_call_params("not a list")
        self.assertIn("Messages must be a list", str(context.exception))

    def test_valid_message_format(self) -> None:
        """Test that valid message formats pass validation."""
        valid_messages = [
            [{"role": "user", "content": "hello"}],
            [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "hi"}]
        ]

        for messages in valid_messages:
            with self.subTest(messages=messages):
                # Should not raise any exception
                self.llm._validate_call_params(messages)

    @patch.object(HuggingFaceHubLLM, '_call')
    def test_call_method_validation(self, mock_super_call) -> None:
        """Test that call method performs proper validation before calling parent."""
        # Mock the parent class call method
        mock_super_call.return_value = LLMOutput(text="test response")

        # Test with valid messages - should pass validation and call parent
        result = self.llm._call(messages=self.test_messages)

        # Verify validation was called (no exception raised means validation passed)
        mock_super_call.assert_called_once_with(messages=self.test_messages)
        self.assertEqual(result, mock_super_call.return_value)

    @patch.object(HuggingFaceHubLLM, '_acall')
    def test_acall_method_validation(self, mock_super_acall) -> None:
        """Test that acall method performs proper validation before calling parent."""
        # Create a proper async mock return value
        expected_output = LLMOutput(text="test response")

        # Mock the async method to return the expected output
        mock_super_acall.return_value = expected_output

        # Test with valid messages - should pass validation and call parent
        async def run_test():
            result = await self.llm._acall(messages=self.test_messages)
            mock_super_acall.assert_called_once_with(messages=self.test_messages)
            return result

        result = asyncio.run(run_test())
        self.assertEqual(result.text, "test response")

    def test_call_with_invalid_messages(self) -> None:
        """Test that call method raises error with invalid messages."""
        with self.assertRaises(ValueError):
            self.llm.call(messages=[])

    def test_acall_with_invalid_messages(self) -> None:
        """Test that acall method raises error with invalid messages."""

        async def run_test():
            with self.assertRaises(ValueError):
                await self.llm.acall(messages=[])

        asyncio.run(run_test())

    def test_as_langchain_method(self) -> None:
        """Test that as_langchain method returns a valid langchain-compatible object."""
        langchain_llm = self.llm.as_langchain()
        self.assertIsNotNone(langchain_llm)
        # Verify it can be used to create a ConversationChain
        llm_chain = ConversationChain(llm=langchain_llm)
        self.assertIsNotNone(llm_chain)

    def test_get_num_tokens_method(self) -> None:
        """Test that get_num_tokens method returns a valid count."""
        test_text = "hello world"
        token_count = self.llm.get_num_tokens(test_text)
        self.assertIsInstance(token_count, int)
        self.assertGreaterEqual(token_count, 0)


if __name__ == '__main__':
    unittest.main()
