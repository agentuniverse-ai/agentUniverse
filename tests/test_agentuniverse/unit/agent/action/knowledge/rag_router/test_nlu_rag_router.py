# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_nlu_rag_router.py

"""Unit tests for NluRagRouter with the routing agent fully mocked."""

import json
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router \
    as nlu_module
from agentuniverse.agent.action.knowledge.rag_router.nlu_rag_router \
    import NluRagRouter
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum


class FakeAgent:
    def __init__(self, output):
        self.output = output
        self.agent_model = SimpleNamespace(profile={})
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs
        return SimpleNamespace(output=self.output)


class FakeStore:
    def __init__(self, name, description):
        self.name = name
        self.description = description


@contextmanager
def mock_services(agent, stores):
    with patch.object(nlu_module, "AgentManager") as agent_mgr, \
            patch.object(nlu_module, "StoreManager") as store_mgr:
        agent_mgr.return_value.get_instance_obj.return_value = agent
        store_mgr.return_value.get_instance_obj.side_effect = \
            stores.__getitem__
        yield agent


@pytest.fixture
def query():
    return Query(query_str="what is agent universe?", keywords={"agent"})


@pytest.fixture
def stores():
    return {"store_a": FakeStore("store_a", "store a docs"),
            "store_b": FakeStore("store_b", "store b docs")}


class TestNluRagRouter:
    def test_default_attributes(self):
        router = NluRagRouter()
        assert router.llm is None
        assert router.agent_name == "nlu_rag_route_agent"
        assert router.store_amount == 1
        assert router.component_type == ComponentEnum.RAG_ROUTER

    def test_routes_selected_stores_in_order(self, query, stores):
        with mock_services(FakeAgent("store_b,store_a"), stores) as agent:
            result = NluRagRouter(store_amount=2).rag_route(
                query, ["store_a", "store_b"])
        assert result == [(query, "store_b"), (query, "store_a")]
        assert all(pair[0] is query for pair in result)

    def test_store_amount_truncates_agent_output(self, query, stores):
        with mock_services(FakeAgent("store_a,store_b"), stores):
            result = NluRagRouter().rag_route(query, ["store_a", "store_b"])
        assert result == [(query, "store_a")]

    def test_unknown_stores_are_filtered_out(self, query, stores):
        with mock_services(FakeAgent("store_a,unknown_store"), stores):
            result = NluRagRouter(store_amount=2).rag_route(query, ["store_a"])
        assert result == [(query, "store_a")]

    def test_all_unknown_output_returns_empty(self, query, stores):
        with mock_services(FakeAgent("nonexistent"), stores):
            result = NluRagRouter(store_amount=2).rag_route(query, ["store_a"])
        assert result == []

    def test_agent_run_receives_query_and_store_info(self, query, stores):
        with mock_services(FakeAgent("store_a"), stores) as agent:
            NluRagRouter().rag_route(query, ["store_a", "store_b"])
        assert agent.run_kwargs["query"] == query.query_str
        assert agent.run_kwargs["store_amount"] == 1
        assert json.loads(agent.run_kwargs["store_info"]) == {
            "store_a": "store a docs", "store_b": "store b docs"}

    def test_configured_llm_updates_agent_profile(self, query, stores):
        llm_config = {"model_name": "gpt-4o", "temperature": 0}
        with mock_services(FakeAgent("store_a"), stores) as agent:
            NluRagRouter(llm=llm_config).rag_route(query, ["store_a"])
        assert agent.agent_model.profile["llm_model"] == llm_config

    def test_initialize_by_component_configer(self):
        router = NluRagRouter()
        configer = SimpleNamespace(name="nlu_router", description="desc",
                                   llm={"model_name": "gpt-4o"},
                                   agent_name="custom_agent",
                                   store_amount=3)
        router.initialize_by_component_configer(configer)
        assert router.name == "nlu_router"
        assert router.description == "desc"
        assert router.llm == {"model_name": "gpt-4o"}
        assert router.agent_name == "custom_agent"
        assert router.store_amount == 3
