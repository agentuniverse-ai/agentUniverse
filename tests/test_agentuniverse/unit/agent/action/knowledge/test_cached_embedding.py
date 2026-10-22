"""Cache behavior with a deterministic provider, not a live embedding model."""
import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from pydantic import PrivateAttr

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.embedding.cached_embedding import CachedEmbedding


class Provider(Embedding):
    embedding_model_name: str = "model-v1"
    embedding_dims: int = 2
    _calls: list = PrivateAttr(default_factory=list)
    _result: object = PrivateAttr(default=None)

    def get_embeddings(self, texts, **kwargs):
        self._calls.append((list(texts), dict(kwargs)))
        if isinstance(self._result, Exception):
            raise self._result
        return self._result if self._result is not None else [[len(text), 1.0] for text in texts]

    async def async_get_embeddings(self, texts, **kwargs):
        await asyncio.sleep(0)
        return self.get_embeddings(texts, **kwargs)


@pytest.fixture
def setup():
    provider = Provider()
    with patch("agentuniverse.agent.action.knowledge.embedding.cached_embedding.EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = provider
        yield CachedEmbedding(backend_name="provider", cache_version="v1"), provider


def test_dedup_order_copies_and_partial_hit(setup):
    cache, provider = setup
    result = cache.get_embeddings(["aa", "b", "aa"])
    assert result == [[2, 1], [1, 1], [2, 1]]
    result[0][0] = 999
    assert result[2][0] == 2
    assert cache.get_embeddings(["aa", "ccc"]) == [[2, 1], [3, 1]]
    assert [call[0] for call in provider._calls] == [["aa", "b"], ["ccc"]]


def test_nested_option_types_do_not_collide(setup):
    cache, provider = setup
    cache.get_embeddings(["a"], options={"shape": [1, 2]})
    cache.get_embeddings(["a"], options={"shape": (1, 2)})
    assert len(provider._calls) == 2


def test_nested_non_string_keys_rejected_before_provider(setup):
    cache, provider = setup
    with pytest.raises(ValueError, match="string"):
        cache.get_embeddings(["a"], options={1: "value"})
    assert not provider._calls


def test_provider_option_mutation_does_not_change_callers_input(setup):
    cache, provider = setup
    options = {"nested": [1]}
    original = Provider.get_embeddings
    def mutate(self, texts, **kwargs):
        kwargs["options"]["nested"].append(2)
        return original(self, texts, **kwargs)
    with patch.object(Provider, "get_embeddings", mutate):
        cache.get_embeddings(["a"], options=options)
    assert options == {"nested": [1]}


def test_async_call_uses_captured_options_not_later_caller_mutation(setup):
    cache, provider = setup
    async def scenario():
        started, release = asyncio.Event(), asyncio.Event()
        options = {"value": 1}
        async def wait_for_call(self, texts, **kwargs):
            started.set()
            await release.wait()
            self._calls.append((texts, kwargs))
            return [[kwargs["options"]["value"], 1.0] for _ in texts]
        with patch.object(Provider, "async_get_embeddings", wait_for_call):
            pending = asyncio.create_task(cache.async_get_embeddings(["a"], options=options))
            await asyncio.wait_for(started.wait(), 2)
            options["value"] = 9
            release.set()
            assert await pending == [[1, 1]]
        assert await cache.async_get_embeddings(["a"], options={"value": 1}) == [[1, 1]]
        assert len(provider._calls) == 1
    asyncio.run(scenario())


def test_recursive_options_fail_before_provider(setup):
    cache, provider = setup
    recursive = []
    recursive.append(recursive)
    with pytest.raises(ValueError, match="acyclic"):
        cache.get_embeddings(["a"], options=recursive)
    assert not provider._calls


def test_model_version_role_and_options_isolation(setup):
    cache, provider = setup
    cache.get_embeddings(["a"], text_type="query")
    cache.get_embeddings(["a"], text_type="document")
    cache.get_embeddings(["a"], text_type="query")
    cache.cache_version = "v2"
    cache.get_embeddings(["a"], text_type="query")
    provider.embedding_model_name = "model-v2"
    cache.get_embeddings(["a"], text_type="query")
    assert len(provider._calls) == 4


def test_lru_and_disabled_cache(setup):
    cache, provider = setup
    cache.max_entries = 2
    cache.get_embeddings(["a", "b"])
    cache.get_embeddings(["a"])
    cache.get_embeddings(["c"])
    cache.get_embeddings(["b"])
    assert len(provider._calls) == 3
    cache.max_entries = 0
    cache.get_embeddings(["b"])
    cache.get_embeddings(["b"])
    assert len(provider._calls) == 5


@pytest.mark.parametrize("result", [[], [[1]], [[1, float("nan")]], [[1, True]], [[1, 2], [1, 2]], "bad"])
def test_invalid_response_never_cached(setup, result):
    cache, provider = setup
    provider._result = result
    with pytest.raises(ValueError):
        cache.get_embeddings(["a"])
    provider._result = None
    assert cache.get_embeddings(["a"]) == [[1, 1]]
    assert len(provider._calls) == 2


def test_provider_error_retry_and_clear(setup):
    cache, provider = setup
    provider._result = RuntimeError("offline")
    with pytest.raises(RuntimeError):
        cache.get_embeddings(["a"])
    provider._result = None
    cache.get_embeddings(["a"])
    cache.clear_cache()
    cache.get_embeddings(["a"])
    assert len(provider._calls) == 3


def test_async_and_langchain_roles(setup):
    cache, provider = setup
    async def run():
        assert await cache.async_get_embeddings(["a"]) == [[1, 1]]
        assert await cache.async_get_embeddings(["a"]) == [[1, 1]]
        adapter = cache.as_langchain()
        assert await adapter.aembed_query("a") == [1, 1]
        assert await adapter.aembed_documents(["a"]) == [[1, 1]]
        assert adapter.embed_query("a") == [1, 1]
    asyncio.run(run())
    assert len(provider._calls) == 3


@pytest.mark.parametrize("texts", [None, "a", [1]])
def test_bad_texts(setup, texts):
    cache, provider = setup
    with pytest.raises(ValueError):
        cache.get_embeddings(texts)
    assert not provider._calls


def test_empty_and_bad_options(setup):
    cache, provider = setup
    assert cache.get_embeddings([]) == []
    with pytest.raises(ValueError):
        cache.get_embeddings(["a"], unsupported=float("nan"))
    assert not provider._calls


def test_clear_during_request_does_not_repopulate(setup):
    cache, provider = setup
    original = Provider.get_embeddings
    def fetch(self, texts, **kwargs):
        cache.clear_cache()
        return original(self, texts, **kwargs)
    with patch.object(Provider, "get_embeddings", fetch):
        cache.get_embeddings(["a"])
    cache.get_embeddings(["a"])
    assert len(provider._calls) == 2


def test_backend_replacement_never_reuses_vectors(setup):
    cache, provider = setup
    cache.get_embeddings(["a"])
    other = Provider()
    other._result = [[9.0, 8.0]]
    with patch("agentuniverse.agent.action.knowledge.embedding.cached_embedding.EmbeddingManager") as manager:
        manager.return_value.get_instance_obj.return_value = other
        assert cache.get_embeddings(["a"]) == [[9, 8]]


def test_yaml_resolves_and_initializes(tmp_path):
    import importlib
    from pathlib import Path
    import yaml
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    root = Path(__file__).resolve().parents[6]
    path = root / "agentuniverse/agent/action/knowledge/embedding/cached_embedding.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    cls = getattr(importlib.import_module(data["metadata"]["module"]), data["metadata"]["class"])
    config = ComponentConfiger()
    for key, value in data.items():
        if key != "metadata":
            setattr(config, key, value)
    cache = cls()._initialize_by_component_configer(config)
    assert cache.cache_version == "example-v1"
    assert cache.max_entries == 1024


def test_real_openai_component_and_langchain_adapter():
    from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
    backend = OpenAIEmbedding(embedding_model_name="fixture", openai_api_key="not-a-real-key")
    cache = CachedEmbedding(backend_name="openai", cache_version="fixture-v1")
    with patch("agentuniverse.agent.action.knowledge.embedding.cached_embedding.EmbeddingManager") as manager, \
            patch("agentuniverse.agent.action.knowledge.embedding.openai_embedding.OpenAI") as sdk:
        manager.return_value.get_instance_obj.return_value = backend
        sdk.return_value.embeddings.create.return_value = SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 2.0])])
        adapter = cache.as_langchain()
        assert adapter.embed_documents(["a", "a"]) == [[1, 2], [1, 2]]
        assert adapter.embed_documents(["a"]) == [[1, 2]]
        assert sdk.return_value.embeddings.create.call_count == 1
        assert sdk.return_value.embeddings.create.call_args.kwargs == {"input": ["a"], "model": "fixture"}


def test_cancelled_async_request_not_cached(setup):
    cache, provider = setup
    async def run():
        started = asyncio.Event()
        async def wait(self, texts, **kwargs):
            started.set()
            await asyncio.Event().wait()
        with patch.object(Provider, "async_get_embeddings", wait):
            task = asyncio.create_task(cache.async_get_embeddings(["a"]))
            await started.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert await cache.async_get_embeddings(["a"]) == [[1, 1]]
    asyncio.run(run())
    assert len(provider._calls) == 1


def test_parallel_misses_and_independent_results(setup):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    cache, provider = setup
    barrier = Barrier(2)
    original = Provider.get_embeddings
    def fetch(self, texts, **kwargs):
        barrier.wait(timeout=5)
        return original(self, texts, **kwargs)
    with patch.object(Provider, "get_embeddings", fetch), ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(cache.get_embeddings, ["a"]) for _ in range(2)]
        results = [future.result(timeout=10) for future in futures]
    results[0][0][0] = 99
    assert results[1] == [[1, 1]]
    assert cache.get_embeddings(["a"]) == [[1, 1]]
    assert len(provider._calls) == 2
