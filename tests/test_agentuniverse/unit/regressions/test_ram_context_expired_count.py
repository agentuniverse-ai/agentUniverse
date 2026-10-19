"""Regression tests for RAM context-store counts."""

from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import (
    ContextMetadata,
    ContextSegment,
    ContextType,
)
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_count_excludes_expired_segments():
    store = RamContextStore(name="ram", ttl_hours=1)
    expired = ContextSegment(
        id="expired",
        type=ContextType.CONVERSATION,
        content="old context",
        tokens=2,
        metadata=ContextMetadata(
            created_at=datetime.now() - timedelta(hours=2),
        ),
    )
    current = ContextSegment(
        id="current",
        type=ContextType.CONVERSATION,
        content="current context",
        tokens=2,
    )

    store.add([expired, current], session_id="session")

    assert store.count("session") == 1
