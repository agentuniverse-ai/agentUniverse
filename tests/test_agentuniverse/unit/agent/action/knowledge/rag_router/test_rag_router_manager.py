# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_rag_router_manager.py

"""Unit tests for the singleton RagRouterManager registry."""

import pytest

from agentuniverse.agent.action.knowledge.rag_router.base_router import \
    BaseRouter
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager \
    import RagRouterManager
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def manager():
    return RagRouterManager()


@pytest.fixture
def router():
    return BaseRouter(name="test_router", description="router docs")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    """Restore the singleton registry after every test."""
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestRagRouterManager:
    """Test RagRouterManager registry semantics."""

    def test_singleton_identity(self):
        assert RagRouterManager() is RagRouterManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.RAG_ROUTER

    def test_register_and_list(self, manager, router):
        manager.register("r1", router)
        manager.register("r2", BaseRouter(name="other"))
        assert manager.get_instance_name_list() == ["r1", "r2"]
        assert manager.get_instance_obj_list()[-1].name == "other"

    def test_duplicate_register_keeps_first(self, manager, router):
        manager.register("r1", router)
        manager.register("r1", BaseRouter(name="replacement"))
        assert manager.get_instance_name_list() == ["r1"]
        assert manager.get_instance_obj_list()[0] is router

    def test_unregister_removes_instance(self, manager, router):
        manager.register("r1", router)
        manager.unregister("r1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = BaseRouter(name="default_router", default_symbol=True)
        manager.register("r1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager, router):
        manager.register("r1", router)
        assert "__default_instance__" not in manager.get_instance_name_list()
        assert manager.get_default_instance() is None

    def test_get_instance_obj_list_returns_registered_objects(self, manager,
                                                              router):
        manager.register("r1", router)
        assert manager.get_instance_obj_list() == [router]
