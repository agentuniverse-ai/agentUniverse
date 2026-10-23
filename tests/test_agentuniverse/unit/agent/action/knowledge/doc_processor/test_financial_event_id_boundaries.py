"""Event identity must preserve boundaries between arbitrary source IDs."""
import hashlib

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document


def aggregate(ids, method):
    processor = FinancialEventAggregator(use_embeddings=False, use_llm=False,
                                         clustering_method=method, skip_on_error=False)
    documents = [Document(id=source_id, text='Company announced quarterly earnings today.')
                 for source_id in ids]
    events = processor.process_docs(documents)
    assert len(events) == 1
    assert events[0].metadata['source_count'] == len(ids)
    return events[0]


@pytest.mark.parametrize('method', ['dbscan', 'hierarchical'])
@pytest.mark.parametrize('left,right', [
    (['a|b', 'c'], ['a', 'b|c']),
    (['a', 'b', 'c'], ['a|b', 'c']),
    (['a|b|c'], ['a', 'b', 'c']),
    # Also distinguish backslashes from escape characters introduced for |.
    (['a\\', 'b|c'], ['a|b\\', 'c']),
])
def test_distinct_source_boundaries_produce_distinct_events(method, left, right):
    first = aggregate(left, method)
    second = aggregate(right, method)
    assert first.id != second.id
    assert first.metadata['event_id'] != second.metadata['event_id']


@pytest.mark.parametrize('method', ['dbscan', 'hierarchical'])
def test_source_order_does_not_change_event_identity(method):
    ids = ['来源|first', 'source\\second', 'third']
    assert aggregate(ids, method).id == aggregate(list(reversed(ids)), method).id


@pytest.mark.parametrize('method', ['dbscan', 'hierarchical'])
def test_ordinary_source_ids_retain_existing_event_identity(method):
    ids = ['source-b', 'source-a']
    expected = 'event_' + hashlib.md5('source-a|source-b'.encode()).hexdigest()[:12]
    assert aggregate(ids, method).id == expected
