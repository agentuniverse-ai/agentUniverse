import unittest

from agentuniverse.base.util.system_util import process_yaml_func


class Extension:
    def __init__(self):
        self.calls = 0

    def choose(self, provider="default", *, enabled=True):
        self.calls += 1
        return provider, enabled


class TestFuncKeywordArguments(unittest.TestCase):
    def setUp(self):
        self.extension = Extension()

    def test_duplicate_keywords_are_rejected_before_execution(self):
        cases = [
            (
                '@FUNC(choose(provider="a", provider="b"))',
                "provider",
            ),
            (
                "@FUNC(choose(enabled=True, enabled=False))",
                "enabled",
            ),
            (
                '@FUNC(choose(provider="a", enabled=True, provider="b"))',
                "provider",
            ),
        ]
        for expression, name in cases:
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(
                    ValueError, f"Duplicate keyword argument '{name}'"
                ):
                    process_yaml_func(expression, self.extension)
                self.assertEqual(self.extension.calls, 0)

    def test_distinct_keywords_are_preserved(self):
        result = process_yaml_func(
            '@FUNC(choose(provider="a", enabled=False))',
            self.extension,
        )
        self.assertEqual(result, ("a", False))
        self.assertEqual(self.extension.calls, 1)

    def test_positional_argument_is_preserved(self):
        result = process_yaml_func(
            '@FUNC(choose("a"))', self.extension
        )
        self.assertEqual(result, ("a", True))

    def test_defaults_are_preserved(self):
        result = process_yaml_func(
            "@FUNC(choose())", self.extension
        )
        self.assertEqual(result, ("default", True))

    def test_positional_keyword_collision_remains_invalid(self):
        with self.assertRaises(ValueError):
            process_yaml_func(
                '@FUNC(choose("a", provider="b"))',
                self.extension,
            )
        self.assertEqual(self.extension.calls, 0)

    def test_unknown_keyword_remains_invalid(self):
        with self.assertRaises(ValueError):
            process_yaml_func(
                "@FUNC(choose(unknown=True))",
                self.extension,
            )
        self.assertEqual(self.extension.calls, 0)

    def test_plain_string_is_unchanged(self):
        self.assertEqual(
            process_yaml_func("plain text", self.extension),
            "plain text",
        )
        self.assertEqual(self.extension.calls, 0)


if __name__ == "__main__":
    unittest.main()
