from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import (
    SemanticDeduplicator,
)
from agentuniverse.agent.action.knowledge.store.document import Document


def test_semantic_keep_best_compares_with_current_representative():
    processor = SemanticDeduplicator(
        name="test_deduplicator",
        embedding_name="test_embedding",
        merge_strategy="keep_best",
    )
    documents = [
        Document(id="first", text="first", metadata={}),
        Document(id="richest", text="second", metadata={"a": 1, "b": 2, "c": 3}),
        Document(id="poorer", text="third", metadata={"a": 1}),
    ]
    embedding = Mock()
    embedding.get_embeddings.return_value = [[1.0, 0.0]] * len(documents)

    with patch(
        "agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator.EmbeddingManager"
    ) as manager:
        manager.return_value.get_instance_obj.return_value = embedding
        result = processor._remove_semantic_duplicates(documents)

    assert [document.id for document in result] == ["richest"]
