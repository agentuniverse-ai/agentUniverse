# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_enum.py

"""Unit tests for the ToolTypeEnum."""

import pytest

from agentuniverse.agent.action.tool.enum import ToolTypeEnum


class TestToolTypeEnum:
    """Test ToolTypeEnum members and values."""

    def test_members_and_values(self):
        assert ToolTypeEnum.API.value == "api"
        assert ToolTypeEnum.MCP.value == "mcp"
        assert ToolTypeEnum.FUNC.value == "func"

    def test_member_names(self):
        assert ToolTypeEnum.API.name == "API"
        assert ToolTypeEnum.MCP.name == "MCP"
        assert ToolTypeEnum.FUNC.name == "FUNC"

    def test_all_members(self):
        assert list(ToolTypeEnum) == [ToolTypeEnum.API, ToolTypeEnum.MCP,
                                      ToolTypeEnum.FUNC]

    def test_values_are_unique(self):
        values = [member.value for member in ToolTypeEnum]
        assert len(values) == len(set(values))

    def test_construct_from_value(self):
        assert ToolTypeEnum("api") is ToolTypeEnum.API
        assert ToolTypeEnum("mcp") is ToolTypeEnum.MCP
        assert ToolTypeEnum("func") is ToolTypeEnum.FUNC

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ToolTypeEnum("invalid")

    def test_str_representation(self):
        assert str(ToolTypeEnum.API) == "ToolTypeEnum.API"
        assert repr(ToolTypeEnum.MCP) == "<ToolTypeEnum.MCP: 'mcp'>"
