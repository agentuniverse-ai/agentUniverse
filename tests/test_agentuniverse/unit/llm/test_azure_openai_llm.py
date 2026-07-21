# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/21
# @FileName: test_azure_openai_llm.py

"""Unit tests for AzureOpenAILLM."""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.azure_openai_llm import AzureOpenAILLM


class TestAzureOpenAILLMConfig(unittest.TestCase):

    def test_defaults_from_env(self):
        with patch.dict("os.environ", {
            "AZURE_OPENAI_API_KEY": "test-key",
            "AZURE_OPENAI_ENDPOINT": "https://my-resource.openai.azure.com",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "my-deployment",
            "AZURE_OPENAI_API_VERSION": "2024-06-01",
        }):
            llm = AzureOpenAILLM(model_name="gpt-4o")
            self.assertEqual(llm.api_key, "test-key")
            self.assertEqual(llm.api_base,
                             "https://my-resource.openai.azure.com")
            self.assertEqual(llm.deployment_name, "my-deployment")
            self.assertEqual(llm.api_version, "2024-06-01")

    def test_api_version_default(self):
        with patch.dict("os.environ", {}, clear=True):
            llm = AzureOpenAILLM(model_name="gpt-4o", api_key="k",
                                 api_base="https://x.openai.azure.com")
            self.assertEqual(llm.api_version, "2024-02-15-preview")

    def test_max_context_length(self):
        llm = AzureOpenAILLM(model_name="gpt-4o", api_key="k",
                             api_base="https://x.openai.azure.com")
        self.assertEqual(llm.max_context_length(), 128000)

    def test_max_context_length_fallback(self):
        llm = AzureOpenAILLM(model_name="unknown-model", api_key="k",
                             api_base="https://x.openai.azure.com")
        self.assertEqual(llm.max_context_length(), 4096)


class TestAzureOpenAIClientConstruction(unittest.TestCase):

    def test_build_client_kwargs(self):
        llm = AzureOpenAILLM(
            model_name="gpt-4o", api_key="k",
            api_base="https://x.openai.azure.com",
            api_version="2024-06-01")
        kwargs = llm._build_client_kwargs()
        self.assertEqual(kwargs["api_key"], "k")
        self.assertEqual(kwargs["azure_endpoint"], "https://x.openai.azure.com")
        self.assertEqual(kwargs["api_version"], "2024-06-01")

    def test_new_client_uses_azure_openai(self):
        llm = AzureOpenAILLM(
            model_name="gpt-4o", api_key="k",
            api_base="https://x.openai.azure.com")
        with patch("openai.AzureOpenAI") as mock_cls:
            mock_cls.return_value = MagicMock()
            llm._new_client()
            mock_cls.assert_called_once()

    def test_new_async_client_uses_async_azure(self):
        llm = AzureOpenAILLM(
            model_name="gpt-4o", api_key="k",
            api_base="https://x.openai.azure.com")
        with patch("openai.AsyncAzureOpenAI") as mock_cls:
            mock_cls.return_value = MagicMock()
            llm._new_async_client()
            mock_cls.assert_called_once()


class TestAzureOpenAIDeploymentNameInCall(unittest.TestCase):

    def test_call_passes_deployment_name_as_model(self):
        llm = AzureOpenAILLM(
            model_name="gpt-4o", api_key="k",
            api_base="https://x.openai.azure.com",
            deployment_name="prod-deployment")

        captured_kwargs = {}
        with patch.object(
            type(llm).__mro__[1], "_call",
            return_value=MagicMock()
        ) as mock_super:
            llm._call(messages=[{"role": "user", "content": "hi"}])
            captured_kwargs = mock_super.call_args.kwargs

        self.assertIn("model", captured_kwargs)
        self.assertEqual(captured_kwargs["model"], "prod-deployment")


class TestAzureOpenAIGetNumTokens(unittest.TestCase):

    def test_get_num_tokens_uses_tiktoken(self):
        llm = AzureOpenAILLM(
            model_name="gpt-4o", api_key="k",
            api_base="https://x.openai.azure.com")
        tokens = llm.get_num_tokens("hello world")
        self.assertGreater(tokens, 0)
        self.assertIsInstance(tokens, int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
