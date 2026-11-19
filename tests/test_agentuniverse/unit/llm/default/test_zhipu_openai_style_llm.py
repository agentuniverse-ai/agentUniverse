# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_zhipu_openai_style_llm.py
"""Unit tests for DefaultZhiPuLLM."""

import pytest

from agentuniverse.llm.default.zhipu_openai_style_llm import (
    ZHIPU_MAXCONTETNLENGTH,
    DefaultZhiPuLLM,
)
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestDefaultZhiPuLLM:
    """Test DefaultZhiPuLLM implementation."""

    @pytest.fixture
    def llm(self):
        """Create a DefaultZhiPuLLM instance for testing."""
        return DefaultZhiPuLLM(model_name="GLM-4")

    def test_is_openai_style_llm(self, llm):
        """The class should inherit from OpenAIStyleLLM."""
        assert isinstance(llm, DefaultZhiPuLLM)
        assert isinstance(llm, OpenAIStyleLLM)

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert ZHIPU_MAXCONTETNLENGTH
        assert "GLM-4-Plus" in ZHIPU_MAXCONTETNLENGTH
        assert all(v > 0 for v in ZHIPU_MAXCONTETNLENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("GLM-4-Plus", 128000),
            ("GLM-4-Air", 128000),
            ("GLM-4-Long", 1000000),
            ("GLM-4-Flash", 128000),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        llm = DefaultZhiPuLLM(model_name=model_name)
        assert llm.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 128000."""
        llm = DefaultZhiPuLLM(model_name="not-a-real-model")
        assert llm.max_context_length() == 128000

    def test_env_fields_default_to_none(self, monkeypatch):
        """Optional fields should be None when no env vars are set."""
        for key in ("ZHIPU_API_KEY", "ZHIPU_ORGANIZATION",
                    "ZHIPU_API_BASE", "ZHIPU_PROXY"):
            monkeypatch.delenv(key, raising=False)
        llm = DefaultZhiPuLLM(model_name="GLM-4")
        assert llm.api_key is None
        assert llm.organization is None
        assert llm.api_base is None
        assert llm.proxy is None

    def test_env_fields_read_from_environment(self, monkeypatch):
        """Optional fields should be populated from environment variables."""
        monkeypatch.setenv("ZHIPU_API_KEY", "sk-test-123")
        monkeypatch.setenv("ZHIPU_API_BASE", "https://api.example.test/v1")
        llm = DefaultZhiPuLLM(model_name="GLM-4")
        assert llm.api_key == "sk-test-123"
        assert llm.api_base == "https://api.example.test/v1"
