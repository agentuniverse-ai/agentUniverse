"""Search relevance, synchronization, and copy contracts for RAM context storage."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier, Event, RLock

import pytest

from agentuniverse.agent.context.context_model import ContextMetadata, ContextPriority, ContextSegment, ContextType
from agentuniverse.agent.context.store.ram_context_store import RamContextStore


def _segment(segment_id, content="Python context", **kwargs):
    return ContextSegment(
        id=segment_id,
        type=ContextType.BACKGROUND,
        content=content,
        tokens=2,
        metadata=ContextMetadata(decay_rate=0),
        **kwargs,
    )


@pytest.mark.parametrize("priority", list(ContextPriority))
def test_priority_cannot_make_an_unrelated_segment_a_search_hit(priority):
    store = RamContextStore()
    unrelated = _segment("unrelated", "Cooking recipes", priority=priority)
    store.add([unrelated], session_id="session")

    assert store.search("python", "session") == []
    assert unrelated.metadata.access_count == 0


def test_metadata_keyword_match_remains_relevant():
    store = RamContextStore()
    relevant = _segment("relevant", "Language reference", priority=ContextPriority.LOW)
    relevant.metadata.keywords = ["PYTHON"]
    unrelated = _segment("unrelated", "Cooking recipes", priority=ContextPriority.CRITICAL)
    store.add([relevant, unrelated], session_id="session")

    assert store.search("python", "session", top_k=1) == [relevant]
    assert unrelated.metadata.access_count == 0


def test_priority_still_orders_actual_matches():
    store = RamContextStore()
    low = _segment("low", priority=ContextPriority.LOW)
    high = _segment("high", priority=ContextPriority.HIGH)
    unrelated = _segment("unrelated", "Cooking recipes", priority=ContextPriority.CRITICAL)
    store.add([low, high, unrelated], session_id="session")

    assert store.search("python", "session") == [high, low]


class _ObservedRLock:
    """Signal lock acquisition attempts so tests need no scheduling sleeps."""

    def __init__(self):
        self.lock = RLock()
        self.attempted = Event()

    def __enter__(self):
        self.attempted.set()
        assert self.lock.acquire(timeout=5), "Store operation did not release the lock"
        return self

    def __exit__(self, *args):
        self.lock.release()


@pytest.mark.parametrize(
    "method,args,kwargs",
    [
        ("add", ([],), {"session_id": "session"}),
        ("get", ("session",), {}),
        ("search", ("python", "session"), {}),
        ("delete", ("session",), {}),
        ("prune", ("session",), {}),
        ("get_by_ids", ("session", ["one"]), {}),
        ("count", ("session",), {}),
        ("get_all_sessions", (), {}),
        ("clear_all", (), {}),
        ("batch_add", ({"other": []},), {}),
        ("initialize_metrics", (), {}),
        ("get_metrics", (), {}),
        ("__deepcopy__", (), {}),
    ],
)
def test_public_operations_use_the_same_store_lock(method, args, kwargs):
    store = RamContextStore(enable_metrics=True)
    store.add([_segment("one")], session_id="session")
    observed = _ObservedRLock()
    store._lock = observed

    with ThreadPoolExecutor(max_workers=1) as executor:
        with observed.lock:
            pending = executor.submit(getattr(store, method), *args, **kwargs)
            assert observed.attempted.wait(timeout=2), f"{method} did not acquire the store lock"
            assert not pending.done()
        pending.result(timeout=5)


def test_concurrent_adds_preserve_segments_and_metrics():
    workers = 4
    per_worker = 25
    store = RamContextStore(max_segments=workers * per_worker, enable_metrics=True)
    start = Barrier(workers)

    def add_segments(worker):
        start.wait(timeout=5)
        for index in range(per_worker):
            store.add([_segment(f"{worker}-{index}")], session_id="session")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(add_segments, worker) for worker in range(workers)]
        for future in futures:
            future.result(timeout=10)

    expected_ids = {f"{worker}-{index}" for worker in range(workers) for index in range(per_worker)}
    assert {segment.id for segment in store.get("session", limit=100)} == expected_ids
    assert store.get_metrics()["add_count"] == workers * per_worker


def test_concurrent_reads_preserve_access_counts_and_metric_snapshots():
    store = RamContextStore(enable_metrics=True)
    segment = _segment("one")
    store.add([segment], session_id="session")
    workers = 4
    per_worker = 25
    start = Barrier(workers)

    def read_segments():
        start.wait(timeout=5)
        for _ in range(per_worker):
            assert store.get("session") == [segment]
            assert store.search("python", "session") == [segment]
            assert store.get_by_ids("session", [segment.id]) == [segment]
            metrics = store.get_metrics()
            assert metrics["avg_get_time_ms"] == metrics["total_get_time_ms"] / metrics["get_count"]

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(read_segments) for _ in range(workers)]
        for future in futures:
            future.result(timeout=10)

    assert segment.metadata.access_count == workers * per_worker * 3
    metrics = store.get_metrics()
    assert metrics["get_count"] == metrics["search_count"] == workers * per_worker
    metrics["get_count"] = -1
    assert store.get_metrics()["get_count"] == workers * per_worker


def test_concurrent_reads_and_cleanup_preserve_capacity():
    store = RamContextStore(max_segments=5, enable_metrics=True)
    start = Barrier(4)

    def exercise(worker):
        start.wait(timeout=5)
        for index in range(30):
            segment = _segment(f"{worker}-{index}")
            store.add([segment], session_id="session")
            store.get("session")
            store.search("python", "session")
            store.get_by_ids("session", [segment.id])
            assert store.count("session") <= 5
            store.get_all_sessions()
            store.prune("session", min_priority=ContextPriority.HIGH)
            store.delete("session", segment_ids=[segment.id])
            if index % 5 == 0:
                store.clear_all()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(exercise, worker) for worker in range(4)]
        for future in futures:
            future.result(timeout=10)

    assert store.count("session") <= 5
    assert store.get_metrics()["add_count"] == 120


@pytest.mark.parametrize("copy_method", ["create_copy", "model_copy", "deepcopy"])
def test_copy_preserves_isolated_storage_metrics_and_lock(copy_method):
    store = RamContextStore(enable_metrics=True)
    store.add([_segment("one")], session_id="session")
    if copy_method == "deepcopy":
        copied = deepcopy(store)
    elif copy_method == "model_copy":
        copied = store.model_copy(deep=True)
    else:
        copied = store.create_copy()

    assert copied is not store
    assert copied._lock is not store._lock
    assert "_lock" not in copied.model_dump()
    copied.get_by_ids("session", ["one"])[0].metadata.keywords.append("copy-only")
    copied.delete("session")
    assert store.count("session") == 1
    assert store.get_by_ids("session", ["one"])[0].metadata.keywords == []
    assert store.get_metrics()["delete_count"] == 0
    assert copied.get_metrics()["delete_count"] == 1


def test_shallow_copy_shares_the_lock_with_its_shared_storage():
    store = RamContextStore(enable_metrics=True)
    copied = store.model_copy()

    assert copied._lock is store._lock
    assert copied._storage is store._storage
    assert copied._metrics is store._metrics


def test_new_store_instances_have_independent_locks_and_storage():
    first = RamContextStore()
    second = RamContextStore()

    assert first._lock is not second._lock
    first.add([_segment("one")], session_id="session")
    assert second.count("session") == 0


def test_deepcopy_preserves_aliases_between_explicit_shallow_copies():
    store = RamContextStore()
    store.add([_segment("one")], session_id="session")

    first, second = deepcopy([store, store.model_copy()])

    assert first._lock is second._lock
    assert first._storage is second._storage
    assert first._lock is not store._lock
    assert first._storage is not store._storage


def test_batch_add_and_failed_call_do_not_leave_the_lock_held():
    store = RamContextStore()
    with store._lock:
        assert store._lock.acquire(blocking=False), "batch_add requires a reentrant lock"
        store._lock.release()

    with pytest.raises(ValueError, match="session_id is required"):
        store.add([_segment("invalid")])

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(store.batch_add, {"one": [_segment("one")], "two": [_segment("two")]}).result(timeout=5)

    assert set(store.get_all_sessions()) == {"one", "two"}
