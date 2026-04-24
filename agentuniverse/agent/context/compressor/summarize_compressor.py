# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 16:00
# @Author  : kaichuan
# @FileName: summarize_compressor.py
"""Summarize compressor - LLM-based semantic summarization strategy.

This compressor uses LLMs to generate semantic summaries of context segments,
preserving meaning while reducing token count. It achieves better semantic
preservation than truncation but is slower and uses LLM tokens.

Use cases:
- BACKGROUND and REFERENCE segments that can be condensed
- Data analysis context where semantic meaning is critical
- When token budget allows for LLM calls
"""

import time
from typing import List, Optional

from agentuniverse.agent.context.compressor.context_compressor import (
    ContextCompressor,
    CompressionMetrics,
)
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextPriority,
    ContextType,
)


class SummarizeCompressor(ContextCompressor):
    """LLM-based summarization compression strategy.

    Uses LLMs to generate concise summaries of context segments, preserving
    semantic meaning while reducing token count.

    Algorithm:
    1. Preserve CRITICAL segments (no summarization)
    2. Group segments by type and priority
    3. For each group, generate summary using LLM
    4. Replace original segments with summary segment
    5. Preserve metadata and relationships

    Attributes:
        llm_name: Name of LLM to use for summarization
        summarize_types: Types of segments to summarize (default: BACKGROUND, REFERENCE)
        summary_ratio: Target ratio for summaries (default: 0.3 = 70% reduction)
        batch_size: Number of segments to summarize together
        preserve_structure: Whether to preserve segment structure in summaries
    """

    llm_name: str = "default_llm"
    summarize_types: List[ContextType] = [
        ContextType.BACKGROUND,
        ContextType.REFERENCE,
        ContextType.CONVERSATION,
    ]
    summary_ratio: float = 0.3
    batch_size: int = 5
    preserve_structure: bool = True

    def __init__(self, **kwargs):
        """Initialize summarize compressor."""
        super().__init__(**kwargs)
        self._llm = None

    def initialize_by_component_configer(self, component_configer) -> 'SummarizeCompressor':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # Initialize LLM for summarization
        if self.llm_name:
            from agentuniverse.llm.llm_manager import LLMManager
            self._llm = LLMManager().get_instance_obj(self.llm_name)

        return self

    def compress(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        **kwargs
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Compress segments through LLM summarization.

        Args:
            segments: List of context segments to compress
            target_tokens: Target token count after compression
            **kwargs: Additional parameters:
                - preserve_segments: List of segment IDs to not summarize
                - summary_prompt: Custom summarization prompt template

        Returns:
            Tuple of (summarized_segments, compression_metrics)

        Raises:
            ValueError: If target_tokens <= 0 or segments is empty
            RuntimeError: If LLM is not available
        """
        start_time = time.time()

        if not segments:
            raise ValueError("Cannot compress empty segment list")

        if target_tokens <= 0:
            raise ValueError(f"Invalid target_tokens: {target_tokens}")

        if not self._llm:
            raise RuntimeError("LLM not initialized for summarization")

        original_segments = segments.copy()
        preserve_ids = set(kwargs.get("preserve_segments", []))

        # Step 1: Separate CRITICAL and preserve_ids
        critical_segments = [
            seg for seg in segments
            if seg.priority == ContextPriority.CRITICAL or seg.id in preserve_ids
        ]
        summarizable = [
            seg for seg in segments
            if seg.priority != ContextPriority.CRITICAL and seg.id not in preserve_ids
        ]

        critical_tokens = self.calculate_total_tokens(critical_segments)

        if critical_tokens >= target_tokens:
            # CRITICAL alone exceeds target, return as-is
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = self.create_metrics(
                original_segments, critical_segments, elapsed_ms, "summarize"
            )
            return critical_segments, metrics

        available_tokens = target_tokens - critical_tokens

        # Step 2: Group segments for summarization
        groups = self._group_for_summarization(summarizable)

        # Step 3: Summarize each group
        summarized = []
        tokens_used = 0

        for group_type, group_segments in groups.items():
            if tokens_used >= available_tokens:
                break

            # Calculate target tokens for this group
            group_target = min(
                available_tokens - tokens_used,
                int(self.calculate_total_tokens(group_segments) * self.summary_ratio)
            )

            if group_target <= 10:
                continue  # Skip groups with insufficient token budget

            # Generate summary
            summary_seg = self._summarize_group(
                group_segments,
                group_target,
                kwargs.get("summary_prompt")
            )

            if summary_seg:
                summarized.append(summary_seg)
                tokens_used += summary_seg.tokens

        # Step 4: Combine results
        result = critical_segments + summarized

        elapsed_ms = (time.time() - start_time) * 1000
        metrics = self.create_metrics(
            original_segments, result, elapsed_ms, "summarize",
            segments_compressed=len(summarized)
        )

        return result, metrics

    def _group_for_summarization(
        self,
        segments: List[ContextSegment]
    ) -> dict[str, List[ContextSegment]]:
        """Group segments by type for batch summarization.

        Args:
            segments: Segments to group

        Returns:
            Dictionary mapping group key to segment list
        """
        groups = {}

        for seg in segments:
            # Only summarize configured types
            if seg.type not in self.summarize_types:
                continue

            # Group by type and priority
            key = f"{seg.type.value}_{seg.priority.value}"

            if key not in groups:
                groups[key] = []
            groups[key].append(seg)

        return groups

    def _summarize_group(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        custom_prompt: Optional[str] = None
    ) -> Optional[ContextSegment]:
        """Summarize a group of segments using LLM.

        Args:
            segments: Segments to summarize
            target_tokens: Target token count for summary
            custom_prompt: Optional custom summarization prompt

        Returns:
            Summary segment or None if summarization fails
        """
        if not segments:
            return None

        # Build summarization prompt
        prompt = custom_prompt or self._build_summary_prompt(segments, target_tokens)

        try:
            # Call LLM for summarization
            # Note: Actual implementation depends on LLM interface
            # This is a placeholder that assumes a call() method
            if hasattr(self._llm, 'call'):
                response = self._llm.call(prompt)
                summary_text = response.get('content', '') if isinstance(response, dict) else str(response)
            else:
                # Fallback: use basic concatenation with truncation
                summary_text = self._basic_summarization(segments, target_tokens)

            # Count tokens in summary
            summary_tokens = self._count_tokens(summary_text)

            # Create summary segment
            summary_seg = ContextSegment(
                type=segments[0].type,
                priority=segments[0].priority,
                content=summary_text,
                tokens=summary_tokens,
                session_id=segments[0].session_id,
            )

            # Mark as compressed
            summary_seg.metadata.compressed = True
            summary_seg.metadata.source_type = "llm_summary"
            summary_seg.metadata.version = 1

            # Preserve relationships
            summary_seg.related_ids = [seg.id for seg in segments]

            return summary_seg

        except Exception as e:
            # Fallback to basic summarization on error
            return self._basic_summarization_segment(segments, target_tokens)

    def _build_summary_prompt(
        self,
        segments: List[ContextSegment],
        target_tokens: int
    ) -> str:
        """Build LLM prompt for summarization.

        Args:
            segments: Segments to summarize
            target_tokens: Target token count

        Returns:
            Summarization prompt string
        """
        # Combine segment content
        combined_content = "\n\n".join([
            f"[{seg.type.value.upper()}] {seg.content}"
            for seg in segments
        ])

        prompt = f"""You are summarizing context information for an AI agent.
Create a concise summary that preserves the key information while reducing token count.

TARGET TOKEN COUNT: Approximately {target_tokens} tokens (about {target_tokens * 4} characters)

ORIGINAL CONTENT:
{combined_content}

SUMMARY:
"""

        return prompt

    def _basic_summarization(
        self,
        segments: List[ContextSegment],
        target_tokens: int
    ) -> str:
        """Fallback: basic summarization without LLM.

        Args:
            segments: Segments to summarize
            target_tokens: Target token count

        Returns:
            Basic summary text
        """
        # Simple approach: concatenate and truncate
        combined = " | ".join([seg.content for seg in segments])

        # Estimate character limit
        target_chars = target_tokens * 4

        if len(combined) <= target_chars:
            return combined

        # Truncate with ellipsis
        return combined[:target_chars - 10] + "... [summarized]"

    def _basic_summarization_segment(
        self,
        segments: List[ContextSegment],
        target_tokens: int
    ) -> ContextSegment:
        """Create basic summary segment (fallback).

        Args:
            segments: Segments to summarize
            target_tokens: Target token count

        Returns:
            Summary segment
        """
        summary_text = self._basic_summarization(segments, target_tokens)
        summary_tokens = min(target_tokens, len(summary_text) // 4)

        summary_seg = ContextSegment(
            type=segments[0].type,
            priority=segments[0].priority,
            content=summary_text,
            tokens=summary_tokens,
            session_id=segments[0].session_id,
        )

        summary_seg.metadata.compressed = True
        summary_seg.metadata.source_type = "basic_summary"
        summary_seg.related_ids = [seg.id for seg in segments]

        return summary_seg

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using LLM tokenizer.

        Args:
            text: Text to count

        Returns:
            Token count
        """
        if self._llm and hasattr(self._llm, 'get_num_tokens'):
            return self._llm.get_num_tokens(text)

        # Fallback: rough estimation
        return len(text) // 4

    def estimate_information_loss(
        self,
        original_segments: List[ContextSegment],
        compressed_segments: List[ContextSegment],
        **kwargs
    ) -> float:
        """Estimate information loss from summarization.

        For LLM summarization, loss is estimated conservatively as:
        loss = 0.05 + (1.0 - compression_ratio) * 0.1

        This assumes LLM summarization preserves semantic meaning well,
        so information loss is lower than token reduction would suggest.

        Args:
            original_segments: Original segments
            compressed_segments: Summarized segments
            **kwargs: Additional parameters

        Returns:
            Information loss estimate (target: 0.05-0.15 for summaries)
        """
        original_tokens = self.calculate_total_tokens(original_segments)
        compressed_tokens = self.calculate_total_tokens(compressed_segments)

        if original_tokens == 0:
            return 0.0

        compression_ratio = compressed_tokens / original_tokens

        # Base loss from summarization (even perfect summaries lose some detail)
        base_loss = 0.05

        # Additional loss from compression
        compression_loss = (1.0 - compression_ratio) * 0.1

        total_loss = min(1.0, base_loss + compression_loss)

        return total_loss
