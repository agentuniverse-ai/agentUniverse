# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/9/20 21:10
# @FileName: test_request_task_stream.py
import asyncio

from agentuniverse.agent_serve.web.request_task import RequestTask


def test_async_receive_steps_does_not_print_to_stdout_on_timeout(capsys):
    """The async stream loop must log through LOGGER, not print().

    Before the fix every 1.5s poll timeout of every in-flight async streaming
    request wrote a raw line to stdout.
    """

    async def scenario():
        task = RequestTask(func=lambda **kwargs: None, saved=False)
        task.async_task = asyncio.create_task(asyncio.sleep(1.2, result={"answer": "ok"}))

        async def feed_eof():
            # The first queue.get already timed out at ~0.5s + 1s sleep, so
            # this EOF is waiting in the queue when the loop polls again.
            await asyncio.sleep(1.1)
            await task.async_queue.put('{"type": "EOF"}')

        feeder = asyncio.create_task(feed_eof())
        chunks = []
        async for chunk in task.async_receive_steps():
            chunks.append(chunk)
        await feeder
        return chunks

    chunks = asyncio.run(scenario())

    assert capsys.readouterr().out == ""
    assert len(chunks) == 1
    assert '"result"' in chunks[0]
    assert '"answer": "ok"' in chunks[0]
