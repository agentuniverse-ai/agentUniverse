# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_llm_channel_manager.py
"""Unit tests for the LLMChannelManager component registry."""

from types import SimpleNamespace

import pytest

from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.llm.llm_channel.llm_channel_manager import LLMChannelManager


@pytest.fixture
def manager():
    """Return the singleton manager with an isolated instance map."""
    mgr = LLMChannelManager()
    saved = dict(mgr._instance_obj_map)
    mgr._instance_obj_map.clear()
    yield mgr
    mgr._instance_obj_map.clear()
    mgr._instance_obj_map.update(saved)


def code(mgr, appname, name):
    return f"{appname}.{mgr._component_type.value.lower()}.{name}"


def make_channel(name="demo", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestLLMChannelManager:
    """Test registration and lookup of LLM channel components."""

    def test_singleton_returns_same_instance(self, manager):
        assert manager is LLMChannelManager()

    def test_component_type_is_llm_channel(self, manager):
        assert manager._component_type == ComponentEnum.LLM_CHANNEL

    def test_register_and_get_existing_instance(self, manager):
        channel = make_channel()
        manager.register(code(manager, "testapp", "demo"), channel)
        got = manager.get_instance_obj("demo", appname="testapp", new_instance=False)
        assert got is channel

    def test_get_with_new_instance_returns_copy(self, manager):
        channel = make_channel()
        manager.register(code(manager, "testapp", "demo"), channel)
        assert manager.get_instance_obj("demo", appname="testapp",
                                        new_instance=True) == "copied"

    def test_unregister_removes_instance(self, manager):
        channel = make_channel()
        key = code(manager, "testapp", "demo")
        manager.register(key, channel)
        manager.unregister(key)
        assert key not in manager.get_instance_name_list()

    def test_instance_name_list_reflects_registry(self, manager):
        key_a = code(manager, "testapp", "a")
        key_b = code(manager, "testapp", "b")
        manager.register(key_a, make_channel())
        manager.register(key_b, make_channel())
        names = manager.get_instance_name_list()
        assert key_a in names
        assert key_b in names
