# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: test_tei_embedding.py

import asyncio
import json
import unittest

import httpx

from agentuniverse.agent.action.knowledge.embedding.tei_embedding import TEIEmbedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _vector_for(text: str) -> list:
    """Deterministic vector derived from the text, used to verify ordering."""
    return [float(len(text)), float(sum(ord(c) for c in text) % 1000)]


class _TEIMockTransport(httpx.MockTransport):
    """Mock transport recording requests and serving TEI style responses."""

    def __init__(self):
        self.requests = []
        super().__init__(self._handler)

    def get_requests(self) -> list:
        return self.requests

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        payload = json.loads(request.content.decode("utf-8"))
        data = []
        for i, text in enumerate(payload["input"]):
            data.append({"object": "embedding", "embedding": _vector_for(text),
                         "index": i})
        return httpx.Response(200, json={"object": "list", "data": data,
                                         "model": payload["model"],
                                         "usage": {"prompt_tokens": 1,
                                                   "total_tokens": 1}})


class _ShuffledTEIMockTransport(_TEIMockTransport):
    """Mock transport returning embeddings out of index order."""

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        payload = json.loads(request.content.decode("utf-8"))
        data = [{"object": "embedding", "embedding": _vector_for(text),
                 "index": i}
                for i, text in enumerate(payload["input"])]
        data.reverse()
        return httpx.Response(200, json={"object": "list", "data": data})


class TEIEmbeddingTest(unittest.TestCase):
    """Offline tests for TEIEmbedding with a mocked httpx transport."""

    def setUp(self) -> None:
        self.embedding = TEIEmbedding(api_key=None)

    def _attach_transport(self, transport: httpx.MockTransport) -> None:
        self.embedding.client = httpx.Client(transport=transport)

    @staticmethod
    def _sent_payloads(transport) -> list:
        return [json.loads(r.content.decode("utf-8"))
                for r in transport.get_requests()]

    def test_request_shape_keyless(self) -> None:
        transport = _TEIMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["hello world", "agentUniverse"])

        self.assertEqual(result, [_vector_for("hello world"),
                                  _vector_for("agentUniverse")])
        recorded = transport.get_requests()
        self.assertEqual(len(recorded), 1)
        request = recorded[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(str(request.url),
                         "http://localhost:8080/v1/embeddings")
        # TEI is keyless: no Authorization header by default.
        self.assertNotIn("Authorization", request.headers)
        payload = json.loads(request.content.decode("utf-8"))
        self.assertEqual(payload["model"], "BAAI/bge-m3")
        self.assertEqual(payload["input"], ["hello world", "agentUniverse"])
        # No dimensions parameter unless embedding_dims is configured.
        self.assertNotIn("dimensions", payload)

    def test_optional_api_key_sends_bearer(self) -> None:
        embedding = TEIEmbedding(api_key="proxy_token")
        transport = _TEIMockTransport()
        embedding.client = httpx.Client(transport=transport)
        embedding.get_embeddings(["hello"])

        request = transport.get_requests()[0]
        self.assertEqual(request.headers["Authorization"],
                         "Bearer proxy_token")

    def test_empty_string_api_key_is_treated_as_unset(self) -> None:
        embedding = TEIEmbedding(api_key="")
        transport = _TEIMockTransport()
        embedding.client = httpx.Client(transport=transport)
        # Keyless call still works, no Authorization header is sent.
        result = embedding.get_embeddings(["hello"])

        self.assertEqual(result, [_vector_for("hello")])
        self.assertNotIn("Authorization",
                         transport.get_requests()[0].headers)

    def test_dimensions_sent_when_configured(self) -> None:
        embedding = TEIEmbedding(api_key=None, embedding_dims=512)
        transport = _TEIMockTransport()
        embedding.client = httpx.Client(transport=transport)
        embedding.get_embeddings(["hello"])

        payload = self._sent_payloads(transport)[0]
        self.assertEqual(payload["dimensions"], 512)

    def test_custom_api_base(self) -> None:
        embedding = TEIEmbedding(api_key=None,
                                 api_base="http://tei.internal:9000/v1")
        transport = _TEIMockTransport()
        embedding.client = httpx.Client(transport=transport)
        embedding.get_embeddings(["hello"])

        request = transport.get_requests()[0]
        self.assertEqual(str(request.url),
                         "http://tei.internal:9000/v1/embeddings")

    def test_default_model(self) -> None:
        self.assertEqual(TEIEmbedding(api_key=None).embedding_model_name,
                         "BAAI/bge-m3")

    def test_empty_texts(self) -> None:
        self._attach_transport(_TEIMockTransport())
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings([])
        self.assertIn("non-empty", str(context.exception))

    def test_missing_model_name(self) -> None:
        embedding = TEIEmbedding(api_key=None, embedding_model_name=None)
        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(["hello"])
        self.assertIn("embedding_model_name", str(context.exception))

    def test_batching_by_input_count(self) -> None:
        transport = _TEIMockTransport()
        self._attach_transport(transport)
        texts = [f"text-{i}" for i in range(600)]
        result = self.embedding.get_embeddings(texts)

        payloads = self._sent_payloads(transport)
        self.assertEqual(len(payloads), 3)
        self.assertEqual(len(payloads[0]["input"]), 256)
        self.assertEqual(len(payloads[1]["input"]), 256)
        self.assertEqual(len(payloads[2]["input"]), 88)
        # Results are merged back in input order.
        self.assertEqual(result, [_vector_for(text) for text in texts])

    def test_batching_single_batch(self) -> None:
        transport = _TEIMockTransport()
        self._attach_transport(transport)
        texts = [f"text-{i}" for i in range(256)]
        self.embedding.get_embeddings(texts)

        payloads = self._sent_payloads(transport)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len(payloads[0]["input"]), 256)

    def test_response_order_by_index(self) -> None:
        transport = _ShuffledTEIMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["a", "bb", "ccc"])

        # Even though the mock returns data reversed, embeddings follow the
        # input order.
        self.assertEqual(result, [_vector_for("a"), _vector_for("bb"),
                                  _vector_for("ccc")])

    def test_malformed_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"data": [{"embedding": [0.1]}]})

        self.embedding.client = httpx.Client(
            transport=httpx.MockTransport(handler))
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(["a", "b"])
        self.assertIn("Malformed TEI embeddings response",
                      str(context.exception))

    def test_http_error_propagation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, json={"error": "model loading"})

        self.embedding.client = httpx.Client(
            transport=httpx.MockTransport(handler))
        with self.assertRaises(Exception) as context:
            self.embedding.get_embeddings(["hello"])
        self.assertIn("503", str(context.exception))
        self.assertIn("TEI server", str(context.exception))

    def test_async_get_embeddings(self) -> None:
        transport = _TEIMockTransport()
        self._attach_transport(transport)
        result = asyncio.run(
            self.embedding.async_get_embeddings(["hello", "world"]))

        self.assertEqual(result, [_vector_for("hello"), _vector_for("world")])
        self.assertEqual(len(transport.get_requests()), 1)

    def test_as_langchain(self) -> None:
        transport = _TEIMockTransport()
        self._attach_transport(transport)
        langchain_embedding = self.embedding.as_langchain()

        documents = langchain_embedding.embed_documents(["doc1", "doc2"])
        self.assertEqual(documents, [_vector_for("doc1"), _vector_for("doc2")])
        query = langchain_embedding.embed_query("query1")
        self.assertEqual(query, _vector_for("query1"))

        self.assertEqual(len(transport.get_requests()), 2)

    def test_initialize_by_component_configer(self) -> None:
        cfg = Configer()
        cfg.value = {
            'name': 'tei_embedding',
            'description': 'embedding use tei',
            'embedding_model_name': 'BAAI/bge-m3',
            'embedding_dims': 1024,
            'api_key': 'cfg_api_key',
            'api_base': 'http://localhost:9000/v1',
            'timeout': 60,
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        embedding = TEIEmbedding()
        embedding._initialize_by_component_configer(configer)

        self.assertEqual(embedding.name, 'tei_embedding')
        self.assertEqual(embedding.embedding_model_name, 'BAAI/bge-m3')
        self.assertEqual(embedding.embedding_dims, 1024)
        self.assertEqual(embedding.api_key, 'cfg_api_key')
        self.assertEqual(embedding.api_base, 'http://localhost:9000/v1')
        self.assertEqual(embedding.timeout, 60)


if __name__ == '__main__':
    unittest.main()
