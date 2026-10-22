"""Tests for the Chroma-backed context store."""

from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class _FakeCollection:
    def __init__(self):
        self._sessions = {
            "session-1": ["segment-1", "segment-2"],
            "session-2": ["segment-3"],
        }

    def get(self, *, where, include=None):
        return {"ids": self._sessions.get(where["session_id"], [])}

    def count(self):
        return sum(len(ids) for ids in self._sessions.values())


def test_count_is_scoped_to_requested_session():
    store = ChromaContextStore()
    store._collection = _FakeCollection()

    assert store.count("session-1") == 2
    assert store.count("session-2") == 1
    assert store.count("missing") == 0
