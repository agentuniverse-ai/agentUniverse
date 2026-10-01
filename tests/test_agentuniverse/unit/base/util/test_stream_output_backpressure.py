#!/usr/bin/env python3

import asyncio
import queue
import threading

import pytest

import agentuniverse.base.util.common_util as common_util_module
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.plan.planner.react_planner.stream_callback import (
    StreamOutPutCallbackHandler,
)
from agentuniverse.base.util.common_util import stream_output


@pytest.fixture(autouse=True)
def _fast_drop_timeout(monkeypatch):
    """Drop-path tests should not wait the 30s production default."""
    monkeypatch.setattr(common_util_module, 'STREAM_PUT_BLOCK_TIMEOUT', 0.05, raising=False)


def test_full_sync_queue_drops_instead_of_raising():
    output_stream = queue.Queue(maxsize=1)
    stream_output(output_stream, {"chunk": 1})
    # a second chunk on a full queue must not raise queue.Full
    stream_output(output_stream, {"chunk": 2})
    assert output_stream.qsize() == 1


def test_full_asyncio_queue_drops_instead_of_raising():
    async def run():
        output_stream = asyncio.Queue(maxsize=1)
        output_stream.put_nowait({"chunk": 1})
        stream_output(output_stream, {"chunk": 2})
        assert output_stream.qsize() == 1

    asyncio.run(run())


def test_backpressure_delivers_all_chunks_to_slow_consumer():
    output_stream = queue.Queue(maxsize=2)
    received = []

    def consumer():
        for _ in range(50):
            received.append(output_stream.get(timeout=30))

    thread = threading.Thread(target=consumer, daemon=True)
    thread.start()
    for i in range(50):
        stream_output(output_stream, {"i": i}, block_timeout=10)
    thread.join(timeout=30)
    assert len(received) == 50
    assert [item["i"] for item in received] == list(range(50))


def test_eof_put_blocks_until_consumer_drains():
    output_stream = queue.Queue(maxsize=1)
    stream_output(output_stream, "chunk")
    drained = threading.Event()

    def consumer():
        output_stream.get(timeout=5)
        drained.set()

    threading.Thread(target=consumer, daemon=True).start()
    # queue is momentarily full; the EOF must wait for the consumer
    stream_output(output_stream, '{"type": "EOF"}', block_timeout=10)
    assert output_stream.get(timeout=5) == '{"type": "EOF"}'


def test_planner_stream_output_tolerates_full_queue():
    input_object = InputObject({"output_stream": queue.Queue(maxsize=1)})
    Planner.stream_output(input_object, {"chunk": 1})
    Planner.stream_output(input_object, {"chunk": 2})


def test_react_stream_callback_tolerates_full_queue():
    from langchain_core.agents import AgentAction

    handler = StreamOutPutCallbackHandler(queue.Queue(maxsize=1))
    handler.on_agent_action(AgentAction(tool="demo", tool_input={}, log="first"))
    handler.on_agent_action(AgentAction(tool="demo", tool_input={}, log="second"))
