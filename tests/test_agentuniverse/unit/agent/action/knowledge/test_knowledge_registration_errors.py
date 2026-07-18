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

These tests cover both the generic base-manager behaviour and the end-to-end
``Knowledge.query_knowledge`` path that originally surfaced the bug.
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
        self.mgr = ComponentManagerBase(ComponentEnum.STORE)

    def test_default_returns_none_when_unregistered(self) -> None:
        # Default behaviour is unchanged: a missing component resolves to None.
        self.assertIsNone(self.mgr.get_instance_obj("missing", appname="test_app"))

    def test_strict_raises_value_error_naming_component(self) -> None:
        # strict=True turns the silent None into an actionable error that names
        # both the component code and its type, instead of letting the caller
        # blow up later with 'NoneType' object has no attribute 'query'.
        with self.assertRaises(ValueError) as ctx:
            self.mgr.get_instance_obj("missing", appname="test_app", strict=True)
        msg = str(ctx.exception)
        self.assertIn("missing", msg)
        self.assertIn(ComponentEnum.STORE.value, msg)

    def test_strict_returns_copy_when_registered(self) -> None:
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
        dummy = MagicMock()
        self.mgr._instance_obj_map["test_app.store.my_store"] = dummy
        result = self.mgr.get_instance_obj(
            "my_store", appname="test_app", strict=True, new_instance=False)
        self.assertIs(result, dummy)


class TestKnowledgeRegistrationErrors(unittest.TestCase):
    """End-to-end: query_knowledge surfaces a clear error for an unregistered
    store instead of a cryptic AttributeError."""

    def test_query_knowledge_raises_clear_error_for_unregistered_store(self) -> None:
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


class TestStrictLookupWithChannelFusion(unittest.TestCase):
    """Strict store lookup must coexist with the opt-in channel-aware recall
    that landed for RRF fusion: when a fusion post-processor is configured,
    ``query_knowledge`` still resolves each store with ``strict=True`` and the
    per-channel merge runs unchanged.
    """

    def test_strict_lookup_runs_alongside_channel_aware_fusion(self) -> None:
        from agentuniverse.agent.action.knowledge.doc_processor.\
            reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
        from agentuniverse.agent.action.knowledge.knowledge import \
            RECALL_CHANNEL_KEY
        from agentuniverse.agent.action.knowledge.store.document import Document

        class _FakeStore:
            def __init__(self, docs):
                self._docs = docs

            def query(self, query):
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
