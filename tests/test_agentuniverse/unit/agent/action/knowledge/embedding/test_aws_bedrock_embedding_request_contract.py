"""Offline coverage of model-specific Bedrock embedding request bodies."""

import asyncio
import json
import socket
from io import BytesIO

import pytest

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    def fail_connect(*args, **kwargs):
        pytest.fail("Bedrock request-contract tests must not use the network")

    monkeypatch.setattr(socket.socket, "connect", fail_connect)
    monkeypatch.setattr(socket, "create_connection", fail_connect)


class RecordingClient:
    def __init__(self):
        self.calls = []

    def invoke_model(self, **kwargs):
        self.calls.append(kwargs)
        vector = [float(len(self.calls)), 0.5]
        response = {"embeddings": [vector]} if "cohere" in kwargs["modelId"] else {"embedding": vector}
        return {"body": BytesIO(json.dumps(response).encode())}


def embed(model, texts=None, call_kwargs=None, **options):
    client = RecordingClient()
    component = AWSBedrockEmbedding(client=client, embedding_model_name=model, **options)
    vectors = component.get_embeddings(texts or ["sample"], **(call_kwargs or {}))
    return vectors, client.calls


@pytest.mark.parametrize("normalize", [True, False])
def test_titan_v1_uses_only_input_text(normalize):
    _, calls = embed("amazon.titan-embed-text-v1", normalize=normalize, dimensions=512)
    assert json.loads(calls[0]["body"]) == {"inputText": "sample"}


@pytest.mark.parametrize("normalize", [True, False])
@pytest.mark.parametrize("dimensions", [None, 256, 512, 1024])
def test_titan_v2_preserves_normalize_and_dimensions(normalize, dimensions):
    _, calls = embed("amazon.titan-embed-text-v2:0", normalize=normalize, dimensions=dimensions)
    expected = {"inputText": "sample", "normalize": normalize}
    if dimensions is not None:
        expected["dimensions"] = dimensions
    assert json.loads(calls[0]["body"]) == expected


@pytest.mark.parametrize("model", ["cohere.embed-english-v3", "cohere.embed-multilingual-v3"])
@pytest.mark.parametrize(
    ("options", "expected"),
    [
        ({}, "search_document"),
        ({"text_type": "document"}, "search_document"),
        ({"text_type": "query"}, "search_query"),
        ({"text_type": "query", "input_type": "classification"}, "classification"),
        ({"text_type": "document", "input_type": "search_query"}, "search_query"),
    ],
)
def test_cohere_respects_framework_text_type_and_explicit_override(model, options, expected):
    _, calls = embed(model, call_kwargs=options)
    assert json.loads(calls[0]["body"]) == {"texts": ["sample"], "input_type": expected}


def test_batch_preserves_order_and_request_envelope():
    vectors, calls = embed("cohere.embed-english-v3", texts=["first", "second"], call_kwargs={"text_type": "query"})
    assert vectors == [[1.0, 0.5], [2.0, 0.5]]
    for call, text in zip(calls, ["first", "second"], strict=True):
        assert call["modelId"] == "cohere.embed-english-v3"
        assert call["contentType"] == "application/json"
        assert call["accept"] == "application/json"
        assert json.loads(call["body"]) == {"texts": [text], "input_type": "search_query"}


@pytest.mark.parametrize(
    ("model", "options", "kwargs", "expected"),
    [
        ("amazon.titan-embed-text-v1", {}, {}, {"inputText": "sample"}),
        ("amazon.titan-embed-text-v2:0", {"normalize": False}, {}, {"inputText": "sample", "normalize": False}),
        ("cohere.embed-english-v3", {}, {"text_type": "query"}, {"texts": ["sample"], "input_type": "search_query"}),
    ],
)
def test_async_path_uses_same_request_contract(model, options, kwargs, expected):
    client = RecordingClient()
    component = AWSBedrockEmbedding(client=client, embedding_model_name=model, **options)
    assert asyncio.run(component.async_get_embeddings(["sample"], **kwargs)) == [[1.0, 0.5]]
    assert json.loads(client.calls[0]["body"]) == expected


def test_real_sdk_accepts_request_envelope_without_network():
    boto3 = pytest.importorskip("boto3")
    from botocore.response import StreamingBody
    from botocore.stub import Stubber

    client = boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id="synthetic",
        aws_secret_access_key="synthetic",  # noqa: S106 - offline Stubber credentials
    )
    body = json.dumps({"embedding": [0.1, 0.2]}).encode()
    with Stubber(client) as stubber:
        stubber.add_response(
            "invoke_model",
            {"body": StreamingBody(BytesIO(body), len(body)), "contentType": "application/json"},
            {
                "modelId": "amazon.titan-embed-text-v2:0",
                "body": json.dumps({"inputText": "sample", "normalize": False, "dimensions": 512}),
                "contentType": "application/json",
                "accept": "application/json",
            },
        )
        component = AWSBedrockEmbedding(
            client=client, embedding_model_name="amazon.titan-embed-text-v2:0", normalize=False, dimensions=512
        )
        assert component.get_embeddings(["sample"]) == [[0.1, 0.2]]
        stubber.assert_no_pending_responses()
