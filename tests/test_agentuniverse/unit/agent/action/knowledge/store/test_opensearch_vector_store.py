#!/usr/bin/env python3
"""Tests for OpenSearchVectorStore."""

import asyncio
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.opensearch_vector_store import OpenSearchVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakeIndices:
    def __init__(self, exists=False):
        self.exists_value = exists
        self.created = []

    def exists(self, index):
        self.exists_index = index
        return self.exists_value

    def create(self, index, body):
        self.created.append((index, body))
        return {"acknowledged": True}


class FakeClient:
    def __init__(self, search_result=None, exists=False):
        self.indices = FakeIndices(exists)
        self.bulk_calls = []
        self.search_calls = []
        self.delete_calls = []
        self.search_result = search_result or {"hits": {"hits": []}}

    def bulk(self, **kwargs):
        self.bulk_calls.append(kwargs)
        return {"errors": False, "items": []}

    def search(self, **kwargs):
        self.search_calls.append(kwargs)
        return self.search_result

    def delete(self, **kwargs):
        self.delete_calls.append(kwargs)
        return {"result": "deleted"}


class FakeAsyncIndices(FakeIndices):
    async def exists(self, index):
        return super().exists(index)

    async def create(self, index, body):
        return super().create(index, body)


class FakeAsyncClient(FakeClient):
    def __init__(self, search_result=None, exists=False):
        super().__init__(search_result, exists)
        self.indices = FakeAsyncIndices(exists)

    async def bulk(self, **kwargs):
        return super().bulk(**kwargs)

    async def search(self, **kwargs):
        return super().search(**kwargs)

    async def delete(self, **kwargs):
        return super().delete(**kwargs)


class TestOpenSearchVectorStore(unittest.TestCase):
    def test_optional_dependency_is_resolver_compatible(self):
        project_file = next(
            parent / "pyproject.toml" for parent in Path(__file__).parents if (parent / "pyproject.toml").is_file()
        )
        with project_file.open("rb") as stream:
            poetry = tomllib.load(stream)["tool"]["poetry"]
        self.assertEqual(poetry["dependencies"]["opensearch-py"], {"version": "^2.8.0", "optional": True})
        self.assertIn("opensearch-py", poetry["extras"]["store_ext"])

    def test_mapping_contains_hnsw_and_keyword_filters(self):
        store = OpenSearchVectorStore(dimensions=3, filter_fields=["tenant"], distance="cosine")
        mapping = store._mapping(3)
        properties = mapping["mappings"]["properties"]
        self.assertTrue(mapping["settings"]["index"]["knn"])
        self.assertEqual(properties["embedding"]["dimension"], 3)
        self.assertEqual(properties["embedding"]["method"]["space_type"], "cosinesimil")
        self.assertEqual(properties["metadata"]["properties"]["tenant"], {"type": "keyword"})

    def test_rejects_unsafe_configuration(self):
        with self.assertRaisesRegex(ValueError, "index_name"):
            OpenSearchVectorStore(index_name="Bad Index")._validate_config(False)
        with self.assertRaisesRegex(ValueError, "filter_fields"):
            OpenSearchVectorStore(filter_fields=["bad-name"])._validate_config(False)
        with self.assertRaisesRegex(ValueError, "distance"):
            OpenSearchVectorStore(distance="unknown")._validate_config(False)

    def test_rejects_dimension_mismatch_and_nonfinite_vectors(self):
        store = OpenSearchVectorStore(dimensions=2)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._validate_vector([1.0], "embedding")
        with self.assertRaisesRegex(ValueError, "finite"):
            store._validate_vector([float("nan"), 1.0], "embedding")

    def test_index_is_created_once(self):
        client = FakeClient(exists=False)
        store = OpenSearchVectorStore(client=client, dimensions=2)
        store._ensure_index(2)
        self.assertEqual(len(client.indices.created), 1)
        self.assertEqual(client.indices.created[0][0], "agentuniverse-documents")

    def test_existing_index_is_not_recreated(self):
        client = FakeClient(exists=True)
        OpenSearchVectorStore(client=client, dimensions=2)._ensure_index(2)
        self.assertEqual(client.indices.created, [])

    def test_upsert_builds_bulk_index_actions(self):
        client = FakeClient(exists=True)
        store = OpenSearchVectorStore(client=client, dimensions=2, refresh="wait_for")
        store.upsert_document([Document(id="1", text="hello", metadata={"tenant": "acme"}, embedding=[0.1, 0.2])])
        call = client.bulk_calls[0]
        self.assertEqual(call["body"][0], {"index": {"_index": "agentuniverse-documents", "_id": "1"}})
        self.assertEqual(call["body"][1]["embedding"], [0.1, 0.2])
        self.assertEqual(call["body"][1]["metadata"], {"tenant": "acme"})
        self.assertEqual(call["refresh"], "wait_for")

    def test_bulk_failures_are_not_silenced(self):
        result = {"errors": True, "items": [{"index": {"error": {"reason": "bad"}}}]}
        with self.assertRaisesRegex(RuntimeError, "1 document"):
            OpenSearchVectorStore._raise_bulk_errors(result)

    def test_query_builds_knn_filter_and_converts_hits(self):
        response = {
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_score": 0.9,
                        "_source": {
                            "id": "1",
                            "text": "hello",
                            "metadata": {"tenant": "acme"},
                            "embedding": [1.0, 0.0],
                        },
                    }
                ]
            }
        }
        client = FakeClient(response, exists=True)
        store = OpenSearchVectorStore(client=client, dimensions=2, filter_fields=["tenant"])
        documents = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=3), metadata_filter={"tenant": "acme"})
        body = client.search_calls[0]["body"]
        self.assertEqual(body["size"], 3)
        self.assertEqual(
            body["query"]["knn"]["embedding"]["filter"],
            {"bool": {"filter": [{"term": {"metadata.tenant": "acme"}}]}},
        )
        self.assertEqual(documents[0].id, "1")
        self.assertEqual(documents[0].metadata["_opensearch_score"], 0.9)

    def test_unfiltered_query_uses_direct_knn_query(self):
        client = FakeClient(exists=True)
        store = OpenSearchVectorStore(client=client, dimensions=2)
        store.query(Query(embeddings=[[0.0, 1.0]]))
        self.assertIn("knn", client.search_calls[0]["body"]["query"])

    def test_rejects_unindexed_metadata_filter(self):
        store = OpenSearchVectorStore(client=FakeClient(exists=True), dimensions=2)
        with self.assertRaisesRegex(ValueError, "not indexed"):
            store.query(Query(embeddings=[[1.0, 0.0]]), metadata_filter={"tenant": "acme"})

    def test_invalid_top_k_fails_before_client_call(self):
        client = FakeClient(exists=True)
        store = OpenSearchVectorStore(client=client, dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))
        self.assertEqual(client.search_calls, [])

    def test_delete_uses_document_id_and_ignore_404(self):
        client = FakeClient()
        OpenSearchVectorStore(client=client).delete_document("abc")
        self.assertEqual(client.delete_calls[0]["id"], "abc")
        self.assertEqual(client.delete_calls[0]["ignore"], [404])

    def test_managed_embeddings(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = OpenSearchVectorStore(client=FakeClient(exists=True), dimensions=2, embedding_model="embedding")
        with patch("agentuniverse.agent.action.knowledge.store.opensearch_vector_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([Document(id="1", text="managed")])
        model.get_embeddings.assert_called_once_with(["managed"])

    def test_connection_url_environment_fallback(self):
        with patch.dict("os.environ", {"OPENSEARCH_VECTOR_URL": "http://example:9200"}):
            args = OpenSearchVectorStore()._resolved_connection_args()
        self.assertEqual(args["hosts"], ["http://example:9200"])

    def test_explicit_hosts_override_environment(self):
        store = OpenSearchVectorStore(connection_args={"hosts": ["http://explicit:9200"]})
        with patch.dict("os.environ", {"OPENSEARCH_VECTOR_URL": "http://environment:9200"}):
            self.assertEqual(store._resolved_connection_args()["hosts"], ["http://explicit:9200"])

    def test_missing_dependency_hint(self):
        with patch.dict("sys.modules", {"opensearchpy": None}), self.assertRaisesRegex(ImportError, "opensearch-py"):
            OpenSearchVectorStore._dependencies()

    def test_async_crud(self):
        response = {"hits": {"hits": [{"_id": "1", "_source": {"id": "1", "text": "async", "embedding": [0.0, 1.0]}}]}}
        client = FakeAsyncClient(response, exists=True)
        store = OpenSearchVectorStore(async_client=client, dimensions=2)

        async def run():
            await store.async_upsert_document([Document(id="1", text="async", embedding=[0.0, 1.0])])
            result = await store.async_query(Query(embeddings=[[0.0, 1.0]], similarity_top_k=1))
            await store.async_delete_document("1")
            return result

        result = asyncio.run(run())
        self.assertEqual(result[0].text, "async")
        self.assertEqual(client.bulk_calls[0]["body"][1]["id"], "1")
        self.assertEqual(client.delete_calls[0]["id"], "1")

    def test_component_schema(self):
        config = Configer()
        config.value = {
            "name": "opensearch_vector_store",
            "dimensions": 3,
            "metadata": {
                "type": "STORE",
                "module": "agentuniverse.agent.action.knowledge.store.opensearch_vector_store",
                "class": "OpenSearchVectorStore",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.STORE.value)
        self.assertEqual(component.metadata_class, "OpenSearchVectorStore")


if __name__ == "__main__":
    unittest.main()
