# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_claude_official_llm_channel.py
"""Unit tests for ClaudeOfficialLLMChannel."""

import pytest

from agentuniverse.llm.llm_channel.claude_official_llm_channel import (
    CLAUDE_MAX_CONTEXT_LENGTH,
    ClaudeOfficialLLMChannel,
)
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


class TestClaudeOfficialLLMChannel:
    """Test ClaudeOfficialLLMChannel implementation."""

    @pytest.fixture
    def channel(self):
        """Create a ClaudeOfficialLLMChannel instance for testing."""
        return ClaudeOfficialLLMChannel()

    def test_is_llm_channel(self, channel):
        """The class should inherit from LLMChannel."""
        assert isinstance(channel, ClaudeOfficialLLMChannel)
        assert isinstance(channel, LLMChannel)

    def test_default_channel_api_base(self, channel):
        """The channel should use the Anthropic API base by default."""
        assert channel.channel_api_base == "https://api.anthropic.com/v1/"

    def test_context_length_table_not_empty(self):
        """The context-length table should contain supported models."""
        assert CLAUDE_MAX_CONTEXT_LENGTH
        assert "claude-3-sonnet-20240229" in CLAUDE_MAX_CONTEXT_LENGTH
        assert all(v > 0 for v in CLAUDE_MAX_CONTEXT_LENGTH.values())

    @pytest.mark.parametrize(
        "model_name,expected",
        [
            ("claude-3-opus-20240229", 200000),
            ("claude-3-sonnet-20240229", 200000),
            ("claude-2.0", 100000),
            ("claude-instant-1.2", 100000),
        ],
    )
    def test_max_context_length_known_model(self, model_name, expected):
        """Known models should report their documented context length."""
        channel = ClaudeOfficialLLMChannel()
        channel.channel_model_name = model_name
        channel.channel_model_config = {}
        assert channel.max_context_length() == expected

    def test_max_context_length_unknown_model_defaults(self):
        """Unknown model names should fall back to 8000."""
        channel = ClaudeOfficialLLMChannel()
        channel.channel_model_name = "not-a-real-model"
        channel.channel_model_config = {}
        assert channel.max_context_length() == 8000
