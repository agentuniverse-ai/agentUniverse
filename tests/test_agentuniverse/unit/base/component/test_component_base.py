# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Unit tests for the ComponentBase component base class."""

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class _StubConfiger:
    """Stub component configer exposing the attributes used by ComponentBase."""

    default_symbol = True


class TestComponentBase:
    """Tests for the ComponentBase class."""

    def test_default_field_values(self):
        component = ComponentBase(component_type=ComponentEnum.LLM)
        assert component.component_type is ComponentEnum.LLM
        assert component.component_config_path is None
        assert component.default_symbol is False

    def test_component_config_path_is_stored(self):
        component = ComponentBase(
            component_type=ComponentEnum.TOOL,
            component_config_path="configs/tool.yaml",
        )
        assert component.component_config_path == "configs/tool.yaml"

    def test_is_default_object_reflects_default_symbol(self):
        component = ComponentBase(component_type=ComponentEnum.AGENT)
        assert component.is_default_object() is False
        component.default_symbol = True
        assert component.is_default_object() is True

    def test_initialize_by_component_configer_sets_default_symbol(self):
        component = ComponentBase(component_type=ComponentEnum.LLM)
        result = component.initialize_by_component_configer(_StubConfiger())
        assert result is component
        assert component.default_symbol is True

    def test_initialize_by_component_configer_without_default_symbol(self):
        component = ComponentBase(component_type=ComponentEnum.LLM)

        class PlainConfiger:
            pass

        component.initialize_by_component_configer(PlainConfiger())
        assert component.default_symbol is False

    def test_create_copy_is_deep_copy(self):
        component = ComponentBase(component_type=ComponentEnum.AGENT)
        component.default_symbol = True
        copy = component.create_copy()
        assert copy is not component
        assert copy.default_symbol is True
        assert copy.component_type is ComponentEnum.AGENT

    def test_create_copy_is_independent(self):
        component = ComponentBase(component_type=ComponentEnum.MEMORY)
        copy = component.create_copy()
        copy.default_symbol = True
        assert component.default_symbol is False
