import unittest

from agentuniverse.agent.action.tool.api_tool import APITool


class APIToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = APITool()

    def test_convert_boolean_values(self) -> None:
        cases = [
            (True, True),
            (False, False),
            ('true', True),
            ('false', False),
            ('1', True),
            ('0', False),
        ]

        for value, expected in cases:
            with self.subTest(value=value):
                result = self.tool.convert_body_property_type(
                    {'type': 'boolean'}, value
                )
                self.assertIs(result, expected)

    def test_invalid_boolean_value_is_preserved(self) -> None:
        result = self.tool.convert_body_property_type(
            {'type': 'boolean'}, 'not-a-boolean'
        )

        self.assertEqual(result, 'not-a-boolean')

    def test_convert_number_values(self) -> None:
        cases = [
            (1, 1),
            (1.5, 1.5),
            ('1', 1),
            ('1.5', 1.5),
        ]

        for value, expected in cases:
            with self.subTest(value=value):
                result = self.tool.convert_body_property_type(
                    {'type': 'number'}, value
                )
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
