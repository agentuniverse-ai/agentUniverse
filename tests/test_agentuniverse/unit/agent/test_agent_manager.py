# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @Author  : Yue Wang
# @FileName: test_agent_manager.py
"""Unit tests for the AgentManager component registry."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    """Return the singleton manager with an isolated instance map."""
    mgr = AgentManager()
    saved = dict(mgr._instance_obj_map)
    mgr._instance_obj_map.clear()
    yield mgr
    mgr._instance_obj_map.clear()
    mgr._instance_obj_map.update(saved)


def code(mgr, appname, name):
    return f"{appname}.{mgr._component_type.value.lower()}.{name}"


def make_agent(name="demo", default_symbol=False):
    return SimpleNamespace(default_symbol=default_symbol, name=name,
                           create_copy=lambda: "copied")


class TestAgentManager:
    """Test registration and lookup of agent components."""

    def test_singleton_returns_same_instance(self, manager):
        assert manager is AgentManager()

    def test_component_type_is_agent(self, manager):
        assert manager._component_type == ComponentEnum.AGENT

    def test_register_and_get_existing_instance(self, manager):
        agent = make_agent()
        manager.register(code(manager, "testapp", "demo"), agent)
        got = manager.get_instance_obj("demo", appname="testapp", new_instance=False)
        assert got is agent

    def test_get_with_new_instance_returns_copy(self, manager):
        agent = make_agent()
        manager.register(code(manager, "testapp", "demo"), agent)
        assert manager.get_instance_obj("demo", appname="testapp",
                                        new_instance=True) == "copied"

    def test_unregister_removes_instance(self, manager):
        agent = make_agent()
        key = code(manager, "testapp", "demo")
        manager.register(key, agent)
        manager.unregister(key)
        assert key not in manager.get_instance_name_list()

    def test_default_instance_is_registered(self, manager):
        agent = make_agent(default_symbol=True)
        manager.register(code(manager, "testapp", "demo"), agent)
        assert manager.get_default_instance() is agent
