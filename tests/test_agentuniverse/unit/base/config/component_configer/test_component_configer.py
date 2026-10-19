# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_component_configer.py

"""Unit tests for the ComponentConfiger."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer


def make_configer(value, path="configs/x.yaml"):
    return SimpleNamespace(value=value, path=path)


class TestComponentConfiger:
    """Test component configuration loading and accessors."""

    def test_default_state(self):
        configer = ComponentConfiger()
        assert configer.configer is None
        assert configer.metadata_type is None
        assert configer.metadata_module is None
        assert configer.metadata_class is None
        assert configer.meta_class is None

    def test_load_by_configer_with_metadata(self):
        component_configer = ComponentConfiger()
        value = {"name": "demo", "metadata": {"type": "agent",
                                              "module": "mod.a",
                                              "class": "DemoAgent"}}
        returned = component_configer.load_by_configer(make_configer(value))
        assert returned is component_configer
        assert component_configer.metadata_type == "agent"
        assert component_configer.metadata_module == "mod.a"
        assert component_configer.metadata_class == "DemoAgent"
        assert component_configer.__dict__.get("name") == "demo"

    def test_prompt_path_defaults_type_to_prompt(self):
        component_configer = ComponentConfiger()
        component_configer.load_by_configer(make_configer({}, path="a/prompt/b.yaml"))
        assert component_configer.metadata_type == "PROMPT"

    def test_meta_class_resolution(self):
        component_configer = ComponentConfiger()
        value = {"meta_class": "agentuniverse.agent.action.tool.api_tool.APITool"}
        component_configer.load_by_configer(make_configer(value))
        assert component_configer.get_component_config_type() == "TOOL"

    def test_meta_class_empty_uses_metadata_type(self):
        component_configer = ComponentConfiger()
        value = {"metadata": {"type": "knowledge", "module": "m",
                              "class": "C"}}
        component_configer.load_by_configer(make_configer(value))
        assert component_configer.get_component_config_type() == "knowledge"

    def test_invalid_value_raises(self):
        component_configer = ComponentConfiger()
        with pytest.raises(Exception, match="Failed to parse"):
            component_configer.load_by_configer(
                make_configer(None, path=None))

    def test_setters_roundtrip(self):
        component_configer = ComponentConfiger()
        component_configer.metadata_module = "m"
        component_configer.metadata_class = "C"
        assert component_configer.metadata_module == "m"
        assert component_configer.metadata_class == "C"
