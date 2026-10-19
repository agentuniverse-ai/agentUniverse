# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:20
# @Author  : kaichuan
# @FileName: test_configer.py
"""Unit tests for Configer in base.config.configer."""

import pytest

from agentuniverse.base.config.configer import Configer, PlaceholderResolver


class TestConfiger:
    """Test Configer loading and value access."""

    def test_defaults(self):
        """A fresh Configer has no path and an empty value dict."""
        configer = Configer()
        assert configer.path is None
        assert configer.value == {}

    def test_path_and_value_setters(self):
        """The path and value properties accept assignments."""
        configer = Configer()
        configer.path = "some/path.yaml"
        configer.value = {"a": 1}
        assert configer.path == "some/path.yaml"
        assert configer.value == {"a": 1}

    def test_load_yaml_file(self, tmp_path):
        """load_by_path parses a YAML file into value and returns self."""
        file = tmp_path / "cfg.yaml"
        file.write_text("name: demo\nnested:\n  key: value\n", encoding="utf-8")
        configer = Configer()
        result = configer.load_by_path(str(file))
        assert result is configer
        assert configer.value["name"] == "demo"
        assert configer.value["nested"]["key"] == "value"

    def test_load_toml_file(self, tmp_path):
        """load_by_path parses a TOML file into value and returns self."""
        file = tmp_path / "cfg.toml"
        file.write_text('name = "demo"\n', encoding="utf-8")
        configer = Configer()
        assert configer.load_by_path(str(file)) is configer
        assert configer.value == {"name": "demo"}

    def test_unsupported_format_raises(self, tmp_path):
        """A file with an unsupported extension raises ValueError."""
        file = tmp_path / "cfg.txt"
        file.write_text("name=demo", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported file format: txt"):
            Configer().load_by_path(str(file))

    def test_load_uses_configured_path(self, tmp_path):
        """load() loads the path given to the constructor."""
        file = tmp_path / "cfg.yaml"
        file.write_text("key: from-path\n", encoding="utf-8")
        configer = Configer(path=str(file))
        configer.load()
        assert configer.get("key") == "from-path"

    def test_get_set_to_dict(self):
        """get/set/to_dict operate on the stored value dict."""
        configer = Configer()
        assert configer.get("missing") is None
        assert configer.get("missing", "fallback") == "fallback"
        configer.set("k", [1, 2])
        assert configer.get("k") == [1, 2]
        assert configer.to_dict() is configer.value


class TestPlaceholderResolver:
    """Test placeholder resolution in config values."""

    def test_root_package_placeholder(self):
        """${ROOT_PACKAGE} resolves to the configured root package name."""
        resolver = PlaceholderResolver()
        resolver.set_root_package_name("my_pkg")
        assert resolver.resolve({"m": "agentuniverse.agent.x"}) == {"m": "agentuniverse.agent.x"}
        assert resolver.resolve("${ROOT_PACKAGE}.agent") == "my_pkg.agent"

    def test_nested_structure_resolution(self):
        """Placeholders inside nested dicts and lists are resolved."""
        resolver = PlaceholderResolver()
        resolver.set_root_package_name("pkg")
        data = {"a": ["${ROOT_PACKAGE}.x", "plain"], "b": {"c": "${ROOT_PACKAGE}.y"}}
        assert resolver.resolve(data) == {"a": ["pkg.x", "plain"], "b": {"c": "pkg.y"}}
