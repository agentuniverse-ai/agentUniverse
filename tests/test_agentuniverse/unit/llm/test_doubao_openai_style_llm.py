import unittest
from unittest.mock import patch, MagicMock
import asyncio
import os
import toml
from pathlib import Path

from agentuniverse.llm.default.doubao_openai_style_llm import DouBaoOpenAIStyleLLM
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.configer import Configer


def load_llm_yaml(yaml_path: str) -> dict:
    """Load LLM configuration from YAML file.
    
    Args:
        yaml_path: Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary containing model settings and extra_body
    """
    configer = Configer(path=yaml_path).load()
    return configer.value


class TestDoubaoOpenAIStyleLLM(unittest.TestCase):
    def setUp(self) -> None:
        """Set up test fixtures."""
        # Load custom keys from configuration file
        current_dir = Path(__file__).parent
        custom_key_path = current_dir / 'custom_key.toml'

        if custom_key_path.exists():
            config = toml.load(custom_key_path)
            self.api_key = config['KEY_LIST'].get('DOUBAO_API_KEY', '')
            self.api_base = config['KEY_LIST'].get('DOUBAO_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')
            self.model_name = 'doubao-seed-1-6-lite-251015'

            # Set environment variables for the LLM to use
            if self.api_key:
                os.environ['DOUBAO_API_KEY'] = self.api_key
            if self.api_base:
                os.environ['DOUBAO_API_BASE'] = self.api_base
        else:
            raise FileNotFoundError(f"Configuration file not found: {custom_key_path}")

        # Initialize ApplicationConfigManager for each test
        app_configer = AppConfiger()
        ApplicationConfigManager().app_configer = app_configer

        # Initialize LLM instance with configuration
        self.llm = DouBaoOpenAIStyleLLM(
            model_name=self.model_name,
            api_key=self.api_key,
            api_base=self.api_base
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

    def test_call_with_extra_data(self) -> None:
        """Test call with extra_body loaded from YAML configuration."""
        # Get the path to doubao_openai_style_llm.yaml
        yaml_path = Path(__file__).parent.parent.parent.parent.parent / 'agentuniverse' / 'llm' / 'default' / 'doubao_openai_style_llm.yaml'
        
        # print(f"\n[Loading YAML Config] {yaml_path}")
        
        # Load configuration from YAML using load_llm_yaml function
        llm_config = load_llm_yaml(str(yaml_path))
        # print(f"\n[YAML Configuration]")
        # print(f"  Name: {llm_config.get('name')}")
        # print(f"  Model: {llm_config.get('model_name')}")
        # print(f"  Max Tokens: {llm_config.get('max_tokens')}")
        # print(f"  Extra Body: {llm_config.get('extra_body')}")
        
        # Extract extra_body from YAML configuration
        extra_body = llm_config.get('extra_body', {})
        
        messages = [
            {
                "role": "user",
                "content": "hi, please introduce yourself",
            }
        ]
        
        # Test non-streaming call with extra_body from YAML
        print(f"\n[Testing Non-streaming with extra_body]")
        output = self.llm.call(
            messages=messages, 
            streaming=False,
            extra_body=extra_body
        )
        print(f"[Response]\n{output.__str__()}")
        self.assertIsNotNone(output.text)
        
        # Test streaming call with extra_body from YAML
        print(f"\n[Testing Streaming with extra_body]")
        content = ""
        for chunk in self.llm.call(
            messages=messages,
            streaming=True,
            extra_body=extra_body
        ):
            if chunk.text:
                content += chunk.text
                print(chunk.text, end='')
        print()  # New line after streaming
        self.assertGreater(len(content), 0)

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
