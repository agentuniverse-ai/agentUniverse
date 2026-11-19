# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_openai_official_llm_channel.py
"""Unit tests for OpenAIOfficialLLMChannel."""

import pytest

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_channel.openai_official_llm_channel import (
    OPENAI_MAX_CONTEXT_LENGTH,
    OpenAIOfficialLLMChannel,
)


class TestOpenAIOfficialLLMChannel:
    """Test OpenAIOfficialLLMChannel implementation."""

    @pytest.fixture
    def channel(self):
        """Create an OpenAIOfficialLLMChannel instance for testing."""
        return OpenAIOfficialLLMChannel()

    def test_is_llm_channel(self, channel):
        """The class should inherit from LLMChannel."""
        assert isinstance(channel, OpenAIOfficialLLMChannel)
        assert isinstance(channel, LLMChannel)

    def test_default_channel_api_base(self, channel):
        """The channel should use the OpenAI API base by default."""
        assert channel.channel_api_base == "https://api.openai.com/v1"

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert OPENAI_MAX_CONTEXT_LENGTH
        assert "gpt-4o" in OPENAI_MAX_CONTEXT_LENGTH
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
        channel = OpenAIOfficialLLMChannel()
        channel.channel_model_name = model_name
        channel.channel_model_config = {}
        assert channel.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 128000."""
        channel = OpenAIOfficialLLMChannel()
        channel.channel_model_name = "not-a-real-model"
        channel.channel_model_config = {}
        assert channel.max_context_length() == 128000
