# -*- coding: utf-8 -*-
"""Unit tests for agentuniverse.base.util.env_util."""

import pytest

from agentuniverse.base.util.env_util import get_from_env


class TestGetFromEnv:
    """Tests for the get_from_env helper function."""

    def test_returns_value_when_env_set(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "hello")
        assert get_from_env("AU_TEST_KEY") == "hello"

    def test_returns_none_when_env_missing(self, monkeypatch):
        monkeypatch.delenv("AU_TEST_KEY", raising=False)
        assert get_from_env("AU_TEST_KEY") is None

    def test_returns_none_when_env_is_empty(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "")
        assert get_from_env("AU_TEST_KEY") is None

    def test_returns_whitespace_value(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "   ")
        assert get_from_env("AU_TEST_KEY") == "   "

    def test_returns_numeric_string_value(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "0")
        assert get_from_env("AU_TEST_KEY") == "0"

    def test_preserves_other_env_variables(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "value")
        monkeypatch.setenv("AU_OTHER_KEY", "other")
        assert get_from_env("AU_TEST_KEY") == "value"
        assert get_from_env("AU_OTHER_KEY") == "other"

    def test_returns_none_after_env_is_removed(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_KEY", "value")
        assert get_from_env("AU_TEST_KEY") == "value"
        monkeypatch.delenv("AU_TEST_KEY")
        assert get_from_env("AU_TEST_KEY") is None
