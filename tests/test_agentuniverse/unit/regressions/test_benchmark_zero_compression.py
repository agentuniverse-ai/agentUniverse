import pytest

from agentuniverse.agent.context.benchmark.benchmark_suite import ContextBenchmarkSuite


def test_compression_benchmark_rejects_empty_workload():
    suite = ContextBenchmarkSuite(object())

    with pytest.raises(ValueError, match="num_segments must be positive"):
        suite._test_compression_quality(0)
