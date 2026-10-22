from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class FakeCollection:
    def __init__(self):
        self.last_where = None
        self.last_include = None

    def get(self, where, include=None):
        self.last_where = where
        self.last_include = include
        return {"ids": ["segment-1", "segment-2"]}


def test_chroma_context_count_returns_session_filtered_count():
    store = ChromaContextStore()
    collection = FakeCollection()
    store._collection = collection

    assert store.count("session-a") == 2
    assert collection.last_where == {"session_id": "session-a"}
    assert collection.last_include == []


def test_chroma_context_count_returns_zero_without_collection():
    assert ChromaContextStore().count("session-a") == 0
