# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/12 10:00
# @Author  : yuewang
# @FileName: test_log_type_enum.py
"""Unit tests for the LogTypeEnum enumeration."""

import pytest

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestLogTypeEnum:
    """Test LogTypeEnum members and str-Enum behavior."""

    @pytest.fixture
    def member_map(self):
        """Map of enum member names to values."""
        return {item.name: item.value for item in LogTypeEnum}

    def test_members_cover_all_log_sources(self, member_map):
        """Every expected log type is registered."""
        assert member_map["default"] == "default"
        assert member_map["sls"] == "sls"
        assert member_map["flask_request"] == "flask_request"
        assert member_map["flask_response"] == "flask_response"
        assert member_map["agent_input"] == "agent_input"
        assert member_map["agent_first_token"] == "agent_first_token"
        assert member_map["llm_invocation"] == "llm_invocation"
        assert member_map["tool_invocation"] == "tool_invocation"

    def test_member_values_match_names(self, member_map):
        """Each member's value equals its name; count is fixed."""
        assert len(LogTypeEnum) == 11
        assert all(item.value == item.name for item in LogTypeEnum)

    def test_str_enum_accepts_plain_strings(self):
        """Members compare equal to their plain string values."""
        assert LogTypeEnum.agent_input == "agent_input"
        assert LogTypeEnum.llm_invocation.value == "llm_invocation"
        assert isinstance(LogTypeEnum.default, str)

    def test_from_value_roundtrip(self):
        """LogTypeEnum(value) resolves to the matching member."""
        for name in ("sls", "agent_invocation", "tool_input"):
            assert LogTypeEnum(name) is getattr(LogTypeEnum, name)

    def test_unknown_value_raises(self):
        """Constructing from an unknown string raises ValueError."""
        with pytest.raises(ValueError):
            LogTypeEnum("not_a_log_type")
