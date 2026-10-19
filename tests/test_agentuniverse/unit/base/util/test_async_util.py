# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/01/05 10:35
# @Author  : kaichuan
# @FileName: test_async_util.py
"""Unit tests for run_async_from_sync in base.util.async_util."""

import asyncio

import pytest

from agentuniverse.base.util.async_util import run_async_from_sync


def test_run_async_from_sync_returns_exception_objects_as_values():
    expected = ValueError("result payload")

    async def return_exception():
        return expected

    assert run_async_from_sync(return_exception()) is expected


def test_run_async_from_sync_reraises_coroutine_exceptions():
    expected = ValueError("coroutine failed")

    async def fail():
        raise expected

    with pytest.raises(ValueError) as caught:
        run_async_from_sync(fail())

    assert caught.value is expected


def test_run_async_from_sync_propagates_cancellation():
    async def cancel():
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        run_async_from_sync(cancel(), timeout=0.1)
class TestRunAsyncFromSync:
    """Test executing coroutines from a synchronous context."""

    def test_returns_coroutine_result(self):
        """The value returned by the coroutine is returned to the caller."""

        async def add(a, b):
            await asyncio.sleep(0)
            return a + b

        assert run_async_from_sync(add(2, 3)) == 5

    def test_forwards_arguments(self):
        """Positional and keyword arguments reach the coroutine."""

        async def greet(name, punctuation="!"):
            return f"hello {name}{punctuation}"

        assert run_async_from_sync(greet("world", punctuation="?")) == "hello world?"

    def test_none_result(self):
        """A coroutine without a return value yields None."""

        async def noop():
            await asyncio.sleep(0)

        assert run_async_from_sync(noop()) is None

    def test_non_coroutine_raises_type_error(self):
        """Passing a non-coroutine raises TypeError."""
        with pytest.raises(TypeError, match="Expected a coroutine, but got int"):
            run_async_from_sync(42)

    def test_coroutine_exception_reraised(self):
        """Exceptions raised inside the coroutine propagate to the caller."""

        async def boom():
            raise ValueError("inner failure")

        with pytest.raises(ValueError, match="inner failure"):
            run_async_from_sync(boom())

    def test_timeout_raises(self):
        """Exceeding the timeout raises TimeoutError."""

        async def slow():
            await asyncio.sleep(5)

        with pytest.raises(TimeoutError, match="timed out after 0.1 seconds"):
            run_async_from_sync(slow(), timeout=0.1)
