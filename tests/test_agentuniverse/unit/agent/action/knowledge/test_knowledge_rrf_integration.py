#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Integration tests for multi-store recall fusion through Knowledge.

These exercise the real ``Knowledge.query_knowledge`` retrieval/merge path
together with the ``ReciprocalRankFusionProcessor`` post-processor, verifying
that a document recalled by several stores survives the merge with its channel
identity intact and therefore receives a combined RRF score.
"""

import unittest
from unittest.mock import MagicMock, patch

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.doc_processor.\
    reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
from agentuniverse.agent.action.knowledge.knowledge import Knowledge, \
    RECALL_CHANNEL_KEY
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class _FakeStore:
    """Minimal store stub returning a fixed, ranked document list.

    Fresh ``Document`` copies are returned per query so that two stores
    reporting the "same" document yield distinct objects with an identical
    deterministic id — mirroring real store behaviour.
    """

    def __init__(self, docs):
        self._docs = docs

    def query(self, query: Query):
        return [Document(text=d.text, metadata=dict(d.metadata or {}))
                for d in self._docs]


class TestKnowledgeRrfIntegration(unittest.TestCase):
    """Multi-store recall fused by RRF through the Knowledge pipeline."""

    def _build_knowledge(self, stores):
        return Knowledge(
            name="rrf_knowledge",
            stores=list(stores.keys()),
            rag_router="base_router",
            post_processors=["reciprocal_rank_fusion_processor"],
        )

    def _run_query(self, knowledge, stores, rrf):
        """Drive ``query_knowledge`` with the managers and tracing mocked.

        The ``@trace_knowledge`` decorator pulls in ConversationMemoryModule /
        Monitor which require app configuration that is unavailable in unit
        tests; both are patched out so the real ``query_knowledge`` body runs.
        """
        router = MagicMock()
        router.rag_route.return_value = [
            (Query(query_str="q"), store_code) for store_code in stores
        ]
        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor, \
                patch.object(knowledge_module, "RagRouterManager") as router_mgr, \
                patch.object(knowledge_module, "StoreManager") as store_mgr, \
                patch.object(knowledge_module, "DocProcessorManager") as proc_mgr:
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            store_mgr.return_value.get_instance_obj.side_effect = \
                lambda code, **_: stores[code]
            proc_mgr.return_value.get_instance_obj.return_value = rrf
            return knowledge.query_knowledge(query_str="q")

    def test_shared_doc_gets_combined_rrf_score(self) -> None:
        """A doc recalled by two stores fuses to a combined RRF score."""
        stores = {
            "vector_store": _FakeStore(
                [Document(text="shared"), Document(text="only vector")]),
            "keyword_store": _FakeStore(
                [Document(text="shared"), Document(text="only keyword")]),
        }
        rrf = ReciprocalRankFusionProcessor(channel_key=RECALL_CHANNEL_KEY, k=60)
        knowledge = self._build_knowledge(stores)

        out = self._run_query(knowledge, stores, rrf)

        # The shared document is returned once (RRF dedups by id) yet its score
        # accumulates across both channels: rank 0 in each → 2 * 1/61.
        by_text = {d.text: d for d in out}
        self.assertIn("shared", by_text)
        self.assertAlmostEqual(
            by_text["shared"].metadata["relevance_score"], 2.0 / 61)
        # The single-channel docs tie at rank 1 → 1/62.
        self.assertAlmostEqual(
            by_text["only vector"].metadata["relevance_score"], 1.0 / 62)
        self.assertAlmostEqual(
            by_text["only keyword"].metadata["relevance_score"], 1.0 / 62)
        # The shared doc outranks everything else.
        self.assertEqual(out[0].text, "shared")

    def test_recall_channel_stamped_on_documents(self) -> None:
        """Each recalled document carries the store it came from."""
        stores = {
            "vector_store": _FakeStore([Document(text="v doc")]),
            "keyword_store": _FakeStore([Document(text="k doc")]),
        }
        rrf = ReciprocalRankFusionProcessor(channel_key=RECALL_CHANNEL_KEY)
        knowledge = self._build_knowledge(stores)

        out = self._run_query(knowledge, stores, rrf)

        channels = {d.metadata[RECALL_CHANNEL_KEY] for d in out}
        self.assertEqual(channels, {"vector_store", "keyword_store"})

    def test_shared_doc_not_collapsed_before_post_processing(self) -> None:
        """Before the fix the shared doc was dropped to a single copy with a
        single-channel score (1/61); it must now fuse to 2/61."""
        stores = {
            "vector_store": _FakeStore([Document(text="shared")]),
            "keyword_store": _FakeStore([Document(text="shared")]),
        }
        rrf = ReciprocalRankFusionProcessor(channel_key=RECALL_CHANNEL_KEY, k=60)
        knowledge = self._build_knowledge(stores)

        out = self._run_query(knowledge, stores, rrf)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "shared")
        self.assertAlmostEqual(
            out[0].metadata["relevance_score"], 2.0 / 61)

    def test_no_rrf_collapses_cross_store_duplicates(self) -> None:
        """Without a channel-fusion post-processor, Knowledge keeps the default
        retrieval contract: a document recalled by several stores is returned
        exactly once (master behaviour), not once per store, and no
        ``recall_channel`` metadata leaks onto the documents."""
        stores = {
            "vector_store": _FakeStore(
                [Document(text="shared"), Document(text="only vector")]),
            "keyword_store": _FakeStore(
                [Document(text="shared"), Document(text="only keyword")]),
        }
        knowledge = Knowledge(
            name="no_rrf_knowledge",
            stores=list(stores.keys()),
            rag_router="base_router",
            post_processors=[],  # no fusion → default retrieval contract
        )

        out = self._run_query(knowledge, stores, rrf=None)

        by_text = [d.text for d in out]
        self.assertEqual(by_text.count("shared"), 1)  # collapsed, not duplicated
        self.assertIn("only vector", by_text)
        self.assertIn("only keyword", by_text)
        for doc in out:
            self.assertNotIn(RECALL_CHANNEL_KEY, doc.metadata or {})

    def test_processor_without_channel_key_keeps_default_contract(self) -> None:
        """A post-processor that does not declare a ``channel_key`` must not
        trigger per-channel recall — channel-aware dedup is opt-in via
        ``channel_key``, so the default contract still collapses a document
        recalled by several stores to a single copy."""
        stores = {
            "vector_store": _FakeStore([Document(text="shared")]),
            "keyword_store": _FakeStore([Document(text="shared")]),
        }
        # A non-channel processor: channel_key left at its None default.
        non_channel_processor = ReciprocalRankFusionProcessor(channel_key=None)
        knowledge = Knowledge(
            name="no_channel_key_knowledge",
            stores=list(stores.keys()),
            rag_router="base_router",
            post_processors=["some_other_processor"],
        )

        out = self._run_query(knowledge, stores, non_channel_processor)

        self.assertEqual([d.text for d in out].count("shared"), 1)


if __name__ == '__main__':
    unittest.main()
