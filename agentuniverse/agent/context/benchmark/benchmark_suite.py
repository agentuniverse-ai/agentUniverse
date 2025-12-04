#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/04 14:30
# @Author  : kaichuan
# @FileName: benchmark_suite.py
"""Comprehensive benchmarking suite for Context Engineering system.

This module provides tools to benchmark context engineering performance
against industry standards (Cursor, Claude, etc.) across multiple dimensions:

1. Multi-turn Coherence: Ability to maintain context across turns
2. Context Preservation: Information retention after compression
3. Compression Efficiency: Ratio and quality of compression
4. Retrieval Accuracy: Precision and recall of context search
5. Performance: Latency, throughput, memory usage
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import (
    ContextSegment,
    ContextType,
    ContextPriority,
    ContextMetadata,
)


@dataclass
class BenchmarkMetrics:
    """Comprehensive metrics from benchmarking run.

    Target Benchmarks (vs Cursor/Claude):
    - Multi-turn coherence: >0.85
    - Compression ratio: 60-80%
    - Information loss: <10%
    - Retrieval precision: >0.90
    - Retrieval latency: <100ms
    - Memory usage: <500MB for 10K turns
    """

    # Coherence metrics
    multi_turn_coherence: float = 0.0  # 0.0-1.0, target >0.85
    context_consistency: float = 0.0  # 0.0-1.0

    # Compression metrics
    compression_ratio: float = 0.0  # tokens_after / tokens_before, target 0.6-0.8
    information_loss: float = 0.0  # 0.0-1.0, target <0.1
    context_preservation: float = 0.0  # 1 - information_loss

    # Retrieval metrics
    retrieval_precision: float = 0.0  # relevant / total_retrieved, target >0.9
    retrieval_recall: float = 0.0  # relevant_retrieved / total_relevant
    retrieval_f1: float = 0.0  # Harmonic mean of precision and recall

    # Performance metrics
    average_latency_ms: float = 0.0  # Average operation latency, target <100ms
    p95_latency_ms: float = 0.0  # 95th percentile latency
    p99_latency_ms: float = 0.0  # 99th percentile latency
    throughput_ops_per_sec: float = 0.0  # Operations per second

    # Resource metrics
    memory_usage_mb: float = 0.0  # Memory consumption, target <500MB for 10K
    tokens_per_turn_avg: float = 0.0  # Average tokens per turn
    tokens_per_turn_p95: float = 0.0  # 95th percentile

    # Test statistics
    total_operations: int = 0
    total_duration_sec: float = 0.0
    test_cases_passed: int = 0
    test_cases_failed: int = 0

    # Additional details
    details: Dict[str, Any] = field(default_factory=dict)

    def passes_targets(self) -> bool:
        """Check if metrics meet target benchmarks.

        Returns:
            True if all targets met
        """
        return (
            self.multi_turn_coherence >= 0.85
            and self.compression_ratio >= 0.6
            and self.compression_ratio <= 0.8
            and self.information_loss < 0.1
            and self.retrieval_precision >= 0.9
            and self.average_latency_ms < 100
            and self.memory_usage_mb < 500  # For 10K turns
        )

    def get_score(self) -> float:
        """Calculate overall quality score (0-100).

        Returns:
            Weighted score out of 100
        """
        weights = {
            "coherence": 0.25,
            "compression": 0.20,
            "retrieval": 0.25,
            "performance": 0.20,
            "resource": 0.10,
        }

        scores = {
            "coherence": self.multi_turn_coherence * 100,
            "compression": (1 - abs(0.7 - self.compression_ratio) / 0.3) * 100,
            "retrieval": (self.retrieval_precision + self.retrieval_recall) / 2 * 100,
            "performance": max(0, (1 - self.average_latency_ms / 200)) * 100,
            "resource": max(0, (1 - self.memory_usage_mb / 1000)) * 100,
        }

        return sum(score * weights[category] for category, score in scores.items())


@dataclass
class BenchmarkResult:
    """Result from a benchmark test run."""

    test_name: str
    passed: bool
    metrics: BenchmarkMetrics
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


class ContextBenchmarkSuite:
    """Comprehensive benchmark suite for Context Engineering.

    This suite evaluates the context system across multiple dimensions,
    comparing against industry standards (Cursor, Claude).

    Example:
        >>> suite = ContextBenchmarkSuite(context_manager)
        >>> results = suite.run_full_suite()
        >>> print(f"Overall score: {results.metrics.get_score():.1f}/100")
        >>> print(f"Passes targets: {results.metrics.passes_targets()}")
    """

    def __init__(self, context_manager: ContextManager):
        """Initialize benchmark suite.

        Args:
            context_manager: ContextManager instance to benchmark
        """
        self.context_manager = context_manager
        self._latencies: List[float] = []

    def run_full_suite(
        self,
        num_turns: int = 100,
        **kwargs
    ) -> BenchmarkResult:
        """Run complete benchmark suite.

        Args:
            num_turns: Number of conversation turns to simulate
            **kwargs: Additional parameters for specific tests

        Returns:
            Aggregated benchmark results
        """
        print("Running Context Engineering Benchmark Suite...")
        print(f"Target: {num_turns} turns\n")

        start_time = time.time()
        metrics = BenchmarkMetrics()
        passed = 0
        failed = 0

        try:
            # Test 1: Multi-turn coherence
            print("1. Testing multi-turn coherence...")
            coherence_result = self._test_multi_turn_coherence(num_turns)
            metrics.multi_turn_coherence = coherence_result
            print(f"   Coherence: {coherence_result:.3f} (target: >0.85)")
            passed += 1 if coherence_result >= 0.85 else 0
            failed += 0 if coherence_result >= 0.85 else 1

            # Test 2: Compression quality
            print("\n2. Testing compression quality...")
            comp_ratio, info_loss = self._test_compression_quality(num_turns // 2)
            metrics.compression_ratio = comp_ratio
            metrics.information_loss = info_loss
            metrics.context_preservation = 1 - info_loss
            print(f"   Compression: {comp_ratio:.1%} (target: 60-80%)")
            print(f"   Info loss: {info_loss:.1%} (target: <10%)")
            passed += 1 if (0.6 <= comp_ratio <= 0.8 and info_loss < 0.1) else 0
            failed += 0 if (0.6 <= comp_ratio <= 0.8 and info_loss < 0.1) else 1

            # Test 3: Retrieval accuracy
            print("\n3. Testing retrieval accuracy...")
            precision, recall = self._test_retrieval_accuracy()
            metrics.retrieval_precision = precision
            metrics.retrieval_recall = recall
            metrics.retrieval_f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall) > 0 else 0
            )
            print(f"   Precision: {precision:.3f} (target: >0.90)")
            print(f"   Recall: {recall:.3f}")
            print(f"   F1: {metrics.retrieval_f1:.3f}")
            passed += 1 if precision >= 0.9 else 0
            failed += 0 if precision >= 0.9 else 1

            # Test 4: Performance
            print("\n4. Testing performance...")
            latency_stats = self._test_performance(num_turns)
            metrics.average_latency_ms = latency_stats["avg"]
            metrics.p95_latency_ms = latency_stats["p95"]
            metrics.p99_latency_ms = latency_stats["p99"]
            metrics.throughput_ops_per_sec = latency_stats["throughput"]
            print(f"   Avg latency: {latency_stats['avg']:.1f}ms (target: <100ms)")
            print(f"   P95 latency: {latency_stats['p95']:.1f}ms")
            print(f"   Throughput: {latency_stats['throughput']:.1f} ops/sec")
            passed += 1 if latency_stats["avg"] < 100 else 0
            failed += 0 if latency_stats["avg"] < 100 else 1

            # Test 5: Resource usage
            print("\n5. Testing resource usage...")
            memory_mb, tokens_avg = self._test_resource_usage(num_turns)
            metrics.memory_usage_mb = memory_mb
            metrics.tokens_per_turn_avg = tokens_avg
            expected_memory = (num_turns / 10000) * 500  # Scale target
            print(f"   Memory: {memory_mb:.1f}MB (target: <{expected_memory:.0f}MB)")
            print(f"   Tokens/turn: {tokens_avg:.1f}")
            passed += 1 if memory_mb < expected_memory else 0
            failed += 0 if memory_mb < expected_memory else 1

        except Exception as e:
            print(f"\n❌ Benchmark failed: {e}")
            return BenchmarkResult(
                test_name="full_suite",
                passed=False,
                metrics=metrics,
                error=str(e)
            )

        # Calculate final metrics
        metrics.total_operations = num_turns
        metrics.total_duration_sec = time.time() - start_time
        metrics.test_cases_passed = passed
        metrics.test_cases_failed = failed

        # Print summary
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Overall Score: {metrics.get_score():.1f}/100")
        print(f"Tests Passed: {passed}/5")
        print(f"Meets Targets: {'✅ YES' if metrics.passes_targets() else '❌ NO'}")
        print(f"Duration: {metrics.total_duration_sec:.2f}s")
        print("=" * 60)

        return BenchmarkResult(
            test_name="full_suite",
            passed=metrics.passes_targets(),
            metrics=metrics
        )

    def _test_multi_turn_coherence(self, num_turns: int) -> float:
        """Test context coherence across multiple turns.

        Args:
            num_turns: Number of turns to simulate

        Returns:
            Coherence score (0-1)
        """
        session_id = f"benchmark_coherence_{datetime.now().timestamp()}"
        self.context_manager.create_context_window(
            session_id,
            task_type="dialogue"
        )

        # Simulate conversation with references to previous context
        coherence_checks = []
        for i in range(num_turns):
            # Add message referencing previous turns
            if i > 0:
                ref_turn = max(0, i - 5)  # Reference recent turns
                content = f"Turn {i}: Following up on turn {ref_turn} discussion..."
            else:
                content = f"Turn {i}: Initial message..."

            self.context_manager.add_context(
                session_id,
                content,
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM
            )

            # Every 10 turns, check if we can retrieve earlier context
            if i % 10 == 0 and i > 0:
                retrieved = self.context_manager.search_context(
                    session_id,
                    f"turn {i-5}",
                    top_k=5
                )
                # Check if we found relevant context
                found = any(f"Turn {i-5}" in seg.content for seg in retrieved)
                coherence_checks.append(1.0 if found else 0.0)

        # Calculate average coherence
        return sum(coherence_checks) / len(coherence_checks) if coherence_checks else 0.0

    def _test_compression_quality(self, num_segments: int) -> tuple[float, float]:
        """Test compression ratio and information loss.

        Args:
            num_segments: Number of segments to compress

        Returns:
            Tuple of (compression_ratio, information_loss)
        """
        session_id = f"benchmark_compression_{datetime.now().timestamp()}"
        window = self.context_manager.create_context_window(
            session_id,
            max_tokens=1000  # Small window to trigger compression
        )

        # Add segments until compression occurs
        original_content = []
        for i in range(num_segments):
            content = f"Important information item {i}: " + "content " * 20
            original_content.append(content)
            self.context_manager.add_context(
                session_id,
                content,
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM
            )

        # Get metrics
        metrics = self.context_manager.get_budget_utilization(session_id)

        # Estimate compression ratio from token usage
        compression_ratio = metrics['utilization']

        # Estimate information loss (simplified)
        retrieved = self.context_manager.get_context(session_id)
        info_loss = 1.0 - (len(retrieved) / num_segments)

        return compression_ratio, info_loss

    def _test_retrieval_accuracy(self) -> tuple[float, float]:
        """Test search precision and recall.

        Returns:
            Tuple of (precision, recall)
        """
        session_id = f"benchmark_retrieval_{datetime.now().timestamp()}"
        self.context_manager.create_context_window(session_id)

        # Add known content with keywords
        keywords = ["authentication", "database", "API", "testing", "deployment"]
        for keyword in keywords:
            for i in range(3):
                self.context_manager.add_context(
                    session_id,
                    f"Document about {keyword}: content here...",
                    ContextType.BACKGROUND,
                    ContextPriority.MEDIUM
                )

        # Test retrieval for each keyword
        precision_scores = []
        recall_scores = []

        for keyword in keywords:
            results = self.context_manager.search_context(
                session_id,
                keyword,
                top_k=5
            )

            # Calculate precision: how many results are relevant
            relevant_results = sum(1 for r in results if keyword in r.content.lower())
            precision = relevant_results / len(results) if results else 0.0
            precision_scores.append(precision)

            # Calculate recall: did we find all relevant docs (3 expected)
            recall = relevant_results / 3.0
            recall_scores.append(recall)

        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_recall = sum(recall_scores) / len(recall_scores)

        return avg_precision, avg_recall

    def _test_performance(self, num_operations: int) -> Dict[str, float]:
        """Test operation latency and throughput.

        Args:
            num_operations: Number of operations to measure

        Returns:
            Dictionary with latency statistics
        """
        session_id = f"benchmark_perf_{datetime.now().timestamp()}"
        self.context_manager.create_context_window(session_id)

        latencies = []
        start_time = time.time()

        for i in range(num_operations):
            op_start = time.time()

            # Mix of operations
            if i % 3 == 0:
                # Add context
                self.context_manager.add_context(
                    session_id,
                    f"Message {i}",
                    ContextType.CONVERSATION,
                    ContextPriority.MEDIUM
                )
            elif i % 3 == 1:
                # Search
                self.context_manager.search_context(
                    session_id,
                    "message",
                    top_k=5
                )
            else:
                # Get context
                self.context_manager.get_context(session_id)

            latency_ms = (time.time() - op_start) * 1000
            latencies.append(latency_ms)

        total_time = time.time() - start_time
        latencies.sort()

        return {
            "avg": sum(latencies) / len(latencies),
            "p95": latencies[int(len(latencies) * 0.95)],
            "p99": latencies[int(len(latencies) * 0.99)],
            "throughput": num_operations / total_time,
        }

    def _test_resource_usage(self, num_turns: int) -> tuple[float, float]:
        """Test memory usage and token efficiency.

        Args:
            num_turns: Number of turns to simulate

        Returns:
            Tuple of (memory_mb, tokens_per_turn_avg)
        """
        import sys

        session_id = f"benchmark_resource_{datetime.now().timestamp()}"
        self.context_manager.create_context_window(session_id)

        # Measure initial memory
        initial_size = sys.getsizeof(self.context_manager)

        total_tokens = 0
        for i in range(num_turns):
            content = f"Turn {i}: " + "word " * 50  # ~50 tokens
            self.context_manager.add_context(
                session_id,
                content,
                ContextType.CONVERSATION,
                ContextPriority.MEDIUM
            )
            total_tokens += 50

        # Measure final memory
        final_size = sys.getsizeof(self.context_manager)
        memory_mb = (final_size - initial_size) / (1024 * 1024)

        # Get actual token usage from metrics
        metrics = self.context_manager.get_budget_utilization(session_id)
        actual_tokens = metrics['total_tokens']
        tokens_per_turn = actual_tokens / num_turns

        return memory_mb, tokens_per_turn
