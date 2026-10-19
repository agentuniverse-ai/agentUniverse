# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_store.py

"""Unit tests for the abstract Store knowledge-store base class."""

import asyncio
from types import SimpleNamespace
from unittest import mock

import pytest

import agentuniverse.agent.action.knowledge.store.store as store_module
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum


@pytest.fixture
def store():
    return Store(name="store_a", description="store a docs")


@pytest.fixture
def query():
    return Query(query_str="what is agent universe?", keywords={"agent"})


class TestStore:
    """Test Store defaults, abstract API and configer initialization."""

    def test_default_attributes(self):
        store = Store()
        assert store.name is None
        assert store.description is None
        assert store.component_type == ComponentEnum.STORE
        assert store.client is None
        assert store.async_client is None

    def test_query_raises_not_implemented(self, store, query):
        with pytest.raises(NotImplementedError):
            store.query(query)

    def test_insert_and_upsert_raise_not_implemented(self, store):
        with pytest.raises(NotImplementedError):
            store.insert_document([])
        with pytest.raises(NotImplementedError):
            store.upsert_document([])
        with pytest.raises(NotImplementedError):
            store.update_document([])
        with pytest.raises(NotImplementedError):
            store.delete_document("doc_1")

    def test_async_api_raises_not_implemented(self, store, query):
        with pytest.raises(NotImplementedError):
            asyncio.run(store.async_query(query))
        with pytest.raises(NotImplementedError):
            asyncio.run(store.async_insert_document([]))

    def test_create_copy_returns_self(self, store):
        assert store.create_copy() is store

    def test_initialize_by_component_configer(self):
        store = Store()
        with mock.patch.object(store_module, "add_post_fork") as add_post_fork:
            configer = SimpleNamespace(name="renamed", description="new docs")
            returned = store.initialize_by_component_configer(configer)
        assert returned is store
        assert store.name == "renamed"
        assert store.description == "new docs"
        assert add_post_fork.call_count == 2

    def test_initialize_skips_falsy_fields(self):
        store = Store(name="keep", description="keep docs")
        with mock.patch.object(store_module, "add_post_fork"):
            store.initialize_by_component_configer(
                SimpleNamespace(name=None, description=""))
        assert store.name == "keep"
        assert store.description == "keep docs"
