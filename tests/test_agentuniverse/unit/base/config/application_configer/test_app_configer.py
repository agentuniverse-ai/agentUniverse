# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_app_configer.py
"""Unit tests for AppConfiger."""

import pytest

from agentuniverse.base.config.application_configer.app_configer import AppConfiger


class _FakeConfiger:
    """Minimal stand-in for Configer exposing a plain ``value`` dict."""

    def __init__(self, value):
        self.value = value


class TestAppConfiger:
    """Test AppConfiger construction, loading and properties."""

    @pytest.fixture
    def app_configer(self):
        """Create a fresh AppConfiger instance."""
        return AppConfiger()

    def test_constructor_defaults(self, app_configer):
        """Fresh instance has None package lists and empty collections."""
        assert app_configer.base_info_appname is None
        assert app_configer.root_package_name is None
        assert app_configer.core_agent_package_list is None
        assert app_configer.core_llm_package_list is None
        assert app_configer.core_memory_package_list is None
        assert app_configer.core_work_pattern_package_list is None
        assert app_configer.conversation_memory_configer == {}
        assert app_configer.agent_llm_set == set()
        assert app_configer.agent_toolkit_set == set()
        assert app_configer.yaml_func_instance is None

    def test_load_by_configer_reads_sections(self):
        """load_by_configer populates properties from the configer value."""
        value = {
            'BASE_INFO': {'appname': 'demo_app'},
            'PACKAGE_PATH_INFO': {'ROOT_PACKAGE': 'demo_package'},
            'CORE_PACKAGE': {'default': ['p1', 'p2'], 'agent': ['a1'], 'llm': None},
            'CONVERSATION_MEMORY': {'enabled': True},
            'PLUGINS': {'llm_plugins': []},
        }
        app_configer = AppConfiger().load_by_configer(_FakeConfiger(value))
        assert app_configer.base_info_appname == 'demo_app'
        assert app_configer.root_package_name == 'demo_package'
        assert app_configer.core_default_package_list == ['p1', 'p2']
        assert app_configer.core_agent_package_list == ['a1']
        assert app_configer.core_llm_package_list is None
        assert app_configer.conversation_memory_configer == {'enabled': True}
        assert app_configer.llm_plugins == []

    def test_load_by_configer_missing_keys(self):
        """load_by_configer tolerates an empty configuration value."""
        app_configer = AppConfiger().load_by_configer(_FakeConfiger({}))
        assert app_configer.base_info_appname is None
        assert app_configer.core_agent_package_list is None
        assert app_configer.conversation_memory_configer == {}
        assert app_configer.llm_plugins == []

    def test_load_by_configer_returns_self(self):
        """load_by_configer is chainable and returns the same instance."""
        app_configer = AppConfiger()
        assert app_configer.load_by_configer(_FakeConfiger({})) is app_configer

    def test_load_llm_plugins_imports_callables(self):
        """load_llm_plugins resolves dotted module.attribute references."""
        funcs = AppConfiger.load_llm_plugins(['agentuniverse.base.annotation.singleton.singleton'])
        assert len(funcs) == 1
        assert callable(funcs[0])
        assert funcs[0].__name__ == 'singleton'

    def test_yaml_func_instance_setter(self, app_configer):
        """yaml_func_instance setter stores the assigned value."""
        app_configer.yaml_func_instance = 'some_yaml_func'
        assert app_configer.yaml_func_instance == 'some_yaml_func'
