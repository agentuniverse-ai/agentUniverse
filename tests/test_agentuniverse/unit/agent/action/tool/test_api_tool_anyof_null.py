import unittest

from agentuniverse.agent.action.tool.api_tool import APITool


class APIToolAnyOfNullTest(unittest.TestCase):

    def test_any_of_null_does_not_convert_falsey_values(self):
        tool = APITool()
        schema = [{"type": "null"}, {"type": "integer"}]

        self.assertEqual(0, tool.convert_body_property_any_of({}, 0, schema))
        self.assertEqual("", tool.convert_body_property_any_of({}, "", schema))
        self.assertIsNone(tool.convert_body_property_any_of({}, None, schema))


if __name__ == "__main__":
    unittest.main()
