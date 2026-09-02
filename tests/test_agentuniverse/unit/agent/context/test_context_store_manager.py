# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_context_store_manager.py
"""Unit tests for the ContextStoreManager component registry."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.context.context_store_manager import ContextStoreManager
from agentuniverse.base.component.component_enum import ComponentEnum


def code(mgr, appname, name):
    return f"{appname}.{mgr._component_type.value.lower()}.{name}"


def make_store(name="ram_context_store", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestContextStoreManager:
    """Test registration and lookup of context store components."""

    def test_component_type_is_context_store(self):
        mgr = ContextStoreManager()
        assert mgr._component_type == ComponentEnum.CONTEXT_STORE

    def test_register_and_get_existing_instance(self):
        mgr = ContextStoreManager()
        store = make_store()
        mgr.register(code(mgr, "testapp", "ram_context_store"), store)
        got = mgr.get_instance_obj("ram_context_store", appname="testapp",
                                   new_instance=False)
        assert got is store

    def test_get_with_new_instance_returns_copy(self):
        mgr = ContextStoreManager()
        store = make_store()
        mgr.register(code(mgr, "testapp", "ram_context_store"), store)
        assert mgr.get_instance_obj("ram_context_store", appname="testapp",
                                    new_instance=True) == "copied"

    def test_unregister_removes_instance(self):
        mgr = ContextStoreManager()
        key = code(mgr, "testapp", "ram_context_store")
        mgr.register(key, make_store())
        mgr.unregister(key)
        assert key not in mgr.get_instance_name_list()

    def test_instance_name_list_reflects_registry(self):
        mgr = ContextStoreManager()
        key = code(mgr, "testapp", "ram_context_store")
        mgr.register(key, make_store())
        assert mgr.get_instance_name_list() == [key]
