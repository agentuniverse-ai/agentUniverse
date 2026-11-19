"""Offline Bedrock embedding tests: no SDK, credentials, or network required."""

import asyncio
import json
import socket
import sys
from io import BytesIO
from unittest.mock import Mock

import pytest

from agentuniverse.agent.action.knowledge.embedding.aws_bedrock_embedding import AWSBedrockEmbedding


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    blocked = Mock(side_effect=AssertionError("Offline tests must not open network connections"))
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)


@pytest.fixture
def embedding(monkeypatch):
    monkeypatch.setitem(sys.modules, "boto3", None)
    monkeypatch.setitem(sys.modules, "botocore", None)
    return AWSBedrockEmbedding(
        embedding_model_name="amazon.titan-embed-text-v1",
        aws_access_key_id=None,
        aws_secret_access_key=None,
        client=Mock(),
    )


@pytest.mark.parametrize(
    ("model", "dimensions", "response"),
    [
        ("amazon.titan-embed-text-v1", None, {"embedding": [0.1] * 1536}),
        ("amazon.titan-embed-text-v2", 1024, {"embedding": [0.1] * 1024}),
        ("cohere.embed-multilingual-v3", None, {"embeddings": [[0.2] * 1024]}),
    ],
)
def test_model_requests(embedding, model, dimensions, response):
    embedding.embedding_model_name = model
    embedding.dimensions = dimensions
    embedding.client.invoke_model.return_value = {"body": BytesIO(json.dumps(response).encode())}

    result = embedding.get_embeddings(["hello"], input_type="search_query")

    assert result == ([response["embedding"]] if "embedding" in response else response["embeddings"])
    request = embedding.client.invoke_model.call_args.kwargs
    assert request["modelId"] == model
    assert request["contentType"] == request["accept"] == "application/json"
    expected = {"texts": ["hello"], "input_type": "search_query"}
    if "titan" in model:
        expected = {"inputText": "hello", "normalize": True}
        if dimensions:
            expected["dimensions"] = dimensions
    assert json.loads(request["body"]) == expected


@pytest.mark.parametrize("use_async", [False, True])
def test_multiple_texts(embedding, use_async):
    embedding.client.invoke_model.side_effect = [
        {"body": BytesIO(b'{"embedding": [0.1]}')},
        {"body": BytesIO(b'{"embedding": [0.2]}')},
    ]
    texts = ["first", "second"]
    result = asyncio.run(embedding.async_get_embeddings(texts)) if use_async else embedding.get_embeddings(texts)
    assert result == [[0.1], [0.2]]
    assert [
        json.loads(call.kwargs["body"])["inputText"] for call in embedding.client.invoke_model.call_args_list
    ] == texts


def test_normalize_disabled(embedding):
    embedding.normalize = False
    embedding.client.invoke_model.return_value = {"body": BytesIO(b'{"embedding": [0.1]}')}
    embedding.get_embeddings(["test"])
    assert "normalize" not in json.loads(embedding.client.invoke_model.call_args.kwargs["body"])


def test_cohere_default_input_type(embedding):
    embedding.embedding_model_name = "cohere.embed-english-v3"
    embedding.client.invoke_model.return_value = {"body": BytesIO(b'{"embeddings": [[0.2]]}')}
    assert embedding.get_embeddings(["test"]) == [[0.2]]
    assert json.loads(embedding.client.invoke_model.call_args.kwargs["body"])["input_type"] == "search_document"


def test_empty_input(embedding):
    assert embedding.get_embeddings([]) == []
    embedding.client.invoke_model.assert_not_called()


def test_missing_model(embedding):
    embedding.embedding_model_name = None
    with pytest.raises(ValueError, match="embedding_model_name"):
        embedding.get_embeddings(["test"])
    embedding.client.invoke_model.assert_not_called()


def test_unsupported_model(embedding):
    embedding.embedding_model_name = "unsupported.model"
    with pytest.raises(Exception, match="Unsupported model"):
        embedding.get_embeddings(["test"])
    embedding.client.invoke_model.assert_not_called()


def test_api_error(embedding):
    embedding.client.invoke_model.side_effect = RuntimeError("service unavailable")
    with pytest.raises(Exception, match="Failed to get embedding for text: service unavailable"):
        embedding.get_embeddings(["test"])


def test_missing_embedding(embedding):
    embedding.client.invoke_model.return_value = {"body": BytesIO(b"{}")}
    with pytest.raises(Exception, match="Failed to extract embedding"):
        embedding.get_embeddings(["test"])


def test_langchain_adapter_arguments(embedding, monkeypatch):
    from langchain_community import embeddings

    adapter = Mock()
    monkeypatch.setattr(embeddings, "BedrockEmbeddings", adapter)
    assert embedding.as_langchain() is adapter.return_value
    adapter.assert_called_once_with(
        client=embedding.client, model_id=embedding.embedding_model_name, region_name=embedding.aws_region
    )
