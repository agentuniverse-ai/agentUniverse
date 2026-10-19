# -*- coding: utf-8 -*-
"""Unit tests for agentuniverse.base.util.async_util."""

import queue

import pytest

from agentuniverse.base.util.async_util import (
    _async_runner_thread_target,
    run_async_from_sync,
)


class TestAsyncRunnerThreadTarget:
    """Tests for the internal _async_runner_thread_target helper."""

    def test_put_result_into_queue(self):
        async def compute():
            return 42

        result_queue = queue.Queue(maxsize=1)
        _async_runner_thread_target(compute(), result_queue)
        assert result_queue.get_nowait() == 42

    def test_put_exception_into_queue(self):
        async def explode():
            raise ValueError("boom")

        result_queue = queue.Queue(maxsize=1)
        _async_runner_thread_target(explode(), result_queue)
        exc = result_queue.get_nowait()
        assert isinstance(exc, ValueError)
        assert str(exc) == "boom"

    def test_put_none_result_into_queue(self):
        async def do_nothing():
            return None

        result_queue = queue.Queue(maxsize=1)
        _async_runner_thread_target(do_nothing(), result_queue)
        assert result_queue.get_nowait() is None


class TestRunAsyncFromSync:
    """Tests for the run_async_from_sync bridge function."""

    def test_return_value(self):
        async def add(a, b):
            return a + b

        assert run_async_from_sync(add(3, 5)) == 8

    def test_return_string(self):
        async def greet(name):
            return "hello " + name

        assert run_async_from_sync(greet("world")) == "hello world"

    def test_return_none(self):
        async def no_result():
            return None

        assert run_async_from_sync(no_result()) is None

    def test_raise_type_error_for_non_coroutine(self):
        def not_a_coroutine():
            return 1

        with pytest.raises(TypeError):
            run_async_from_sync(not_a_coroutine)

    def test_re_raise_coroutine_exception(self):
        async def fail():
            raise RuntimeError("failed")

        with pytest.raises(RuntimeError, match="failed"):
            run_async_from_sync(fail())

    def test_accepts_explicit_timeout(self):
        async def value():
            return 1

        assert run_async_from_sync(value(), timeout=5) == 1
