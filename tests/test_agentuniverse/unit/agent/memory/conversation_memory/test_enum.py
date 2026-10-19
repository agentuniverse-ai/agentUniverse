# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 10:05
# @Author  : yuewang
# @FileName: test_enum.py
"""Unit tests for conversation_memory enum definitions."""

import pytest

from agentuniverse.agent.memory.conversation_memory.enum import (
    ConversationMessageEnum,
    ConversationMessageSourceType,
)


class TestConversationMessageEnum:
    """Test ConversationMessageEnum values and uniqueness."""

    def test_expected_members(self):
        assert set(m.name for m in ConversationMessageEnum) == {'INPUT', 'OUTPUT'}

    def test_values(self):
        assert ConversationMessageEnum.INPUT.value == 'input'
        assert ConversationMessageEnum.OUTPUT.value == 'output'

    def test_lookup_by_value(self):
        assert ConversationMessageEnum('input') is ConversationMessageEnum.INPUT
        assert ConversationMessageEnum('output') is ConversationMessageEnum.OUTPUT

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ConversationMessageEnum('unknown')

    def test_values_are_unique(self):
        values = [m.value for m in ConversationMessageEnum]
        assert len(values) == len(set(values))


class TestConversationMessageSourceType:
    """Test ConversationMessageSourceType values."""

    def test_expected_members(self):
        assert set(m.name for m in ConversationMessageSourceType) == {
            'AGENT', 'TOOL', 'KNOWLEDGE', 'LLM', 'USER'
        }

    def test_values(self):
        assert ConversationMessageSourceType.AGENT.value == 'agent'
        assert ConversationMessageSourceType.TOOL.value == 'tool'
        assert ConversationMessageSourceType.KNOWLEDGE.value == 'knowledge'
        assert ConversationMessageSourceType.LLM.value == 'llm'
        assert ConversationMessageSourceType.USER.value == 'user'

    def test_lookup_by_value(self):
        for member in ConversationMessageSourceType:
            assert ConversationMessageSourceType(member.value) is member


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
