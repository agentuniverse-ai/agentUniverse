#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: test_runcrate_openai_style_llm.py
import json
import os
import unittest
from unittest.mock import patch

import httpx

from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.llm.default.runcrate_openai_style_llm import DefaultRuncrateLLM

RUNCRATE_ENV = ('RUNCRATE_API_KEY', 'RUNCRATE_API_BASE', 'RUNCRATE_PROXY', 'RUNCRATE_ORGANIZATION')


def _completion(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    return httpx.Response(200, request=request, json={
        'id': 'chatcmpl-test',
        'object': 'chat.completion',
        'created': 1,
        'model': body['model'],
        'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hello'}, 'finish_reason': 'stop'}],
        'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2},
    })


class TestRuncrateOpenAIStyleLLM(unittest.TestCase):
    def setUp(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in RUNCRATE_ENV}
        patcher = patch.dict(os.environ, env, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        ApplicationConfigManager().app_configer = AppConfiger()

    def test_defaults(self) -> None:
        llm = DefaultRuncrateLLM(model_name='deepseek-ai/DeepSeek-V4.1-Flash')
        self.assertEqual(llm.api_base, 'https://api.runcrate.ai/v1')
        self.assertIsNone(llm.api_key)

    def test_settings_from_environment(self) -> None:
        with patch.dict(os.environ, {'RUNCRATE_API_KEY': 'env-key', 'RUNCRATE_API_BASE': 'https://proxy.example/v1'}):
            llm = DefaultRuncrateLLM(model_name='deepseek-ai/DeepSeek-V4.1-Flash')
        self.assertEqual(llm.api_key, 'env-key')
        self.assertEqual(llm.api_base, 'https://proxy.example/v1')

    def test_explicit_settings_win(self) -> None:
        with patch.dict(os.environ, {'RUNCRATE_API_KEY': 'env-key'}):
            llm = DefaultRuncrateLLM(model_name='m', api_key='explicit-key', api_base='https://other.example/v1')
        self.assertEqual(llm.api_key, 'explicit-key')
        self.assertEqual(llm.api_base, 'https://other.example/v1')

    def test_call_posts_chat_completion_to_runcrate(self) -> None:
        llm = DefaultRuncrateLLM(model_name='deepseek-ai/DeepSeek-V4.1-Flash', api_key='test-key', max_tokens=16)
        sent = []

        def send(client: httpx.Client, request: httpx.Request, **kwargs) -> httpx.Response:
            sent.append(request)
            return _completion(request)

        with patch.object(httpx.Client, 'send', send):
            output = llm.call(messages=[{'role': 'user', 'content': 'Hi'}], streaming=False)

        self.assertEqual(output.text, 'Hello')
        self.assertEqual(len(sent), 1)
        self.assertEqual(str(sent[0].url), 'https://api.runcrate.ai/v1/chat/completions')
        self.assertEqual(sent[0].headers['authorization'], 'Bearer test-key')
        body = json.loads(sent[0].content)
        self.assertEqual(body['model'], 'deepseek-ai/DeepSeek-V4.1-Flash')
        self.assertEqual(body['messages'], [{'role': 'user', 'content': 'Hi'}])


if __name__ == '__main__':
    unittest.main()
