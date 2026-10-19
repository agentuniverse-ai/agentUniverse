# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_gemini_official_llm_channel.py
"""Unit tests for GeminiOfficialLLMChannel configuration helpers."""

import pytest

from agentuniverse.llm.llm_channel.gemini_official_llm_channel import (
    GeminiOfficialLLMChannel,
    GEMINI_MAX_CONTEXT_LENGTH,
)


def make_channel(model):
    channel = GeminiOfficialLLMChannel(channel_model_name=model)
    channel.channel_model_config = {}
    return channel


class TestGeminiOfficialLLMChannel:
    """Test max context length resolution and defaults."""

    def test_api_base_default(self):
        assert (GeminiOfficialLLMChannel(channel_model_name="x")
                .channel_api_base
                == "https://generativelanguage.googleapis.com/v1beta/openai/")

    def test_model_name_is_kept(self):
        assert make_channel("gemini-2.0-flash").channel_model_name == "gemini-2.0-flash"

    def test_known_model_context_length(self):
        assert make_channel("gemini-2.0-flash").max_context_length() == 1048576

    def test_unknown_model_falls_back(self):
        assert make_channel("no-such-model").max_context_length() == 8000

    def test_configured_length_takes_precedence(self):
        channel = make_channel("gemini-2.0-flash")
        channel._channel_model_config = {"max_context_length": 2048}
        assert channel.max_context_length() == 2048

    def test_constant_map_only_has_flash_model(self):
        assert GEMINI_MAX_CONTEXT_LENGTH == {"gemini-2.0-flash": 1048576}
