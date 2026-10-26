"""Offline request-level regressions for the pinned LangChain Azure adapter."""

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
import tiktoken

from agentuniverse.agent.action.knowledge.embedding.azureopenai_embedding import (
    AzureOpenAIEmbedding,
)


@pytest.fixture
def requests_sent(monkeypatch):
    """Intercept HTTP only; keep real LangChain validators and OpenAI clients."""
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "OPENAI_API_BASE",
        "OPENAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_AD_TOKEN",
        "OPENAI_API_VERSION",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("OPENAI_API_VERSION", "1999-01-01")
    requests = []

    def send(client, request, **kwargs):
        requests.append((str(request.url), json.loads(request.content)))
        return httpx.Response(
            200,
            request=request,
            json={
                "data": [{"embedding": [1.0, 0.0], "index": 0, "object": "embedding"}],
                "object": "list",
                "model": "test",
                "usage": {"prompt_tokens": 1, "total_tokens": 1},
            },
        )

    async def async_send(client, request, **kwargs):
        return send(client, request, **kwargs)

    # Avoid tokenizer downloads, but preserve the real adapter's tokenization path.
    encoding = SimpleNamespace(encode=lambda text, **kwargs: [104, 105])
    monkeypatch.setattr(tiktoken, "encoding_for_model", lambda model: encoding)
    monkeypatch.setattr(httpx.Client, "send", send)
    monkeypatch.setattr(httpx.AsyncClient, "send", async_send)
    return requests


@pytest.mark.parametrize("model", ["custom-deployment", "text-embedding-ada-002"])
@pytest.mark.parametrize("dimensions", [None, 2])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_langchain_preserves_azure_request_configuration(requests_sent, dimensions, asynchronous, model):
    """A custom deployment, API version and dimensions survive conversion."""
    embedding = AzureOpenAIEmbedding(
        azure_api_key="offline-test-key",
        resource_name="offline-resource",
        azure_api_version="2024-02-01",
        embedding_model_name=model,
        embedding_dims=dimensions,
    )
    native = asyncio.run(embedding.async_get_embeddings(["hi"])) if asynchronous else embedding.get_embeddings(["hi"])
    adapter = embedding.as_langchain()
    converted = asyncio.run(adapter.aembed_documents(["hi"])) if asynchronous else adapter.embed_documents(["hi"])
    assert native == converted == [[1.0, 0.0]]
    assert len(requests_sent) == 2
    native_url, native_body = requests_sent[0]
    converted_url, converted_body = requests_sent[1]
    assert converted_url == native_url
    assert f"/deployments/{model}/embeddings" in converted_url
    assert "api-version=2024-02-01" in converted_url
    assert converted_body["model"] == native_body["model"] == model
    assert converted_body.get("dimensions") == native_body.get("dimensions")
    assert ("dimensions" in converted_body) == (dimensions is not None)
    assert adapter.model == adapter.deployment == model
    assert adapter.openai_api_version == "2024-02-01"


def test_unconfigured_model_retains_langchain_default(requests_sent):
    """Do not introduce validation errors for historically optional models."""
    embedding = AzureOpenAIEmbedding(
        azure_api_key="offline-test-key",
        resource_name="offline-resource",
        azure_api_version="2024-02-01",
    )
    adapter = embedding.as_langchain()
    assert adapter.model == "text-embedding-ada-002"
    assert adapter.deployment is None
    assert adapter.model_kwargs == {}
    assert adapter.openai_api_version == embedding.azure_api_version
    assert requests_sent == []
