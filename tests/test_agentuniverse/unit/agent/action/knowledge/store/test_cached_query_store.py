import asyncio
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import Field

import agentuniverse.agent.action.knowledge.store.cached_query_store as module
from agentuniverse.agent.action.knowledge.store.cached_query_store import CachedQueryStore, _encoded
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager


class CountingStore(Store):
    calls: int = 0
    async_calls: int = 0
    writes: int = 0
    fail: bool = False
    docs: list = Field(default_factory=lambda: [Document(id="one", text="alpha", metadata={"nested": [1]})])

    def query(self, query, **kwargs):
        self.calls += 1
        query.keywords.add("provider-mutated")
        if self.fail:
            raise RuntimeError("backend unavailable")
        return self.docs

    async def async_query(self, query, **kwargs):
        self.async_calls += 1
        await asyncio.sleep(0)
        return self.docs

    def insert_document(self, documents, **kwargs):
        self.writes += 1
        if self.fail:
            raise RuntimeError("partial write")
        self.docs = documents
        return "written"

    upsert_document = insert_document
    update_document = insert_document

    def delete_document(self, document_id, **kwargs):
        self.writes += 1
        self.docs = [doc for doc in self.docs if doc.id != document_id]

    async def async_insert_document(self, documents, **kwargs):
        return self.insert_document(documents, **kwargs)

    async_upsert_document = async_insert_document
    async_update_document = async_insert_document

    async def async_delete_document(self, document_id, **kwargs):
        return self.delete_document(document_id, **kwargs)


@pytest.fixture
def registered():
    manager = StoreManager()
    previous_pool = dict(manager._instance_obj_map)
    apps = ApplicationConfigManager()
    try:
        previous_app = apps.app_configer
    except ValueError:
        previous_app = None
    config = Configer()
    config.value = {"BASE_INFO": {"appname": "cache-tests"}}
    apps.app_configer = AppConfiger().load_by_configer(config)
    manager._instance_obj_map.clear()
    backend = CountingStore(name="underlying_store")
    manager.register(backend.get_instance_code(), backend)
    cached = CachedQueryStore(name="cache", backend_store="underlying_store", cache_revision="v1", enabled=True)
    try:
        yield backend, cached, manager
    finally:
        manager._instance_obj_map.clear()
        manager._instance_obj_map.update(previous_pool)
        apps.app_configer = previous_app


def test_exact_hits_do_not_share_query_or_document_objects(registered):
    backend, cache, _ = registered
    query = Query(query_str="alpha")
    first = cache.query(query)
    first[0].metadata["nested"].append(2)
    first[0].text = "changed"
    second = cache.query(query)
    assert second[0].text == "alpha" and second[0].metadata == {"nested": [1]}
    assert backend.docs[0].metadata == {"nested": [1]}
    assert query.keywords == set()
    assert backend.calls == 1 and cache.cache_info()["hits"] == 1
    assert cache.create_copy() is cache  # framework store lifecycle intentionally shares cache.


@pytest.mark.parametrize("changes", [
    {"query_str": "beta"}, {"similarity_top_k": 4}, {"keywords": {"beta"}},
    {"query_text_bundles": ["beta"]}, {"embeddings": [[1.0, 2.0]]},
    {"ext_info": {"tenant": "other"}},
])
def test_every_query_dimension_is_keyed(registered, changes):
    backend, cache, _ = registered
    cache.query(Query(query_str="alpha"))
    cache.query(Query(query_str="alpha").model_copy(update=changes))
    assert backend.calls == 2


def test_typed_options_never_collide_and_unsupported_bypass(registered):
    backend, cache, _ = registered
    values = [True, 1, 1.0, [1], (1,), {1}, frozenset({1}), {"1": 1}]
    for value in values:
        cache.query(Query(query_str="alpha"), filters=value)
    assert backend.calls == len(values)
    assert len({_encoded(value) for value in values}) == len(values)
    for _ in range(2):
        cache.query(Query(), filters={1: "unsupported integer key"})
        cache.query(Query(), filters=float("inf"))
    assert backend.calls == len(values) + 4


def test_ttl_is_absolute_and_clock_monotonic(registered, monkeypatch):
    backend, cache, _ = registered
    now = [10.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: now[0])
    cache.ttl_seconds = 5.0
    cache.query(Query())
    now[0] = 14.0
    cache.query(Query())
    now[0] = 15.0
    cache.query(Query())
    assert backend.calls == 2


def test_revision_backend_replacement_disable_and_clear(registered):
    backend, cache, manager = registered
    cache.query(Query())
    cache.cache_revision = "v2"
    cache.query(Query())
    cache.clear_cache()
    cache.query(Query())
    cache.enabled = False
    cache.query(Query())
    cache.query(Query())
    assert backend.calls == 5
    cache.enabled = True
    replacement = CountingStore(name="underlying_store", docs=[Document(text="replacement")])
    manager.unregister(replacement.get_instance_code())
    manager.register(replacement.get_instance_code(), replacement)
    assert cache.query(Query())[0].text == "replacement"
    assert replacement.calls == 1


def test_empty_results_cached_failures_not_cached(registered):
    backend, cache, _ = registered
    backend.docs = []
    assert cache.query(Query()) == cache.query(Query()) == []
    assert backend.calls == 1
    cache.clear_cache()
    backend.fail = True
    for _ in range(2):
        with pytest.raises(RuntimeError):
            cache.query(Query())
    assert backend.calls == 3 and cache.cache_info()["entries"] == 0


@pytest.mark.parametrize("method", ["insert_document", "upsert_document", "update_document", "delete_document"])
def test_every_write_invalidates(registered, method):
    backend, cache, _ = registered
    cache.query(Query())
    value = "one" if method == "delete_document" else [Document(text="new")]
    getattr(cache, method)(value)
    assert cache.query(Query()) == backend.docs
    assert backend.calls == 2


def test_failed_write_also_invalidates(registered):
    backend, cache, _ = registered
    cache.query(Query())
    backend.fail = True
    with pytest.raises(RuntimeError):
        cache.insert_document([])
    assert cache.cache_info()["entries"] == cache.cache_info()["active_writes"] == 0
    backend.fail = False
    cache.query(Query())
    assert backend.calls == 2


def test_lru_eviction_and_byte_budgets(registered):
    backend, cache, _ = registered
    cache.max_entries = 2
    for key in ("a", "b", "a", "c", "b"):
        cache.query(Query(query_str=key))
    assert backend.calls == 4 and cache.cache_info()["entries"] == 2
    cache.max_cache_bytes = 1
    cache.query(Query())
    cache.query(Query())
    assert cache.cache_info()["entries"] == cache.cache_info()["encoded_bytes"] == 0


@pytest.mark.parametrize("field,value", [("max_entry_bytes", 1), ("max_key_bytes", 1), ("max_documents", 1)])
def test_oversized_results_delegate_without_truncation(registered, field, value):
    backend, cache, _ = registered
    backend.docs.append(Document(text="second"))
    setattr(cache, field, value)
    for _ in range(2):
        assert len(cache.query(Query())) == 2
    assert backend.calls == 2 and cache.cache_info()["entries"] == 0


def test_inflight_clear_cannot_repopulate_old_result(registered):
    backend, cache, _ = registered
    started, release = threading.Event(), threading.Event()
    original = CountingStore.query
    def blocked(self, query, **kwargs):
        result = original(self, query, **kwargs)
        started.set()
        assert release.wait(5)
        return result
    with patch.object(CountingStore, "query", blocked), ThreadPoolExecutor(1) as executor:
        pending = executor.submit(cache.query, Query())
        try:
            assert started.wait(5)
            cache.clear_cache()
        finally:
            release.set()
        assert pending.result(timeout=5)[0].text == "alpha"
    assert cache.cache_info()["entries"] == 0
    cache.query(Query())
    assert backend.calls == 2


def test_async_queries_and_all_write_delegates(registered):
    backend, cache, _ = registered
    async def scenario():
        for method in ("async_insert_document", "async_upsert_document", "async_update_document", "async_delete_document"):
            await cache.async_query(Query())
            await cache.async_query(Query())
            value = "one" if method == "async_delete_document" else [Document(id="one", text=method)]
            await getattr(cache, method)(value)
        assert await cache.async_query(Query()) == []
    asyncio.run(scenario())
    assert backend.async_calls == 5 and backend.writes == 4
    cache.query(Query())
    assert backend.calls == 1  # synchronous and asynchronous results are separate.


def test_async_cancel_does_not_cache_and_write_cancel_invalidates(registered):
    _, cache, _ = registered
    async def scenario():
        started = asyncio.Event()
        async def blocked(*args, **kwargs):
            started.set()
            await asyncio.Event().wait()
        for method in ("async_query", "async_insert_document"):
            cache.query(Query())
            with patch.object(CountingStore, method, blocked):
                value = Query() if method == "async_query" else []
                pending = asyncio.create_task(getattr(cache, method)(value))
                await asyncio.wait_for(started.wait(), 2)
                pending.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await pending
                started.clear()
            assert cache.cache_info()["active_writes"] == 0
        assert cache.cache_info()["entries"] == 0
    asyncio.run(scenario())


@pytest.mark.parametrize("field,value", [("ttl_seconds", float("nan")), ("max_entries", True),
    ("backend_store", ""), ("cache_revision", ""), ("enabled", 1)])
def test_mutated_options_revalidated(registered, field, value):
    _, cache, _ = registered
    cache.query(Query())
    setattr(cache, field, value)
    with pytest.raises(ValueError):
        cache.query(Query())


def test_cache_wrapper_cycle_rejected(registered):
    _, cache, manager = registered
    manager.register(cache.get_instance_code(), cache)
    cache.backend_store = "cache"
    with pytest.raises(ValueError, match="chains"):
        cache.query(Query())


def test_queries_during_write_do_not_populate_cache(registered):
    backend, cache, _ = registered
    started, release = threading.Event(), threading.Event()
    original = CountingStore.insert_document
    def blocked(self, documents, **kwargs):
        started.set()
        assert release.wait(5)
        return original(self, documents, **kwargs)
    cache.query(Query())
    with patch.object(CountingStore, "insert_document", blocked), ThreadPoolExecutor(1) as executor:
        pending = executor.submit(cache.insert_document, [Document(text="new")])
        try:
            assert started.wait(5)
            assert cache.query(Query())[0].text == "alpha"
            assert cache.cache_info()["entries"] == 0
        finally:
            release.set()
        assert pending.result(timeout=5) == "written"
    assert cache.query(Query())[0].text == "new"
    assert backend.calls == 3


def test_serialized_byte_budget_evicts_even_below_entry_count(registered):
    _, cache, _ = registered
    cache.query(Query(query_str="a"))
    size = cache.cache_info()["encoded_bytes"]
    cache.max_cache_bytes = size + 1
    cache.query(Query(query_str="b"))
    cache.query(Query(query_str="c"))
    assert cache.cache_info()["entries"] == 1
    assert cache.cache_info()["encoded_bytes"] <= size + 1


def test_real_yaml_knowledge_sqlite_pipeline(tmp_path, registered):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader

    class CountedSQLite(SQLiteStore):
        query_calls: int = 0
        def query(self, query, **kwargs):
            self.query_calls += 1
            return super().query(query, **kwargs)

    _, _, manager = registered
    managers = [DocProcessorManager(), RagRouterManager(), ReaderManager()]
    pools = [dict(item._instance_obj_map) for item in managers]
    prior_post_fork = list(POST_FORK_QUEUE)
    store = knowledge = None
    try:
        for item in managers:
            item._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        # Match deployment: copy the opt-in example to an application's .yaml.
        config_path = tmp_path / "cached_query_store.yaml"
        shutil.copyfile(root / "agentuniverse/agent/action/knowledge/store/cached_query_store.yaml.example", config_path)
        config = ComponentConfiger().load_by_configer(Configer(str(config_path)).load())
        assert config.enabled is False
        config.enabled = True
        config.backend_store = "actual_sqlite"
        cached = CachedQueryStore().initialize_by_component_configer(config)
        store = CountedSQLite(name="actual_sqlite", db_path=str(tmp_path / "actual.db"), keyword_extractor="keywords")
        store._new_client()
        manager.register(store.get_instance_code(), store)
        manager.register(cached.get_instance_code(), cached)
        for item, component in zip(managers, [JiebaKeywordExtractor(name="keywords", top_k=100), BaseRouter(name="base_router"), TxtReader(name="text")]):
            item.register(component.get_instance_code(), component)
        knowledge = Knowledge(stores=["cached_query_store"], readers={"txt": "text"})
        path = tmp_path / "source.txt"
        path.write_text("alpha manual", encoding="utf-8")
        knowledge.insert_knowledge(source_path=str(path))
        store.conn.close()
        store._new_client()
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            results = [knowledge.query_knowledge(query_str="alpha", keywords={"alpha"}) for _ in range(3)]
            assert store.query_calls == 1
            assert all(len(result) == 1 and result[0].text == "alpha manual" for result in results)
            results[0][0].metadata["caller_only"] = True
            assert "caller_only" not in knowledge.query_knowledge(query_str="alpha", keywords={"alpha"})[0].metadata
            cached.upsert_document([Document(id=results[0][0].id, text="beta manual")])
            assert knowledge.query_knowledge(query_str="alpha", keywords={"alpha"}) == []
            updated = knowledge.query_knowledge(query_str="beta", keywords={"beta"})
            assert len(updated) == 1 and updated[0].text == "beta manual"
            cached.delete_document(updated[0].id)
            assert knowledge.query_knowledge(query_str="beta", keywords={"beta"}) == []
        assert cached.cache_info()["hits"] >= 3
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if store is not None:
            store.conn.close()
        for item, pool in zip(managers, pools):
            item._instance_obj_map.clear()
            item._instance_obj_map.update(pool)
        POST_FORK_QUEUE[:] = prior_post_fork


def test_startup_hook_discards_inherited_cache_and_lock(registered):
    backend, cache, _ = registered
    cache.query(Query())
    previous_lock = cache._lock
    cache._new_client()
    assert cache._lock is not previous_lock
    assert cache.cache_info()["entries"] == 0
    cache.query(Query())
    assert backend.calls == 2


def test_backend_switch_between_resolve_and_lookup_never_crosses_results(registered):
    _, cache, manager = registered
    resolved, proceed = threading.Event(), threading.Event()
    original = CachedQueryStore._resolve
    def delayed(self):
        result = original(self)
        if threading.current_thread().name.startswith("old-query"):
            resolved.set()
            assert proceed.wait(5)
        return result
    replacement = CountingStore(name="replacement", docs=[Document(text="new backend")])
    manager.register(replacement.get_instance_code(), replacement)
    with patch.object(CachedQueryStore, "_resolve", delayed), ThreadPoolExecutor(1, thread_name_prefix="old-query") as executor:
        pending = executor.submit(cache.query, Query())
        try:
            assert resolved.wait(5)
            cache.backend_store = "replacement"
            assert cache.query(Query())[0].text == "new backend"
        finally:
            proceed.set()
        assert pending.result(timeout=5)[0].text == "alpha"
    assert cache.query(Query())[0].text == "new backend"
    assert replacement.calls == 1
