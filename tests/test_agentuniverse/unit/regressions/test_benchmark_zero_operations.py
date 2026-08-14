import pytest

from agentuniverse.agent.context.benchmark.benchmark_suite import ContextBenchmarkSuite


def test_performance_benchmark_rejects_empty_workload():
    suite = ContextBenchmarkSuite(object())

    with pytest.raises(ValueError, match="num_operations must be positive"):
        suite._test_performance(0)
