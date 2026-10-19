"""Session-scoped count behavior for the Chroma context store."""

from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


class FakeCollection:
    def __init__(self, sessions):
        self.sessions = sessions
        self.calls = []

    def get(self, *, where, include=None, limit=None, offset=0):
        self.calls.append((where, include, limit, offset))
        matching = [index for index, session in enumerate(self.sessions) if session == where["session_id"]]
        return {"ids": matching[offset:offset + limit if limit is not None else None]}

    def count(self):
        return len(self.sessions)


def test_count_only_includes_requested_session():
    store = ChromaContextStore()
    collection = FakeCollection(["first", "second", "first"])
    store._collection = collection

    assert store.count("first") == 2
    assert store.count("missing") == 0
    assert all(call[1] == [] for call in collection.calls)


def test_count_pages_through_large_sessions():
    store = ChromaContextStore()
    collection = FakeCollection(["first"] * 1001 + ["second"])
    store._collection = collection

    assert store.count("first") == 1001
    assert [call[3] for call in collection.calls] == [0, 1000]


def test_count_checks_following_page_at_exact_batch_boundary():
    store = ChromaContextStore()
    collection = FakeCollection(["first"] * 2000 + ["second"])
    store._collection = collection

    assert store.count("first") == 2000
    assert [call[3] for call in collection.calls] == [0, 1000, 2000]
