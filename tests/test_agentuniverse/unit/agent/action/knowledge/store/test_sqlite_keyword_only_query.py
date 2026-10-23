"""Keyword-only retrieval must produce real BM25 scores without query text."""

import sqlite3

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.fixture
def store(monkeypatch):
    connection = sqlite3.connect(":memory:")
    instance = SQLiteStore(conn=connection)
    instance._create_tables()
    # Documents in these tests already have keywords; replace only the
    # managed keyword-extractor lookup, preserving real indexing and Jieba BM25.
    monkeypatch.setattr(instance, "_get_document_keyword", lambda doc: doc.keywords)
    yield instance
    connection.close()


@pytest.mark.parametrize("query_text", [None, "", " \t\n"])
@pytest.mark.parametrize("term,filler", [("alpha", "beta gamma delta"), ("苹果", "香蕉 西瓜 梨子")])
def test_keyword_only_query_returns_ranked_matches(store, monkeypatch, query_text, term, filler):
    store.insert_document([
        Document(id="dense", text=f"{term} {term} {term}", keywords={term}),
        Document(id="sparse", text=f"{term} {filler}", keywords={term}),
        Document(id="unrelated", text="unrelated", keywords={"unrelated"}),
    ])
    original_scorer = SQLiteStore.compute_bm25
    scores = {}

    def record_scores(instance, query, text, *args):
        value = original_scorer(instance, query, text, *args)
        scores[text] = value
        return value

    monkeypatch.setattr(SQLiteStore, "compute_bm25", record_scores)
    query = Query(query_str=query_text, keywords={term})
    result = store.query(query)
    assert [doc.id for doc in result] == ["dense", "sparse"]
    assert len(scores) == 2
    assert all(score > 0 for score in scores.values())
    assert query.query_str == query_text
    assert query.keywords == {term}


def test_nonempty_query_text_remains_the_scoring_source(store, monkeypatch):
    store.insert_document([
        Document(id="alpha", text="alpha alpha alpha", keywords={"alpha"}),
        Document(id="beta", text="beta beta beta", keywords={"beta"}),
    ])
    original_scorer = SQLiteStore.compute_bm25
    scores = {}

    def record_scores(instance, query, text, *args):
        value = original_scorer(instance, query, text, *args)
        scores[text] = value
        return value

    monkeypatch.setattr(SQLiteStore, "compute_bm25", record_scores)
    result = store.query(Query(query_str="beta", keywords={"alpha", "beta"}))
    assert result[0].id == "beta"
    assert scores["alpha alpha alpha"] == 0
    assert scores["beta beta beta"] > 0


def test_unmatched_keywords_return_empty_without_query_text(store):
    store.insert_document([Document(text="alpha", keywords={"alpha"})])
    assert store.query(Query(keywords={"missing"})) == []
