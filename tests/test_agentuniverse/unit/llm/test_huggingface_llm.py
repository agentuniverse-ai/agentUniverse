# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/08/05
# @FileName: test_huggingface_llm.py

"""Unit tests of the native huggingface_hub based LLM component, fully mocked."""

import asyncio
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

from agentuniverse.llm.default.huggingface_llm import HuggingFaceLLM


def _chat_output(content='hello', role='assistant', prompt_tokens=3, completion_tokens=2):
    message = types.SimpleNamespace(content=content, role=role)
    choice = types.SimpleNamespace(message=message)
    usage = types.SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    return types.SimpleNamespace(choices=[choice], usage=usage)


def _chat_chunk(content):
    delta = types.SimpleNamespace(content=content)
    return types.SimpleNamespace(choices=[types.SimpleNamespace(delta=delta)], usage=None)


def _tg_chunk(text):
    return types.SimpleNamespace(token=types.SimpleNamespace(text=text))


async def _aiter(items):
    for item in items:
        yield item


class HuggingFaceLLMTest(unittest.TestCase):

    def setUp(self):
        self.llm = HuggingFaceLLM(model_name='Qwen/Qwen2.5-7B-Instruct',
                                  huggingface_api_key='token', max_tokens=64, temperature=0.5)

    # ---------------- client construction ----------------

    def test_client_args_with_model_and_provider(self):
        llm = HuggingFaceLLM(model_name='m', huggingface_api_key='k', provider='together')
        args = llm._client_args()
        self.assertEqual(args['model'], 'm')
        self.assertEqual(args['provider'], 'together')
        self.assertNotIn('base_url', args)

    def test_client_args_base_url_excludes_model(self):
        llm = HuggingFaceLLM(model_name='m', huggingface_base_url='http://tgi:8080',
                             huggingface_api_key='k')
        args = llm._client_args()
        self.assertEqual(args['base_url'], 'http://tgi:8080')
        self.assertNotIn('model', args)

    def test_client_args_requires_model_or_base_url(self):
        with self.assertRaises(ValueError):
            HuggingFaceLLM(huggingface_api_key='k')._client_args()

    def test_api_key_falls_back_to_hf_token(self):
        with patch.dict('os.environ', {'HF_TOKEN': 'from-hf-token'}, clear=True):
            self.assertEqual(HuggingFaceLLM(model_name='m').huggingface_api_key, 'from-hf-token')

    def test_missing_huggingface_hub_raises_import_error(self):
        with patch.dict(sys.modules, {'huggingface_hub': None}):
            with self.assertRaises(ImportError):
                HuggingFaceLLM(model_name='m', huggingface_api_key='k')._new_client()

    # ---------------- argument building ----------------

    def test_chat_args_always_send_model_name(self):
        llm = HuggingFaceLLM(model_name='m', huggingface_base_url='http://tgi:8080')
        self.assertEqual(llm._chat_args(None, False, {})['model'], 'm')

    def test_chat_args_drop_none_and_keep_stop(self):
        args = self.llm._chat_args(['<end>'], True, {})
        self.assertEqual(args['stop'], ['<end>'])
        self.assertTrue(args['stream'])
        self.assertEqual(args['max_tokens'], 64)
        self.assertNotIn('seed', args)

    def test_chat_args_put_native_params_in_extra_body(self):
        llm = HuggingFaceLLM(model_name='m', top_k=10, repetition_penalty=1.1, do_sample=True)
        args = llm._chat_args(None, False, {})
        self.assertEqual(args['extra_body'],
                         {'top_k': 10, 'repetition_penalty': 1.1, 'do_sample': True})
        self.assertNotIn('top_k', args)

    def test_text_generation_args_pass_native_params(self):
        llm = HuggingFaceLLM(model_name='m', huggingface_base_url='http://tgi:8080',
                             task='text_generation', max_tokens=32, top_k=10,
                             repetition_penalty=1.1, do_sample=True, seed=7)
        args = llm._text_generation_args(None, False, {})
        self.assertEqual(args['max_new_tokens'], 32)
        self.assertEqual(args['top_k'], 10)
        self.assertEqual(args['repetition_penalty'], 1.1)
        self.assertTrue(args['do_sample'])
        self.assertEqual(args['seed'], 7)
        self.assertNotIn('model', args)

    def test_as_prompt_flattens_messages(self):
        self.assertEqual(
            HuggingFaceLLM.as_prompt([{'role': 'system', 'content': 'a'},
                                      {'role': 'user', 'content': 'b'}, 'c']),
            'a\nb\nc')

    # ---------------- chat task ----------------

    def test_call_chat_returns_llm_output(self):
        client = MagicMock()
        client.chat_completion.return_value = _chat_output('hi there')
        self.llm.client = client
        output = self.llm._call([{'role': 'user', 'content': 'hi'}])
        self.assertEqual(output.text, 'hi there')
        self.assertEqual(output.message.type, 'assistant')
        self.assertEqual(output.usage.total_tokens, 5)

    def test_call_chat_streaming(self):
        client = MagicMock()
        client.chat_completion.return_value = iter([_chat_chunk('a'), _chat_chunk('b')])
        self.llm.client = client
        self.assertEqual(''.join(o.text for o in self.llm._call([], streaming=True)), 'ab')

    def test_acall_chat(self):
        client = MagicMock()

        async def _chat(**kwargs):
            return _chat_output('async hi')

        client.chat_completion = _chat
        self.llm.async_client = client
        output = asyncio.run(self.llm._acall([{'role': 'user', 'content': 'hi'}]))
        self.assertEqual(output.text, 'async hi')

    def test_acall_chat_streaming(self):
        client = MagicMock()

        async def _chat(**kwargs):
            return _aiter([_chat_chunk('x'), _chat_chunk('y')])

        client.chat_completion = _chat
        self.llm.async_client = client

        async def _run():
            stream = await self.llm._acall([], streaming=True)
            return ''.join([chunk.text async for chunk in stream])

        self.assertEqual(asyncio.run(_run()), 'xy')

    # ---------------- text generation task ----------------

    def test_call_text_generation(self):
        client = MagicMock()
        client.text_generation.return_value = 'generated'
        llm = HuggingFaceLLM(model_name='m', task='text_generation', client=client)
        output = llm._call([{'role': 'user', 'content': 'prompt'}])
        self.assertEqual(output.text, 'generated')
        self.assertEqual(client.text_generation.call_args[0][0], 'prompt')

    def test_call_text_generation_streaming(self):
        client = MagicMock()
        client.text_generation.return_value = iter([_tg_chunk('1'), _tg_chunk('2')])
        llm = HuggingFaceLLM(model_name='m', task='text_generation', client=client)
        self.assertEqual(''.join(o.text for o in llm._call([], streaming=True)), '12')

    def test_acall_text_generation_streaming(self):
        client = MagicMock()

        async def _tg(prompt, **kwargs):
            return _aiter([_tg_chunk('p'), _tg_chunk('q')])

        client.text_generation = _tg
        llm = HuggingFaceLLM(model_name='m', task='text_generation', async_client=client)

        async def _run():
            stream = await llm._acall([], streaming=True)
            return ''.join([chunk.text async for chunk in stream])

        self.assertEqual(asyncio.run(_run()), 'pq')

    # ---------------- misc ----------------

    def test_max_context_length_known_and_default(self):
        self.assertEqual(HuggingFaceLLM(model_name='Qwen/Qwen2.5-7B-Instruct').max_context_length(),
                         32768)
        self.assertEqual(HuggingFaceLLM(model_name='unknown/model').max_context_length(), 4096)

    def test_as_langchain_returns_native_instance(self):
        from agentuniverse.llm.huggingface_langchain_instance import HuggingFaceLangchainInstance
        self.assertIsInstance(self.llm.as_langchain(), HuggingFaceLangchainInstance)

    def test_langchain_instance_delegates_to_component(self):
        from langchain_core.messages import HumanMessage
        from agentuniverse.llm.huggingface_langchain_instance import HuggingFaceLangchainInstance
        llm = MagicMock()
        llm.call.return_value = types.SimpleNamespace(text='delegated')
        result = HuggingFaceLangchainInstance(llm).invoke([HumanMessage(content='hi')])
        self.assertEqual(result.content, 'delegated')
        self.assertEqual(llm.call.call_args.kwargs['messages'],
                         [{'role': 'user', 'content': 'hi'}])


if __name__ == '__main__':
    unittest.main()
