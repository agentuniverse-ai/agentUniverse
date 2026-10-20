# -*- coding:utf-8 -*-

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.metadata_filter import (
    MetadataFilter,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def _documents():
    return [
        Document(text="first", metadata={"tenant": "a", "score": 0.9, "tags": ["faq"]}),
        Document(text="second", metadata={"tenant": "b", "score": 0.8, "tags": ["guide"]}),
        Document(text="third", metadata={"tenant": "a", "score": 0.4}),
        Document(text="fourth", metadata=None),
    ]


def test_metadata_filter_applies_all_conditions_and_preserves_order():
    documents = _documents()
    processor = MetadataFilter(conditions=[
        {"field": "tenant", "operator": "eq", "value": "a"},
        {"field": "score", "operator": "gte", "value": 0.5},
    ])

    result = processor.process_docs(documents)

    assert [document.text for document in result] == ["first"]
    assert result[0] is documents[0]


def test_metadata_filter_supports_any_membership_and_contains():
    processor = MetadataFilter(
        conditions=[
            {"field": "tenant", "operator": "eq", "value": "b"},
            {"field": "tags", "operator": "contains", "value": "faq"},
        ],
        match_mode="any",
    )

    assert [document.text for document in processor.process_docs(_documents())] == [
        "first", "second"
    ]


def test_metadata_filter_handles_missing_fields_explicitly():
    documents = _documents()
    excluded = MetadataFilter(conditions=[
        {"field": "region", "operator": "eq", "value": "global"},
    ])
    included = MetadataFilter(
        conditions=[
            {"field": "region", "operator": "eq", "value": "global"},
        ],
        missing="include",
    )

    assert excluded.process_docs(documents) == []
    assert [document.text for document in included.process_docs(documents)] == [
        "first", "second", "third", "fourth"
    ]


def test_metadata_filter_exists_and_not_in_operators():
    processor = MetadataFilter(conditions=[
        {"field": "tags", "operator": "exists", "value": True},
        {"field": "tenant", "operator": "not_in", "value": ["blocked"]},
    ])

    assert [document.text for document in processor.process_docs(_documents())] == [
        "first", "second"
    ]


def test_metadata_filter_rejects_invalid_conditions():
    with pytest.raises(ValueError, match="requires a value"):
        MetadataFilter(conditions=[{"field": "tenant"}]).process_docs(_documents())

    with pytest.raises(TypeError, match="requires a collection"):
        MetadataFilter(conditions=[
            {"field": "tenant", "operator": "in", "value": "a"},
        ]).process_docs(_documents())
