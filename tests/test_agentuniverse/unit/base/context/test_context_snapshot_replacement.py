"""Framework snapshots replace task state when worker threads are reused."""

import asyncio
from contextlib import AsyncExitStack, contextmanager
from contextvars import Context, copy_context
from threading import get_ident

import pytest
from opentelemetry import context as otel_context

from agentuniverse.agent_serve.web.thread_with_result import (
    ThreadPoolExecutorWithReturnValue,
    ThreadWithReturnValue,
)
from agentuniverse.base.context.context_coordinator import ContextCoordinator
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.context.mcp_session_manager import MCPSessionManager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager


@pytest.fixture(autouse=True)
def clean_context():
    """Keep real manager state isolated without opening MCP connections."""
    manager = FrameworkContextManager()
    trace_manager = AuTraceManager()
    trace = trace_manager.context_instance.get(None)
    mcp_session = MCPSessionManager().save_mcp_session()
    manager.clear_all_contexts()
    try:
        yield manager
    finally:
        manager.clear_all_contexts()
        trace_manager.recover_trace(trace)
        MCPSessionManager().recover_mcp_session(**mcp_session)


def snapshot(values):
    """Capture a real coordinator snapshot in an independent context."""
    def capture():
        FrameworkContextManager().set_all_contexts(values)
        return ContextCoordinator.save_context()

    return Context().run(capture)


@contextmanager
def recovered(pack):
    """Balance any real OTEL attachment made by the coordinator."""
    token = ContextCoordinator.recover_context(pack)
    try:
        yield
    finally:
        if token is not None:
            otel_context.detach(token)


@pytest.mark.parametrize("values", [{}, {"request": "next"}])
def test_recovery_removes_keys_absent_from_snapshot(clean_context, values):
    manager = clean_context
    pack = snapshot(values)
    manager.set_context("obsolete", "previous request")

    with recovered(pack):
        assert manager.get_all_contexts() == values
        assert not manager.is_context_exist("obsolete")
        assert manager.get_context("obsolete", "absent") == "absent"


def test_recovery_removes_old_log_context(clean_context):
    manager = clean_context
    pack = snapshot({"request": "next"})
    manager.set_log_context("request_id", "previous")

    with recovered(pack):
        assert manager.get_context("LOG_CONTEXT") is None
        assert manager.get_all_contexts() == {"request": "next"}


def test_recovery_preserves_falsy_snapshot_values(clean_context):
    values = {"none": None, "false": False, "zero": 0, "text": "",
              "list": [], "mapping": {}}
    pack = snapshot(values)
    clean_context.set_context("obsolete", "previous")

    with recovered(pack):
        assert clean_context.get_all_contexts() == values


def test_recovery_preserves_tokens_for_retained_names(clean_context):
    manager = clean_context
    pack = snapshot({"shared": "snapshot"})
    manager.set_context("shared", "outer")
    token = manager.set_context("shared", "inner")
    manager.set_context("obsolete", "previous")

    with recovered(pack):
        assert manager.get_context("shared") == "snapshot"
        manager.reset_context("shared", token)
        assert manager.get_context("shared") == "outer"
        assert not manager.is_context_exist("obsolete")


def test_recovery_does_not_mutate_parent_registry(clean_context):
    manager = clean_context
    pack = snapshot({"child": "new"})
    manager.set_context("parent", "retained")
    child = copy_context()

    def restore_child():
        with recovered(pack):
            return manager.get_all_contexts()

    assert child.run(restore_child) == {"child": "new"}
    assert manager.get_all_contexts() == {"parent": "retained"}
    assert not manager.is_context_exist("child")


def test_recovery_isolates_async_siblings(clean_context):
    manager = clean_context
    packs = [snapshot({"first": "one"}), snapshot({"second": "two"})]
    manager.set_context("parent", "retained")

    async def run_siblings():
        ready = asyncio.Event()
        count = 0

        async def worker(pack):
            nonlocal count
            with recovered(pack):
                count += 1
                if count == 2:
                    ready.set()
                await asyncio.wait_for(ready.wait(), timeout=3)
                return manager.get_all_contexts()

        return await asyncio.gather(*(worker(pack) for pack in packs))

    assert asyncio.run(run_siblings()) == [{"first": "one"}, {"second": "two"}]
    assert manager.get_all_contexts() == {"parent": "retained"}


def worker_state():
    """Return the actual worker identity and complete framework snapshot."""
    return get_ident(), FrameworkContextManager().get_all_contexts()


def test_reused_executor_drops_cleared_caller_state(clean_context):
    manager = clean_context
    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        manager.set_context("request", "first")
        first_id, first = executor.submit(worker_state).result(timeout=3)
        manager.clear_all_contexts()
        second_id, second = executor.submit(worker_state).result(timeout=3)

    assert first == {"request": "first"}
    assert first_id == second_id
    assert second == {}


def test_reused_executor_replaces_nonoverlapping_requests(clean_context):
    manager = clean_context
    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        manager.set_context("first", "one")
        first_id, first = executor.submit(worker_state).result(timeout=3)
        manager.clear_all_contexts()
        manager.set_context("second", "two")
        second_id, second = executor.submit(worker_state).result(timeout=3)

    assert first == {"first": "one"}
    assert first_id == second_id
    assert second == {"second": "two"}


def test_reused_executor_drops_state_created_by_failed_task(clean_context):
    manager = clean_context
    manager.set_context("caller", "same")

    def fail():
        manager.set_context("worker_only", "failed request")
        raise ValueError("task failed")

    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        with pytest.raises(ValueError, match="task failed"):
            executor.submit(fail).result(timeout=3)
        _, second = executor.submit(worker_state).result(timeout=3)

    assert second == {"caller": "same"}


def test_reused_executor_map_drops_previous_request(clean_context):
    manager = clean_context
    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        manager.set_context("request", "first")
        first_id, _ = executor.submit(worker_state).result(timeout=3)
        manager.clear_all_contexts()
        states = list(executor.map(lambda _: worker_state(), range(3), timeout=5))

    assert states == [(first_id, {}), (first_id, {}), (first_id, {})]


def test_direct_thread_still_uses_construction_time_snapshot(clean_context):
    manager = clean_context
    manager.set_context("request", "captured")
    thread = ThreadWithReturnValue(target=worker_state)
    manager.clear_all_contexts()
    manager.set_context("later", "caller")
    thread.start()
    thread.join(timeout=3)
    assert not thread.is_alive()
    _, values = thread.result()
    assert values == {"request": "captured"}
    assert manager.get_all_contexts() == {"later": "caller"}


def test_default_set_all_contexts_still_merges_and_returns_tokens(clean_context):
    manager = clean_context
    manager.set_context("untouched", "retained")
    manager.set_context("shared", "before")
    tokens = manager.set_all_contexts({"shared": "after", "added": "new"})

    assert manager.get_all_contexts() == {
        "untouched": "retained", "shared": "after", "added": "new"}
    for name, token in tokens.items():
        manager.reset_context(name, token)
    assert manager.get_context("shared") == "before"
    assert manager.get_context("added") is None
    assert manager.get_context("untouched") == "retained"


def test_replace_set_all_contexts_returns_usable_tokens(clean_context):
    manager = clean_context
    manager.set_context("shared", "before")
    manager.set_context("obsolete", "previous")
    tokens = manager.set_all_contexts({"shared": "after", "added": "new"},
                                      replace=True)

    assert manager.get_all_contexts() == {"shared": "after", "added": "new"}
    for name, token in tokens.items():
        manager.reset_context(name, token)
    assert manager.get_context("shared") == "before"
    assert manager.get_context("added") is None
    assert not manager.is_context_exist("obsolete")


def test_recovery_still_restores_native_trace_mcp_and_otel(clean_context):
    manager = clean_context
    trace_manager = AuTraceManager()
    mcp_manager = MCPSessionManager()
    trace_manager.set_session_id("captured-session")
    captured_trace = trace_manager.trace_context
    stack = AsyncExitStack()
    sessions = {}
    mcp_manager.recover_mcp_session(sessions, stack)
    key = otel_context.create_key("snapshot-replacement-test")
    source_token = otel_context.attach(otel_context.set_value(key, "captured"))
    try:
        pack = ContextCoordinator.save_context()
    finally:
        otel_context.detach(source_token)

    trace_manager.reset_trace()
    mcp_manager.recover_mcp_session(None, None)
    manager.set_context("obsolete", "previous")
    try:
        with recovered(pack):
            assert trace_manager.trace_context is captured_trace
            assert trace_manager.get_session_id() == "captured-session"
            state = mcp_manager.save_mcp_session()
            assert state["mcp_session_dict"] is sessions
            assert state["exit_stack"] is stack
            assert otel_context.get_value(key) == "captured"
            assert manager.get_all_contexts() == {}
        assert otel_context.get_value(key) is None
    finally:
        asyncio.run(stack.aclose())
