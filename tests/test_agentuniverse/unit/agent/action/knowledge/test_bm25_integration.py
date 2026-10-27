"""Real persisted candidates -> public Knowledge query -> lexical reranking."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.doc_processor.bm25_reranker import BM25Reranker
from agentuniverse.agent.action.knowledge.doc_processor.context_budget_compressor import ContextBudgetCompressor
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.doc_processor.threshold_filter import ThresholdFilter
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


def test_documented_demo_command_runs_in_fresh_process():
    root = Path(__file__).resolve().parents[6]
    completed = subprocess.run(
        [sys.executable, "-m", "examples.bm25_reranking_demo"],
        cwd=root, capture_output=True, text=True, check=True, timeout=60,
    )
    report = json.loads(completed.stdout)
    assert report["scope"] == "hand_authored_examples_not_a_quality_benchmark"
    exact, semantic = report["cases"]
    assert exact["recall_at_1"] == {"original": 0, "rrf": 0, "bm25": 1}
    assert semantic["recall_at_1"] == {"original": 1, "rrf": 1, "bm25": 0}
    for case in report["cases"]:
        assert all(set(ids) == {"0", "1", "2"} for ids in case["rankings"].values())


def test_sqlite_demo_uses_real_managers_and_public_query():
    completed = subprocess.run(
        [sys.executable, "-m", "examples.bm25_sqlite_demo"],
        cwd=Path(__file__).resolve().parents[6], capture_output=True,
        text=True, check=False, timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["workflow"] == "sqlite_insert_reopen_public_knowledge_query"
    assert report["persisted_count"] == 3
    assert report["persisted_metadata_unchanged"] is True
    assert report["reranked"][0]["id"] == "exact"
    assert report["reranked"][0]["bm25_score"] > 0
    assert {row["id"] for row in report["reranked"]} == set(report["original_ids"])


def test_shipped_yaml_is_discovered_registered_and_resolved(monkeypatch):
    """Exercise bootstrap scan/registration, not a hand-built processor fixture."""
    from agentuniverse.base.agentuniverse import AgentUniverse
    from agentuniverse.base.component.component_enum import ComponentEnum
    from agentuniverse.base.config.config_type_enum import ConfigTypeEnum
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager

    config_manager = ApplicationConfigManager()
    # Isolate singleton state without mocking scan, class resolution or lookup.
    monkeypatch.setattr(config_manager, "_ApplicationConfigManager__app_configer", AppConfiger())
    manager = DocProcessorManager()
    monkeypatch.setattr(manager, "_instance_obj_map", {})
    app = AgentUniverse()
    scanned = app.scan(
        ["agentuniverse.agent.action.knowledge.doc_processor"],
        ConfigTypeEnum.YAML, ComponentEnum.DOC_PROCESSOR,
    )
    configs = [config for config in scanned if config.name == "bm25_reranker"]
    assert len(configs) == 1
    # This is the same registration method called by application bootstrap.
    app._AgentUniverse__register(ComponentEnum.DOC_PROCESSOR, configs)
    processor = manager.get_instance_obj("bm25_reranker", strict=True)
    assert isinstance(processor, BM25Reranker)
    assert processor.top_n == 5
    assert processor.component_config_path.endswith("bm25_reranker.yaml")
    docs = [Document(id="near", text="AX-120 manual"), Document(id="exact", text="AX-12 manual")]
    assert processor.process_docs(docs, Query(query_str="AX-12"))[0].id == "exact"
    processor.top_n = 1
    assert manager.get_instance_obj("bm25_reranker", strict=True).top_n == 5


@pytest.mark.parametrize("mode", ["disabled", "bm25", "threshold", "budget", "rrf_bm25"])
def test_public_query_over_reopened_databases(tmp_path, mode):
    originals = [
        Document(id="neighbor", text="alpha AX-120 installation guide", metadata={"source": "A", "relevance_score": 9}),
        Document(id="exact", text="alpha AX-12 installation guide", metadata={"source": "B", "relevance_score": 8}),
        Document(id="other", text="alpha maintenance guide", metadata={"source": "C", "relevance_score": 7}),
    ]
    processors = {
        "keywords": JiebaKeywordExtractor(),
        "rank": ThresholdFilter(filters=[{"type": "topk", "k": 100}], preserve_order=False),
        "bm25": BM25Reranker(),
        "threshold": ThresholdFilter(score_field="bm25_score", filters=[{"type": "score", "min_score": 0.001}]),
        "budget": ContextBudgetCompressor(counter="char", budget=len(originals[1].text)),
        "rrf": ReciprocalRankFusionProcessor(channel_key="recall_channel"),
    }
    stores = {}
    knowledge = None
    with patch.object(knowledge_module, "DocProcessorManager") as pm, \
            patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as sm:
        pm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        sm.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        try:
            for name, indexes in [("first", [0, 1, 2]), ("second", [0, 1])]:
                store = SQLiteStore(db_path=str(tmp_path / f"{name}.db"), keyword_extractor="keywords")
                stores[name] = store
                store._new_client()
                store.insert_document([originals[i].model_copy(deep=True) for i in indexes])
                store.conn.close()
                store._new_client()
            pipeline = ["rrf"] if mode == "rrf_bm25" else ["rank"]
            if mode != "disabled":
                pipeline.append("bm25")
            if mode in ("threshold", "budget"):
                pipeline.append(mode)
            knowledge = Knowledge(name="bm25-example", stores=list(stores), post_processors=pipeline)
            router = MagicMock()
            # A controlled broad-recall router; SQL reads, scoring, threads,
            # public-query deduplication and processors are not mocked.
            router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), name) for name in stores]
            with patch.object(knowledge_module, "StoreManager") as store_manager, \
                    patch.object(knowledge_module, "RagRouterManager") as router_manager, \
                    patch.object(trace_module, "ConversationMemoryModule"), \
                    patch.object(trace_module, "Monitor") as monitor:
                store_manager.return_value.get_instance_obj.side_effect = lambda name, **kw: stores[name]
                router_manager.return_value.get_instance_obj.return_value = router
                monitor.get_invocation_chain.return_value = []
                result = knowledge.query_knowledge(query_str="AX-12")
            ids = [doc.id for doc in result]
            assert len(ids) == len(set(ids))
            if mode == "disabled":
                assert ids == ["neighbor", "exact", "other"]
                assert all("bm25_score" not in doc.metadata for doc in result)
            else:
                assert ids[0] == "exact"
                assert result[0].metadata["bm25_score"] > 0
                assert result[0].metadata["source"] == "B"
                if mode in ("threshold", "budget"):
                    assert ids == ["exact"]
                else:
                    assert len(ids) == 3
                if mode != "rrf_bm25":
                    assert result[0].metadata["relevance_score"] == 8
            for store in stores.values():
                persisted = store.conn.execute("SELECT metadata FROM documents").fetchall()
                assert all("bm25_score" not in json.loads(row[0]) for row in persisted)
        finally:
            if knowledge is not None:
                knowledge.insert_executor.shutdown(wait=True)
                knowledge.query_executor.shutdown(wait=True)
            for store in stores.values():
                store.conn.close()


@pytest.mark.parametrize("query,texts,relevant,expected", [
    ("AX-12", ["AX-120 manual", "AX-12 manual", "repair guide"], "1", (0, 0, 1)),
    # Counterexample: exact lexical overlap cannot infer synonyms/intent.
    ("car repair", ["automobile servicing", "car repair invoice", "weather"], "0", (1, 1, 0)),
])
def test_labeled_toy_comparison_retains_semantic_counterexample(query, texts, relevant, expected):
    batch = [Document(id=str(i), text=text, metadata={"channel": "A"}) for i, text in enumerate(texts)]
    rrf_input = batch + [batch[0].model_copy(update={"metadata": {"channel": "B"}})]
    rrf = ReciprocalRankFusionProcessor(channel_key="channel").process_docs(rrf_input, Query(query_str=query))
    bm25 = BM25Reranker().process_docs(batch, Query(query_str=query))
    # Recall@1 on explicitly supplied toy labels, not a production benchmark.
    actual = tuple(int(result[0].id == relevant) for result in (batch, rrf, bm25))
    assert actual == expected
