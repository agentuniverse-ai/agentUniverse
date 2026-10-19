# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_baichuan_official_llm_channel.py
"""Unit tests for BaichuanOfficialLLMChannel configuration helpers."""

import pytest

from agentuniverse.llm.llm_channel.baichuan_official_llm_channel import (
    BaichuanOfficialLLMChannel,
    BAICHUAN_MAX_CONTEXT_LENGTH,
)


def make_channel(model):
    channel = BaichuanOfficialLLMChannel(channel_model_name=model)
    channel.channel_model_config = {}
    return channel


class TestBaichuanOfficialLLMChannel:
    """Test max context length resolution and defaults."""

    def test_api_base_default(self):
        assert (BaichuanOfficialLLMChannel(channel_model_name="x")
                .channel_api_base == "https://api.baichuan-ai.com/v1")

    def test_model_name_is_kept(self):
        assert make_channel("Baichuan4").channel_model_name == "Baichuan4"

    def test_known_model_context_lengths(self):
        assert make_channel("Baichuan2-Turbo").max_context_length() == 8000
        assert make_channel("Baichuan2-Turbo-192k").max_context_length() == 192000
        assert make_channel("Baichuan3-Turbo-128k").max_context_length() == 128000

    def test_unknown_model_falls_back(self):
        assert make_channel("no-such-model").max_context_length() == 8000

    def test_configured_length_takes_precedence(self):
        channel = make_channel("Baichuan4")
        channel._channel_model_config = {"max_context_length": 777}
        assert channel.max_context_length() == 777

    def test_constant_map_contains_baichuan4(self):
        assert BAICHUAN_MAX_CONTEXT_LENGTH["Baichuan4"] == 8000
