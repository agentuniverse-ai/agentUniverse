# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_enum.py
"""Unit tests for the memory enums defined in agent.memory.enum."""

import pytest

from agentuniverse.agent.memory.enum import ChatMessageEnum, MemoryTypeEnum


class TestMemoryEnums:
    """Test the MemoryTypeEnum and ChatMessageEnum definitions."""

    @pytest.fixture
    def expected_memory_types(self):
        """Return the expected (member name, member value) pairs."""
        return [("SHORT_TERM", "short_term"), ("LONG_TERM", "long_term")]

    def test_memory_type_member_values(self, expected_memory_types):
        """Test the declared value of every MemoryTypeEnum member."""
        for name, value in expected_memory_types:
            member = getattr(MemoryTypeEnum, name)
            assert member.value == value
            assert isinstance(member, MemoryTypeEnum)

    def test_memory_type_members_and_uniqueness(self, expected_memory_types):
        """Test the member names and value uniqueness of MemoryTypeEnum."""
        assert len(MemoryTypeEnum) == 2
        assert {member.name for member in MemoryTypeEnum} == {pair[0] for pair in expected_memory_types}
        assert len({member.value for member in MemoryTypeEnum}) == len(MemoryTypeEnum)

    def test_chat_message_member_values(self):
        """Test the declared value of every ChatMessageEnum member."""
        expected = {
            "SYSTEM": "system",
            "HUMAN": "human",
            "AI": "ai",
            "INPUT": "input",
            "OUTPUT": "output",
            "USER": "user",
            "ASSISTANT": "assistant",
        }
        assert {member.name: member.value for member in ChatMessageEnum} == expected

    def test_chat_message_member_uniqueness(self):
        """Test that all ChatMessageEnum members share unique values."""
        assert len(ChatMessageEnum) == 7
        assert len({member.value for member in ChatMessageEnum}) == len(ChatMessageEnum)

    def test_lookup_by_value(self):
        """Test resolving an enum member from its string value."""
        assert MemoryTypeEnum("long_term") is MemoryTypeEnum.LONG_TERM
        assert MemoryTypeEnum("short_term") is MemoryTypeEnum.SHORT_TERM
        assert ChatMessageEnum("human") is ChatMessageEnum.HUMAN
        assert ChatMessageEnum("assistant") is ChatMessageEnum.ASSISTANT

    def test_invalid_value_raises(self):
        """Test that unknown values raise a ValueError."""
        with pytest.raises(ValueError):
            MemoryTypeEnum("unknown")
        with pytest.raises(ValueError):
            ChatMessageEnum("tool")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
