# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/21 14:55
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_llm.py
import asyncio
import unittest

from langchain.chains import ConversationChain

from agentuniverse.llm.default.default_openai_llm import DefaultOpenAILLM


class LLMTest(unittest.TestCase):
    """
    Test cases for LLM class
    """

    def setUp(self) -> None:
        """Create a DefaultOpenAILLM instance under test."""
        self.llm = DefaultOpenAILLM(model_name='gpt-4o')

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

    #
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

    def test_gpt_4o_image(self):
        """Verify a multimodal call with an image URL runs successfully."""
        response = self.llm.call(
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
                {"role": "user", "content": [
                    {"type": "text", "text": "What's the area of the triangle?"},
                    {"type": "image_url", "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/The_Algebra_of_Mohammed_Ben_Musa_-_page_82b.png"}
                     }
                ]}
            ],
            temperature=0.0,
        )
        print(response.__str__())


if __name__ == '__main__':
    unittest.main()
