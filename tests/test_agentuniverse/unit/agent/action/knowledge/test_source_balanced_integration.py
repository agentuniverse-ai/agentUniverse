"""Public Knowledge queries over two real, file-backed SQLite stores.

Only manager lookups and unrelated tracing services are patched. Database
writes/reads, futures, deduplication, and post-processing execute normally.
"""

from collections import Counter
from unittest.mock import MagicMock, patch

import pytest

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.doc_processor.context_budget_compressor import ContextBudgetCompressor
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.doc_processor.source_balanced_selector import SourceBalancedSelector
from agentuniverse.agent.action.knowledge.doc_processor.threshold_filter import ThresholdFilter
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore


@pytest.mark.parametrize("mode", ["disabled", "strict", "refill", "rrf", "budget"])
def test_public_query_with_persisted_sources(tmp_path, mode):
    originals = [Document(id=f"doc-{i}", text=f"alpha evidence {i}",
                          metadata={"source": source, "relevance_score": 100 - i})
                 for i, source in enumerate(["A", "A", "A", "B", "C"])]
    processors = {
        "keywords": JiebaKeywordExtractor(),
        "rank": ThresholdFilter(filters=[{"type": "topk", "k": 100}], preserve_order=False),
        "select": SourceBalancedSelector(top_n=5 if mode == "refill" else 3, refill=mode == "refill"),
        "budget": ContextBudgetCompressor(budget=1000, counter="char"),
        "rrf": ReciprocalRankFusionProcessor(channel_key="recall_channel"),
    }
    if mode == "budget":
        processors["budget"].budget = len(originals[0].text) + 4
    stores = {}
    knowledge = None
    with patch.object(knowledge_module, "DocProcessorManager") as processor_manager:
        processor_manager.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
        # SQLiteStore imports the same singleton factory; patch its lookup too.
        with patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as sqlite_manager:
            sqlite_manager.return_value.get_instance_obj.side_effect = lambda name, **kw: processors[name]
            try:
                for name, indexes in [("first", [0, 1, 2, 3]), ("second", [0, 4])]:
                    store = SQLiteStore(db_path=str(tmp_path / f"{name}.db"), keyword_extractor="keywords")
                    stores[name] = store
                    store._new_client()
                    store.insert_document([originals[i].model_copy(deep=True) for i in indexes])
                    store.conn.close()
                    store._new_client()  # Query a reopened database, not cached documents.

                pipeline = ["rank"]
                if mode == "rrf":
                    pipeline = ["rrf"]
                if mode != "disabled":
                    pipeline.append("select")
                pipeline.append("budget")
                knowledge = Knowledge(name="source-example", stores=list(stores), post_processors=pipeline)
                router = MagicMock()
                router.rag_route.return_value = [(Query(query_str="alpha", keywords={"alpha"}), name)
                                                 for name in stores]
                with patch.object(knowledge_module, "StoreManager") as store_manager, \
                        patch.object(knowledge_module, "RagRouterManager") as router_manager, \
                        patch.object(trace_module, "ConversationMemoryModule"), \
                        patch.object(trace_module, "Monitor") as monitor:
                    store_manager.return_value.get_instance_obj.side_effect = lambda name, **kw: stores[name]
                    router_manager.return_value.get_instance_obj.return_value = router
                    monitor.get_invocation_chain.return_value = []
                    result = knowledge.query_knowledge(query_str="alpha")

                ids = [doc.id for doc in result]
                assert len(ids) == len(set(ids))
                if mode in ("disabled", "refill"):
                    assert ids == [f"doc-{i}" for i in range(5)]
                    assert len({doc.metadata["source"] for doc in result[:3]}) == 1
                elif mode == "strict":
                    assert ids == ["doc-0", "doc-3", "doc-4"]
                    assert len({doc.metadata["source"] for doc in result}) == 3
                elif mode == "budget":
                    assert ids == ["doc-0", "doc-3"]
                    assert sum(len(doc.text) for doc in result) == processors["budget"].budget
                    assert result[1].metadata["truncated"] is True
                else:
                    assert len(result) == 3
                    assert set(Counter(doc.metadata["source"] for doc in result).values()) == {1}
                if mode != "rrf":
                    assert all("recall_channel" not in doc.metadata for doc in result)
                for store in stores.values():
                    persisted = store.conn.execute("SELECT metadata FROM documents").fetchall()
                    assert all("recall_channel" not in row[0] for row in persisted)
            finally:
                if knowledge is not None:
                    knowledge.insert_executor.shutdown(wait=True)
                    knowledge.query_executor.shutdown(wait=True)
                for store in stores.values():
                    store.conn.close()
