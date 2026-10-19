# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : Yue Wang
# @FileName: test_component_base.py
"""Unit tests for ComponentBase."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum


class TestComponentBase:
    """Test ComponentBase model defaults and helpers."""

    @pytest.fixture
    def component(self):
        """Create a minimal ComponentBase instance."""
        return ComponentBase(component_type=ComponentEnum.LLM)

    def test_model_defaults(self, component):
        """Optional fields fall back to documented defaults."""
        assert component.component_type == ComponentEnum.LLM
        assert component.component_config_path is None
        assert component.default_symbol is False

    def test_is_default_object_false(self, component):
        """A plain instance is not a default object."""
        assert component.is_default_object() is False

    def test_create_copy_is_independent(self, component):
        """create_copy returns a separate, equal instance."""
        component.component_config_path = "some/path.yaml"
        copy = component.create_copy()
        assert copy is not component
        assert copy.component_config_path == "some/path.yaml"
        assert copy.component_type == ComponentEnum.LLM

    def test_initialize_copies_default_symbol(self, component):
        """default_symbol from a configer is transferred to the component."""
        configer = SimpleNamespace(default_symbol=True)
        result = component.initialize_by_component_configer(configer)
        assert result is component
        assert component.is_default_object() is True

    def test_initialize_without_symbol_attribute(self, component):
        """Configer without default_symbol leaves the component unchanged."""
        configer = SimpleNamespace()
        component.initialize_by_component_configer(configer)
        assert component.default_symbol is False

    def test_get_instance_code_uses_app_name(self):
        """Instance code is appname.component_type.name in lowercase type."""

        class NamedComponent(ComponentBase):
            """ComponentBase subclass that declares a name field."""

            name: str = "anon"

        component = NamedComponent(component_type=ComponentEnum.LLM, name="test_llm")
        with patch(
            "agentuniverse.base.component.component_base.ApplicationConfigManager"
        ) as manager_cls:
            manager_cls.return_value.app_configer.base_info_appname = "demo_app"
            code = component.get_instance_code()
        assert code == "demo_app.llm.test_llm"
