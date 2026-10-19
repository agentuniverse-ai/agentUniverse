# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for agentuniverse.base.util.system_util."""

import os

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.system_util import (
    get_module_path, is_api_key_missing, is_system_builtin, parse_dynamic_str,
    process_dict_with_funcs, process_yaml_func,
)


class _YamlFuncExtension:
    """Stand-in for the yaml func extension object."""
    @staticmethod
    def load_key(name: str) -> str:
        return f"resolved-{name}"


class _Component:
    """Stand-in exposing component_type and component_config_path."""
    def __init__(self, component_type=None, component_config_path=None):
        self.component_type = component_type
        self.component_config_path = component_config_path


class TestParseDynamicStr:
    """Tests for parse_dynamic_str."""
    def test_plain_or_unimportable_values_pass_through(self):
        assert parse_dynamic_str("not-a-function") == "not-a-function"
        assert parse_dynamic_str("no.such.module.func") == "no.such.module.func"
    def test_callable_module_attribute_is_invoked(self):
        assert parse_dynamic_str("sys.getdefaultencoding") == "utf-8"


class TestGetModulePath:
    """Tests for get_module_path."""
    def test_builds_dotted_module_path(self, tmp_path):
        base = tmp_path / "root_pkg" / "sub"
        base.mkdir(parents=True)
        (base / "demo_agent.yaml").write_text("name: demo")
        (base / "demo_agent.py").write_text("# demo")
        assert get_module_path(str(base / "demo_agent.yaml"), "root_pkg") == "root_pkg.sub.demo_agent"
    def test_missing_py_file_raises(self, tmp_path):
        base = tmp_path / "root_pkg"
        base.mkdir(parents=True)
        (base / "demo_agent.yaml").write_text("name: demo")
        with pytest.raises(FileNotFoundError):
            get_module_path(str(base / "demo_agent.yaml"), "root_pkg")


class TestProcessYamlFunc:
    """Tests for process_yaml_func."""
    def test_resolves_method_call_on_instance(self):
        instance = _YamlFuncExtension()
        assert process_yaml_func('@FUNC(load_key("qwen"))', instance) == "resolved-qwen"
    def test_non_call_expression_raises_value_error(self):
        with pytest.raises(ValueError, match="Expected a function call"):
            process_yaml_func("@FUNC(plain_name)", _YamlFuncExtension())
    def test_unclosed_expression_passes_through(self):
        assert process_yaml_func("@FUNC(load_key(", _YamlFuncExtension()) == "@FUNC(load_key("


class TestProcessDictWithFuncs:
    """Tests for process_dict_with_funcs."""
    def test_resolves_nested_func_expressions(self):
        instance = _YamlFuncExtension()
        result = process_dict_with_funcs(
            {"a": '@FUNC(load_key("one"))', "nested": {"b": '@FUNC(load_key("two"))'}, "c": 3},
            instance,
        )
        assert result == {"a": "resolved-one", "nested": {"b": "resolved-two"}, "c": 3}
    def test_none_instance_returns_input_unchanged(self):
        value = {"a": '@FUNC(load_key("one"))'}
        assert process_dict_with_funcs(value, None) == value


class TestSystemPredicates:
    """Tests for is_system_builtin and is_api_key_missing."""
    def test_is_system_builtin_matches_known_system_paths(self):
        assert is_system_builtin(None) is False
        llm = _Component(ComponentEnum.LLM, os.path.join("agentuniverse", "llm", "default", "x.yaml"))
        tool = _Component(ComponentEnum.TOOL, os.path.join("agentuniverse", "agent", "action", "tool", "y.yaml"))
        custom = _Component(ComponentEnum.LLM, os.path.join("my", "llm", "z.yaml"))
        assert is_system_builtin(llm) is True
        assert is_system_builtin(tool) is True
        assert is_system_builtin(custom) is False
    def test_is_api_key_missing_checks_empty_attribute(self):
        assert is_api_key_missing(object(), "api_key_name") is False
        assert is_api_key_missing(_Component(component_config_path=""), "component_config_path") is True
        assert is_api_key_missing(_Component(component_config_path="cfg"), "component_config_path") is False
