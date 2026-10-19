# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/01 10:00
# @Author  : Yue Wang
# @FileName: test_default_openai_llm.py
"""Unit tests for DefaultOpenAILLM."""

import pytest

from agentuniverse.llm.default.default_openai_llm import (
    OPENAI_MAX_CONTEXT_LENGTH,
    DefaultOpenAILLM,
)
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestDefaultOpenAILLM:
    """Test DefaultOpenAILLM implementation."""

    @pytest.fixture
    def llm(self):
        """Create a DefaultOpenAILLM instance for testing."""
        return DefaultOpenAILLM(model_name="gpt-4o")

    def test_is_openai_style_llm(self, llm):
        """The class should inherit from OpenAIStyleLLM."""
        assert isinstance(llm, DefaultOpenAILLM)
        assert isinstance(llm, OpenAIStyleLLM)

    def test_context_length_table_not_empty(self):
        """The max-context-length table should contain known models."""
        assert OPENAI_MAX_CONTEXT_LENGTH
        assert "gpt-3.5-turbo" in OPENAI_MAX_CONTEXT_LENGTH
        assert all(v > 0 for v in OPENAI_MAX_CONTEXT_LENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("gpt-3.5-turbo", 4096),
            ("gpt-4", 8192),
            ("gpt-4o", 128000),
            ("gpt-4-32k", 32768),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        llm = DefaultOpenAILLM(model_name=model_name)
        assert llm.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown or missing model names should fall back to 4096."""
        llm = DefaultOpenAILLM(model_name="not-a-real-model")
        assert llm.max_context_length() == 4096
        assert DefaultOpenAILLM().max_context_length() == 4096

    def test_env_fields_default_to_none(self, monkeypatch):
        """Optional fields should be None when no env vars are set."""
        for key in ("OPENAI_API_KEY", "OPENAI_ORGANIZATION",
                    "OPENAI_API_BASE", "OPENAI_PROXY"):
            monkeypatch.delenv(key, raising=False)
        llm = DefaultOpenAILLM(model_name="gpt-4o")
        assert llm.api_key is None
        assert llm.organization is None
        assert llm.api_base is None
        assert llm.proxy is None

    def test_env_fields_read_from_environment(self, monkeypatch):
        """Optional fields should be populated from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
        monkeypatch.setenv("OPENAI_API_BASE", "https://api.example.test/v1")
        llm = DefaultOpenAILLM(model_name="gpt-4o")
        assert llm.api_key == "sk-test-123"
        assert llm.api_base == "https://api.example.test/v1"
