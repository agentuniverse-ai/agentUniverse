# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @Time    : 2026/10/19
# @FileName: test_mistral_embedding.py

import asyncio
import json
import unittest

import httpx

from agentuniverse.agent.action.knowledge.embedding.mistral_embedding import MistralEmbedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _vector_for(text: str) -> list:
    """Deterministic vector derived from the text, used to verify ordering."""
    return [float(len(text)), float(sum(ord(c) for c in text) % 1000)]


class _MistralMockTransport(httpx.MockTransport):
    """Mock transport recording requests and serving Mistral style responses."""

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


class _ShuffledMistralMockTransport(_MistralMockTransport):
    """Mock transport returning embeddings out of index order."""

    def _handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        payload = json.loads(request.content.decode("utf-8"))
        data = [{"object": "embedding", "embedding": _vector_for(text),
                 "index": i}
                for i, text in enumerate(payload["input"])]
        data.reverse()
        return httpx.Response(200, json={"object": "list", "data": data})


class MistralEmbeddingTest(unittest.TestCase):
    """Offline tests for MistralEmbedding with a mocked httpx transport."""

    def setUp(self) -> None:
        self.embedding = MistralEmbedding(api_key="test_api_key")

    def _attach_transport(self, transport: httpx.MockTransport) -> None:
        self.embedding.client = httpx.Client(transport=transport)

    @staticmethod
    def _sent_payloads(transport) -> list:
        return [json.loads(r.content.decode("utf-8"))
                for r in transport.get_requests()]

    def test_request_shape(self) -> None:
        transport = _MistralMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["hello world", "agentUniverse"])

        self.assertEqual(result, [_vector_for("hello world"),
                                  _vector_for("agentUniverse")])
        recorded = transport.get_requests()
        self.assertEqual(len(recorded), 1)
        request = recorded[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(str(request.url),
                         "https://api.mistral.ai/v1/embeddings")
        self.assertEqual(request.headers["Authorization"],
                         "Bearer test_api_key")
        payload = json.loads(request.content.decode("utf-8"))
        self.assertEqual(payload["model"], "mistral-embed")
        self.assertEqual(payload["input"], ["hello world", "agentUniverse"])

    def test_default_model_and_dimension_note(self) -> None:
        # The default model is mistral-embed; embedding_dims stays None so no
        # dimension parameter is sent (mistral-embed outputs 1024 dimensions).
        embedding = MistralEmbedding(api_key="test_api_key")
        self.assertEqual(embedding.embedding_model_name, "mistral-embed")
        self.assertIsNone(embedding.embedding_dims)
        transport = _MistralMockTransport()
        self._attach_transport(transport)
        self.embedding.get_embeddings(["hello"])

        payload = self._sent_payloads(transport)[0]
        self.assertEqual(payload["model"], "mistral-embed")

    def test_empty_texts(self) -> None:
        self._attach_transport(_MistralMockTransport())
        with self.assertRaises(ValueError) as context:
            self.embedding.get_embeddings([])
        self.assertIn("non-empty", str(context.exception))

    def test_missing_api_key(self) -> None:
        embedding = MistralEmbedding(api_key=None)
        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(["hello"])
        self.assertIn("api_key", str(context.exception))

    def test_empty_string_api_key_placeholder(self) -> None:
        embedding = MistralEmbedding(api_key="")
        with self.assertRaises(ValueError) as context:
            embedding.get_embeddings(["hello"])
        self.assertIn("api_key", str(context.exception))

    def test_batching_by_input_count(self) -> None:
        transport = _MistralMockTransport()
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

    def test_batching_single_batch(self) -> None:
        transport = _MistralMockTransport()
        self._attach_transport(transport)
        texts = [f"text-{i}" for i in range(128)]
        self.embedding.get_embeddings(texts)

        payloads = self._sent_payloads(transport)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(len(payloads[0]["input"]), 128)

    def test_response_order_by_index(self) -> None:
        transport = _ShuffledMistralMockTransport()
        self._attach_transport(transport)
        result = self.embedding.get_embeddings(["a", "bb", "ccc"])

        # Even though the mock returns data reversed, embeddings follow the
        # input order.
        self.assertEqual(result, [_vector_for("a"), _vector_for("bb"),
                                  _vector_for("ccc")])

    def test_http_error_propagation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, json={"message": "rate limited"})

        self.embedding.client = httpx.Client(
            transport=httpx.MockTransport(handler))
        with self.assertRaises(Exception) as context:
            self.embedding.get_embeddings(["hello"])
        self.assertIn("429", str(context.exception))

    def test_async_get_embeddings(self) -> None:
        transport = _MistralMockTransport()
        self._attach_transport(transport)
        result = asyncio.run(
            self.embedding.async_get_embeddings(["hello", "world"]))

        self.assertEqual(result, [_vector_for("hello"), _vector_for("world")])
        self.assertEqual(len(transport.get_requests()), 1)

    def test_as_langchain(self) -> None:
        transport = _MistralMockTransport()
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
            'name': 'mistral_embedding',
            'description': 'embedding use mistral api',
            'embedding_model_name': 'mistral-embed',
            'embedding_dims': 1024,
            'api_key': 'cfg_api_key',
            'api_base': 'https://api.mistral.ai/v1',
            'timeout': 60,
        }
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)

        embedding = MistralEmbedding()
        embedding._initialize_by_component_configer(configer)

        self.assertEqual(embedding.name, 'mistral_embedding')
        self.assertEqual(embedding.embedding_model_name, 'mistral-embed')
        self.assertEqual(embedding.embedding_dims, 1024)
        self.assertEqual(embedding.api_key, 'cfg_api_key')
        self.assertEqual(embedding.api_base, 'https://api.mistral.ai/v1')
        self.assertEqual(embedding.timeout, 60)


if __name__ == '__main__':
    unittest.main()
