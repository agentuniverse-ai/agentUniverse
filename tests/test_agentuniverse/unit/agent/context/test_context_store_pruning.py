#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from datetime import datetime, timedelta

from agentuniverse.agent.context.context_model import ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def test_zero_max_age_prunes_existing_segments():
    store = RamContextStore(name="test_store", ttl_hours=24)
    segment = ContextSegment(
        type=ContextType.BACKGROUND,
        content="Existing context",
        tokens=2,
    )
    segment.metadata.created_at = datetime.now() - timedelta(seconds=1)
    store.add([segment], session_id="session")

    assert store.prune(
        "session", max_age_hours=0, min_decay_score=0
    ) == 1
    assert store.count("session") == 0
