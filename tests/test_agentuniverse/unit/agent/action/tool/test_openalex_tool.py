#!/usr/bin/env python3

import copy
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.openalex_tool import OpenAlexTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

SAMPLE_WORK = {
    "id": "https://openalex.org/W123",
    "doi": "https://doi.org/10.1000/example",
    "display_name": "Example multi-agent paper",
    "publication_year": 2025,
    "publication_date": "2025-08-01",
    "type": "article",
    "language": "en",
    "authorships": [
        {
            "author_position": "first",
            "author": {
                "id": "https://openalex.org/A1",
                "display_name": "Alice Smith",
                "orcid": "https://orcid.org/0000-0001-0000-0001",
            },
            "institutions": [
                {
                    "id": "https://openalex.org/I1",
                    "display_name": "Example University",
                    "country_code": "CN",
                }
            ],
            "is_corresponding": True,
        }
    ],
    "primary_location": {
        "landing_page_url": "https://doi.org/10.1000/example",
        "pdf_url": "https://example.org/paper.pdf",
        "source": {
            "id": "https://openalex.org/S1",
            "display_name": "Example Journal",
            "issn_l": "1234-5678",
            "type": "journal",
        },
    },
    "open_access": {
        "is_oa": True,
        "oa_status": "gold",
        "oa_url": "https://example.org/paper.pdf",
    },
    "cited_by_count": 42,
    "referenced_works_count": 21,
    "topics": [
        {
            "id": "https://openalex.org/T1",
            "display_name": "Multi-Agent Systems",
            "score": 0.98,
            "field": {"display_name": "Computer Science"},
            "domain": {"display_name": "Physical Sciences"},
        }
    ],
    "keywords": [
        {"display_name": "Artificial intelligence", "score": 0.9},
    ],
    "abstract_inverted_index": {
        "Agent": [0],
        "systems": [1],
        "cooperate.": [2],
    },
}


def response_mock(*, json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class OpenAlexToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = OpenAlexTool(
            api_key="test-api-key",
            email="developer@example.com",
        )

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_search_returns_normalized_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 100, "next_cursor": None},
                "results": [SAMPLE_WORK],
            }
        )

        result = self.tool.execute(query="multi-agent systems", max_results=3)

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "multi-agent systems")
        self.assertEqual(result["max_results"], 3)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["sort"], "relevance_score")
        self.assertEqual(result["order"], "desc")
        self.assertEqual(result["total_results"], 100)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["next_cursor"], "")

        work = result["works"][0]
        self.assertEqual(work["openalex_id"], "W123")
        self.assertEqual(work["doi"], "10.1000/example")
        self.assertEqual(work["title"], "Example multi-agent paper")
        self.assertEqual(work["abstract"], "Agent systems cooperate.")
        self.assertFalse(work["abstract_truncated"])
        self.assertEqual(work["publication_year"], 2025)
        self.assertEqual(work["citation_count"], 42)
        self.assertEqual(work["reference_count"], 21)
        self.assertEqual(work["authors"][0]["name"], "Alice Smith")
        self.assertEqual(work["authors"][0]["institutions"][0]["name"], "Example University")
        self.assertEqual(work["venue"]["name"], "Example Journal")
        self.assertTrue(work["open_access"]["is_open_access"])
        self.assertEqual(work["topics"][0]["field"], "Computer Science")
        self.assertEqual(work["keywords"][0]["name"], "Artificial intelligence")

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.openalex.org/works")
        self.assertEqual(request.kwargs["params"]["search"], "multi-agent systems")
        self.assertEqual(request.kwargs["params"]["per_page"], 3)
        self.assertEqual(request.kwargs["params"]["page"], 1)
        self.assertEqual(request.kwargs["params"]["sort"], "relevance_score:desc")
        self.assertEqual(request.kwargs["params"]["api_key"], "test-api-key")
        self.assertEqual(request.kwargs["params"]["mailto"], "developer@example.com")
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_search_maps_filters_sort_and_partial_dates(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"meta": {"count": 0}, "results": []})

        result = self.tool.execute(
            query="agent systems",
            max_results=4,
            page=3,
            sort="citation_count",
            order="ASC",
            from_publication_date="2020",
            to_publication_date="2025-02",
            work_type="Article",
            open_access_only=True,
            min_citation_count=10,
        )

        self.assertEqual(result["sort"], "cited_by_count")
        self.assertEqual(result["from_publication_date"], "2020-01-01")
        self.assertEqual(result["to_publication_date"], "2025-02-28")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["page"], 3)
        self.assertEqual(params["sort"], "cited_by_count:asc")
        self.assertEqual(
            params["filter"],
            "from_publication_date:2020-01-01,"
            "to_publication_date:2025-02-28,"
            "type:article,open_access.is_oa:true,cited_by_count:>9",
        )

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_anonymous_search_omits_optional_credentials_and_empty_filter(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"meta": {"count": 0}, "results": []})
        anonymous_tool = OpenAlexTool(api_key=None, email=None)

        result = anonymous_tool.execute(
            query="agents",
            min_citation_count=0,
            to_publication_date="2024-02",
        )

        self.assertEqual(result["to_publication_date"], "2024-02-29")
        params = mock_get.call_args.kwargs["params"]
        self.assertNotIn("api_key", params)
        self.assertNotIn("mailto", params)
        self.assertEqual(params["filter"], "to_publication_date:2024-02-29")
        self.assertNotIn("ids", params["select"].split(","))

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_cursor_paging_returns_next_cursor(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"meta": {"count": 50000, "next_cursor": "next-token"}, "results": []}
        )

        result = self.tool.execute(query="agents", max_results=20, cursor="*")

        self.assertEqual(result["cursor"], "*")
        self.assertEqual(result["next_cursor"], "next-token")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["cursor"], "*")
        self.assertNotIn("page", params)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_work_lookup_normalizes_supported_identifiers(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_WORK)
        inputs = (
            ("https://openalex.org/W123", "W123", "W123"),
            ("10.1000/example", "doi:10.1000/example", "doi:10.1000%2Fexample"),
            ("https://doi.org/10.1000/example", "doi:10.1000/example", "doi:10.1000%2Fexample"),
            ("PMID:29456894", "pmid:29456894", "pmid:29456894"),
        )

        for query, expected_query, expected_path in inputs:
            with self.subTest(query=query):
                mock_get.reset_mock()
                result = self.tool.execute(query=query, mode="WORK", max_results=20)
                self.assertEqual(result["mode"], "work")
                self.assertEqual(result["query"], expected_query)
                self.assertEqual(result["max_results"], 1)
                self.assertEqual(result["total_results"], 1)
                self.assertEqual(
                    mock_get.call_args.args[0],
                    f"https://api.openalex.org/works/{expected_path}",
                )

    def test_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query=" ")
        with self.assertRaisesRegex(ValueError, "3000 UTF-8 bytes"):
            self.tool.execute(query="x" * 3001)
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="agents", mode="paper")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="agents", max_results=0)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="agents", max_results=True)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="agents", page=0)
        with self.assertRaisesRegex(ValueError, "first 10,000"):
            self.tool.execute(query="agents", max_results=20, page=501)
        with self.assertRaisesRegex(ValueError, "page must be 1"):
            self.tool.execute(query="agents", page=2, cursor="*")
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            self.tool.execute(query="agents", cursor=" ")
        with self.assertRaisesRegex(ValueError, "4096 UTF-8 bytes"):
            self.tool.execute(query="agents", cursor="x" * 4097)
        with self.assertRaisesRegex(ValueError, "sort must be one of"):
            self.tool.execute(query="agents", sort="newest")
        with self.assertRaisesRegex(ValueError, "order must be one of"):
            self.tool.execute(query="agents", order="newest")
        with self.assertRaisesRegex(ValueError, "YYYY"):
            self.tool.execute(query="agents", from_publication_date="01-01-2024")
        with self.assertRaisesRegex(ValueError, "valid date"):
            self.tool.execute(query="agents", to_publication_date="2025-02-30")
        with self.assertRaisesRegex(ValueError, "must not be later"):
            self.tool.execute(
                query="agents",
                from_publication_date="2025",
                to_publication_date="2024",
            )
        with self.assertRaisesRegex(ValueError, "work_type"):
            self.tool.execute(query="agents", work_type="Journal Article")
        with self.assertRaisesRegex(ValueError, "must be a boolean"):
            self.tool.execute(query="agents", open_access_only="true")
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            self.tool.execute(query="agents", min_citation_count=-1)
        with self.assertRaisesRegex(ValueError, "OpenAlex work ID"):
            self.tool.execute(query="not-an-id", mode="work")

    def test_missing_metadata_returns_empty_values(self) -> None:
        work = OpenAlexTool._parse_work({"id": "https://openalex.org/W1"})

        self.assertEqual(work["openalex_id"], "W1")
        self.assertEqual(work["doi"], "")
        self.assertEqual(work["title"], "")
        self.assertEqual(work["abstract"], "")
        self.assertFalse(work["abstract_truncated"])
        self.assertEqual(work["publication_year"], 0)
        self.assertEqual(work["authors"], [])
        self.assertEqual(work["author_count"], 0)
        self.assertFalse(work["authors_truncated"])
        self.assertEqual(work["venue"]["name"], "")
        self.assertFalse(work["open_access"]["is_open_access"])
        self.assertEqual(work["topics"], [])
        self.assertEqual(work["keywords"], [])

    def test_abstract_reconstruction_uses_positions(self) -> None:
        abstract = OpenAlexTool._reconstruct_abstract({"world": [1], "Hello": [0], "ignored": ["bad"], "again": [2]})
        self.assertEqual(abstract, "Hello world again")

    def test_abstract_output_is_bounded_and_reports_truncation(self) -> None:
        parsed = OpenAlexTool._parse_work({"abstract_inverted_index": {"word": list(range(1000))}})

        self.assertEqual(len(parsed["abstract"]), 4000)
        self.assertTrue(parsed["abstract_truncated"])

    def test_author_output_is_bounded_and_reports_truncation(self) -> None:
        work = {"authorships": [{"author": {"display_name": str(index)}} for index in range(30)]}

        parsed = OpenAlexTool._parse_work(work)

        self.assertEqual(parsed["author_count"], 30)
        self.assertEqual(len(parsed["authors"]), 25)
        self.assertTrue(parsed["authors_truncated"])

    def test_nested_collections_are_bounded(self) -> None:
        work = copy.deepcopy(SAMPLE_WORK)
        work["authorships"][0]["institutions"] = [{"display_name": f"Institution {index}"} for index in range(7)]
        work["topics"] = [{"display_name": f"Topic {index}"} for index in range(12)]
        work["keywords"] = [{"display_name": f"Keyword {index}"} for index in range(12)]

        parsed = OpenAlexTool._parse_work(work)

        self.assertEqual(len(parsed["authors"][0]["institutions"]), 5)
        self.assertEqual(len(parsed["topics"]), 10)
        self.assertEqual(len(parsed["keywords"]), 10)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_timeout_returns_structured_error_with_context(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(
            query="agents",
            page=2,
            sort="publication_date",
            from_publication_date="2024",
        )

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["sort"], "publication_date")
        self.assertEqual(result["from_publication_date"], "2024-01-01")
        self.assertEqual(result["works"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_http_and_connection_errors_are_structured(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(response=response)
        http_result = self.tool.execute(query="agents")
        self.assertEqual(http_result["error"]["type"], "http_error")
        self.assertIn("429", http_result["error"]["message"])

        mock_get.side_effect = requests.ConnectionError(
            "connection failed for https://api.openalex.org/works?api_key=test-api-key"
        )
        connection_result = self.tool.execute(query="agents")
        self.assertEqual(connection_result["error"]["type"], "request_error")
        self.assertEqual(connection_result["error"]["message"], "OpenAlex request failed.")
        self.assertNotIn("test-api-key", str(connection_result))

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_api_error_and_invalid_json_are_structured(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"error": "Invalid query", "message": "Unsupported filter"})
        api_result = self.tool.execute(query="agents")
        self.assertEqual(api_result["error"]["type"], "api_error")
        self.assertIn("Unsupported filter", api_result["error"]["message"])

        mock_get.return_value = response_mock(json_data={"error": "x" * 1000})
        bounded_error_result = self.tool.execute(query="agents")
        self.assertLessEqual(len(bounded_error_result["error"]["message"]), 521)

        invalid_json = response_mock()
        invalid_json.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = invalid_json
        json_result = self.tool.execute(query="agents")
        self.assertEqual(json_result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex JSON response", json_result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_search_shape_is_structured(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"meta": {}, "results": "not-a-list"})

        result = self.tool.execute(query="agents")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex search response", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_work_shape_is_structured(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 1},
                "results": ["not-an-object"],
            }
        )

        result = self.tool.execute(query="agents")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("work must be an object", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_response_cursor_is_structured(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 0, "next_cursor": {"unexpected": "object"}},
                "results": [],
            }
        )

        result = self.tool.execute(query="agents")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("next_cursor must be a string or null", result["error"]["message"])

    def test_shipped_config_documents_contract(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "openalex_tool.yaml"
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
            "from_publication_date",
            "to_publication_date",
            "work_type",
            "open_access_only",
            "min_citation_count",
        ):
            self.assertIn(parameter, description)
        for metadata_field in (
            "OpenAlex ID",
            "DOI",
            "title",
            "abstract",
            "authors",
            "venue",
            "open-access status",
            "citation",
            "topics",
            "keywords",
            "PDF URL",
        ):
            self.assertIn(metadata_field, description)
        self.assertIn("next_cursor", description)
        self.assertIn("OPENALEX_API_KEY", description)
        self.assertIn("abstract_truncated", description)
        self.assertIn("authors_truncated", description)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_shipped_config_initializes_tool(self, mock_get: Mock) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "openalex_tool.yaml"
        )
        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = OpenAlexTool(api_key=None, email=None).initialize_by_component_configer(tool_configer)
        mock_get.return_value = response_mock(json_data={"meta": {"count": 0}, "results": []})

        result = tool.execute(query="configuration pipeline")

        self.assertEqual(tool.name, "openalex_tool")
        self.assertEqual(tool.input_keys, ["query"])
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "configuration pipeline")
        self.assertEqual(result["works"], [])


if __name__ == "__main__":
    unittest.main()
