# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_query_paraphraser_manager.py
"""Unit tests for QueryParaphraserManager (offline singleton/pool logic)."""

import pytest

from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser import \
    QueryParaphraser
from agentuniverse.agent.action.knowledge.query_paraphraser.query_paraphraser_manager import \
    QueryParaphraserManager
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import ComponentManagerBase

_APPNAME = "test_app"


class _FakeParaphraser(QueryParaphraser):
    """Concrete paraphraser used to fill the manager pool."""

    def query_paraphrase(self, origin_query: Query) -> Query:
        return origin_query


def _code(name: str) -> str:
    """Return the full instance code used by the manager pool."""
    return f"{_APPNAME}.query_paraphraser.{name}"


class TestQueryParaphraserManager:
    """Test registration behavior of the singleton manager offline."""

    @pytest.fixture
    def manager(self, monkeypatch):
        """Return the singleton with an in-memory pool reset per test."""
        mgr = QueryParaphraserManager()
        monkeypatch.setattr(mgr, "_instance_obj_map", {})
        return mgr

    def test_singleton_identity(self):
        """Repeated instantiations return the very same manager object."""
        assert QueryParaphraserManager() is QueryParaphraserManager()

    def test_manager_type_and_component(self, manager):
        """Manager targets QUERY_PARAPHRASER components with an empty pool."""
        assert isinstance(manager, ComponentManagerBase)
        assert manager._component_type == ComponentEnum.QUERY_PARAPHRASER
        assert manager.get_instance_name_list() == []
        assert manager.get_instance_obj_list() == []

    def test_register_and_get_instance(self, manager):
        """Registered components are retrievable from the pool."""
        paraphraser = _FakeParaphraser(name="p1")

        manager.register(_code("p1"), paraphraser)

        assert manager.get_instance_name_list() == [_code("p1")]
        got = manager.get_instance_obj("p1", appname=_APPNAME, new_instance=False)
        assert got is paraphraser

    def test_get_instance_returns_copy_by_default(self, manager):
        """Default get_instance_obj returns an independent copy."""
        paraphraser = _FakeParaphraser(name="p1")
        manager.register(_code("p1"), paraphraser)

        got = manager.get_instance_obj("p1", appname=_APPNAME)

        assert got is not paraphraser
        assert got.name == "p1"

    def test_register_duplicate_keeps_first_instance(self, manager):
        """Re-registering the same code does not overwrite the first object."""
        first = _FakeParaphraser(name="p1")
        second = _FakeParaphraser(name="p1")
        manager.register(_code("p1"), first)

        manager.register(_code("p1"), second)

        assert manager.get_instance_name_list() == [_code("p1")]
        got = manager.get_instance_obj("p1", appname=_APPNAME, new_instance=False)
        assert got is first

    def test_register_default_symbol_sets_default(self, manager):
        """default_symbol components are also stored as the default instance."""
        default_qp = _FakeParaphraser(name="default_qp", default_symbol=True)

        manager.register(_code("default_qp"), default_qp)

        names = set(manager.get_instance_name_list())
        assert names == {_code("default_qp"), "__default_instance__"}
        assert manager.get_default_instance() is default_qp

    def test_unregister_and_strict_get_raises(self, manager):
        """Unregistered names raise a descriptive ValueError when strict."""
        manager.register(_code("p1"), _FakeParaphraser(name="p1"))

        manager.unregister(_code("p1"))

        assert manager.get_instance_name_list() == []
        with pytest.raises(ValueError, match="not registered"):
            manager.get_instance_obj("p1", appname=_APPNAME, strict=True)
