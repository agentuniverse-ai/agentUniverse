import asyncio
import json
import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.vespa_store import VespaStore
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class FakeResponse:
    """Stand-in for pyvespa VespaResponse / VespaQueryResponse objects."""

    def __init__(self, status_code=200, successful=True, payload=None):
        self.status_code = status_code
        self._successful = successful
        self._payload = payload or {}

    def is_successful(self):
        return self._successful

    def get_json(self):
        return self._payload


class FakeVespaClient:
    """Mimics the subset of the pyvespa sync client used by VespaStore."""

    def __init__(self, query_response=None):
        self.fed = []
        self.deleted = []
        self.query_response = query_response or FakeResponse(payload={"root": {"children": []}})

    def feed_data_point(self, schema, data_id, fields, namespace=None, **kwargs):
        self.fed.append((schema, namespace, data_id, fields))
        return FakeResponse()

    def delete_data(self, schema, data_id, namespace=None, **kwargs):
        self.deleted.append((schema, namespace, str(data_id)))
        return FakeResponse()

    def query(self, body=None, **kwargs):
        self.last_body = body
        return self.query_response


class FakeAsyncVespaClient(FakeVespaClient):
    async def feed_data_point(self, schema, data_id, fields, namespace=None, **kwargs):
        self.fed.append((schema, namespace, data_id, fields))
        return FakeResponse()

    async def delete_data(self, schema, data_id, namespace=None, **kwargs):
        self.deleted.append((schema, namespace, str(data_id)))
        return FakeResponse()

    async def query(self, body=None, **kwargs):
        self.last_body = body
        return self.query_response


def _hit(document_id, text, metadata, embedding):
    return {
        "id": f"id:agentuniverse:agentuniverse_document::{document_id}",
        "fields": {
            "id": document_id,
            "text": text,
            "metadata": json.dumps(metadata),
            "embedding": embedding,
        },
    }


class VespaStoreTest(unittest.TestCase):
    def test_rejects_unsafe_schema_name(self):
        with self.assertRaisesRegex(ValueError, "schema_name"):
            VespaStore(schema_name="bad name")._validate_config(False)

    def test_rejects_invalid_application_url(self):
        with self.assertRaisesRegex(ValueError, "application_url"):
            VespaStore(application_url="not-a-url")._url()
        with self.assertRaisesRegex(ValueError, "application_url is required"):
            VespaStore()._url()

    def test_invalid_top_k_fails_before_query(self):
        store = VespaStore(client=FakeVespaClient(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "similarity_top_k"):
            store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=-1))

    def test_query_requires_embedding(self):
        store = VespaStore(client=FakeVespaClient(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "requires embeddings"):
            store.query(Query(query_str="hello"))

    def test_rejects_dimension_mismatch(self):
        store = VespaStore(dimensions=3)
        with self.assertRaisesRegex(ValueError, "does not match"):
            store._check_vector([1.0, 2.0])

    def test_infers_dimension(self):
        store = VespaStore()
        store._check_vector([1.0, 2.0, 3.0])
        self.assertEqual(store.dimensions, 3)

    def test_yql_contains_nearest_neighbor_and_top_k(self):
        store = VespaStore(schema_name="docs", dimensions=2)
        body = store._yql([1.0, 0.0], 4, None)
        self.assertIn("nearestNeighbor(embedding, query_embedding)", body["yql"])
        self.assertIn("targetHits:4", body["yql"])
        self.assertIn("from docs", body["yql"])
        self.assertEqual(body["hits"], 4)
        self.assertEqual(body["input.query(query_embedding)"], [1.0, 0.0])

    def test_yql_appends_metadata_filter(self):
        store = VespaStore(dimensions=2)
        body = store._yql([1.0, 0.0], 3, {"team": "acme"})
        self.assertIn("AND", body["yql"])
        self.assertIn('"team"', body["yql"])
        self.assertIn('"acme"', body["yql"])

    def test_yql_rejects_bad_filter_key(self):
        store = VespaStore(dimensions=2)
        with self.assertRaisesRegex(ValueError, "valid identifier"):
            store._yql([1.0, 0.0], 3, {"bad key!": "x"})

    def test_query_converts_hits_to_documents(self):
        payload = {"root": {"children": [_hit("1", "hello", {"team": "a"}, [0.1, 0.2])]}}
        client = FakeVespaClient(query_response=FakeResponse(payload=payload))
        store = VespaStore(client=client, dimensions=2)
        results = store.query(Query(embeddings=[[1.0, 0.0]], similarity_top_k=5))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "1")
        self.assertEqual(results[0].text, "hello")
        self.assertEqual(results[0].metadata, {"team": "a"})
        self.assertEqual(results[0].embedding, [0.1, 0.2])

    def test_query_uses_embedding_component(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = VespaStore(client=FakeVespaClient(), dimensions=2, embedding_model="embed")
        with patch("agentuniverse.agent.action.knowledge.store.vespa_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.query(Query(query_str="hello"))
        manager.return_value.get_instance_obj.assert_called_once_with("embed", strict=True)

    def test_upsert_feeds_each_document(self):
        client = FakeVespaClient()
        store = VespaStore(client=client, dimensions=2, schema_name="docs", namespace="ns")
        store.upsert_document(
            [Document(id="1", text="hello", metadata={"a": 1}, embedding=[0.1, 0.2])]
        )
        schema, namespace, data_id, fields = client.fed[0]
        self.assertEqual((schema, namespace, data_id), ("docs", "ns", "1"))
        self.assertEqual(fields["text"], "hello")
        self.assertEqual(json.loads(fields["metadata"]), {"a": 1})
        self.assertEqual(fields["embedding"], [0.1, 0.2])

    def test_upsert_generates_missing_embeddings(self):
        model = Mock()
        model.get_embeddings.return_value = [[0.1, 0.2]]
        store = VespaStore(client=FakeVespaClient(), dimensions=2, embedding_model="embed")
        document = Document(id="1", text="hello")
        with patch("agentuniverse.agent.action.knowledge.store.vespa_store.EmbeddingManager") as manager:
            manager.return_value.get_instance_obj.return_value = model
            store.upsert_document([document])
        self.assertEqual(document.embedding, [0.1, 0.2])

    def test_upsert_without_embeddings_requires_model(self):
        store = VespaStore(client=FakeVespaClient(), dimensions=2)
        with self.assertRaisesRegex(ValueError, "embedding_model"):
            store.upsert_document([Document(id="1", text="hello")])

    def test_delete_passes_schema_and_namespace(self):
        client = FakeVespaClient()
        VespaStore(client=client, schema_name="docs", namespace="ns").delete_document("abc")
        self.assertEqual(client.deleted, [("docs", "ns", "abc")])

    def test_upsert_raises_on_failure(self):
        client = FakeVespaClient()
        client.feed_data_point = Mock(return_value=FakeResponse(status_code=500, successful=False))
        store = VespaStore(client=client, dimensions=2)
        with self.assertRaisesRegex(RuntimeError, "upsert"):
            store.upsert_document([Document(id="1", text="x", embedding=[0.1, 0.2])])

    def test_new_client_passes_mtls_credentials(self):
        vespa_cls = Mock()
        store = VespaStore(application_url="http://localhost:8080", cert_path="c.pem", key_path="k.pem")
        with patch.object(store, "_dependencies", return_value=vespa_cls):
            store._new_client()
        vespa_cls.assert_called_once_with(
            url="http://localhost:8080", cert="c.pem", key="k.pem"
        )

    def test_missing_dependency_hint(self):
        with patch.dict("sys.modules", {"vespa.application": None, "vespa": None}):
            with self.assertRaisesRegex(ImportError, "pyvespa"):
                VespaStore._dependencies()

    def test_async_crud(self):
        payload = {"root": {"children": [_hit("1", "async", {}, [0.0, 1.0])]}}
        client = FakeAsyncVespaClient(query_response=FakeResponse(payload=payload))
        store = VespaStore(async_client=client, dimensions=2)

        async def run():
            await store.async_upsert_document([Document(id="1", text="async", embedding=[0.0, 1.0])])
            result = await store.async_query(Query(embeddings=[[0.0, 1.0]], similarity_top_k=1))
            await store.async_delete_document("1")
            return result

        result = asyncio.run(run())
        self.assertEqual(result[0].text, "async")
        self.assertEqual(client.deleted, [("agentuniverse_document", "agentuniverse", "1")])
        self.assertEqual(len(client.fed), 1)

    def test_component_schema(self):
        config = Configer()
        config.value = {
            "name": "vespa_store",
            "dimensions": 3,
            "metadata": {
                "type": "STORE",
                "module": "agentuniverse.agent.action.knowledge.store.vespa_store",
                "class": "VespaStore",
            },
        }
        component = ComponentConfiger().load_by_configer(config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.STORE.value)
        self.assertEqual(component.metadata_class, "VespaStore")


if __name__ == "__main__":
    unittest.main()
