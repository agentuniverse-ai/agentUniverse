# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/7/12 00:40
# @Author  : Cursor Agent
# @FileName: rate_limiter.py
"""
Rate limiting module for agentUniverse.

Provides semaphore-based rate limiting and concurrency control for agents.
"""
from asyncio import Semaphore, Lock
from threading import Semaphore as ThreadSemaphore, Lock as ThreadLock
from typing import Optional, Callable, Any, TypeVar, Awaitable
from functools import wraps
from contextlib import contextmanager

from agentuniverse.base.annotation.singleton import singleton

T = TypeVar('T')


class RateLimiter:
    """Base rate limiter using semaphore for concurrency control.

    Supports both synchronous and asynchronous operations with configurable
    maximum concurrent executions.
    """

    def __init__(self, max_concurrent: int = 10, timeout: Optional[float] = None):
        """Initialize the rate limiter.

        Args:
            max_concurrent: Maximum number of concurrent executions allowed.
            timeout: Maximum time to wait for a permit in seconds. None means wait forever.
        """
        if max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        self._max_concurrent = max_concurrent
        self._timeout = timeout
        self._current_count = 0
        self._total_acquired = 0
        self._total_rejected = 0

    @property
    def max_concurrent(self) -> int:
        """Return the maximum concurrent executions allowed."""
        return self._max_concurrent

    @property
    def current_concurrent(self) -> int:
        """Return the current number of concurrent executions."""
        return self._current_count

    @property
    def total_acquired(self) -> int:
        """Return the total number of successful acquisitions."""
        return self._total_acquired

    @property
    def total_rejected(self) -> int:
        """Return the total number of rejected acquisitions."""
        return self._total_rejected

    @property
    def rejection_rate(self) -> float:
        """Calculate the rejection rate."""
        total = self._total_acquired + self._total_rejected
        if total == 0:
            return 0.0
        return self._total_rejected / total

    def acquire(self) -> bool:
        """Attempt to acquire a permit synchronously.

        Returns:
            True if permit acquired, False otherwise.
        """
        raise NotImplementedError

    def release(self) -> None:
        """Release a permit synchronously."""
        raise NotImplementedError

    def acquire_async(self) -> Awaitable[bool]:
        """Attempt to acquire a permit asynchronously.

        Returns:
            True if permit acquired, False otherwise.
        """
        raise NotImplementedError

    async def release_async(self) -> None:
        """Release a permit asynchronously."""
        raise NotImplementedError

    @contextmanager
    def limit(self):
        """Context manager for synchronous rate limiting.

        Yields:
            True if permit acquired, raises exception otherwise.

        Raises:
            RuntimeError: If permit cannot be acquired within timeout.
        """
        if not self.acquire():
            self._total_rejected += 1
            raise RuntimeError(
                f"Rate limit exceeded: cannot acquire permit within {self._timeout}s. "
                f"Current: {self._current_count}/{self._max_concurrent}"
            )
        try:
            yield True
        finally:
            self.release()

    async def limit_async(self):
        """Async context manager for rate limiting.

        Usage:
            async with rate_limiter.limit_async():
                # do work
        """
        return _AsyncRateLimitContext(self)

    def __repr__(self) -> str:
        return (
            f"RateLimiter(max_concurrent={self._max_concurrent}, "
            f"current={self._current_count}, "
            f"acquired={self._total_acquired}, "
            f"rejected={self._total_rejected})"
        )


class ThreadRateLimiter(RateLimiter):
    """Thread-based rate limiter using threading.Semaphore."""

    def __init__(self, max_concurrent: int = 10, timeout: Optional[float] = None):
        super().__init__(max_concurrent, timeout)
        self._semaphore = ThreadSemaphore(max_concurrent)
        self._lock = ThreadLock()
        self._count_lock = ThreadLock()

    def acquire(self) -> bool:
        acquired = self._semaphore.acquire(timeout=self._timeout)
        if acquired:
            with self._count_lock:
                self._current_count += 1
                self._total_acquired += 1
        else:
            with self._lock:
                self._total_rejected += 1
        return acquired

    def release(self) -> None:
        self._semaphore.release()
        with self._count_lock:
            self._current_count = max(0, self._current_count - 1)

    def acquire_async(self) -> Awaitable[bool]:
        import asyncio
        return self._acquire_async_impl()

    async def _acquire_async_impl(self) -> bool:
        import asyncio
        try:
            acquired = await asyncio.wait_for(
                asyncio.to_thread(self._semaphore.acquire),
                timeout=self._timeout
            )
            if acquired:
                with self._count_lock:
                    self._current_count += 1
                    self._total_acquired += 1
            return acquired
        except asyncio.TimeoutError:
            with self._lock:
                self._total_rejected += 1
            return False

    async def release_async(self) -> None:
        self.release()


class AsyncRateLimiter(RateLimiter):
    """Async-native rate limiter using asyncio.Semaphore."""

    def __init__(self, max_concurrent: int = 10, timeout: Optional[float] = None):
        super().__init__(max_concurrent, timeout)
        self._semaphore = Semaphore(max_concurrent)
        self._lock = Lock()
        self._count_lock = Lock()

    def acquire(self) -> bool:
        """Synchronous acquire (blocking)."""
        acquired = self._semaphore.acquire(blocking=True, timeout=self._timeout)
        if acquired:
            import asyncio
            # Note: This is a sync wrapper for async semaphore
            # In practice, prefer async context manager for async code
            pass
        return acquired

    def release(self) -> None:
        """Synchronous release (blocking)."""
        self._semaphore.release()

    async def acquire_async(self) -> bool:
        acquired = await self._semaphore.acquire(timeout=self._timeout)
        if acquired:
            async with self._count_lock:
                self._current_count += 1
                self._total_acquired += 1
        else:
            async with self._lock:
                self._total_rejected += 1
        return acquired

    async def release_async(self) -> None:
        self._semaphore.release()
        async with self._count_lock:
            self._current_count = max(0, self._current_count - 1)


class _AsyncRateLimitContext:
    """Async context manager implementation for rate limiting."""

    def __init__(self, rate_limiter: RateLimiter):
        self._rate_limiter = rate_limiter
        self._acquired = False

    async def __aenter__(self) -> bool:
        self._acquired = await self._rate_limiter.acquire_async()
        if not self._acquired:
            raise RuntimeError(
                f"Rate limit exceeded: cannot acquire permit within {self._rate_limiter._timeout}s"
            )
        return True

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._acquired:
            await self._rate_limiter.release_async()


def rate_limited(max_concurrent: int = 10, timeout: Optional[float] = 30.0):
    """Decorator for adding rate limiting to synchronous functions.

    Args:
        max_concurrent: Maximum concurrent executions.
        timeout: Timeout for acquiring permit.

    Usage:
        @rate_limited(max_concurrent=5)
        def my_function():
            pass
    """
    limiter = ThreadRateLimiter(max_concurrent=max_concurrent, timeout=timeout)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with limiter.limit():
                return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limited_async(max_concurrent: int = 10, timeout: Optional[float] = 30.0):
    """Decorator for adding rate limiting to async functions.

    Args:
        max_concurrent: Maximum concurrent executions.
        timeout: Timeout for acquiring permit.

    Usage:
        @rate_limited_async(max_concurrent=5)
        async def my_async_function():
            pass
    """
    limiter = AsyncRateLimiter(max_concurrent=max_concurrent, timeout=timeout)

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            async with limiter.limit_async():
                return await func(*args, **kwargs)
        return wrapper
    return decorator
