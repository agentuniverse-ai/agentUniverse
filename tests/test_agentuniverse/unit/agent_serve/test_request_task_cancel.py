# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20 10:30
# @FileName: test_request_task_cancel.py
import asyncio

import pytest

from agentuniverse.agent_serve.web.request_task import (
    InvalidStateTransitionError,
    RequestTask,
    TaskStateEnum,
)


def test_cancel_after_finish_is_a_noop():
    """Canceling a task that already finished must not raise."""

    def run_ok(**kwargs):
        return "ok"

    task = RequestTask(run_ok, saved=False)
    task.run()
    assert task.request_state() == TaskStateEnum.FINISHED.value

    task.cancel()

    assert task.request_state() == TaskStateEnum.FINISHED.value


def test_cancel_is_idempotent():
    """A second cancel on an already canceled task must not raise."""
    task = RequestTask(lambda **kwargs: None, saved=False)
    task.next_state(TaskStateEnum.RUNNING)

    task.cancel()
    task.cancel()

    assert task.request_state() == TaskStateEnum.CANCELED.value


def test_cancel_stops_async_stream():
    """Canceling an async task must end its SSE stream promptly.

    The EOF signal has to reach async_queue: before the fix cancel only
    signaled the thread queue, so the consumer kept receiving chunks from a
    task the state machine had already marked canceled.
    """
    chunk_event = asyncio.Event()

    async def chatty_agent(**kwargs):
        queue = kwargs.get('output_stream')
        for i in range(500):
            await asyncio.sleep(0.01)
            await queue.put(f"chunk-{i}")
            chunk_event.set()
        return "done"

    async def scenario():
        task = RequestTask(chatty_agent, saved=False)
        stream = task.async_stream_run()

        process_chunks_after_cancel = 0
        cancel_issued = False
        async for _item in stream:
            chunk_event.clear()
            if not cancel_issued:
                task.cancel()
                cancel_issued = True
            else:
                process_chunks_after_cancel += 1
            # Ends the wait as soon as the loop is broken by the cancel
            # EOF; before the fix the producer kept feeding chunks here.
            await asyncio.wait_for(chunk_event.wait(), timeout=1)

        # The stream ended while the producer was still running.
        assert not task.async_task.done()
        assert task.request_state() == TaskStateEnum.CANCELED.value
        assert process_chunks_after_cancel == 0

        task.async_task.cancel()
        await asyncio.gather(task.async_task, return_exceptions=True)

    asyncio.run(scenario())


def test_next_state_invalid_transition_raises_specific_error():
    """Out-of-contract transitions raise the dedicated error type."""
    task = RequestTask(lambda **kwargs: None, saved=False)
    with pytest.raises(InvalidStateTransitionError):
        task.next_state(TaskStateEnum.FINISHED)
