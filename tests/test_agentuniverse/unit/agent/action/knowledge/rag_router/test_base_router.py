# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_base_router.py

"""Unit tests for the BaseRouter pass-through router."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.rag_router.base_router import \
    BaseRouter
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def router():
    return BaseRouter(name="base", description="base docs")


@pytest.fixture
def query():
    return Query(query_str="what is agent universe?", keywords={"agent"})


class TestBaseRouter:
    """Test BaseRouter routing and configuration behavior."""

    def test_default_attributes(self):
        router = BaseRouter()
        assert router.name is None
        assert router.description is None
        assert router.component_type == ComponentEnum.RAG_ROUTER

    def test_rag_route_returns_all_stores_in_order(self, router, query):
        result = router.rag_route(query, ["store_a", "store_b", "store_c"])
        assert result == [(query, "store_a"), (query, "store_b"),
                          (query, "store_c")]
        assert all(pair[0] is query for pair in result)

    def test_rag_route_with_empty_store_list(self, router, query):
        assert router.rag_route(query, []) == []

    def test_rag_route_preserves_duplicate_store_names(self, router, query):
        result = router.rag_route(query, ["store_a", "store_a"])
        assert result == [(query, "store_a"), (query, "store_a")]

    def test_initialize_by_component_configer_sets_fields(self, router):
        configer = SimpleNamespace(name="renamed", description="new desc")
        returned = router.initialize_by_component_configer(configer)
        assert returned is router
        assert router.name == "renamed"
        assert router.description == "new desc"

    def test_initialize_skips_falsy_fields(self):
        router = BaseRouter(name="keep", description="keep docs")
        configer = SimpleNamespace(name=None, description="")
        router.initialize_by_component_configer(configer)
        assert router.name == "keep"
        assert router.description == "keep docs"

    def test_subclass_inherits_base_routing(self, query):
        class CustomRouter(BaseRouter):
            pass

        router = CustomRouter()
        assert router.rag_route(query, ["only_store"]) == [
            (query, "only_store")]
