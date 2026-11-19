# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/01/01 10:00
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_enum.py
"""Unit tests for PromptProcessEnum."""

import pytest

from agentuniverse.prompt.enum import PromptProcessEnum


class TestPromptProcessEnum:
    def test_member_values(self):
        assert PromptProcessEnum.TRUNCATE.value == 'truncate'
        assert PromptProcessEnum.STUFF.value == 'stuff'
        assert PromptProcessEnum.MAP_REDUCE.value == 'map_reduce'

    def test_from_value(self):
        assert PromptProcessEnum.from_value('truncate') is PromptProcessEnum.TRUNCATE

    def test_from_value_case_insensitive(self):
        assert PromptProcessEnum.from_value('STUFF') is PromptProcessEnum.STUFF
        assert PromptProcessEnum.from_value('Map_Reduce') is PromptProcessEnum.MAP_REDUCE

    def test_from_value_unknown_raises(self):
        with pytest.raises(ValueError, match='No enum member'):
            PromptProcessEnum.from_value('unknown')

    def test_iteration_order(self):
        assert [m.value for m in PromptProcessEnum] == ['truncate', 'stuff', 'map_reduce']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
