# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 16:00
# @Author  : kaichuan
# @FileName: truncate_compressor.py
"""Truncate compressor - simple content truncation strategy.

This compressor provides fast compression by truncating individual segment
content to fit within token budgets. It's the fastest compression strategy
but has higher information loss compared to selective or summarization approaches.

Use cases:
- Time-critical operations where speed is essential
- Low-priority content that doesn't require preservation
- Fallback when other strategies fail
"""

import time
from typing import List, Optional

from agentuniverse.agent.context.compressor.context_compressor import (
    ContextCompressor,
    CompressionMetrics,
)
from agentuniverse.agent.context.context_model import ContextSegment, ContextPriority


class TruncateCompressor(ContextCompressor):
    """Simple truncation compression strategy.

    Truncates segment content to fit within target token budget. Preserves
    CRITICAL priority segments and truncates others proportionally based on
    importance scores.

    Algorithm:
    1. Preserve all CRITICAL priority segments
    2. Calculate available tokens for other segments
    3. Sort segments by importance (priority * decay * access)
    4. Truncate each segment proportionally to importance
    5. Remove segments with <10 tokens after truncation

    Attributes:
        min_segment_tokens: Minimum tokens to keep per segment (default: 10)
        truncate_marker: String appended to truncated content
    """

    min_segment_tokens: int = 10
    truncate_marker: str = "... [truncated]"

    def compress(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        **kwargs
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Compress segments through content truncation.

        Args:
            segments: List of context segments to compress
            target_tokens: Target token count after compression
            **kwargs: Additional parameters (unused)

        Returns:
            Tuple of (compressed_segments, compression_metrics)

        Raises:
            ValueError: If target_tokens <= 0 or segments is empty
        """
        start_time = time.time()

        if not segments:
            raise ValueError("Cannot compress empty segment list")

        if target_tokens <= 0:
            raise ValueError(f"Invalid target_tokens: {target_tokens}")

        original_segments = segments.copy()

        # Step 1: Separate CRITICAL from other segments
        critical_segments = [
            seg for seg in segments if seg.priority == ContextPriority.CRITICAL
        ]
        other_segments = [
            seg for seg in segments if seg.priority != ContextPriority.CRITICAL
        ]

        critical_tokens = self.calculate_total_tokens(critical_segments)

        # Step 2: Check if CRITICAL alone exceeds target
        if critical_tokens >= target_tokens:
            # Even CRITICAL needs truncation (rare case)
            compressed = self._truncate_segments(
                critical_segments, target_tokens, preserve_all=True
            )
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = self.create_metrics(
                original_segments, compressed, elapsed_ms, "truncate"
            )
            return compressed, metrics

        # Step 3: Allocate remaining budget to other segments
        available_tokens = target_tokens - critical_tokens

        if not other_segments or available_tokens <= 0:
            # Only CRITICAL segments fit
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = self.create_metrics(
                original_segments, critical_segments, elapsed_ms, "truncate"
            )
            return critical_segments, metrics

        # Step 4: Truncate other segments proportionally
        compressed_other = self._truncate_segments(
            other_segments, available_tokens, preserve_all=False
        )

        # Step 5: Combine results
        result = critical_segments + compressed_other

        elapsed_ms = (time.time() - start_time) * 1000
        metrics = self.create_metrics(
            original_segments, result, elapsed_ms, "truncate",
            segments_compressed=len(compressed_other)
        )

        return result, metrics

    def _truncate_segments(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        preserve_all: bool
    ) -> List[ContextSegment]:
        """Truncate segments to fit within token budget.

        Args:
            segments: Segments to truncate
            target_tokens: Target token count
            preserve_all: If True, preserve all segments (even if tiny)

        Returns:
            List of truncated segments
        """
        if not segments:
            return []

        # Sort by importance (most important first)
        sorted_segments = self.sort_by_importance(segments, reverse=True)

        current_tokens = self.calculate_total_tokens(sorted_segments)

        if current_tokens <= target_tokens:
            # No truncation needed
            return sorted_segments

        # Calculate proportional allocation
        total_importance = sum(
            self._calculate_importance(seg) for seg in sorted_segments
        )

        compressed = []
        remaining_tokens = target_tokens

        for seg in sorted_segments:
            if remaining_tokens <= 0 and not preserve_all:
                break

            # Allocate tokens proportionally to importance
            importance = self._calculate_importance(seg)
            allocated_tokens = int(
                (importance / total_importance) * target_tokens
            ) if total_importance > 0 else 0

            # Ensure minimum tokens
            if preserve_all:
                allocated_tokens = max(allocated_tokens, self.min_segment_tokens)
            elif allocated_tokens < self.min_segment_tokens:
                continue  # Skip segments that would be too small

            # Truncate content if needed
            if seg.tokens > allocated_tokens:
                truncated_seg = self._truncate_content(seg, allocated_tokens)
                compressed.append(truncated_seg)
                remaining_tokens -= truncated_seg.tokens
            else:
                # No truncation needed for this segment
                compressed.append(seg)
                remaining_tokens -= seg.tokens

        return compressed

    def _truncate_content(
        self,
        segment: ContextSegment,
        target_tokens: int
    ) -> ContextSegment:
        """Truncate a single segment's content.

        Args:
            segment: Segment to truncate
            target_tokens: Target token count

        Returns:
            New segment with truncated content
        """
        if target_tokens <= 0:
            target_tokens = self.min_segment_tokens

        # Estimate character ratio (rough: 1 token ≈ 4 characters)
        chars_per_token = len(segment.content) / segment.tokens if segment.tokens > 0 else 4
        target_chars = int(target_tokens * chars_per_token)

        # Reserve space for truncate marker
        marker_tokens = len(self.truncate_marker) // 4
        target_chars -= len(self.truncate_marker)
        target_tokens -= marker_tokens

        if target_chars <= 0:
            target_chars = 10  # Minimum

        # Truncate content
        truncated_content = segment.content[:target_chars] + self.truncate_marker

        # Create new segment with truncated content
        truncated_seg = ContextSegment(
            type=segment.type,
            priority=segment.priority,
            content=truncated_content,
            tokens=target_tokens,
            session_id=segment.session_id,
            parent_id=segment.parent_id,
            related_ids=segment.related_ids.copy(),
        )

        # Preserve metadata reference (mark as compressed)
        truncated_seg.metadata = segment.metadata.model_copy()
        truncated_seg.metadata.compressed = True
        truncated_seg.metadata.version += 1

        return truncated_seg

    def _calculate_importance(self, segment: ContextSegment) -> float:
        """Calculate importance score for a segment.

        Args:
            segment: Segment to score

        Returns:
            Importance score (higher = more important)
        """
        priority_weights = {
            ContextPriority.CRITICAL: 10.0,
            ContextPriority.HIGH: 5.0,
            ContextPriority.MEDIUM: 2.0,
            ContextPriority.LOW: 1.0,
            ContextPriority.EPHEMERAL: 0.5,
        }

        priority_weight = priority_weights.get(segment.priority, 2.0)
        decay = segment.calculate_decay()
        access_bonus = 1.0 + (segment.metadata.access_count * 0.1)

        return priority_weight * decay * access_bonus

    def estimate_information_loss(
        self,
        original_segments: List[ContextSegment],
        compressed_segments: List[ContextSegment],
        **kwargs
    ) -> float:
        """Estimate information loss from truncation.

        For truncation, information loss is estimated as:
        loss = 1.0 - (compressed_tokens / original_tokens)

        This is a rough estimate; actual semantic loss may vary.

        Args:
            original_segments: Original segments
            compressed_segments: Compressed segments
            **kwargs: Additional parameters (unused)

        Returns:
            Information loss estimate (0.0-1.0)
        """
        original_tokens = self.calculate_total_tokens(original_segments)
        compressed_tokens = self.calculate_total_tokens(compressed_segments)

        if original_tokens == 0:
            return 0.0

        # Basic loss estimate: proportion of tokens removed
        token_loss = 1.0 - (compressed_tokens / original_tokens)

        # Adjust for segment removal (losing entire segments is worse)
        original_ids = {seg.id for seg in original_segments}
        compressed_ids = {seg.id for seg in compressed_segments}
        segments_lost = len(original_ids - compressed_ids)
        segment_loss_penalty = (segments_lost / len(original_segments)) * 0.2

        total_loss = min(1.0, token_loss + segment_loss_penalty)

        return total_loss
