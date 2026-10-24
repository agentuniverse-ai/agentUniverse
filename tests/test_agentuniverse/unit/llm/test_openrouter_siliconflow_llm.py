#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : dxz0069
# @FileName: test_openrouter_siliconflow_llm.py

import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.openrouter_openai_style_llm import (
    OPENROUTER_API_BASE,
    DefaultOpenRouterLLM,
)
from agentuniverse.llm.default.siliconflow_openai_style_llm import DefaultSiliconFlowLLM
from agentuniverse.llm.llm_output import LLMOutput


def _chat_completion(text='hello'):
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.content = text
    completion.model_dump.return_value = {'choices': [{'message': {'content': text}}]}
    completion.dict.return_value = {'choices': [{'delta': {'content': text}}]}
    return completion


class TestSiliconFlowLLM(unittest.TestCase):
    """Test suite for the SiliconFlow LLM, run against a mocked client."""

    def test_defaults(self):
        llm = DefaultSiliconFlowLLM(api_key='sf-key')
        self.assertEqual(llm.api_base, 'https://api.siliconflow.cn/v1')
        self.assertEqual(llm.api_key, 'sf-key')

    def test_max_context_length(self):
        llm = DefaultSiliconFlowLLM(api_key='k', model_name='Qwen/Qwen2.5-72B-Instruct')
        self.assertEqual(llm.max_context_length(), 32768)
        unknown = DefaultSiliconFlowLLM(api_key='k', model_name='vendor/unknown-model')
        self.assertEqual(unknown.max_context_length(), 4096)
        configured = DefaultSiliconFlowLLM(api_key='k', model_name='vendor/unknown-model')
        configured._max_context_length = 999999
        self.assertEqual(configured.max_context_length(), 999999)

    def test_call_targets_siliconflow_endpoint(self):
        llm = DefaultSiliconFlowLLM(api_key='sf-key', model_name='deepseek-ai/DeepSeek-V3')
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = _chat_completion()
            result = llm._call([{'role': 'user', 'content': 'hi'}])
        client_kwargs = openai_cls.call_args.kwargs
        self.assertEqual(client_kwargs['api_key'], 'sf-key')
        self.assertEqual(client_kwargs['base_url'], 'https://api.siliconflow.cn/v1')
        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'deepseek-ai/DeepSeek-V3')
        self.assertIsInstance(result, LLMOutput)


class TestOpenRouterLLM(unittest.TestCase):
    """Test suite for the OpenRouter LLM, run against a mocked client."""

    def test_defaults(self):
        llm = DefaultOpenRouterLLM(api_key='or-key')
        self.assertEqual(llm.api_base, OPENROUTER_API_BASE)

    def test_max_context_length(self):
        llm = DefaultOpenRouterLLM(api_key='k', model_name='openai/gpt-4o')
        self.assertEqual(llm.max_context_length(), 128000)
        unknown = DefaultOpenRouterLLM(api_key='k', model_name='vendor/unknown-model')
        self.assertEqual(unknown.max_context_length(), 8192)

    def test_call_targets_openrouter_endpoint(self):
        llm = DefaultOpenRouterLLM(api_key='or-key', model_name='anthropic/claude-3.5-sonnet')
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = _chat_completion('hi from openrouter')
            result = llm._call([{'role': 'user', 'content': 'hi'}])
        client_kwargs = openai_cls.call_args.kwargs
        self.assertEqual(client_kwargs['api_key'], 'or-key')
        self.assertEqual(client_kwargs['base_url'], OPENROUTER_API_BASE)
        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['model'], 'anthropic/claude-3.5-sonnet')
        self.assertEqual(result.text, 'hi from openrouter')

    def test_extra_headers_flow_through(self):
        llm = DefaultOpenRouterLLM(
            api_key='or-key', model_name='openai/gpt-4o',
            ext_headers={'HTTP-Referer': 'https://my.app', 'X-Title': 'My App'})
        with patch('agentuniverse.llm.openai_style_llm.OpenAI') as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = _chat_completion()
            llm._call([{'role': 'user', 'content': 'hi'}])
        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs['extra_headers']['X-Title'], 'My App')


if __name__ == '__main__':
    unittest.main()
