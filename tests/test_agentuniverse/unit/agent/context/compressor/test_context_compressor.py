# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/05 09:20
# @Author  : Yue Wang
# @FileName: test_context_compressor.py
"""Unit tests for base ContextCompressor helpers and metrics."""

import pytest
from agentuniverse.agent.context.compressor.context_compressor import ContextCompressor, CompressionMetrics
from agentuniverse.agent.context.context_model import ContextSegment, ContextMetadata, ContextType, ContextPriority

class _SimpleCompressor(ContextCompressor):
    """Concrete compressor used to exercise the base class helpers."""

    def compress(self, segments, target_tokens, **kwargs):
        raise NotImplementedError

    def estimate_information_loss(self, original_segments, compressed_segments, **kwargs):
        return 0.0


def _seg(priority, tokens):
    """Segment with a deterministic decay score of exactly 1.0."""
    return ContextSegment(type=ContextType.BACKGROUND, priority=priority, content="sample",
                          tokens=tokens,
                          metadata=ContextMetadata(relevance_score=1.0, decay_rate=0.0))


FIVE = [_seg(p, n) for p, n in zip(
    (ContextPriority.CRITICAL, ContextPriority.HIGH, ContextPriority.MEDIUM,
     ContextPriority.LOW, ContextPriority.EPHEMERAL), (5, 6, 7, 8, 9))]
ORDER = [ContextPriority.CRITICAL, ContextPriority.HIGH, ContextPriority.MEDIUM, ContextPriority.LOW, ContextPriority.EPHEMERAL]


class TestContextCompressor:
    """Test base compressor defaults, helpers and validation."""

    @pytest.fixture
    def compressor(self):
        """Create a concrete compressor subclass instance."""
        return _SimpleCompressor()

    def test_defaults_and_abstract(self, compressor):
        assert compressor.compression_ratio == 0.5
        assert compressor.preserve_critical is True
        assert compressor.max_compression_time_ms == 1000.0
        assert compressor.component_type.value == "CONTEXT_COMPRESSOR"
        with pytest.raises(TypeError):
            ContextCompressor()

    def test_token_and_priority_helpers(self, compressor):
        assert compressor.calculate_total_tokens(FIVE) == 35
        assert compressor.calculate_total_tokens([]) == 0
        kept = compressor.filter_by_priority(FIVE, "high")
        assert [s.priority for s in kept] == [ContextPriority.CRITICAL, ContextPriority.HIGH]
        assert compressor.filter_by_priority(FIVE, "bogus") == FIVE[:3]  # unknown falls back to MEDIUM

    def test_sort_by_importance(self, compressor):
        assert [s.priority for s in compressor.sort_by_importance(FIVE)] == ORDER
        ascending = compressor.sort_by_importance(FIVE, reverse=False)
        assert ascending[0].priority == ContextPriority.EPHEMERAL
        assert ascending[-1].priority == ContextPriority.CRITICAL

    def test_create_metrics(self, compressor):
        kept = FIVE[:3]
        metrics = compressor.create_metrics(FIVE, kept, 12.5, "test")
        assert (metrics.original_tokens, metrics.compressed_tokens) == (35, 18)
        assert metrics.compression_ratio == pytest.approx(18 / 35)
        assert metrics.segments_removed == 2
        assert metrics.segments_preserved == 3
        assert metrics.information_loss_estimate == 0.0 and metrics.strategy_used == "test"
        assert compressor.create_metrics([], [], 1.0, "test").compression_ratio == 1.0
        defaults = CompressionMetrics(original_tokens=100, compressed_tokens=40, compression_ratio=0.4)
        assert (defaults.segments_removed, defaults.compression_time_ms,
                defaults.information_loss_estimate, defaults.strategy_used) == (0, 0.0, 0.0, "unknown")

    def test_validate_compression_result(self, compressor):
        kept = FIVE[:3]
        valid = compressor.create_metrics(FIVE, kept, 1.0, "test")
        assert compressor.validate_compression_result(kept, 100, valid) is True
        assert compressor.validate_compression_result([], 100, valid) is False
        big = CompressionMetrics(original_tokens=10, compressed_tokens=80, compression_ratio=8.0)
        assert compressor.validate_compression_result(kept[:1], 70, big) is False
        lossy = CompressionMetrics(original_tokens=10, compressed_tokens=5, compression_ratio=0.5,
                                   information_loss_estimate=0.9)
        assert compressor.validate_compression_result(kept[:1], 70, lossy) is False
        slow = CompressionMetrics(original_tokens=10, compressed_tokens=5, compression_ratio=0.5,
                                  compression_time_ms=5000.0)
        assert compressor.validate_compression_result(kept[:1], 70, slow) is False
