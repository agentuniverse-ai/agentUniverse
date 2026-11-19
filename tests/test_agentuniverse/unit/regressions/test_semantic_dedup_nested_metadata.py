from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import (
    SemanticDeduplicator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def test_semantic_merge_handles_nested_json_lists_without_mutating_inputs():
    processor = SemanticDeduplicator(name="test_deduplicator", merge_strategy="merge")
    first = Document(
        id="first",
        text="same",
        metadata={"items": [{"name": "alpha"}], "nested": {"keep": True}},
    )
    second = Document(
        id="second",
        text="same",
        metadata={"items": [{"name": "beta"}, {"name": "alpha"}]},
    )

    merged = processor._merge_docs(first, second)

    assert merged.metadata["items"] == [{"name": "alpha"}, {"name": "beta"}]
    assert first.metadata == {"items": [{"name": "alpha"}], "nested": {"keep": True}}
    merged.metadata["items"][0]["name"] = "changed"
    assert first.metadata["items"][0]["name"] == "alpha"
