# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_configer.py

"""Unit tests for the Configer configuration loader."""

import os
import tempfile

import pytest

from agentuniverse.base.config.configer import Configer, PlaceholderResolver


class TestConfigerBasics:
    """Test the plain dict-backed Configer API."""

    def test_default_state(self):
        configer = Configer()
        assert configer.path is None
        assert configer.value == {}
        assert configer.get("missing") is None
        assert configer.get("missing", 42) == 42
        assert configer.to_dict() == {}

    def test_set_get_roundtrip(self):
        configer = Configer()
        configer.set("a", 1)
        configer.set("b", {"c": 2})
        assert configer.get("a") == 1
        assert configer.get("b") == {"c": 2}
        assert configer.to_dict() == {"a": 1, "b": {"c": 2}}

    def test_path_and_value_setters(self):
        configer = Configer()
        configer.path = "/tmp/app.yaml"
        assert configer.path == "/tmp/app.yaml"
        configer.value = {"k": "v"}
        assert configer.value == {"k": "v"}


class TestConfigerFileLoad:
    """Test loading config files."""

    def test_load_yaml_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml",
                                         delete=False) as f:
            f.write("name: demo\nitems:\n  - 1\n  - 2\n")
            path = f.name
        try:
            configer = Configer(path)
            loaded = configer.load()
            assert loaded is configer
            assert configer.value == {"name": "demo", "items": [1, 2]}
        finally:
            os.unlink(path)

    def test_unsupported_file_format_raises(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as f:
            f.write("{}")
            path = f.name
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                Configer(path).load()
        finally:
            os.unlink(path)


class TestPlaceholderResolver:
    """Test env placeholder resolution."""

    def test_env_placeholder(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_ENV_VAR", "hello")
        resolver = PlaceholderResolver()
        assert resolver.resolve("x-${AU_TEST_ENV_VAR}") == "x-hello"

    def test_missing_env_placeholder_becomes_empty(self):
        assert PlaceholderResolver().resolve("${AU_NOPE_VAR}") == ""

    def test_dict_and_list_resolution(self, monkeypatch):
        monkeypatch.setenv("AU_TEST_ENV_VAR", "v")
        resolver = PlaceholderResolver()
        assert resolver.resolve({"a": "${AU_TEST_ENV_VAR}"}) == {"a": "v"}
        assert resolver.resolve(["${AU_TEST_ENV_VAR}"]) == ["v"]

    def test_non_string_values_passthrough(self):
        resolver = PlaceholderResolver()
        assert resolver.resolve(42) == 42
        assert resolver.resolve(None) is None
