# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Regression tests for the context-aware thread helpers.

`ThreadPoolExecutorWithReturnValue.submit()` returns a `ContextAwareFuture`
that it builds itself, in front of the future returned by
`ThreadPoolExecutor.submit()`. The two used to disagree about state: `cancel()`
went to the front object only, so it reported success while the underlying
callable kept running. A caller that cancels to avoid a side effect was told the
side effect had been prevented when it had not.
"""

import threading
import time
import unittest

from agentuniverse.agent_serve.web.thread_with_result import (
    ContextAwareFuture,
    ThreadPoolExecutorWithReturnValue,
    ThreadWithReturnValue,
)


class ThreadWithReturnValueTest(unittest.TestCase):
    """The plain thread wrapper, which was already correct."""

    def test_it_returns_the_target_result(self):
        thread = ThreadWithReturnValue(target=lambda a, b: a + b, args=(1, 2))
        thread.start()

        self.assertEqual(thread.result(), 3)

    def test_a_target_without_arguments_works(self):
        thread = ThreadWithReturnValue(target=lambda: "no-args")
        thread.start()

        self.assertEqual(thread.result(), "no-args")

    def test_keyword_arguments_are_forwarded(self):
        thread = ThreadWithReturnValue(target=lambda a, b=0: a - b, args=(10,), kwargs={"b": 4})
        thread.start()

        self.assertEqual(thread.result(), 6)

    def test_an_exception_is_re_raised_by_result(self):
        def boom():
            raise ValueError("inner failure")

        thread = ThreadWithReturnValue(target=boom)
        thread.start()

        with self.assertRaises(ValueError):
            thread.result()

    def test_a_thread_without_target_returns_none(self):
        thread = ThreadWithReturnValue()
        thread.start()

        self.assertIsNone(thread.result())


class ContextAwareFutureTest(unittest.TestCase):
    """The submit path: state has to reflect the work that actually runs."""

    def setUp(self):
        self.executor = ThreadPoolExecutorWithReturnValue(max_workers=1)

    def tearDown(self):
        self.executor.shutdown(wait=True)

    def test_submit_returns_a_context_aware_future(self):
        future = self.executor.submit(lambda: 42)

        self.assertIsInstance(future, ContextAwareFuture)
        self.assertEqual(future.result(), 42)

    def test_a_completed_future_reports_done_and_not_cancelled(self):
        future = self.executor.submit(lambda: "x")
        future.result()

        self.assertTrue(future.done())
        self.assertFalse(future.cancelled())

    def test_cancel_on_a_queued_task_prevents_it_from_running(self):
        """The regression: `cancel()` used to return True while the work ran.

        A first task occupies the single worker so the second stays queued and
        is genuinely cancellable, which is what the standard executor offers.
        """
        started = []
        release = threading.Event()

        def blocker():
            started.append("blocker")
            release.wait(timeout=2)

        def side_effect():
            started.append("side_effect")

        self.executor.submit(blocker)
        while "blocker" not in started:
            time.sleep(0.01)

        future = self.executor.submit(side_effect)
        cancelled = future.cancel()

        release.set()
        self.executor.shutdown(wait=True)

        self.assertTrue(cancelled)
        self.assertTrue(future.cancelled())
        self.assertNotIn("side_effect", started)

    def test_cancel_reports_false_once_the_task_has_started(self):
        """Matches `concurrent.futures`: a running task cannot be cancelled."""
        started = threading.Event()
        release = threading.Event()

        def work():
            started.set()
            release.wait(timeout=2)

        future = self.executor.submit(work)
        started.wait(timeout=2)

        cancelled = future.cancel()

        release.set()
        self.executor.shutdown(wait=True)

        self.assertFalse(cancelled)

    def test_an_exception_sets_both_the_future_and_the_error_attribute(self):
        def boom():
            raise ValueError("inner failure")

        future = self.executor.submit(boom)

        with self.assertRaises(ValueError):
            future.result()
        self.assertIsInstance(future.error, ValueError)
        self.assertTrue(future.done())

    def test_map_still_works(self):
        results = list(ThreadPoolExecutorWithReturnValue(max_workers=2).map(lambda x: x * 2, [1, 2, 3]))

        self.assertEqual(results, [2, 4, 6])


if __name__ == "__main__":
    unittest.main()
