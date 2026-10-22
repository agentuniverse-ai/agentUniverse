# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/20
# @FileName: test_kimi_openai_style_llm.py

"""Unit tests for KIMIOpenAIStyleLLM.get_num_tokens failure handling.

The tokenizer endpoint is a synchronous HTTP call on the LLM hot path. These
tests lock in the failure contract added alongside the timeout: a stalled or
malformed response surfaces a clear ``RuntimeError`` instead of hanging the
call or crashing deep in a ``None.get`` chain.
"""

import unittest
from unittest.mock import patch, MagicMock

from agentuniverse.llm.default.kimi_openai_style_llm import KIMIOpenAIStyleLLM


def _make_response(status_code: int = 200, json_body=None, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 300
    response.text = text or (str(json_body) if json_body is not None else "")
    if json_body is not None:
        response.json.return_value = json_body
    else:
        def _raise():
            raise ValueError("not JSON")
        response.json.side_effect = _raise
    return response


class TestKimiGetNumTokensFailureHandling(unittest.TestCase):
    """get_num_tokens must surface clear errors for every non-happy path."""

    def setUp(self) -> None:
        # A minimal instance; we never hit the network because requests.post
        # is patched in each test.
        self.llm = KIMIOpenAIStyleLLM(model_name="moonshot-v1-8k",
                                      api_key="test-key",
                                      api_base="https://tokenizer.example/v1")

    def test_happy_path_returns_total_tokens(self) -> None:
        response = _make_response(json_body={"data": {"total_tokens": 42}})
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response) as posted:
            result = self.llm.get_num_tokens("hello")
        self.assertEqual(result, 42)
        # Timeout was actually passed through.
        self.assertIn("timeout", posted.call_args.kwargs)
        self.assertIsNotNone(posted.call_args.kwargs["timeout"])

    def test_non_2xx_response_raises_runtime_error_with_status(self) -> None:
        # Previously: res.json() would raise JSONDecodeError with no context.
        response = _make_response(status_code=503, text="service unavailable")
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                self.llm.get_num_tokens("hello")
        self.assertIn("503", str(ctx.exception))
        self.assertIn("tokenizer.example", str(ctx.exception))

    def test_non_json_body_raises_runtime_error_with_url(self) -> None:
        # A gateway HTML error page instead of JSON.
        response = _make_response(json_body=None, text="<html>gateway error</html>")
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                self.llm.get_num_tokens("hello")
        self.assertIn("non-JSON", str(ctx.exception))

    def test_missing_data_field_raises_clear_error(self) -> None:
        # Regression: previously this hit ``None.get('total_tokens')`` and
        # raised AttributeError: 'NoneType' object has no attribute 'get'.
        response = _make_response(json_body={"unexpected": "shape"})
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                self.llm.get_num_tokens("hello")
        self.assertIn("total_tokens", str(ctx.exception))

    def test_missing_total_tokens_raises_clear_error(self) -> None:
        response = _make_response(json_body={"data": {"some_other_field": 1}})
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                self.llm.get_num_tokens("hello")
        self.assertIn("total_tokens", str(ctx.exception))

    def test_non_integer_total_tokens_raises_clear_error(self) -> None:
        response = _make_response(json_body={"data": {"total_tokens": "not-a-number"}})
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response):
            with self.assertRaises(RuntimeError) as ctx:
                self.llm.get_num_tokens("hello")
        self.assertIn("non-integer", str(ctx.exception))

    def test_request_timeout_is_passed_through(self) -> None:
        # A stalled tokenizer must not hang the call indefinitely. The timeout
        # is the contract; this test pins it so it cannot silently regress.
        response = _make_response(json_body={"data": {"total_tokens": 0}})
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   return_value=response) as posted:
            self.llm.get_num_tokens("hello")
        timeout = posted.call_args.kwargs["timeout"]
        self.assertIsNotNone(timeout)
        self.assertGreater(timeout, 0)

    def test_connection_error_propagates(self) -> None:
        # requests itself raises on connection failure / timeout; that should
        # propagate unchanged rather than being swallowed into a RuntimeError.
        import requests as requests_module
        with patch("agentuniverse.llm.default.kimi_openai_style_llm.requests.post",
                   side_effect=requests_module.ConnectionError("dns failure")):
            with self.assertRaises(requests_module.ConnectionError):
                self.llm.get_num_tokens("hello")


if __name__ == "__main__":
    unittest.main(verbosity=2)
