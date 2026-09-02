# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 12:20
# @Author  : yuewang
# @FileName: test_llm_channel_manager.py
"""Unit tests for LLMChannelManager."""

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.llm_channel.llm_channel_manager import LLMChannelManager


@pytest.fixture
def manager():
    """Return the LLMChannelManager singleton."""
    return LLMChannelManager()


class TestLLMChannelManager:
    """Test LLMChannelManager registration behavior."""

    def test_singleton(self, manager):
        assert manager is LLMChannelManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.LLM_CHANNEL

    def test_register_and_get(self, manager):
        channel = LLMChannel()
        channel.channel_name = 'ch1'
        manager.register('app.llm_channel.ch1', channel)
        assert manager.get_instance_obj('ch1', appname='app', new_instance=False) is channel

    def test_get_unknown_returns_none(self, manager):
        assert manager.get_instance_obj('absent_ch_xyz', appname='app') is None

    def test_get_unknown_strict_raises(self, manager):
        with pytest.raises(ValueError, match='is not registered'):
            manager.get_instance_obj('absent_ch_xyz', appname='app', strict=True)

    def test_unregister(self, manager):
        manager.register('app.llm_channel.ch2', LLMChannel())
        manager.unregister('app.llm_channel.ch2')
        assert manager.get_instance_obj('ch2', appname='app') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
