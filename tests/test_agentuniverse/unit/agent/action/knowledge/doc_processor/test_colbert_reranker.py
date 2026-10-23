"""Arithmetic, budgets, real fixed-revision model and public Knowledge integration."""

import json
import math
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest
import torch

from agentuniverse.agent.action.knowledge.doc_processor.colbert_reranker import ColbertReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture(scope="module")
def encoder():
    # Deliberately not importorskip: the documented model fixture is required.
    return ColbertReranker()._get_encoder()


def processor(encoder, **settings):
    instance = ColbertReranker(**settings)
    instance._encoder = encoder
    return instance


def test_maxsim_is_not_mean_pooling():
    q = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    d = torch.tensor([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    assert ColbertReranker._maxsim(q, d, 6) == pytest.approx(2.0)
    assert float(q.mean(0) @ d.mean(0)) != pytest.approx(2.0)


@pytest.mark.parametrize(
    "q,d,limit",
    [
        (torch.zeros(0, 2), torch.zeros(1, 2), 9),
        (torch.zeros(2), torch.zeros(1, 2), 9),
        (torch.zeros(1, 3), torch.zeros(1, 2), 9),
        (torch.ones(2, 2), torch.ones(2, 2), 3),
        (torch.tensor([[float("nan")]]), torch.ones(1, 1), 1),
        (torch.ones(1, 1), torch.tensor([[float("inf")]]), 1),
    ],
)
def test_invalid_vectors(q, d, limit):
    with pytest.raises(ValueError):
        ColbertReranker._maxsim(q, d, limit)


@pytest.mark.parametrize(
    "settings",
    [{"top_n": 0}, {"max_documents": True}, {"batch_size": 17}, {"max_score_cells": -1}, {"max_document_chars": "20"}],
)
def test_invalid_configuration(settings):
    with pytest.raises(ValueError):
        ColbertReranker(**settings)


@pytest.mark.parametrize(
    "settings,query,docs",
    [
        ({}, Query(query_str=""), [Document(text="a")]),
        ({}, Query(query_str="q"), [Document(text=" ")]),
        ({"max_documents": 1}, Query(query_str="q"), [Document(text="a"), Document(text="b")]),
        ({"max_query_chars": 1}, Query(query_str="qq"), [Document(text="a")]),
        ({"max_document_chars": 1}, Query(query_str="q"), [Document(text="aa")]),
        ({"max_total_chars": 1}, Query(query_str="qq"), []),
    ],
)
def test_preload_input_bounds(settings, query, docs):
    ranker = ColbertReranker(**settings)
    with patch.object(ColbertReranker, "_get_encoder", side_effect=AssertionError("must not load")):
        with pytest.raises(ValueError):
            ranker.process_docs(docs, query)


def test_empty_candidates_does_not_load():
    with patch.object(ColbertReranker, "_get_encoder", side_effect=AssertionError("must not load")):
        assert ColbertReranker().process_docs([], Query(query_str="query")) == []


def test_actual_model_oracle_stable_ties_and_input_isolation(encoder):
    ranker = processor(encoder, top_n=3, batch_size=2)
    docs = [
        Document(id="same-a", text="A dog barks.", embedding=[0.1, 0.2], metadata={"nested": [1]}),
        Document(id="cat", text="A cat purrs."),
        Document(id="same-b", text="A dog barks."),
    ]
    before = deepcopy([d.model_dump() for d in docs])
    query = Query(query_str="Which animal barks?")
    actual, report = ranker.rerank(docs, query)
    q = encoder.encode_query([query.query_str], normalize_embeddings=True, show_progress_bar=False)
    d = encoder.encode_document([item.text for item in docs], normalize_embeddings=True, show_progress_bar=False)
    oracle = encoder.similarity(q, d)[0].tolist()
    assert report["scores_in_input_order"] == pytest.approx(oracle, abs=1e-5)
    # Independent scalar-loop oracle, not the matrix implementation under test.
    scalar = [sum(max(float(torch.dot(qv, dv)) for dv in vectors) for qv in q[0]) for vectors in d]
    assert report["scores_in_input_order"] == pytest.approx(scalar, abs=1e-5)
    assert [item.id for item in actual][:2] == ["same-a", "same-b"]
    assert actual[0].embedding == [0.1, 0.2]
    actual[0].metadata["nested"].append(2)
    assert [item.model_dump() for item in docs] == before
    assert query.query_str == "Which animal barks?"
    assert report["truncated"] is False and report["query_vectors"] == 32


@pytest.mark.parametrize("task", ["query", "document", "cells"])
def test_actual_token_budgets_precede_encoding(encoder, task):
    ranker = processor(encoder, max_score_cells=1 if task == "cells" else 9600)
    query = Query(query_str="token " * 40 if task == "query" else "query")
    docs = [Document(text="token " * 310 if task == "document" else "document")]
    with patch.object(encoder, "encode_query", side_effect=AssertionError("encoding must not run")):
        with pytest.raises(ValueError):
            ranker.rerank(docs, query)


def test_copies_share_encoder_lock_but_not_results(encoder):
    ranker = processor(encoder, top_n=1)
    copied = ranker.create_copy()
    assert copied._encoder is ranker._encoder
    assert copied._lock is ranker._lock
    docs = [Document(id="dog", text="A dog barks."), Document(id="cat", text="A cat purrs.")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        left = pool.submit(ranker.process_docs, docs, Query(query_str="Which animal barks?"))
        right = pool.submit(copied.process_docs, docs, Query(query_str="Which animal purrs?"))
        assert left.result(timeout=30)[0].id == "dog"
        assert right.result(timeout=30)[0].id == "cat"
    assert all(document.metadata is None for document in docs)


def test_controlled_qrels_comparison_with_bm25(encoder, record_property):
    from rank_bm25 import BM25Okapi

    texts = [
        "A database rollback cancels a transaction and restores the previous row values.",
        "A database commit makes a transaction's changes permanent.",
        "A savepoint marks part of a database transaction for partial rollback.",
        "Database indexes make lookup faster but consume extra disk space.",
        "Merge sort guarantees O(n log n) time in the worst case by merging sorted halves.",
        "Bubble sort repeatedly swaps adjacent values and has quadratic worst-case time.",
        "Binary search locates a value in a sorted array in logarithmic time.",
        "A hash table stores values using keys and a hash function.",
        "ColBERT scores each query token against document tokens, takes the maximum similarity, then sums.",
        "Mean pooling averages all token vectors into one vector before comparing sentences.",
        "BM25 ranks documents from lexical term frequency and document length.",
        "A cross encoder jointly processes each query and document pair through a transformer.",
    ]
    queries = [
        ("Which database operation undoes pending changes?", 0),
        ("Which sorting algorithm guarantees O(n log n) worst-case time?", 4),
        ("How are text tokens compared in ColBERT?", 8),
    ]

    def tokenize(text):
        return re.findall(r"\w+", text.lower())

    bm25 = BM25Okapi([tokenize(text) for text in texts])
    ranker = processor(encoder, top_n=12)
    docs = [Document(id=str(i), text=text) for i, text in enumerate(texts)]
    rows = []
    for query, relevant in queries:
        rss_before = psutil.Process().memory_info().rss
        start = time.perf_counter()
        result, report = ranker.rerank(docs, Query(query_str=query))
        elapsed = time.perf_counter() - start
        rss_after = psutil.Process().memory_info().rss
        order = [int(doc.id) for doc in result]
        lexical = sorted(range(len(texts)), key=lambda i: (-bm25.get_scores(tokenize(query))[i], i))
        rank = order.index(relevant) + 1
        bm_rank = lexical.index(relevant) + 1
        rows.append(
            {
                "query": query,
                "colbert_reciprocal_rank": 1 / rank,
                "bm25_reciprocal_rank": 1 / bm_rank,
                "colbert_ndcg_at_10": 1 / math.log2(rank + 1) if rank <= 10 else 0,
                "bm25_ndcg_at_10": 1 / math.log2(bm_rank + 1) if bm_rank <= 10 else 0,
                "input_order_reciprocal_rank": 1 / (relevant + 1),
                "rss_before_bytes": rss_before,
                "rss_after_bytes": rss_after,
                "seconds": elapsed,
                "max_score_cells": 32 * max(report["document_vectors"]),
            }
        )
        assert set(order) == set(range(12))
    record_property("controlled_fixture_not_general_benchmark", json.dumps(rows))
    print("CONTROLLED_FIXTURE", json.dumps(rows))


def test_yaml_sqlite_public_knowledge_pipeline(encoder, tmp_path, monkeypatch):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    managers = [DocProcessorManager(), StoreManager(), RagRouterManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    apps = ApplicationConfigManager()
    app = Configer()
    app.value = {"BASE_INFO": {"appname": "colbert-test"}}
    monkeypatch.setattr(apps, "_ApplicationConfigManager__app_configer", AppConfiger().load_by_configer(app))
    root = next(parent for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file())
    config_path = tmp_path / "colbert.yaml"
    shutil.copyfile(
        root / "agentuniverse/agent/action/knowledge/doc_processor/colbert_reranker.yaml.example", config_path
    )
    config = ComponentConfiger().load_by_configer(Configer(str(config_path)).load())
    ranker = ColbertReranker().initialize_by_component_configer(config)
    ranker._encoder = encoder
    store = SQLiteStore(name="colbert_store", db_path=str(tmp_path / "documents.sqlite"), keyword_extractor="keywords")
    knowledge = None
    try:
        keywords = JiebaKeywordExtractor(name="keywords", top_k=30)
        router = BaseRouter(name="base_router")
        for component, manager in [
            (ranker, managers[0]),
            (keywords, managers[0]),
            (store, managers[1]),
            (router, managers[2]),
        ]:
            manager.register(component.get_instance_code(), component)
        store._new_client()
        store.insert_document(
            [
                Document(id="dog", text="The animal dog barks.", metadata={"source": "fixture"}),
                Document(id="cat", text="The animal cat purrs.", metadata={"source": "fixture"}),
            ]
        )
        store.conn.close()
        store._new_client()
        knowledge = Knowledge(stores=["colbert_store"], post_processors=["colbert_reranker"])
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(query_str="animal barks")
        assert result[0].id == "dog"
        assert result[0].metadata["source"] == "fixture"
        assert "colbert_rerank" in result[0].metadata
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store.conn:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
