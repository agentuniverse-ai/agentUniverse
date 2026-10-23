# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/25 10:00
# @Author  : AI Assistant
# @Email   : assistant@example.com
# @FileName: test_azure_openai_llm.py
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.azure_openai_llm import AzureOpenAILLM


class TestAzureOpenAILLM(unittest.TestCase):
    """Test cases for AzureOpenAILLM."""

    def setUp(self):
        self.llm = AzureOpenAILLM()
        self.llm.model_name = "gpt-35-turbo"
        self.llm.api_key = "test-api-key"
        self.llm.api_base = "https://test.openai.azure.com/"
        self.llm.api_version = "2024-02-15-preview"
        self.llm.deployment_name = "test-deployment"

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.llm.model_name, "gpt-35-turbo")
        self.assertEqual(self.llm.api_key, "test-api-key")
        self.assertEqual(self.llm.api_base, "https://test.openai.azure.com/")
        self.assertEqual(self.llm.api_version, "2024-02-15-preview")
        self.assertEqual(self.llm.deployment_name, "test-deployment")

    def test_max_context_length(self):
        """Test max context length."""
        self.assertEqual(self.llm.max_context_length(), 4096)

        self.llm.model_name = "gpt-4"
        self.assertEqual(self.llm.max_context_length(), 8192)

        self.llm.model_name = "gpt-4-32k"
        self.assertEqual(self.llm.max_context_length(), 32768)

        self.llm.model_name = "gpt-4-turbo"
        self.assertEqual(self.llm.max_context_length(), 128000)

    @patch('openai.AzureOpenAI')
    def test_new_client(self, mock_azure_class):
        """Test client initialization."""
        mock_client = MagicMock()
        mock_azure_class.return_value = mock_client

        client = self.llm._new_client()
        self.assertIsNotNone(client)

    @patch('openai.AsyncAzureOpenAI')
    def test_new_async_client(self, mock_async_azure_class):
        """Test async client initialization."""
        mock_client = MagicMock()
        mock_async_azure_class.return_value = mock_client

        client = self.llm._new_async_client()
        self.assertIsNotNone(client)


if __name__ == '__main__':
    unittest.main()
