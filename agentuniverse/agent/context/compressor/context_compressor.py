# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 16:00
# @Author  : kaichuan
# @FileName: context_compressor.py
"""Base class for context compression strategies.

Context compression is critical for managing token budgets while preserving
information quality. This module defines the abstract interface for all
compression strategies.
"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.agent.context.context_model import ContextSegment


class CompressionMetrics(BaseModel):
    """Metrics for compression quality assessment.

    These metrics help evaluate compression effectiveness and guide
    adaptive compression strategy selection.
    """

    original_tokens: int
    compressed_tokens: int
    compression_ratio: float = Field(
        description="compressed_tokens / original_tokens (target: 0.2-0.4 for 60-80% reduction)"
    )
    information_loss_estimate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated information loss (0.0 = no loss, 1.0 = total loss, target: <0.1)"
    )
    segments_removed: int = Field(default=0)
    segments_compressed: int = Field(default=0)
    segments_preserved: int = Field(default=0)
    compression_time_ms: float = Field(default=0.0)
    strategy_used: str = Field(default="unknown")


class ContextCompressor(ComponentBase):
    """Abstract base class for context compression strategies.

    All compression strategies must inherit from this class and implement
    the compress() method. The base class provides common utilities for
    metrics calculation and segment evaluation.

    Attributes:
        compression_ratio: Target compression ratio (0.0-1.0)
        preserve_critical: Whether to preserve CRITICAL priority segments
        max_compression_time_ms: Maximum time allowed for compression
    """

    component_type: ComponentEnum = ComponentEnum.CONTEXT_COMPRESSOR

    compression_ratio: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Target compression ratio (0.5 = 50% reduction)"
    )
    preserve_critical: bool = Field(
        default=True,
        description="Always preserve CRITICAL priority segments"
    )
    max_compression_time_ms: float = Field(
        default=1000.0,
        description="Maximum compression time in milliseconds"
    )

    @abstractmethod
    def compress(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        **kwargs
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Compress segments to fit within target token budget.

        This is the core method that each compression strategy must implement.
        The strategy should reduce the total tokens while preserving as much
        information as possible.

        Args:
            segments: List of context segments to compress
            target_tokens: Target token count after compression
            **kwargs: Additional strategy-specific parameters

        Returns:
            Tuple of:
                - List of compressed/selected segments
                - CompressionMetrics with quality assessment

        Raises:
            ValueError: If target_tokens is invalid or segments is empty
        """
        pass

    @abstractmethod
    def estimate_information_loss(
        self,
        original_segments: List[ContextSegment],
        compressed_segments: List[ContextSegment],
        **kwargs
    ) -> float:
        """Estimate information loss from compression.

        This method provides a quality metric for compression effectiveness.
        Different strategies may use different approaches:
        - TruncateCompressor: Based on content overlap
        - SelectiveCompressor: Based on priority and decay scores
        - SummarizeCompressor: Based on semantic similarity (BLEU/ROUGE)

        Args:
            original_segments: Original segments before compression
            compressed_segments: Segments after compression
            **kwargs: Additional parameters for estimation

        Returns:
            Information loss estimate (0.0-1.0, where 0.0 = no loss)
        """
        pass

    def calculate_total_tokens(self, segments: List[ContextSegment]) -> int:
        """Calculate total tokens in segment list.

        Args:
            segments: List of segments

        Returns:
            Total token count
        """
        return sum(seg.tokens for seg in segments)

    def filter_by_priority(
        self,
        segments: List[ContextSegment],
        min_priority: str
    ) -> List[ContextSegment]:
        """Filter segments by minimum priority level.

        Priority hierarchy: CRITICAL > HIGH > MEDIUM > LOW > EPHEMERAL

        Args:
            segments: List of segments to filter
            min_priority: Minimum priority level

        Returns:
            Filtered segments meeting priority threshold
        """
        priority_order = {
            "ephemeral": 0,
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        min_level = priority_order.get(min_priority.lower(), 2)

        return [
            seg for seg in segments
            if priority_order.get(seg.priority.value.lower(), 2) >= min_level
        ]

    def sort_by_importance(
        self,
        segments: List[ContextSegment],
        reverse: bool = True
    ) -> List[ContextSegment]:
        """Sort segments by importance score.

        Importance is calculated as:
        importance = priority_weight * decay_score * (1 + access_count * 0.1)

        Args:
            segments: List of segments to sort
            reverse: If True, sort descending (most important first)

        Returns:
            Sorted segment list
        """
        priority_weights = {
            "critical": 10.0,
            "high": 5.0,
            "medium": 2.0,
            "low": 1.0,
            "ephemeral": 0.5,
        }

        def importance_score(seg: ContextSegment) -> float:
            priority_weight = priority_weights.get(seg.priority.value.lower(), 2.0)
            decay = seg.calculate_decay()
            access_bonus = 1.0 + (seg.metadata.access_count * 0.1)
            return priority_weight * decay * access_bonus

        return sorted(segments, key=importance_score, reverse=reverse)

    def create_metrics(
        self,
        original_segments: List[ContextSegment],
        compressed_segments: List[ContextSegment],
        compression_time_ms: float,
        strategy_name: str,
        **kwargs
    ) -> CompressionMetrics:
        """Create compression metrics for quality assessment.

        Args:
            original_segments: Original segments before compression
            compressed_segments: Segments after compression
            compression_time_ms: Time taken for compression
            strategy_name: Name of compression strategy used
            **kwargs: Additional metric parameters

        Returns:
            CompressionMetrics instance with calculated metrics
        """
        original_tokens = self.calculate_total_tokens(original_segments)
        compressed_tokens = self.calculate_total_tokens(compressed_segments)

        # Calculate compression ratio (lower = more compression)
        compression_ratio = (
            compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        )

        # Estimate information loss
        info_loss = self.estimate_information_loss(
            original_segments, compressed_segments, **kwargs
        )

        # Count segment changes
        original_ids = {seg.id for seg in original_segments}
        compressed_ids = {seg.id for seg in compressed_segments}

        segments_removed = len(original_ids - compressed_ids)
        segments_compressed = kwargs.get("segments_compressed", 0)
        segments_preserved = len(compressed_ids)

        return CompressionMetrics(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            information_loss_estimate=info_loss,
            segments_removed=segments_removed,
            segments_compressed=segments_compressed,
            segments_preserved=segments_preserved,
            compression_time_ms=compression_time_ms,
            strategy_used=strategy_name,
        )

    def validate_compression_result(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        metrics: CompressionMetrics
    ) -> bool:
        """Validate that compression meets quality standards.

        Checks:
        - Compressed tokens <= target_tokens
        - Information loss < 0.3 (30%)
        - Compression time < max_compression_time_ms
        - At least one segment preserved

        Args:
            segments: Compressed segments
            target_tokens: Target token count
            metrics: Compression metrics

        Returns:
            True if compression is valid, False otherwise
        """
        if len(segments) == 0:
            return False

        if metrics.compressed_tokens > target_tokens:
            return False

        if metrics.information_loss_estimate > 0.3:
            return False

        if metrics.compression_time_ms > self.max_compression_time_ms:
            return False

        return True
