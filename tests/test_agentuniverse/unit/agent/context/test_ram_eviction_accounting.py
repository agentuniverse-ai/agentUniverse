"""Keep window accounting consistent with capacity evictions during writes."""

from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.context.context_manager import ContextManager
from agentuniverse.agent.context.context_model import ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def make_manager(capacity=2, budget=1000):
    manager = ContextManager()
    manager._hot_store = RamContextStore(max_segments=capacity)
    manager.create_context_window("session", max_tokens=budget + 1000, reserved_tokens=1000)
    return manager


def add(manager, tokens, priority=ContextPriority.HIGH, session="session"):
    return manager.add_context(session, "x" * (tokens * 4), ContextType.CONVERSATION, priority)


def assert_accounting(manager, session="session"):
    # Inspect without a retrieval, which would itself update access/LRU order.
    stored = list(manager._hot_store._storage.get(session, {}).values())
    window = manager.get_context_window(session)
    assert set(window.segment_ids) == {segment.id for segment in stored}
    assert window.total_tokens == sum(segment.tokens for segment in stored)


def test_capacity_eviction_removes_old_id_and_its_token_cost():
    manager = make_manager()
    oldest = add(manager, 10)
    add(manager, 20)
    newest = add(manager, 30)

    assert_accounting(manager)
    window = manager.get_context_window("session")
    assert oldest.id not in window.segment_ids
    assert newest.id in window.segment_ids
    assert window.total_tokens == 50


@pytest.mark.parametrize("priority", [ContextPriority.EPHEMERAL, ContextPriority.LOW, ContextPriority.MEDIUM])
def test_priority_eviction_reports_the_actual_victim(priority):
    manager = make_manager()
    first = add(manager, 10)
    victim = add(manager, 20, priority)
    victim.metadata.relevance_score = 0.2
    add(manager, 30)

    assert_accounting(manager)
    window = manager.get_context_window("session")
    assert victim.id not in window.segment_ids
    assert first.id in window.segment_ids
    assert window.total_tokens == 40


def test_new_ephemeral_segment_can_evict_itself_without_phantom_accounting():
    manager = make_manager()
    add(manager, 10)
    add(manager, 20)
    discarded = add(manager, 30, ContextPriority.EPHEMERAL)

    assert_accounting(manager)
    window = manager.get_context_window("session")
    assert discarded.id not in window.segment_ids
    assert window.total_tokens == 30


def test_capacity_accounting_does_not_trigger_unnecessary_budget_eviction():
    manager = make_manager(budget=30)
    with patch.object(ContextManager, "_make_room") as make_room:
        for _ in range(20):
            add(manager, 10)
        make_room.assert_not_called()
    assert_accounting(manager)


def test_recent_access_and_session_isolation_are_preserved():
    manager = make_manager()
    first = add(manager, 10)
    second = add(manager, 20)
    manager._hot_store.get_by_ids("session", [first.id])
    other = add(manager, 40, session="other")
    add(manager, 30)

    assert_accounting(manager)
    assert_accounting(manager, "other")
    assert second.id not in manager.get_context_window("session").segment_ids
    assert manager.get_context_window("other").segment_ids == [other.id]


def test_zero_capacity_does_not_leave_phantom_segment():
    manager = make_manager(capacity=0)
    add(manager, 10)
    assert_accounting(manager)
    assert manager.get_context_window("session").total_tokens == 0


def test_large_capacity_accounting_needs_no_paged_read():
    manager = make_manager(capacity=101, budget=10000)
    with patch.object(RamContextStore, "get", side_effect=AssertionError("unexpected read")):
        for _ in range(205):
            add(manager, 10)
    assert_accounting(manager)
    assert manager.get_context_window("session").total_tokens == 1010


def segment(identifier, tokens):
    return ContextSegment(id=identifier, content=identifier, tokens=tokens, type=ContextType.CONVERSATION)


def test_store_reports_all_batch_evictions_and_keeps_metrics_once_per_call():
    store = RamContextStore(max_segments=2, enable_metrics=True)
    segments = [segment(str(i), i + 1) for i in range(5)]

    evicted = store.add(segments, session_id="session")

    assert [item.id for item in evicted] == ["0", "1", "2"]
    assert [item.tokens for item in evicted] == [1, 2, 3]
    assert list(store._storage["session"]) == ["3", "4"]
    assert store.get_metrics()["add_count"] == 1
    assert store.add([], session_id="session") == []
    assert store.get_metrics()["add_count"] == 2


def test_store_replacement_without_eviction_returns_empty_report():
    store = RamContextStore(max_segments=1)
    assert store.add([segment("one", 1)], session_id="session") == []
    assert store.add([segment("one", 2)], session_id="session") == []
    assert store._storage["session"]["one"].tokens == 2


def test_nonreporting_store_retains_existing_manager_behavior():
    manager = make_manager()
    manager._hot_store = Mock()
    manager._hot_store.add.return_value = None

    created = add(manager, 10)

    window = manager.get_context_window("session")
    assert window.segment_ids == [created.id]
    assert window.total_tokens == 10
    manager._hot_store.get.assert_not_called()


def test_evicted_untracked_segment_does_not_reduce_existing_window_tokens():
    manager = make_manager()
    manager._hot_store = Mock()
    manager._hot_store.add.return_value = None
    first = add(manager, 10)
    manager._hot_store.add.return_value = [segment("untracked", 100)]
    second = add(manager, 20)

    window = manager.get_context_window("session")
    assert window.segment_ids == [first.id, second.id]
    assert window.total_tokens == 30


def test_failed_store_write_does_not_mutate_window():
    manager = make_manager()
    manager._hot_store = Mock()
    manager._hot_store.add.side_effect = RuntimeError("write failed")

    with pytest.raises(RuntimeError, match="write failed"):
        add(manager, 10)

    window = manager.get_context_window("session")
    assert window.segment_ids == []
    assert window.total_tokens == 0


def test_capacity_then_complete_compression_preserves_accounting():
    """Capacity eviction and >100-item maintenance compose on one session."""
    manager = make_manager(capacity=101, budget=10000)
    for _ in range(205):
        add(manager, 10)
    assert_accounting(manager)
    window = manager.get_context_window("session")
    retained = set(window.segment_ids)
    assert len(retained) == 101
    window.max_tokens = window.total_tokens + window.reserved_tokens
    manager._compressor = Mock()
    manager._compressor.compress.side_effect = lambda items, *args, **kwargs: (items, None)

    manager._make_room(window, needed_tokens=1)

    assert_accounting(manager)
    assert set(window.segment_ids) == retained
    assert {item.id for item in manager._compressor.compress.call_args.args[0]} == retained
    # A subsequent bounded write must still remove only its actual victim.
    window.max_tokens = 11000
    newest = add(manager, 10)
    assert_accounting(manager)
    assert len(window.segment_ids) == 101
    assert newest.id in window.segment_ids
    assert len(set(window.segment_ids) & retained) == 100
