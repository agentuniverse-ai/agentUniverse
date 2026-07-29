#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.base.util.prompt_util import split_text_on_tokens


class TestSplitTextOnTokens(unittest.TestCase):
    def test_empty_text_does_not_divide_by_zero(self):
        self.assertEqual(split_text_on_tokens("", text_token=0), [""])


if __name__ == "__main__":
    unittest.main()
