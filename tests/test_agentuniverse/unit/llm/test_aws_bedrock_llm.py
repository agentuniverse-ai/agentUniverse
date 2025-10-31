import unittest
from unittest.mock import patch, MagicMock
import asyncio

from agentuniverse.llm.default.aws_bedrock_llm import AWSBedrockLLM
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger

class TestAWSBedrockLLM(unittest.TestCase):
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Initialize ApplicationConfigManager for each test

        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer
        
        self.llm = AWSBedrockLLM(
            model_name='amazon.nova-lite-v1:0',
            aws_access_key_id='AWS_ACCESS_KEY_ID',
            aws_secret_access_key='AWS_SECRET_ACCESS_KEY',
            aws_region='us-east-1',
        )

    
    def test_call(self) -> None:
        """Test synchronous call with real API."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = self.llm.call(messages=messages, streaming=False)
        print(output.__str__())
        self.assertIsNotNone(output.text)

    
    def test_acall(self) -> None:
        """Test asynchronous call with real API."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        output = asyncio.run(self.llm.acall(messages=messages, streaming=False))
        print(output.__str__())
        self.assertIsNotNone(output.text)


    def test_call_stream(self):
        """Test streaming call with real API."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        chunks = []
        for chunk in self.llm.call(messages=messages, streaming=True):
            print(chunk.text, end='')
            chunks.append(chunk.text)
        print()
        self.assertGreater(len(chunks), 0)

    
    def test_acall_stream(self):
        """Test async streaming call with real API."""
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        asyncio.run(self.call_stream(messages=messages))

    async def call_stream(self, messages: list):
        """Helper for async streaming test."""
        chunks = []
        async for chunk in await self.llm.acall(messages=messages, streaming=True):
            print(chunk.text, end='')
            chunks.append(chunk.text)
        print()
        self.assertGreater(len(chunks), 0)

    def test_get_num_tokens(self):
        """Test token counting."""
        text = "hi, please introduce yourself"
        token_count = self.llm.get_num_tokens(text)
        print(f"Token count for '{text}': {token_count}")
        self.assertGreater(token_count, 0)
        # Simple approximation: ~4 characters per token
        expected_approx = len(text) // 4
        self.assertAlmostEqual(token_count, expected_approx, delta=5)

if __name__ == '__main__':
    unittest.main()
