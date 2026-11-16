# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 11:56
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_framework_context.py

import asyncio
import queue
import threading
import time
from contextvars import copy_context

import pytest

from agentuniverse.base.context.framework_context import FrameworkContext
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager

context_manager: FrameworkContextManager = FrameworkContextManager()


def add(q: queue.Queue):
    """Add.
    """
    with FrameworkContext({"add_value": 1}):
        for i in range(10):
            add_value = context_manager.get_context("add_value")
            add_value += 1
            context_manager.set_context("add_value", add_value)
            time.sleep(0.001)
        q.put(context_manager.get_context("add_value"))


async def async_add(q: queue.Queue):
    """Async add.
    """
    await asyncio.get_event_loop().run_in_executor(None, add, q)


@pytest.mark.asyncio
async def test_context_thread_and_async_isolation():
    """Test that context thread and async isolation.
    """
    queue1 = queue.Queue()
    queue2 = queue.Queue()
    queue3 = queue.Queue()
    queue4 = queue.Queue()
    t1 = threading.Thread(target=add, args=(queue1,))
    t2 = threading.Thread(target=add, args=(queue2,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    await async_add(queue3)
    await async_add(queue4)
    assert queue1.get() == 11
    assert queue2.get() == 11
    assert queue3.get() == 11
    assert queue4.get() == 11


def test_set_all_contexts_returns_tokens_for_restoration():
    """Test that set all contexts returns tokens for restoration.
    """
    context_manager.clear_all_contexts()
    original_token = context_manager.set_context("request_id", "worker-value")

    tokens = context_manager.set_all_contexts(
        {
            "request_id": "parent-value",
            "temporary_key": "temporary-value",
        }
    )

    assert context_manager.get_context("request_id") == "parent-value"
    assert context_manager.get_context("temporary_key") == "temporary-value"

    for var_name, token in tokens.items():
        context_manager.reset_context(var_name, token)

    assert context_manager.get_context("request_id") == "worker-value"
    assert context_manager.get_context("temporary_key") is None

    context_manager.reset_context("request_id", original_token)
    context_manager.clear_all_contexts()


def test_log_context_isolated_across_copied_contexts():
    """Test that log context isolated across copied contexts.
    """
    context_manager.clear_all_contexts()
    context_manager.set_log_context("request_id", "parent")
    child_context = copy_context()

    def update_child_context():
        """Update child context.
        """
        context_manager.set_log_context("worker_id", "child")
        return context_manager.get_context("LOG_CONTEXT")

    child_log_context = child_context.run(update_child_context)

    assert child_log_context == {
        "request_id": "parent",
        "worker_id": "child",
    }
    assert context_manager.get_context("LOG_CONTEXT") == {
        "request_id": "parent",
    }
    context_manager.clear_all_contexts()


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
