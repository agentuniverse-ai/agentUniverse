# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/03 16:00
# @Author  : kaichuan
# @FileName: adaptive_compressor.py
"""Adaptive compressor - dynamic strategy selection based on context.

This compressor intelligently selects the best compression strategy based on:
- Segment characteristics (types, priorities, sizes)
- Performance requirements (time constraints, quality targets)
- Historical effectiveness metrics

Strategy Selection Rules:
- Time-critical + low quality requirement → Truncate
- Quality-critical + sufficient time → Summarize
- Balanced requirements → Selective
- Mixed content → Hybrid approach
"""

import time
from typing import List, Optional, Dict, Any
from enum import Enum

from agentuniverse.agent.context.compressor.context_compressor import (
    ContextCompressor,
    CompressionMetrics,
)
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextPriority,
    ContextType,
)


class CompressionStrategy(str, Enum):
    """Available compression strategies."""
    TRUNCATE = "truncate"
    SELECTIVE = "selective"
    SUMMARIZE = "summarize"
    HYBRID = "hybrid"


class AdaptiveCompressor(ContextCompressor):
    """Adaptive compression strategy selector.

    Dynamically selects the best compression strategy based on context
    characteristics and performance requirements.

    Selection Algorithm:
    1. Analyze segment composition (types, priorities, token distribution)
    2. Evaluate constraints (time_limit, quality_threshold)
    3. Calculate strategy scores
    4. Select highest-scoring strategy
    5. Execute compression with selected strategy

    Attributes:
        time_critical_threshold_ms: Time limit for "time-critical" classification
        quality_threshold: Minimum acceptable quality (1 - info_loss)
        enable_hybrid: Whether to use hybrid multi-strategy approach
        truncate_weight: Weight for truncate strategy (speed)
        selective_weight: Weight for selective strategy (balance)
        summarize_weight: Weight for summarize strategy (quality)
    """

    time_critical_threshold_ms: float = 500.0
    quality_threshold: float = 0.9  # Target: >=90% preservation
    enable_hybrid: bool = True
    truncate_weight: float = 1.0
    selective_weight: float = 1.0
    summarize_weight: float = 1.0

    def __init__(self, **kwargs):
        """Initialize adaptive compressor."""
        super().__init__(**kwargs)
        self._truncate_compressor = None
        self._selective_compressor = None
        self._summarize_compressor = None

    def initialize_by_component_configer(self, component_configer) -> 'AdaptiveCompressor':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # Initialize sub-compressors
        from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
        from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
        from agentuniverse.agent.context.compressor.summarize_compressor import SummarizeCompressor

        self._truncate_compressor = TruncateCompressor(
            name=f"{self.name}_truncate",
            compression_ratio=self.compression_ratio
        )

        self._selective_compressor = SelectiveCompressor(
            name=f"{self.name}_selective",
            compression_ratio=self.compression_ratio
        )

        self._summarize_compressor = SummarizeCompressor(
            name=f"{self.name}_summarize",
            compression_ratio=self.compression_ratio,
            llm_name=kwargs.get("llm_name", "default_llm")
        )

        return self

    def compress(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        **kwargs
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Compress segments using adaptively selected strategy.

        Args:
            segments: List of context segments to compress
            target_tokens: Target token count after compression
            **kwargs: Additional parameters:
                - time_limit_ms: Maximum compression time allowed
                - min_quality: Minimum acceptable quality (1 - info_loss)
                - force_strategy: Force specific strategy (bypass selection)

        Returns:
            Tuple of (compressed_segments, compression_metrics)

        Raises:
            ValueError: If target_tokens <= 0 or segments is empty
        """
        start_time = time.time()

        # Handle empty input - return empty result
        if not segments:
            elapsed_ms = (time.time() - start_time) * 1000
            metrics = CompressionMetrics(
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=0.0,
                information_loss_estimate=0.0,
                segments_removed=0,
                segments_compressed=0,
                segments_preserved=0,
                compression_time_ms=elapsed_ms,
                strategy_used="adaptive"
            )
            return [], metrics

        if target_tokens <= 0:
            raise ValueError(f"Invalid target_tokens: {target_tokens}")

        # Check for forced strategy
        force_strategy = kwargs.get("force_strategy")
        if force_strategy:
            return self._execute_strategy(
                force_strategy, segments, target_tokens, kwargs
            )

        # Step 1: Analyze segment characteristics
        analysis = self._analyze_segments(segments, target_tokens)

        # Step 2: Get constraints
        time_limit_ms = kwargs.get("time_limit_ms", self.max_compression_time_ms)
        min_quality = kwargs.get("min_quality", self.quality_threshold)

        # Step 3: Select strategy
        selected_strategy = self._select_strategy(
            analysis, time_limit_ms, min_quality
        )

        # Step 4: Execute compression
        compressed, metrics = self._execute_strategy(
            selected_strategy, segments, target_tokens, kwargs
        )

        # Update metrics with selection info
        elapsed_ms = (time.time() - start_time) * 1000
        metrics.strategy_used = f"adaptive_{selected_strategy.value}"
        metrics.compression_time_ms = elapsed_ms

        return compressed, metrics

    def _analyze_segments(
        self,
        segments: List[ContextSegment],
        target_tokens: int
    ) -> Dict[str, Any]:
        """Analyze segment characteristics for strategy selection.

        Args:
            segments: Segments to analyze
            target_tokens: Target token count

        Returns:
            Analysis dictionary with metrics
        """
        total_tokens = self.calculate_total_tokens(segments)
        compression_needed = 1.0 - (target_tokens / total_tokens) if total_tokens > 0 else 0.0

        # Count by priority
        priority_counts = {
            ContextPriority.CRITICAL: 0,
            ContextPriority.HIGH: 0,
            ContextPriority.MEDIUM: 0,
            ContextPriority.LOW: 0,
            ContextPriority.EPHEMERAL: 0,
        }

        for seg in segments:
            priority_counts[seg.priority] = priority_counts.get(seg.priority, 0) + 1

        # Count by type
        type_counts = {}
        for seg in segments:
            type_counts[seg.type] = type_counts.get(seg.type, 0) + 1

        # Calculate diversity
        priority_diversity = len([c for c in priority_counts.values() if c > 0]) / 5.0
        type_diversity = len(type_counts) / len(ContextType)

        return {
            "total_segments": len(segments),
            "total_tokens": total_tokens,
            "target_tokens": target_tokens,
            "compression_needed": compression_needed,
            "priority_counts": priority_counts,
            "type_counts": type_counts,
            "priority_diversity": priority_diversity,
            "type_diversity": type_diversity,
            "has_critical": priority_counts[ContextPriority.CRITICAL] > 0,
            "avg_segment_size": total_tokens / len(segments) if segments else 0,
        }

    def _select_strategy(
        self,
        analysis: Dict[str, Any],
        time_limit_ms: float,
        min_quality: float
    ) -> CompressionStrategy:
        """Select best compression strategy based on analysis.

        Scoring System:
        - Truncate: Fast, lower quality
        - Selective: Balanced speed and quality
        - Summarize: Slower, higher quality
        - Hybrid: Best quality, slowest

        Args:
            analysis: Segment analysis results
            time_limit_ms: Maximum time allowed
            min_quality: Minimum acceptable quality

        Returns:
            Selected compression strategy
        """
        time_critical = time_limit_ms < self.time_critical_threshold_ms
        quality_critical = min_quality >= 0.9
        compression_needed = analysis["compression_needed"]

        # Score each strategy
        scores = {
            CompressionStrategy.TRUNCATE: 0.0,
            CompressionStrategy.SELECTIVE: 0.0,
            CompressionStrategy.SUMMARIZE: 0.0,
            CompressionStrategy.HYBRID: 0.0,
        }

        # Rule 1: Time-critical → prefer truncate
        if time_critical:
            scores[CompressionStrategy.TRUNCATE] += 5.0 * self.truncate_weight
            scores[CompressionStrategy.SELECTIVE] += 2.0 * self.selective_weight
        else:
            scores[CompressionStrategy.TRUNCATE] += 1.0 * self.truncate_weight
            scores[CompressionStrategy.SELECTIVE] += 3.0 * self.selective_weight
            scores[CompressionStrategy.SUMMARIZE] += 2.0 * self.summarize_weight

        # Rule 2: Quality-critical → prefer summarize/hybrid
        if quality_critical:
            scores[CompressionStrategy.SUMMARIZE] += 4.0 * self.summarize_weight
            if self.enable_hybrid:
                scores[CompressionStrategy.HYBRID] += 5.0
        else:
            scores[CompressionStrategy.SELECTIVE] += 2.0 * self.selective_weight

        # Rule 3: High compression needed → prefer selective
        if compression_needed > 0.6:  # >60% reduction
            scores[CompressionStrategy.SELECTIVE] += 4.0 * self.selective_weight
            scores[CompressionStrategy.TRUNCATE] += 2.0 * self.truncate_weight

        # Rule 4: Many CRITICAL segments → prefer selective (no CRITICAL compression)
        if analysis.get("has_critical"):
            critical_ratio = (
                analysis["priority_counts"][ContextPriority.CRITICAL] /
                analysis["total_segments"]
            )
            if critical_ratio > 0.3:  # >30% CRITICAL
                scores[CompressionStrategy.SELECTIVE] += 3.0 * self.selective_weight

        # Rule 5: High diversity → prefer hybrid
        if self.enable_hybrid:
            if analysis["priority_diversity"] > 0.6 or analysis["type_diversity"] > 0.5:
                scores[CompressionStrategy.HYBRID] += 3.0

        # Rule 6: Summarizable content → prefer summarize
        summarizable_types = {
            ContextType.BACKGROUND, ContextType.REFERENCE, ContextType.CONVERSATION
        }
        summarizable_count = sum(
            analysis["type_counts"].get(t, 0) for t in summarizable_types
        )
        summarizable_ratio = summarizable_count / analysis["total_segments"]

        if summarizable_ratio > 0.5:
            scores[CompressionStrategy.SUMMARIZE] += 3.0 * self.summarize_weight

        # Disable hybrid if not enabled
        if not self.enable_hybrid:
            scores.pop(CompressionStrategy.HYBRID, None)

        # Disable summarize if time-critical
        if time_critical:
            scores.pop(CompressionStrategy.SUMMARIZE, None)
            scores.pop(CompressionStrategy.HYBRID, None)

        # Select highest score
        if not scores:
            return CompressionStrategy.TRUNCATE  # Fallback

        selected = max(scores, key=scores.get)
        return selected

    def _execute_strategy(
        self,
        strategy: CompressionStrategy,
        segments: List[ContextSegment],
        target_tokens: int,
        kwargs: Dict[str, Any]
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Execute selected compression strategy.

        Args:
            strategy: Strategy to execute
            segments: Segments to compress
            target_tokens: Target token count
            kwargs: Additional parameters

        Returns:
            Tuple of (compressed_segments, compression_metrics)
        """
        if strategy == CompressionStrategy.TRUNCATE:
            return self._truncate_compressor.compress(segments, target_tokens, **kwargs)

        elif strategy == CompressionStrategy.SELECTIVE:
            return self._selective_compressor.compress(segments, target_tokens, **kwargs)

        elif strategy == CompressionStrategy.SUMMARIZE:
            return self._summarize_compressor.compress(segments, target_tokens, **kwargs)

        elif strategy == CompressionStrategy.HYBRID:
            return self._hybrid_compress(segments, target_tokens, kwargs)

        else:
            # Fallback to selective
            return self._selective_compressor.compress(segments, target_tokens, **kwargs)

    def _hybrid_compress(
        self,
        segments: List[ContextSegment],
        target_tokens: int,
        kwargs: Dict[str, Any]
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Hybrid compression using multiple strategies.

        Algorithm:
        1. Use selective for high-priority segments
        2. Use summarize for background/reference
        3. Use truncate for remaining if needed

        Args:
            segments: Segments to compress
            target_tokens: Target token count
            kwargs: Additional parameters

        Returns:
            Tuple of (compressed_segments, compression_metrics)
        """
        start_time = time.time()

        # Separate by category
        high_priority = [
            seg for seg in segments
            if seg.priority in [ContextPriority.CRITICAL, ContextPriority.HIGH]
        ]
        summarizable = [
            seg for seg in segments
            if seg.type in [ContextType.BACKGROUND, ContextType.REFERENCE]
            and seg not in high_priority
        ]
        remaining = [
            seg for seg in segments
            if seg not in high_priority and seg not in summarizable
        ]

        result = []
        tokens_used = 0

        # Step 1: Keep high priority (selective)
        if high_priority:
            hp_target = int(target_tokens * 0.4)  # 40% budget
            hp_compressed, _ = self._selective_compressor.compress(
                high_priority, hp_target, **kwargs
            )
            result.extend(hp_compressed)
            tokens_used += self.calculate_total_tokens(hp_compressed)

        # Step 2: Summarize background/reference
        if summarizable and tokens_used < target_tokens:
            sum_target = int(target_tokens * 0.4) - tokens_used  # 40% budget
            if sum_target > 0:
                sum_compressed, _ = self._summarize_compressor.compress(
                    summarizable, sum_target, **kwargs
                )
                result.extend(sum_compressed)
                tokens_used += self.calculate_total_tokens(sum_compressed)

        # Step 3: Truncate remaining if space available
        if remaining and tokens_used < target_tokens:
            rem_target = target_tokens - tokens_used
            if rem_target > 0:
                rem_compressed, _ = self._truncate_compressor.compress(
                    remaining, rem_target, **kwargs
                )
                result.extend(rem_compressed)

        elapsed_ms = (time.time() - start_time) * 1000
        metrics = self.create_metrics(
            segments, result, elapsed_ms, "hybrid",
            segments_compressed=len(result)
        )

        return result, metrics

    def estimate_information_loss(
        self,
        original_segments: List[ContextSegment],
        compressed_segments: List[ContextSegment],
        **kwargs
    ) -> float:
        """Estimate information loss for adaptive compression.

        Delegates to the compressor that was actually used.

        Args:
            original_segments: Original segments
            compressed_segments: Compressed segments
            **kwargs: Additional parameters

        Returns:
            Information loss estimate
        """
        # Use selective compressor's estimation as default
        return self._selective_compressor.estimate_information_loss(
            original_segments, compressed_segments, **kwargs
        )
