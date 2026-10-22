import asyncio
import threading
import time

import pytest

from agentuniverse.base.util.async_util import run_async_from_sync


def test_timeout_cancels_worker_coroutine_before_returning():
    cancelled = threading.Event()

    async def wait_forever():
        try:
            await asyncio.sleep(60)
        finally:
            cancelled.set()

    started_at = time.monotonic()
    with pytest.raises(TimeoutError):
        run_async_from_sync(wait_forever(), timeout=0.01)

    assert cancelled.wait(0.2)
    assert time.monotonic() - started_at < 0.5
