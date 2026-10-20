# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/13
# @FileName: test_knowledge_registration_errors.py

"""
Tests for clear error reporting when a referenced component is not registered.

Background: ``ComponentManagerBase.get_instance_obj`` used to return ``None``
silently when a component (store / rag-router / ...) was not registered, so a
later attribute access on the result crashed with a cryptic
``AttributeError: 'NoneType' object has no attribute 'query'`` (issues #207 and
#203). The ``strict=True`` path now raises a descriptive ``ValueError`` instead.

These tests cover the generic base-manager behaviour and Knowledge pipeline
lookups for stores, readers, document processors, and query paraphrasers.
"""

import unittest
from unittest.mock import MagicMock, patch

import agentuniverse.base.annotation.trace as trace_module
from agentuniverse.agent.action.knowledge import knowledge as knowledge_module
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.component.component_manager_base import \
    ComponentManagerBase
import agentuniverse.base.component.component_manager_base as cmb_module


class TestGetInstanceObjStrict(unittest.TestCase):
    """Unit tests for the ``strict`` flag on get_instance_obj."""

    def setUp(self) -> None:
        """Set up a fresh store component manager for each test."""
        self.mgr = ComponentManagerBase(ComponentEnum.STORE)

    def test_default_returns_none_when_unregistered(self) -> None:
        """A missing component still resolves to ``None`` by default."""
        # Default behaviour is unchanged: a missing component resolves to None.
        self.assertIsNone(self.mgr.get_instance_obj("missing", appname="test_app"))

    def test_strict_raises_value_error_naming_component(self) -> None:
        """Strict mode turns the silent ``None`` into a ``ValueError`` naming the component."""
        # strict=True turns the silent None into an actionable error that names
        # both the component code and its type, instead of letting the caller
        # blow up later with 'NoneType' object has no attribute 'query'.
        with self.assertRaises(ValueError) as ctx:
            self.mgr.get_instance_obj("missing", appname="test_app", strict=True)
        msg = str(ctx.exception)
        self.assertIn("missing", msg)
        self.assertIn(ComponentEnum.STORE.value, msg)

    def test_strict_returns_copy_when_registered(self) -> None:
        """Strict mode keeps the happy path: a registered component comes back as a copy."""
        # strict must not change the happy path: a registered component is
        # still returned (as an independent copy when new_instance=True).
        copy_sentinel = object()
        dummy = MagicMock()
        dummy.create_copy.return_value = copy_sentinel
        self.mgr._instance_obj_map["test_app.store.my_store"] = dummy
        result = self.mgr.get_instance_obj(
            "my_store", appname="test_app", strict=True)
        self.assertIs(result, copy_sentinel)

    def test_strict_returns_raw_instance_when_new_instance_false(self) -> None:
        """The registered instance itself is returned when ``new_instance`` is False."""
        dummy = MagicMock()
        self.mgr._instance_obj_map["test_app.store.my_store"] = dummy
        result = self.mgr.get_instance_obj(
            "my_store", appname="test_app", strict=True, new_instance=False)
        self.assertIs(result, dummy)


class TestKnowledgeRegistrationErrors(unittest.TestCase):
    """End-to-end: query_knowledge surfaces a clear error for an unregistered
    store instead of a cryptic AttributeError."""

    def test_query_knowledge_raises_clear_error_for_unregistered_store(self) -> None:
        """End-to-end check that ``query_knowledge`` reports a descriptive error."""
        knowledge = Knowledge(
            name="guard_knowledge",
            stores=["definitely_unregistered_store"],
            rag_router="base_router",
        )
        # Router routes the query to a store code that no one registered.
        router = MagicMock()
        router.rag_route.return_value = [
            (Query(query_str="q"), "definitely_unregistered_store")]

        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor, \
                patch.object(knowledge_module, "RagRouterManager") as router_mgr, \
                patch.object(cmb_module, "ApplicationConfigManager") as acm:
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            acm.return_value.app_configer.base_info_appname = "test_app"

            with self.assertRaises(ValueError) as ctx:
                knowledge.query_knowledge(query_str="q")

        msg = str(ctx.exception)
        self.assertIn("definitely_unregistered_store", msg)
        self.assertIn(ComponentEnum.STORE.value, msg)


class TestKnowledgePipelineRegistrationErrors(unittest.TestCase):
    """Knowledge pipeline components fail with actionable registration errors."""

    def _knowledge(self, **kwargs) -> Knowledge:
        knowledge = Knowledge(**kwargs)
        self.addCleanup(knowledge.insert_executor.shutdown, wait=True)
        self.addCleanup(knowledge.query_executor.shutdown, wait=True)
        return knowledge

    @staticmethod
    def _set_test_app(acm: MagicMock) -> None:
        acm.return_value.app_configer.base_info_appname = "test_app"

    def test_load_data_reports_unregistered_custom_reader(self) -> None:
        knowledge = self._knowledge(
            readers={"url": "definitely_unregistered_custom_reader"})

        with patch.object(cmb_module, "ApplicationConfigManager") as acm:
            self._set_test_app(acm)
            with self.assertRaises(ValueError) as ctx:
                knowledge._load_data(source_path="https://example.com/article")

        message = str(ctx.exception)
        self.assertIn("url", message)
        self.assertIn("definitely_unregistered_custom_reader", message)
        self.assertIn(ComponentEnum.READER.value, message)
        self.assertIn("Knowledge.readers", message)
        self.assertNotIn("NoneType", message)

    def test_load_data_reports_unregistered_default_reader(self) -> None:
        source_type = "q2default"
        reader_code = "definitely_unregistered_default_reader"
        knowledge = self._knowledge()

        with patch.dict(knowledge_module.ReaderManager.DEFAULT_READER,
                        {source_type: reader_code}), \
                patch.object(knowledge_module.os.path, "isfile", return_value=True), \
                patch.object(cmb_module, "ApplicationConfigManager") as acm:
            self._set_test_app(acm)
            with self.assertRaises(ValueError) as ctx:
                knowledge._load_data(source_path=f"/tmp/document.{source_type}")

        message = str(ctx.exception)
        self.assertIn(source_type, message)
        self.assertIn(reader_code, message)
        self.assertIn(ComponentEnum.READER.value, message)
        self.assertIn("Knowledge.readers", message)
        self.assertNotIn("NoneType", message)

    def test_load_data_reports_source_type_without_reader_mapping(self) -> None:
        source_type = "q2unknown"
        knowledge = self._knowledge()

        with patch.object(knowledge_module.os.path, "isfile", return_value=True):
            with self.assertRaises(ValueError) as ctx:
                knowledge._load_data(source_path=f"/tmp/document.{source_type}")

        message = str(ctx.exception)
        self.assertIn(source_type, message)
        self.assertIn(ComponentEnum.READER.value, message)
        self.assertIn("Knowledge.readers", message)
        self.assertIn("registered", message)
        self.assertNotIn("NoneType", message)

    def test_load_data_preserves_registered_reader_copy_error(self) -> None:
        reader_code = "registered_but_invalid_reader"
        knowledge = self._knowledge(readers={"url": reader_code})
        registered_reader = MagicMock()
        registered_reader.create_copy.side_effect = ValueError("reader copy failed")
        reader_manager = MagicMock()
        reader_manager.get_instance_obj.return_value = registered_reader

        with patch.object(knowledge_module, "ReaderManager",
                          return_value=reader_manager):
            with self.assertRaisesRegex(ValueError, "reader copy failed"):
                knowledge._load_data(source_path="https://example.com/article")

        reader_manager.get_instance_obj.assert_called_once_with(
            reader_code, new_instance=False, strict=True)

    def test_doc_processing_stages_report_unregistered_processor(self) -> None:
        query = Query(query_str="q")
        cases = (
            ("insert", "insert_processors", "_insert_process", ([],)),
            ("update", "update_processors", "_update_process", ([],)),
            ("post", "post_processors", "_rag_post_process", ([], query)),
        )

        with patch.object(cmb_module, "ApplicationConfigManager") as acm:
            self._set_test_app(acm)
            for stage, config_field, method_name, args in cases:
                processor_code = f"definitely_unregistered_{stage}_processor"
                knowledge = self._knowledge(**{config_field: [processor_code]})
                with self.subTest(stage=stage), self.assertRaises(ValueError) as ctx:
                    getattr(knowledge, method_name)(*args)

                message = str(ctx.exception)
                self.assertIn(processor_code, message)
                self.assertIn(ComponentEnum.DOC_PROCESSOR.value, message)
                self.assertIn("configuration", message)
                self.assertNotIn("NoneType", message)

    def test_paraphrase_query_reports_unregistered_paraphraser(self) -> None:
        paraphraser_code = "definitely_unregistered_query_paraphraser"
        knowledge = self._knowledge(query_paraphrasers=[paraphraser_code])

        with patch.object(cmb_module, "ApplicationConfigManager") as acm:
            self._set_test_app(acm)
            with self.assertRaises(ValueError) as ctx:
                knowledge._paraphrase_query(Query(query_str="q"))

        message = str(ctx.exception)
        self.assertIn(paraphraser_code, message)
        self.assertIn(ComponentEnum.QUERY_PARAPHRASER.value, message)
        self.assertIn("configuration", message)
        self.assertNotIn("NoneType", message)


class TestStrictLookupWithChannelFusion(unittest.TestCase):
    """Strict store lookup must coexist with the opt-in channel-aware recall
    that landed for RRF fusion: when a fusion post-processor is configured,
    ``query_knowledge`` still resolves each store with ``strict=True`` and the
    per-channel merge runs unchanged.
    """

    def test_strict_lookup_runs_alongside_channel_aware_fusion(self) -> None:
        """Strict store lookup must coexist with channel-aware RRF fusion recall."""
        from agentuniverse.agent.action.knowledge.doc_processor.\
            reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
        from agentuniverse.agent.action.knowledge.knowledge import \
            RECALL_CHANNEL_KEY
        from agentuniverse.agent.action.knowledge.store.document import Document

        class _FakeStore:
            """Minimal in-memory store stub backed by the given documents."""

            def __init__(self, docs):
                """Store the source documents for later queries."""
                self._docs = docs

            def query(self, query):
                """Return one Document per stored document, copying text and metadata."""
                return [Document(text=d.text, metadata=dict(d.metadata or {}))
                        for d in self._docs]

        stores = {
            "vector_store": _FakeStore([Document(text="shared")]),
            "keyword_store": _FakeStore([Document(text="shared")]),
        }
        rrf = ReciprocalRankFusionProcessor(channel_key=RECALL_CHANNEL_KEY, k=60)
        knowledge = Knowledge(
            name="strict_fusion_knowledge",
            stores=list(stores.keys()),
            rag_router="base_router",
            post_processors=["reciprocal_rank_fusion_processor"],
        )

        router = MagicMock()
        router.rag_route.return_value = [
            (Query(query_str="q"), code) for code in stores]
        with patch.object(trace_module, "ConversationMemoryModule"), \
                patch.object(trace_module, "Monitor") as monitor, \
                patch.object(knowledge_module, "RagRouterManager") as router_mgr, \
                patch.object(knowledge_module, "StoreManager") as store_mgr, \
                patch.object(knowledge_module, "DocProcessorManager") as proc_mgr:
            monitor.get_invocation_chain.return_value = []
            router_mgr.return_value.get_instance_obj.return_value = router
            # The loop passes strict=True; the stub still resolves each
            # registered store so the channel-aware merge can run.
            store_mgr.return_value.get_instance_obj.side_effect = \
                lambda code, **_: stores[code]
            proc_mgr.return_value.get_instance_obj.return_value = rrf

            out = knowledge.query_knowledge(query_str="q")

        # The shared document is fused across both channels (2 * 1/61),
        # proving strict lookup did not short-circuit the channel-aware merge.
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].text, "shared")
        self.assertAlmostEqual(out[0].metadata["relevance_score"], 2.0 / 61)
        # And query_knowledge resolved the stores via strict=True, so the
        # clear-error contract holds even with channel fusion enabled.
        strict_lookup_calls = [
            c for c in store_mgr.return_value.get_instance_obj.call_args_list
            if c.kwargs.get("strict") is True]
        self.assertTrue(
            strict_lookup_calls,
            "query_knowledge should look up stores with strict=True")


if __name__ == '__main__':
    unittest.main()
