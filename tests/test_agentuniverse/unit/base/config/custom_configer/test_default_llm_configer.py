# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_default_llm_configer.py
"""Unit tests for DefaultLLMConfiger."""

import pytest

from agentuniverse.base.config.custom_configer.default_llm_configer import DefaultLLMConfiger


@pytest.fixture
def raw_class():
    """Return the class before the singleton decorator wraps it."""
    return DefaultLLMConfiger.__wrapped__


class TestDefaultLLMConfiger:
    """Test DefaultLLMConfiger singleton and TOML loading behavior."""

    def test_class_attribute_default(self):
        """The class-level default_llm attribute starts as None."""
        assert DefaultLLMConfiger.default_llm is None

    def test_singleton_returns_same_instance(self):
        """The decorated class always returns the same instance."""
        first = DefaultLLMConfiger()
        second = DefaultLLMConfiger()
        assert first is second

    def test_default_instance_has_empty_value(self):
        """An instance created without a config path has an empty value."""
        instance = DefaultLLMConfiger()
        assert instance.value == {}
        assert instance.default_llm is None

    def test_loads_toml_default_llm(self, raw_class, tmp_path):
        """A TOML config file populates default_llm from the DEFAULT section."""
        config_path = tmp_path / "default_llm.toml"
        config_path.write_text("[DEFAULT]\ndefault_llm = 'qwen-max'\n")
        instance = raw_class(str(config_path))
        assert instance.default_llm == 'qwen-max'
        assert instance.value.get('DEFAULT', {}).get('default_llm') == 'qwen-max'

    def test_missing_config_file_does_not_raise(self, raw_class, tmp_path, capsys):
        """A missing config path is tolerated with a printed warning."""
        missing = tmp_path / "no_such_file.toml"
        instance = raw_class(str(missing))
        captured = capsys.readouterr()
        assert 'Configuration file not found' in captured.out
        assert instance.default_llm is None

    def test_config_without_default_section(self, raw_class, tmp_path):
        """A TOML file without a DEFAULT section leaves default_llm None."""
        config_path = tmp_path / "other.toml"
        config_path.write_text("[OTHER]\nkey = 'value'\n")
        instance = raw_class(str(config_path))
        assert instance.default_llm is None
        assert instance.value == {'OTHER': {'key': 'value'}}
