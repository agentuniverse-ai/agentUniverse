# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import pytest

faiss = pytest.importorskip("faiss", reason="faiss not installed")

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.faiss_store import FaissStore


@pytest.mark.parametrize("persist", [False, True])
def test_faiss_basic_insert_query(tmp_path, persist):
    index_path = str(tmp_path / "faiss.index") if persist else None
    store = FaissStore()
    store.embedding_model = None
    # Prepare embeddings manually to avoid API keys
    docs = [
        Document(text="apple", embedding=[1.0, 0.0, 0.0]),
        Document(text="banana", embedding=[0.0, 1.0, 0.0]),
        Document(text="cherry", embedding=[0.0, 0.0, 1.0]),
    ]
    store.index_path = index_path
    store.insert_document(docs)

    q = Query(query_str="apple", embeddings=[[1.0, 0.0, 0.0]])
    res = store.query(q)
    assert len(res) >= 1
    assert res[0].text == "apple"

    if persist:
        # reload
        store2 = FaissStore()
        store2.index_path = index_path
        store2._new_client()
        store2._ids = store._ids
        store2._texts = store._texts
        store2._metas = store._metas
        res2 = store2.query(q)
        assert len(res2) >= 1


def test_faiss_upsert_delete(tmp_path):
    store = FaissStore()
    store.embedding_model = None
    docs = [
        Document(text="alpha", embedding=[1.0, 0.0]),
        Document(text="beta", embedding=[0.0, 1.0]),
    ]
    store.insert_document(docs)
    # upsert alpha
    store.upsert_document([Document(text="alpha-updated", embedding=[1.0, 0.0])])
    # delete beta
    store.delete_document(docs[1].id)
    q = Query(query_str="alpha", embeddings=[[1.0, 0.0]])
    res = store.query(q)
    assert any("alpha" in d.text for d in res)


