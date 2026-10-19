# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_llm_manager.py
"""Unit tests for the LLMManager component registry behavior."""

from types import SimpleNamespace

import pytest

from agentuniverse.llm.llm_manager import LLMManager


@pytest.fixture
def manager():
    """Return the singleton manager with an isolated instance map."""
    mgr = LLMManager()
    saved = dict(mgr._instance_obj_map)
    mgr._instance_obj_map.clear()
    yield mgr
    mgr._instance_obj_map.clear()
    mgr._instance_obj_map.update(saved)


def make_obj(name="demo", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestLLMManager:
    """Test registration and lookup of LLM components."""

    def test_singleton_returns_same_instance(self, manager):
        assert manager is LLMManager()

    def test_register_and_get_existing_instance(self, manager):
        obj = make_obj()
        manager.register("testapp.llm.demo", obj)
        assert manager.get_instance_obj("demo", appname="testapp",
                                        new_instance=False) is obj

    def test_get_with_new_instance_returns_copy(self, manager):
        obj = make_obj()
        manager.register("testapp.llm.demo", obj)
        assert manager.get_instance_obj("demo", appname="testapp",
                                        new_instance=True) == "copied"

    def test_default_instance_is_returned(self, manager):
        obj = make_obj(default_symbol=True)
        manager.register("testapp.llm.demo", obj)
        assert manager.get_default_instance() is obj
        assert manager.get_instance_obj("__default_instance__",
                                        new_instance=False) is obj

    def test_unregister_removes_instance(self, manager):
        obj = make_obj()
        manager.register("testapp.llm.demo", obj)
        manager.unregister("testapp.llm.demo")
        assert "testapp.llm.demo" not in manager.get_instance_name_list()

    def test_instance_name_list_reflects_registry(self, manager):
        manager.register("testapp.llm.a", make_obj())
        manager.register("testapp.llm.b", make_obj())
        names = manager.get_instance_name_list()
        assert "testapp.llm.a" in names
        assert "testapp.llm.b" in names
