"""Store-local query mutations must not cross recall tasks or reach processors."""
import threading
from copy import deepcopy
from unittest.mock import patch

import pytest
from pydantic import Field
from PIL import Image

from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
from agentuniverse.base.config.configer import Configer
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
import agentuniverse.base.annotation.trace as trace_module


@pytest.fixture
def managers():
    pools = [StoreManager(), DocProcessorManager(), RagRouterManager()]
    snapshots = [dict(manager._instance_obj_map) for manager in pools]
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    config = Configer()
    config.value = {"BASE_INFO": {"appname": "query-isolation"}}
    apps.app_configer = AppConfiger().load_by_configer(config)
    for manager in pools:
        manager._instance_obj_map.clear()
    base = BaseRouter(name="base_router")
    pools[2].register(base.get_instance_code(), base)
    try:
        yield pools
    finally:
        for manager, snapshot in zip(pools, snapshots):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(snapshot)
        apps.app_configer = previous


def public_query(knowledge, **kwargs):
    with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
        monitor.get_invocation_chain.return_value = []
        return knowledge.query_knowledge(**kwargs)


def shutdown(knowledge):
    knowledge.insert_executor.shutdown(wait=True)
    knowledge.query_executor.shutdown(wait=True)


def test_real_sqlite_extractors_keep_independent_query_keywords(tmp_path, managers):
    done = threading.Event()

    class OrderedSQLite(SQLiteStore):
        first: bool = False
        received: list = Field(default_factory=list)
        def query(self, query, **kwargs):
            if not self.first:
                assert done.wait(5)
            self.received.append(deepcopy(query))
            try:
                return super().query(query, **kwargs)
            finally:
                if self.first:
                    done.set()

    first = OrderedSQLite(name="first", db_path=str(tmp_path / "first.db"), keyword_extractor="one", first=True)
    second = OrderedSQLite(name="second", db_path=str(tmp_path / "second.db"), keyword_extractor="many")
    knowledge = Knowledge(stores=["first", "second"])
    try:
        for store in (first, second):
            store._new_client()
            managers[0].register(store.get_instance_code(), store)
        for extractor in (JiebaKeywordExtractor(name="one", top_k=1), JiebaKeywordExtractor(name="many", top_k=100)):
            managers[1].register(extractor.get_instance_code(), extractor)
        first.insert_document([Document(id="a", text="alpha")])
        second.insert_document([Document(id="b", text="beta")])
        # More alpha occurrences make top-1 selection deterministic, not a tie.
        result = public_query(knowledge, query_str="alpha alpha beta")
        assert {doc.id for doc in result} == {"a", "b"}
        assert first.received[0].keywords == second.received[0].keywords == set()
    finally:
        shutdown(knowledge)
        for store in (first, second):
            if store.conn is not None:
                store.conn.close()


@pytest.mark.parametrize("fail_first", [False, True])
def test_nested_query_mutations_do_not_reach_other_store_or_postprocessor(fail_first):
    done = threading.Event()
    seen = []
    post_queries = []
    class Mutating:
        def query(self, query):
            query.query_str = "changed"
            query.keywords.add("private")
            query.embeddings[0].append(9.0)
            query.query_text_bundles.append("private")
            query.query_image_bundles[0].putpixel((0, 0), (255, 0, 0))
            query.ext_info["filter"]["values"].append("private")
            done.set()
            if fail_first:
                raise RuntimeError("controlled provider failure")
            return [Document(id="a", text="first")]
    class Observing:
        def query(self, query):
            assert done.wait(5)
            seen.append(deepcopy(query))
            return [Document(id="b", text="second")]
    stores = {"first": Mutating(), "second": Observing()}
    knowledge = Knowledge(stores=list(stores))
    caller_filter = {"filter": {"values": ["public"]}}
    caller_image = Image.new("RGB", (2, 2), (0, 0, 0))
    def process(self, docs, query):
        post_queries.append(deepcopy(query))
        return docs
    try:
        with patch("agentuniverse.agent.action.knowledge.knowledge.StoreManager") as manager, \
             patch("agentuniverse.agent.action.knowledge.knowledge.RagRouterManager") as router, \
             patch.object(Knowledge, "_rag_post_process", process):
            manager.return_value.get_instance_obj.side_effect = lambda name, **kwargs: stores[name]
            router.return_value.get_instance_obj.return_value = BaseRouter()
            result = public_query(knowledge, query_str="original", keywords={"public"}, embeddings=[[1.0]],
                                  query_text_bundles=["original"], query_image_bundles=[caller_image], ext_info=caller_filter)
        assert {doc.id for doc in result} == ({"b"} if fail_first else {"a", "b"})
        for snapshot in [*seen, *post_queries]:
            assert snapshot.query_str == "original"
            assert snapshot.keywords == {"public"}
            assert snapshot.embeddings == [[1.0]]
            assert snapshot.query_text_bundles == ["original"]
            assert snapshot.query_image_bundles[0].getpixel((0, 0)) == (0, 0, 0)
            assert snapshot.ext_info == {"filter": {"values": ["public"]}}
        assert caller_filter == {"filter": {"values": ["public"]}}
        assert caller_image.getpixel((0, 0)) == (0, 0, 0)
    finally:
        shutdown(knowledge)


def test_uncopyable_routed_query_fails_before_any_store_dispatch():
    class Uncopyable:
        def __deepcopy__(self, memo):
            raise TypeError("uncopyable provider context")
    knowledge = Knowledge(stores=["first", "second"])
    tasks = [(Query(query_str="plain"), "first"),
             (Query(query_str="context", ext_info={"context": Uncopyable()}), "second")]
    try:
        with patch.object(Knowledge, "_route_rag", return_value=tasks), \
             patch("agentuniverse.agent.action.knowledge.knowledge.StoreManager") as manager:
            with pytest.raises(TypeError, match="uncopyable"):
                public_query(knowledge, query_str="source")
        manager.return_value.get_instance_obj.assert_not_called()
    finally:
        shutdown(knowledge)


@pytest.mark.parametrize("reuse_query", [False, True])
def test_router_owned_shared_context_is_copied_per_task(reuse_query):
    shared = ["public"]
    original = Query(query_str="source", ext_info={"left": shared, "right": shared})
    other = original if reuse_query else Query(
        query_str="source", ext_info={"left": shared, "right": shared})
    finished = threading.Event()
    observed = []

    class Mutating:
        def query(self, query):
            try:
                assert query.ext_info["left"] is query.ext_info["right"]
                query.ext_info["left"].append("private")
                return [Document(id="first", text="first")]
            finally:
                finished.set()

    class Observing:
        def query(self, query):
            assert finished.wait(5)
            observed.append(query)
            return [Document(id="second", text="second")]

    providers = {"first": Mutating(), "second": Observing()}
    knowledge = Knowledge(stores=list(providers))
    try:
        with patch.object(Knowledge, "_route_rag", return_value=[
            (original, "first"), (other, "second")
        ]), patch("agentuniverse.agent.action.knowledge.knowledge.StoreManager") as manager:
            manager.return_value.get_instance_obj.side_effect = lambda name, **kwargs: providers[name]
            result = public_query(knowledge, query_str="source")
        assert [doc.id for doc in result] == ["first", "second"]
        assert len(observed) == 1
        assert observed[0].ext_info["left"] == ["public"]
        assert observed[0].ext_info["left"] is observed[0].ext_info["right"]
        assert observed[0].ext_info["left"] is not shared
        assert shared == ["public"]
        assert original.ext_info["left"] is shared
        assert other.ext_info["left"] is shared
    finally:
        shutdown(knowledge)


@pytest.mark.parametrize("stores", [[], ["same"], ["same", "same"]])
def test_router_task_order_and_distinct_queries_preserved(stores):
    knowledge = Knowledge(stores=stores)
    supplied = [Query(query_str=str(index), ext_info={"order": [index]}) for index in range(len(stores))]
    observed = []
    class Provider:
        def query(self, query):
            observed.append(query)
            return [Document(id=query.query_str, text=query.query_str)]
    try:
        with patch.object(Knowledge, "_route_rag", return_value=list(zip(supplied, stores))), \
             patch("agentuniverse.agent.action.knowledge.knowledge.StoreManager") as manager:
            manager.return_value.get_instance_obj.return_value = Provider()
            result = public_query(knowledge, query_str="source")
        assert [doc.id for doc in result] == [str(index) for index in range(len(stores))]
        assert sorted(query.query_str for query in observed) == [str(index) for index in range(len(stores))]
        assert all(received is not original for received in observed for original in supplied)
    finally:
        shutdown(knowledge)
