#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import anthropic

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


class TestClaudeLLMTemperature(unittest.TestCase):
    """ClaudeLLM must not force a sampling temperature that the user never set.

    Current Claude models (Opus 4.7+, Sonnet 5/5.5, Haiku 5.5) reject any
    sampling parameter with a 400 ``invalid_request_error``. ``ClaudeLLM``
    previously inherited the ``LLM`` base default of ``temperature=0.5`` and
    always forwarded it to ``messages.create``, so every call to those models
    failed. The default is now ``None`` and is translated to
    ``anthropic.NOT_GIVEN`` so the field is omitted unless the caller set one.
    """

    def setUp(self) -> None:
        self.stub_client = MagicMock()
        self.stub_client.messages.create = MagicMock(
            return_value=MagicMock(content=[MagicMock(text='hi')]))
        self.stub_client.close = MagicMock()

    def _temperature_from_call(self) -> object:
        _, kwargs = self.stub_client.messages.create.call_args
        return kwargs.get('temperature')

    def test_default_temperature_is_none(self) -> None:
        llm = ClaudeLLM(model_name='claude-sonnet-5-5', api_key='ak')
        self.assertIsNone(llm.temperature)

    def test_call_omits_temperature_when_unset(self) -> None:
        llm = ClaudeLLM(model_name='claude-sonnet-5-5', api_key='ak')
        with patch.object(ClaudeLLM, '_new_client', return_value=self.stub_client):
            llm._call(messages=[{'role': 'user', 'content': 'hi'}])
        self.assertIs(self._temperature_from_call(), anthropic.NOT_GIVEN)

    def test_call_sends_configured_temperature(self) -> None:
        llm = ClaudeLLM(model_name='claude-3-5-sonnet-latest', api_key='ak',
                        temperature=0.3)
        with patch.object(ClaudeLLM, '_new_client', return_value=self.stub_client):
            llm._call(messages=[{'role': 'user', 'content': 'hi'}])
        self.assertEqual(self._temperature_from_call(), 0.3)

    def test_call_sends_kwargs_temperature_override(self) -> None:
        llm = ClaudeLLM(model_name='claude-3-5-sonnet-latest', api_key='ak')
        with patch.object(ClaudeLLM, '_new_client', return_value=self.stub_client):
            llm._call(messages=[{'role': 'user', 'content': 'hi'}], temperature=0.9)
        self.assertEqual(self._temperature_from_call(), 0.9)


if __name__ == '__main__':
    unittest.main()
