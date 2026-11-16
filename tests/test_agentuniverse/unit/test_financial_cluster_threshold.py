"""Exercise actual text-overlap scoring and clustering through process_docs."""
import math

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import (
    FinancialEventAggregator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def aggregate(texts, threshold, method="dbscan"):
    docs = [Document(id=f"source-{i}", text=text, metadata={"source": i})
            for i, text in enumerate(texts)]
    processor = FinancialEventAggregator(
        use_embeddings=False, use_llm=False, skip_on_error=False,
        similarity_threshold=threshold, clustering_method=method,
    )
    result = processor.process_docs(docs)
    assert [doc.metadata for doc in docs] == [{"source": i} for i in range(len(docs))]
    return result


@pytest.mark.parametrize("left,right,threshold", [
    ("Annual revenues increased", "Quarterly profits declined", 0.0),
    ("revenue", "revenue profit sales earnings", 0.25),
    ("revenue profit", "revenue profit sales earnings", 0.5),
    ("revenue profit sales", "revenue profit sales earnings", 0.75),
    ("revenue profit sales", "revenue profit sales", 1.0),
])
def test_similarity_equal_to_threshold_includes_both_sources(left, right, threshold):
    doc, = aggregate([left, right], threshold)
    assert doc.metadata["source_count"] == 2
    assert [source["id"] for source in doc.metadata["source_documents"]] == [
        "source-0", "source-1",
    ]
    assert doc.text
    assert "financial_event" in doc.keywords


@pytest.mark.parametrize("threshold,expected", [
    (math.nextafter(0.75, 0.0), [2]),
    (math.nextafter(0.75, 1.0), [1, 1]),
])
def test_values_immediately_on_either_side_of_boundary_stay_distinct(threshold, expected):
    docs = aggregate(["revenue profit sales", "revenue profit sales earnings"], threshold)
    assert [doc.metadata["source_count"] for doc in docs] == expected


@pytest.mark.parametrize("order", [(0, 1, 2), (2, 1, 0), (1, 0, 2)])
def test_boundary_neighbors_are_also_included_during_expansion(order):
    # A-B and B-C have overlap 2/3; A-C has only 1/3. C must be discovered
    # while expanding B when A starts the cluster, rather than becoming noise.
    texts = ["revenue profit", "revenue profit sales", "profit sales"]
    doc, = aggregate([texts[i] for i in order], 2 / 3)
    assert doc.metadata["source_count"] == 3
    assert [source["id"] for source in doc.metadata["source_documents"]] == [
        "source-0", "source-1", "source-2",
    ]


def test_hierarchical_method_already_includes_exact_matches_at_one():
    doc, = aggregate(["revenue profit", "revenue profit"], 1.0, method="hierarchical")
    assert doc.metadata["source_count"] == 2


def test_empty_batch_stays_empty():
    assert aggregate([], 1.0) == []


def test_single_source_stays_a_single_source():
    doc, = aggregate(["revenue profit"], 1.0)
    assert doc.metadata["source_count"] == 1
    assert doc.metadata["source_documents"][0]["id"] == "source-0"
