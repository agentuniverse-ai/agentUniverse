from unittest import TestCase

from openai.types.chat.chat_completion_chunk import (
    ChatCompletionChunk,
    Choice,
    ChoiceDelta,
)

from agentuniverse.llm.openai_llm import OpenAILLM
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM


class TestOpenAIStreamDictChunks(TestCase):

    parsers = (OpenAILLM.parse_result, OpenAIStyleLLM.parse_result)

    def test_plain_dict_chunks_are_preserved_as_raw_output(self):
        chunk = {"choices": [{"delta": {"content": "hello"}}]}

        for parser in self.parsers:
            with self.subTest(parser=parser.__qualname__):
                result = parser(chunk)

                self.assertEqual(result.text, "hello")
                self.assertEqual(result.raw, chunk)

    def test_model_chunks_are_serialized_as_raw_output(self):
        chunk = ChatCompletionChunk(
            id="chunk-id",
            choices=[Choice(index=0, delta=ChoiceDelta(content="hello"))],
            created=0,
            model="test-model",
            object="chat.completion.chunk",
        )

        for parser in self.parsers:
            with self.subTest(parser=parser.__qualname__):
                result = parser(chunk)

                self.assertEqual(result.text, "hello")
                self.assertEqual(result.raw, chunk.model_dump())
