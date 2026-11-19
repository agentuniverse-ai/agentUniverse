# -*- coding:utf-8 -*-

import os

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.metadata_filter import (
    MetadataFilter,
)
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer
import agentuniverse.agent.action.knowledge.doc_processor.metadata_filter as metadata_filter_module


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


def test_metadata_filter_applies_shipped_yaml_configuration():
    config_path = str(
        os.path.join(
            os.path.dirname(metadata_filter_module.__file__),
            "metadata_filter.yaml",
        )
    )
    configer = Configer(path=config_path).load()
    component_configer = ComponentConfiger().load_by_configer(configer)
    processor = MetadataFilter().initialize_by_component_configer(component_configer)
    documents = [
        Document(text="allowed", metadata={"tenant_id": "tenant-a", "language": "en"}),
        Document(text="other tenant", metadata={"tenant_id": "tenant-b", "language": "en"}),
        Document(text="other language", metadata={"tenant_id": "tenant-a", "language": "fr"}),
    ]

    result = processor.process_docs(documents)

    assert processor.conditions == [
        {"field": "tenant_id", "operator": "eq", "value": "tenant-a"},
        {"field": "language", "operator": "in", "value": ["en", "zh"]},
    ]
    assert processor.match_mode == "all"
    assert processor.missing == "exclude"
    assert [document.text for document in result] == ["allowed"]
