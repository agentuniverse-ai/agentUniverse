"""Thread-owned, pull-based adapters for synchronous Bedrock event streams."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from contextvars import copy_context
from typing import Any

from agentuniverse.llm.llm_output import LLMOutput

_END = object()


class BedrockStream(Iterator[LLMOutput]):
    """Own the response even before the text generator is first advanced."""

    def __init__(self, iterator: Iterator[LLMOutput], response_stream: Any):
        self._iterator = iterator
        self._response_stream = response_stream
        self._closed = False

    def __next__(self) -> LLMOutput:
        if self._closed:
            raise StopIteration
        try:
            return next(self._iterator)
        except StopIteration:
            self.close()
            raise
        except BaseException:
            # Do not replace an iteration error with a secondary close error.
            with suppress(Exception):
                self.close()
            raise

    def close(self) -> None:
        """Close the generator and response exactly once."""
        if not self._closed:
            self._closed = True
            try:
                self._iterator.close()
            finally:
                self._response_stream.close()


async def async_bedrock_stream(factory: Callable[[], BedrockStream]) -> AsyncIterator[LLMOutput]:
    """Open/read/close on one worker, with at most one requested read at a time.

    Cancellation queues cleanup behind the in-flight SDK operation instead of
    closing a generator while it is executing or waiting on network I/O here.
    """
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bedrock-stream")
    iterator = None
    cancelled = False

    def open_stream():
        nonlocal iterator
        iterator = factory()

    def read_next():
        # StopIteration cannot be transferred through an asyncio Future.
        return next(iterator, _END)

    def close_stream():
        if iterator is not None:
            iterator.close()

    def submit(function):
        return asyncio.wrap_future(executor.submit(copy_context().run, function))

    try:
        await submit(open_stream)
        while True:
            item = await submit(read_next)
            if item is _END:
                break
            yield item
    except asyncio.CancelledError:
        cancelled = True
        raise
    finally:
        cleanup = executor.submit(copy_context().run, close_stream)
        executor.shutdown(wait=False)
        if not cancelled:
            await asyncio.shield(asyncio.wrap_future(cleanup))
