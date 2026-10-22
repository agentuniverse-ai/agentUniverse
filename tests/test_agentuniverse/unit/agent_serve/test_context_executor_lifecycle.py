"""Returned context futures must reflect actual queued/running/terminal state."""

from concurrent.futures import CancelledError, as_completed, wait
from concurrent.futures.thread import BrokenThreadPool
from threading import Event
from unittest.mock import patch

import pytest

from agentuniverse.agent_serve.web import thread_with_result as module
from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


@pytest.fixture
def executor():
    with (
        patch.object(module.ContextCoordinator, "save_context", return_value={}),
        patch.object(module.ContextCoordinator, "recover_context", return_value=None),
    ):
        pool = module.ThreadPoolExecutorWithReturnValue(max_workers=1)
        try:
            yield pool
        finally:
            pool.shutdown(wait=True, cancel_futures=True)


def test_cancelled_queued_task_never_runs(executor):
    release, entered, executed = Event(), Event(), Event()

    def blocker():
        entered.set()
        assert release.wait(3)

    first = executor.submit(blocker)
    try:
        assert entered.wait(2)
        queued = executor.submit(executed.set)
        assert queued.cancel()
    finally:
        release.set()
    first.result(timeout=2)
    executor.shutdown(wait=True)
    assert not executed.is_set()
    with pytest.raises(CancelledError):
        queued.result(timeout=1)


def test_running_future_cannot_be_cancelled(executor):
    release, entered = Event(), Event()

    def work():
        entered.set()
        assert release.wait(3)
        return 42

    future = executor.submit(work)
    try:
        assert entered.wait(2)
        assert future.running()
        assert not future.cancel()
    finally:
        release.set()
    assert future.result(timeout=2) == 42


@pytest.mark.parametrize("cancel_before_shutdown", [False, True])
def test_shutdown_cancellation_reaches_returned_future(executor, cancel_before_shutdown):
    release, entered = Event(), Event()

    def blocker():
        entered.set()
        assert release.wait(3)

    first = executor.submit(blocker)
    try:
        assert entered.wait(2)
        queued = executor.submit(lambda: "must not execute")
        if cancel_before_shutdown:
            assert queued.cancel()
        executor.shutdown(wait=False, cancel_futures=True)
        assert queued.cancelled()
        done, pending = wait([queued], timeout=0.2)
        assert done == {queued}
        assert not pending
        assert list(as_completed([queued], timeout=0.2)) == [queued]
        with pytest.raises(CancelledError):
            queued.result(timeout=0.2)
    finally:
        release.set()
    first.result(timeout=2)


@pytest.mark.parametrize("error", [ValueError("bad"), SystemExit("exit"), KeyboardInterrupt("stop")])
def test_task_errors_complete_the_returned_future(executor, error):
    def fail():
        raise error

    future = executor.submit(fail)
    with pytest.raises(type(error)) as caught:
        future.result(timeout=0.5)
    assert caught.value is error
    assert future.error is error


def test_success_keeps_context_future_and_callback_contract(executor):
    future = executor.submit(lambda: 42)
    assert isinstance(future, module.ContextAwareFuture)
    assert future.result(timeout=2) == 42
    callback_ran = Event()
    future.add_done_callback(lambda finished: callback_ran.set())
    assert callback_ran.wait(1)
    assert future.error is None


def test_context_is_recovered_and_detached_after_failure(executor):
    token = object()

    def fail():
        raise ValueError("failed after context recovery")

    with (
        patch.object(module.ContextCoordinator, "recover_context", return_value=token) as recover,
        patch.object(module.otel_context, "detach") as detach,
    ):
        future = executor.submit(fail)
        with pytest.raises(ValueError, match="failed after context recovery"):
            future.result(timeout=2)
        executor.shutdown(wait=True)
        recover.assert_called_once_with({})
        detach.assert_called_once_with(token)


def test_context_recovery_failure_finishes_future_without_running_task(executor):
    executed = Event()
    with patch.object(module.ContextCoordinator, "recover_context", side_effect=ValueError("bad context")):
        future = executor.submit(executed.set)
        with pytest.raises(ValueError, match="bad context"):
            future.result(timeout=2)
    assert not executed.is_set()


def test_map_preserves_order_and_argument_forwarding(executor):
    assert list(executor.map(lambda x, y: x + y, [3, 1, 2], [30, 10, 20], timeout=2)) == [33, 11, 22]


@pytest.mark.parametrize("cancel_first", [False, True])
def test_failed_initializer_finishes_waiters_without_running_task(cancel_first):
    release, entered, executed = Event(), Event(), Event()

    def initializer():
        entered.set()
        assert release.wait(5)
        raise RuntimeError("initializer failed")

    with patch.object(module.ContextCoordinator, "save_context", return_value={}):
        pool = module.ThreadPoolExecutorWithReturnValue(max_workers=1, initializer=initializer)
        try:
            future = pool.submit(executed.set)
            assert entered.wait(2)
            if cancel_first:
                assert future.cancel()
            release.set()
            pool.shutdown(wait=True)
            done, pending = wait([future], timeout=0.5)
            assert done == {future}
            assert not pending
            with pytest.raises(CancelledError if cancel_first else BrokenThreadPool):
                future.result(timeout=0.5)
            if not cancel_first:
                assert future.exception() is future.error
            assert not executed.is_set()
        finally:
            release.set()
            pool.shutdown(wait=True, cancel_futures=True)


def test_success_preserves_captured_context_and_keyword_arguments(executor):
    pack = {"request": "captured"}
    token = object()
    with (
        patch.object(module.ContextCoordinator, "save_context", return_value=pack),
        patch.object(module.ContextCoordinator, "recover_context", return_value=token) as recover,
        patch.object(module.otel_context, "detach") as detach,
    ):
        future = executor.submit(lambda x, *, y: x + y, 20, y=22)
        assert future.result(timeout=2) == 42
        executor.shutdown(wait=True)
        assert future._context_pack is pack
        recover.assert_called_once_with(pack)
        detach.assert_called_once_with(token)


def test_cancelled_task_does_not_recover_context(executor):
    release, entered = Event(), Event()

    def blocker():
        entered.set()
        assert release.wait(5)

    first = executor.submit(blocker)
    try:
        assert entered.wait(2)
        with patch.object(module.ContextCoordinator, "recover_context") as recover:
            queued = executor.submit(lambda: None)
            calls = []
            queued.add_done_callback(lambda finished: calls.append(finished))
            assert queued.cancel()
            assert queued.cancel()
            release.set()
            executor.shutdown(wait=True)
            recover.assert_not_called()
            assert calls == [queued]
            assert wait([queued], timeout=0.5).done == {queued}
    finally:
        release.set()
    first.result(timeout=2)


def test_submit_after_shutdown_raises_immediately(executor):
    executor.shutdown(wait=True)
    with pytest.raises(RuntimeError, match="shutdown"):
        executor.submit(lambda: None)


def test_real_framework_and_otel_context_follow_each_submission():
    manager = FrameworkContextManager()
    key = module.otel_context.create_key("executor-lifecycle-test")

    def read_context():
        return manager.get_context("executor_lifecycle_request"), module.otel_context.get_value(key)

    with module.ThreadPoolExecutorWithReturnValue(max_workers=1) as pool:
        for value in ("first", "second"):
            token = module.otel_context.attach(module.otel_context.set_value(key, value))
            try:
                with FrameworkContext({"executor_lifecycle_request": value}):
                    assert pool.submit(read_context).result(timeout=2) == (value, value)
                    assert read_context() == (value, value)
            finally:
                module.otel_context.detach(token)
