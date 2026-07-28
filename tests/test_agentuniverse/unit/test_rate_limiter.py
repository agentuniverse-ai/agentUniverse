# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/12 00:55
# @Author  : Cursor Agent
# @FileName: test_rate_limiter.py
"""
Unit tests for the rate limiter module.
These tests can run standalone without requiring the full agentuniverse package.
"""
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest import TestCase


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

try:
    from agentuniverse.base.util.rate_limiter import (
        RateLimiter,
        ThreadRateLimiter,
        AsyncRateLimiter,
        rate_limited,
        rate_limited_async,
        AgentConcurrencyManager,
        AgentConcurrencyConfig,
        ConcurrencyStrategy,
        ConcurrencyContext,
    )
except ImportError:
    from rate_limiter import (
        RateLimiter,
        ThreadRateLimiter,
        AsyncRateLimiter,
        rate_limited,
        rate_limited_async,
    )
    from agent_concurrency_controller import (
        AgentConcurrencyManager,
        AgentConcurrencyConfig,
        ConcurrencyStrategy,
        ConcurrencyContext,
    )


class TestThreadRateLimiter(TestCase):
    """Test cases for ThreadRateLimiter."""

    def test_basic_acquire_release(self):
        """Test basic acquire and release operations."""
        limiter = ThreadRateLimiter(max_concurrent=2)

        result1 = limiter.acquire()
        self.assertTrue(result1)
        self.assertEqual(limiter.current_concurrent, 1)

        result2 = limiter.acquire()
        self.assertTrue(result2)
        self.assertEqual(limiter.current_concurrent, 2)

        result3 = limiter.acquire()
        self.assertFalse(result3)

        limiter.release()
        self.assertEqual(limiter.current_concurrent, 1)

        result4 = limiter.acquire()
        self.assertTrue(result4)

    def test_context_manager(self):
        """Test the context manager functionality."""
        limiter = ThreadRateLimiter(max_concurrent=1)

        with limiter.limit():
            self.assertEqual(limiter.current_concurrent, 1)

        self.assertEqual(limiter.current_concurrent, 0)

    def test_context_manager_rejection(self):
        """Test context manager raises exception when limit exceeded."""
        limiter = ThreadRateLimiter(max_concurrent=1, timeout=0.1)

        limiter.acquire()

        with self.assertRaises(RuntimeError) as context:
            with limiter.limit():
                pass

        self.assertIn("Rate limit exceeded", str(context.exception))

    def test_stats_tracking(self):
        """Test statistics tracking."""
        limiter = ThreadRateLimiter(max_concurrent=2)

        for _ in range(3):
            limiter.acquire()
            limiter.release()

        self.assertEqual(limiter.total_acquired, 3)
        self.assertEqual(limiter.total_rejected, 0)

    def test_rejection_rate(self):
        """Test rejection rate calculation."""
        limiter = ThreadRateLimiter(max_concurrent=1)

        limiter.acquire()
        limiter.acquire()
        limiter.acquire()

        self.assertEqual(limiter.total_acquired, 1)
        self.assertEqual(limiter.total_rejected, 2)
        self.assertAlmostEqual(limiter.rejection_rate, 0.666, places=2)

    def test_concurrent_acquisitions(self):
        """Test concurrent acquisitions."""
        limiter = ThreadRateLimiter(max_concurrent=3)
        results = []
        lock = threading.Lock()

        def worker():
            if limiter.acquire():
                with lock:
                    results.append('acquired')
                time.sleep(0.05)
                limiter.release()
            else:
                with lock:
                    results.append('rejected')

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        acquired_count = results.count('acquired')
        rejected_count = results.count('rejected')

        self.assertEqual(acquired_count, 3)
        self.assertEqual(rejected_count, 7)

    def test_timeout(self):
        """Test timeout functionality."""
        limiter = ThreadRateLimiter(max_concurrent=1, timeout=0.1)

        limiter.acquire()

        start = time.time()
        result = limiter.acquire()
        elapsed = time.time() - start

        self.assertFalse(result)
        self.assertLess(elapsed, 0.2)


class TestAsyncRateLimiter(TestCase):
    """Test cases for AsyncRateLimiter."""

    def test_async_acquire_release(self):
        """Test async acquire and release."""
        limiter = AsyncRateLimiter(max_concurrent=2)

        async def test():
            result = await limiter.acquire_async()
            self.assertTrue(result)
            self.assertEqual(limiter.current_concurrent, 1)

            result = await limiter.acquire_async()
            self.assertTrue(result)
            self.assertEqual(limiter.current_concurrent, 2)

            result = await limiter.acquire_async()
            self.assertFalse(result)

            await limiter.release_async()
            await limiter.release_async()

        asyncio.run(test())

    def test_async_context_manager(self):
        """Test async context manager."""
        limiter = AsyncRateLimiter(max_concurrent=1)

        async def test():
            async with limiter.limit_async():
                self.assertEqual(limiter.current_concurrent, 1)

            self.assertEqual(limiter.current_concurrent, 0)

        asyncio.run(test())


class TestRateLimitedDecorator(TestCase):
    """Test cases for rate limited decorators."""

    def test_sync_decorator(self):
        """Test synchronous rate limited decorator."""
        execution_count = [0]
        lock = threading.Lock()

        @rate_limited(max_concurrent=2)
        def rate_limited_func():
            with lock:
                execution_count[0] += 1
            time.sleep(0.05)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(rate_limited_func) for _ in range(5)]
            for future in as_completed(futures):
                try:
                    future.result()
                except RuntimeError:
                    pass

        self.assertGreaterEqual(execution_count[0], 2)


class TestAgentConcurrencyManager(TestCase):
    """Test cases for AgentConcurrencyManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AgentConcurrencyManager()

    def tearDown(self):
        """Clean up after tests."""
        self.manager._controller._agent_limiters.clear()
        self.manager._controller._agent_configs.clear()
        self.manager._controller._active_executions.clear()
        self.manager._controller._global_limiter = None

    def test_register_agent(self):
        """Test agent registration."""
        config = AgentConcurrencyConfig(max_concurrent=3)
        self.manager.register_agent("test_agent", config)

        stats = self.manager.controller.get_agent_stats("test_agent")
        self.assertTrue(stats['enabled'])
        self.assertEqual(stats['max_concurrent'], 3)

    def test_acquire_release_permit(self):
        """Test acquiring and releasing permits."""
        config = AgentConcurrencyConfig(max_concurrent=2, enabled=True)
        self.manager.register_agent("test_agent", config)

        acquired, exec_id = self.manager.acquire_permit("test_agent")
        self.assertTrue(acquired)
        self.assertIsNotNone(exec_id)

        acquired2, exec_id2 = self.manager.acquire_permit("test_agent")
        self.assertTrue(acquired2)

        acquired3, _ = self.manager.acquire_permit("test_agent")
        self.assertFalse(acquired3)

        self.manager.release_permit(exec_id)
        self.manager.release_permit(exec_id2)

        acquired4, _ = self.manager.acquire_permit("test_agent")
        self.assertTrue(acquired4)
        self.manager.release_permit(acquired4)

    def test_global_limit(self):
        """Test global concurrency limit."""
        self.manager.set_global_limit(max_concurrent=2)

        limiter = self.manager.controller._global_limiter
        self.assertTrue(limiter.acquire())
        self.assertTrue(limiter.acquire())
        self.assertFalse(limiter.acquire())

        limiter.release()
        limiter.release()

    def test_unregister_agent(self):
        """Test agent unregistration."""
        config = AgentConcurrencyConfig(max_concurrent=3)
        self.manager.register_agent("test_agent", config)

        self.manager.unregister_agent("test_agent")

        stats = self.manager.controller.get_agent_stats("test_agent")
        self.assertFalse(stats['enabled'])

    def test_stats(self):
        """Test statistics collection."""
        config = AgentConcurrencyConfig(max_concurrent=5)
        self.manager.register_agent("stats_agent", config)

        for _ in range(10):
            acquired, exec_id = self.manager.acquire_permit("stats_agent")
            if acquired:
                self.manager.release_permit(exec_id)

        stats = self.manager.get_stats()
        self.assertIn('total_executions', stats)
        self.assertIn('total_rejections', stats)


class TestConcurrencyContext(TestCase):
    """Test cases for ConcurrencyContext."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AgentConcurrencyManager()
        config = AgentConcurrencyConfig(max_concurrent=1)
        self.manager.register_agent("ctx_test_agent", config)

    def tearDown(self):
        """Clean up after tests."""
        self.manager._controller._agent_limiters.clear()
        self.manager._controller._agent_configs.clear()
        self.manager._controller._active_executions.clear()

    def test_context_manager_success(self):
        """Test context manager with successful acquisition."""
        with ConcurrencyContext(self.manager, "ctx_test_agent") as ctx:
            self.assertTrue(ctx.acquired)
            self.assertIsNotNone(ctx.execution_id)
            self.assertIsNone(ctx.rejection_reason)

    def test_context_manager_rejection(self):
        """Test context manager with rejection."""
        acquired, exec_id = self.manager.acquire_permit("ctx_test_agent")
        self.assertTrue(acquired)

        with ConcurrencyContext(self.manager, "ctx_test_agent") as ctx:
            self.assertFalse(ctx.acquired)
            self.assertIsNotNone(ctx.rejection_reason)

        self.manager.release_permit(exec_id)

    def test_context_manager_auto_release(self):
        """Test that context manager automatically releases on exit."""
        with ConcurrencyContext(self.manager, "ctx_test_agent") as ctx:
            self.assertTrue(ctx.acquired)

        acquired, _ = self.manager.acquire_permit("ctx_test_agent")
        self.assertTrue(acquired)
        self.manager.release_permit(acquired)


class TestRateLimiterEdgeCases(TestCase):
    """Test edge cases and error conditions."""

    def test_invalid_max_concurrent(self):
        """Test that invalid max_concurrent raises error."""
        with self.assertRaises(ValueError):
            ThreadRateLimiter(max_concurrent=0)

        with self.assertRaises(ValueError):
            ThreadRateLimiter(max_concurrent=-1)

    def test_multiple_limiter_instances(self):
        """Test that multiple limiter instances work independently."""
        limiter1 = ThreadRateLimiter(max_concurrent=1)
        limiter2 = ThreadRateLimiter(max_concurrent=1)

        limiter1.acquire()
        limiter2.acquire()

        self.assertFalse(limiter1.acquire())
        self.assertFalse(limiter2.acquire())

        limiter1.release()
        self.assertTrue(limiter1.acquire())
        self.assertFalse(limiter2.acquire())

    def test_repr(self):
        """Test string representation."""
        limiter = ThreadRateLimiter(max_concurrent=5)
        limiter.acquire()
        limiter.acquire()

        repr_str = repr(limiter)
        self.assertIn("max_concurrent=5", repr_str)
        self.assertIn("current=2", repr_str)


if __name__ == '__main__':
    import unittest
    unittest.main()
