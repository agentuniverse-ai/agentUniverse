import unittest
from unittest.mock import patch
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
import agentuniverse.agent.action.knowledge.knowledge as module


class TestKnowledgeWriteFailures(unittest.TestCase):
    def test_failed_insert_is_reported_after_other_stores_finish(self):
        self._assert_failure('insert_knowledge', 'insert_document')

    def test_failed_update_is_reported_after_other_stores_finish(self):
        self._assert_failure('update_knowledge', 'update_document')

    def test_missing_store_prevents_partial_insert(self):
        self._assert_missing_store_prevents_write('insert_knowledge')

    def test_missing_store_prevents_partial_update(self):
        self._assert_missing_store_prevents_write('update_knowledge')

    def _assert_missing_store_prevents_write(self, operation):
        calls = []
        class Store:
            def insert_document(self, documents):
                calls.append('insert')
            def update_document(self, documents):
                calls.append('update')

        def lookup(code, **kwargs):
            if code == 'missing':
                raise ValueError('missing store')
            return Store()

        knowledge = Knowledge(name='write_test', stores=['healthy', 'missing'])
        knowledge._load_data = lambda **kwargs: []
        manager = lambda: type('Manager', (), {'get_instance_obj': lambda self, code, **kwargs: lookup(code, **kwargs)})()
        with patch.object(module, 'StoreManager', manager):
            with self.assertRaisesRegex(ValueError, 'missing store'):
                getattr(knowledge, operation)()
        self.assertEqual(calls, [])

    def _assert_failure(self, operation, method):
        calls = []
        class Store:
            def __init__(self, name):
                self.name = name
            def insert_document(self, documents):
                calls.append(self.name)
                if self.name == 'broken':
                    raise OSError('backend unavailable')
            update_document = insert_document

        knowledge = Knowledge(name='write_test', stores=['broken', 'healthy'])
        knowledge._load_data = lambda **kwargs: []
        manager = lambda: type('Manager', (), {'get_instance_obj': lambda self, code, **kwargs: Store(code)})()
        with patch.object(module, 'StoreManager', manager):
            with self.assertRaises(RuntimeError) as caught:
                getattr(knowledge, operation)()
        self.assertCountEqual(calls, ['broken', 'healthy'])
        self.assertIn('broken', str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, OSError)
