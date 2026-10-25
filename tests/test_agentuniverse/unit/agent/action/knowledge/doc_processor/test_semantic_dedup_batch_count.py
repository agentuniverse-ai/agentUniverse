"""Malformed embedding batch sizes must not change document vectors or drops."""

from copy import deepcopy
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.doc_processor import semantic_deduplicator as module
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.fixture
def provider(monkeypatch):
    model = Mock()
    manager = Mock()
    manager.get_instance_obj.return_value = model
    monkeypatch.setattr(module, "EmbeddingManager", lambda: manager)
    return model


@pytest.mark.parametrize("count", [0, 1, 2, 4])
@pytest.mark.parametrize("skip_on_error", [False, True], ids=["strict", "fallback"])
def test_wrong_batch_count_preserves_vectors_and_error_policy(provider, count, skip_on_error):
    documents = [
        Document(text="first distinct document", embedding=[1.0, 0.0]),
        Document(text="second distinct document", embedding=[0.0, 1.0]),
        Document(text="third distinct document", embedding=[-1.0, 0.0]),
    ]
    original_vectors = deepcopy([doc.embedding for doc in documents])
    provider.get_embeddings.return_value = [[1.0, 1.0] for _ in range(count)]
    processor = module.SemanticDeduplicator(embedding_name="test", skip_on_error=skip_on_error)
    if skip_on_error:
        result = processor.process_docs(documents)
        assert [doc.id for doc in result] == [doc.id for doc in documents]
    else:
        with pytest.raises(ValueError, match="one embedding per document"):
            processor.process_docs(documents)
    assert [doc.embedding for doc in documents] == original_vectors
    provider.get_embeddings.assert_called_once_with([doc.text for doc in documents])


def test_complete_batch_still_deduplicates_and_assigns_vectors(provider):
    documents = [Document(text="first"), Document(text="second"), Document(text="third")]
    provider.get_embeddings.return_value = [[1.0, 0.0]] * 3
    result = module.SemanticDeduplicator(embedding_name="test").process_docs(documents)
    assert result == [documents[0]]
    assert [doc.embedding for doc in documents] == [[1.0, 0.0]] * 3


def test_batch_count_matches_documents_after_exact_deduplication(provider):
    documents = [Document(text="same"), Document(text="same"), Document(text="other")]
    provider.get_embeddings.return_value = [[1.0, 0.0], [1.0, 0.0]]
    result = module.SemanticDeduplicator(embedding_name="test", skip_on_error=False).process_docs(documents)
    assert result == [documents[0]]
    provider.get_embeddings.assert_called_once_with(["same", "other"])
