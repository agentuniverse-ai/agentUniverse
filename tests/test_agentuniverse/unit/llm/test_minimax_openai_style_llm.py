#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Deterministic unit tests for the MiniMax OpenAI-style LLM integration.

These tests exercise the *real* ``_call`` / ``_acall`` code path on
``MiniMaxOpenAIStyleLLM`` (inherited from ``OpenAIStyleLLM``) but stub out
the underlying ``openai.OpenAI`` / ``openai.AsyncOpenAI`` clients so the
tests are deterministic and require no network or API credentials.

The mocks are applied at the ``_new_client`` / ``_new_async_client`` boundary
— the channel class still controls ``api_base``, ``model_name`` etc., so the
real wiring between LLM and channel is verified.
"""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import (
    ApplicationConfigManager,
)
from agentuniverse.llm.default.minimax_openai_style_llm import (
    MINIMAX_MAX_CONTEXT_LENGTH,
    MiniMaxOpenAIStyleLLM,
)


def _init_app_configer():
    """Initialize a bare AppConfiger so ``@trace_llm`` doesn't blow up."""
    ApplicationConfigManager().app_configer = AppConfiger()


class _FakeMessage(SimpleNamespace):
    """A simple stand-in for an OpenAI message chunk used by streaming."""

    def dict(self):
        return {"choices": [{"delta": {"content": self.content}}]}


class _FakeStreamChunk(SimpleNamespace):
    """Stand-in for an OpenAI streaming chunk that supports .dict()."""

    def __init__(self, content: str):
        choices = [{"delta": {"content": content}}]
        super().__init__(choices=choices, model_dump=lambda: {"choices": choices})

    def dict(self):
        return {"choices": self.choices}


def _make_fake_chat_completion(text: str = "hello from MiniMax") -> MagicMock:
    """Build a stand-in for an OpenAI chat completion response (non-streaming)."""
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = text
    completion.model_dump.return_value = {"id": "fake", "choices": [{"message": {"content": text}}]}
    return completion


def _make_fake_stream_chunks(texts):
    """Build a stand-in for an OpenAI streaming response (sync iterable)."""
    return [_FakeStreamChunk(t) for t in texts]


def _make_fake_async_stream_chunks(texts):
    """Build a stand-in for an OpenAI streaming response (async iterable)."""

    async def _gen():
        for t in texts:
            yield _FakeStreamChunk(t)

    return _gen()


class TestMiniMaxContextLength(unittest.TestCase):
    """Configuration registration: every documented model returns the right
    context window, and unknown model names fall back conservatively."""

    def test_known_models(self):
        expected = {
            "MiniMax-M3": 1000000,
            "MiniMax-M2.7": 204800,
            "MiniMax-M2.7-highspeed": 204800,
            "MiniMax-M2.5": 204800,
            "MiniMax-M2.5-highspeed": 204800,
            "MiniMax-M2.1": 204800,
            "MiniMax-M2.1-highspeed": 204800,
            "MiniMax-M2": 204800,
            "M2-her": 64000,
        }
        for model_name, context in expected.items():
            with self.subTest(model=model_name):
                llm = MiniMaxOpenAIStyleLLM(model_name=model_name, api_key="x", api_base="y")
                self.assertEqual(llm.max_context_length(), context)

    def test_unknown_model_uses_safe_fallback(self):
        llm = MiniMaxOpenAIStyleLLM(model_name="MiniMax-future", api_key="x", api_base="y")
        # Fallback must equal the smallest catalog entry so we never advertise
        # a window larger than what any known MiniMax model actually supports.
        self.assertEqual(llm.max_context_length(), 64000)

    def test_explicit_max_context_length_overrides_table(self):
        llm = MiniMaxOpenAIStyleLLM(
            model_name="MiniMax-M3",
            api_key="x",
            api_base="y",
        )
        # The actual storage field is the private `_max_context_length` — same
        # mechanism used by set_by_agent_model.
        llm._max_context_length = 4096
        self.assertEqual(llm.max_context_length(), 4096)

    def test_catalog_constant_is_consistent(self):
        # The LLM-side and channel-side dicts must stay in sync; both modules
        # share the same dict imported via this single import.
        from agentuniverse.llm.llm_channel.minimax_official_llm_channel import (
            MINIMAX_MAX_CONTEXT_LENGTH as CHANNEL_DICT,
        )

        self.assertEqual(MINIMAX_MAX_CONTEXT_LENGTH, CHANNEL_DICT)


class TestMiniMaxConfigurationRegistration(unittest.TestCase):
    """The yaml-driven fields populate the LLM correctly."""

    def test_default_yaml_model_is_minimax_m3(self):
        # The default yaml ships with model_name 'MiniMax-M3' — that file is
        # part of the integration, so we assert it loads to the new default.
        import yaml

        with open(
            "agentuniverse/llm/default/minimax_openai_style_llm.yaml", "r", encoding="utf-8"
        ) as f:
            cfg = yaml.safe_load(f)
        self.assertEqual(cfg["model_name"], "MiniMax-M3")

    def test_env_driven_fields(self):
        with patch.dict(
            os.environ,
            {
                "MINIMAX_API_KEY": "k",
                "MINIMAX_API_BASE": "https://api.minimax.io/v1",
                "MINIMAX_ORGANIZATION": "org",
                "MINIMAX_PROXY": "http://proxy",
            },
        ):
            llm = MiniMaxOpenAIStyleLLM(model_name="MiniMax-M3")
        self.assertEqual(llm.api_key, "k")
        self.assertEqual(llm.api_base, "https://api.minimax.io/v1")
        self.assertEqual(llm.organization, "org")
        self.assertEqual(llm.proxy, "http://proxy")


class TestMiniMaxSyncCall(unittest.TestCase):
    """Synchronous calls — exercises real _call code path with the openai
    client stubbed out."""

    def setUp(self):
        _init_app_configer()
        self.llm = MiniMaxOpenAIStyleLLM(
            model_name="MiniMax-M3",
            api_key="fake-key",
            api_base="https://api.minimaxi.com/v1",
        )

    def test_call_non_streaming(self):
        completion = _make_fake_chat_completion("hello back")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = completion
        with patch.object(MiniMaxOpenAIStyleLLM, "_new_client", return_value=mock_client):
            result = self.llm.call(
                messages=[{"role": "user", "content": "hi"}], streaming=False
            )

        self.assertEqual(result.text, "hello back")
        # The real _call must have invoked the openai client with the
        # LLM's configured model_name and api_base.
        mock_client.chat.completions.create.assert_called_once()
        kwargs = mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["model"], "MiniMax-M3")
        self.assertEqual(kwargs["stream"], False)
        self.assertEqual(mock_client.base_url, "https://api.minimaxi.com/v1")

    def test_call_streaming(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _make_fake_stream_chunks(
            ["he", "llo"]
        )
        with patch.object(MiniMaxOpenAIStyleLLM, "_new_client", return_value=mock_client):
            chunks = list(
                self.llm.call(messages=[{"role": "user", "content": "hi"}], streaming=True)
            )

        # generate_stream_result should produce at least one LLMOutput-like chunk
        self.assertGreater(len(chunks), 0)
        joined = "".join(getattr(c, "text", str(c)) for c in chunks)
        self.assertIn("hello", joined)


class TestMiniMaxAsyncCall(unittest.TestCase):
    """Asynchronous calls — exercises real _acall code path."""

    def setUp(self):
        _init_app_configer()
        self.llm = MiniMaxOpenAIStyleLLM(
            model_name="M2-her",
            api_key="fake-key",
            api_base="https://api.minimax.io/v1",
        )

    def test_acall_non_streaming(self):
        completion = _make_fake_chat_completion("async hi")
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=completion)
        with patch.object(
            MiniMaxOpenAIStyleLLM, "_new_async_client", return_value=mock_client
        ):
            result = asyncio.run(
                self.llm.acall(
                    messages=[{"role": "user", "content": "hi"}], streaming=False
                )
            )

        self.assertEqual(result.text, "async hi")
        kwargs = mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["model"], "M2-her")
        # The international base URL must have been honored end-to-end.
        self.assertEqual(mock_client.base_url, "https://api.minimax.io/v1")

    def test_acall_streaming(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=_make_fake_async_stream_chunks(["a", "sync"])
        )
        with patch.object(
            MiniMaxOpenAIStyleLLM, "_new_async_client", return_value=mock_client
        ):
            chunks = asyncio.run(
                self._collect_async_stream(
                    [{"role": "user", "content": "hi"}]
                )
            )

        joined = "".join(getattr(c, "text", str(c)) for c in chunks)
        self.assertIn("async", joined)

    async def _collect_async_stream(self, messages):
        items = []
        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            items.append(chunk)
        return items


class TestMiniMaxRegionSwitching(unittest.TestCase):
    """The same LLM class must work against both the China and international
    base URLs — verified at the api_base wiring layer rather than via network."""

    def setUp(self):
        _init_app_configer()

    def _build_llm(self, region: str) -> MiniMaxOpenAIStyleLLM:
        url = {
            "cn": "https://api.minimaxi.com/v1",
            "intl": "https://api.minimax.io/v1",
        }[region]
        return MiniMaxOpenAIStyleLLM(
            model_name="MiniMax-M2",
            api_key="k",
            api_base=url,
        )

    def test_cn_url_propagates_to_client(self):
        llm = self._build_llm("cn")
        completion = _make_fake_chat_completion("cn-reply")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = completion
        with patch.object(MiniMaxOpenAIStyleLLM, "_new_client", return_value=mock_client):
            llm.call(messages=[{"role": "user", "content": "hi"}], streaming=False)
        self.assertEqual(mock_client.base_url, "https://api.minimaxi.com/v1")

    def test_intl_url_propagates_to_client(self):
        llm = self._build_llm("intl")
        completion = _make_fake_chat_completion("intl-reply")
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = completion
        with patch.object(MiniMaxOpenAIStyleLLM, "_new_client", return_value=mock_client):
            llm.call(messages=[{"role": "user", "content": "hi"}], streaming=False)
        self.assertEqual(mock_client.base_url, "https://api.minimax.io/v1")


if __name__ == "__main__":
    unittest.main()