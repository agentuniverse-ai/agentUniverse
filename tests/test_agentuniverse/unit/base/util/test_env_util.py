# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_env_util.py
"""Unit tests for the environment variable helper."""

import os

import pytest

from agentuniverse.base.util.env_util import get_from_env


class TestEnvUtil:
    """Test get_from_env lookups against os.environ."""

    def test_returns_set_value(self, monkeypatch):
        """A populated environment variable is returned as-is."""
        monkeypatch.setenv("AU_TEST_ENV", "hello")
        assert get_from_env("AU_TEST_ENV") == "hello"

    def test_missing_key_returns_none(self, monkeypatch):
        """A key absent from the environment yields None."""
        monkeypatch.delenv("AU_TEST_MISSING", raising=False)
        assert get_from_env("AU_TEST_MISSING") is None

    def test_empty_value_returns_none(self, monkeypatch):
        """An empty string is treated as unset."""
        monkeypatch.setenv("AU_TEST_EMPTY", "")
        assert get_from_env("AU_TEST_EMPTY") is None

    @pytest.mark.parametrize(
        "value",
        ["0", "false", "a b c", "中文", "12345"],
    )
    def test_nonempty_values_pass_through(self, monkeypatch, value):
        """Any non-empty value is returned unchanged."""
        monkeypatch.setenv("AU_TEST_PASS", value)
        assert get_from_env("AU_TEST_PASS") == value

    def test_does_not_mutate_environment(self, monkeypatch):
        """Reading a variable leaves the environment untouched."""
        monkeypatch.setenv("AU_TEST_STABLE", "kept")
        before = dict(os.environ)
        get_from_env("AU_TEST_STABLE")
        get_from_env("AU_TEST_NOT_THERE")
        assert dict(os.environ) == before
