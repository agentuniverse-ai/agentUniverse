# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 11:56
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: test_framework_context.py

import queue
import time
import threading

import pytest

from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.context.framework_context import FrameworkContext

context_manager: FrameworkContextManager = FrameworkContextManager()


def add(q: queue.Queue):
    with FrameworkContext({"add_value": 1}):
        for i in range(10):
            add_value = context_manager.get_context("add_value")
            add_value += 1
            context_manager.set_context("add_value", add_value)
            time.sleep(0.001)
        q.put(context_manager.get_context("add_value"))


async def async_add(q: queue.Queue):
    add(q)


@pytest.mark.asyncio
async def test_context_thread_and_async_isolation():
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


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
