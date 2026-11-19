# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/08 10:00
# @Author  : test
# @FileName: test_enum.py
"""Unit tests for the conversation_memory enum module."""

import pytest

from agentuniverse.agent.memory.conversation_memory.enum import (
    ConversationMessageEnum,
    ConversationMessageSourceType,
)


class TestConversationMessageEnum:
    """Tests for ConversationMessageEnum."""

    @pytest.fixture
    def expected(self):
        """Mapping of member name to member value."""
        return {"INPUT": "input", "OUTPUT": "output"}

    def test_member_values(self, expected):
        """Test every member holds its declared value."""
        for name, value in expected.items():
            assert getattr(ConversationMessageEnum, name).value == value

    def test_member_count(self):
        """Test the enum only contains the declared members."""
        assert len(ConversationMessageEnum) == 2

    def test_lookup_by_value(self, expected):
        """Test ConversationMessageEnum(value) returns the right member."""
        for name, value in expected.items():
            assert ConversationMessageEnum(value) is getattr(ConversationMessageEnum, name)

    def test_lookup_by_name(self, expected):
        """Test ConversationMessageEnum[name] returns the right member."""
        for name in expected:
            assert ConversationMessageEnum[name] is getattr(ConversationMessageEnum, name)

    def test_values_are_unique(self, expected):
        """Test no two members share the same value."""
        values = [member.value for member in ConversationMessageEnum]
        assert values == list(expected.values())
        assert len(values) == len(set(values))


class TestConversationMessageSourceType:
    """Tests for ConversationMessageSourceType."""

    @pytest.fixture
    def expected(self):
        """Mapping of member name to member value."""
        return {"AGENT": "agent", "TOOL": "tool", "KNOWLEDGE": "knowledge",
                "LLM": "llm", "USER": "user"}

    def test_member_values(self, expected):
        """Test every member holds its declared value."""
        for name, value in expected.items():
            assert getattr(ConversationMessageSourceType, name).value == value

    def test_member_count(self):
        """Test the enum only contains the declared members."""
        assert len(ConversationMessageSourceType) == 5

    def test_lookup_and_roundtrip(self, expected):
        """Test lookup by value/name and that values are unique."""
        values = []
        for name, value in expected.items():
            member = getattr(ConversationMessageSourceType, name)
            assert ConversationMessageSourceType(value) is member
            assert ConversationMessageSourceType[name] is member
            values.append(value)
        assert len(values) == len(set(values))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
