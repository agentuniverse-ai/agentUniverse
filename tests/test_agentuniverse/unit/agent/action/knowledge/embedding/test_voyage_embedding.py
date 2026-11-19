# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: test_voyage_embedding.py

import asyncio
import json
import unittest

import httpx

from agentuniverse.agent.action.knowledge.embedding.voyage_embedding import VoyageEmbedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _vector_for(text: str) -> list:
    """Deterministic vector derived from the text, used to verify ordering."""
    return [float(len(text)), float(sum(ord(c) for c in text) % 1000)]


class _VoyageMockTransport(httpx.MockTransport):
    """Mock transport recording requests and serving Voyage AI style responses."""

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
                                         "model": payload["model"]})


class _ShuffledVoyageMockTransport(_VoyageMockTransport):
    """Mock transport returning embeddings out of index order."""

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        payload = json.loads(request.content.decode("utf-8"))
        data = [{"object": "embedding", "embedding": _vector_for(text),
                 "index": i}
                for i, text in enumerate(payload["input"])]
        data.reverse()
        return httpx.Response(200, json={"object": "list", "data": data})


class VoyageEmbeddingTest(unittest.TestCase):
    """Offline tests for VoyageEmbedding with a mocked httpx transport."""

    def setUp(self) -> None:
        self.embedding = VoyageEmbedding(api_key="test_api_key")

    def _attach_transport(self, transport: httpx.MockTransport) -> None:
        self.embedding.client = httpx.Client(transport=transport)

    @staticmethod
    def _sent_payloads(transport) -> list:
        return [json.loads(r.content.decode("utf-8"))
                for r in transport.get_requests()]

    def test_request_shape(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["hello world", "agentUniverse"])

        self.assertEqual(result, [_vector_for("hello world"),
                                  _vector_for("agentUniverse")])
        recorded = transport.get_requests()
        self.assertEqual(len(recorded), 1)
        request = recorded[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(str(request.url),
                         "https://api.voyageai.com/v1/embeddings")
        self.assertEqual(request.headers["Authorization"],
                         "Bearer test_api_key")
        payload = json.loads(request.content.decode("utf-8"))
        self.assertEqual(payload["model"], "voyage-3.5")
        self.assertEqual(payload["input"], ["hello world", "agentUniverse"])
        self.assertEqual(payload["input_type"], "document")
        self.assertNotIn("output_dimension", payload)

    def test_dimension_passthrough(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        self.embedding.embedding_dims = 256
        self.embedding.get_embeddings(["hello"])

        payload = self._sent_payloads(transport)[0]
        self.assertEqual(payload["output_dimension"], 256)

    def test_input_type_per_call_override(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        self.embedding.get_embeddings(["hello"], input_type="query")

        payload = self._sent_payloads(transport)[0]
        self.assertEqual(payload["input_type"], "query")

    def test_invalid_input_type(self) -> None:
        self._attach_transport(_VoyageMockTransport())
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings(["hello"], input_type="unknown")
        self.assertIn("input_type", str(context.exception))

    def test_empty_texts(self) -> None:
        self._attach_transport(_VoyageMockTransport())
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings([])
        self.assertIn("non-empty", str(context.exception))

    def test_missing_api_key(self) -> None:
        embedding = VoyageEmbedding(api_key=None)
        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(["hello"])
        self.assertIn("api_key", str(context.exception))

    def test_empty_string_api_key_placeholder(self) -> None:
        embedding = VoyageEmbedding(api_key="")
        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(["hello"])
        self.assertIn("api_key", str(context.exception))

    def test_batching_by_input_count(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        texts = [f"text-{i}" for i in range(300)]
        result = self.embedding.get_embeddings(texts)

        payloads = self._sent_payloads(transport)
        self.assertEqual(len(payloads), 3)
        self.assertEqual(len(payloads[0]["input"]), 128)
        self.assertEqual(len(payloads[1]["input"]), 128)
        self.assertEqual(len(payloads[2]["input"]), 44)
        # Results are merged back in input order.
        self.assertEqual(result, [_vector_for(text) for text in texts])

    def test_batching_by_token_budget(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        # Each text is estimated at 5,000 tokens (20,000 chars / 4): seven of
        # them total 35,000 estimated tokens, exceeding the 32,000-token
        # budget per request, so the last text is split into a second request.
        long_texts = ["a" * 20000 for _ in range(7)]
        self.embedding.get_embeddings(long_texts)

        payloads = self._sent_payloads(transport)
        self.assertEqual(len(payloads), 2)
        self.assertEqual(len(payloads[0]["input"]), 6)
        self.assertEqual(len(payloads[1]["input"]), 1)

    def test_response_order_by_index(self) -> None:
        transport = _ShuffledVoyageMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["a", "bb", "ccc"])

        # Even though the mock returns data reversed, embeddings follow the
        # input order.
        self.assertEqual(result, [_vector_for("a"), _vector_for("bb"),
                                  _vector_for("ccc")])

    def test_http_error_propagation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, json={"error": "internal"})

        self.embedding.client = httpx.Client(
            transport=httpx.MockTransport(handler))
        with self.assertRaises(Exception) as context:
            self.embedding.get_embeddings(["hello"])
        self.assertIn("500", str(context.exception))

    def test_async_get_embeddings(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        result = asyncio.run(
            self.embedding.async_get_embeddings(["hello", "world"]))

        self.assertEqual(result, [_vector_for("hello"), _vector_for("world")])
        self.assertEqual(len(transport.get_requests()), 1)

    def test_as_langchain(self) -> None:
        transport = _VoyageMockTransport()
        self._attach_transport(transport)
        langchain_embedding = self.embedding.as_langchain()

        documents = langchain_embedding.embed_documents(["doc1", "doc2"])
        self.assertEqual(documents, [_vector_for("doc1"), _vector_for("doc2")])
        query = langchain_embedding.embed_query("query1")
        self.assertEqual(query, _vector_for("query1"))

        payloads = self._sent_payloads(transport)
        self.assertEqual(payloads[0]["input_type"], "document")
        self.assertEqual(payloads[1]["input_type"], "query")

    def test_initialize_by_component_configer(self) -> None:
        cfg = Configer()
        cfg.value = {
            'name': 'voyage_embedding',
            'description': 'embedding use voyage ai',
            'embedding_model_name': 'voyage-code-3',
            'embedding_dims': 1024,
            'api_key': 'cfg_api_key',
            'api_base': 'https://api.voyageai.com/v1',
            'input_type': 'query',
            'timeout': 60,
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        embedding = VoyageEmbedding()
        embedding._initialize_by_component_configer(configer)

        self.assertEqual(embedding.name, 'voyage_embedding')
        self.assertEqual(embedding.embedding_model_name, 'voyage-code-3')
        self.assertEqual(embedding.embedding_dims, 1024)
        self.assertEqual(embedding.api_key, 'cfg_api_key')
        self.assertEqual(embedding.api_base, 'https://api.voyageai.com/v1')
        self.assertEqual(embedding.input_type, 'query')
        self.assertEqual(embedding.timeout, 60)


if __name__ == '__main__':
    unittest.main()
