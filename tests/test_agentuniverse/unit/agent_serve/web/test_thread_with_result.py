from threading import Event

from agentuniverse.agent_serve.web.thread_with_result import (
    ThreadPoolExecutorWithReturnValue,
)


def test_cancelled_queued_future_does_not_run_callable():
    first_started = Event()
    release_first = Event()
    second_ran = Event()

    def block_worker():
        first_started.set()
        release_first.wait(timeout=2)

    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        first = executor.submit(block_worker)
        assert first_started.wait(timeout=2)

        second = executor.submit(second_ran.set)
        assert second.cancel()
        release_first.set()

        first.result(timeout=2)

    assert second.cancelled()
    assert not second_ran.is_set()


def test_running_future_cannot_be_cancelled():
    started = Event()
    release = Event()

    def wait_for_release():
        started.set()
        release.wait(timeout=2)
        return "done"

    with ThreadPoolExecutorWithReturnValue(max_workers=1) as executor:
        future = executor.submit(wait_for_release)
        assert started.wait(timeout=2)
        assert not future.cancel()
        release.set()
        assert future.result(timeout=2) == "done"
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/09/02
# @FileName: test_thread_with_result.py

"""Unit tests for thread/future helpers that return values."""

import time

import pytest

from agentuniverse.agent_serve.web.thread_with_result import (
    ThreadPoolExecutorWithReturnValue,
    ThreadWithReturnValue,
)


def add(a, b):
    return a + b


def boom():
    raise ValueError("thread error")


class TestThreadWithReturnValue:
    """Test ThreadWithReturnValue result capture and error re-raising."""

    def test_returns_target_result(self):
        thread = ThreadWithReturnValue(target=add, args=(2, 3))
        thread.start()
        assert thread.result() == 5

    def test_raises_target_error(self):
        thread = ThreadWithReturnValue(target=boom)
        thread.start()
        with pytest.raises(ValueError, match="thread error"):
            thread.result()

    def test_no_target_returns_none(self):
        thread = ThreadWithReturnValue()
        thread.start()
        assert thread.result() is None


class TestThreadPoolExecutorWithReturnValue:
    """Test executor submit/map return values and error propagation."""

    def test_submit_returns_future_with_result(self):
        with ThreadPoolExecutorWithReturnValue() as executor:
            future = executor.submit(add, 4, 5)
            assert future.result(timeout=5) == 9

    def test_submit_propagates_exception(self):
        with ThreadPoolExecutorWithReturnValue() as executor:
            future = executor.submit(boom)
            with pytest.raises(ValueError, match="thread error"):
                future.result(timeout=5)

    def test_map_applies_function(self):
        with ThreadPoolExecutorWithReturnValue() as executor:
            assert list(executor.map(add, [1, 2, 3], [10, 20, 30])) == \
                [11, 22, 33]

    def test_submit_returns_context_aware_future(self):
        with ThreadPoolExecutorWithReturnValue() as executor:
            future = executor.submit(lambda: "x")
            assert future.result(timeout=5) == "x"
