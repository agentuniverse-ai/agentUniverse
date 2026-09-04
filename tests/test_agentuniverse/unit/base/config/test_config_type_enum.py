# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_config_type_enum.py

"""Unit tests for the ConfigTypeEnum."""

import pytest

from agentuniverse.base.config.config_type_enum import ConfigTypeEnum


class TestConfigTypeEnum:
    """Test ConfigTypeEnum members and values."""

    def test_member_values(self):
        assert ConfigTypeEnum.TOML.value == "toml"
        assert ConfigTypeEnum.YAML.value == "yaml"
        assert ConfigTypeEnum.JSON.value == "json"
        assert ConfigTypeEnum.XML.value == "xml"
        assert ConfigTypeEnum.PROPERTIES.value == "properties"
        assert ConfigTypeEnum.INI.value == "ini"
        assert ConfigTypeEnum.ENV.value == "env"

    def test_all_members(self):
        assert len(list(ConfigTypeEnum)) == 7

    def test_from_value(self):
        assert ConfigTypeEnum("yaml") is ConfigTypeEnum.YAML

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            ConfigTypeEnum("unknown")
