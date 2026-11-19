from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.context_store import ContextStore


class ListContextStore(ContextStore):
    def __init__(self, segments):
        super().__init__(name="list", max_segments=200)
        self._segments = segments

    def add(self, segments, **kwargs):
        self._segments.extend(segments)

    def get(self, session_id, context_type=None, limit=100, **kwargs):
        return self._segments[:limit]

    def search(self, query, session_id, top_k=10, **kwargs):
        return []

    def delete(self, session_id, segment_ids=None, **kwargs):
        pass

    def prune(self, session_id, **kwargs):
        return 0


def test_default_count_is_not_capped_by_get_default():
    segments = [
        ContextSegment(id=str(index), type=ContextType.REFERENCE, content=str(index), tokens=1)
        for index in range(101)
    ]
    store = ListContextStore(segments)

    assert store.count("session") == 101
