from pathlib import Path
import asyncio
import shutil
from unittest.mock import patch

import pytest

from agentuniverse.agent.action.knowledge.rag_router.alias_query_router import AliasQueryRouter
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.alias_recall_store import AliasRecallStore
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.agent.action.knowledge.store.document import Document


class ControlledStore(Store):
    calls: int = 0
    writes: int = 0
    fail: bool = False

    def query(self, query, **kwargs):
        self.calls += 1
        if self.fail and self.calls == 2:
            raise RuntimeError("alias provider failure")
        return [Document(id=query.query_str, text=query.query_str, metadata={"values": [1]})]

    async def async_query(self, query, **kwargs):
        await asyncio.sleep(0)
        return self.query(query, **kwargs)

    def insert_document(self, documents, **kwargs):
        self.writes += 1
        return documents

    upsert_document = insert_document
    update_document = insert_document
    delete_document = insert_document

    async def async_insert_document(self, documents, **kwargs):
        return self.insert_document(documents, **kwargs)

    async_upsert_document = async_insert_document
    async_update_document = async_insert_document
    async_delete_document = async_insert_document


def test_sequential_async_results_and_write_passthrough():
    backend = ControlledStore()
    wrapper = AliasRecallStore(backend_store="test", planner=AliasQueryRouter(aliases={"EV": ["vehicle"]}))
    async def run():
        result = await wrapper.async_query(Query(query_str="EV"))
        assert [doc.text for doc in result] == ["EV", "vehicle"]
        for method in ("async_insert_document", "async_upsert_document", "async_update_document", "async_delete_document"):
            assert await getattr(wrapper, method)("value") == "value"
    with patch.object(AliasRecallStore, "_backend", return_value=backend):
        asyncio.run(run())
        for method in ("insert_document", "upsert_document", "update_document", "delete_document"):
            assert getattr(wrapper, method)("value") == "value"
    assert backend.calls == 2 and backend.writes == 8


@pytest.mark.parametrize("field,value", [("max_result_documents", 1), ("max_result_chars", 3)])
def test_combined_result_budget(field, value):
    wrapper = AliasRecallStore(backend_store="test", planner=AliasQueryRouter(aliases={"EV": ["vehicle"]}))
    setattr(wrapper, field, value)
    with patch.object(AliasRecallStore, "_backend", return_value=ControlledStore()):
        with pytest.raises(ValueError, match="combined"):
            wrapper.query(Query(query_str="EV"))


def test_alias_failure_propagates_instead_of_silent_partial_results():
    wrapper = AliasRecallStore(backend_store="test", planner=AliasQueryRouter(aliases={"EV": ["vehicle"]}))
    with patch.object(AliasRecallStore, "_backend", return_value=ControlledStore(fail=True)):
        with pytest.raises(RuntimeError, match="provider failure"):
            wrapper.query(Query(query_str="EV"))


def test_async_cancel_stops_additional_alias_queries():
    backend = ControlledStore()
    wrapper = AliasRecallStore(backend_store="test", planner=AliasQueryRouter(aliases={"EV": ["vehicle", "car"]}))
    async def run():
        started = asyncio.Event()
        async def block(self, query, **kwargs):
            self.calls += 1
            started.set()
            await asyncio.Event().wait()
        with patch.object(ControlledStore, "async_query", block):
            pending = asyncio.create_task(wrapper.async_query(Query(query_str="EV")))
            await asyncio.wait_for(started.wait(), 2)
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
        assert backend.calls == 1
    with patch.object(AliasRecallStore, "_backend", return_value=backend):
        asyncio.run(run())


def texts(routes):
    return [query.query_str for query, _ in routes]


def test_original_first_and_each_route_independent():
    router = AliasQueryRouter(aliases={"EV": ["electric vehicle"]})
    origin = Query(query_str="EV charging", keywords={"EV"}, embeddings=[[1.0]],
                   similarity_top_k=7, ext_info={"filter": {"tenant": "a"}})
    routes = router.rag_route(origin, ["one", "two"])
    assert texts(routes) == ["EV charging", "EV charging", "electric vehicle charging", "electric vehicle charging"]
    assert [store for _, store in routes] == ["one", "two", "one", "two"]
    assert routes[0][0].keywords == {"EV"} and routes[0][0].embeddings == [[1.0]]
    assert routes[2][0].keywords == set() and routes[2][0].embeddings == []
    assert all(query.similarity_top_k == 7 for query, _ in routes)
    routes[0][0].ext_info["filter"]["tenant"] = "changed"
    assert origin.ext_info["filter"]["tenant"] == routes[1][0].ext_info["filter"]["tenant"] == "a"
    assert origin.query_str == "EV charging" and origin.keywords == {"EV"}


def test_boundaries_case_and_literal_characters():
    router = AliasQueryRouter(aliases={"EV": ["electric vehicle"], "C++": ["cpp"]})
    assert texts(router.rag_route(Query(query_str="FEVER ev C++"), ["one"])) == ["FEVER ev C++", "FEVER ev cpp"]
    assert texts(router.rag_route(Query(query_str="EV EV"), ["one"])) == ["EV EV", "electric vehicle electric vehicle"]


def test_overlap_longest_and_no_cascade_or_cartesian_expansion():
    router = AliasQueryRouter(aliases={"New": ["N"], "New York": ["NYC"], "NYC": ["city"]}, max_variants=10)
    assert texts(router.rag_route(Query(query_str="New York NYC"), ["one"])) == ["New York NYC", "NYC NYC", "New York city"]


def test_substring_opt_in_chinese():
    original = Query(query_str="查询电动车手册")
    router = AliasQueryRouter(aliases={"电动车": ["新能源汽车"]})
    assert len(router.rag_route(original, ["one"])) == 1
    router.boundary = "substring"
    assert texts(router.rag_route(original, ["one"])) == ["查询电动车手册", "查询新能源汽车手册"]


def test_alias_order_duplicate_elimination_and_budget():
    router = AliasQueryRouter(aliases={"EV": ["EV", "car", "car", "vehicle", "automobile"]}, max_variants=3)
    assert texts(router.rag_route(Query(query_str="EV"), ["one"])) == ["EV", "car", "vehicle"]
    router.max_routes = 2
    with pytest.raises(ValueError, match="product"):
        router.rag_route(Query(query_str="EV"), ["one"])


@pytest.mark.parametrize("options", [{"aliases": {"": ["x"]}}, {"aliases": {"x": "y"}},
    {"aliases": {"x": []}}, {"aliases": {"x": [""]}}, {"boundary": "regex"},
    {"max_variants": True}, {"max_routes": 0}])
def test_invalid_options(options):
    with pytest.raises(ValueError):
        AliasQueryRouter(**options).rag_route(Query(query_str="x"), ["one"])


def test_expansion_bound_and_ambiguous_bundle_rejection():
    router = AliasQueryRouter(aliases={"x": ["longer"]}, max_query_chars=2)
    with pytest.raises(ValueError, match="expanded"):
        router.rag_route(Query(query_str="x"), ["one"])
    router.max_query_chars = 100
    with pytest.raises(ValueError, match="bundle"):
        router.rag_route(Query(query_str="x", query_text_bundles=["other"]), ["one"])


def test_no_expansion_defaults_empty_and_runtime_validation():
    router = AliasQueryRouter()
    query = Query(query_str=None, embeddings=[[0.1]])
    routes = router.rag_route(query, ["one", "one"])
    assert len(routes) == 2 and routes[0][0].embeddings == [[0.1]]
    assert routes[0][0] is not routes[1][0] and routes[0][0] is not query
    assert router.rag_route(Query(query_str="x"), []) == []
    router.max_routes = True
    with pytest.raises(ValueError):
        router.rag_route(query, ["one"])


def test_actual_yaml_sqlite_knowledge_recall_and_duplicate_identity(tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.store.document import Document
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.store.alias_recall_store import AliasRecallStore
    from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
    from agentuniverse.base.config.configer import Configer
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    managers = [StoreManager(), DocProcessorManager(), RagRouterManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    callbacks = list(POST_FORK_QUEUE)
    apps = ApplicationConfigManager()
    try:
        prior = apps.app_configer
    except ValueError:
        prior = None
    store = ordinary = expanded = None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "alias-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[7]
        copied = tmp_path / "alias.yaml"
        shutil.copyfile(root / "agentuniverse/agent/action/knowledge/store/alias_recall_store.yaml.example", copied)
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        config.aliases = {"EV": ["electric vehicle"]}
        config.backend_store = "local"
        wrapped = AliasRecallStore().initialize_by_component_configer(config)
        store = SQLiteStore(name="local", db_path=str(tmp_path / "documents.db"), keyword_extractor="keywords")
        store._new_client()
        base = BaseRouter(name="base_router")
        for manager, component in zip(managers, [store, JiebaKeywordExtractor(name="keywords", top_k=100), base]):
            manager.register(component.get_instance_code(), component)
        managers[0].register(wrapped.get_instance_code(), wrapped)
        store.insert_document([Document(id="alias-only", text="electric vehicle manual"), Document(id="both", text="EV electric vehicle overview")])
        store.conn.close()
        store._new_client()
        ordinary = Knowledge(stores=["local"])
        expanded = Knowledge(stores=["alias_recall_store"])
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            baseline = ordinary.query_knowledge(query_str="EV", keywords={"EV"})
            result = expanded.query_knowledge(query_str="EV", keywords={"EV"})
        assert [doc.id for doc in baseline] == ["both"]
        assert [doc.id for doc in result] == ["both", "alias-only"]
        # Original-first merge, not per-query RRF votes; shared IDs remain unique.
        assert len(result) == len({doc.id for doc in result})
        assert all("recall_channel" not in (doc.metadata or {}) for doc in result)
    finally:
        for knowledge in (ordinary, expanded):
            if knowledge is not None:
                knowledge.insert_executor.shutdown(wait=True)
                knowledge.query_executor.shutdown(wait=True)
        if store is not None:
            store.conn.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = prior
        POST_FORK_QUEUE[:] = callbacks
