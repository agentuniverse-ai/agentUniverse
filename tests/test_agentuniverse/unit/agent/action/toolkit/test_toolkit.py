# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_toolkit.py

"""Unit tests for the Toolkit tool-collection component."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.toolkit.toolkit import Toolkit
from agentuniverse.base.component.component_enum import ComponentEnum


class TestToolkit:
    """Test Toolkit defaults, tool name listing and configer init."""

    def test_default_attributes(self):
        toolkit = Toolkit()
        assert toolkit.name == ""
        assert toolkit.description is None
        assert toolkit.include == []
        assert toolkit.component_type == ComponentEnum.TOOLKIT

    def test_constructor_accepts_fields(self):
        toolkit = Toolkit(name="tk", description="docs", include=["t1"])
        assert toolkit.name == "tk"
        assert toolkit.description == "docs"
        assert toolkit.include == ["t1"]

    def test_tool_names_returns_deep_copy(self):
        toolkit = Toolkit(include=["t1", "t2"])
        names = toolkit.tool_names
        names.append("t3")
        assert names == ["t1", "t2", "t3"]
        assert toolkit.include == ["t1", "t2"]

    def test_func_call_list_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            Toolkit().func_call_list

    def test_initialize_sets_fields_from_configer(self):
        toolkit = Toolkit()
        configer = SimpleNamespace(
            configer=SimpleNamespace(value={"metadata": {"k": 1}}),
            name="tk_name", description="tk desc", include=["tool1"])
        returned = toolkit.initialize_by_component_configer(configer)
        assert returned is toolkit
        assert toolkit.name == "tk_name"
        assert toolkit.description == "tk desc"
        assert toolkit.include == ["tool1"]

    def test_initialize_applies_configer_value_items(self):
        toolkit = Toolkit()
        configer = SimpleNamespace(
            configer=SimpleNamespace(
                value={"include": ["from_value"], "metadata": {"k": 1}}),
            name="tk_name", description=None, include=["from_attr"])
        toolkit.initialize_by_component_configer(configer)
        # configer.include attribute wins over the raw configer value map.
        assert toolkit.include == ["from_attr"]

    def test_initialize_handles_missing_attributes(self):
        toolkit = Toolkit(name="keep")
        configer = SimpleNamespace(
            configer=SimpleNamespace(value={"metadata": {"k": 1}}),
            name=None, description=None)
        toolkit.initialize_by_component_configer(configer)
        assert toolkit.name == "keep"
        assert toolkit.include == []
