# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 14:30
# @Author  : kaichuan
# @FileName: test_chroma_context_store.py
"""Unit tests for ChromaContextStore (offline, no Chroma server)."""

import pytest

from agentuniverse.agent.context.context_model import (
    ContextMetadata, ContextPriority, ContextSegment, ContextType)
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class TestChromaContextStore:
    """Test ChromaContextStore config, guards and pure helpers."""

    @pytest.fixture
    def store(self):
        """ChromaContextStore without an initialized collection."""
        return ChromaContextStore()

    @pytest.fixture
    def segment(self):
        """Sample context segment."""
        return ContextSegment(
            type=ContextType.BACKGROUND, priority=ContextPriority.HIGH,
            content="Python context storage", tokens=3, session_id="s1",
            parent_id="p1", task_id="t1", agent_id="a1",
            metadata=ContextMetadata(relevance_score=0.9),
        )

    @staticmethod
    def _build_metadata(segment):
        """Build the metadata dict ChromaContextStore.add() would store."""
        return {
            "session_id": segment.session_id, "segment_id": segment.id,
            "type": segment.type.value, "priority": segment.priority.value,
            "tokens": segment.tokens,
            "created_at": segment.metadata.created_at.isoformat(),
            "last_accessed": segment.metadata.last_accessed.isoformat(),
            "access_count": segment.metadata.access_count,
            "relevance_score": segment.metadata.relevance_score,
            "decay_rate": segment.metadata.decay_rate,
        }

    def test_default_configuration(self, store):
        assert store.storage_tier == "cold"
        assert store.collection_name == "agentuniverse_context"
        assert store.embedding_model_name is None
        assert store.persist_directory == "./chroma_db"
        assert store.similarity_threshold == 0.7
        assert store.max_segments == 1000 and store.ttl_hours == 24

    def test_custom_configuration(self):
        store = ChromaContextStore(
            collection_name="custom_col", persist_directory="/tmp/cdb",
            similarity_threshold=0.5)
        assert store.collection_name == "custom_col"
        assert store.persist_directory == "/tmp/cdb"
        assert store.similarity_threshold == 0.5

    def test_add_requires_session_id(self, store, segment):
        with pytest.raises(ValueError, match="session_id is required"):
            store.add([segment])

    def test_add_without_collection_raises(self, store, segment):
        with pytest.raises(RuntimeError, match="not initialized"):
            store.add([segment], session_id="s1")

    def test_uninitialized_returns_empty_results(self, store):
        assert store.get("s1") == []
        assert store.search("query", "s1") == []
        assert store.get_by_ids("s1", ["id1"]) == []
        assert store.count("s1") == 0
        assert store.prune("s1") == 0
        assert store.get_all_sessions() == []
        assert store.delete("s1") is None
        assert store.clear_all() is None

    def test_metadata_to_segment_roundtrip(self, store, segment):
        metadata = self._build_metadata(segment)
        metadata.update({"parent_id": "p1", "task_id": "t1", "agent_id": "a1"})
        parsed = store._metadata_to_segment(segment.content, metadata)
        assert parsed.id == segment.id
        assert parsed.type == ContextType.BACKGROUND
        assert parsed.priority == ContextPriority.HIGH
        assert parsed.content == segment.content
        assert parsed.tokens == 3 and parsed.session_id == "s1"
        assert parsed.parent_id == "p1" and parsed.task_id == "t1"
        assert parsed.agent_id == "a1"
        assert parsed.metadata.created_at == segment.metadata.created_at
        assert parsed.metadata.relevance_score == 0.9
        plain = ContextSegment(type=ContextType.SYSTEM, content="sys", tokens=1)
        parsed_plain = store._metadata_to_segment(
            plain.content, self._build_metadata(plain))
        assert parsed_plain.type == ContextType.SYSTEM
        assert parsed_plain.priority == ContextPriority.MEDIUM
        assert parsed_plain.parent_id is None
