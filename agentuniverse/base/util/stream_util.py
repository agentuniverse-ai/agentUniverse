"""Forward iterator closure to resources acquired before iteration starts."""
import inspect
from typing import AsyncIterator, Iterator, TypeVar

T = TypeVar('T')


def _close(stream):
    close = getattr(stream, 'close', None)
    if callable(close):
        close()


async def _aclose(stream):
    close = getattr(stream, 'aclose', None)
    if not callable(close):
        close = getattr(stream, 'close', None)
    if callable(close):
        result = close()
        if inspect.isawaitable(result):
            await result


class ClosingIterator(Iterator[T]):
    """Own an iterator and its resource, including before the first next()."""

    def __init__(self, iterator, owner):
        self._iterator = iter(iterator)
        self._owner = owner
        self._closed = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._closed:
            raise StopIteration
        try:
            return next(self._iterator)
        except BaseException:
            self.close()
            raise

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            _close(self._iterator)
        finally:
            if self._owner is not self._iterator:
                _close(self._owner)


class ClosingAsyncIterator(AsyncIterator[T]):
    """Async counterpart supporting both aclose() and SDK async close()."""

    def __init__(self, iterator, owner):
        self._iterator = iterator.__aiter__()
        self._owner = owner
        self._closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self._iterator.__anext__()
        except BaseException:
            await self.aclose()
            raise

    async def aclose(self):
        if self._closed:
            return
        self._closed = True
        try:
            await _aclose(self._iterator)
        finally:
            if self._owner is not self._iterator:
                await _aclose(self._owner)


def map_stream(stream, parse):
    """Parse chunks while retaining explicit ownership of the source stream."""
    def chunks():
        for chunk in stream:
            output = parse(chunk)
            if output:
                yield output

    return ClosingIterator(chunks(), stream)


def map_async_stream(stream, parse):
    """Parse async chunks and close an acquired source even if never started."""
    async def chunks():
        async for chunk in stream:
            output = parse(chunk)
            if output:
                yield output

    return ClosingAsyncIterator(chunks(), stream)
