import unittest
from unittest.mock import Mock, patch

from agentuniverse.agent.action.tool.api_tool import APITool


class TestAPIToolPathParameters(unittest.TestCase):
    def test_path_parameters_are_percent_encoded_as_single_segments(self):
        tool = APITool(
            openapi_spec={
                "operation": {
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True},
                        {"name": "include", "in": "query"},
                    ]
                }
            }
        )
        response = Mock()
        value = "a/b ?#中文%"

        with patch("agentuniverse.agent.action.tool.api_tool.ssrf_proxy.get", return_value=response) as request:
            result = tool.do_http_request(
                "https://example.com/items/{item_id}",
                "GET",
                {},
                {"item_id": value, "include": "metadata"},
            )

        self.assertIs(result, response)
        request.assert_called_once_with(
            "https://example.com/items/a%2Fb%20%3F%23%E4%B8%AD%E6%96%87%25",
            params={"include": "metadata"},
            headers={},
            data={},
            follow_redirects=True,
        )


if __name__ == "__main__":
    unittest.main()
