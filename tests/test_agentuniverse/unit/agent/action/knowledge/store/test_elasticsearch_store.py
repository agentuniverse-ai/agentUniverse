#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : dxz0069
# @FileName: test_elasticsearch_store.py

import unittest
from unittest.mock import MagicMock

import os
import sys
import types

try:
    import elasticsearch  # noqa: F401

    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    # Inject a minimal fake of the client library so the component's lazy
    # import resolves and the behavioral tests below still run everywhere;
    # the fake is only the client class, all connection behavior is mocked
    # by the tests themselves.
    _fake_elasticsearch = types.ModuleType("elasticsearch")
    _fake_elasticsearch.Elasticsearch = MagicMock()
    sys.modules.setdefault("elasticsearch", _fake_elasticsearch)

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class TestElasticsearchStore(unittest.TestCase):
    """Test cases for the Elasticsearch store, run against mocked clients."""

    def setUp(self):
        from agentuniverse.agent.action.knowledge.store.elasticsearch_store import ElasticsearchStore
        self.ElasticsearchStore = ElasticsearchStore
        self.store = ElasticsearchStore(index_name="test_index")

    def _mock_client(self):
        client = MagicMock()
        client.indices.exists.return_value = False
        self.store.client = client
        return client

    def test_similarity_mapping(self):
        self.assertEqual(self.store._similarity(), "cosine")
        self.assertEqual(self.ElasticsearchStore(distance="EUCLID")._similarity(), "l2_norm")
        self.assertEqual(self.ElasticsearchStore(distance="DOT")._similarity(), "dot_product")
        self.assertEqual(self.ElasticsearchStore(distance="unknown")._similarity(), "cosine")

    def test_insert_creates_index_with_dense_vector_mapping(self):
        client = self._mock_client()
        documents = [Document(id="doc1", text="hello", embedding=[0.1, 0.2])]
        self.store.insert_document(documents)
        create_kwargs = client.indices.create.call_args.kwargs
        self.assertEqual(create_kwargs["index"], "test_index")
        vector_field = create_kwargs["mappings"]["properties"]["embedding"]
        self.assertEqual(vector_field["type"], "dense_vector")
        self.assertEqual(vector_field["dims"], 2)
        self.assertEqual(vector_field["similarity"], "cosine")

    def test_insert_indexes_documents_by_id(self):
        client = self._mock_client()
        documents = [
            Document(id="doc1", text="hello", embedding=[0.1, 0.2], metadata={"k": "v"}),
            Document(id="doc2", text="no embedding"),
        ]
        self.store.insert_document(documents)
        self.assertEqual(client.index.call_count, 1)
        kwargs = client.index.call_args.kwargs
        self.assertEqual(kwargs["index"], "test_index")
        self.assertEqual(kwargs["id"], "doc1")
        self.assertEqual(kwargs["document"]["text"], "hello")
        self.assertEqual(kwargs["document"]["metadata"], {"k": "v"})

    def test_upsert_and_update_share_write_path(self):
        client = self._mock_client()
        documents = [Document(id="doc1", text="hello", embedding=[0.1, 0.2])]
        self.store.upsert_document(documents)
        self.store.update_document(documents)
        self.assertEqual(client.index.call_count, 2)

    def test_query_uses_knn_search(self):
        client = self._mock_client()
        client.indices.exists.return_value = True
        client.search.return_value = {
            "hits": {
                "hits": [
                    {"_id": "doc1", "_source": {"text": "hello", "metadata": {"k": "v"},
                                                "embedding": [0.1, 0.2]}}
                ]
            }
        }
        results = self.store.query(Query(query_str="hi", embeddings=[[0.1, 0.2]], similarity_top_k=5))
        search_kwargs = client.search.call_args.kwargs
        self.assertEqual(search_kwargs["index"], "test_index")
        knn = search_kwargs["knn"]
        self.assertEqual(knn["field"], "embedding")
        self.assertEqual(knn["query_vector"], [0.1, 0.2])
        self.assertEqual(knn["k"], 5)
        self.assertEqual(knn["num_candidates"], 50)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "doc1")
        self.assertEqual(results[0].text, "hello")
        self.assertEqual(results[0].metadata, {"k": "v"})
        # vectors are only attached when requested
        self.assertEqual(results[0].embedding, [])

    def test_query_with_vectors(self):
        client = self._mock_client()
        client.indices.exists.return_value = True
        client.search.return_value = {
            "hits": {"hits": [{"_id": "doc1", "_source": {"text": "hello", "embedding": [0.1, 0.2]}}]}
        }
        store = self.ElasticsearchStore(index_name="test_index", with_vectors=True)
        store.client = client
        results = store.query(Query(query_str="hi", embeddings=[[0.1, 0.2]]))
        self.assertEqual(results[0].embedding, [0.1, 0.2])

    def test_query_without_embeddings(self):
        self._mock_client()
        self.assertEqual(self.store.query(Query(query_str="hi")), [])
        self.store.client.search.assert_not_called()

    def test_query_without_client(self):
        store = self.ElasticsearchStore()
        self.assertEqual(store.query(Query(query_str="hi")), [])

    def test_delete_document(self):
        client = self._mock_client()
        client.indices.exists.return_value = True
        self.store.delete_document("doc1")
        client.delete.assert_called_once()
        kwargs = client.delete.call_args.kwargs
        self.assertEqual(kwargs["index"], "test_index")
        self.assertEqual(kwargs["id"], "doc1")
        self.assertEqual(kwargs["ignore"], [404])

    def test_delete_document_missing_index(self):
        client = self._mock_client()
        client.indices.exists.return_value = False
        self.store.delete_document("doc1")
        client.delete.assert_not_called()

    def test_new_client_connection_args(self):
        from agentuniverse.agent.action.knowledge.store.elasticsearch_store import DEFAULT_CONNECTION_ARGS
        store = self.ElasticsearchStore(
            connection_args={"hosts": "https://es.example.com:9200", "api_key": "secret"})
        with unittest.mock.patch("elasticsearch.Elasticsearch") as es_cls:
            client = store._new_client()
        self.assertIs(client, es_cls.return_value)
        kwargs = es_cls.call_args.kwargs
        self.assertEqual(kwargs["hosts"], "https://es.example.com:9200")
        self.assertEqual(kwargs["api_key"], "secret")
        self.assertNotIn("basic_auth", kwargs)


@unittest.skipUnless(
    ELASTICSEARCH_AVAILABLE and os.environ.get("ELASTICSEARCH_HOST"),
    "real integration test: install elasticsearch, start Elasticsearch "
    "(docker run -d -p 9200:9200 -e discovery.type=single-node -e xpack.security.enabled=false "
    "docker.elastic.co/elasticsearch/elasticsearch:8.15.0) and set ELASTICSEARCH_HOST to run",
)
class TestElasticsearchStoreIntegration(unittest.TestCase):
    """Integration tests against a real Elasticsearch server.

    Start a server and set the endpoint to run:
        docker run -d --name elasticsearch -p 9200:9200 \
            -e discovery.type=single-node -e xpack.security.enabled=false \
            docker.elastic.co/elasticsearch/elasticsearch:8.15.0
        ELASTICSEARCH_HOST=http://localhost:9200 python -m pytest \
            tests/test_agentuniverse/unit/agent/action/knowledge/store/test_elasticsearch_store.py
    """

    def test_roundtrip(self):
        import uuid as uuid_module
        from agentuniverse.agent.action.knowledge.store.elasticsearch_store import ElasticsearchStore

        index_name = "test_" + uuid_module.uuid4().hex[:8]
        store = ElasticsearchStore(
            index_name=index_name,
            connection_args={"hosts": os.environ["ELASTICSEARCH_HOST"]},
        )
        store.client = store._new_client()
        try:
            documents = [
                Document(id="doc1", text="hello world", embedding=[1.0, 0.0], metadata={"k": "v"}),
                Document(id="doc2", text="goodbye world", embedding=[0.0, 1.0]),
            ]
            store.insert_document(documents)
            store.client.indices.refresh(index=index_name)
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=1))
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].text, "hello world")
            store.upsert_document([Document(id="doc1", text="updated", embedding=[1.0, 0.1])])
            store.client.indices.refresh(index=index_name)
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
            texts = {document.text for document in results}
            self.assertIn("updated", texts)
            self.assertNotIn("hello world", texts)
            store.delete_document("doc1")
            store.client.indices.refresh(index=index_name)
            results = store.query(Query(query_str="hi", embeddings=[[1.0, 0.0]], similarity_top_k=10))
            self.assertEqual([document.text for document in results], ["goodbye world"])
        finally:
            if store.client.indices.exists(index=index_name):
                store.client.indices.delete(index=index_name)


if __name__ == "__main__":
    unittest.main()
