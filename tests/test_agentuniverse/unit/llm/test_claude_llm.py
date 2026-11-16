#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

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


if __name__ == '__main__':
    unittest.main()
