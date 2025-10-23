# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/22 10:16
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: async_util.py

import asyncio
import queue
import threading
from queue import Queue
from typing import Coroutine, TypeVar, Any, Optional

T = TypeVar("T")


def _async_runner_thread_target(coro: Coroutine[Any, Any, T], result_queue: Queue):
    """
    Internal target function for the worker thread.

    It creates a new event loop in the current thread (the worker thread),
    runs the provided coroutine within that loop, and puts the result
    or any exception encountered into the result_queue.
    """
    try:
        result = asyncio.run(coro)
        result_queue.put(result)
    except Exception as e:
        result_queue.put(e)


def run_async_from_sync(coro: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """
    Synchronously executes an asynchronous coroutine in a separate thread
    and returns its result.

    This function is designed to be called from synchronous code, especially
    when you need to call an async function without blocking an existing
    event loop (if called from an async context via a sync function).

    It starts a new thread, which creates its own event loop to run the
    coroutine. The calling thread blocks until the result is available
    or a timeout occurs.

    Args:
        coro: The coroutine object to execute (e.g., my_async_func(arg1)).
              Ensure this is the coroutine object, not the function itself.
        timeout: Optional maximum time in seconds to wait for the result.
                 If None, waits indefinitely.

    Returns:
        The result returned by the awaited coroutine.

    Raises:
        TypeError: If the provided 'coro' argument is not a coroutine.
        TimeoutError: If the timeout is reached before the coroutine completes.
        Any Exception: Any exception raised by the coroutine during its execution
                       will be re-raised in the calling thread.
    """
    if not asyncio.iscoroutine(coro):
        raise TypeError(f"Expected a coroutine, but got {type(coro).__name__}")

    # Using a queue for thread-safe communication of the result/exception
    result_queue: Queue = Queue(maxsize=1)
    worker_thread = threading.Thread(target=_async_runner_thread_target, args=(coro, result_queue), daemon=True)
    worker_thread.start()

    try:
        result = result_queue.get(timeout=timeout)
    except queue.Empty:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    finally:
        worker_thread.join(timeout=1.0)

    if isinstance(result, Exception):
        raise result
    else:
        return result
