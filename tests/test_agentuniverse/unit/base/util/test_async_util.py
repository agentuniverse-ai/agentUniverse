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
