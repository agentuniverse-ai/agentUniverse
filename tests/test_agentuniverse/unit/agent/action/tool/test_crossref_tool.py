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
    "subtitle": ["An extended metadata example"],
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
    "ISSN": ["1234-5678", "8765-4321"],
    "ISBN": ["978-1-4028-9462-6"],
    "subject": ["Artificial Intelligence", "Medicine"],
    "language": "en",
    "volume": "12",
    "issue": "3",
    "page": "101-110",
    "is-referenced-by-count": 25,
    "references-count": 40,
    "funder": [
        {
            "name": "Example Research Foundation",
            "DOI": "10.13039/100000001",
            "award": ["GRANT-123"],
        }
    ],
    "license": [
        {
            "URL": "https://creativecommons.org/licenses/by/4.0/",
            "start": {"date-parts": [[2025, 8, 13]]},
            "content-version": "vor",
            "delay-in-days": 0,
        }
    ],
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
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["offset"], 0)
        self.assertEqual(result["cursor"], "")
        self.assertEqual(result["sort"], "relevance")
        self.assertEqual(result["order"], "desc")
        self.assertEqual(result["from_pub_date"], "")
        self.assertEqual(result["until_pub_date"], "")
        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["next_cursor"], "")
        self.assertEqual(
            result["works"][0],
            {
                "doi": "10.1000/example",
                "title": "Example scholarly work",
                "subtitle": "An extended metadata example",
                "authors": ["Alice Smith", "Example Research Consortium"],
                "abstract": "Useful abstract text.",
                "container_title": "Example Journal",
                "published": "2025-08-13",
                "publisher": "Example Publisher",
                "type": "journal-article",
                "url": "https://doi.org/10.1000/example",
                "issn": ["1234-5678", "8765-4321"],
                "isbn": ["978-1-4028-9462-6"],
                "subjects": ["Artificial Intelligence", "Medicine"],
                "language": "en",
                "volume": "12",
                "issue": "3",
                "pages": "101-110",
                "citation_count": 25,
                "reference_count": 40,
                "funders": [
                    {
                        "name": "Example Research Foundation",
                        "doi": "10.13039/100000001",
                        "awards": ["GRANT-123"],
                    }
                ],
                "licenses": [
                    {
                        "url": "https://creativecommons.org/licenses/by/4.0/",
                        "start_date": "2025-08-13",
                        "content_version": "vor",
                        "delay_in_days": 0,
                    }
                ],
            },
        )

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.crossref.org/v1/works")
        self.assertEqual(request.kwargs["params"]["query.bibliographic"], "AI medicine")
        self.assertEqual(request.kwargs["params"]["rows"], 3)
        self.assertEqual(request.kwargs["params"]["offset"], 0)
        self.assertEqual(request.kwargs["params"]["sort"], "relevance")
        self.assertEqual(request.kwargs["params"]["order"], "desc")
        self.assertNotIn("filter", request.kwargs["params"])
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
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["offset"], 0)
        self.assertEqual(result["sort"], "")
        self.assertEqual(result["order"], "")
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["works"][0]["doi"], "10.1000/example")
        self.assertEqual(
            mock_get.call_args.args[0],
            "https://api.crossref.org/v1/works/10.1000%2Fexample",
        )

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_search_maps_paging_sorting_and_date_filters(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {"total-results": 100, "items": []},
            }
        )

        result = self.tool.execute(
            query="AI medicine",
            max_results=4,
            page=3,
            sort="citation_count",
            order="ASC",
            from_pub_date="2024-01",
            until_pub_date="2025-06-30",
        )

        self.assertEqual(result["page"], 3)
        self.assertEqual(result["offset"], 8)
        self.assertEqual(result["sort"], "is-referenced-by-count")
        self.assertEqual(result["order"], "asc")
        self.assertEqual(result["from_pub_date"], "2024-01")
        self.assertEqual(result["until_pub_date"], "2025-06-30")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["offset"], 8)
        self.assertEqual(params["sort"], "is-referenced-by-count")
        self.assertEqual(params["order"], "asc")
        self.assertEqual(params["filter"], "from-pub-date:2024-01,until-pub-date:2025-06-30")

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_search_supports_one_sided_date_filter(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {"total-results": 0, "items": []},
            }
        )

        self.tool.execute(query="AI medicine", until_pub_date="2020")

        self.assertEqual(mock_get.call_args.kwargs["params"]["filter"], "until-pub-date:2020")

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_search_uses_cursor_for_deep_pagination(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "status": "ok",
                "message-type": "work-list",
                "message": {
                    "total-results": 100000,
                    "items": [],
                    "next-cursor": "next-cursor-token",
                },
            }
        )

        result = self.tool.execute(query="AI medicine", max_results=20, cursor="*")

        self.assertEqual(result["cursor"], "*")
        self.assertEqual(result["offset"], 0)
        self.assertEqual(result["next_cursor"], "next-cursor-token")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["cursor"], "*")
        self.assertNotIn("offset", params)

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
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="AI", page=0)
        with self.assertRaisesRegex(ValueError, "offset below 10000"):
            self.tool.execute(query="AI", max_results=20, page=501)
        with self.assertRaisesRegex(ValueError, "page must be 1"):
            self.tool.execute(query="AI", page=2, cursor="*")
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            self.tool.execute(query="AI", cursor=" ")
        with self.assertRaisesRegex(ValueError, "sort must be one of"):
            self.tool.execute(query="AI", sort="citations")
        with self.assertRaisesRegex(ValueError, "order must be one of"):
            self.tool.execute(query="AI", order="newest")
        with self.assertRaisesRegex(ValueError, "YYYY"):
            self.tool.execute(query="AI", from_pub_date="2025/01/01")
        with self.assertRaisesRegex(ValueError, "valid date"):
            self.tool.execute(query="AI", until_pub_date="2025-02-30")
        with self.assertRaisesRegex(ValueError, "must not be later"):
            self.tool.execute(query="AI", from_pub_date="2025-02", until_pub_date="2025-01")
        with self.assertRaisesRegex(ValueError, "valid DOI"):
            self.tool.execute(query="not-a-doi", mode="doi")

    def test_missing_metadata_returns_empty_values(self) -> None:
        work = CrossrefTool._parse_work({"DOI": "10.1000/minimal"})

        self.assertEqual(work["doi"], "10.1000/minimal")
        self.assertEqual(work["title"], "")
        self.assertEqual(work["subtitle"], "")
        self.assertEqual(work["authors"], [])
        self.assertEqual(work["abstract"], "")
        self.assertEqual(work["container_title"], "")
        self.assertEqual(work["published"], "")
        self.assertEqual(work["publisher"], "")
        self.assertEqual(work["type"], "")
        self.assertEqual(work["url"], "https://doi.org/10.1000/minimal")
        self.assertEqual(work["issn"], [])
        self.assertEqual(work["isbn"], [])
        self.assertEqual(work["subjects"], [])
        self.assertEqual(work["language"], "")
        self.assertEqual(work["volume"], "")
        self.assertEqual(work["issue"], "")
        self.assertEqual(work["pages"], "")
        self.assertEqual(work["citation_count"], 0)
        self.assertEqual(work["reference_count"], 0)
        self.assertEqual(work["funders"], [])
        self.assertEqual(work["licenses"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["works"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.crossref_tool.requests.get")
    def test_error_response_preserves_search_context(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(
            query="AI medicine",
            max_results=2,
            page=2,
            sort="published_online",
            order="asc",
            from_pub_date="2024",
        )

        self.assertEqual(result["page"], 2)
        self.assertEqual(result["offset"], 2)
        self.assertEqual(result["sort"], "published-online")
        self.assertEqual(result["order"], "asc")
        self.assertEqual(result["from_pub_date"], "2024")

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
        for parameter in (
            "query",
            "mode",
            "max_results",
            "page",
            "cursor",
            "sort",
            "order",
            "from_pub_date",
            "until_pub_date",
        ):
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
            "subtitle",
            "ISSN",
            "ISBN",
            "subjects",
            "language",
            "volume",
            "issue",
            "pages",
            "citation count",
            "reference count",
            "funders",
            "licenses",
        ):
            self.assertIn(metadata_field, description)
        self.assertIn("offset must remain below 10000", description)
        self.assertIn("next_cursor", description)
        self.assertIn("YYYY, YYYY-MM, or YYYY-MM-DD", description)
        self.assertIn("CROSSREF_EMAIL", description)


if __name__ == "__main__":
    unittest.main()
