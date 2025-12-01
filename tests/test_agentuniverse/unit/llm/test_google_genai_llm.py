import unittest
import asyncio
from agentuniverse.llm.default.google_genai_llm import GoogleGenaiLLM


class TestGoogleGenaiLLM(unittest.TestCase):
    def setUp(self) -> None:
        self.llm = GoogleGenaiLLM(model_name='gemini-1.5-flash',
                                  api_key='your_google_api_key')

    def test_call(self) -> None:
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = self.llm.call(messages=messages, streaming=False)
        print(output.__str__())

    def test_acall(self) -> None:
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        print(output.__str__())

    def test_call_stream(self):
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        for chunk in self.llm.call(messages=messages, streaming=True):
            print(chunk.text, end='')
        print()

    def test_acall_stream(self):
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        asyncio.run(self.call_stream(messages=messages))

    async def call_stream(self, messages: list):
        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            print(chunk.text, end='')
        print()

    def test_get_num_tokens(self):
        print(self.llm.get_num_tokens('"content": "hi, please introduce yourself",'))


if __name__ == '__main__':
    unittest.main()
