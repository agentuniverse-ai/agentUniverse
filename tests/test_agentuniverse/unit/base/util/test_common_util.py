#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest

from agentuniverse.base.util.common_util import parse_and_check_json_markdown


class TestParseAndCheckJsonMarkdown(unittest.TestCase):
    def test_accepts_json_object_with_expected_keys(self):
        result = parse_and_check_json_markdown(
            '{"answer": 42}',
            ["answer"],
        )

        self.assertEqual(result, {"answer": 42})

    def test_rejects_partial_parser_none_result_as_invalid_json(self):
        with self.assertRaisesRegex(
            ValueError,
            "Expected a JSON object",
        ):
            parse_and_check_json_markdown('{"answer":]', ["answer"])


if __name__ == "__main__":
    unittest.main()
