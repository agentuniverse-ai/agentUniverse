import asyncio
from types import SimpleNamespace

from agentuniverse.llm.default.claude_llm import ClaudeLLM


class _AsyncChunks:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        self._iterator = iter(self._chunks)
        return self

    async def __anext__(self):
        try:
            return next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration


def test_claude_async_stream_does_not_write_chunks_to_stdout(capsys):
    chunks = _AsyncChunks([
        SimpleNamespace(type="message_start"),
        SimpleNamespace(
            type="content_block_delta",
            delta=SimpleNamespace(text="hello"),
            model_dump=lambda: {"type": "content_block_delta"},
        ),
    ])

    async def collect():
        return [chunk async for chunk in ClaudeLLM().agenerate_stream_result(chunks)]

    result = asyncio.run(collect())

    assert [chunk.text for chunk in result] == ["hello"]
    assert capsys.readouterr().out == ""
