"""Tests for context benchmark metric aggregation."""

from agentuniverse.agent.context.benchmark.benchmark_suite import BenchmarkMetrics


def test_overall_score_is_clamped_to_documented_range():
    poor_metrics = BenchmarkMetrics(
        compression_ratio=2.0,
        average_latency_ms=1000.0,
        memory_usage_mb=5000.0,
    )
    inflated_metrics = BenchmarkMetrics(
        multi_turn_coherence=2.0,
        compression_ratio=0.7,
        retrieval_precision=2.0,
        retrieval_recall=2.0,
    )

    assert poor_metrics.get_score() == 0.0
    assert inflated_metrics.get_score() == 100.0
