#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.crossref_tool import CrossrefTool


SAMPLE_WORK = {
    "DOI": "10.1000/example",
    "title": ["Example <i>scholarly</i> work"],
    "author": [
        {"given": "Alice", "family": "Smith"},
        {"name": "Example Research Consortium"},
    ],
    "abstract": "<jats:p>Useful <jats:bold>abstract</jats:bold> text.</jats:p>",
    "container-title": ["Example Journal"],
    "published": {"date-parts": [[2025, 8, 13]]},
    "publisher": "Example Publisher",
    "type": "journal-article",
    "URL": "https://doi.org/10.1000/example",
}


def response_mock(*, json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class CrossrefToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = CrossrefTool(email="developer@example.com")

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_search_returns_structured_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {"total-results": 42, "items": [SAMPLE_WORK]},
            }
        )

        result = self.tool.execute(query="AI medicine", max_results=3)

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "AI medicine")
        self.assertEqual(result["max_results"], 3)
        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(
            result["works"][0],
            {
                "doi": "10.1000/example",
                "title": "Example scholarly work",
                "authors": ["Alice Smith", "Example Research Consortium"],
                "abstract": "Useful abstract text.",
                "container_title": "Example Journal",
                "published": "2025-08-13",
                "publisher": "Example Publisher",
                "type": "journal-article",
                "url": "https://doi.org/10.1000/example",
            },
        )

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.crossref.org/v1/works")
        self.assertEqual(request.kwargs["params"]["query.bibliographic"], "AI medicine")
        self.assertEqual(request.kwargs["params"]["rows"], 3)
        self.assertEqual(request.kwargs["params"]["mailto"], "developer@example.com")
        self.assertIn("mailto:developer@example.com", request.kwargs["headers"]["User-Agent"])
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_doi_lookup_normalizes_url_and_returns_one_work(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work",
                "message": SAMPLE_WORK,
            }
        )

        result = self.tool.execute(
            query="https://doi.org/10.1000/example",
            mode="DOI",
            max_results=20,
        )

        self.assertEqual(result["mode"], "doi")
        self.assertEqual(result["query"], "10.1000/example")
        self.assertEqual(result["max_results"], 1)
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["works"][0]["doi"], "10.1000/example")
        self.assertEqual(
            mock_get.call_args.args[0],
            "https://api.crossref.org/v1/works/10.1000%2Fexample",
        )

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_empty_search_returns_no_works(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {"total-results": 0, "items": []},
            }
        )

        result = self.tool.execute(query="no matching work")

        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["returned_results"], 0)
        self.assertEqual(result["works"], [])

    def test_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query="  ")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="AI", mode="detail")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="AI", max_results=0)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="AI", max_results=True)
        with self.assertRaisesRegex(ValueError, "valid DOI"):
            self.tool.execute(query="not-a-doi", mode="doi")

    def test_missing_metadata_returns_empty_values(self) -> None:
        work = CrossrefTool._parse_work({"DOI": "10.1000/minimal"})

        self.assertEqual(work["doi"], "10.1000/minimal")
        self.assertEqual(work["title"], "")
        self.assertEqual(work["authors"], [])
        self.assertEqual(work["abstract"], "")
        self.assertEqual(work["container_title"], "")
        self.assertEqual(work["published"], "")
        self.assertEqual(work["publisher"], "")
        self.assertEqual(work["type"], "")
        self.assertEqual(work["url"], "https://doi.org/10.1000/minimal")

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["works"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_http_error_returns_structured_error(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertIn("429", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_connection_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("connection failed")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_error")
        self.assertIn("connection failed", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_api_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "failed",
                "message-type": "validation-failure",
                "message": [{"message": "Invalid query parameter"}],
            }
        )

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("Invalid query parameter", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_invalid_json_returns_structured_error(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = response

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid Crossref JSON response", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_invalid_message_shape_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {"total-results": 1, "items": "not-a-list"},
            }
        )

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid search items", result["error"]["message"])

    def test_shipped_config_exposes_modes_and_metadata(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "crossref_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        description = config["description"]
        for parameter in ("query", "mode", "max_results"):
            self.assertIn(parameter, description)
        for mode in ("search", "doi"):
            self.assertIn(mode, description)
        for metadata_field in (
            "DOI",
            "title",
            "authors",
            "abstract",
            "container title",
            "publication date",
            "publisher",
            "work type",
            "URL",
        ):
            self.assertIn(metadata_field, description)
        self.assertIn("CROSSREF_EMAIL", description)


if __name__ == "__main__":
    unittest.main()
