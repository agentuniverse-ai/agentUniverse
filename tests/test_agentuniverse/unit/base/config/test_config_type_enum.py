# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/15 10:00
# @Author  : Yue Wang
# @FileName: test_config_type_enum.py
"""Unit tests for ConfigTypeEnum."""

import pytest

from agentuniverse.base.config.config_type_enum import ConfigTypeEnum


class TestConfigTypeEnum:
    """Test ConfigTypeEnum member values and lookups."""

    def test_expected_members_exist(self):
        """All documented configuration file types are present."""
        expected = {"TOML", "YAML", "JSON", "XML", "PROPERTIES", "INI", "ENV"}
        assert set(m.name for m in ConfigTypeEnum) == expected

    def test_member_values_are_lowercase_extensions(self):
        """Each value is the lowercase of its name."""
        for member in ConfigTypeEnum:
            assert member.value == member.name.lower()

    def test_specific_values(self):
        """Concrete values match the documented configuration extensions."""
        assert ConfigTypeEnum.TOML.value == "toml"
        assert ConfigTypeEnum.YAML.value == "yaml"
        assert ConfigTypeEnum.JSON.value == "json"
        assert ConfigTypeEnum.PROPERTIES.value == "properties"

    def test_from_value_lookup(self):
        """Members can be resolved from their string values."""
        assert ConfigTypeEnum("toml") is ConfigTypeEnum.TOML
        assert ConfigTypeEnum("properties") is ConfigTypeEnum.PROPERTIES
        assert ConfigTypeEnum("env") is ConfigTypeEnum.ENV

    def test_from_value_unknown_raises(self):
        """An unknown configuration type string raises ValueError."""
        with pytest.raises(ValueError):
            ConfigTypeEnum("csv")

    def test_values_are_unique(self):
        """No two members share the same value."""
        values = [m.value for m in ConfigTypeEnum]
        assert len(values) == len(set(values))
