import asyncio
import json
import unittest
from unittest.mock import Mock, patch

# Test doubles intentionally raise concise built-in errors.
# ruff: noqa: TRY003
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.redis_vector_store import RedisVectorStore
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakePipeline:
    """A fake redis pipeline that records hset calls until executed."""

    def __init__(self):
        """Initialize the fake pipeline with an empty call log."""
        self.calls = []
        self.executed = False

    def hset(self, key, mapping):
        """Record an hset key/mapping pair and return self for chaining."""
        self.calls.append((key, mapping))
        return self

    def execute(self):
        """Mark the pipeline as executed and return one success per recorded call."""
        self.executed = True
        return [1] * len(self.calls)


class FakeAsyncPipeline(FakePipeline):
    """An async fake redis pipeline for exercising the async client."""

    async def __aenter__(self):
        """Return self when entering the async context manager."""
        return self

    async def __aexit__(self, *args):
        """Allow the async context manager to exit without cleanup."""
        return None

    async def execute(self):
        """Mark the pipeline as executed and return one success per recorded call."""
        self.executed = True
        return [1] * len(self.calls)


class FakeConnection:
    """A fake redis connection that records commands and returns canned replies."""

    def __init__(self, search_response=None):
        """Initialize the fake connection with optional canned search response rows."""
        self.calls = []
        self.deleted = []
        self.search_response = search_response or [0]
        self.pipeline_obj = FakePipeline()

    def execute_command(self, *args):
        """Record a command and return the canned search response for FT.SEARCH."""
        self.calls.append(args)
        return self.search_response if args[0] == "FT.SEARCH" else b"OK"

    def pipeline(self, transaction=False):
        """Remember the transaction flag and return the fake pipeline object."""
        self.transaction = transaction
        return self.pipeline_obj

    def delete(self, key):
        """Record the deleted key and return 1."""
        self.deleted.append(key)
        return 1


class FakeAsyncConnection(FakeConnection):
    """An async fake redis connection that wraps the synchronous fake."""

    def __init__(self, search_response=None):
        """Initialize with a fake async pipeline as the pipeline object."""
        super().__init__(search_response)
        self.pipeline_obj = FakeAsyncPipeline()

    async def execute_command(self, *args):
        """Async wrapper delegating command execution to the synchronous fake."""
        return super().execute_command(*args)

    async def delete(self, key):
        """Async wrapper delegating deletion to the synchronous fake."""
        return super().delete(key)


class RedisVectorStoreTest(unittest.TestCase):
    """Unit tests for RedisVectorStore covering commands and validation."""

    def test_index_command_contains_hnsw_schema(self):
        """Verify the index command builds an HNSW schema with filter tag fields."""
        store = RedisVectorStore(dimensions=3, filter_tag_fields=["tenant"])
        command = store._index_command(3)
        self.assertEqual(command[:2], ["FT.CREATE", "agentuniverse_documents"])
        self.assertIn("HNSW", command)
        self.assertIn("FLOAT32", command)
        self.assertIn("meta_tenant", command)
        self.assertIn("COSINE", command)

    def test_rejects_unsafe_identifiers(self):
        """Verify unsafe index names, key prefixes and tag fields are rejected."""
        with self.assertRaisesRegex(ValueError, "index_name"):
            RedisVectorStore(index_name="idx; FLUSHALL")._validate_config(False)
        with self.assertRaisesRegex(ValueError, "key_prefix"):
            RedisVectorStore(key_prefix="prefix *")._validate_config(False)
        with self.assertRaisesRegex(ValueError, "filter_tag_fields"):
            RedisVectorStore(filter_tag_fields=["bad-name"])._validate_config(False)

    def test_vector_binary_round_trip(self):
        """Verify vectors round-trip losslessly through the binary encoding."""
        vector = [0.1, -0.2, 3.0]
        decoded = RedisVectorStore._bytes_vector(RedisVectorStore._vector_bytes(vector))
        for actual, expected in zip(decoded, vector, strict=True):
            self.assertAlmostEqual(actual, expected, places=6)

    def test_rejects_dimension_mismatch_and_nonfinite(self):
        """Verify dimension mismatches and non-finite vectors are rejected."""
        store = RedisVectorStore(dimensions=2)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._check_vector([1.0])
        with self.assertRaisesRegex(ValueError, "finite"):
            store._check_vector([float("nan"), 1.0])

    def test_query_and_row_conversion(self):
        """Verify FT.SEARCH responses convert into Documents with metadata and embeddings."""
        vector = RedisVectorStore._vector_bytes([1.0, 0.0])
        response = [
            1,
            b"agentuniverse:document:one",
            [b"id", b"one", b"text", b"hello", b"metadata", b'{"team":"a"}', b"embedding", vector],
        ]
        connection = FakeConnection(response)
        store = RedisVectorStore(client=connection, dimensions=2, create_index=False)
        documents = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=1))
        self.assertEqual(documents[0].id, "one")
        self.assertEqual(documents[0].metadata, {"team": "a"})
        self.assertEqual(documents[0].embedding, [1.0, 0.0])
        self.assertEqual(connection.calls[-1][0], "FT.SEARCH")

    def test_query_builds_indexed_metadata_filter(self):
        """Verify metadata filters over indexed tag fields are rendered into the query."""
        connection = FakeConnection()
        store = RedisVectorStore(
            client=connection,
            dimensions=2,
            create_index=False,
            filter_tag_fields=["tenant", "active"],
        )
        store.query(
            Query(embeddings=[[1.0, 0.0]], similarity_top_k=3),
            metadata_filter={"tenant": "a b", "active": True},
        )
        query = connection.calls[-1][2]
        self.assertIn("@meta_tenant:{a\\ b}", query)
        self.assertIn("@meta_active:{true}", query)

    def test_query_rejects_unindexed_filter(self):
        """Verify filters over fields that are not indexed tag fields raise a ValueError."""
        store = RedisVectorStore(client=FakeConnection(), dimensions=2, create_index=False)
        with self.assertRaisesRegex(ValueError, "not indexed"):
            store.query(Query(embeddings=[[1.0, 0.0]]), metadata_filter={"tenant": "a"})

    def test_invalid_top_k_fails_before_redis(self):
        """Verify a negative similarity_top_k fails before any redis call is made."""
        connection = FakeConnection()
        store = RedisVectorStore(client=connection, dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))
        self.assertEqual(connection.calls, [])

    def test_upsert_uses_pipeline_and_filter_fields(self):
        """Verify upsert writes indexed tag fields and metadata through the pipeline."""
        connection = FakeConnection()
        store = RedisVectorStore(
            client=connection,
            dimensions=2,
            create_index=False,
            filter_tag_fields=["tenant"],
        )
        store.upsert_document([Document(id="1", text="hello", metadata={"tenant": "acme"}, embedding=[0.1, 0.2])])
        key, mapping = connection.pipeline_obj.calls[0]
        self.assertEqual(key, "agentuniverse:document:1")
        self.assertEqual(mapping["meta_tenant"], "acme")
        self.assertEqual(json.loads(mapping["metadata"]), {"tenant": "acme"})
        self.assertTrue(connection.pipeline_obj.executed)

    def test_delete_uses_prefixed_key(self):
        """Verify delete_document targets the key produced by the key_prefix."""
        connection = FakeConnection()
        RedisVectorStore(client=connection).delete_document("abc")
        self.assertEqual(connection.deleted, ["agentuniverse:document:abc"])

    def test_missing_embeddings_require_model(self):
        """Verify upserting documents without embeddings requires an embedding model."""
        store = RedisVectorStore(client=FakeConnection(), dimensions=2, create_index=False)
        with self.assertRaisesRegex(ValueError, "embedding_model"):
            store.upsert_document([Document(text="hello")])

    def test_managed_embeddings(self):
        """Verify missing document embeddings are generated by the embedding model."""
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = RedisVectorStore(client=FakeConnection(), dimensions=2, create_index=False, embedding_model="embed")
        document = Document(text="hello")
        with patch("agentuniverse.agent.action.knowledge.store.redis_vector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([document])
        self.assertEqual(document.embedding, [0.1, 0.2])

    def test_connection_url_from_environment(self):
        """Verify the connection URL falls back to the REDIS_VECTOR_URL env var."""
        with patch.dict("os.environ", {"REDIS_VECTOR_URL": "redis://test"}):
            self.assertEqual(RedisVectorStore()._url(), "redis://test")

    def test_missing_dependency_hint(self):
        """Verify a helpful ImportError is raised when the redis package is absent."""
        with patch.dict("sys.modules", {"redis": None}), self.assertRaisesRegex(ImportError, "redis package"):
            RedisVectorStore._dependencies()

    def test_existing_index_error_is_accepted(self):
        """Verify an index-already-exists error is tolerated during index creation."""
        class ExistingConnection(FakeConnection):
            """A fake connection whose index command always reports the index exists."""

            def execute_command(self, *args):
                """Raise a RuntimeError to simulate an index that already exists."""
                raise RuntimeError("Index already exists")

        RedisVectorStore(client=ExistingConnection(), dimensions=2)._ensure_index(2)

    def test_async_crud(self):
        """Verify async upsert, query and delete flow through the async client."""
        vector = RedisVectorStore._vector_bytes([0.0, 1.0])
        response = [1, b"doc:1", [b"id", b"1", b"text", b"async", b"metadata", b"{}", b"embedding", vector]]
        connection = FakeAsyncConnection(response)
        store = RedisVectorStore(async_client=connection, dimensions=2, create_index=False)

        async def run():
            """Exercise async upsert/query/delete and return the query result."""
            await store.async_upsert_document([Document(id="1", text="async", embedding=[0.0, 1.0])])
            result = await store.async_query(Query(embeddings=[[0.0, 1.0]], similarity_top_k=1))
            await store.async_delete_document("1")
            return result

        result = asyncio.run(run())
        self.assertEqual(result[0].text, "async")
        self.assertTrue(connection.pipeline_obj.executed)
        self.assertEqual(connection.deleted, ["agentuniverse:document:1"])

    def test_component_schema(self):
        """Verify the store component loads its config with the correct metadata."""
        config = Configer()
        config.value = {
            "name": "redis_vector_store",
            "dimensions": 3,
            "metadata": {
                "type": "STORE",
                "module": "agentuniverse.agent.action.knowledge.store.redis_vector_store",
                "class": "RedisVectorStore",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.STORE.value)
        self.assertEqual(component.metadata_class, "RedisVectorStore")


if __name__ == "__main__":
    unittest.main()
