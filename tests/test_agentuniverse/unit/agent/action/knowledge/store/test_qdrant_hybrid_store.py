import asyncio
from copy import deepcopy
from unittest.mock import AsyncMock, Mock

import pytest

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.qdrant_hybrid_store import QdrantHybridStore
from agentuniverse.agent.action.knowledge.store.query import Query

models = pytest.importorskip("qdrant_client.models")


def doc(identity="a"):
    return Document(
        id=identity,
        text="alpha",
        embedding=[3, 4],
        metadata={"tenant": "a", "qdrant_sparse": {"indices": [3, 1], "values": [2.0, 1.0]}},
    )


def query():
    return Query(
        embeddings=[[1, 0]], ext_info={"sparse_vector": {"indices": [3], "values": [1.0]}, "filters": {"tenant": "a"}}
    )


@pytest.fixture
def store():
    return QdrantHybridStore(dimensions=2, client=Mock())


def test_both_vectors_preserve_identity_and_inputs(store):
    original = doc()
    before = original.model_dump()
    points = store._points([original], {})
    assert points[0].payload["id"] == "a"
    assert points[0].vector[store.DENSE] == pytest.approx([0.6, 0.8])
    assert points[0].vector[store.SPARSE].indices == [1, 3]
    assert "qdrant_sparse" not in points[0].payload["metadata"]
    assert original.model_dump() == before
    assert store._point_id("a") == points[0].id
    assert store._point_id(points[0].id) != points[0].id


@pytest.mark.parametrize(
    "sparse",
    [
        None,
        {},
        {"indices": [], "values": []},
        {"indices": [1, 1], "values": [1, 2]},
        {"indices": [True], "values": [1]},
        {"indices": [-1], "values": [1]},
        {"indices": [4294967296], "values": [1]},
        {"indices": [1], "values": [float("nan")]},
        {"indices": [1], "values": [0]},
        {"indices": [1], "values": [1e40]},
        {"indices": [1], "values": [1, 2]},
    ],
)
def test_invalid_sparse_preflight(store, sparse):
    original = doc()
    original.metadata["qdrant_sparse"] = sparse
    with pytest.raises(ValueError):
        store.upsert_document([original])
    store.client.upsert.assert_not_called()
    store.client.get_collection.assert_not_called()


@pytest.mark.parametrize("vector", [[0, 0], [1], [float("inf"), 1], [True, 1]])
def test_dense_validation(store, vector):
    with pytest.raises(ValueError):
        store._dense(vector)


def test_native_prefetch_filter_in_both_routes_without_mutation(store):
    q = query()
    before = q.model_dump()
    request = store._request(q, {})
    assert request["query"].fusion == models.Fusion.RRF
    assert len(request["prefetch"]) == 2
    assert [p.using for p in request["prefetch"]] == [store.DENSE, store.SPARSE]
    assert all(p.filter == request["query_filter"] for p in request["prefetch"])
    assert all(p.limit == store.candidate_k for p in request["prefetch"])
    assert q.model_dump() == before
    assert len({store._token("x", v) for v in (True, 1, 1.0, "1", None)}) == 5


def test_limits_no_io_empty_batch_and_zero_top(store):
    with pytest.raises(ValueError, match="duplicate"):
        store.upsert_document([doc(), doc()])
    store.max_payload_bytes = 1
    with pytest.raises(ValueError, match="budget"):
        store.upsert_document([doc()])
    assert store.query(Query(similarity_top_k=0)) == []
    assert store.insert_document([])["status"] == "completed"
    store.client.get_collection.assert_not_called()


@pytest.mark.parametrize(
    "options",
    [
        {"dimensions": True},
        {"collection_name": "../other"},
        {"candidate_k": 1},
        {"create_collection": 1},
        {"with_vectors": "false"},
        {"mode": "other"},
        {"timeout_seconds": 0},
    ],
)
def test_configuration_validation(options):
    with pytest.raises(ValueError):
        QdrantHybridStore(**options)._validate()


def test_reject_incompatible_named_vectors_and_unconfirmed_write(store):
    info = Mock()
    info.config.params.vectors = {"embedding": models.VectorParams(size=2, distance=models.Distance.COSINE)}
    info.config.params.sparse_vectors = {}
    with pytest.raises(ValueError, match="dedicated"):
        store._check_schema(info)
    with pytest.raises(RuntimeError, match="not confirmed"):
        store._outcome(models.UpdateResult(operation_id=1, status=models.UpdateStatus.ACKNOWLEDGED))


def test_async_cancel_propagates_without_adapter_retry(store):
    async def scenario():
        client = AsyncMock()
        info = Mock()
        info.config.params.vectors = {store.DENSE: models.VectorParams(size=2, distance=models.Distance.COSINE)}
        info.config.params.sparse_vectors = {store.SPARSE: models.SparseVectorParams()}
        client.get_collection.return_value = info
        store.async_client = client
        ready = asyncio.Event()

        async def write(**kwargs):
            ready.set()
            await asyncio.Future()

        client.upsert.side_effect = write
        task = asyncio.create_task(store.async_upsert_document([doc()]))
        await asyncio.wait_for(ready.wait(), 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert client.upsert.await_count == 1
        await store.aclose()
        client.close.assert_awaited_once()
        assert store.async_client is None

    asyncio.run(scenario())


def test_outputs_are_isolated_and_identity_checked(store):
    point = models.ScoredPoint(
        id=store._point_id("a"),
        version=1,
        score=0.5,
        payload={"id": "a", "text": "alpha", "metadata": {"nested": [1]}, "_au_qdrant_hybrid": 1},
    )
    from qdrant_client.http.models.models import QueryResponse

    response = QueryResponse(points=[point])
    before = deepcopy(response)
    result = store._documents(response)
    result[0].metadata["nested"].append(2)
    assert response == before
    point.payload["id"] = "b"
    with pytest.raises(RuntimeError, match="identity"):
        store._documents(response)
