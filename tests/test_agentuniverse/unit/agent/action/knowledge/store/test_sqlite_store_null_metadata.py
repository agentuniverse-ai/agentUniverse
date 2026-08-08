#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sqlite3

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def test_query_supports_documents_without_metadata():
    store = SQLiteStore()
    store.conn = sqlite3.connect(":memory:")
    store._create_tables()
    with store.conn:
        store.conn.execute(
            "INSERT INTO documents (id, text, word_count, metadata) "
            "VALUES (?, ?, ?, ?)",
            ("doc-1", "hello", 1, None),
        )
        store.conn.execute(
            "INSERT INTO inverted_index (term, doc_id) VALUES (?, ?)",
            ("hello", "doc-1"),
        )

    results = store.query(Query(query_str="hello", keywords={"hello"}))

    assert len(results) == 1
    assert results[0].id == "doc-1"
    assert results[0].metadata is None
