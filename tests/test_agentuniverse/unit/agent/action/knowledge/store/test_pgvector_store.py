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
    """A fake psycopg cursor that records executemany batches for assertions."""

    def __init__(self):
        """Initialize the fake cursor with an empty batch list."""
        self.batches = []

    def __enter__(self):
        """Support context-manager usage by returning self."""
        return self

    def __exit__(self, *args):
        """Allow use in a with block without performing cleanup."""
        return None

    def executemany(self, sql, rows):
        """Record the sql and rows of an executemany call for later assertions."""
        self.batches.append((sql, list(rows)))


class FakeConnection:
    """A fake psycopg connection that records calls and returns canned rows."""

    def __init__(self, rows=None):
        """Initialize the fake connection with optional canned result rows."""
        self.rows = rows or []
        self.calls = []
        self.cursor_obj = FakeCursor()

    def execute(self, sql, params=None):
        """Record an execute call and return self to allow chaining."""
        self.calls.append((sql, params))
        return self

    def fetchall(self):
        """Return the canned rows configured for this connection."""
        return self.rows

    def cursor(self):
        """Return the shared fake cursor object."""
        return self.cursor_obj


class PGVectorStoreTest(unittest.TestCase):
    """Unit tests for PGVectorStore covering SQL generation and validation."""

    def test_new_client_creates_extension_before_registering(self):
        """Verify the connection is created only after the vector extension is requested."""
        connection = FakeConnection()
        psycopg = Mock()
        psycopg.connect.return_value = connection

        def register(conn):
            """Assert the connection is registered after the vector extension SQL ran first."""
            self.assertIs(conn, connection)
            self.assertEqual(connection.calls[0][0], "CREATE EXTENSION IF NOT EXISTS vector")

        store = PGVectorStore(connection_url="postgresql://test", create_table=False)
        with patch.object(store, "_dependencies", return_value=(psycopg, register, Mock())):
            self.assertIs(store._new_client(), connection)

    def test_invalid_top_k_fails_before_database_access(self):
        """Verify a negative similarity_top_k raises without touching the connection."""
        connection = FakeConnection()
        store = PGVectorStore(client=connection, dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))
        self.assertEqual(connection.calls, [])

    def test_table_sql_cosine(self):
        """Verify table SQL statements use the cosine distance operator for vectors."""
        store = PGVectorStore(dimensions=3, table_name="docs")
        statements = store._table_sql(3)
        self.assertIn("vector(3)", statements[1])
        self.assertIn("vector_cosine_ops", statements[2])

    def test_rejects_unsafe_table_name(self):
        """Verify an unsafe table name is rejected during validation."""
        with self.assertRaisesRegex(ValueError, "identifier"):
            PGVectorStore(table_name="docs; DROP TABLE users")._validate_config(False)

    def test_rejects_dimension_mismatch(self):
        """Verify vectors whose size differs from the configured dimension raise."""
        store = PGVectorStore(dimensions=3)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._check_vector([1.0, 2.0])

    def test_infers_dimension(self):
        """Verify the store dimension is inferred from the first checked vector."""
        store = PGVectorStore()
        store._check_vector([1.0, 2.0, 3.0])
        self.assertEqual(store.dimensions, 3)

    def test_query_with_metadata_filter(self):
        """Verify queries with a metadata filter embed it into the SELECT statement."""
        rows = [("one", "text", {"team": "a"}, [1.0, 0.0], 0.1)]
        connection = FakeConnection(rows)
        store = PGVectorStore(client=connection, dimensions=2, table_name="docs")
        result = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=3), metadata_filter={"team": "a"})
        self.assertEqual(result[0].id, "one")
        select = next(call for call in connection.calls if call[0].startswith("SELECT"))
        self.assertIn("metadata @>", select[0])
        self.assertIn("%s::vector", select[0])
        self.assertEqual(json.loads(select[1][1]), {"team": "a"})
        self.assertEqual(select[1][-1], 3)

    def test_query_requires_embedding(self):
        """Verify querying without embeddings raises a ValueError."""
        store = PGVectorStore(client=FakeConnection(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "requires embeddings"):
            store.query(Query(query_str="hello"))

    def test_query_uses_embedding_component(self):
        """Verify queries without embeddings fetch vectors from the configured embedding model."""
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = PGVectorStore(client=FakeConnection(), dimensions=2, embedding_model="embed")
        with patch("agentuniverse.agent.action.knowledge.store.pgvector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.query(Query(query_str="hello"))
        manager.return_value.get_instance_obj.assert_called_once_with("embed", strict=True)

    def test_upsert_parameterizes_values(self):
        """Verify upsert sends parameterized rows through executemany."""
        connection = FakeConnection()
        store = PGVectorStore(client=connection, dimensions=2, table_name="docs")
        store.upsert_document([Document(id="1", text="hello", metadata={"a": 1}, embedding=[0.1, 0.2])])
        sql, rows = connection.cursor_obj.batches[0]
        self.assertIn("ON CONFLICT", sql)
        self.assertEqual(rows[0][0], "1")
        self.assertEqual(json.loads(rows[0][2]), {"a": 1})

    def test_upsert_generates_missing_embeddings(self):
        """Verify upsert fills in missing document embeddings via the embedding model."""
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = PGVectorStore(client=FakeConnection(), dimensions=2, embedding_model="embed")
        document = Document(text="hello")
        with patch("agentuniverse.agent.action.knowledge.store.pgvector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([document])
        self.assertEqual(document.embedding, [0.1, 0.2])

    def test_delete_is_parameterized(self):
        """Verify delete_document passes the id as a bound parameter, never inline SQL."""
        connection = FakeConnection()
        store = PGVectorStore(client=connection, table_name="docs")
        store.delete_document("x' OR true")
        self.assertEqual(connection.calls[-1][1], ["x' OR true"])

    def test_rows_to_documents(self):
        """Verify raw rows convert into Documents with normalized metadata and embeddings."""
        docs = PGVectorStore._rows_to_documents([("1", "hello", None, (0.1, 0.2), 0.3)])
        self.assertEqual(docs[0].metadata, {})
        self.assertEqual(docs[0].embedding, [0.1, 0.2])

    def test_rows_to_documents_supports_pgvector_value(self):
        """Verify pgvector values exposing to_list are converted to plain lists."""
        vector = Mock()
        vector.to_list.return_value = [0.1, 0.2]
        docs = PGVectorStore._rows_to_documents([("1", "hello", {}, vector, 0.3)])
        self.assertEqual(docs[0].embedding, [0.1, 0.2])
        vector.to_list.assert_called_once_with()

    def test_missing_dependency_hint(self):
        """Verify a helpful ImportError is raised when psycopg is unavailable."""
        with patch.dict("sys.modules", {"psycopg": None}), self.assertRaisesRegex(ImportError, "psycopg"):
            PGVectorStore._dependencies()

    def test_connection_url_from_environment(self):
        """Verify the connection URL falls back to the PGVECTOR_CONNECTION_URL env var."""
        with patch.dict("os.environ", {"PGVECTOR_CONNECTION_URL": "postgresql://test"}):
            self.assertEqual(PGVectorStore()._url(), "postgresql://test")

    def test_component_schema(self):
        """Verify the store component loads its config with the correct metadata."""
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
