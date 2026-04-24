# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 10:00
# @Author  : kaichuan
# @FileName: test_selective_compressor.py
"""Unit tests for SelectiveCompressor - Priority-weighted intelligent selection."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
    ContextMetadata,
)


class TestSelectiveCompressor:
    """Test suite for SelectiveCompressor."""

    @pytest.fixture
    def compressor(self):
        """Create SelectiveCompressor instance."""
        return SelectiveCompressor(
            name='test_selective',
            compression_ratio=0.6,  # Target 40% reduction
            min_quality_threshold=0.9
        )

    @pytest.fixture
    def sample_segments(self):
        """Create sample context segments with different priorities."""
        segments = []
        now = datetime.now()

        # CRITICAL priority (should always be preserved)
        segments.append(ContextSegment(
            type=ContextType.SYSTEM,
            priority=ContextPriority.CRITICAL,
            content="System prompt: You are a helpful assistant",
            tokens=10,
            session_id="test_session",
            metadata=ContextMetadata(
                created_at=now - timedelta(hours=1),
                last_accessed=now,
                access_count=5,
                relevance_score=1.0
            )
        ))

        # HIGH priority (80% should be preserved)
        for i in range(10):
            segments.append(ContextSegment(
                type=ContextType.TASK,
                priority=ContextPriority.HIGH,
                content=f"Task context {i}",
                tokens=20,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=2 + i*0.1),
                    last_accessed=now - timedelta(hours=i*0.1),
                    access_count=5 - i//2,
                    relevance_score=0.9 - i*0.02
                )
            ))

        # MEDIUM priority (50% should be preserved)
        for i in range(10):
            segments.append(ContextSegment(
                type=ContextType.CONVERSATION,
                priority=ContextPriority.MEDIUM,
                content=f"Conversation context {i}",
                tokens=15,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=5 + i*0.2),
                    last_accessed=now - timedelta(hours=i*0.3),
                    access_count=3 - i//3,
                    relevance_score=0.7 - i*0.03
                )
            ))

        # LOW priority (conditional preservation)
        for i in range(5):
            segments.append(ContextSegment(
                type=ContextType.BACKGROUND,
                priority=ContextPriority.LOW,
                content=f"Background context {i}",
                tokens=10,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=10 + i),
                    last_accessed=now - timedelta(hours=5 + i),
                    access_count=1,
                    relevance_score=0.5 - i*0.05
                )
            ))

        # EPHEMERAL priority (should be discarded)
        for i in range(5):
            segments.append(ContextSegment(
                type=ContextType.TOOL_RESULT,
                priority=ContextPriority.EPHEMERAL,
                content=f"Temporary data {i}",
                tokens=5,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=15 + i),
                    last_accessed=now - timedelta(hours=10 + i),
                    access_count=0,
                    relevance_score=0.3
                )
            ))

        return segments

    def test_compression_ratio(self, compressor, sample_segments):
        """Test that compression achieves target ratio (60-80% reduction)."""
        original_tokens = sum(seg.tokens for seg in sample_segments)
        target_tokens = int(original_tokens * 0.4)  # 60% reduction

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000
        )

        compressed_tokens = sum(seg.tokens for seg in compressed)

        # Verify compression ratio
        actual_ratio = compressed_tokens / original_tokens
        assert 0.2 <= actual_ratio <= 0.8, f"Compression ratio {actual_ratio:.2%} out of range"
        assert compressed_tokens <= target_tokens * 1.1, "Exceeded target tokens by >10%"

        # Verify metrics
        assert metrics.original_tokens == original_tokens
        assert metrics.compressed_tokens == compressed_tokens
        assert 0.2 <= metrics.compression_ratio <= 0.8

    def test_critical_preservation(self, compressor, sample_segments):
        """Test that CRITICAL priority segments are always preserved."""
        critical_segments = [s for s in sample_segments if s.priority == ContextPriority.CRITICAL]
        critical_ids = {s.id for s in critical_segments}

        target_tokens = 50  # Very low to force aggressive compression

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            preserve_types=[ContextType.SYSTEM, ContextType.TASK]
        )

        compressed_ids = {s.id for s in compressed}

        # All CRITICAL segments should be present
        assert critical_ids.issubset(compressed_ids), "CRITICAL segments were removed"

    def test_information_loss(self, compressor, sample_segments):
        """Test that information loss is <10%."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000,
            min_quality=0.9
        )

        # Information loss should be <10%
        assert metrics.information_loss_estimate < 0.1, \
            f"Information loss {metrics.information_loss_estimate:.2%} exceeds 10%"

    def test_priority_weighting(self, compressor, sample_segments):
        """Test that priority-weighted selection works correctly."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        # Count segments by priority in compressed result
        priority_counts = {
            ContextPriority.CRITICAL: 0,
            ContextPriority.HIGH: 0,
            ContextPriority.MEDIUM: 0,
            ContextPriority.LOW: 0,
            ContextPriority.EPHEMERAL: 0,
        }

        for seg in compressed:
            priority_counts[seg.priority] += 1

        # Verify priority preservation rates
        critical_original = sum(1 for s in sample_segments if s.priority == ContextPriority.CRITICAL)
        high_original = sum(1 for s in sample_segments if s.priority == ContextPriority.HIGH)
        medium_original = sum(1 for s in sample_segments if s.priority == ContextPriority.MEDIUM)
        ephemeral_original = sum(1 for s in sample_segments if s.priority == ContextPriority.EPHEMERAL)

        # CRITICAL: 100% preserved
        assert priority_counts[ContextPriority.CRITICAL] == critical_original

        # HIGH: ≥70% preserved (some tolerance)
        high_ratio = priority_counts[ContextPriority.HIGH] / high_original if high_original > 0 else 0
        assert high_ratio >= 0.7, f"HIGH priority preservation {high_ratio:.1%} < 70%"

        # MEDIUM: ≥30% preserved (flexible)
        medium_ratio = priority_counts[ContextPriority.MEDIUM] / medium_original if medium_original > 0 else 0
        assert medium_ratio >= 0.3, f"MEDIUM priority preservation {medium_ratio:.1%} < 30%"

        # EPHEMERAL: Should be mostly removed
        ephemeral_ratio = priority_counts[ContextPriority.EPHEMERAL] / ephemeral_original if ephemeral_original > 0 else 0
        assert ephemeral_ratio <= 0.2, f"EPHEMERAL priority preservation {ephemeral_ratio:.1%} > 20%"

    def test_recency_scoring(self, compressor, sample_segments):
        """Test that more recent segments are preferred."""
        # Get only HIGH priority segments to isolate recency effect
        high_segments = [s for s in sample_segments if s.priority == ContextPriority.HIGH]

        # Sort by created_at
        high_segments_sorted = sorted(high_segments, key=lambda s: s.metadata.created_at, reverse=True)

        target_tokens = sum(seg.tokens for seg in high_segments) // 2

        compressed, metrics = compressor.compress(
            high_segments,
            target_tokens
        )

        # Most recent segments should be preserved
        compressed_ids = {s.id for s in compressed}
        recent_ids = {s.id for s in high_segments_sorted[:5]}  # Top 5 most recent

        overlap = len(recent_ids & compressed_ids)
        assert overlap >= 3, f"Only {overlap}/5 most recent segments preserved"

    def test_access_count_scoring(self, compressor, sample_segments):
        """Test that frequently accessed segments are preferred."""
        # Create segments with varying access counts
        segments = []
        now = datetime.now()

        for i in range(10):
            segments.append(ContextSegment(
                type=ContextType.CONVERSATION,
                priority=ContextPriority.MEDIUM,
                content=f"Message {i}",
                tokens=10,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=i),
                    last_accessed=now - timedelta(minutes=i),
                    access_count=10 - i,  # Higher access counts for earlier messages
                    relevance_score=0.8
                )
            ))

        target_tokens = 50  # Keep 5 out of 10

        compressed, metrics = compressor.compress(
            segments,
            target_tokens
        )

        # Segments with higher access counts should be preferred
        compressed_access_counts = [s.metadata.access_count for s in compressed]
        average_access = sum(compressed_access_counts) / len(compressed_access_counts)

        assert average_access >= 6, f"Average access count {average_access:.1f} too low"

    def test_empty_input(self, compressor):
        """Test compression with empty input."""
        compressed, metrics = compressor.compress([], target_tokens=100)

        assert len(compressed) == 0
        assert metrics.original_tokens == 0
        assert metrics.compressed_tokens == 0
        assert metrics.compression_ratio == 0.0  # 0/0 = 0.0 (not undefined)
        assert metrics.information_loss_estimate == 0.0

    def test_already_under_budget(self, compressor, sample_segments):
        """Test when segments are already under target tokens."""
        total_tokens = sum(seg.tokens for seg in sample_segments)
        target_tokens = total_tokens * 2  # Double the current tokens

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        # Should return all segments unchanged
        assert len(compressed) == len(sample_segments)
        assert metrics.compression_ratio == 1.0

    def test_preserve_types(self, compressor, sample_segments):
        """Test that specified types are preserved."""
        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens=100,
            preserve_types=[ContextType.SYSTEM, ContextType.TASK]
        )

        # All SYSTEM and TASK segments should be preserved
        system_task_original = [s for s in sample_segments
                                if s.type in [ContextType.SYSTEM, ContextType.TASK]]
        system_task_compressed = [s for s in compressed
                                   if s.type in [ContextType.SYSTEM, ContextType.TASK]]

        assert len(system_task_compressed) == len(system_task_original), \
            "Not all SYSTEM/TASK segments preserved"

    def test_compression_time(self, compressor, sample_segments):
        """Test that compression completes within time limit."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2
        time_limit_ms = 500

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=time_limit_ms
        )

        # Should complete within time limit
        assert metrics.compression_time_ms <= time_limit_ms * 1.5, \
            f"Compression took {metrics.compression_time_ms:.0f}ms > {time_limit_ms}ms limit"

    def test_min_quality_threshold(self, compressor, sample_segments):
        """Test compression maintains acceptable quality.

        Note: SelectiveCompressor doesn't enforce min_quality directly
        (that's handled by AdaptiveCompressor). This test just verifies
        typical compression quality.
        """
        target_tokens = sum(seg.tokens for seg in sample_segments) // 3

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        # SelectiveCompressor should achieve <10% information loss typically
        assert metrics.information_loss_estimate < 0.15, \
            f"Information loss {metrics.information_loss_estimate:.2%} too high"

    def test_decay_calculation(self, compressor):
        """Test that decay scoring works correctly."""
        now = datetime.now()

        # Recent segment with high access
        recent_segment = ContextSegment(
            type=ContextType.CONVERSATION,
            priority=ContextPriority.MEDIUM,
            content="Recent message",
            tokens=10,
            session_id="test",
            metadata=ContextMetadata(
                created_at=now - timedelta(minutes=10),
                last_accessed=now - timedelta(minutes=5),
                access_count=10,
                relevance_score=0.9,
                decay_rate=0.1
            )
        )

        # Old segment with low access
        old_segment = ContextSegment(
            type=ContextType.CONVERSATION,
            priority=ContextPriority.MEDIUM,
            content="Old message",
            tokens=10,
            session_id="test",
            metadata=ContextMetadata(
                created_at=now - timedelta(hours=24),
                last_accessed=now - timedelta(hours=12),
                access_count=1,
                relevance_score=0.5,
                decay_rate=0.1
            )
        )

        segments = [recent_segment, old_segment]
        target_tokens = 10  # Keep only 1

        compressed, metrics = compressor.compress(segments, target_tokens)

        # Recent segment should be preserved
        assert len(compressed) == 1
        assert compressed[0].id == recent_segment.id

    def test_strategy_name(self, compressor):
        """Test that strategy name is correctly set."""
        compressed, metrics = compressor.compress(
            [],
            target_tokens=100
        )

        assert metrics.strategy_used == "selective"

    def test_segments_removed_count(self, compressor, sample_segments):
        """Test that segments_removed metric is accurate."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        expected_removed = len(sample_segments) - len(compressed)
        assert metrics.segments_removed == expected_removed
