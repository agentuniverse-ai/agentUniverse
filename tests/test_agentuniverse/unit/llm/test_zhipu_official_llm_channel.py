# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_zhipu_official_llm_channel.py
"""Unit tests for ZhiPuOfficialLLMChannel configuration helpers."""

import pytest

from agentuniverse.llm.llm_channel.zhipu_official_llm_channel import (
    ZhiPuOfficialLLMChannel,
    ZHIPU_MAX_CONTEXT_LENGTH,
)


def make_channel(model):
    return ZhiPuOfficialLLMChannel(channel_model_name=model)


class TestZhiPuOfficialLLMChannel:
    """Test max context length resolution and defaults."""

    def test_api_base_default(self):
        assert (ZhiPuOfficialLLMChannel(channel_model_name="x")
                .channel_api_base == "https://open.bigmodel.cn/api/paas/v4/")

    def test_model_name_is_kept(self):
        assert make_channel("GLM-4").channel_model_name == "GLM-4"

    def test_known_model_context_lengths(self):
        assert make_channel("GLM-4").max_context_length() == 128000
        assert make_channel("GLM-4-Long").max_context_length() == 1000000
        assert make_channel("GLM-4-AirX").max_context_length() == 8000

    def test_unknown_model_falls_back(self):
        assert make_channel("no-such-model").max_context_length() == 128000

    def test_constant_map_contains_glm_models(self):
        assert ZHIPU_MAX_CONTEXT_LENGTH["GLM-4-Flash"] == 128000
        assert ZHIPU_MAX_CONTEXT_LENGTH["GLM-4-Plus"] == 128000
