# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_embedding_manager.py

"""Unit tests for the singleton EmbeddingManager registry."""

import pytest

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.embedding.embedding_manager \
    import EmbeddingManager
from agentuniverse.base.component.component_enum import ComponentEnum


class FakeEmbedding(Embedding):
    """A minimal concrete embedding used for registration tests."""

    def get_embeddings(self, texts, **kwargs):
        return [[1.0]] * len(texts)

    async def async_get_embeddings(self, texts, **kwargs):
        return [[1.0]] * len(texts)


@pytest.fixture
def manager():
    return EmbeddingManager()


@pytest.fixture
def embedding():
    return FakeEmbedding(name="test_embedding")


@pytest.fixture(autouse=True)
def clean_manager(manager):
    """Restore the singleton registry after every test."""
    baseline = set(manager.get_instance_name_list())
    yield
    for name in list(manager.get_instance_name_list()):
        if name not in baseline:
            manager.unregister(name)


class TestEmbeddingManager:
    """Test EmbeddingManager registry semantics."""

    def test_singleton_identity(self):
        assert EmbeddingManager() is EmbeddingManager()

    def test_component_type(self, manager):
        assert manager._component_type == ComponentEnum.EMBEDDING

    def test_register_and_list(self, manager, embedding):
        manager.register("e1", embedding)
        manager.register("e2", FakeEmbedding(name="other"))
        assert manager.get_instance_name_list() == ["e1", "e2"]
        assert manager.get_instance_obj_list()[-1].name == "other"

    def test_duplicate_register_keeps_first(self, manager, embedding):
        manager.register("e1", embedding)
        manager.register("e1", FakeEmbedding(name="replacement"))
        assert manager.get_instance_name_list() == ["e1"]
        assert manager.get_instance_obj_list()[0] is embedding

    def test_unregister_removes_instance(self, manager, embedding):
        manager.register("e1", embedding)
        manager.unregister("e1")
        assert manager.get_instance_name_list() == []

    def test_default_symbol_registers_default_instance(self, manager):
        default = FakeEmbedding(name="default_emb", default_symbol=True)
        manager.register("e1", default)
        assert "__default_instance__" in manager.get_instance_name_list()
        assert manager.get_default_instance() is default

    def test_non_default_symbol_skips_default_instance(self, manager,
                                                      embedding):
        manager.register("e1", embedding)
        assert "__default_instance__" not in manager.get_instance_name_list()
        assert manager.get_default_instance() is None
