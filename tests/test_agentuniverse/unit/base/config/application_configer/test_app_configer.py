# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_app_configer.py

"""Unit tests for the AppConfiger application configuration."""

import math
from types import SimpleNamespace

from agentuniverse.base.config.application_configer.app_configer import \
    AppConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import \
    ToolConfiger


def sample_value():
    return {
        "BASE_INFO": {"appname": "demo_app"},
        "PACKAGE_PATH_INFO": {"ROOT_PACKAGE": "demo"},
        "CORE_PACKAGE": {"agent": ["pkg.agent"], "tool": ["pkg.tool"],
                         "default": ["pkg.default"]},
        "CONVERSATION_MEMORY": {"max_tokens": 100},
        "PLUGINS": {"llm_plugins": []},
    }


class TestAppConfigerDefaults:
    """Test default AppConfiger state."""

    def test_defaults(self):
        app_configer = AppConfiger()
        assert app_configer.base_info_appname is None
        assert app_configer.conversation_memory_configer == {}
        assert app_configer.tool_configer_map == {}
        assert app_configer.agent_llm_set == set()

    def test_map_setters(self):
        app_configer = AppConfiger()
        tool_configer = ToolConfiger()
        app_configer.tool_configer_map = {"t": tool_configer}
        assert app_configer.tool_configer_map["t"] is tool_configer


class TestAppConfigerLoad:
    """Test load_by_configer and plugin helpers."""

    def test_load_by_configer(self):
        app_configer = AppConfiger()
        configer = SimpleNamespace(value=sample_value())
        returned = app_configer.load_by_configer(configer)
        assert returned is app_configer
        assert app_configer.base_info_appname == "demo_app"
        assert app_configer.root_package_name == "demo"
        assert app_configer.core_agent_package_list == ["pkg.agent"]
        assert app_configer.core_default_package_list == ["pkg.default"]
        assert app_configer.conversation_memory_configer == {"max_tokens": 100}

    def test_load_llm_plugins(self):
        funcs = AppConfiger.load_llm_plugins(["math.sqrt"])
        assert funcs == [math.sqrt]

    def test_load_llm_plugins_empty(self):
        assert AppConfiger.load_llm_plugins([]) == []
