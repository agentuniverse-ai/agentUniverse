#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import patch

from agentuniverse.llm.default.wenxin_llm import TokenModelList, WenXinLLM


class TestWenXinTokenModelList(unittest.TestCase):
    def test_documented_ernie_models_are_distinct_entries(self) -> None:
        for model in ('ernie-4.5-turbo-32k',
                      'ernie-4.5-8k-preview',
                      'ernie-4.0-8k',
                      'ernie-3.5-8k',
                      'ernie-speed-8k',
                      'ernie-speed-128k',
                      'ernie-lite-8k',
                      'ernie-tiny-8k',
                      'ernie-char-8k'):
            self.assertIn(model, TokenModelList)

    def test_get_num_tokens_selects_model_specific_tokenizer(self) -> None:
        llm = WenXinLLM(model_name='ernie-4.0-8k', api_key='ak', secret_key='sk')
        with patch('agentuniverse.llm.default.wenxin_llm.tokenizer.Tokenizer') as tokenizer_cls:
            tokenizer_cls.return_value.count_tokens.return_value = 7
            count = llm.get_num_tokens('hello world')
        self.assertEqual(count, 7)
        _, kwargs = tokenizer_cls.return_value.count_tokens.call_args
        self.assertEqual(kwargs.get('model'), 'ernie-4.0-8k')


if __name__ == '__main__':
    unittest.main()
