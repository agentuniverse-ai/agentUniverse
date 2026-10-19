# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_kimi_official_llm_channel.py
"""Unit tests for KimiOfficialLLMChannel configuration helpers."""

import pytest

from agentuniverse.llm.llm_channel.kimi_official_llm_channel import (
    KimiOfficialLLMChannel,
    KIMI_MAX_CONTEXT_LENGTH,
)


def make_channel(model):
    channel = KimiOfficialLLMChannel(channel_model_name=model)
    channel.channel_model_config = {}
    return channel


class TestKimiOfficialLLMChannel:
    """Test max context length resolution and defaults."""

    def test_api_base_default(self):
        assert (KimiOfficialLLMChannel(channel_model_name="x")
                .channel_api_base == "https://api.moonshot.cn/v1")

    def test_model_name_is_kept(self):
        assert make_channel("moonshot-v1-8k").channel_model_name == "moonshot-v1-8k"

    def test_known_model_context_lengths(self):
        assert make_channel("moonshot-v1-8k").max_context_length() == 8000
        assert make_channel("moonshot-v1-32k").max_context_length() == 32000
        assert make_channel("moonshot-v1-128k").max_context_length() == 128000

    def test_unknown_model_falls_back(self):
        assert make_channel("no-such-model").max_context_length() == 8000

    def test_configured_length_takes_precedence(self):
        channel = make_channel("moonshot-v1-8k")
        channel._channel_model_config = {"max_context_length": 999}
        assert channel.max_context_length() == 999

    def test_constant_map_contains_models(self):
        assert set(KIMI_MAX_CONTEXT_LENGTH) == {"moonshot-v1-8k",
                                                "moonshot-v1-32k",
                                                "moonshot-v1-128k"}
