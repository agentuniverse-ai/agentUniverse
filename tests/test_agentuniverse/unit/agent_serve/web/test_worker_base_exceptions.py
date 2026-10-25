"""Verify failure transport through actual threads and context-aware executors."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from threading import Event

from opentelemetry import context as otel_context
import pytest

from agentuniverse.agent_serve.web.thread_with_result import (
    ThreadPoolExecutorWithReturnValue, ThreadWithReturnValue,
)
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager


@contextmanager
def worker_result(kind, target):
    """Run a real worker and yield a bounded result accessor and worker handle."""
    if kind == 'thread':
        thread = ThreadWithReturnValue(target=target)
        thread.start()
        try:
            thread.join(timeout=2)
            assert not thread.is_alive(), 'worker did not finish'
            yield thread.result, thread
        finally:
            thread.join(timeout=2)
    else:
        with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
            future = executor.submit(target)
            yield lambda: future.result(timeout=1), future


@pytest.fixture
def worker_context():
    """Provide a real framework context and restore the caller after testing."""
    manager = FrameworkContextManager()
    previous = manager.get_all_contexts()
    manager.clear_all_contexts()
    manager.set_context('worker_failure_test', 'parent context')
    try:
        yield manager
    finally:
        manager.clear_all_contexts()
        manager.set_all_contexts(previous)


@pytest.mark.parametrize('kind', ['thread', 'pool'])
@pytest.mark.parametrize('failure_type', [
    asyncio.CancelledError, SystemExit, KeyboardInterrupt, BaseException,
])
def test_target_base_exception_reaches_result_with_identity(kind, failure_type, worker_context):
    """Cancellation/exit failures reach the caller rather than disappearing."""
    manager = worker_context
    failure = failure_type('target failure')
    seen_context = []

    def target():
        seen_context.append(manager.get_context('worker_failure_test'))
        raise failure

    with worker_result(kind, target) as (result, worker):
        with pytest.raises(failure_type) as raised:
            result()
        assert raised.value is failure
        assert worker.error is failure
        if kind == 'pool':
            assert worker.done()
            assert worker.exception(timeout=0) is failure
    assert seen_context == ['parent context']


@pytest.mark.parametrize('kind', ['thread', 'pool'])
def test_ordinary_exception_propagation_is_preserved(kind, worker_context):
    """Ordinary target exceptions retain their object identity."""
    failure = ValueError('ordinary failure')

    def target():
        raise failure

    with worker_result(kind, target) as (result, worker):
        with pytest.raises(ValueError) as raised:
            result()
        assert raised.value is failure
        assert worker.error is failure


@pytest.mark.parametrize('kind', ['thread', 'pool'])
@pytest.mark.parametrize('value', [None, {'answer': 42}])
def test_successful_results_and_context_are_preserved(kind, value, worker_context):
    """Successful values and captured framework variables still arrive intact."""
    manager = worker_context

    def target():
        return value, manager.get_context('worker_failure_test')

    with worker_result(kind, target) as (result, worker):
        returned, context = result()
        assert returned is value
        assert context == 'parent context'
        assert worker.error is None


@pytest.mark.parametrize('kind', ['thread', 'pool'])
def test_exception_returned_as_a_value_is_not_raised(kind, worker_context):
    """Returning an exception object is distinct from raising it."""
    value = ValueError('ordinary return value')
    with worker_result(kind, lambda: value) as (result, worker):
        assert result() is value
        assert worker.error is None


@pytest.mark.parametrize('failure_type', [
    asyncio.CancelledError, SystemExit, KeyboardInterrupt, BaseException,
])
def test_done_callback_failure_is_not_reported_as_target_failure(failure_type, worker_context):
    """A successful target keeps its result/error state if a done callback exits."""
    release = Event()
    callback_failure = failure_type('done callback failure')
    callbacks = []
    context_key = otel_context.create_key('worker_callback_test')
    parent_token = otel_context.attach(otel_context.set_value(context_key, 'parent'))

    def target():
        assert release.wait(timeout=2), 'target was not released'
        return 'successful result'

    def callback(future):
        callbacks.append((future.result(), otel_context.get_value(context_key)))
        raise callback_failure

    try:
        with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
            future = executor.submit(target)
            try:
                future.add_done_callback(callback)
            finally:
                release.set()
            assert future.result(timeout=2) == 'successful result'
            # Observe the same worker without installing another task context.
            observer = ThreadPoolExecutor.submit(
                executor, lambda: otel_context.get_value(context_key))
            assert observer.result(timeout=2) is None
    finally:
        otel_context.detach(parent_token)
    # shutdown(wait=True) ensures callback processing and the wrapper finished.
    assert callbacks == [('successful result', 'parent')]
    assert future.exception(timeout=0) is None
    assert future.error is None
