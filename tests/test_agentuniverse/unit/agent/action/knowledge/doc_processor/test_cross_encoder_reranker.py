# !/usr/bin/env python3

# @Time    : 2026/10/02
# @FileName: test_cross_encoder_reranker.py

"""Tests for the CrossEncoderReranker doc processor.

The sentence-transformers dependency (which pulls in torch) is never
installed here: every test injects a fake module through ``sys.modules``,
which also proves the component's import is lazy.
"""

import os
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import agentuniverse.agent.action.knowledge.doc_processor.cross_encoder_reranker as cer_module
from agentuniverse.agent.action.knowledge.doc_processor.cross_encoder_reranker import CrossEncoderReranker
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer

_YAML_PATH = os.path.join(os.path.dirname(cer_module.__file__), "cross_encoder_reranker.yaml")


def _fake_st(predict_scores, model=None):
    """Build a fake sentence_transformers module whose CrossEncoder returns
    ``predict_scores`` from ``predict``. Returns (module, cross_encoder_cls).
    """
    cross_encoder_cls = MagicMock()
    instance = model or MagicMock()
    instance.predict.return_value = list(predict_scores)
    cross_encoder_cls.return_value = instance
    module = SimpleNamespace(CrossEncoder=cross_encoder_cls)
    return module, cross_encoder_cls, instance


def _rerank(docs, query_str, scores, **kwargs):
    """Run one rerank with the fake CrossEncoder injected; returns
    (output_docs, cross_encoder_cls, instance).
    """
    module, cls, instance = _fake_st(scores)
    with patch.dict(sys.modules, {"sentence_transformers": module}):
        reranker = CrossEncoderReranker(**kwargs)
        out = reranker.process_docs(docs, Query(query_str=query_str))
    return out, cls, instance


def _docs(*texts):
    return [Document(text=t) for t in texts]


class TestCrossEncoderOrdering(unittest.TestCase):
    """Documents come back sorted by descending model score."""

    def test_sorts_by_descending_score(self) -> None:
        out, _, _ = _rerank(_docs("a", "b", "c"), "q", [0.1, 0.9, 0.5])
        self.assertEqual([d.text for d in out], ["b", "c", "a"])

    def test_stamps_relevance_scores(self) -> None:
        out, _, _ = _rerank(_docs("a", "b"), "q", [0.2, 0.8])
        self.assertEqual(out[0].metadata["relevance_score"], 0.8)
        self.assertEqual(out[1].metadata["relevance_score"], 0.2)

    def test_top_n_truncates_after_sorting(self) -> None:
        out, _, _ = _rerank(_docs("a", "b", "c"), "q", [0.1, 0.9, 0.5], top_n=2)
        self.assertEqual([d.text for d in out], ["b", "c"])

    def test_top_n_none_keeps_all(self) -> None:
        out, _, _ = _rerank(_docs("a", "b", "c"), "q", [0.1, 0.9, 0.5])
        self.assertEqual(len(out), 3)

    def test_ties_keep_recall_order(self) -> None:
        out, _, _ = _rerank(_docs("first", "second", "third"), "q", [0.5, 0.5, 0.5])
        self.assertEqual([d.text for d in out], ["first", "second", "third"])

    def test_custom_score_key(self) -> None:
        out, _, _ = _rerank(_docs("a"), "q", [0.7], score_key="ce_score")
        self.assertEqual(out[0].metadata["ce_score"], 0.7)
        self.assertNotIn("relevance_score", out[0].metadata or {})

    def test_empty_score_key_skips_stamping(self) -> None:
        out, _, _ = _rerank(_docs("a"), "q", [0.7], score_key="")
        self.assertNotIn("relevance_score", out[0].metadata or {})

    def test_preserves_existing_metadata(self) -> None:
        doc = Document(text="a", metadata={"source": "kb"})
        out, _, _ = _rerank([doc], "q", [0.7])
        self.assertEqual(out[0].metadata["source"], "kb")
        self.assertEqual(out[0].metadata["relevance_score"], 0.7)

    def test_empty_docs_returns_empty(self) -> None:
        out, cls, _ = _rerank([], "q", [])
        self.assertEqual(out, [])
        # No documents: the model must never be loaded.
        cls.assert_not_called()

    def test_none_text_scores_as_empty_string(self) -> None:
        # An explicit id is required: the Document validator derives the id
        # from text via uuid5, which cannot run on None.
        out, _, instance = _rerank([Document(text=None, id="none-doc")], "q", [0.3])
        pairs = instance.predict.call_args.args[0]
        self.assertEqual(pairs, [("q", "")])
        self.assertEqual(len(out), 1)


class TestCrossEncoderModelInteraction(unittest.TestCase):
    """Model construction, caching, batching and dependency handling."""

    def test_predict_receives_pairs_and_batch_size(self) -> None:
        _rerank(_docs("a", "b"), "my query", [0.1, 0.2], batch_size=8)
        # Re-run to capture the instance explicitly.
        module, cls, instance = _fake_st([0.1, 0.2])
        with patch.dict(sys.modules, {"sentence_transformers": module}):
            CrossEncoderReranker(batch_size=8).process_docs(_docs("a", "b"), Query(query_str="my query"))
        (pairs,) = instance.predict.call_args.args
        self.assertEqual(pairs, [("my query", "a"), ("my query", "b")])
        self.assertEqual(instance.predict.call_args.kwargs["batch_size"], 8)
        self.assertFalse(instance.predict.call_args.kwargs["show_progress_bar"])

    def test_model_name_passed_to_constructor(self) -> None:
        _, cls, _ = _rerank(_docs("a"), "q", [0.5], model_name="BAAI/bge-reranker-v2-m3")
        cls.assert_called_once_with("BAAI/bge-reranker-v2-m3")

    def test_device_forwarded_only_when_set(self) -> None:
        _, cls, _ = _rerank(_docs("a"), "q", [0.5])
        cls.assert_called_once_with("BAAI/bge-reranker-base")
        _, cls2, _ = _rerank(_docs("a"), "q", [0.5], device="cpu")
        cls2.assert_called_once_with("BAAI/bge-reranker-base", device="cpu")

    def test_model_cached_across_calls(self) -> None:
        module, cls, _ = _fake_st([0.5])
        with patch.dict(sys.modules, {"sentence_transformers": module}):
            reranker = CrossEncoderReranker()
            reranker.process_docs(_docs("a"), Query(query_str="q"))
            reranker.process_docs(_docs("b"), Query(query_str="q2"))
        self.assertEqual(cls.call_count, 1)

    def test_missing_dependency_raises_with_install_hint(self) -> None:
        # sys.modules entry set to None makes the from-import raise ImportError.
        with patch.dict(sys.modules, {"sentence_transformers": None}), self.assertRaises(ImportError) as ctx:
            CrossEncoderReranker().process_docs(_docs("a"), Query(query_str="q"))
        self.assertIn("rerank_ext", str(ctx.exception))

    def test_predict_failure_propagates(self) -> None:
        # A configured reranker must not silently pass through unreranked.
        module, _, instance = _fake_st([0.5])
        instance.predict.side_effect = RuntimeError("model exploded")
        with patch.dict(sys.modules, {"sentence_transformers": module}), self.assertRaises(RuntimeError):
            CrossEncoderReranker().process_docs(_docs("a"), Query(query_str="q"))


class TestCrossEncoderQueryContract(unittest.TestCase):
    """A reranker without a query cannot score — same contract as the
    existing cloud rerankers."""

    def test_missing_query_raises(self) -> None:
        module, _, _ = _fake_st([0.5])
        with patch.dict(sys.modules, {"sentence_transformers": module}), self.assertRaises(ValueError):
            CrossEncoderReranker().process_docs(_docs("a"), None)

    def test_empty_query_str_raises(self) -> None:
        module, _, _ = _fake_st([0.5])
        with patch.dict(sys.modules, {"sentence_transformers": module}), self.assertRaises(ValueError):
            CrossEncoderReranker().process_docs(_docs("a"), Query(query_str="  "))


class TestCrossEncoderConfig(unittest.TestCase):
    """Invalid configuration fails loudly at load time."""

    def test_bad_values_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="cer", description="d", model_name="  "),
            SimpleNamespace(name="cer", description="d", top_n=0),
            SimpleNamespace(name="cer", description="d", batch_size=0),
        ):
            with self.assertRaises(ValueError):
                CrossEncoderReranker()._initialize_by_component_configer(bad)

    def test_bad_types_raise_at_configer_load(self) -> None:
        for bad in (
            SimpleNamespace(name="cer", description="d", model_name=7),
            SimpleNamespace(name="cer", description="d", top_n="5"),
            SimpleNamespace(name="cer", description="d", score_key=7),
            SimpleNamespace(name="cer", description="d", device=3),
        ):
            with self.assertRaises(TypeError):
                CrossEncoderReranker()._initialize_by_component_configer(bad)

    def test_attributes_loaded_from_configer(self) -> None:
        configer = SimpleNamespace(
            name="cer", description="d", model_name="my/model", top_n=5, score_key="s", batch_size=4, device="cpu"
        )
        proc = CrossEncoderReranker()._initialize_by_component_configer(configer)
        self.assertEqual(proc.model_name, "my/model")
        self.assertEqual(proc.top_n, 5)
        self.assertEqual(proc.score_key, "s")
        self.assertEqual(proc.batch_size, 4)
        self.assertEqual(proc.device, "cpu")


class TestCrossEncoderRegistration(unittest.TestCase):
    """The shipped yaml resolves through the real framework loader and
    loads without sentence-transformers installed."""

    def test_yaml_resolves_to_doc_processor_type(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(component_configer.get_component_config_type(), ComponentEnum.DOC_PROCESSOR.value)

    def test_yaml_exposes_module_and_class(self) -> None:
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        self.assertEqual(
            component_configer.metadata_module,
            "agentuniverse.agent.action.knowledge.doc_processor." "cross_encoder_reranker",
        )
        self.assertEqual(component_configer.metadata_class, "CrossEncoderReranker")

    def test_shipped_yaml_initializes_without_dependency(self) -> None:
        # The real venv has no sentence-transformers installed: successful
        # initialization proves the import is lazy and the shipped yaml is
        # loadable at framework start.
        self.assertNotIn("sentence_transformers", sys.modules)
        configer = Configer(path=os.path.abspath(_YAML_PATH)).load()
        component_configer = ComponentConfiger().load_by_configer(configer)
        proc = CrossEncoderReranker()._initialize_by_component_configer(component_configer)
        self.assertEqual(proc.model_name, "BAAI/bge-reranker-base")
        self.assertIsNone(proc.top_n)


class TestCrossEncoderThroughKnowledgePipeline(unittest.TestCase):
    """The reranker runs as a real post_processor through query_knowledge."""

    def test_reranks_in_the_pipeline(self) -> None:
        import agentuniverse.base.annotation.trace as trace_module
        from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
        from agentuniverse.agent.action.knowledge.knowledge import Knowledge

        class _FakeStore:
            def query(self, query):
                return [Document(text="low"), Document(text="high")]

        module, _, _ = _fake_st([0.1, 0.9])
        knowledge = Knowledge(
            name="cer_knowledge",
            stores=["only_store"],
            rag_router="base_router",
            post_processors=["cross_encoder_reranker"],
        )
        router = MagicMock()
        router.rag_route.side_effect = lambda q, stores: [(q, "only_store")]

        with (
            patch.dict(sys.modules, {"sentence_transformers": module}),
            patch.object(trace_module, "ConversationMemoryModule"),
            patch.object(trace_module, "Monitor") as monitor,
            patch.object(knowledge_module, "RagRouterManager") as router_mgr,
            patch.object(knowledge_module, "StoreManager") as store_mgr,
            patch.object(knowledge_module, "DocProcessorManager") as proc_mgr,
        ):
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            store_mgr.return_value.get_instance_obj.side_effect = lambda code, **_: _FakeStore()
            proc_mgr.return_value.get_instance_obj.return_value = CrossEncoderReranker()
            out = knowledge.query_knowledge(query_str="q")

        self.assertEqual([d.text for d in out], ["high", "low"])
        self.assertEqual(out[0].metadata["relevance_score"], 0.9)


if __name__ == "__main__":
    unittest.main()
