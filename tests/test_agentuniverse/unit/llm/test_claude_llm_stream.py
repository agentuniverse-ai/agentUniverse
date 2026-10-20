import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

from agentuniverse.llm.default.claude_llm import ClaudeLLM


class _AsyncChunks:
    def __init__(self, chunks):
        self._chunks = chunks

    def __aiter__(self):
        self._iter = iter(self._chunks)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class _Chunk:
    type = "content_block_delta"
    delta = SimpleNamespace(text="hello")

    def model_dump(self):
        return {"type": self.type, "text": self.delta.text}


class ClaudeLLMStreamTest(unittest.IsolatedAsyncioTestCase):

    async def test_async_stream_does_not_print_chunks(self):
        llm = ClaudeLLM()
        stdout = io.StringIO()

        async def collect():
            return [
                output
                async for output in llm.agenerate_stream_result(_AsyncChunks([_Chunk()]))
            ]

        with redirect_stdout(stdout):
            outputs = await collect()

        self.assertEqual("hello", outputs[0].text)
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
