# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_deepseek_official_llm_channel.py
"""Unit tests for DeepseekOfficialLLMChannel configuration helpers."""

import pytest

from agentuniverse.llm.llm_channel.deepseek_official_llm_channel import (
    DeepseekOfficialLLMChannel,
    DEEPSEEK_MAX_CONTEXT_LENGTH,
)


def make_channel(model):
    channel = DeepseekOfficialLLMChannel(channel_model_name=model)
    channel.channel_model_config = {}
    return channel


class TestDeepseekOfficialLLMChannel:
    """Test max context length resolution and defaults."""

    def test_api_base_default(self):
        assert (DeepseekOfficialLLMChannel(channel_model_name="x")
                .channel_api_base == "https://api.deepseek.com/v1")

    def test_model_name_is_kept(self):
        channel = make_channel("deepseek-chat")
        assert channel.channel_model_name == "deepseek-chat"

    def test_known_model_context_length(self):
        assert make_channel("deepseek-chat").max_context_length() == 64000
        assert make_channel("deepseek-coder").max_context_length() == 32000

    def test_unknown_model_falls_back(self):
        assert make_channel("no-such-model").max_context_length() == 8000

    def test_configured_length_takes_precedence(self):
        channel = make_channel("deepseek-chat")
        channel._channel_model_config = {"max_context_length": 12345}
        assert channel.max_context_length() == 12345

    def test_constant_map_contains_reasoner(self):
        assert DEEPSEEK_MAX_CONTEXT_LENGTH["deepseek-reasoner"] == 64000
