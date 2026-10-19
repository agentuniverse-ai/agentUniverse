# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_rag_router.py

"""Unit tests for the RagRouter base routing class."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.rag_router.rag_router import RagRouter
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum


class StubRouter(RagRouter):
    """Concrete router that returns the full store list."""

    def _rag_route(self, query, store_list):
        return [(query, store) for store in store_list]


@pytest.fixture
def query():
    return Query(query_str="what is agent universe?", keywords={"agent"})


class TestRagRouter:
    """Test RagRouter defaults, delegation and configuration."""

    def test_default_attributes(self):
        router = RagRouter()
        assert router.name is None
        assert router.description is None
        assert router.component_type == ComponentEnum.RAG_ROUTER

    def test_rag_route_delegates_to_rag_route(self, query):
        router = StubRouter()
        result = router.rag_route(query, ["store_a", "store_b"])
        assert result == [(query, "store_a"), (query, "store_b")]
        assert all(pair[0] is query for pair in result)

    def test_base_rag_route_returns_none(self, query):
        # The abstract base implementation performs no routing.
        assert RagRouter().rag_route(query, ["store_a"]) is None

    def test_initialize_by_component_configer_sets_fields(self):
        router = StubRouter()
        configer = SimpleNamespace(name="renamed", description="new desc")
        returned = router.initialize_by_component_configer(configer)
        assert returned is router
        assert router.name == "renamed"
        assert router.description == "new desc"

    def test_initialize_skips_falsy_fields(self):
        router = StubRouter(name="keep", description="keep docs")
        router.initialize_by_component_configer(
            SimpleNamespace(name=None, description=""))
        assert router.name == "keep"
        assert router.description == "keep docs"

    def test_subclass_can_override_rag_route(self, query):
        class CustomRouter(RagRouter):
            def _rag_route(self, query, store_list):
                return [(query, "only") for _ in store_list]

        assert CustomRouter().rag_route(query, ["a", "b"]) == [
            (query, "only"), (query, "only")]
