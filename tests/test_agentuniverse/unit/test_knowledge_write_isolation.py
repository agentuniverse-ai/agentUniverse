"""Real thread-pool writes must not share mutable document payloads."""
from copy import deepcopy
import threading
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore

MODULE = 'agentuniverse.agent.action.knowledge.knowledge'


@pytest.mark.parametrize('operation', ['insert', 'update'])
@pytest.mark.parametrize('failure', [False, True])
def test_each_store_receives_an_independent_processed_batch(operation, failure):
    docs = [Document(id='a', text='original', embedding=[1.0], keywords={'base'},
                     metadata={'nested': {'tags': ['original']}}),
            Document(id='b', text='second')]
    expected = deepcopy(docs)
    mutated = threading.Event()
    observed = []

    class MutatingStore:
        def write(self, batch):
            batch[0].text = 'store-specific'
            batch[0].embedding.append(99.0)
            batch[0].keywords.add('private')
            batch[0].metadata['nested']['tags'].append('private')
            batch.pop()
            mutated.set()
            if failure:
                raise RuntimeError('simulated store rejection')

        insert_document = update_document = write

    class ObservingStore:
        def write(self, batch):
            if not mutated.wait(3):
                raise RuntimeError('writer did not run')
            observed.extend(deepcopy(batch))

        insert_document = update_document = write

    stores = {'mutating': MutatingStore(), 'observing': ObservingStore()}
    knowledge = Knowledge(stores=list(stores))
    try:
        with patch.object(Knowledge, '_load_data', return_value=docs), patch(f'{MODULE}.StoreManager') as manager:
            manager.return_value.get_instance_obj.side_effect = lambda name, **kwargs: stores[name]
            getattr(knowledge, f'{operation}_knowledge')(source_path='unused')
        assert observed == expected
        assert docs == expected
    finally:
        knowledge.insert_executor.shutdown(wait=True)
        knowledge.query_executor.shutdown(wait=True)


@pytest.mark.parametrize('operation', ['insert', 'update'])
def test_independent_managed_embedding_dimensions(operation):
    """Use real vector preparation with different per-store embedding models."""
    docs = [Document(text='shared input')]
    first_finished = threading.Event()
    received = {}

    class Embeddings:
        def __init__(self, dimensions):
            self.dimensions = dimensions

        def get_embeddings(self, texts):
            return [[1.0] * self.dimensions for _ in texts]

    class VectorStoreBoundary:
        def __init__(self, name, dimensions):
            self.name = name
            self.backend = RedisVectorStore(dimensions=dimensions, embedding_model=name)

        def write(self, batch):
            if self.name == 'three' and not first_finished.wait(3):
                raise RuntimeError('first vector store did not finish')
            received[self.name] = self.backend._vectors_for_documents(batch)
            if self.name == 'two':
                first_finished.set()

        insert_document = update_document = write

    stores = {'two': VectorStoreBoundary('two', 2), 'three': VectorStoreBoundary('three', 3)}
    knowledge = Knowledge(stores=list(stores))
    try:
        with patch.object(Knowledge, '_load_data', return_value=docs), \
             patch(f'{MODULE}.StoreManager') as manager, \
             patch('agentuniverse.agent.action.knowledge.store.redis_vector_store.EmbeddingManager') as embeddings:
            manager.return_value.get_instance_obj.side_effect = lambda name, **kwargs: stores[name]
            embeddings.return_value.get_instance_obj.side_effect = lambda name, **kwargs: Embeddings(2 if name == 'two' else 3)
            getattr(knowledge, f'{operation}_knowledge')(source_path='unused')
        assert received == {'two': [[1.0, 1.0]], 'three': [[1.0, 1.0, 1.0]]}
        assert docs[0].embedding == []
    finally:
        knowledge.insert_executor.shutdown(wait=True)
        knowledge.query_executor.shutdown(wait=True)


@pytest.mark.parametrize('operation', ['insert', 'update'])
@pytest.mark.parametrize('selected', [[], ['only'], ['only', 'other']])
def test_store_override_and_processor_order_are_unchanged(operation, selected):
    raw = [Document(text='raw')]
    processed = [Document(text='processed', metadata={'nested': ['preserved']})]
    received = []

    class Store:
        def write(self, docs):
            received.append(docs)
        insert_document = update_document = write

    knowledge = Knowledge(stores=['default'])
    try:
        with patch.object(Knowledge, '_load_data', return_value=raw), \
             patch.object(Knowledge, f'_{operation}_process', return_value=processed) as processor, \
             patch(f'{MODULE}.StoreManager') as manager:
            manager.return_value.get_instance_obj.return_value = Store()
            getattr(knowledge, f'{operation}_knowledge')(source_path='unused', stores=selected)
        processor.assert_called_once_with(raw)
        assert len(received) == len(selected)
        assert all(batch == processed for batch in received)
        assert all(batch is not processed and batch[0] is not processed[0] for batch in received)
        if len(received) == 2:
            assert received[0][0].metadata is not received[1][0].metadata
        assert [call.args[0] for call in manager.return_value.get_instance_obj.call_args_list] == selected
    finally:
        knowledge.insert_executor.shutdown(wait=True)
        knowledge.query_executor.shutdown(wait=True)
