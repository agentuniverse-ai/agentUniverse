import sys
import unittest
from unittest.mock import MagicMock

try:
    import neo4j  # noqa: F401
except ImportError:
    sys.modules.setdefault('neo4j', MagicMock())

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.neo4j_store import Neo4jStore


class TestNeo4jDocumentIdBinding(unittest.TestCase):
    def setUp(self):
        self.store = Neo4jStore()
        self.session = MagicMock()
        self.store.driver = MagicMock()
        self.store.driver.session.return_value = self.session
        self.document = Document(id="x'} MATCH (n) DETACH DELETE n //", text='text', metadata={})

    def test_insert_binds_document_id(self):
        self.store.insert_document([self.document])
        cypher = self.session.run.call_args.args[0]
        self.assertIn('$id', cypher)
        self.assertNotIn(self.document.id, cypher)
        self.assertEqual(self.session.run.call_args.kwargs['id'], self.document.id)
        self.session.close.assert_called_once()

    def test_update_binds_document_id(self):
        self.store.update_document([self.document])
        cypher = self.session.run.call_args.args[0]
        self.assertIn('$id', cypher)
        self.assertNotIn(self.document.id, cypher)
        self.assertEqual(self.session.run.call_args.kwargs['id'], self.document.id)
        self.session.close.assert_called_once()
