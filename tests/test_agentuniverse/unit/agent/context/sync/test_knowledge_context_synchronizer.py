"""Tests for knowledge-to-context synchronization."""

from types import SimpleNamespace

from agentuniverse.agent.context.sync.knowledge_context_synchronizer import (
    KnowledgeContextSynchronizer,
)


class _RecordingContextManager:
    def __init__(self):
        self.added = []

    def add_context(self, *args, **kwargs):
        segment = SimpleNamespace(id=f"stored-{len(self.added)}")
        self.added.append(segment)
        return segment


def test_sync_tracks_ids_returned_by_context_manager():
    manager = _RecordingContextManager()
    synchronizer = KnowledgeContextSynchronizer(manager)

    result = synchronizer.sync_knowledge_to_context(
        knowledge_id="guide",
        documents=["first", "second"],
        session_id="session-1",
    )

    assert result.segments_added == 2
    assert synchronizer._knowledge_context_map["guide"] == [
        segment.id for segment in manager.added
    ]
