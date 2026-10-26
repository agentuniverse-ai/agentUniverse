"""Regression coverage for values and failures crossing the sync bridge."""

import asyncio

import pytest

from agentuniverse.base.util.async_util import run_async_from_sync


@pytest.mark.parametrize("value", [ValueError("result data"), None,
                                   (False, ValueError("nested data"))])
def test_returns_coroutine_value_unchanged(value):
    async def return_value():
        return value

    assert run_async_from_sync(return_value(), timeout=1) is value


def test_reraises_coroutine_failure_unchanged():
    failure = ValueError("execution failed")

    async def fail():
        raise failure

    with pytest.raises(ValueError) as caught:
        run_async_from_sync(fail(), timeout=1)

    assert caught.value is failure


def test_reraises_coroutine_cancellation():
    async def cancel():
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        run_async_from_sync(cancel(), timeout=0.1)
