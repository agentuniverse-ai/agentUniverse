"""Deadline reports, bounded late calls and deterministic resource cleanup."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any

import pytest

from agentuniverse.agent.action.knowledge.deadline_retrieval import DeadlineRetrievalCoordinator, RetrievalCapacityError
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store


class CallableStore(Store):
    callback: Any = None

    def query(self, query, **kwargs):
        return self.callback(query)


def store(callback):
    return CallableStore(callback=callback)


def test_success_empty_and_error_are_distinct_without_exception_message():
    def fail(query):
        raise RuntimeError("secret-token")
    with DeadlineRetrievalCoordinator({"ok": store(lambda q: [Document(text="ok")]),
                                       "empty": store(lambda q: []), "bad": store(fail)}) as coordinator:
        report = coordinator.query(Query(query_str="q"), budget_seconds=2)
    assert [value.status for value in report.channels.values()] == ["success", "success", "error"]
    assert report.channels["bad"].error_type == "RuntimeError"
    assert "secret-token" not in repr(report)
    assert report.partial and [d.text for d in report.documents] == ["ok"]
    assert coordinator.inflight_count == 0


def test_query_and_returned_documents_are_isolated_and_capped():
    original = Document(text="a", metadata={"nested": [1], "recall_channel": "old"})
    query = Query(query_str="q", keywords={"original"}, ext_info={"nested": [1]})
    def mutate(detached):
        detached.keywords.add("modified")
        detached.ext_info["nested"].append(2)
        return [original, Document(text="trimmed")]
    def inspect(detached):
        assert detached.keywords == {"original"}
        assert detached.ext_info == {"nested": [1]}
        return []
    with DeadlineRetrievalCoordinator({"A": store(mutate), "B": store(inspect)}, max_documents_per_channel=1) as coordinator:
        report = coordinator.query(query, budget_seconds=2)
    assert not report.partial and len(report.documents) == 1
    assert report.documents[0].metadata["recall_channel"] == "A"
    report.documents[0].metadata["nested"].append(3)
    assert original.metadata == {"nested": [1], "recall_channel": "old"}
    assert query.ext_info == {"nested": [1]} and query.keywords == {"original"}


def test_running_timeout_is_tracked_rejects_capacity_and_never_adds_late_result():
    started, release = Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return [Document(text="late")]
    coordinator = DeadlineRetrievalCoordinator({"fast": store(lambda q: [Document(text="fast")]), "slow": store(slow)},
                                                max_workers=2, max_inflight=2)
    try:
        with ThreadPoolExecutor(max_workers=1) as caller:
            pending = caller.submit(coordinator.query, Query(), budget_seconds=0.2)
            assert started.wait(2)
            report = pending.result(timeout=2)
        assert report.channels["fast"].status == "success"
        assert report.channels["slow"].status == "timeout" and report.channels["slow"].still_running
        assert coordinator.inflight_count == 1
        with pytest.raises(RetrievalCapacityError):
            coordinator.query(Query(), budget_seconds=1)
        assert [d.text for d in report.documents] == ["fast"]
        release.set()
        coordinator.close()
        assert coordinator.inflight_count == 0
        assert [d.text for d in report.documents] == ["fast"]
    finally:
        release.set()
        coordinator.close()


def test_queued_timeout_is_cancelled_without_calling_store():
    release, started, queued_called = Event(), Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return []
    def queued(query):
        queued_called.set()
        return []
    coordinator = DeadlineRetrievalCoordinator({"running": store(slow), "queued": store(queued)}, max_workers=1)
    try:
        report = coordinator.query(Query(), budget_seconds=0.2)
        assert started.is_set()
        assert report.channels["queued"].status == "timeout"
        assert not report.channels["queued"].still_running
        release.set()
        coordinator.close()
        assert not queued_called.is_set()
    finally:
        release.set()
        coordinator.close()


def test_nonblocking_close_stops_admission_but_does_not_claim_thread_stopped():
    release, started = Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return []
    coordinator = DeadlineRetrievalCoordinator({"slow": store(slow)}, max_inflight=1)
    try:
        coordinator.query(Query(), budget_seconds=0.2)
        assert started.is_set()
        coordinator.close(wait_for_running=False)
        assert coordinator.inflight_count == 1
        with pytest.raises(RuntimeError, match="closed"):
            coordinator.query(Query(), budget_seconds=1)
        with pytest.raises(RuntimeError, match="closed"):
            coordinator.__enter__()
    finally:
        release.set()
        coordinator.close()
    assert coordinator.inflight_count == 0


def test_zero_budget_does_not_call_provider():
    called = Event()
    with DeadlineRetrievalCoordinator({"A": store(lambda q: called.set())}) as coordinator:
        report = coordinator.query(Query(), budget_seconds=0)
    assert report.channels["A"].status == "timeout"
    assert not called.is_set()


def test_caller_interruption_keeps_running_call_owned(monkeypatch):
    import agentuniverse.agent.action.knowledge.deadline_retrieval as module
    release, started = Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return []
    def interrupted(*args, **kwargs):
        assert started.wait(2)
        raise KeyboardInterrupt()
    coordinator = DeadlineRetrievalCoordinator({"slow": store(slow)}, max_inflight=1)
    try:
        monkeypatch.setattr(module, "wait", interrupted)
        with pytest.raises(KeyboardInterrupt):
            coordinator.query(Query(), budget_seconds=3)
        assert coordinator.inflight_count == 1
    finally:
        release.set()
        coordinator.close()
    assert coordinator.inflight_count == 0


def test_executor_submit_failure_cancels_queued_but_tracks_running(monkeypatch):
    release, started = Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return []
    coordinator = DeadlineRetrievalCoordinator({"A": store(slow), "B": store(lambda q: [])})
    original_submit = coordinator._executor.submit
    calls = []
    def submit(*args):
        calls.append(1)
        if len(calls) == 2:
            assert started.wait(2)
            raise RuntimeError("submit failed")
        return original_submit(*args)
    try:
        monkeypatch.setattr(coordinator._executor, "submit", submit)
        with pytest.raises(RuntimeError, match="submit failed"):
            coordinator.query(Query(), budget_seconds=3)
        assert coordinator.inflight_count == 1
    finally:
        release.set()
        coordinator.close()
    assert coordinator.inflight_count == 0


def test_late_error_is_discarded_and_capacity_released():
    release, started = Event(), Event()
    def slow_failure(query):
        started.set()
        assert release.wait(5)
        raise ValueError("late secret")
    coordinator = DeadlineRetrievalCoordinator({"A": store(slow_failure)})
    try:
        report = coordinator.query(Query(), budget_seconds=0.2)
        assert started.is_set() and report.channels["A"].status == "timeout"
        release.set()
        coordinator.close()
        assert report.channels["A"].error_type is None
        assert "late secret" not in repr(report)
        assert coordinator.inflight_count == 0
    finally:
        release.set()
        coordinator.close()


def test_all_empty_success_is_not_partial():
    with DeadlineRetrievalCoordinator({"A": store(lambda q: []), "B": store(lambda q: [])}) as coordinator:
        report = coordinator.query(Query(), budget_seconds=2)
    assert report.documents == [] and not report.partial


def test_shutdown_cancelled_queue_is_distinct_from_deadline():
    started, release = Event(), Event()
    def slow(query):
        started.set()
        assert release.wait(5)
        return []
    coordinator = DeadlineRetrievalCoordinator({"running": store(slow), "queued": store(lambda q: [])}, max_workers=1)
    try:
        with ThreadPoolExecutor(max_workers=1) as caller:
            pending = caller.submit(coordinator.query, Query(), budget_seconds=0.2)
            assert started.wait(2)
            coordinator.close(wait_for_running=False)
            report = pending.result(timeout=2)
        assert report.channels["queued"].status == "cancelled"
        assert report.channels["running"].status == "timeout"
    finally:
        release.set()
        coordinator.close()


def test_capacity_reusable_after_late_task_finishes(monkeypatch):
    release, drained = Event(), Event()
    def slow(query):
        assert release.wait(5)
        return [Document(text="result")]
    coordinator = DeadlineRetrievalCoordinator({"A": store(slow)}, max_workers=1, max_inflight=1)
    original_release = coordinator._release
    def observe(future):
        original_release(future)
        if coordinator.inflight_count == 0:
            drained.set()
    monkeypatch.setattr(coordinator, "_release", observe)
    try:
        first = coordinator.query(Query(), budget_seconds=0.2)
        assert first.partial and coordinator.inflight_count == 1
        release.set()
        assert drained.wait(2)
        second = coordinator.query(Query(), budget_seconds=2)
        assert not second.partial and second.documents[0].text == "result"
        assert first.documents == []
    finally:
        release.set()
        coordinator.close()


@pytest.mark.parametrize("bad", [None, {}, [object()]])
def test_invalid_store_results_have_explicit_error(bad):
    with DeadlineRetrievalCoordinator({"A": store(lambda q: bad)}) as coordinator:
        report = coordinator.query(Query(), budget_seconds=2)
    assert report.channels["A"].status == "error"
    assert report.channels["A"].error_type == "TypeError"


@pytest.mark.parametrize("budget", [-1, True, float("nan"), float("inf"), "1", 86401])
def test_bad_budget_never_calls_provider(budget):
    called = Event()
    with DeadlineRetrievalCoordinator({"A": store(lambda q: called.set())}) as coordinator:
        with pytest.raises(ValueError):
            coordinator.query(Query(), budget_seconds=budget)
    assert not called.is_set()


@pytest.mark.parametrize("options", [{"max_workers": 0}, {"max_workers": True},
    {"max_inflight": 0}, {"max_documents_per_channel": -1}])
def test_bad_options(options):
    with pytest.raises(ValueError):
        DeadlineRetrievalCoordinator({"A": store(lambda q: [])}, **options)


@pytest.mark.parametrize("stores", [{}, {"": store(lambda q: [])}, {"A": object()}])
def test_invalid_stores(stores):
    with pytest.raises(ValueError):
        DeadlineRetrievalCoordinator(stores)


def test_real_sqlite_query_and_rrf_composition(tmp_path):
    from unittest.mock import patch
    from agentuniverse.agent.action.knowledge.store.sqlite_store import SQLiteStore
    from agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor import JiebaKeywordExtractor
    from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor
    stores = {}
    try:
        with patch("agentuniverse.agent.action.knowledge.store.sqlite_store.DocProcessorManager") as manager:
            manager.return_value.get_instance_obj.return_value = JiebaKeywordExtractor()
            for channel in ("A", "B"):
                instance = SQLiteStore(db_path=str(tmp_path / (channel + ".db")), keyword_extractor="keywords")
                stores[channel] = instance
                instance._new_client()
                instance.insert_document([Document(id="shared", text="alpha manual", metadata={"source": "manual"})])
                instance.conn.close()
                instance._new_client()
            with DeadlineRetrievalCoordinator(stores) as coordinator:
                report = coordinator.query(Query(query_str="alpha", keywords={"alpha"}), budget_seconds=3)
        assert not report.partial
        assert [d.metadata["recall_channel"] for d in report.documents] == ["A", "B"]
        fused = ReciprocalRankFusionProcessor(channel_key="recall_channel").process_docs(report.documents)
        assert len(fused) == 1 and fused[0].id == "shared"
        assert fused[0].metadata["relevance_score"] == pytest.approx(2 / 61)
    finally:
        for instance in stores.values():
            instance.conn.close()
