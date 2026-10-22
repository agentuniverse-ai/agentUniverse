"""Exercise history selection against Qdrant's real local scrolling backend."""
from datetime import datetime, timedelta

import pytest

pytest.importorskip("qdrant_client")
from qdrant_client import QdrantClient, models

from agentuniverse.agent.memory.memory_storage.qdrant_memory_storage import QdrantMemoryStorage


@pytest.fixture
def storage():
    client = QdrantClient(":memory:")
    client.create_collection(
        "memory",
        vectors_config={"embedding": models.VectorParams(size=2, distance=models.Distance.COSINE)},
    )
    yield QdrantMemoryStorage(client=client)
    client.close()


def populate(storage, count=250):
    origin = datetime(2026, 1, 1)
    points = []
    for index in range(count):
        points.append(models.PointStruct(
            id=index + 1,
            vector={"embedding": [1.0, 0.0]},
            payload={
                "content": str(index),
                "gmt_created": (origin + timedelta(seconds=index)).isoformat(),
                "session_id": "session", "agent_id": "agent", "source": "user",
                "type": "input",
            },
        ))
    storage.client.upsert("memory", points)


@pytest.mark.parametrize("limit", [1, 2, 10, 101, 300])
def test_latest_history_across_pages(storage, limit):
    populate(storage)
    messages = storage.get(session_id="session", top_k=limit)
    assert [message.content for message in messages] == [str(i) for i in range(max(0, 250-limit), 250)]


def test_filters_apply_before_history_selection(storage):
    populate(storage)
    storage.client.set_payload("memory", {"session_id": "other"}, points=[250])
    storage.client.set_payload("memory", {"agent_id": "other"}, points=[249])
    storage.client.set_payload("memory", {"source": "other"}, points=[248])
    storage.client.set_payload("memory", {"type": "output"}, points=[247])
    messages = storage.get(session_id="session", agent_id="agent", source="user", type=["input"], top_k=2)
    assert [message.content for message in messages] == ["244", "245"]


def test_timestamps_not_point_ids_determine_recency(storage):
    populate(storage, 5)
    storage.client.set_payload("memory", {"gmt_created": "2027-01-01T00:00:00"}, points=[1])
    assert [m.content for m in storage.get(session_id="session", top_k=2)] == ["4", "0"]


def test_empty_filtered_history(storage):
    populate(storage, 2)
    assert storage.get(session_id="missing", top_k=2) == []


def test_equal_timestamps_have_stable_id_tiebreak(storage):
    populate(storage, 5)
    storage.client.set_payload("memory", {"gmt_created": "2026-01-01T00:00:00"}, points=[1, 2, 3, 4, 5])
    assert [m.content for m in storage.get(session_id="session", top_k=2)] == ["3", "4"]


def test_missing_timestamp_sorts_before_timestamped_history(storage):
    populate(storage, 3)
    storage.client.delete_payload("memory", ["gmt_created"], points=[3])
    assert [m.content for m in storage.get(session_id="session", top_k=2)] == ["0", "1"]


def test_payload_absence_does_not_break_unfiltered_history(storage):
    populate(storage, 2)
    storage.client.upsert("memory", [models.PointStruct(id=3, vector={"embedding": [1.0, 0.0]})])
    assert [m.content for m in storage.get(top_k=3)] == [None, "0", "1"]
