import numpy as np

from agentuniverse.agent.action.knowledge.doc_processor import financial_event_aggregator
from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import (
    FinancialEventAggregator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


class _TrackingQueue:
    created = []

    def __init__(self, values=()):
        self.values = list(values)
        self.appended = []
        self.__class__.created.append(self)

    def __bool__(self):
        return bool(self.values)

    def popleft(self):
        return self.values.pop(0)

    def append(self, value):
        self.appended.append(value)
        self.values.append(value)


def test_dbscan_frontier_enqueues_each_dense_neighbor_once(monkeypatch):
    _TrackingQueue.created.clear()
    monkeypatch.setattr(financial_event_aggregator, "deque", _TrackingQueue)
    aggregator = FinancialEventAggregator(
        name="test_aggregator",
        similarity_threshold=0.85,
        use_embeddings=False,
        use_llm=False,
    )
    documents = [Document(id=str(index), text=f"document {index}") for index in range(40)]
    similarity = np.ones((len(documents), len(documents)))

    clusters = aggregator._cluster_with_dbscan(documents, similarity)

    assert len(clusters) == 1
    assert clusters[0].documents == [str(index) for index in range(40)]
    assert len(_TrackingQueue.created) == 1
    assert _TrackingQueue.created[0].appended == []
