"""Exercise response alignment through real SDK clients, without network I/O."""
import asyncio
import base64
from copy import deepcopy
import json
import struct

import httpx
from openai import AsyncAzureOpenAI, AzureOpenAI
import pytest

from agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding import AzureOpenAIEmbedding
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding


def record(index, vector=None):
    return {"object": "embedding", "index": index,
            "embedding": vector if vector is not None else [0.25, 0.5]}


@pytest.fixture(params=[("openai", False), ("openai", True),
                       ("azure", False), ("azure", True)],
                ids=["openai-sync", "openai-async", "azure-sync", "azure-async"])
def invoke(request):
    provider, asynchronous = request.param

    def call(records, texts, dimensions=None, status=200):
        original_records, original_texts = deepcopy(records), list(texts)
        requests = []

        def respond(req):
            body = json.loads(req.content)
            requests.append(body)
            assert body["input"] == texts
            assert body["model"] == "test-model"
            if dimensions is None:
                assert "dimensions" not in body
            else:
                assert body["dimensions"] == dimensions
            if status != 200:
                return httpx.Response(status, json={"error": {
                    "message": "invalid input", "type": "invalid_request_error",
                    "param": "input", "code": None}})
            return httpx.Response(200, json={
                "object": "list", "model": "test-model", "data": records,
                "usage": {"prompt_tokens": 2, "total_tokens": 2},
            })

        async def run():
            with httpx.Client(transport=httpx.MockTransport(respond)) as sync_http:
                async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as async_http:
                    if provider == "openai":
                        embedding = OpenAIEmbedding(
                            embedding_model_name="test-model", dimensions=dimensions,
                            openai_api_key="offline-test", openai_client_args={
                                "base_url": "https://example.invalid/v1",
                                "max_retries": 0,
                                "http_client": async_http if asynchronous else sync_http,
                            },
                        )
                    else:
                        settings = {"api_key": "offline-test", "api_version": "2024-02-01",
                                    "azure_endpoint": "https://example.invalid", "max_retries": 0}
                        embedding = AzureOpenAIEmbedding(
                            azure_api_key="offline-test", azure_api_version="2024-02-01",
                            resource_name="offline-test", embedding_model_name="test-model",
                            embedding_dims=dimensions,
                            client=AzureOpenAI(http_client=sync_http, **settings),
                            async_client=AsyncAzureOpenAI(http_client=async_http, **settings),
                        )
                    if asynchronous:
                        return await embedding.async_get_embeddings(texts)
                    return embedding.get_embeddings(texts)

        try:
            return asyncio.run(run())
        finally:
            assert len(requests) == 1
            assert records == original_records
            assert texts == original_texts

    call.provider = provider
    return call


@pytest.mark.parametrize("indices", [(0, 1, 2), (2, 0, 1), (2, 1, 0)])
@pytest.mark.parametrize("dimensions", [None, 2])
def test_vectors_follow_input_positions(invoke, indices, dimensions):
    vectors = [[0.25, 0.5], [1.25, 1.5], [2.25, 2.5]]
    records = [record(index, vectors[index]) for index in indices]
    # Repeated input text must not collapse distinct positional records.
    assert invoke(records, ["same", "different", "same"], dimensions) == vectors


INVALID = [
    pytest.param([], id="empty-response"),
    pytest.param([record(0)], id="missing-record"),
    pytest.param([record(0), record(1), record(2)], id="extra-record"),
    pytest.param([record(0), record(0)], id="duplicate-index"),
    pytest.param([record(0), record(-1)], id="negative-index"),
    pytest.param([record(0), record(2)], id="out-of-range-index"),
    pytest.param([record(0), record(0.5)], id="fractional-index"),
    pytest.param([record(0), record(True)], id="boolean-index"),
    pytest.param([record(0), record("1")], id="string-index"),
    pytest.param([record(0), record(None)], id="null-index"),
    pytest.param([record(0), {"object": "embedding", "embedding": [1.25, 1.5]}],
                 id="absent-index"),
]


@pytest.mark.parametrize("records", INVALID)
def test_invalid_mapping_fails_before_returning_vectors(invoke, records):
    expected_type = ValueError if invoke.provider == "openai" else Exception
    with pytest.raises(expected_type, match="Invalid embedding response"):
        invoke(records, ["first", "second"])


def test_sdk_decoded_base64_vectors_are_reordered(invoke):
    vectors = [[0.25, 0.5], [1.25, 1.5]]
    records = [record(index, base64.b64encode(struct.pack("ff", *vectors[index])).decode())
               for index in [1, 0]]
    assert invoke(records, ["first", "second"]) == vectors


def test_single_input_is_unchanged(invoke):
    assert invoke([record(0)], ["only"]) == [[0.25, 0.5]]


def test_bad_request_error_contract_is_preserved(invoke):
    expected_type = ValueError if invoke.provider == "openai" else Exception
    with pytest.raises(expected_type, match="invalid input"):
        invoke([], ["text"], status=400)
