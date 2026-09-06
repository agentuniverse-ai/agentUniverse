#
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import subprocess
import sys
import unittest

import agentuniverse
from agentuniverse.base.util.prompt_util import split_text_on_tokens

_REPO_ROOT = os.path.dirname(os.path.dirname(agentuniverse.__file__))


class TestSplitTextOnTokens(unittest.TestCase):
    def test_empty_text_returns_itself(self) -> None:
        self.assertEqual(split_text_on_tokens('', 0), [''])

    def test_returns_when_chunk_size_not_larger_than_overlap(self) -> None:
        """A chunk size smaller than the overlap must not hang the splitter.

        Runs the call in a subprocess so the unfixable infinite loop shows up
        as a test failure instead of a hung/OOM-ing test process.
        """
        code = (
            "from agentuniverse.base.util.prompt_util import split_text_on_tokens;"
            "chunks = split_text_on_tokens('x' * 2000, 2000,"
            " chunk_size=48, chunk_overlap=100);"
            "assert all(chunks), chunks"
        )
        completed = subprocess.run(
            [sys.executable, '-c', code],
            cwd=_REPO_ROOT, timeout=10, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_normal_splitting_is_preserved(self) -> None:
        chunks = split_text_on_tokens('a' * 100, 100, chunk_size=10, chunk_overlap=2)
        self.assertEqual(chunks[0], 'a' * 10)
        self.assertEqual(len(chunks[-1]), 4)
        self.assertTrue(all('a' * 4 in chunk for chunk in chunks))


if __name__ == '__main__':
    unittest.main()
