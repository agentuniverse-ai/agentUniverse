"""Verify Gemini configuration through the real SDK's request conversion."""

import asyncio
import json

import pytest

from agentuniverse.agent.action.knowledge.embedding.gemini_embedding import GeminiEmbedding
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


@pytest.fixture
def sdk(monkeypatch):
    genai = pytest.importorskip("google.genai")
    client = genai.Client(api_key="offline-key", vertexai=False)
    requests = []

    def request(method, path, body, *args, **kwargs):
        # The actual SDK has converted EmbedContentConfig and each batch item.
        # Stop at its HTTP boundary; no network or credentials are needed.
        body = json.loads(json.dumps(body))
        requests.append((method, path, body))
        return {
            "embeddings": [
                {"values": [float(index + 1)] * item.get("outputDimensionality", 768)}
                for index, item in enumerate(body["requests"])
            ]
        }

    monkeypatch.setattr(client._api_client, "request", request)
    return client, requests


def configured(client, dimensions):
    config = Configer()
    config.value = {
        "name": "offline",
        "description": "offline embedding test",
        "embedding_model_name": "gemini-embedding-001",
        "embedding_dims": dimensions,
    }
    model = GeminiEmbedding(client=client, gemini_api_key=None)
    return model.initialize_by_component_configer(ComponentConfiger().load_by_configer(config))


@pytest.mark.parametrize("dimensions", [None, 256])
@pytest.mark.parametrize("role", [None, "query", "document"])
@pytest.mark.parametrize("asynchronous", [False, True])
def test_direct_requests_preserve_config_and_batch_order(sdk, dimensions, role, asynchronous):
    client, requests = sdk
    model = configured(client, dimensions)
    kwargs = {} if role is None else {"text_type": role}
    if asynchronous:
        vectors = asyncio.run(model.async_get_embeddings(["first", "second"], **kwargs))
    else:
        vectors = model.get_embeddings(["first", "second"], **kwargs)
    assert len(requests) == 1
    method, path, body = requests[0]
    assert method.lower() == "post"
    assert path == "models/gemini-embedding-001:batchEmbedContents"
    assert [item["content"]["parts"][0]["text"] for item in body["requests"]] == ["first", "second"]
    for item in body["requests"]:
        assert item.get("outputDimensionality") == dimensions
        assert "taskType" not in item
        if dimensions is None:
            assert "outputDimensionality" not in item
    assert vectors == [[1.0] * (dimensions or 768), [2.0] * (dimensions or 768)]


@pytest.mark.parametrize("entrypoint", ["embed_documents", "embed_query", "aembed_documents", "aembed_query"])
def test_langchain_preserves_configured_dimensions(sdk, entrypoint):
    client, requests = sdk
    adapter = configured(client, 256).as_langchain()
    query = entrypoint.endswith("query")
    result = getattr(adapter, entrypoint)("question" if query else ["first", "second"])
    if entrypoint.startswith("a"):
        result = asyncio.run(result)
    if query:
        assert result == [1.0] * 256
    else:
        assert result == [[1.0] * 256, [2.0] * 256]
    assert len(requests) == 1
    for item in requests[0][2]["requests"]:
        assert item["outputDimensionality"] == 256
        assert "taskType" not in item


def test_unrecognized_role_does_not_change_default_request(sdk):
    client, requests = sdk
    model = configured(client, None)
    model.get_embeddings(["first"], text_type="custom")
    assert "taskType" not in requests[0][2]["requests"][0]


def test_default_model_and_unconfigured_custom_client_remain_compatible():
    class Models:
        def embed_content(self, *, model, contents):
            from types import SimpleNamespace
            assert model == "text-embedding-004"
            assert contents == ["first"]
            return SimpleNamespace(embeddings=[SimpleNamespace(values=[1.0])])

    from types import SimpleNamespace
    model = GeminiEmbedding(client=SimpleNamespace(models=Models()))
    assert model.get_embeddings(["first"]) == [[1.0]]


@pytest.mark.parametrize("model_name", ["embedding-001", "models/embedding-001"])
@pytest.mark.parametrize("entrypoint", ["direct", "embed_query", "embed_documents"])
def test_legacy_model_omits_unsupported_task_type(sdk, model_name, entrypoint):
    client, requests = sdk
    model = GeminiEmbedding(client=client, embedding_model_name=model_name)
    if entrypoint == "direct":
        model.get_embeddings(["first"], text_type="query")
    elif entrypoint == "embed_query":
        model.as_langchain().embed_query("first")
    else:
        model.as_langchain().embed_documents(["first"])
    item = requests[0][2]["requests"][0]
    assert item["model"] == "models/embedding-001"
    assert "taskType" not in item
    assert "outputDimensionality" not in item


def test_explicit_dimensions_are_not_silently_ignored_on_legacy_model(sdk):
    client, requests = sdk
    model = GeminiEmbedding(client=client, embedding_model_name="embedding-001", embedding_dims=256)
    # The remote model, not AU, validates whether requested dimensions are supported.
    model.get_embeddings(["first"])
    assert requests[0][2]["requests"][0]["outputDimensionality"] == 256


def test_provider_error_is_not_replaced_by_a_default_dimension_retry(sdk, monkeypatch):
    client, _ = sdk
    attempts = []

    def request(*args, **kwargs):
        attempts.append(args)
        raise RuntimeError("unsupported dimensions")

    monkeypatch.setattr(client._api_client, "request", request)
    with pytest.raises(ValueError, match="unsupported dimensions"):
        configured(client, 256).get_embeddings(["first"])
    assert len(attempts) == 1


@pytest.mark.parametrize("model_name", ["text-embedding-004", "gemini-embedding-001", "models/gemini-embedding-001", "gemini-embedding-2", "models/gemini-embedding-2-preview", "custom-model"])
def test_dimensions_do_not_rewrite_model_or_add_task_type(sdk, model_name):
    client, requests = sdk
    model = GeminiEmbedding(client=client, embedding_model_name=model_name, embedding_dims=256)
    model.get_embeddings(["first"], text_type="query")
    item = requests[0][2]["requests"][0]
    assert item["model"] == "models/" + model_name.removeprefix("models/")
    assert item["outputDimensionality"] == 256
    assert "taskType" not in item
