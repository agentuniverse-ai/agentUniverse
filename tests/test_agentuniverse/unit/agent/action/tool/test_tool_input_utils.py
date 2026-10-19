# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_tool_input_utils.py
"""Unit tests for parse_strict_bool in tool_input_utils."""

import pytest

from agentuniverse.agent.action.tool.common_tool.tool_input_utils import parse_strict_bool


class TestParseStrictBool:
    def test_none_returns_default(self):
        assert parse_strict_bool(None, 'flag') is False
        assert parse_strict_bool(None, 'flag', default=True) is True

    def test_bool_passthrough(self):
        assert parse_strict_bool(True, 'flag') is True
        assert parse_strict_bool(False, 'flag') is False

    def test_true_strings(self):
        for value in ('true', '1', 'yes', 'y', 'on', ' TRUE ', 'ON'):
            assert parse_strict_bool(value, 'flag') is True

    def test_false_strings(self):
        for value in ('false', '0', 'no', 'n', 'off', 'False'):
            assert parse_strict_bool(value, 'flag') is False

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError, match='flag'):
            parse_strict_bool('maybe', 'flag')

    def test_numeric_zero_one(self):
        assert parse_strict_bool(1, 'flag') is True
        assert parse_strict_bool(0.0, 'flag') is False

    def test_invalid_numeric_raises(self):
        with pytest.raises(ValueError):
            parse_strict_bool(2, 'flag')

    def test_other_types_raise(self):
        with pytest.raises(ValueError):
            parse_strict_bool(['true'], 'flag')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
