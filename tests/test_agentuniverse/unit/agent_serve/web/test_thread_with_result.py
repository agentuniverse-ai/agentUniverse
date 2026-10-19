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
