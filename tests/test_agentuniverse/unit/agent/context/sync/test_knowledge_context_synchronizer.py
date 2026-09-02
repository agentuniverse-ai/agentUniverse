# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 14:00
# @Author  : kaichuan
# @FileName: test_knowledge_context_synchronizer.py
"""Unit tests for KnowledgeContextSynchronizer (offline logic)."""

import hashlib

import pytest

from agentuniverse.agent.context.context_model import (
    ContextMetadata, ContextPriority, ContextSegment, ContextType)
from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    ConflictResolutionStrategy, KnowledgeContextSynchronizer, SyncResult)


class _FakeContextManager:
    """In-memory ContextManager stand-in (no storage backend)."""

    def __init__(self):
        self.segments = []

    def add_context(self, session_id, content, context_type, priority=None, **kwargs):
        segment = ContextSegment(type=context_type, content=content,
                                 tokens=len(content.split()), session_id=session_id,
                                 metadata=ContextMetadata(**kwargs.get("metadata", {})))
        self.segments.append(segment)
        return segment

    def get_context(self, session_id, **kwargs):
        return [s for s in self.segments if s.session_id == session_id]


class TestKnowledgeContextSynchronizer:
    """Test synchronizer defaults and pure sync logic."""

    @pytest.fixture
    def synchronizer(self):
        """Synchronizer bound to an in-memory fake ContextManager."""
        return KnowledgeContextSynchronizer(context_manager=_FakeContextManager())

    def test_default_configuration(self):
        sync = KnowledgeContextSynchronizer(context_manager=None)
        assert sync.conflict_strategy == ConflictResolutionStrategy.NEWEST_WINS
        assert sync.enable_versioning is True
        assert sync._knowledge_versions == {} and sync._knowledge_context_map == {}
        result = SyncResult()
        assert result.segments_added == 0 and result.version is None
        assert ConflictResolutionStrategy.MERGE.value == "merge"
        assert ConflictResolutionStrategy.VERSION_BOTH.value == "version_both"

    def test_compute_hash(self, synchronizer):
        assert synchronizer._compute_hash(["hello", "world"]) == hashlib.sha256(
            "helloworld".encode()).hexdigest()
        assert len(synchronizer._compute_hash(["a"])) == 64
        assert synchronizer._compute_hash(["a", "b"]) == synchronizer._compute_hash(["ab"])
        assert synchronizer._compute_hash(["ab"]) != synchronizer._compute_hash(["ac"])

    def test_sync_adds_segments_and_versions(self, synchronizer):
        result = synchronizer.sync_knowledge_to_context(
            "doc1", ["first document here", "second"], "s1")
        assert result.segments_added == 2 and result.version is not None
        assert result.details["documents_processed"] == 2
        assert len(synchronizer._knowledge_context_map["doc1"]) == 2
        manager = synchronizer.context_manager
        assert len(manager.segments) == 2
        assert manager.segments[0].type == ContextType.BACKGROUND
        assert synchronizer.get_knowledge_version("doc1") is result.version

    def test_sync_skips_unchanged_and_force_updates(self, synchronizer):
        docs = ["stable content one", "stable content two"]
        synchronizer.sync_knowledge_to_context("doc1", docs, "s1")
        second = synchronizer.sync_knowledge_to_context("doc1", docs, "s1")
        assert second.segments_added == 0
        assert second.details.get("skipped") == "No content changes detected"
        forced = synchronizer.sync_knowledge_to_context(
            "doc1", docs, "s1", force_update=True)
        assert forced.segments_added == 2
        assert len(synchronizer.context_manager.segments) == 4

    def test_invalidate_segments(self, synchronizer):
        segments = [ContextSegment(type=ContextType.BACKGROUND,
                                   priority=ContextPriority.HIGH, content=c,
                                   tokens=1, session_id="s1") for c in ("a", "b")]
        synchronizer.context_manager.segments = segments
        assert synchronizer._invalidate_segments("s1", [segments[0].id]) == 1
        assert segments[0].priority == ContextPriority.LOW
        assert segments[0].metadata.custom.get("invalidated") is True
        assert segments[1].priority == ContextPriority.HIGH

    def test_resolve_conflicts_strategies(self, synchronizer):
        critical = ContextSegment(type=ContextType.BACKGROUND,
                                  priority=ContextPriority.CRITICAL,
                                  content="old critical", tokens=2)
        low = ContextSegment(type=ContextType.BACKGROUND, priority=ContextPriority.LOW,
                             content="old low", tokens=2)
        resolve = synchronizer._resolve_conflicts
        newest = resolve([critical], ["new doc"],
                         ConflictResolutionStrategy.NEWEST_WINS, "k1", "s1")
        assert [s.content for s in newest] == ["new doc"]
        preserved = resolve([critical, low], ["new doc"],
                            ConflictResolutionStrategy.CRITICAL_PRESERVED, "k1", "s1")
        assert [s.content for s in preserved] == ["old critical", "new doc"]
        versioned = resolve([critical], ["new doc"],
                            ConflictResolutionStrategy.VERSION_BOTH, "k1", "s1")
        assert len(versioned) == 2
        assert versioned[0].priority == ContextPriority.MEDIUM
        assert versioned[0].metadata.custom["version"] == "old"
        assert versioned[1].metadata.custom["version"] == "new"
        merged = resolve([critical], ["new doc"], ConflictResolutionStrategy.MERGE, "k1", "s1")
        assert len(merged) == 2 and merged[1].content == "new doc"
