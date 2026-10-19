"""Bound dense-cluster queue work while preserving traversal and thresholds."""
import sys
from collections import deque
from unittest.mock import patch

import numpy as np
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document


def run_cluster(matrix, threshold=.85):
    processor = FinancialEventAggregator(use_embeddings=False, use_llm=False, similarity_threshold=threshold)
    docs = [Document(id=str(i), text=f'article {i}') for i in range(len(matrix))]
    # Isolate traversal cost from source/entity extraction.
    with patch.object(FinancialEventAggregator, '_create_cluster', side_effect=lambda items: [doc.id for doc in items]):
        return processor._cluster_with_dbscan(docs, matrix)


@pytest.mark.parametrize('count', [100, 200])
def test_dense_cluster_dequeues_each_document_at_most_once(count):
    stats = {'pops': 0, 'max_pending': 0}

    def profile(frame, event, arg):
        if event == 'c_call' and getattr(arg, '__name__', '') in ('pop', 'popleft'):
            queue = getattr(arg, '__self__', None)
            if isinstance(queue, (list, deque)):
                stats['pops'] += 1
                stats['max_pending'] = max(stats['max_pending'], len(queue))

    previous = sys.getprofile()
    try:
        sys.setprofile(profile)
        clusters = run_cluster(np.ones((count, count)))
    finally:
        sys.setprofile(previous)
    assert clusters == [[str(i) for i in range(count)]]
    assert stats['pops'] <= count
    assert stats['max_pending'] <= count


def test_transitive_neighbors_preserve_breadth_first_order_and_singletons():
    matrix = np.eye(6)
    for left, right in [(0, 1), (0, 3), (1, 2), (3, 4)]:
        matrix[left, right] = matrix[right, left] = .9
    assert run_cluster(matrix) == [['0', '1', '3', '2', '4'], ['5']]


def test_threshold_equality_remains_excluded():
    matrix = np.array([[1., .5, .6], [.5, 1., 0.], [.6, 0., 1.]])
    assert run_cluster(matrix, threshold=.5) == [['0', '2'], ['1']]


def test_empty_and_singleton_inputs():
    assert run_cluster(np.empty((0, 0))) == []
    assert run_cluster(np.ones((1, 1))) == [['0']]
