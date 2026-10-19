# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_context_manager_manager.py
"""Unit tests for the ContextManagerManager component registry."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.context_manager_manager import ContextManagerManager
from agentuniverse.base.component.component_enum import ComponentEnum


def code(mgr, appname, name):
    return f"{appname}.{mgr._component_type.value.lower()}.{name}"


def make_manager(name="default_context_manager", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestContextManagerManager:
    """Test registration and lookup of context manager components."""

    def test_component_type_is_context_manager(self):
        mgr = ContextManagerManager()
        assert mgr._component_type == ComponentEnum.CONTEXT_MANAGER

    def test_register_and_get_existing_instance(self):
        mgr = ContextManagerManager()
        ctx = make_manager()
        mgr.register(code(mgr, "testapp", "default_context_manager"), ctx)
        got = mgr.get_instance_obj("default_context_manager", appname="testapp",
                                   new_instance=False)
        assert got is ctx

    def test_get_with_new_instance_returns_copy(self):
        mgr = ContextManagerManager()
        ctx = make_manager()
        mgr.register(code(mgr, "testapp", "default_context_manager"), ctx)
        assert mgr.get_instance_obj("default_context_manager", appname="testapp",
                                    new_instance=True) == "copied"

    def test_unregister_removes_instance(self):
        mgr = ContextManagerManager()
        key = code(mgr, "testapp", "default_context_manager")
        mgr.register(key, make_manager())
        mgr.unregister(key)
        assert key not in mgr.get_instance_name_list()

    def test_instance_name_list_reflects_registry(self):
        mgr = ContextManagerManager()
        key = code(mgr, "testapp", "default_context_manager")
        mgr.register(key, make_manager())
        assert mgr.get_instance_name_list() == [key]
