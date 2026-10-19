"""Keep MMR selection bounded without changing its ranking contract."""

import cProfile
import random

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.mmr_processor import MMRProcessor


@pytest.mark.parametrize("lambda_coef", [0.0, 0.25, 0.5, 1.0])
@pytest.mark.parametrize("limit", [1, 3, None])
def test_incremental_selection_matches_mmr_definition(lambda_coef, limit):
    rng = random.Random(17)  # noqa: S311 - reproducible ranking fixtures
    vectors = [[rng.uniform(-1, 1) for _ in range(3)] for _ in range(9)]
    # Include a zero vector and a duplicate to exercise negative similarities and ties.
    vectors += [[0.0, 0.0, 0.0], list(vectors[0])]
    query = [1.0, -0.5, 0.25]
    processor = MMRProcessor(lambda_coef=lambda_coef, top_n=limit)
    relevance = [processor._cosine(vector, query) for vector in vectors]
    remaining = list(range(len(vectors)))
    expected = [max(remaining, key=lambda i: relevance[i])]
    remaining.remove(expected[0])
    while remaining and len(expected) < (limit or len(vectors)):
        next_index = max(
            remaining,
            key=lambda i: lambda_coef * relevance[i]
            - (1 - lambda_coef) * max(processor._cosine(vectors[i], vectors[j]) for j in expected),
        )
        expected.append(next_index)
        remaining.remove(next_index)

    assert processor._select(vectors, query) == expected


def test_full_selection_has_quadratic_function_call_budget():
    # A deterministic work budget catches cubic scans without timing thresholds.
    count = 160
    vectors = [[1.0, float(i)] for i in range(count)]
    profile = cProfile.Profile()
    result = profile.runcall(MMRProcessor()._select, vectors, [1.0, 0.0])

    assert len(result) == count
    assert sum(entry.callcount for entry in profile.getstats()) < 40 * count * count
