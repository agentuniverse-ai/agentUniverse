# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_log_type_enum.py

"""Unit tests for the LogTypeEnum."""

import pytest

from agentuniverse.base.util.logging.log_type_enum import LogTypeEnum


class TestLogTypeEnum:
    """Test LogTypeEnum members and values."""

    def test_member_values(self):
        assert LogTypeEnum.default == "default"
        assert LogTypeEnum.sls == "sls"
        assert LogTypeEnum.flask_request == "flask_request"
        assert LogTypeEnum.flask_response == "flask_response"
        assert LogTypeEnum.agent_input == "agent_input"
        assert LogTypeEnum.agent_invocation == "agent_invocation"
        assert LogTypeEnum.agent_first_token == "agent_first_token"
        assert LogTypeEnum.llm_input == "llm_input"
        assert LogTypeEnum.llm_invocation == "llm_invocation"
        assert LogTypeEnum.tool_input == "tool_input"
        assert LogTypeEnum.tool_invocation == "tool_invocation"

    def test_is_str_enum(self):
        assert issubclass(LogTypeEnum, str)
        assert isinstance(LogTypeEnum.default, str)

    def test_member_count(self):
        assert len(list(LogTypeEnum)) == 11

    def test_from_value(self):
        assert LogTypeEnum("tool_input") is LogTypeEnum.tool_input

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            LogTypeEnum("invalid")
