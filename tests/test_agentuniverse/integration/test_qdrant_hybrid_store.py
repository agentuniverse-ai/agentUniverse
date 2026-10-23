"""Opt-in real Qdrant: use a disposable local service, never a production cluster."""

import asyncio
import os
import shutil
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.qdrant_hybrid_store import QdrantHybridStore
from agentuniverse.agent.action.knowledge.store.query import Query


@pytest.fixture
def store():
    endpoint = os.environ.get("AU_QDRANT_TEST_URL")
    if not endpoint:
        pytest.skip("set AU_QDRANT_TEST_URL for real service integration tests")
    pytest.importorskip("qdrant_client")
    backend = QdrantHybridStore(
        connection_args={"url": endpoint, "trust_env": False},
        collection_name="au_test_" + uuid4().hex,
        dimensions=2,
        create_collection=True,
    )
    backend._ready()
    backend.create_collection = False
    try:
        yield backend
    finally:
        backend.client.delete_collection(backend.collection_name)
        backend.close()


def docs():
    return [
        Document(
            id="exact",
            text="ZX-42 manual",
            embedding=[0.8, 0.6],
            metadata={"tenant": "a", "qdrant_sparse": {"indices": [42], "values": [5.0]}},
        ),
        Document(
            id="semantic",
            text="power startup manual",
            embedding=[1, 0],
            metadata={"tenant": "a", "qdrant_sparse": {"indices": [1], "values": [5.0]}},
        ),
        Document(
            id="other-tenant",
            text="ZX-42 private",
            embedding=[1, 0],
            metadata={"tenant": "b", "qdrant_sparse": {"indices": [42], "values": [10.0]}},
        ),
    ]


def query():
    return Query(
        embeddings=[[1, 0]], ext_info={"sparse_vector": {"indices": [42], "values": [1.0]}, "filters": {"tenant": "a"}}
    )


def test_real_native_fusion_matches_direct_server_query_and_filter(store):
    from qdrant_client import models

    assert store.insert_document(docs())["status"] == "completed"
    scope = models.Filter(
        must=[
            models.FieldCondition(key="_au_qdrant_hybrid", match=models.MatchValue(value=1)),
            models.FieldCondition(key="_au_filters", match=models.MatchValue(value=store._token("tenant", "a"))),
        ]
    )
    expected = store.client.query_points(
        collection_name=store.collection_name,
        prefetch=[
            models.Prefetch(query=[1, 0], using="au_dense", filter=scope, limit=50),
            models.Prefetch(
                query=models.SparseVector(indices=[42], values=[1.0]), using="au_sparse", filter=scope, limit=50
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        query_filter=scope,
        limit=10,
        with_payload=True,
    ).points
    actual = store.query(query())
    assert [d.id for d in actual] == [p.payload["id"] for p in expected] == ["exact", "semantic"]
    assert [d.metadata["qdrant_retrieval"]["score"] for d in actual] == pytest.approx([p.score for p in expected])
    store.mode = "dense"
    assert [d.id for d in store.query(query())] == ["semantic", "exact"]
    store.mode = "sparse"
    assert [d.id for d in store.query(query())] == ["exact"]


def test_real_replacement_updates_both_vectors_payload_reopen_delete(store):
    store.upsert_document(docs())
    replacement = Document(
        id="exact",
        text="new manual",
        embedding=[0, 1],
        metadata={"new": True, "qdrant_sparse": {"indices": [99], "values": [2.0]}},
    )
    store.update_document([replacement])
    point = store.client.retrieve(store.collection_name, ids=[store._point_id("exact")], with_vectors=True)[0]
    assert point.payload["metadata"] == {"new": True}
    assert point.vector[store.DENSE] == pytest.approx([0, 1])
    assert point.vector[store.SPARSE].indices == [99]
    reopened = QdrantHybridStore(
        connection_args=store.connection_args,
        collection_name=store.collection_name,
        dimensions=2,
        mode="sparse",
        with_vectors=True,
    )
    try:
        q = Query(ext_info={"sparse_vector": {"indices": [99], "values": [1.0]}})
        found = reopened.query(q)
        assert [d.id for d in found] == ["exact"]
        assert found[0].metadata["qdrant_sparse"]["indices"] == [99]
        assert found[0].embedding == pytest.approx([0, 1])
        reopened.delete_document("exact")
        assert reopened.query(q) == []
        assert reopened.delete_document("exact")["status"] == "completed"
    finally:
        reopened.close()


def test_real_async_crud_and_vectors(store):
    async def scenario():
        try:
            await store.async_insert_document(docs())
            assert [d.id for d in await store.async_query(query())] == ["exact", "semantic"]
            await store.async_update_document(
                [
                    Document(
                        id="exact",
                        text="updated",
                        embedding=[0, 1],
                        metadata={"tenant": "a", "qdrant_sparse": {"indices": [99], "values": [1.0]}},
                    )
                ]
            )
            store.mode = "sparse"
            assert await store.async_query(query()) == []
            await store.async_upsert_document(docs()[:1])
            assert [d.id for d in await store.async_query(query())] == ["exact"]
            await store.async_delete_document("exact")
            assert await store.async_query(query()) == []
        finally:
            await store.aclose()

    asyncio.run(scenario())


def test_real_schema_mismatch_and_batch_preflight_leave_data_unchanged(store):
    store.insert_document(docs()[:1])
    incompatible = QdrantHybridStore(
        connection_args=store.connection_args, collection_name=store.collection_name, dimensions=3
    )
    try:
        with pytest.raises(ValueError, match="dimension"):
            incompatible.upsert_document(
                [
                    Document(
                        id="bad",
                        text="invalid",
                        embedding=[1, 0, 0],
                        metadata={"qdrant_sparse": {"indices": [1], "values": [1.0]}},
                    )
                ]
            )
    finally:
        incompatible.close()
    malformed = docs()[1]
    malformed.metadata["qdrant_sparse"]["indices"] = [1, 1]
    with pytest.raises(ValueError):
        store.upsert_document([docs()[0], malformed])
    assert store.client.count(store.collection_name, exact=True).count == 1


def test_real_scalar_filter_types_are_distinct(store):
    values = [True, 1, 1.0, "1", None]
    documents = []
    for index, value in enumerate(values):
        document = docs()[0]
        document.id = str(index)
        document.metadata["typed"] = value
        documents.append(document)
    store.insert_document(documents)
    for index, value in enumerate(values):
        q = query()
        q.ext_info["filters"] = {"typed": value}
        assert [document.id for document in store.query(q)] == [str(index)]


def test_real_yaml_processors_public_knowledge_roundtrip(store, tmp_path):
    import agentuniverse.base.annotation.trace as trace_module
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
    from agentuniverse.agent.action.knowledge.doc_processor.doc_processor_manager import DocProcessorManager
    from agentuniverse.agent.action.knowledge.knowledge import Knowledge
    from agentuniverse.agent.action.knowledge.rag_router.base_router import BaseRouter
    from agentuniverse.agent.action.knowledge.rag_router.rag_router_manager import RagRouterManager
    from agentuniverse.agent.action.knowledge.reader.file.txt_reader import TxtReader
    from agentuniverse.agent.action.knowledge.reader.reader_manager import ReaderManager
    from agentuniverse.agent.action.knowledge.store.store_manager import StoreManager
    from agentuniverse.agent_serve.web.post_fork_queue import POST_FORK_QUEUE
    from agentuniverse.base.config.application_configer.app_configer import AppConfiger
    from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
    from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
    from agentuniverse.base.config.configer import Configer

    class FixtureVectors(DocProcessor):
        def _process_docs(self, documents, query=None):
            for document in documents:
                document.embedding = [1, 0]
                document.metadata["qdrant_sparse"] = {"indices": [42], "values": [1.0]}
            return documents

    managers = [ReaderManager(), StoreManager(), RagRouterManager(), DocProcessorManager()]
    pools = [dict(manager._instance_obj_map) for manager in managers]
    callbacks = list(POST_FORK_QUEUE)
    apps = ApplicationConfigManager()
    try:
        previous = apps.app_configer
    except ValueError:
        previous = None
    knowledge, backend = None, None
    try:
        app = Configer()
        app.value = {"BASE_INFO": {"appname": "qdrant-hybrid-integration"}}
        apps.app_configer = AppConfiger().load_by_configer(app)
        for manager in managers:
            manager._instance_obj_map.clear()
        root = Path(__file__).resolve().parents[3]
        copied = tmp_path / "qdrant.yaml"
        shutil.copyfile(root / "agentuniverse/agent/action/knowledge/store/qdrant_hybrid_store.yaml.example", copied)
        config = ComponentConfiger().load_by_configer(Configer(str(copied)).load())
        config.connection_args, config.collection_name, config.dimensions = (
            store.connection_args,
            store.collection_name,
            2,
        )
        backend = QdrantHybridStore().initialize_by_component_configer(config)
        components = [
            TxtReader(name="text"),
            backend,
            BaseRouter(name="base_router"),
            FixtureVectors(name="fixture_vectors"),
        ]
        for manager, component in zip(managers, components):
            manager.register(component.get_instance_code(), component)
        knowledge = Knowledge(
            readers={"txt": "text"}, stores=["qdrant_hybrid_store"], insert_processors=["fixture_vectors"]
        )
        path = tmp_path / "manual.txt"
        path.write_text("ZX-42 product manual", encoding="utf-8")
        knowledge.insert_knowledge(source_path=str(path))
        assert backend.client.count(store.collection_name, exact=True).count == 1
        with patch.object(trace_module, "ConversationMemoryModule"), patch.object(trace_module, "Monitor") as monitor:
            monitor.get_invocation_chain.return_value = []
            result = knowledge.query_knowledge(
                query_str="ZX-42", embeddings=[[1, 0]], ext_info={"sparse_vector": {"indices": [42], "values": [1.0]}}
            )
        assert len(result) == 1 and result[0].text == "ZX-42 product manual"
        assert result[0].metadata["file_name"] == "manual.txt"
        assert result[0].metadata["qdrant_retrieval"]["mode"] == "hybrid"
    finally:
        if knowledge is not None:
            knowledge.insert_executor.shutdown(wait=True)
            knowledge.query_executor.shutdown(wait=True)
        if backend is not None:
            backend.close()
        for manager, pool in zip(managers, pools):
            manager._instance_obj_map.clear()
            manager._instance_obj_map.update(pool)
        apps.app_configer = previous
        POST_FORK_QUEUE[:] = callbacks
