"""Tests for Chroma context metadata serialization."""

from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextPriority,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class _CapturingCollection:
    def add(self, **kwargs):
        self.payload = kwargs


def test_chroma_round_trip_preserves_rich_metadata_and_relationships():
    store = ChromaContextStore()
    store._collection = _CapturingCollection()
    segment = ContextSegment(
        type=ContextType.REFERENCE,
        priority=ContextPriority.HIGH,
        content="reference",
        tokens=3,
        session_id="session-1",
        related_ids=["related-1", "related-2"],
        metadata=ContextMetadata(
            source_type="knowledge_base",
            source_id="doc-7",
            keywords=["api", "contract"],
            entities={"service": "billing"},
            compressed=True,
            compression_ratio=0.5,
            custom={"tenant": "alpha"},
        ),
    )

    store.add([segment], session_id="session-1")
    restored = store._metadata_to_segment(
        store._collection.payload["documents"][0],
        store._collection.payload["metadatas"][0],
    )

    assert restored.metadata == segment.metadata
    assert restored.related_ids == segment.related_ids
