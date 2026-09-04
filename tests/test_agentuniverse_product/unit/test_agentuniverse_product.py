# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/23 17:49
# @Author  : Yue Wang
# @Email   : 1939455790@qq.com
# @FileName: test_agentuniverse_product.py

"""Unit tests for the AgentUniverseProduct bootstrap class."""

import sys
import pytest

from agentuniverse_product.agentuniverse_product import AgentUniverseProduct


@pytest.fixture
def product():
    return AgentUniverseProduct()


class TestAgentUniverseProduct:
    """Tests for singleton behavior and pure helper logic."""

    def test_singleton_returns_same_instance(self):
        assert AgentUniverseProduct() is AgentUniverseProduct()

    def test_singleton_is_shared_with_fixture(self, product):
        assert AgentUniverseProduct() is product

    def test_add_to_sys_path_appends_existing_dir(self, product, tmp_path):
        (tmp_path / "platform").mkdir()
        path_str = str(tmp_path / "platform")
        try:
            product._add_to_sys_path(tmp_path, ["platform"])
            assert path_str in sys.path
        finally:
            if path_str in sys.path:
                sys.path.remove(path_str)

    def test_add_to_sys_path_skips_missing_dir(self, product, tmp_path):
        (tmp_path / "platform").mkdir()
        present = str(tmp_path / "platform")
        missing = str(tmp_path / "app")
        try:
            product._add_to_sys_path(tmp_path, ["platform", "app"])
            assert present in sys.path
            assert missing not in sys.path
        finally:
            if present in sys.path:
                sys.path.remove(present)

    def test_add_to_sys_path_with_empty_sub_dirs(self, product, tmp_path):
        before = list(sys.path)
        product._add_to_sys_path(tmp_path, [])
        assert sys.path == before
