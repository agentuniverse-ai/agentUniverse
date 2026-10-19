# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/10 11:55
# @Author  : yuewang
# @FileName: test_enum.py
"""Unit tests for PromptProcessEnum."""

import pytest

from agentuniverse.prompt.enum import PromptProcessEnum


class TestPromptProcessEnum:
    """Test PromptProcessEnum members and lookup."""

    def test_members(self):
        assert set(m.name for m in PromptProcessEnum) == {
            'TRUNCATE', 'STUFF', 'MAP_REDUCE'
        }

    def test_values(self):
        assert PromptProcessEnum.TRUNCATE.value == 'truncate'
        assert PromptProcessEnum.STUFF.value == 'stuff'
        assert PromptProcessEnum.MAP_REDUCE.value == 'map_reduce'

    def test_from_value_exact(self):
        assert PromptProcessEnum.from_value('stuff') is PromptProcessEnum.STUFF

    def test_from_value_case_insensitive(self):
        assert PromptProcessEnum.from_value('MAP_REDUCE') is PromptProcessEnum.MAP_REDUCE
        assert PromptProcessEnum.from_value('Truncate') is PromptProcessEnum.TRUNCATE

    def test_from_value_invalid_raises(self):
        with pytest.raises(ValueError, match='No enum member'):
            PromptProcessEnum.from_value('bogus')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
