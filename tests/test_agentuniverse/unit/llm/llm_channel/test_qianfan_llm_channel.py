# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_qianfan_llm_channel.py
"""Unit tests for QianfanLLMChannel."""

import pytest

from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_channel.qianfan_llm_channel import QianfanLLMChannel


class TestQianfanLLMChannel:
    """Test QianfanLLMChannel implementation."""

    @pytest.fixture
    def channel(self):
        """Create a QianfanLLMChannel instance for testing."""
        return QianfanLLMChannel()

    def test_is_llm_channel(self, channel):
        """The class should inherit from LLMChannel."""
        assert isinstance(channel, QianfanLLMChannel)
        assert isinstance(channel, LLMChannel)

    def test_default_channel_api_base(self, channel):
        """The channel should use the Qianfan API base by default."""
        assert channel.channel_api_base == "https://qianfan.baidubce.com/v2/"

    def test_initialize_returns_self(self, channel):
        """create_copy should return the channel itself."""
        assert channel.create_copy() is channel

    def test_channel_model_fields_default(self, channel):
        """Model-related fields should default to None."""
        assert channel.channel_model_name is None
        assert channel.channel_api_key is None
