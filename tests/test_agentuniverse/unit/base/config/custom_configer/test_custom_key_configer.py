# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/13 10:00
# @Author  : kaichuan
# @FileName: test_custom_key_configer.py
"""Unit tests for CustomKeyConfiger."""

import os

import pytest

import agentuniverse.base.config.custom_configer.custom_key_configer as ck_module
from agentuniverse.base.config.custom_configer.custom_key_configer import (
    CustomKeyConfiger,
)


def _instances_dict() -> dict:
    """Return the private singleton registry held in the decorator closure."""
    for cell in ck_module.CustomKeyConfiger.__closure__:
        try:
            contents = cell.cell_contents
        except ValueError:  # empty cell
            continue
        if isinstance(contents, dict):
            return contents
    raise AssertionError("singleton registry dict not found in closure")


@pytest.fixture(autouse=True)
def reset_singleton():
    """Give each test a fresh singleton instance."""
    registry = _instances_dict()
    registry.clear()
    yield
    registry.clear()


class TestCustomKeyConfiger:
    """Test CustomKeyConfiger singleton and key-loading behavior."""

    def test_singleton_returns_same_instance(self):
        """Repeated construction returns the same instance."""
        first = CustomKeyConfiger()
        second = CustomKeyConfiger()
        assert first is second

    def test_no_path_starts_with_empty_value(self):
        """Constructed without a path, the value map is empty."""
        configer = CustomKeyConfiger()
        assert configer.value == {}

    def test_missing_file_skips_load_without_error(self, tmp_path):
        """A missing config file is skipped rather than raised."""
        missing = tmp_path / "does_not_exist.yaml"
        configer = CustomKeyConfiger(str(missing))
        assert configer.value == {}

    def test_key_list_exported_to_environment(self, tmp_path, monkeypatch):
        """Entries under KEY_LIST are copied into os.environ."""
        monkeypatch.setenv("CK_TEST_KEY", "original")
        path = tmp_path / "keys.yaml"
        path.write_text("KEY_LIST:\n  CK_TEST_KEY: secret_value\n")
        configer = CustomKeyConfiger(str(path))
        assert os.environ.get("CK_TEST_KEY") == "secret_value"
        assert configer.value["KEY_LIST"]["CK_TEST_KEY"] == "secret_value"

    def test_inherited_get_returns_default(self):
        """The inherited Configer.get honors its default argument."""
        configer = CustomKeyConfiger()
        assert configer.get("missing_key", 123) == 123


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
