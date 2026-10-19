"""Expiration behavior for the in-memory context store."""

from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_get_by_ids_does_not_return_expired_segments():
    store = RamContextStore(ttl_hours=1)
    expired = ContextSegment(
        type=ContextType.CONVERSATION,
        content="expired",
        tokens=1,
        metadata=ContextMetadata(
            created_at=datetime.now() - timedelta(hours=2),
            last_accessed=datetime.now() - timedelta(hours=2),
        ),
    )
    store.add([expired], session_id="session-1")

    assert store.get_by_ids("session-1", [expired.id]) == []
    assert expired.metadata.access_count == 0
