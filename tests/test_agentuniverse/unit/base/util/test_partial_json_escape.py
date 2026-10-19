"""Preserve recovered string values when JSON ends inside an escape."""

import unittest

from agentuniverse.base.util.common_util import (
    parse_and_check_json_markdown,
    parse_partial_json,
)


class PartialJsonEscapeTests(unittest.TestCase):
    def test_incomplete_escape_preserves_value(self):
        for count in (1, 3, 5):
            with self.subTest(backslashes=count):
                source = '{"text": "abc' + '\\' * count
                self.assertEqual(
                    parse_partial_json(source),
                    {"text": "abc" + '\\' * (count // 2)},
                )

    def test_complete_escape_preserves_backslashes(self):
        for count in (0, 2, 4):
            with self.subTest(backslashes=count):
                source = '{"text": "abc' + '\\' * count
                self.assertEqual(
                    parse_partial_json(source),
                    {"text": "abc" + '\\' * (count // 2)},
                )

    def test_tool_key_validation_retains_recovered_input(self):
        source = '{"text": "abc' + '\\'
        self.assertEqual(
            parse_and_check_json_markdown(source, ["text"]),
            {"text": "abc"},
        )

    def test_complete_json_is_unchanged(self):
        self.assertEqual(parse_partial_json('{"text": "abc\\\\"}'),
                         {"text": "abc\\"})


if __name__ == "__main__":
    unittest.main()
