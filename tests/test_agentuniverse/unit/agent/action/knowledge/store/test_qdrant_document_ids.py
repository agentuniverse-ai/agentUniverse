#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from unittest.mock import Mock

from qdrant_client import QdrantClient

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.qdrant_store import QdrantStore


def test_non_uuid_document_ids_round_trip_and_delete_consistently():
    client = Mock(spec=QdrantClient)
    client.collection_exists.return_value = True
    store = QdrantStore(client=client)
    document = Document(
        id="source-document-id",
        text="content",
        embedding=[0.1, 0.2],
    )

    store.upsert_document([document])

    point = client.upsert.call_args.kwargs["points"][0]
    assert point.payload["id"] == "source-document-id"
    restored = store.to_documents([
        Mock(id=point.id, payload=point.payload, vector=point.vector)
    ])
    assert restored[0].id == "source-document-id"

    store.delete_document("source-document-id")
    assert client.delete.call_args.kwargs["points_selector"] == [point.id]
