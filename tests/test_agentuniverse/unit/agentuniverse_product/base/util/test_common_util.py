# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_common_util.py

"""Unit tests for the product common_util helpers."""

import pytest

from agentuniverse_product.base.util.common_util import is_component_id_unique


class TestIsComponentIdUnique:
    """Test the component id uniqueness guard."""

    def test_none_id_is_unique(self):
        assert is_component_id_unique(None, "TOOL") is True

    def test_none_type_is_unique(self):
        assert is_component_id_unique("t1", None) is True

    def test_none_both_is_unique(self):
        assert is_component_id_unique(None, None) is True

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError):
            is_component_id_unique("t1", "NOT_A_TYPE")
