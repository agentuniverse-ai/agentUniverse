# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for HuggingFaceHubLLM."""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.llm.default.huggingface_hub_llm import HuggingFaceHubLLM


class _FakeConfiger:
    """Minimal Configer stand-in exposing a raw yaml value dict."""

    def __init__(self, value):
        self.value = value
        self.path = "huggingface_hub_llm.yaml"


def _make_llm_configer(value):
    configer = LLMConfiger().load_by_configer(_FakeConfiger(value))
    configer.yaml_func_instance = None
    return configer


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


class TestHuggingFaceHubLLMConfigerInit(unittest.TestCase):

    _METADATA = {
        "type": "LLM",
        "module": "agentuniverse.llm.default.huggingface_hub_llm",
        "class": "HuggingFaceHubLLM",
    }

    def test_yaml_fields_are_applied(self):
        llm = HuggingFaceHubLLM(model_name="m")
        configer = _make_llm_configer({
            "name": "default_huggingface_hub_llm",
            "description": "desc",
            "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
            "api_key": "hf-from-yaml",
            "inference_endpoint": "https://my.endpoint.huggingface.cloud",
            "timeout": 60,
            "metadata": self._METADATA,
        })
        llm.initialize_by_component_configer(configer)
        self.assertEqual(llm.name, "default_huggingface_hub_llm")
        self.assertEqual(llm.model_name, "meta-llama/Meta-Llama-3-8B-Instruct")
        self.assertEqual(llm.api_key, "hf-from-yaml")
        self.assertEqual(llm.inference_endpoint,
                         "https://my.endpoint.huggingface.cloud")
        self.assertEqual(llm.timeout, 60)

    def test_empty_placeholder_does_not_clobber_env_fallback(self):
        # Unset ${VAR} placeholders resolve to '' at config load time.
        llm = HuggingFaceHubLLM(model_name="m", api_key="hf-token-fallback")
        configer = _make_llm_configer({
            "name": "default_huggingface_hub_llm",
            "model_name": "m",
            "api_key": "",
            "inference_endpoint": "",
            "metadata": self._METADATA,
        })
        llm.initialize_by_component_configer(configer)
        self.assertEqual(llm.api_key, "hf-token-fallback")
        self.assertIsNone(llm.inference_endpoint)

    def test_absent_fields_keep_defaults(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        configer = _make_llm_configer({
            "name": "default_huggingface_hub_llm",
            "model_name": "m",
            "metadata": self._METADATA,
        })
        llm.initialize_by_component_configer(configer)
        self.assertEqual(llm.api_key, "k")
        self.assertEqual(llm.timeout, 30.0)


class TestHuggingFaceHubLLMGetNumTokens(unittest.TestCase):

    def test_get_num_tokens(self):
        llm = HuggingFaceHubLLM(model_name="m", api_key="k")
        tokens = llm.get_num_tokens("hello world")
        self.assertGreater(tokens, 0)
        self.assertIsInstance(tokens, int)


if __name__ == "__main__":
    unittest.main(verbosity=2)
