import uuid
from unittest.mock import Mock

from agentuniverse.agent.action.knowledge.store.qdrant_store import QdrantStore


def test_delete_normalizes_non_uuid_document_ids():
    client = Mock()
    store = QdrantStore(client=client)

    store.delete_document("order-42")

    expected_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "order-42"))
    client.delete.assert_called_once_with(
        collection_name="qdrant_db",
        points_selector=[expected_id],
    )


def test_normalize_point_id_preserves_uuid_values():
    document_id = "12345678-1234-5678-1234-567812345678"

    assert QdrantStore._normalize_point_id(document_id) == document_id
