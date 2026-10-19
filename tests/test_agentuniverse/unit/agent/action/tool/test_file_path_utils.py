# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_file_path_utils.py
"""Unit tests for resolve_safe_path."""

import os

import pytest

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path


class TestResolveSafePath:
    def test_relative_path_resolves_under_base(self, tmp_path):
        resolved = resolve_safe_path('a.txt', str(tmp_path))
        assert resolved == os.path.realpath(str(tmp_path / 'a.txt'))

    def test_nested_relative_path(self, tmp_path):
        resolved = resolve_safe_path(os.path.join('sub', 'b.txt'), str(tmp_path))
        assert resolved == os.path.realpath(str(tmp_path / 'sub' / 'b.txt'))

    def test_absolute_path_inside_base(self, tmp_path):
        target = tmp_path / 'c.txt'
        resolved = resolve_safe_path(str(target), str(tmp_path))
        assert resolved == os.path.realpath(str(target))

    def test_parent_traversal_rejected(self, tmp_path):
        base = tmp_path / 'allowed'
        base.mkdir()
        with pytest.raises(ValueError, match='escapes'):
            resolve_safe_path('../secret.txt', str(base))

    def test_absolute_outside_base_rejected(self, tmp_path):
        outside = tmp_path / 'secret.txt'
        with pytest.raises(ValueError, match='escapes'):
            resolve_safe_path(str(outside), str(tmp_path / 'allowed'))

    def test_non_string_rejected(self, tmp_path):
        with pytest.raises(ValueError, match='non-empty string'):
            resolve_safe_path(123, str(tmp_path))

    def test_empty_path_rejected(self, tmp_path):
        with pytest.raises(ValueError, match='non-empty string'):
            resolve_safe_path('', str(tmp_path))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
