"""Cancellation must reach the synchronous caller of the async bridge."""

import asyncio
import unittest

from agentuniverse.base.util.async_util import run_async_from_sync


class AsyncCancellationTests(unittest.TestCase):
    def test_cancelled_task_reaches_caller(self):
        async def cancel_self():
            asyncio.current_task().cancel()
            await asyncio.sleep(0)

        # Bound the regression: the old worker exits without publishing a result.
        with self.assertRaises(asyncio.CancelledError):
            run_async_from_sync(cancel_self(), timeout=0.5)

    def test_explicit_cancellation_preserves_message(self):
        async def cancel():
            raise asyncio.CancelledError("request cancelled")

        with self.assertRaisesRegex(asyncio.CancelledError, "request cancelled"):
            run_async_from_sync(cancel(), timeout=0.5)

    def test_regular_result_and_exception(self):
        async def value():
            return 42

        async def fail():
            raise ValueError("invalid request")

        self.assertEqual(run_async_from_sync(value(), timeout=0.5), 42)
        with self.assertRaisesRegex(ValueError, "invalid request"):
            run_async_from_sync(fail(), timeout=0.5)


if __name__ == "__main__":
    unittest.main()
