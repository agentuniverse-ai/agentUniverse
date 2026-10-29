import unittest

from langchain.chains.conversation.base import ConversationChain

import asyncio
from agentuniverse.llm.default.gemini_openai_style_llm import GeminiOpenAIStyleLLM


class TestGeminiOpenAIStyleLLM(unittest.TestCase):
    """Unit tests for the GeminiOpenAIStyleLLM wrapper."""

    def setUp(self) -> None:
        """Create a GeminiOpenAIStyleLLM instance under test."""
        self.llm = GeminiOpenAIStyleLLM(model_name='gemini-2.0-flash',
                                        api_key='xxxx',
                                        api_base='https://generativelanguage.googleapis.com/v1beta/openai/',
                                        proxy='http://127.0.0.1:10808')

    def test_call(self) -> None:
        """Verify a synchronous non-streaming call returns an LLM result."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = self.llm.call(messages=messages, streaming=False)
        print(output.__str__())

    def test_acall(self) -> None:
        """Verify an asynchronous non-streaming call returns an LLM result."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        print(output.__str__())

    def test_call_stream(self):
        """Verify a synchronous streaming call yields response chunks."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        for chunk in self.llm.call(messages=messages, streaming=True):
            print(chunk.text, end='')
        print()

    #
    def test_acall_stream(self):
        """Verify the async streaming path through the call_stream helper."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        asyncio.run(self.call_stream(messages=messages))

    async def call_stream(self, messages: list):
        """Consume and print chunks from an asynchronous streaming call.

        Args:
            messages: The chat messages to send to the LLM.
        """
        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            print(chunk, end='')
        print()

    def test_as_langchain(self):
        """Verify the LLM can be wrapped for use in a langchain chain."""
        langchain_llm = self.llm.as_langchain()
        llm_chain = ConversationChain(llm=langchain_llm)
        res = llm_chain.predict(input='hello')
        print(res)

    def test_get_num_tokens(self):
        """Verify the token-count estimation call runs successfully."""
        print(self.llm.get_num_tokens('"content": "hi, please introduce yourself",'))


if __name__ == '__main__':
    unittest.main()
