import pytest

from agentuniverse.agent.context.benchmark.benchmark_suite import ContextBenchmarkSuite


def test_resource_benchmark_rejects_empty_workload():
    suite = ContextBenchmarkSuite(object())

    with pytest.raises(ValueError, match="num_turns must be positive"):
        suite._test_resource_usage(0)
