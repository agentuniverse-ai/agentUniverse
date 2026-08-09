# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for HuggingFaceHubLLM."""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from agentuniverse.llm.default.huggingface_hub_llm import HuggingFaceHubLLM


class TestHuggingFaceHubLLMConfig(unittest.TestCase):

    def test_defaults_from_env(self):
        with patch.dict("os.environ", {
            "HUGGINGFACE_API_KEY": "hf-test-key",
            "HUGGINGFACE_INFERENCE_ENDPOINT": "https://my-endpoint.endpoint.huggingface.cloud",
        }):
            llm = HuggingFaceHubLLM(model_name="meta-llama/Meta-Llama-3-8B-Instruct")
            self.assertEqual(llm.api_key, "hf-test-key")
            self.assertEqual(llm.inference_endpoint,
                             "https://my-endpoint.endpoint.huggingface.cloud")

    def test_fallback_to_hf_token_env(self):
        with patch.dict("os.environ", {
            "HF_TOKEN": "hf-token-fallback",
        }, clear=True):
            llm = HuggingFaceHubLLM(model_name="m")
            self.assertEqual(llm.api_key, "hf-token-fallback")

    def test_timeout_default(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        self.assertEqual(llm.timeout, 30.0)

    def test_max_context_length_default(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        self.assertEqual(llm.max_context_length(), 4096)


class TestHuggingFaceHubLLMClient(unittest.TestCase):

    def test_new_client_uses_inference_client(self):
        llm = HuggingFaceHubLLM(
            model_name="meta-llama/Meta-Llama-3-8B-Instruct", api_key="k")
        with patch("huggingface_hub.InferenceClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            llm._new_client()
            mock_cls.assert_called_once()
            call_kwargs = mock_cls.call_args.kwargs
            self.assertEqual(call_kwargs["token"], "k")
            self.assertEqual(call_kwargs["model"],
                             "meta-llama/Meta-Llama-3-8B-Instruct")

    def test_new_client_prefers_inference_endpoint(self):
        llm = HuggingFaceHubLLM(
            model_name="some-model", api_key="k",
            inference_endpoint="https://my.endpoint.huggingface.cloud")
        with patch("huggingface_hub.InferenceClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            llm._new_client()
            call_kwargs = mock_cls.call_args.kwargs
            self.assertEqual(call_kwargs["model"],
                             "https://my.endpoint.huggingface.cloud")

    def test_new_async_client(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        with patch("huggingface_hub.AsyncInferenceClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            llm._new_async_client()
            mock_cls.assert_called_once()


class TestHuggingFaceHubLLMCall(unittest.TestCase):

    def test_call_non_streaming(self):
        llm = HuggingFaceHubLLM(
            model_name="m", api_key="k", streaming=False)
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="hello from HF"))
        ]
        mock_client.chat_completion.return_value = mock_response
        llm.client = mock_client

        result = llm._call(messages=[{"role": "user", "content": "hi"}])
        self.assertEqual(result.text, "hello from HF")

    def test_call_streaming(self):
        llm = HuggingFaceHubLLM(
            model_name="m", api_key="k", streaming=True)
        mock_client = MagicMock()

        def _fake_stream(**kwargs):
            for text in ["chunk1", "chunk2"]:
                yield MagicMock(choices=[
                    MagicMock(delta=MagicMock(content=text))
                ])
        mock_client.chat_completion.side_effect = lambda **kw: _fake_stream(**kw)
        llm.client = mock_client

        gen = llm._call(messages=[{"role": "user", "content": "hi"}])
        chunks = [chunk.text for chunk in gen]
        self.assertEqual(chunks, ["chunk1", "chunk2"])


class TestHuggingFaceHubLLMGetNumTokens(unittest.TestCase):

    def test_get_num_tokens(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        tokens = llm.get_num_tokens("hello world")
        self.assertGreater(tokens, 0)
        self.assertIsInstance(tokens, int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
