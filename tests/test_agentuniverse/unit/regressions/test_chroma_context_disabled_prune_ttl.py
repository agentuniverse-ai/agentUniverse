from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.chroma_context_store import ChromaContextStore


def test_chroma_prune_disables_age_filter_for_nonpositive_ttl(monkeypatch):
    store = ChromaContextStore(ttl_hours=0)
    store._collection = object()
    segment = ContextSegment(type=ContextType.TASK, content="old", tokens=1)
    segment.metadata.created_at = datetime.now() - timedelta(days=30)
    deleted = []
    monkeypatch.setattr(ChromaContextStore, "get", lambda *args, **kwargs: [segment])
    monkeypatch.setattr(ChromaContextStore, "delete", lambda *args, **kwargs: deleted.append(args))

    assert store.prune("session") == 0
    assert deleted == []
