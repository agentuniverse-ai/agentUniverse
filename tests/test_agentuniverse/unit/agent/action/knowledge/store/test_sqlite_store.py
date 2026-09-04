# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_sqlite_store.py

"""Unit tests for SQLiteStore pure behaviors (no database connection)."""

from types import SimpleNamespace
from unittest import mock

import pytest

import agentuniverse.agent.action.knowledge.store.store as store_module
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.fixture
def store():
    return SQLiteStore()


class TestSQLiteStore:
    """Test SQLiteStore defaults, BM25 scoring and configer init."""

    def test_default_attributes(self, store):
        assert store.db_path == "sqlite_store.db"
        assert store.conn is None
        assert store.k1 == 1.5
        assert store.b == 0.75
        assert store.keyword_extractor is None
        assert store.similarity_top_k == 10

    def test_compute_bm25_positive_for_matching_term(self, store):
        inverted_index = {"hello": ["d1"], "world": ["d1"]}
        score = store.compute_bm25("hello", "hello world", inverted_index,
                                   total_doc_count=1, total_word_count=3)
        assert score > 0

    def test_compute_bm25_zero_for_missing_term(self, store):
        inverted_index = {"hello": ["d1"]}
        score = store.compute_bm25("absent_term", "hello world",
                                   inverted_index,
                                   total_doc_count=1, total_word_count=3)
        assert score == 0

    def test_compute_bm25_is_deterministic(self, store):
        inverted_index = {"hello": ["d1"], "world": ["d1"]}
        args = ("hello world", "hello world", inverted_index, 1, 3)
        assert store.compute_bm25(*args) == store.compute_bm25(*args)

    def test_compute_bm25_prefers_more_frequent_term(self, store):
        inverted_index = {"hello": ["d1"]}
        single = store.compute_bm25("hello", "hello world",
                                    inverted_index,
                                    total_doc_count=1, total_word_count=3)
        double = store.compute_bm25("hello", "hello hello world",
                                    inverted_index,
                                    total_doc_count=1, total_word_count=4)
        assert double > single

    def test_initialize_by_component_configer(self, store):
        configer = SimpleNamespace(
            name="sqlite", description="sqlite docs",
            db_path=":memory:", k1=2.0, b=0.5,
            keyword_extractor="sentence_keyword_extractor",
            similarity_top_k=3)
        with mock.patch.object(store_module, "add_post_fork"):
            store.initialize_by_component_configer(configer)
        assert store.name == "sqlite"
        assert store.db_path == ":memory:"
        assert store.k1 == 2.0
        assert store.b == 0.5
        assert store.keyword_extractor == "sentence_keyword_extractor"
        assert store.similarity_top_k == 3

    def test_to_documents_handles_none(self):
        assert SQLiteStore.to_documents(None) == []
