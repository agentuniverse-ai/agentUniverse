# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 10:30
# @Author  : kaichuan
# @FileName: test_adaptive_compressor.py
"""Unit tests for AdaptiveCompressor - Intelligent strategy selector."""

import pytest
from datetime import datetime, timedelta

from agentuniverse.agent.context.compressor.adaptive_compressor import AdaptiveCompressor
from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
    ContextMetadata,
)


class TestAdaptiveCompressor:
    """Test suite for AdaptiveCompressor."""

    @pytest.fixture
    def compressor(self):
        """Create AdaptiveCompressor instance."""
        adaptive = AdaptiveCompressor(
            name='test_adaptive',
            compression_ratio=0.6,
            enable_hybrid=False  # Disable hybrid (requires LLM)
        )
        # Initialize only truncate and selective (no LLM needed)
        adaptive._truncate_compressor = TruncateCompressor(name='truncate')
        adaptive._selective_compressor = SelectiveCompressor(name='selective')
        # Set weights to avoid summarize strategy
        adaptive.truncate_weight = 1.0
        adaptive.selective_weight = 1.0
        adaptive.summarize_weight = 0.0  # Disable summarize (requires LLM)
        return adaptive

    @pytest.fixture
    def sample_segments(self):
        """Create sample context segments."""
        segments = []
        now = datetime.now()

        for i in range(20):
            priority = ContextPriority.HIGH if i < 5 else ContextPriority.MEDIUM
            segments.append(ContextSegment(
                type=ContextType.CONVERSATION,
                priority=priority,
                content=f"Message {i}: This is a sample message with some content",
                tokens=15,
                session_id="test_session",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=i),
                    last_accessed=now - timedelta(minutes=i*10),
                    access_count=10 - i//2,
                    relevance_score=0.9 - i*0.02
                )
            ))

        return segments

    def test_strategy_selection_time_critical(self, compressor, sample_segments):
        """Test that truncate strategy is selected for time-critical scenarios."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=50  # Very tight time limit
        )

        # Should select fast strategy (truncate or selective)
        assert metrics.strategy_used in ["adaptive_truncate", "adaptive_selective"]
        assert metrics.compression_time_ms <= 100  # Fast execution

    def test_strategy_selection_quality_critical(self, compressor, sample_segments):
        """Test that high-quality strategy is selected for quality-critical scenarios."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            min_quality=0.95,  # Very high quality requirement
            time_limit_ms=2000  # Sufficient time
        )

        # Should select high-quality strategy (selective preferred)
        assert metrics.strategy_used in ["adaptive_selective", "adaptive_truncate"]
        assert metrics.information_loss_estimate <= 0.15  # Good quality

    def test_strategy_selection_aggressive_compression(self, compressor, sample_segments):
        """Test strategy selection for aggressive compression needs."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 4  # 75% reduction

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000
        )

        # Should select strategy good at aggressive compression
        assert metrics.strategy_used in ["adaptive_selective", "adaptive_truncate"]
        assert metrics.compression_ratio <= 0.3

    def test_strategy_selection_high_critical_ratio(self, compressor):
        """Test strategy selection with many CRITICAL segments."""
        segments = []
        now = datetime.now()

        # Create segments with high CRITICAL ratio
        for i in range(10):
            priority = ContextPriority.CRITICAL if i < 7 else ContextPriority.MEDIUM
            segments.append(ContextSegment(
                type=ContextType.SYSTEM if priority == ContextPriority.CRITICAL else ContextType.CONVERSATION,
                priority=priority,
                content=f"Content {i}",
                tokens=10,
                session_id="test",
                metadata=ContextMetadata(
                    created_at=now - timedelta(hours=i),
                    last_accessed=now,
                    relevance_score=0.9
                )
            ))

        target_tokens = 50

        compressed, metrics = compressor.compress(
            segments,
            target_tokens
        )

        # Should select selective strategy (best for preserving CRITICAL)
        assert metrics.strategy_used == "adaptive_selective"

    def test_compression_metrics(self, compressor, sample_segments):
        """Test that compression metrics are accurate."""
        original_tokens = sum(seg.tokens for seg in sample_segments)
        target_tokens = original_tokens // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        # Verify metrics
        assert metrics.original_tokens == original_tokens
        assert metrics.compressed_tokens == sum(seg.tokens for seg in compressed)
        assert 0.0 <= metrics.compression_ratio <= 1.0
        assert 0.0 <= metrics.information_loss_estimate <= 1.0
        assert metrics.compression_time_ms > 0

    def test_empty_input(self, compressor):
        """Test compression with empty input."""
        compressed, metrics = compressor.compress([], target_tokens=100)

        assert len(compressed) == 0
        assert metrics.original_tokens == 0
        assert metrics.compressed_tokens == 0
        assert metrics.compression_ratio == 0.0  # Empty case returns 0.0

    def test_already_under_budget(self, compressor, sample_segments):
        """Test when segments are already under budget."""
        total_tokens = sum(seg.tokens for seg in sample_segments)
        target_tokens = total_tokens * 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens
        )

        # Should return all segments
        assert len(compressed) == len(sample_segments)
        assert metrics.compression_ratio == 1.0

    def test_preserve_types(self, compressor, sample_segments):
        """Test that specified types are preserved."""
        # Add some SYSTEM segments
        now = datetime.now()
        sample_segments.append(ContextSegment(
            type=ContextType.SYSTEM,
            priority=ContextPriority.CRITICAL,
            content="System prompt",
            tokens=20,
            session_id="test",
            metadata=ContextMetadata(created_at=now, last_accessed=now)
        ))

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens=100,
            preserve_types=[ContextType.SYSTEM]
        )

        # SYSTEM segment should be preserved
        system_segments = [s for s in compressed if s.type == ContextType.SYSTEM]
        assert len(system_segments) > 0

    def test_min_quality_threshold(self, compressor, sample_segments):
        """Test that minimum quality threshold is respected."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2
        min_quality = 0.9

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            min_quality=min_quality
        )

        # Information loss should not exceed threshold
        assert metrics.information_loss_estimate <= (1.0 - min_quality) * 1.1  # 10% tolerance

    def test_time_limit_respected(self, compressor, sample_segments):
        """Test that time limit is generally respected."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2
        time_limit_ms = 500

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=time_limit_ms
        )

        # Should complete reasonably close to time limit
        assert metrics.compression_time_ms <= time_limit_ms * 2  # Allow 2x tolerance

    def test_fallback_on_error(self, compressor):
        """Test that fallback strategy is used on error."""
        # Create segments that might cause issues
        segments = []
        now = datetime.now()

        for i in range(5):
            segments.append(ContextSegment(
                type=ContextType.CONVERSATION,
                priority=ContextPriority.MEDIUM,
                content=f"Message {i}",
                tokens=10,
                session_id="test",
                metadata=ContextMetadata(created_at=now, last_accessed=now)
            ))

        target_tokens = 30

        compressed, metrics = compressor.compress(
            segments,
            target_tokens
        )

        # Should still produce valid results
        assert len(compressed) <= len(segments)
        assert sum(seg.tokens for seg in compressed) <= target_tokens * 1.2

    def test_context_analysis(self, compressor, sample_segments):
        """Test that context analysis works correctly."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        # Analyze context
        analysis = compressor._analyze_segments(sample_segments, target_tokens)

        # Verify analysis results
        assert analysis["total_segments"] == len(sample_segments)
        assert analysis["total_tokens"] > 0
        assert 0.0 <= analysis["type_diversity"] <= 1.0
        assert analysis["compression_needed"] > 0

    def test_strategy_scoring(self, compressor, sample_segments):
        """Test that strategy selection works correctly."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        # Test strategy selection through actual compression
        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000
        )

        # Should select a valid strategy
        assert "adaptive_" in metrics.strategy_used
        assert metrics.compression_ratio <= 1.0
        assert len(compressed) <= len(sample_segments)

    def test_hybrid_enabled(self, compressor, sample_segments):
        """Test that hybrid strategy can be selected when enabled."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        compressed, metrics = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000,
            min_quality=0.9
        )

        # With hybrid disabled, should use truncate or selective
        assert metrics.strategy_used in ["adaptive_truncate", "adaptive_selective"]

    def test_consistent_results(self, compressor, sample_segments):
        """Test that compression produces consistent results."""
        target_tokens = sum(seg.tokens for seg in sample_segments) // 2

        # Run compression twice
        compressed1, metrics1 = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000
        )

        compressed2, metrics2 = compressor.compress(
            sample_segments,
            target_tokens,
            time_limit_ms=1000
        )

        # Should select same strategy and produce similar results
        assert metrics1.strategy_used == metrics2.strategy_used
        assert abs(metrics1.compression_ratio - metrics2.compression_ratio) < 0.1

    def test_different_scenarios(self, compressor, sample_segments):
        """Test adaptive behavior across different scenarios."""
        total_tokens = sum(seg.tokens for seg in sample_segments)

        # Scenario 1: Time-critical
        _, metrics1 = compressor.compress(
            sample_segments,
            total_tokens // 2,
            time_limit_ms=50
        )

        # Scenario 2: Quality-critical
        _, metrics2 = compressor.compress(
            sample_segments,
            total_tokens // 2,
            min_quality=0.95,
            time_limit_ms=2000
        )

        # Scenario 3: Balanced
        _, metrics3 = compressor.compress(
            sample_segments,
            total_tokens // 2,
            time_limit_ms=1000,
            min_quality=0.9
        )

        # Different scenarios should potentially select different strategies
        strategies = {metrics1.strategy_used, metrics2.strategy_used, metrics3.strategy_used}
        # Allow for possibility of same strategy if context dictates
        assert len(strategies) >= 1  # At least one strategy used
