# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_deep_seek_openai_style_llm.py
"""Unit tests for DefaultDeepSeekLLM."""

import pytest

from agentuniverse.llm.default.deep_seek_openai_style_llm import (
    DEEpSEEkMAXCONTETNLENGTH,
    DefaultDeepSeekLLM,
)
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestDefaultDeepSeekLLM:
    """Test DefaultDeepSeekLLM implementation."""

    @pytest.fixture
    def llm(self):
        """Create a DefaultDeepSeekLLM instance for testing."""
        return DefaultDeepSeekLLM(model_name="deepseek-chat")

    def test_is_openai_style_llm(self, llm):
        """The class should inherit from OpenAIStyleLLM."""
        assert isinstance(llm, DefaultDeepSeekLLM)
        assert isinstance(llm, OpenAIStyleLLM)

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert DEEpSEEkMAXCONTETNLENGTH
        assert "deepseek-chat" in DEEpSEEkMAXCONTETNLENGTH
        assert "deepseek-coder" in DEEpSEEkMAXCONTETNLENGTH
        assert all(v > 0 for v in DEEpSEEkMAXCONTETNLENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("deepseek-chat", 64000),
            ("deepseek-coder", 32000),
            ("deepseek-reasoner", 64000),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        llm = DefaultDeepSeekLLM(model_name=model_name)
        assert llm.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 4096."""
        llm = DefaultDeepSeekLLM(model_name="not-a-real-model")
        assert llm.max_context_length() == 4096

    def test_env_fields_default_to_none(self, monkeypatch):
        """Optional fields should be None when no env vars are set."""
        for key in ("DEEPSEEK_API_KEY", "DEEPSEEK_ORGANIZATION",
                    "DEEPSEEK_API_BASE", "DEEPSEEK_PROXY"):
            monkeypatch.delenv(key, raising=False)
        llm = DefaultDeepSeekLLM(model_name="deepseek-chat")
        assert llm.api_key is None
        assert llm.organization is None
        assert llm.api_base is None
        assert llm.proxy is None

    def test_env_fields_read_from_environment(self, monkeypatch):
        """Optional fields should be populated from environment variables."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-123")
        monkeypatch.setenv("DEEPSEEK_API_BASE", "https://api.example.test/v1")
        llm = DefaultDeepSeekLLM(model_name="deepseek-chat")
        assert llm.api_key == "sk-test-123"
        assert llm.api_base == "https://api.example.test/v1"
