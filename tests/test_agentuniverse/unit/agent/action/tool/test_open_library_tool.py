#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.open_library_tool import OpenLibraryTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


def response_mock(json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class OpenLibraryToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = OpenLibraryTool()

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_keyword_search_returns_normalized_books(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            {
                "numFound": 42,
                "docs": [
                    {
                        "key": "/works/OL27448W",
                        "title": "The Hobbit",
                        "subtitle": "There and Back Again",
                        "author_name": ["J. R. R. Tolkien"],
                        "author_key": ["OL26320A"],
                        "isbn": ["9780261102217"],
                        "publisher": ["George Allen & Unwin"],
                        "language": ["eng"],
                        "first_publish_year": 1937,
                        "publish_year": [1937, 1951],
                        "edition_count": 321,
                        "cover_i": 10521270,
                        "subject": ["Fantasy fiction"],
                        "ebook_access": "borrowable",
                    }
                ],
            }
        )

        result = self.tool.execute(query="hobbit adventure", max_results=3, page=2)

        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["offset"], 3)
        self.assertEqual(
            result["books"][0],
            {
                "work_key": "/works/OL27448W",
                "title": "The Hobbit",
                "subtitle": "There and Back Again",
                "authors": ["J. R. R. Tolkien"],
                "author_keys": ["OL26320A"],
                "isbn": ["9780261102217"],
                "publishers": ["George Allen & Unwin"],
                "languages": ["eng"],
                "first_publish_year": 1937,
                "publish_years": [1937, 1951],
                "edition_count": 321,
                "subjects": ["Fantasy fiction"],
                "ebook_access": "borrowable",
                "cover_url": "https://covers.openlibrary.org/b/id/10521270-L.jpg",
                "work_url": "https://openlibrary.org/works/OL27448W",
            },
        )
        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://openlibrary.org/search.json")
        self.assertEqual(request.kwargs["params"]["q"], "hobbit adventure")
        self.assertEqual(request.kwargs["params"]["page"], 2)
        self.assertEqual(request.kwargs["params"]["limit"], 3)
        self.assertIn("title", request.kwargs["params"]["fields"])
        self.assertEqual(request.kwargs["headers"]["Accept"], "application/json")
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_field_search_builds_server_side_filters(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock({"numFound": 0, "docs": []})

        result = self.tool.execute(
            query='Tolkien: "Author"',
            search_field="AUTHOR",
            from_year=1930,
            until_year=1950,
            language="ENG",
        )

        self.assertEqual(result["from_year"], 1930)
        self.assertEqual(result["until_year"], 1950)
        self.assertEqual(result["language"], "eng")
        query = mock_get.call_args.kwargs["params"]["q"]
        self.assertEqual(
            query,
            r'author:"Tolkien\: \"Author\"" AND first_publish_year:[1930 TO 1950] AND language:"eng"',
        )

    def test_query_escaping_includes_backslashes(self) -> None:
        escaped = OpenLibraryTool._escape_query_value(r"C:\Books\AI")
        self.assertEqual(escaped, r"C\:\\Books\\AI")

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_isbn_search_normalizes_valid_isbn(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock({"numFound": 1, "docs": []})

        result = self.tool.execute(query="978-0-261-10221-7", search_field="isbn")

        self.assertEqual(result["query"], "9780261102217")
        self.assertEqual(mock_get.call_args.kwargs["params"]["q"], 'isbn:"9780261102217"')

    def test_input_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query=" ")
        with self.assertRaisesRegex(ValueError, "search_field must be one of"):
            self.tool.execute(query="book", search_field="subject")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="book", max_results=21)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="book", max_results=True)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="book", page=0)
        with self.assertRaisesRegex(ValueError, "offset below 10000"):
            self.tool.execute(query="book", max_results=20, page=502)
        with self.assertRaisesRegex(ValueError, "from_year must be an integer"):
            self.tool.execute(query="book", from_year="2000")
        with self.assertRaisesRegex(ValueError, "from_year must not be later"):
            self.tool.execute(query="book", from_year=2025, until_year=2020)
        with self.assertRaisesRegex(ValueError, "ISO 639-2"):
            self.tool.execute(query="book", language="en")
        with self.assertRaisesRegex(ValueError, "valid ISBN"):
            self.tool.execute(query="9780261102218", search_field="isbn")

    def test_isbn10_checksum_accepts_x(self) -> None:
        self.assertEqual(self.tool._normalize_isbn("0-8044-2957-X"), "080442957X")

    def test_repeated_fields_are_bounded(self) -> None:
        book = self.tool._parse_book({"isbn": [str(index) for index in range(30)]})
        self.assertEqual(len(book["isbn"]), 20)
        self.assertEqual(book["work_url"], "")
        self.assertEqual(book["cover_url"], "")

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="artificial intelligence")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["books"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_http_and_connection_errors_are_sanitized(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError("sensitive request details", response=response)
        http_result = self.tool.execute(query="book")
        self.assertEqual(http_result["error"]["message"], "Open Library returned HTTP status 429.")

        mock_get.side_effect = requests.ConnectionError("sensitive proxy details")
        request_result = self.tool.execute(query="book")
        self.assertEqual(request_result["error"]["message"], "Open Library request failed.")

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_invalid_json_and_shape_return_structured_errors(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("bad", "", 0)
        mock_get.return_value = response
        invalid_json = self.tool.execute(query="book")
        self.assertEqual(invalid_json["error"]["type"], "invalid_response")

        mock_get.return_value = response_mock({"numFound": 1, "docs": {}})
        invalid_shape = self.tool.execute(query="book")
        self.assertIn("search documents", invalid_shape["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_invalid_document_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock({"numFound": 1, "docs": ["invalid"]})
        result = self.tool.execute(query="book")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_shipped_yaml_documents_contract(self) -> None:
        config_path = self._config_path()
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        self.assertEqual(config["metadata"]["class"], "OpenLibraryTool")
        description = config["description"]
        for term in (
            "query",
            "search_field",
            "keyword",
            "title",
            "author",
            "isbn",
            "max_results",
            "page",
            "from_year",
            "until_year",
            "language",
        ):
            self.assertIn(term, description)

    @patch("agentuniverse.agent.action.tool.common_tool.open_library_tool.requests.get")
    def test_shipped_config_initializes_tool(self, mock_get: Mock) -> None:
        configer = Configer(str(self._config_path())).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = OpenLibraryTool().initialize_by_component_configer(tool_configer)
        mock_get.return_value = response_mock({"numFound": 0, "docs": []})

        result = tool.execute(query="configuration pipeline")

        self.assertEqual(tool.name, "open_library_tool")
        self.assertEqual(tool.input_keys, ["query"])
        self.assertEqual(result["books"], [])

    @staticmethod
    def _config_path() -> Path:
        return (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "open_library_tool.yaml"
        )


if __name__ == "__main__":
    unittest.main()
