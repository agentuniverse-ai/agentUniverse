"""Regression coverage for semantic cluster representative selection."""
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('richness,expected', [
    ([0, 3, 1], 1),
    ([0, 3, 3], 1),
    ([0, 1, 3], 2),
    ([3, 1, 0], 0),
])
def test_semantic_keep_best_retains_richest_representative(richness, expected):
    docs = [Document(id=str(i), text=f'version {i}',
                     metadata={str(k): k for k in range(count)})
            for i, count in enumerate(richness)]
    # An independent cluster must remain in its original position.
    docs.append(Document(id='other', text='unrelated'))
    model = Mock()
    model.get_embeddings.return_value = [[1., 0.]] * len(richness) + [[0., 1.]]
    processor = SemanticDeduplicator(
        name='test', embedding_name='mock', merge_strategy='keep_best',
        skip_on_error=False,
    )
    with patch('agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = processor.process_docs(docs)
    assert [doc.id for doc in result] == [str(expected), 'other']
    model.get_embeddings.assert_called_once_with([doc.text for doc in docs])
