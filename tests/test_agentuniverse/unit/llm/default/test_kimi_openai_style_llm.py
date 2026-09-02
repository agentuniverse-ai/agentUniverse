# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_kimi_openai_style_llm.py
"""Unit tests for KIMIOpenAIStyleLLM."""

import pytest

from agentuniverse.llm.default.kimi_openai_style_llm import (
    KIMI_Max_CONTEXT_LENGTH,
    KIMIOpenAIStyleLLM,
)
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestKIMIOpenAIStyleLLM:
    """Test KIMIOpenAIStyleLLM implementation."""

    @pytest.fixture
    def llm(self):
        """Create a KIMIOpenAIStyleLLM instance for testing."""
        return KIMIOpenAIStyleLLM(model_name="moonshot-v1-8k")

    def test_is_openai_style_llm(self, llm):
        """The class should inherit from OpenAIStyleLLM."""
        assert isinstance(llm, KIMIOpenAIStyleLLM)
        assert isinstance(llm, OpenAIStyleLLM)

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert KIMI_Max_CONTEXT_LENGTH
        assert "moonshot-v1-8k" in KIMI_Max_CONTEXT_LENGTH
        assert all(v > 0 for v in KIMI_Max_CONTEXT_LENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("moonshot-v1-8k", 8000),
            ("moonshot-v1-32k", 32000),
            ("moonshot-v1-128k", 128000),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        llm = KIMIOpenAIStyleLLM(model_name=model_name)
        assert llm.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 8000."""
        llm = KIMIOpenAIStyleLLM(model_name="not-a-real-model")
        assert llm.max_context_length() == 8000

    def test_env_fields_defaults(self, monkeypatch):
        """Optional fields should use documented defaults without env vars."""
        for key in ("KIMI_API_KEY", "KIMI_API_BASE", "KIMI_PROXY",
                    "KIMI_ORGANIZATION"):
            monkeypatch.delenv(key, raising=False)
        llm = KIMIOpenAIStyleLLM(model_name="moonshot-v1-8k")
        assert llm.api_key is None
        assert llm.api_base == "https://api.moonshot.cn/v1"
        assert llm.proxy is None

    def test_env_fields_read_from_environment(self, monkeypatch):
        """Optional fields should be populated from environment variables."""
        monkeypatch.setenv("KIMI_API_KEY", "sk-test-123")
        monkeypatch.setenv("KIMI_API_BASE", "https://api.example.test/v1")
        llm = KIMIOpenAIStyleLLM(model_name="moonshot-v1-8k")
        assert llm.api_key == "sk-test-123"
        assert llm.api_base == "https://api.example.test/v1"
