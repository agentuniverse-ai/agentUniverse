# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 14:00
# @Author  : kaichuan
# @FileName: test_ram_context_store.py
"""Unit tests for RamContextStore."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.store.ram_context_store import RamContextStore
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
    ContextMetadata,
)


class TestRamContextStore:
    """Test RamContextStore implementation."""

    @pytest.fixture
    def store(self):
        """Create a RamContextStore instance for testing."""
        return RamContextStore(
            name="test_ram_store",
            max_segments=100,
            ttl_hours=24,
        )

    @pytest.fixture
    def sample_segments(self):
        """Create sample context segments."""
        return [
            ContextSegment(
                type=ContextType.SYSTEM,
                priority=ContextPriority.CRITICAL,
                content="System prompt: You are a helpful assistant",
                tokens=10,
            ),
            ContextSegment(
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="User: Hello",
                tokens=5,
            ),
            ContextSegment(
                type=ContextType.CONVERSATION,
                priority=ContextPriority.HIGH,
                content="Assistant: Hi there!",
                tokens=7,
            ),
            ContextSegment(
                type=ContextType.BACKGROUND,
                priority=ContextPriority.MEDIUM,
                content="Background knowledge about topic X",
                tokens=20,
            ),
        ]

    def test_initialization(self, store):
        """Test store initialization."""
        assert store.name == "test_ram_store"
        assert store.storage_tier == "hot"
        assert store.max_segments == 100
        assert store.ttl_hours == 24

    def test_add_segments(self, store, sample_segments):
        """Test adding segments to store."""
        store.add(sample_segments, session_id="session_1")

        # Verify storage
        retrieved = store.get("session_1")
        assert len(retrieved) == 4

    def test_add_without_session_id(self, store, sample_segments):
        """Test adding without session_id raises error."""
        with pytest.raises(ValueError, match="session_id is required"):
            store.add(sample_segments)

    def test_get_segments(self, store, sample_segments):
        """Test retrieving segments."""
        store.add(sample_segments, session_id="session_1")

        # Get all segments
        segments = store.get("session_id"="session_1")
        assert len(segments) == 4

    def test_get_with_type_filter(self, store, sample_segments):
        """Test retrieving segments filtered by type."""
        store.add(sample_segments, session_id="session_1")

        # Get only CONVERSATION type
        conversations = store.get(
            session_id="session_1",
            context_type=ContextType.CONVERSATION
        )

        assert len(conversations) == 2
        assert all(s.type == ContextType.CONVERSATION for s in conversations)

    def test_get_with_priority_filter(self, store, sample_segments):
        """Test retrieving segments filtered by priority."""
        store.add(sample_segments, session_id="session_1")

        # Get only HIGH priority
        high_priority = store.get(
            session_id="session_1",
            priority=ContextPriority.HIGH
        )

        assert len(high_priority) == 2
        assert all(s.priority == ContextPriority.HIGH for s in high_priority)

    def test_get_with_limit(self, store, sample_segments):
        """Test retrieving segments with limit."""
        store.add(sample_segments, session_id="session_1")

        # Get only 2 segments
        limited = store.get("session_1", limit=2)

        assert len(limited) == 2

    def test_get_nonexistent_session(self, store):
        """Test getting from nonexistent session returns empty list."""
        segments = store.get("nonexistent_session")
        assert len(segments) == 0

    def test_search_keyword_match(self, store):
        """Test keyword search."""
        segments = [
            ContextSegment(
                type=ContextType.BACKGROUND,
                content="Python is a programming language",
                tokens=10,
            ),
            ContextSegment(
                type=ContextType.BACKGROUND,
                content="JavaScript is also a programming language",
                tokens=12,
            ),
            ContextSegment(
                type=ContextType.BACKGROUND,
                content="Cooking recipes for dinner",
                tokens=8,
            ),
        ]
        store.add(segments, session_id="session_1")

        # Search for "programming"
        results = store.search("programming", "session_1", top_k=10)

        assert len(results) == 2
        assert all("programming" in s.content.lower() for s in results)

    def test_search_exact_phrase(self, store):
        """Test exact phrase search."""
        segments = [
            ContextSegment(
                type=ContextType.CONVERSATION,
                content="I love machine learning",
                tokens=10,
            ),
            ContextSegment(
                type=ContextType.CONVERSATION,
                content="Machine learning is great",
                tokens=10,
            ),
            ContextSegment(
                type=ContextType.CONVERSATION,
                content="I love coding",
                tokens=8,
            ),
        ]
        store.add(segments, session_id="session_1")

        # Search for exact phrase
        results = store.search("machine learning", "session_1", top_k=10)

        assert len(results) == 2

    def test_search_with_top_k(self, store):
        """Test search with top_k limit."""
        segments = [
            ContextSegment(
                type=ContextType.BACKGROUND,
                content=f"Document {i} about AI and machine learning",
                tokens=15,
            )
            for i in range(10)
        ]
        store.add(segments, session_id="session_1")

        # Search with top_k=3
        results = store.search("AI machine learning", "session_1", top_k=3)

        assert len(results) == 3

    def test_delete_specific_segments(self, store, sample_segments):
        """Test deleting specific segments."""
        store.add(sample_segments, session_id="session_1")

        segment_ids = [sample_segments[0].id, sample_segments[1].id]
        store.delete("session_1", segment_ids=segment_ids)

        # Verify deletion
        remaining = store.get("session_1")
        assert len(remaining) == 2
        assert all(s.id not in segment_ids for s in remaining)

    def test_delete_all_segments(self, store, sample_segments):
        """Test deleting all segments for a session."""
        store.add(sample_segments, session_id="session_1")

        store.delete("session_1")

        # Verify all deleted
        segments = store.get("session_1")
        assert len(segments) == 0

    def test_prune_expired_segments(self, store):
        """Test pruning expired segments."""
        # Create segments with old timestamps
        old_segment = ContextSegment(
            type=ContextType.BACKGROUND,
            content="Old content",
            tokens=10,
        )
        old_segment.metadata.created_at = datetime.now() - timedelta(hours=48)

        new_segment = ContextSegment(
            type=ContextType.BACKGROUND,
            content="New content",
            tokens=10,
        )

        store.add([old_segment, new_segment], session_id="session_1")

        # Prune (default TTL is 24 hours)
        pruned_count = store.prune("session_1")

        assert pruned_count == 1
        remaining = store.get("session_1")
        assert len(remaining) == 1
        assert remaining[0].id == new_segment.id

    def test_prune_low_priority(self, store):
        """Test pruning low priority segments."""
        segments = [
            ContextSegment(
                type=ContextType.BACKGROUND,
                priority=ContextPriority.CRITICAL,
                content="Critical content",
                tokens=10,
            ),
            ContextSegment(
                type=ContextType.BACKGROUND,
                priority=ContextPriority.LOW,
                content="Low priority content",
                tokens=10,
            ),
        ]
        store.add(segments, session_id="session_1")

        # Prune with min_priority=MEDIUM
        pruned_count = store.prune(
            "session_1",
            min_priority=ContextPriority.MEDIUM
        )

        assert pruned_count == 1
        remaining = store.get("session_1")
        assert len(remaining) == 1
        assert remaining[0].priority == ContextPriority.CRITICAL

    def test_lru_eviction(self, store):
        """Test LRU eviction when max_segments exceeded."""
        store.max_segments = 5

        # Add 6 segments (should trigger eviction)
        segments = [
            ContextSegment(
                type=ContextType.BACKGROUND,
                priority=ContextPriority.LOW,
                content=f"Segment {i}",
                tokens=10,
            )
            for i in range(6)
        ]
        store.add(segments, session_id="session_1")

        # Should have only 5 segments
        remaining = store.get("session_1")
        assert len(remaining) <= 5

    def test_get_by_ids(self, store, sample_segments):
        """Test retrieving specific segments by IDs."""
        store.add(sample_segments, session_id="session_1")

        segment_ids = [sample_segments[0].id, sample_segments[2].id]
        segments = store.get_by_ids("session_1", segment_ids)

        assert len(segments) == 2
        assert all(s.id in segment_ids for s in segments)

    def test_count(self, store, sample_segments):
        """Test counting segments."""
        store.add(sample_segments, session_id="session_1")

        count = store.count("session_1")
        assert count == 4

    def test_count_empty_session(self, store):
        """Test counting nonexistent session."""
        count = store.count("nonexistent")
        assert count == 0

    def test_get_all_sessions(self, store):
        """Test getting all session IDs."""
        segments1 = [ContextSegment(type=ContextType.TASK, content="Test 1", tokens=5)]
        segments2 = [ContextSegment(type=ContextType.TASK, content="Test 2", tokens=5)]

        store.add(segments1, session_id="session_1")
        store.add(segments2, session_id="session_2")

        sessions = store.get_all_sessions()

        assert len(sessions) == 2
        assert "session_1" in sessions
        assert "session_2" in sessions

    def test_clear_all(self, store, sample_segments):
        """Test clearing all storage."""
        store.add(sample_segments, session_id="session_1")
        store.add(sample_segments, session_id="session_2")

        store.clear_all()

        assert len(store.get_all_sessions()) == 0

    def test_access_tracking(self, store, sample_segments):
        """Test that accessing segments updates metadata."""
        store.add(sample_segments, session_id="session_1")

        segment_id = sample_segments[0].id
        initial_count = sample_segments[0].metadata.access_count

        # Access the segment
        store.get_by_ids("session_1", [segment_id])

        # Retrieve again to check updated count
        segments = store.get_by_ids("session_1", [segment_id])
        assert segments[0].metadata.access_count > initial_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
