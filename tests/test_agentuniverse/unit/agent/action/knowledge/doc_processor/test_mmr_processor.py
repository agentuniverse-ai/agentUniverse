# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/16
# @FileName: test_mmr_processor.py

"""Tests for the MMRProcessor doc processor."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.doc_processor.mmr_processor as \
    mmr_module
from agentuniverse.agent.action.knowledge.doc_processor.mmr_processor import \
    MMRProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(mmr_module.__file__),
                          "mmr_processor.yaml")


def _doc(name: str, embedding) -> Document:
    return Document(text=name, embedding=list(embedding))


# Fixture: query along the x-axis.
#   d1 = [1, 0]  rel = 1.0
#   d2 = [1, 1]  rel = 1/sqrt2 ~ 0.7071   (also similar to d1: sim 0.7071)
#   d3 = [0, 1]  rel = 0.0                (orthogonal to d1, sim 0.0)
_Q = [1.0, 0.0]
_D1 = [1.0, 0.0]
_D2 = [1.0, 1.0]
_D3 = [0.0, 1.0]


class TestMMRSelection(unittest.TestCase):
    """Greedy MMR selection over pre-supplied embeddings."""

    def setUp(self) -> None:
        self.query = Query(query_str="q", embeddings=[_Q])

    def _run(self, docs, **kwargs):
        proc = MMRProcessor(**kwargs)
        return proc.process_docs(docs, self.query)

    def test_empty_input_returns_empty(self) -> None:
        self.assertEqual(self._run([]), [])

    def test_non_positive_top_n_returns_empty(self) -> None:
        docs = [_doc("d1", _D1)]
        self.assertEqual(self._run(docs, top_n=0), [])
        self.assertEqual(self._run(docs, top_n=-3), [])

    def test_pure_relevance_when_lambda_is_one(self) -> None:
        # lambda=1 ignores diversity: output is relevance order d1 > d2 > d3.
        out = self._run([_doc("d1", _D1), _doc("d2", _D2), _doc("d3", _D3)],
                        lambda_coef=1.0)
        self.assertEqual([d.text for d in out], ["d1", "d2", "d3"])

    def test_diversity_when_lambda_is_zero(self) -> None:
        # lambda=0 maximises diversity: after the most relevant d1, the
        # orthogonal d3 is preferred over the redundant d2.
        out = self._run([_doc("d1", _D1), _doc("d2", _D2), _doc("d3", _D3)],
                        lambda_coef=0.0)
        self.assertEqual([d.text for d in out], ["d1", "d3", "d2"])

    def test_top_n_truncates_after_reranking(self) -> None:
        out = self._run([_doc("d1", _D1), _doc("d2", _D2), _doc("d3", _D3)],
                        lambda_coef=1.0, top_n=2)
        self.assertEqual([d.text for d in out], ["d1", "d2"])

    def test_most_relevant_first_regardless_of_lambda(self) -> None:
        # The first MMR pick is always the most query-relevant document.
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
            out = self._run([_doc("d2", _D2), _doc("d1", _D1), _doc("d3", _D3)],
                            lambda_coef=lam)
            self.assertEqual(out[0].text, "d1", f"lambda={lam}")

    def test_top_n_larger_than_input_keeps_all(self) -> None:
        out = self._run([_doc("d1", _D1), _doc("d2", _D2)],
                        lambda_coef=1.0, top_n=10)
        self.assertEqual(len(out), 2)

    def test_score_key_stamps_cosine_relevance(self) -> None:
        out = self._run([_doc("d1", _D1), _doc("d2", _D2), _doc("d3", _D3)],
                        lambda_coef=1.0, score_key="mmr_score")
        scores = {d.text: d.metadata["mmr_score"] for d in out}
        self.assertAlmostEqual(scores["d1"], 1.0)
        self.assertAlmostEqual(scores["d2"], 0.70710678, places=6)
        self.assertAlmostEqual(scores["d3"], 0.0)

    def test_no_score_key_leaves_metadata_clean(self) -> None:
        out = self._run([_doc("d1", _D1)], lambda_coef=1.0)
        self.assertNotIn("mmr_score", out[0].metadata or {})


class TestMMREmbeddingResolution(unittest.TestCase):
    """Embedding acquisition and graceful fallback."""

    def test_uses_query_embeddings_directly(self) -> None:
        # Query.embeddings[0] is used; no EmbeddingManager call is made.
        query = Query(query_str="q", embeddings=[_Q])
        with patch.object(mmr_module, "EmbeddingManager") as emb_mgr:
            out = MMRProcessor().process_docs(
                [_doc("d1", _D1), _doc("d2", _D2)], query)
            emb_mgr.assert_not_called()
        self.assertEqual([d.text for d in out], ["d1", "d2"])

    def test_missing_embeddings_without_model_falls_back(self) -> None:
        # No embeddings anywhere and no embedding_name -> input order preserved.
        docs = [Document(text="a"), Document(text="b")]
        out = MMRProcessor().process_docs(docs, Query(query_str="q"))
        self.assertEqual([d.text for d in out], ["a", "b"])

    def test_partial_embeddings_without_model_falls_back(self) -> None:
        # One doc has an embedding, the other does not, and there is no model to
        # fill the gap -> safe fallback to input order.
        docs = [_doc("d1", _D1), Document(text="d2")]
        out = MMRProcessor().process_docs(docs, Query(query_str="q",
                                                      embeddings=[_Q]))
        self.assertEqual([d.text for d in out], ["d1", "d2"])

    def test_embedding_name_computes_missing_embeddings(self) -> None:
        # Docs lack embeddings; embedding_name drives an EmbeddingManager call
        # that supplies them, so MMR runs and ranks by relevance.
        docs = [Document(text="d1"), Document(text="d2"), Document(text="d3")]
        model = MagicMock()
        # First call embeds the three doc texts, second embeds the query string.
        model.get_embeddings.side_effect = [
            [_D1, _D2, _D3],   # documents
            [_Q],              # query
        ]
        with patch.object(mmr_module, "EmbeddingManager") as emb_mgr:
            emb_mgr.return_value.get_instance_obj.return_value = model
            out = MMRProcessor(embedding_name="fake_emb", lambda_coef=1.0)\
                .process_docs(docs, Query(query_str="q"))
        # Relevance order with the supplied vectors.
        self.assertEqual([d.text for d in out], ["d1", "d2", "d3"])

    def test_embedding_lookup_failure_falls_back(self) -> None:
        with patch.object(mmr_module, "EmbeddingManager") as emb_mgr:
            emb_mgr.return_value.get_instance_obj.side_effect = RuntimeError(
                "no model")
            out = MMRProcessor(embedding_name="bad")\
                .process_docs([Document(text="a")], Query(query_str="q"))
        self.assertEqual([d.text for d in out], ["a"])


class TestMMRConfig(unittest.TestCase):
    """Initialization and configuration."""

    def test_invalid_lambda_raises(self) -> None:
        configer = SimpleNamespace(name="mmr", description="d", lambda_coef=1.5)
        with self.assertRaises(ValueError):
            MMRProcessor()._initialize_by_component_configer(configer)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="mmr", description="d",
            lambda_coef=0.3, top_n=4, embedding_name="emb", score_key="s")
        proc = MMRProcessor()._initialize_by_component_configer(configer)
        self.assertEqual(proc.lambda_coef, 0.3)
        self.assertEqual(proc.top_n, 4)
        self.assertEqual(proc.embedding_name, "emb")
        self.assertEqual(proc.score_key, "s")


class TestMMRRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.get_component_config_type(),
            ComponentEnum.DOC_PROCESSOR.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor.mmr_processor")
        self.assertEqual(component_configer.metadata_class, "MMRProcessor")


class TestMMRThroughKnowledgePipeline(unittest.TestCase):
    """MMR runs as a real post_processor through Knowledge.query_knowledge."""

    def test_mmr_reranks_in_the_pipeline(self) -> None:
        from agentuniverse.agent.action.knowledge import knowledge as \
            knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge
        import agentuniverse.base.annotation.trace as trace_module

        class _FakeStore:
            def __init__(self, docs):
                self._docs = docs

            def query(self, query):
                # Fresh copies, preserving the hand-crafted embeddings.
                return [Document(text=d.text, embedding=list(d.embedding),
                                 metadata=dict(d.metadata or {}))
                        for d in self._docs]

        # A single store returns d2 (more relevant than d3 to query [1,0]).
        store = _FakeStore([_doc("d2", _D2), _doc("d3", _D3)])
        mmr = MMRProcessor(lambda_coef=1.0, score_key="mmr_score")
        knowledge = Knowledge(
            name="mmr_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            post_processors=["mmr_processor"],
        )
        router = MagicMock()
        router.rag_route.return_value = [(Query(query_str="q"), "only_store")]

        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor, \
                patch.object(knowledge_module, "RagRouterManager") as router_mgr, \
                patch.object(knowledge_module, "StoreManager") as store_mgr, \
                patch.object(knowledge_module, "DocProcessorManager") as proc_mgr:
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            store_mgr.return_value.get_instance_obj.side_effect = \
                lambda code, **_: store
            proc_mgr.return_value.get_instance_obj.return_value = mmr
            out = knowledge.query_knowledge(query_str="q",
                                            embeddings=[_Q])

        # Relevance order: d2 (rel ~0.707) before d3 (rel 0), score stamped.
        self.assertEqual([d.text for d in out], ["d2", "d3"])
        self.assertAlmostEqual(out[0].metadata["mmr_score"], 0.70710678,
                               places=6)


if __name__ == '__main__':
    unittest.main()
