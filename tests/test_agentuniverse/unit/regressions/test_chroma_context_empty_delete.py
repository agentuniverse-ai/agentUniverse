"""Regression tests for Chroma context-store deletion."""

from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class RecordingCollection:
    def __init__(self):
        self.calls = []

    def delete(self, **kwargs):
        self.calls.append(kwargs)


def test_empty_segment_id_list_does_not_delete_session():
    store = ChromaContextStore(name="chroma")
    collection = RecordingCollection()
    store._collection = collection

    store.delete("session", segment_ids=[])

    assert collection.calls == []
