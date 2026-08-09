#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for three independent config/assignment bugs.

Each is a one-line typo that silently disabled a documented capability:

1. MilvusStore: a configured ``query_embedding`` was written into
   ``similarity_top_k`` instead of ``query_embedding`` — so enabling the
   feature simultaneously forced top_k to ``True`` (== 1) and left the
   actual flag at its default ``False``.
2. react_planner: ``stop_sequence`` was read from ``plan`` for the
   presence check but from ``profile`` for the value, so configuring it
   under ``plan`` (as the framework expects) had no effect.
3. ChromaConversationMemoryStorage.get: the ``input`` parameter (semantic
   query) was overwritten with ``None`` at the top of the method, so the
   embedding-based recall branch was dead code for every caller.
"""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# --------------------------------------------------------------------------- #
# 1. MilvusStore config typo
# --------------------------------------------------------------------------- #
class TestMilvusStoreQueryEmbeddingAssignment(unittest.TestCase):
    """``query_embedding`` config must land in ``self.query_embedding``."""

    def test_query_embedding_config_does_not_overwrite_similarity_top_k(self) -> None:
        from agentuniverse.agent.action.knowledge.store.milvus_store import MilvusStore

        store = MilvusStore()
        # Pre-set similarity_top_k to something we can detect a collision on.
        store.similarity_top_k = 42
        store.query_embedding = False

        configer = SimpleNamespace(
            name="milvus", description="d",
            component_config_path=None, default_symbol=False,
            query_embedding=True,
        )
        store._initialize_by_component_configer(configer)

        # The flag is now set, and similarity_top_k was NOT clobbered to True.
        self.assertTrue(store.query_embedding)
        self.assertEqual(
            store.similarity_top_k, 42,
            "query_embedding config must not overwrite similarity_top_k; "
            "the previous typo forced top_k=True (==1) whenever the flag was set.")


# --------------------------------------------------------------------------- #
# 2. react_planner stop_sequence namespace
# --------------------------------------------------------------------------- #
class TestReactPlannerStopSequenceNamespace(unittest.TestCase):
    """``stop_sequence`` configured under ``plan`` must reach the agent."""

    def test_stop_sequence_under_plan_is_used(self) -> None:
        # The fix is a source-level contract: the presence check and the
        # value read must use the SAME namespace. Driving the full invoke()
        # path requires constructing a complete AgentModel (memory, llm,
        # tools, planner config, ...), which is brittle and unrelated to the
        # bug. Instead, parse the source and assert the two reads match —
        # the previous bug read plan for the check and profile for the value.
        import inspect
        from agentuniverse.agent.plan.planner.react_planner import \
            react_planner as rp_module

        source = inspect.getsource(rp_module.ReActPlanner.invoke)
        # Both the 'if <ns>.get('stop_sequence')' check and the assignment
        # must reference agent_model.plan. The bug was a plan/profile mix-up.
        self.assertIn("agent_model.plan.get('stop_sequence')", source)
        self.assertIn("if agent_model.plan.get('stop_sequence'):", source)
        # And the profile-namespace read (the bug) must NOT be present.
        self.assertNotIn(
            "agent_model.profile.get('stop_sequence')", source,
            "stop_sequence must be read from the same namespace it is checked "
            "in (plan); the previous bug checked plan but read profile.")


# --------------------------------------------------------------------------- #
# 3. ChromaConversationMemoryStorage semantic recall
# --------------------------------------------------------------------------- #
class TestChromaConversationMemorySemanticRecall(unittest.TestCase):
    """A non-empty ``input`` must reach the embedding-based query branch."""

    def test_non_empty_input_triggers_embedding_query(self) -> None:
        from agentuniverse.agent.memory.conversation_memory.memory_storage.\
            chroma_conversation_memory_storage import \
            ChromaConversationMemoryStorage

        storage = ChromaConversationMemoryStorage()
        # Stub the collection so we can observe whether the embedding query
        # branch ran.
        fake_collection = MagicMock()
        fake_collection.query.return_value = {
            "ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]],
        }
        storage._collection = fake_collection

        # An embedding model that returns one vector for any input.
        fake_embedding = MagicMock()
        fake_embedding.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
        fake_mgr = MagicMock()
        fake_mgr.get_instance_obj.return_value = fake_embedding
        storage.embedding_model = "fake_emb"

        # Supply a non-empty input — this used to be overwritten with None
        # before the fix, so the embedding branch never ran.
        with patch(
            "agentuniverse.agent.memory.conversation_memory.memory_storage."
            "chroma_conversation_memory_storage.EmbeddingManager",
            return_value=fake_mgr,
        ):
            storage.get(session_id="s1", input="hello world")

        # Embedding model was asked for a vector and the collection's
        # query_embeddings path was exercised.
        fake_embedding.get_embeddings.assert_called_once_with(["hello world"])
        self.assertTrue(
            fake_collection.query.called,
            "non-empty input must reach the embedding-based query branch",
        )
        self.assertIn(
            "query_embeddings",
            fake_collection.query.call_args.kwargs,
            "the embedding branch queries by query_embeddings, not query_texts",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
