"""Nested JSON metadata must remain mergeable across deduplication passes."""
from copy import deepcopy
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator import SemanticDeduplicator
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('semantic', [False, True])
@pytest.mark.parametrize('skip_on_error', [False, True])
def test_merge_nested_lists_and_preserve_input_metadata(semantic, skip_on_error):
    docs = [
        Document(id='a', text='first' if semantic else 'same', metadata={
            'items': [{'a': 1}, ['x']], 'tags': ['first', 'shared'],
            'merged_sources': [{'id': 'prior'}],
        }, keywords={'a'}),
        Document(id='b', text='second' if semantic else 'same', metadata={
            'items': [{'a': 1}, {'a': 2}, ['x'], ['y']],
            'tags': ['shared', 'second'], 'source': 'b',
        }, keywords={'b'}),
        Document(id='c', text='third' if semantic else 'same', metadata={
            'items': [{'a': 3}], 'merged_sources': [{'id': 'external'}],
        }),
    ]
    before = deepcopy([doc.metadata for doc in docs])
    processor = SemanticDeduplicator(
        name='test', merge_strategy='merge', use_embeddings=semantic,
        embedding_name='mock', skip_on_error=skip_on_error,
    )
    model = Mock()
    model.get_embeddings.return_value = [[1., 0.]] * 3
    with patch('agentuniverse.agent.action.knowledge.doc_processor.semantic_deduplicator.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value = model
        result = processor.process_docs(docs)
    assert len(result) == 1
    merged = result[0]
    assert merged.id == 'a'
    assert merged.text == docs[0].text
    assert merged.metadata['items'] == [{'a': 1}, ['x'], {'a': 2}, ['y'], {'a': 3}]
    assert merged.metadata['tags'] == ['first', 'shared', 'second']
    assert merged.metadata['source'] == 'b'
    assert merged.keywords == {'a', 'b'}
    assert [entry['id'] for entry in merged.metadata['merged_sources']] == ['prior', 'b', 'external', 'c']
    assert [doc.metadata for doc in docs] == before


def test_merge_without_metadata_preservation_keeps_first():
    processor = SemanticDeduplicator(
        name='test', merge_strategy='merge', use_embeddings=False,
        preserve_metadata=False, skip_on_error=False,
    )
    docs = [Document(id=str(i), text='same', metadata={'items': [{'a': i}]}) for i in range(2)]
    result = processor.process_docs(docs)
    assert len(result) == 1
    assert result[0].id == '0'
    assert result[0].metadata['items'] == [{'a': 0}]
