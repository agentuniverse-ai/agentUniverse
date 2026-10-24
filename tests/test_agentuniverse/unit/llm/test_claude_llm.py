#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import yaml

from agentuniverse.llm.default.claude_llm import ClaudeLLM


class TestClaudeLLMAsyncClientLifecycle(unittest.IsolatedAsyncioTestCase):
    async def test_acall_stores_and_closes_async_client(self) -> None:
        llm = ClaudeLLM(model_name='claude-3-haiku-20240307', api_key='ak')

        stub_client = MagicMock()
        stub_client.messages.create = AsyncMock(
            return_value=MagicMock(content=[MagicMock(text='hi')]))
        stub_client.close = AsyncMock()

        with patch.object(ClaudeLLM, '_new_async_client', return_value=stub_client):
            result = await llm._acall(messages=[{'role': 'user', 'content': 'hi'}],
                                      streaming=False)

        self.assertEqual(result.text, 'hi')
        self.assertIs(llm.async_client, stub_client)
        stub_client.close.assert_awaited_once()


# Retired by Anthropic: requests naming them fail with a 404 not_found_error.
RETIRED_CLAUDE_MODELS = {
    'claude-3-opus-20240229', 'claude-3-opus-latest', 'claude-3-sonnet-20240229',
    'claude-3-haiku-20240307', 'claude-3-5-sonnet-20240620', 'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-latest', 'claude-3-5-haiku-20241022', 'claude-3-5-haiku-latest',
    'claude-3-7-sonnet-20250219', 'claude-3-7-sonnet-latest',
}


class TestDefaultClaudeLLMConfig(unittest.TestCase):
    def setUp(self) -> None:
        yaml_path = Path(__file__).resolve().parents[4] / 'agentuniverse' / 'llm' / 'default' / 'claude_llm.yaml'
        self.config = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))

    def test_default_model_is_not_retired(self) -> None:
        self.assertNotIn(self.config['model_name'], RETIRED_CLAUDE_MODELS)

    def test_default_model_has_a_known_context_length(self) -> None:
        # max_context_length() looks the model up in a table when the yaml sets none.
        llm = ClaudeLLM(model_name=self.config['model_name'], api_key='ak')
        self.assertGreaterEqual(llm.max_context_length(), 200000)


if __name__ == '__main__':
    unittest.main()
