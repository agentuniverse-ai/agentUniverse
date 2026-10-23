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

import logging
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

logger = logging.getLogger(__name__)


def _load_llm(name: str):
    """Resolve an LLM component by name.

    This stays a module level hook so that applications (and tests) can swap
    the lookup out without importing ``agentuniverse.llm.llm_manager``, which
    pulls in optional dependencies that building a compressor does not need.
    """
    from agentuniverse.llm.llm_manager import LLMManager
    return LLMManager().get_instance_obj(name)


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
        llm_name: Name of the LLM used by the summarize strategy
    """

    time_critical_threshold_ms: float = 500.0
    quality_threshold: float = 0.9  # Target: >=90% preservation
    enable_hybrid: bool = True
    truncate_weight: float = 1.0
    selective_weight: float = 1.0
    summarize_weight: float = 1.0
    llm_name: str = "default_llm"

    def __init__(self, **kwargs):
        """Initialize adaptive compressor."""
        super().__init__(**kwargs)
        # Build the strategy delegates eagerly so that a directly constructed
        # AdaptiveCompressor is usable right away: ContextManager wires the
        # compressor with a plain constructor call, and leaving the delegates
        # as ``None`` turned every summarize/hybrid run into an
        # ``AttributeError: 'NoneType' object has no attribute 'compress'``.
        self._truncate_compressor = None
        self._selective_compressor = None
        self._summarize_compressor = None
        self._build_sub_compressors()

    def _build_sub_compressors(self) -> None:
        """(Re)create the strategy delegates used by ``_execute_strategy``.

        The imports live here instead of at module scope so that importing
        ``adaptive_compressor`` stays cheap and free of circular imports.

        The LLM used by the summarize strategy is attached separately by
        ``_wire_summarize_llm``; a compressor that is built directly in code
        therefore keeps the SELECTIVE fallback until an LLM is wired in.
        """
        from agentuniverse.agent.context.compressor.truncate_compressor import TruncateCompressor
        from agentuniverse.agent.context.compressor.selective_compressor import SelectiveCompressor
        from agentuniverse.agent.context.compressor.summarize_compressor import SummarizeCompressor

        # ``name`` is optional on the base component, so fall back to a stable
        # prefix instead of generating names such as "None_truncate".
        base_name = self.name or "adaptive_compressor"

        self._truncate_compressor = TruncateCompressor(
            name=f"{base_name}_truncate",
            compression_ratio=self.compression_ratio
        )

        self._selective_compressor = SelectiveCompressor(
            name=f"{base_name}_selective",
            compression_ratio=self.compression_ratio
        )

        self._summarize_compressor = SummarizeCompressor(
            name=f"{base_name}_summarize",
            compression_ratio=self.compression_ratio,
            llm_name=self.llm_name
        )

    def _wire_summarize_llm(self) -> None:
        """Attach an LLM instance to the summarize delegate.

        AdaptiveCompressor owns the summarize strategy, so it is the component
        responsible for its LLM.  Without this wiring a quality critical run
        selects SUMMARIZE and then fails with
        ``RuntimeError: LLM not initialized for summarization``.

        The lookup is best effort on purpose: a missing or invalid LLM only
        means the summarize strategy is not runnable, which
        ``_resolve_runnable_strategy`` turns into a SELECTIVE fallback.  A
        compressor that cannot summarize is still far better than one that
        raises while the context window overflows.
        """
        if self._summarize_compressor is None:
            return

        self._summarize_compressor.llm_name = self.llm_name
        try:
            self._summarize_compressor._llm = _load_llm(self.llm_name)
        except Exception as exc:
            logger.warning(
                "Adaptive compressor could not initialise the summarize LLM '%s': %s; "
                "summarize and hybrid strategies will fall back to selective",
                self.llm_name, exc,
            )

    def initialize_by_component_configer(self, component_configer) -> 'AdaptiveCompressor':
        """Initialize from YAML configuration."""
        super().initialize_by_component_configer(component_configer)

        # ``ComponentBase`` does not copy scalar yaml keys onto the component,
        # so read them here.  Every lookup stays optional: a yaml may legally
        # omit any of these keys (the shipped example omits ``llm_name``) and
        # the compressor must keep its constructor values in that case.
        name = getattr(component_configer, "name", None)
        if name:
            self.name = name
        description = getattr(component_configer, "description", None)
        if description:
            self.description = description

        compression_ratio = getattr(component_configer, "compression_ratio", None)
        if compression_ratio is not None:
            self.compression_ratio = compression_ratio

        enable_hybrid = getattr(component_configer, "enable_hybrid", None)
        if enable_hybrid is not None:
            self.enable_hybrid = enable_hybrid

        # The yaml publishes the quality target as ``min_quality_threshold``
        # while the compressor stores it as ``quality_threshold``.
        min_quality_threshold = getattr(component_configer, "min_quality_threshold", None)
        if min_quality_threshold is not None:
            self.quality_threshold = min_quality_threshold

        llm_name = getattr(component_configer, "llm_name", None)
        if llm_name:
            self.llm_name = llm_name

        # ``strategy_weights`` maps strategy names onto score weights.  Unknown
        # keys (for example ``hybrid``, which has no weight field of its own)
        # are ignored on purpose.
        weights = getattr(component_configer, "strategy_weights", None) or {}
        if isinstance(weights, dict):
            self.truncate_weight = float(weights.get("truncate", self.truncate_weight))
            self.selective_weight = float(weights.get("selective", self.selective_weight))
            self.summarize_weight = float(weights.get("summarize", self.summarize_weight))

        # Rebuild with the freshly loaded settings and attach the LLM used by
        # the summarize strategy.
        self._build_sub_compressors()
        self._wire_summarize_llm()

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
            # The strategy is still validated for runnability inside
            # ``_execute_strategy``, so forcing SUMMARIZE without an LLM
            # degrades to SELECTIVE instead of raising.
            compressed, metrics = self._execute_strategy(
                force_strategy, segments, target_tokens, kwargs
            )
            metrics.compression_time_ms = (time.time() - start_time) * 1000
            return compressed, metrics

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

        # Update metrics with selection info.  ``strategy_used`` is filled in
        # by ``_execute_strategy`` because that is the component which knows
        # whether the selected strategy was runnable or had to fall back.
        elapsed_ms = (time.time() - start_time) * 1000
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

    def _is_summarize_runnable(self) -> bool:
        """Return True when the LLM backed summarize delegate can execute."""
        return (
            self._summarize_compressor is not None
            and getattr(self._summarize_compressor, "_llm", None) is not None
        )

    def _requires_summarize(self, segments: List[ContextSegment]) -> bool:
        """Return True when the hybrid delegate would call summarize.

        ``_hybrid_compress`` only summarizes BACKGROUND/REFERENCE segments
        that are not high priority, so a hybrid run over other segment types
        stays safe even when no LLM is available.
        """
        for seg in segments:
            if seg.priority in (ContextPriority.CRITICAL, ContextPriority.HIGH):
                continue
            if seg.type in (ContextType.BACKGROUND, ContextType.REFERENCE):
                return True
        return False

    def _resolve_runnable_strategy(
        self,
        strategy: CompressionStrategy,
        segments: List[ContextSegment]
    ) -> tuple[CompressionStrategy, bool]:
        """Map a selected strategy onto one that can actually execute.

        Args:
            strategy: Strategy chosen by ``_select_strategy`` or forced by the
                caller
            segments: Segments that will be compressed

        Returns:
            Tuple of (runnable strategy, whether a fallback was applied).  The
            LLM backed strategies are downgraded to SELECTIVE when their LLM
            dependency is unavailable, which keeps ``compress`` usable instead
            of raising AttributeError/RuntimeError on a partially wired
            compressor.
        """
        if strategy == CompressionStrategy.SUMMARIZE and not self._is_summarize_runnable():
            return CompressionStrategy.SELECTIVE, True

        if (strategy == CompressionStrategy.HYBRID
                and self._requires_summarize(segments)
                and not self._is_summarize_runnable()):
            return CompressionStrategy.SELECTIVE, True

        return strategy, False

    def _execute_strategy(
        self,
        strategy: CompressionStrategy,
        segments: List[ContextSegment],
        target_tokens: int,
        kwargs: Dict[str, Any]
    ) -> tuple[List[ContextSegment], CompressionMetrics]:
        """Execute selected compression strategy.

        The requested strategy is validated against the state of the sub
        compressors first: an LLM backed strategy whose LLM is missing is
        downgraded to SELECTIVE, and ``CompressionMetrics.strategy_used``
        records the substitution with a ``_fallback`` suffix so callers can
        still tell what really ran.

        Args:
            strategy: Strategy to execute (a ``CompressionStrategy`` or its
                string value)
            segments: Segments to compress
            target_tokens: Target token count
            kwargs: Additional parameters

        Returns:
            Tuple of (compressed_segments, compression_metrics)
        """
        if isinstance(strategy, str):
            strategy = CompressionStrategy(strategy)

        effective, fallback = self._resolve_runnable_strategy(strategy, segments)

        if effective == CompressionStrategy.TRUNCATE:
            compressed, metrics = self._truncate_compressor.compress(
                segments, target_tokens, **kwargs
            )
        elif effective == CompressionStrategy.SUMMARIZE:
            compressed, metrics = self._summarize_compressor.compress(
                segments, target_tokens, **kwargs
            )
        elif effective == CompressionStrategy.HYBRID:
            compressed, metrics = self._hybrid_compress(segments, target_tokens, kwargs)
        else:
            # SELECTIVE is the safe default: it never needs an LLM.
            compressed, metrics = self._selective_compressor.compress(
                segments, target_tokens, **kwargs
            )

        metrics.strategy_used = (
            f"adaptive_{effective.value}{'_fallback' if fallback else ''}"
        )
        return compressed, metrics

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
        # Delegate to the selective compressor (always built by
        # ``_build_sub_compressors``); fall back to a token based estimate when
        # a caller removed the delegates, so a heuristic call never turns into
        # an AttributeError.
        if self._selective_compressor is not None:
            return self._selective_compressor.estimate_information_loss(
                original_segments, compressed_segments, **kwargs
            )

        original_tokens = self.calculate_total_tokens(original_segments)
        if original_tokens <= 0:
            return 0.0
        compressed_tokens = self.calculate_total_tokens(compressed_segments)
        return max(0.0, min(1.0, 1.0 - (compressed_tokens / original_tokens)))
