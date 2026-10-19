# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/05 09:40
# @Author  : Yue Wang
# @FileName: test_truncate_compressor.py
"""Unit tests for TruncateCompressor deterministic behavior."""

import pytest
from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
from agentuniverse.agent.context.context_model import (
    ContextSegment, ContextType, ContextPriority,
)

CRITICAL = ContextSegment(type=ContextType.SYSTEM, priority=ContextPriority.CRITICAL,
                          content="system prompt keep", tokens=40)
OTHERS = [ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.MEDIUM,
                         content=ch * 400, tokens=100) for ch in "xyz"]
SAMPLE = [CRITICAL] + OTHERS


class TestTruncateCompressor:
    """Test the truncation strategy without external dependencies."""

    @pytest.fixture
    def compressor(self):
        """Create a TruncateCompressor instance."""
        return TruncateCompressor()

    def test_default_configuration(self, compressor):
        assert compressor.min_segment_tokens == 10
        assert compressor.truncate_marker == "... [truncated]"
        assert compressor.component_type.value == "CONTEXT_COMPRESSOR"

    def test_compress_validation(self, compressor):
        with pytest.raises(ValueError, match="empty"):
            compressor.compress([], 100)
        tiny = ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.MEDIUM,
                              content="x", tokens=5)
        with pytest.raises(ValueError, match="target_tokens"):
            compressor.compress([tiny], 0)

    def test_compress_under_budget_keeps_all(self, compressor):
        result, metrics = compressor.compress(SAMPLE, 1000)
        assert len(result) == len(SAMPLE)
        assert {s.id for s in result} == {s.id for s in SAMPLE}
        assert metrics.compressed_tokens == sum(s.tokens for s in SAMPLE)
        assert metrics.compression_ratio == 1.0

    def test_compress_respects_budget(self, compressor):
        result, metrics = compressor.compress(SAMPLE, 150)
        assert sum(s.tokens for s in result) <= 150
        assert result[0].id == CRITICAL.id
        assert result[0].content == "system prompt keep"
        truncated = result[1:]
        assert len(truncated) == 3
        assert all(s.content.endswith(compressor.truncate_marker) for s in truncated)
        assert metrics.original_tokens == 340
        assert metrics.strategy_used == "truncate"
        assert metrics.segments_compressed == 3

    def test_compress_critical_only_over_budget(self, compressor):
        segments = [ContextSegment(type=ContextType.SYSTEM, priority=ContextPriority.CRITICAL,
                                   content=ch * 240, tokens=60) for ch in "qr"]
        result, _ = compressor.compress(segments, 100)
        assert len(result) == 2
        assert sum(s.tokens for s in result) <= 100
        assert all(s.content.endswith(compressor.truncate_marker) for s in result)
        assert all(s.metadata.compressed for s in result)

    def test_truncate_content_mechanics(self, compressor):
        segment = ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.HIGH,
                                 content="C" * 80, tokens=20)
        clipped = compressor._truncate_content(segment, 8)
        assert clipped.content == "C" * 17 + compressor.truncate_marker
        assert clipped.tokens == 5
        assert clipped.metadata.compressed is True
        assert clipped.metadata.version == 2

    def test_estimate_information_loss(self, compressor):
        original = [ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.MEDIUM,
                                   content="a", tokens=100),
                    ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.MEDIUM,
                                   content="b", tokens=50)]
        kept = [original[0]]
        assert compressor.estimate_information_loss(original, kept) == pytest.approx(
            1 - 100 / 150 + 0.5 * 0.2)
        empty = [ContextSegment(type=ContextType.CONVERSATION, priority=ContextPriority.MEDIUM,
                                content="", tokens=0)]
        assert compressor.estimate_information_loss(empty, []) == 0.0
