"""Exercise validation/fallback with the real aggregator and document models."""
from copy import deepcopy
from unittest.mock import Mock, patch

import numpy as np
import pytest

from agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator import FinancialEventAggregator
from agentuniverse.agent.action.knowledge.store.document import Document

MODULE = 'agentuniverse.agent.action.knowledge.doc_processor.financial_event_aggregator'


@pytest.mark.parametrize('vectors', [
    [], [[1.0, 0.0]], [[1.0, 0.0]] * 3,
    [[1.0, 0.0], [1.0]], [[], []],
    [[float('nan'), 0.0], [1.0, 0.0]],
    [[1.0, 0.0], [float('inf'), 0.0]],
    [[1.0, 0.0], [float('-inf'), 0.0]],
    [[1.0, 0.0], ['bad', 0.0]],
    [[1.0, 0.0], [True, 0.0]],
    [[1.0, 0.0], None], None,
])
def test_invalid_batch_falls_back_without_mutating_documents(vectors):
    docs = [Document(text='alpha shared', embedding=[9.0], metadata={'source': 'a'}),
            Document(text='beta shared', embedding=[8.0], metadata={'source': 'b'})]
    before = deepcopy(docs)
    processor = FinancialEventAggregator(embedding_name='test')
    provider = Mock()
    provider.get_embeddings.return_value = vectors
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value = provider
        actual = processor._compute_similarity_matrix(docs)
    np.testing.assert_allclose(actual, [[1, 1 / 3], [1 / 3, 1]])
    assert docs == before


@pytest.mark.parametrize('scale', [1.0, 1e200, 1e-200])
def test_finite_extreme_vectors_keep_cosine_and_original_embeddings(scale):
    vectors = [[scale, scale], [scale, 0.0]]
    docs = [Document(text='one'), Document(text='two')]
    processor = FinancialEventAggregator(embedding_name='test')
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value.get_embeddings.return_value = vectors
        matrix = processor._compute_similarity_matrix(docs)
    np.testing.assert_allclose(matrix, [[1, 2 ** -0.5], [2 ** -0.5, 1]])
    assert [doc.embedding for doc in docs] == vectors
    assert np.isfinite(matrix).all()


def test_zero_vectors_do_not_merge_unrelated_news():
    docs = [Document(text='alpha'), Document(text='beta')]
    processor = FinancialEventAggregator(embedding_name='test', use_llm=False)
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value.get_embeddings.return_value = [[0., 0.], [0., 0.]]
        result = processor.process_docs(docs)
    assert len(result) == 2
    assert [doc.metadata['source_count'] for doc in result] == [1, 1]


def test_provider_failure_preserves_existing_embeddings():
    docs = [Document(text='same alpha', embedding=[2.0]), Document(text='same beta', embedding=[3.0])]
    processor = FinancialEventAggregator(embedding_name='test')
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value.get_embeddings.side_effect = RuntimeError('offline')
        matrix = processor._compute_similarity_matrix(docs)
    np.testing.assert_allclose(matrix, [[1, 1 / 3], [1 / 3, 1]])
    assert [d.embedding for d in docs] == [[2.0], [3.0]]


def test_invalid_batch_uses_text_clustering_end_to_end():
    docs = [Document(text='identical news'), Document(text='identical news')]
    processor = FinancialEventAggregator(embedding_name='test', use_llm=False)
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value.get_embeddings.return_value = [[float('nan')], [1.0]]
        result = processor.process_docs(docs)
    assert len(result) == 1
    assert result[0].metadata['source_count'] == 2
    assert all(not d.embedding for d in docs)


@pytest.mark.parametrize('vectors', [
    np.array([[1, 0], [-1, 0]], dtype=np.int64),
    np.array([[1., 0.], [-1., 0.]], dtype=np.float32),
    ((1., 0.), (-1., 0.)),
])
def test_numeric_array_batches_preserve_negative_similarity(vectors):
    docs = [Document(text='one'), Document(text='two')]
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        manager.return_value.get_instance_obj.return_value.get_embeddings.return_value = vectors
        actual = FinancialEventAggregator(embedding_name='test')._compute_similarity_matrix(docs)
    np.testing.assert_allclose(actual, [[1, -1], [-1, 1]])
    assert [doc.embedding for doc in docs] == [[1.0, 0.0], [-1.0, 0.0]]


def test_empty_input_makes_no_embedding_request():
    with patch(f'{MODULE}.EmbeddingManager') as manager:
        assert FinancialEventAggregator(embedding_name='test').process_docs([]) == []
    manager.assert_not_called()
