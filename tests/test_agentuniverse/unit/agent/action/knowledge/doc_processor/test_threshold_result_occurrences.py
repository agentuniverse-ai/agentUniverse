"""Order restoration must retain the occurrence counts selected by filtering."""

from copy import deepcopy

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.threshold_filter import ThresholdFilter
from agentuniverse.agent.action.knowledge.store.document import Document


def document(text, score, **kwargs):
    return Document(text=text, metadata={"relevance_score": score}, **kwargs)


@pytest.mark.parametrize("k", [1, 2, 3])
def test_topk_does_not_reintroduce_unselected_occurrences(k):
    high, low = document("high", 1.0), document("low", 0.1)
    original = [high, high, high, high, low]
    snapshot = deepcopy([item.model_dump() for item in original])
    result = ThresholdFilter(filters=[{"type": "topk", "k": k}]).process_docs(original)
    assert len(result) == k
    assert all(item is high for item in result)
    assert [item.model_dump() for item in original] == snapshot


@pytest.mark.parametrize("percentile,count", [(0.2, 1), (0.4, 2)])
def test_percentile_keeps_selected_occurrence_budget(percentile, count):
    high, low = document("high", 1.0), document("low", 0.1)
    result = ThresholdFilter(filters=[{"type": "percentile", "percentile": percentile}]).process_docs(
        [high, high, high, high, low])
    assert len(result) == count
    assert all(item is high for item in result)


@pytest.mark.parametrize("logic", ["AND", "OR"])
def test_combined_identity_sets_are_not_expanded_again(logic):
    high, low = document("high", 1.0), document("low", 0.1)
    processor = ThresholdFilter(filters=[{"type": "topk", "k": 1},
                                        {"type": "score", "min_score": 0.5}],
                                logic_operator=logic)
    result = processor.process_docs([high, high, high, low])
    assert len(result) == 1
    assert result[0] is high


def test_single_score_filter_preserves_all_selected_repetitions():
    high, low = document("high", 1.0), document("low", 0.1)
    result = ThresholdFilter(filters=[{"type": "score", "min_score": 0.5}]).process_docs([high, low, high])
    assert len(result) == 2
    assert result[0] is result[1] is high


def test_no_filters_preserves_original_list():
    item = document("unchanged", 1.0)
    original = [item, item]
    assert ThresholdFilter().process_docs(original) is original


def test_unordered_topk_behavior_is_unchanged():
    item = document("high", 1.0)
    result = ThresholdFilter(filters=[{"type": "topk", "k": 1}], preserve_order=False).process_docs([item, item])
    assert len(result) == 1
    assert result[0] is item


def test_distinct_objects_with_equal_document_ids_are_not_conflated():
    low = document("low", 0.1, id="shared")
    high = document("high", 1.0, id="shared")
    result = ThresholdFilter(filters=[{"type": "topk", "k": 1}]).process_docs([low, high])
    assert len(result) == 1
    assert result[0] is high


def test_zero_budget_stays_empty():
    item = document("high", 1.0)
    assert ThresholdFilter(filters=[{"type": "topk", "k": 0}]).process_docs([item, item]) == []


def test_interleaved_references_keep_order_and_selected_counts():
    low, high = document("low", 0.1), document("high", 1.0)
    result = ThresholdFilter(filters=[{"type": "topk", "k": 3}]).process_docs([low, high, low, high])
    assert len(result) == 3
    assert result[0] is low
    assert result[1] is result[2] is high
