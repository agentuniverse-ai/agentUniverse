from agentuniverse.agent.context.context_store import ContextStore


class RecordingStore(ContextStore):
    calls: list = []

    def add(self, segments, **kwargs):
        self.calls.append((segments, kwargs))

    def get(self, session_id, context_type=None, limit=100, **kwargs):
        return []

    def search(self, query, session_id, top_k=10, **kwargs):
        return []

    def delete(self, session_id, segment_ids=None, **kwargs):
        return None

    def prune(self, session_id, **kwargs):
        return 0


def test_batch_add_uses_mapping_session_ids_over_shared_kwargs():
    store = RecordingStore()

    store.batch_add({"first": [1], "second": [2]}, session_id="wrong", ttl=30)

    assert [call[1]["session_id"] for call in store.calls] == ["first", "second"]
    assert all(call[1]["ttl"] == 30 for call in store.calls)
