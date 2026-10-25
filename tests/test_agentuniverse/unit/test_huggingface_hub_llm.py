# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_huggingface_hub_llm.py
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.huggingface_hub_llm import HuggingFaceHubLLM


class TestHuggingFaceHubLLM(unittest.TestCase):
    """Test cases for HuggingFaceHubLLM."""

    def setUp(self):
        self.llm = HuggingFaceHubLLM()
        self.llm.model_name = "gpt2"
        self.llm.api_key = "test-api-key"

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.llm.model_name, "gpt2")
        self.assertEqual(self.llm.api_key, "test-api-key")
        self.assertIsNotNone(self.llm.temperature)
        self.assertIsNotNone(self.llm.max_new_tokens)

    def test_messages_to_prompt(self):
        """Test message to prompt conversion."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        prompt = self.llm._messages_to_prompt(messages)
        self.assertIn("System: You are a helpful assistant.", prompt)
        self.assertIn("User: Hello!", prompt)
        self.assertIn("Assistant: Hi there!", prompt)
        self.assertIn("User: How are you?", prompt)
        self.assertTrue(prompt.endswith("Assistant:"))

    def test_max_context_length(self):
        """Test max context length."""
        self.assertEqual(self.llm.max_context_length(), 1024)

        self.llm.model_name = "meta-llama/Llama-2-7b"
        self.assertEqual(self.llm.max_context_length(), 4096)

        self.llm.model_name = "unknown-model"
        self.assertEqual(self.llm.max_context_length(), 2048)

    @patch('huggingface_hub.InferenceClient')
    def test_call(self, mock_client_class):
        """Test _call method."""
        mock_client = MagicMock()
        mock_client.text_generation.return_value = "Hello! I'm doing well, thank you!"
        mock_client_class.return_value = mock_client

        messages = [{"role": "user", "content": "Hello!"}]
        result = self.llm._call(messages)

        self.assertIsNotNone(result)
        self.assertEqual(result.text, "Hello! I'm doing well, thank you!")

    @patch('huggingface_hub.InferenceClient')
    def test_call_with_custom_params(self, mock_client_class):
        """Test _call with custom parameters."""
        mock_client = MagicMock()
        mock_client.text_generation.return_value = "Custom response"
        mock_client_class.return_value = mock_client

        messages = [{"role": "user", "content": "Test"}]
        result = self.llm._call(
            messages,
            max_new_tokens=100,
            temperature=0.7,
            top_p=0.9,
        )

        self.assertIsNotNone(result)
        mock_client.text_generation.assert_called_once()


if __name__ == '__main__':
    unittest.main()
