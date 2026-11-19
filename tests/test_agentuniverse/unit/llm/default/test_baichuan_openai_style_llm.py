# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_baichuan_openai_style_llm.py
"""Unit tests for BAICHUANOpenAIStyleLLM."""

import pytest

from agentuniverse.llm.default.baichuan_openai_style_llm import (
    BAICHUAN_Max_CONTEXT_LENGTH,
    BAICHUANOpenAIStyleLLM,
)
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestBAICHUANOpenAIStyleLLM:
    """Test BAICHUANOpenAIStyleLLM implementation."""

    @pytest.fixture
    def llm(self):
        """Create a BAICHUANOpenAIStyleLLM instance for testing."""
        return BAICHUANOpenAIStyleLLM(model_name="Baichuan4")

    def test_is_openai_style_llm(self, llm):
        """The class should inherit from OpenAIStyleLLM."""
        assert isinstance(llm, BAICHUANOpenAIStyleLLM)
        assert isinstance(llm, OpenAIStyleLLM)

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert BAICHUAN_Max_CONTEXT_LENGTH
        assert "Baichuan2-Turbo" in BAICHUAN_Max_CONTEXT_LENGTH
        assert "Baichuan4" in BAICHUAN_Max_CONTEXT_LENGTH
        assert all(v > 0 for v in BAICHUAN_Max_CONTEXT_LENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("Baichuan2-Turbo", 8000),
            ("Baichuan2-Turbo-192k", 192000),
            ("Baichuan3-Turbo-128k", 128000),
            ("Baichuan4", 8000),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        llm = BAICHUANOpenAIStyleLLM(model_name=model_name)
        assert llm.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 8000."""
        llm = BAICHUANOpenAIStyleLLM(model_name="not-a-real-model")
        assert llm.max_context_length() == 8000

    def test_env_fields_defaults(self, monkeypatch):
        """Optional fields should use documented defaults without env vars."""
        for key in ("BAICHUAN_API_KEY", "BAICHUAN_API_BASE", "BAICHUAN_PROXY",
                    "BAICHUAN_ORGANIZATION"):
            monkeypatch.delenv(key, raising=False)
        llm = BAICHUANOpenAIStyleLLM(model_name="Baichuan4")
        assert llm.api_key is None
        assert llm.api_base == "https://api.baichuan-ai.com/v1"
        assert llm.proxy is None

    def test_env_fields_read_from_environment(self, monkeypatch):
        """Optional fields should be populated from environment variables."""
        monkeypatch.setenv("BAICHUAN_API_KEY", "sk-test-123")
        monkeypatch.setenv("BAICHUAN_API_BASE", "https://api.example.test/v1")
        llm = BAICHUANOpenAIStyleLLM(model_name="Baichuan4")
        assert llm.api_key == "sk-test-123"
        assert llm.api_base == "https://api.example.test/v1"
