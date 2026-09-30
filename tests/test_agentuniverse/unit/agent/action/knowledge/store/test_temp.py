# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_temp.py

"""Unit tests for the BM25 demo utilities in agentuniverse store.temp."""

import contextlib
import io

import pytest

with contextlib.redirect_stdout(io.StringIO()):
    from agentuniverse.agent.action.knowledge.store.temp import (
        build_inverted_index,
        compute_bm25,
        corpus,
    )


@pytest.fixture
def inverted_index():
    return build_inverted_index(corpus)


class TestInvertedIndex:
    """Test build_inverted_index against the module demo corpus."""

    def test_query_term_maps_to_matching_documents(self, inverted_index):
        assert 0 in inverted_index["自然语言"]
        assert 2 in inverted_index["自然语言"]
        assert 1 not in inverted_index["自然语言"]

    def test_every_document_appears_at_least_once(self, inverted_index):
        seen = set()
        for doc_ids in inverted_index.values():
            seen.update(doc_ids)
        assert seen == set(range(len(corpus)))


class TestComputeBm25:
    """Test compute_bm25 scoring properties."""

    def test_non_matching_document_scores_zero(self, inverted_index):
        assert compute_bm25("自然语言处理", 1, corpus, inverted_index) == 0

    def test_matching_documents_score_positive(self, inverted_index):
        assert compute_bm25("自然语言处理", 0, corpus, inverted_index) > 0
        assert compute_bm25("自然语言处理", 2, corpus, inverted_index) > 0

    def test_best_match_is_ranked_first(self, inverted_index):
        scores = [compute_bm25("自然语言处理", i, corpus, inverted_index)
                  for i in range(len(corpus))]
        assert max(scores) == scores[0]

    def test_absent_query_term_scores_zero(self, inverted_index):
        assert compute_bm25("zzzqqq", 0, corpus, inverted_index) == 0

    def test_score_is_deterministic(self, inverted_index):
        assert (compute_bm25("自然语言处理", 0, corpus, inverted_index)
                == compute_bm25("自然语言处理", 0, corpus, inverted_index))
