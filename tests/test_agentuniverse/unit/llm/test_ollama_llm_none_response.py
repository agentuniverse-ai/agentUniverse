# !/usr/bin/env python3

# @Time    : 2026/07/20
# @FileName: test_ollama_llm_none_response.py

"""Unit tests for Ollama LLM error-response handling.

Ollama returns a top-level ``error`` field (instead of ``message``) when the
model is missing, the request is malformed, or the server hits an internal
error. The previous code crashed deep in a ``None.get`` chain with no hint of
the real cause; these tests lock in the contract that the Ollama error is
surfaced verbatim and unexpected shapes raise a clear ValueError.
"""

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.default_ollama_llm import (
    OllamaLLM,
    _extract_ollama_message,
)


async def _async_value(value):
    """Wrap a value in an awaitable for mocking async client methods."""
    return value


class TestExtractOllamaMessage(unittest.TestCase):
    """The shared helper is the contract every call site now depends on."""

    def test_happy_path_returns_message_dict(self) -> None:
        message = _extract_ollama_message({"message": {"role": "assistant", "content": "hi"}})
        self.assertEqual(message, {"role": "assistant", "content": "hi"})

    def test_error_field_surfaces_as_runtime_error(self) -> None:
        # The most common real-world failure: model not found / context
        # overflow. Ollama returns {"error": "..."} with no "message".
        with self.assertRaises(RuntimeError) as ctx:
            _extract_ollama_message({"error": "model 'llama-99x' not found"})
        self.assertIn("model 'llama-99x' not found", str(ctx.exception))

    def test_missing_message_raises_clear_value_error(self) -> None:
        # Regression: previously raised
        # AttributeError: 'NoneType' object has no attribute 'get'.
        with self.assertRaises(ValueError) as ctx:
            _extract_ollama_message({"done": True, "eval_count": 0})
        self.assertIn("missing the 'message' object", str(ctx.exception))

    def test_non_dict_response_raises_clear_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _extract_ollama_message("not-a-dict")
        self.assertIn("unexpected response type", str(ctx.exception))

    def test_message_wrong_type_raises_clear_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _extract_ollama_message({"message": "wrong-type"})
        self.assertIn("missing the 'message' object", str(ctx.exception))


class TestOllamaLLMCallSurfacesErrors(unittest.TestCase):
    """_call and _acall must surface the Ollama error instead of NoneType."""

    def setUp(self) -> None:
        # Stub client so we never touch the network. We patch _new_client /
        # _new_async_client to return a MagicMock whose .chat returns the
        # response we configure per test.
        self.llm = OllamaLLM(
            model_name="test-model",
            base_url="http://localhost:11434",
            streaming=False,
            max_context_length=2048,
            max_tokens=16,
            temperature=0.0,
            request_timeout=10,
        )

    def _patch_client(self, response):
        client = MagicMock()
        client.chat.return_value = response
        # _options() in the real code returns an ollama.Options pydantic object
        # whose setdefault behaviour is unrelated to this PR; return a plain
        # dict so we exercise only the error-handling path under test.
        options_patch = patch.object(self.llm, "_options", return_value={})
        client_patch = patch.object(self.llm, "_new_client", return_value=client)
        return client_patch, options_patch

    def _call_with_response(self, response):
        client_patch, options_patch = self._patch_client(response)
        with client_patch, options_patch:
            return self.llm._call(messages=[{"role": "user", "content": "hi"}])

    def _call_expect_error(self, response, exc_type):
        client_patch, options_patch = self._patch_client(response)
        with client_patch, options_patch, self.assertRaises(exc_type) as ctx:
            self.llm._call(messages=[{"role": "user", "content": "hi"}])
        return ctx

    def test_call_with_error_response_raises_runtime_error(self) -> None:
        ctx = self._call_expect_error({"error": "model 'x' not found"}, RuntimeError)
        self.assertIn("model 'x' not found", str(ctx.exception))

    def test_call_with_missing_message_raises_value_error(self) -> None:
        ctx = self._call_expect_error({"done": True}, ValueError)
        self.assertIn("missing the 'message' object", str(ctx.exception))

    def test_call_happy_path_returns_llm_output(self) -> None:
        output = self._call_with_response({"message": {"role": "assistant", "content": "hello"}})
        self.assertEqual(output.text, "hello")

    def test_call_with_empty_content_returns_empty_string_not_crash(self) -> None:
        # A well-formed response whose content is empty must not crash; it
        # yields an empty-string LLMOutput.
        output = self._call_with_response({"message": {"role": "assistant", "content": ""}})
        self.assertEqual(output.text, "")

    def test_async_call_with_error_response_raises_runtime_error(self) -> None:
        import asyncio

        async_client = MagicMock()
        # client.chat is awaited, so it must return an awaitable resolving to
        # the Ollama error response.
        async_client.chat = MagicMock(return_value=_async_value({"error": "internal error"}))

        with (
            patch.object(self.llm, "_new_async_client", return_value=async_client),
            patch.object(self.llm, "_options", return_value={}),
            self.assertRaises(RuntimeError) as ctx,
        ):
            asyncio.new_event_loop().run_until_complete(self.llm._acall(messages=[{"role": "user", "content": "hi"}]))
        self.assertIn("internal error", str(ctx.exception))


class TestOllamaChannelUsesSameHelperContract(unittest.TestCase):
    """The channel layer imports and uses the same shared helper.

    We assert the import directly rather than reconstructing a V1-style
    LLMChannel subclass (which has stricter field requirements); the helper-
    level tests above already lock in the contract the channel depends on.
    """

    def test_channel_module_imports_shared_helper(self) -> None:
        from agentuniverse.llm.llm_channel import ollama_llm_channel as channel_module

        # The channel must source its error-handling from the same helper as
        # the default LLM, so the two cannot drift.
        self.assertIs(
            channel_module._extract_ollama_message,
            _extract_ollama_message,
            "OllamaLLMChannel must import _extract_ollama_message from agentuniverse.llm.default.default_ollama_llm",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
