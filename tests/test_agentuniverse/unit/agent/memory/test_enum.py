# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:20
# @Author  : yuewang
# @FileName: test_enum.py
"""Unit tests for the agent memory enums."""

import pytest

from agentuniverse.agent.memory.enum import ChatMessageEnum, MemoryTypeEnum


class TestMemoryTypeEnum:
    """Test MemoryTypeEnum values."""

    def test_members(self):
        assert set(m.name for m in MemoryTypeEnum) == {'SHORT_TERM', 'LONG_TERM'}

    def test_values(self):
        assert MemoryTypeEnum.SHORT_TERM.value == 'short_term'
        assert MemoryTypeEnum.LONG_TERM.value == 'long_term'

    def test_lookup_and_error(self):
        assert MemoryTypeEnum('long_term') is MemoryTypeEnum.LONG_TERM
        with pytest.raises(ValueError):
            MemoryTypeEnum('mid_term')


class TestChatMessageEnum:
    """Test ChatMessageEnum values."""

    def test_members(self):
        assert set(m.name for m in ChatMessageEnum) == {
            'SYSTEM', 'HUMAN', 'AI', 'INPUT', 'OUTPUT', 'USER', 'ASSISTANT'
        }

    def test_values(self):
        assert ChatMessageEnum.SYSTEM.value == 'system'
        assert ChatMessageEnum.HUMAN.value == 'human'
        assert ChatMessageEnum.AI.value == 'ai'
        assert ChatMessageEnum.INPUT.value == 'input'
        assert ChatMessageEnum.OUTPUT.value == 'output'
        assert ChatMessageEnum.USER.value == 'user'
        assert ChatMessageEnum.ASSISTANT.value == 'assistant'

    def test_values_are_unique(self):
        values = [m.value for m in ChatMessageEnum]
        assert len(values) == len(set(values))

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ChatMessageEnum('robot')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
