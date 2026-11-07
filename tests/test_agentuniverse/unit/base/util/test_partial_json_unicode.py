"""Keep recoverable string prefixes when a JSON stream cuts a Unicode escape."""
import unittest

from agentuniverse.base.util.common_util import (
    parse_and_check_json_markdown,
    parse_partial_json,
)


class PartialJsonUnicodeTests(unittest.TestCase):
    def test_incomplete_unicode_escape_keeps_field(self):
        for tail in ("", "4", "4F", "4F6"):
            for strict in (False, True):
                with self.subTest(tail=tail, strict=strict):
                    source = '{"text": "prefix' + "\\u" + tail
                    self.assertEqual(parse_partial_json(source, strict=strict),
                                     {"text": "prefix"})

    def test_nested_field_and_prior_values_are_preserved(self):
        source = r'{"id": 7, "payload": {"text": "prefix\u4F'
        self.assertEqual(parse_partial_json(source),
                         {"id": 7, "payload": {"text": "prefix"}})

    def test_array_keeps_incomplete_string_value(self):
        source = r'{"items": ["done", "prefix\u4F'
        self.assertEqual(parse_partial_json(source),
                         {"items": ["done", "prefix"]})

    def test_top_level_string_prefix_is_recoverable(self):
        self.assertEqual(parse_partial_json(r'"prefix\u4F'), "prefix")

    def test_tool_input_validation_keeps_recovered_field(self):
        source = r'{"text": "prefix\u4F'
        self.assertEqual(parse_and_check_json_markdown(source, ["text"]),
                         {"text": "prefix"})

    def test_complete_escapes_and_literal_backslashes_are_unchanged(self):
        self.assertEqual(parse_partial_json(r'{"text": "\u4F60\u597D"}'),
                         {"text": "你好"})
        self.assertEqual(parse_partial_json(r'{"text": "prefix\\u4'),
                         {"text": r"prefix\u4"})
        self.assertIsNone(parse_partial_json('{"text": "prefix"]'))

    def test_backslash_parity_and_incomplete_key_fallback(self):
        for count in range(1, 6):
            with self.subTest(backslashes=count):
                source = '{"text": "prefix' + "\\" * count + "u4"
                expected = "prefix" + "\\" * (count // 2)
                if count % 2 == 0:
                    expected += "u4"
                self.assertEqual(parse_partial_json(source), {"text": expected})
        self.assertEqual(parse_partial_json(r'{"prefix\u4'), {})


if __name__ == "__main__":
    unittest.main()
