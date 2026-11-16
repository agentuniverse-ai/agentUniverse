"""Check query roles through MMR and the DashScope HTTP adapter."""

import json
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.doc_processor.mmr_processor import MMRProcessor
from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import DashscopeEmbedding
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


def test_mmr_uses_query_role_for_query_embedding():
    model = DashscopeEmbedding(dashscope_api_key='test-key',
                               embedding_model_name='text-embedding-v2')
    requests = []

    def respond(**kwargs):
        payload = json.loads(kwargs['data'])
        requests.append(payload)
        texts = payload['input']['texts']
        role = payload['parameters']['text_type']
        # A role-sensitive provider returns a different query vector when
        # mistakenly asked to embed the query as a document.
        vectors = ([[1.0, 0.0]] if role == 'query' else
                   ([[0.0, 1.0]] if texts == ['question'] else
                    [[0.0, 1.0], [1.0, 0.0]]))
        return Mock(json=lambda: {'output': {'embeddings': [
            {'embedding': vector} for vector in vectors]}})

    docs = [Document(id='first', text='first document'),
            Document(id='second', text='second document')]
    processor = MMRProcessor(embedding_name='role-sensitive', top_n=1)
    with patch('agentuniverse.agent.action.knowledge.doc_processor.mmr_processor.EmbeddingManager') as manager, \
            patch('agentuniverse.agent.action.knowledge.embedding.dashscope_embedding.requests.post',
                  side_effect=respond):
        manager.return_value.get_instance_obj.return_value = model
        result = processor.process_docs(docs, Query(query_str='question'))

    assert [request['parameters']['text_type'] for request in requests] == [
        'document', 'query']
    assert [doc.id for doc in result] == ['second']
