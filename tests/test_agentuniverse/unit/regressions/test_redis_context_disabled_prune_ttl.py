from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.redis_context_store import RedisContextStore


def test_redis_prune_disables_age_filter_for_nonpositive_ttl(monkeypatch):
    store = RedisContextStore(ttl_hours=0)
    store._redis = object()
    segment = ContextSegment(type=ContextType.TASK, content="old", tokens=1)
    segment.metadata.created_at = datetime.now() - timedelta(days=30)
    deleted = []
    monkeypatch.setattr(RedisContextStore, "get", lambda *args, **kwargs: [segment])
    monkeypatch.setattr(RedisContextStore, "delete", lambda *args, **kwargs: deleted.append(args))

    assert store.prune("session") == 0
    assert deleted == []
