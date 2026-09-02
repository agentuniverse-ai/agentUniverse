# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/12/05 09:10
# @Author  : Yue Wang
# @FileName: test_benchmark_suite.py
"""Unit tests for benchmark suite metrics and result models."""

from dataclasses import replace
from datetime import datetime

import pytest

from agentuniverse.agent.context.benchmark.benchmark_suite import (
    BenchmarkMetrics,
    BenchmarkResult,
)

PASSING = BenchmarkMetrics(
    multi_turn_coherence=0.9,
    compression_ratio=0.7,
    information_loss=0.05,
    retrieval_precision=0.95,
    retrieval_recall=0.9,
    average_latency_ms=50,
    memory_usage_mb=100,
)
PERFECT = BenchmarkMetrics(
    multi_turn_coherence=1.0,
    compression_ratio=0.7,
    retrieval_precision=1.0,
    retrieval_recall=1.0,
)


class TestBenchmarkSuite:
    """Test BenchmarkMetrics target evaluation and scoring."""

    @pytest.fixture
    def passing_metrics(self):
        """Metrics satisfying every industry target benchmark."""
        return PASSING

    def test_default_values(self):
        """All metric fields default to zero values."""
        metrics = BenchmarkMetrics()
        assert metrics.multi_turn_coherence == 0.0
        assert metrics.information_loss == 0.0
        assert metrics.details == {}

    def test_passes_targets(self, passing_metrics):
        """Passes only when every target benchmark is met."""
        assert passing_metrics.passes_targets() is True
        assert BenchmarkMetrics().passes_targets() is False
        assert replace(passing_metrics, compression_ratio=0.4).passes_targets() is False
        assert replace(passing_metrics, information_loss=0.5).passes_targets() is False
        assert replace(passing_metrics, average_latency_ms=200).passes_targets() is False
        assert replace(passing_metrics, memory_usage_mb=600).passes_targets() is False

    def test_score_perfect_and_default(self):
        """Perfect metrics score 100; untouched metrics score near 3.33."""
        assert PERFECT.get_score() == pytest.approx(100.0)
        assert BenchmarkMetrics().get_score() == pytest.approx(3.3333, abs=1e-3)

    def test_latency_penalises_score(self, passing_metrics):
        """Higher latency reduces the performance weight contribution."""
        slow = replace(passing_metrics, average_latency_ms=300.0)
        assert slow.get_score() < passing_metrics.get_score()
        expected_delta = 0.2 * (1.0 - 50.0 / 200.0) * 100.0
        assert passing_metrics.get_score() - slow.get_score() == pytest.approx(expected_delta, abs=1e-9)

    def test_benchmark_result_fields(self, passing_metrics):
        """BenchmarkResult carries metadata, timestamps and errors."""
        result = BenchmarkResult(test_name="full_suite", passed=True, metrics=passing_metrics)
        assert result.test_name == "full_suite"
        assert isinstance(result.timestamp, datetime)
        assert result.error is None
        failed = BenchmarkResult(test_name="full_suite", passed=False,
                                 metrics=passing_metrics, error="boom")
        assert failed.passed is False
        assert failed.error == "boom"
