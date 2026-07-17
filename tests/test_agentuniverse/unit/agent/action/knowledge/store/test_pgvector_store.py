import json
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakeCursor:
    def __init__(self):
        self.batches = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def executemany(self, sql, rows):
        self.batches.append((sql, list(rows)))


class FakeConnection:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = []
        self.cursor_obj = FakeCursor()

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return self

    def fetchall(self):
        return self.rows

    def cursor(self):
        return self.cursor_obj


class PGVectorStoreTest(unittest.TestCase):
    def test_new_client_creates_extension_before_registering(self):
        connection = FakeConnection()
        psycopg = Mock()
        psycopg.connect.return_value = connection

        def register(conn):
            self.assertIs(conn, connection)
            self.assertEqual(connection.calls[0][0], "CREATE EXTENSION IF NOT EXISTS vector")

        store = PGVectorStore(connection_url="postgresql://test", create_table=False)
        with patch.object(store, "_dependencies", return_value=(psycopg, register, Mock())):
            self.assertIs(store._new_client(), connection)

    def test_invalid_top_k_fails_before_database_access(self):
        connection = FakeConnection()
        store = PGVectorStore(client=connection, dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))
        self.assertEqual(connection.calls, [])

    def test_table_sql_cosine(self):
        store = PGVectorStore(dimensions=3, table_name="docs")
        statements = store._table_sql(3)
        self.assertIn("vector(3)", statements[1])
        self.assertIn("vector_cosine_ops", statements[2])

    def test_rejects_unsafe_table_name(self):
        with self.assertRaisesRegex(ValueError, "identifier"):
            PGVectorStore(table_name="docs; DROP TABLE users")._validate_config(False)

    def test_rejects_dimension_mismatch(self):
        store = PGVectorStore(dimensions=3)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._check_vector([1.0, 2.0])

    def test_infers_dimension(self):
        store = PGVectorStore()
        store._check_vector([1.0, 2.0, 3.0])
        self.assertEqual(store.dimensions, 3)

    def test_query_with_metadata_filter(self):
        rows = [("one", "text", {"team": "a"}, [1.0, 0.0], 0.1)]
        connection = FakeConnection(rows)
        store = PGVectorStore(client=connection, dimensions=2, table_name="docs")
        result = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=3), metadata_filter={"team": "a"})
        self.assertEqual(result[0].id, "one")
        select = next(call for call in connection.calls if call[0].startswith("SELECT"))
        self.assertIn("metadata @>", select[0])
        self.assertEqual(json.loads(select[1][1]), {"team": "a"})
        self.assertEqual(select[1][-1], 3)

    def test_query_requires_embedding(self):
        store = PGVectorStore(client=FakeConnection(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "requires embeddings"):
            store.query(Query(query_str="hello"))

    def test_query_uses_embedding_component(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = PGVectorStore(client=FakeConnection(), dimensions=2, embedding_model="embed")
        with patch("agentuniverse.agent.action.knowledge.store.pgvector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.query(Query(query_str="hello"))
        manager.return_value.get_instance_obj.assert_called_once_with("embed", strict=True)

    def test_upsert_parameterizes_values(self):
        connection = FakeConnection()
        store = PGVectorStore(client=connection, dimensions=2, table_name="docs")
        store.upsert_document([Document(id="1", text="hello", metadata={"a": 1}, embedding=[0.1, 0.2])])
        sql, rows = connection.cursor_obj.batches[0]
        self.assertIn("ON CONFLICT", sql)
        self.assertEqual(rows[0][0], "1")
        self.assertEqual(json.loads(rows[0][2]), {"a": 1})

    def test_upsert_generates_missing_embeddings(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = PGVectorStore(client=FakeConnection(), dimensions=2, embedding_model="embed")
        document = Document(text="hello")
        with patch("agentuniverse.agent.action.knowledge.store.pgvector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([document])
        self.assertEqual(document.embedding, [0.1, 0.2])

    def test_delete_is_parameterized(self):
        connection = FakeConnection()
        store = PGVectorStore(client=connection, table_name="docs")
        store.delete_document("x' OR true")
        self.assertEqual(connection.calls[-1][1], ["x' OR true"])

    def test_rows_to_documents(self):
        docs = PGVectorStore._rows_to_documents([("1", "hello", None, (0.1, 0.2), 0.3)])
        self.assertEqual(docs[0].metadata, {})
        self.assertEqual(docs[0].embedding, [0.1, 0.2])

    def test_missing_dependency_hint(self):
        with patch.dict("sys.modules", {"psycopg": None}), self.assertRaisesRegex(ImportError, "psycopg"):
            PGVectorStore._dependencies()

    def test_connection_url_from_environment(self):
        with patch.dict("os.environ", {"PGVECTOR_CONNECTION_URL": "postgresql://test"}):
            self.assertEqual(PGVectorStore()._url(), "postgresql://test")

    def test_component_schema(self):
        config = Configer()
        config.value = {
            "name": "pgvector_store",
            "dimensions": 3,
            "metadata": {
                "type": "STORE",
                "module": "agentuniverse.agent.action.knowledge.store.pgvector_store",
                "class": "PGVectorStore",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.STORE.value)
        self.assertEqual(component.metadata_class, "PGVectorStore")


if __name__ == "__main__":
    unittest.main()
