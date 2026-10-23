#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.openalex_tool import OpenAlexTool

SAMPLE_WORK = {
    "id": "https://openalex.org/W2741809807",
    "doi": "https://doi.org/10.1000/example",
    "title": "  Example   scholarly work ",
    "display_name": "Example scholarly work",
    "publication_year": 2025,
    "publication_date": "2025-08-13",
    "type": "article",
    "authorships": [
        {
            "author_position": "first",
            "author": {
                "id": "https://openalex.org/A5023888391",
                "display_name": "Alice Smith",
                "orcid": "https://orcid.org/0000-0002-1825-0097",
            },
            "institutions": [
                {
                    "id": "https://openalex.org/I123",
                    "display_name": "Example University",
                    "ror": "https://ror.org/02mhbdp94",
                    "country_code": "US",
                    "type": "education",
                }
            ],
            "countries": ["US", "US"],
            "is_corresponding": True,
            "raw_author_name": "Alice Smith",
        },
        {
            "author_position": "last",
            "author": {
                "id": "https://openalex.org/A987",
                "display_name": "Bob Jones",
                "orcid": None,
            },
            "institutions": [
                {
                    "id": "https://openalex.org/I456",
                    "display_name": "Second Institute",
                    "ror": None,
                    "country_code": "GB",
                    "type": "company",
                }
            ],
            "countries": ["GB"],
            "is_corresponding": False,
            "raw_author_name": "Bob Jones",
        },
    ],
    "primary_location": {
        "is_oa": True,
        "landing_page_url": "https://example.org/article",
        "pdf_url": "https://example.org/article.pdf",
        "license": "cc-by",
        "source": {
            "id": "https://openalex.org/S123",
            "display_name": "Example Journal",
            "issn_l": "1234-5678",
            "issn": ["1234-5678", "8765-4321", "1234-5678"],
            "type": "journal",
            "is_oa": True,
        },
    },
    "open_access": {
        "is_oa": True,
        "oa_status": "gold",
        "oa_url": "https://example.org/article.pdf",
    },
    "cited_by_count": 25,
    "referenced_works_count": 40,
    "topics": [
        {
            "id": "https://openalex.org/T123",
            "display_name": "Machine Learning",
            "score": 0.99,
            "subfield": {
                "id": "https://openalex.org/subfields/1702",
                "display_name": "Artificial Intelligence",
            },
            "field": {
                "id": "https://openalex.org/fields/17",
                "display_name": "Computer Science",
            },
            "domain": {
                "id": "https://openalex.org/domains/4",
                "display_name": "Physical Sciences",
            },
        }
    ],
    "keywords": [
        {
            "id": "https://openalex.org/K123",
            "display_name": "Large Language Model",
            "score": 0.88,
        }
    ],
    "abstract_inverted_index": {
        "Large": [0],
        "language": [1],
        "models": [2],
        "improve": [3],
        "medicine": [4],
    },
}


EXPECTED_WORK = {
    "id": "W2741809807",
    "doi": "10.1000/example",
    "title": "Example scholarly work",
    "abstract": "Large language models improve medicine",
    "publication_year": 2025,
    "publication_date": "2025-08-13",
    "type": "article",
    "authorships": [
        {
            "author_id": "A5023888391",
            "author_name": "Alice Smith",
            "orcid": "0000-0002-1825-0097",
            "author_position": "first",
            "is_corresponding": True,
            "raw_author_name": "Alice Smith",
            "institutions": [
                {
                    "id": "I123",
                    "name": "Example University",
                    "ror": "02mhbdp94",
                    "country_code": "US",
                    "type": "education",
                }
            ],
            "countries": ["US"],
        },
        {
            "author_id": "A987",
            "author_name": "Bob Jones",
            "orcid": "",
            "author_position": "last",
            "is_corresponding": False,
            "raw_author_name": "Bob Jones",
            "institutions": [
                {
                    "id": "I456",
                    "name": "Second Institute",
                    "ror": "",
                    "country_code": "GB",
                    "type": "company",
                }
            ],
            "countries": ["GB"],
        },
    ],
    "primary_location": {
        "is_oa": True,
        "landing_page_url": "https://example.org/article",
        "pdf_url": "https://example.org/article.pdf",
        "license": "cc-by",
        "source": {
            "id": "S123",
            "name": "Example Journal",
            "issn_l": "1234-5678",
            "issn": ["1234-5678", "8765-4321"],
            "type": "journal",
            "is_oa": True,
        },
    },
    "open_access": {
        "is_oa": True,
        "oa_status": "gold",
        "oa_url": "https://example.org/article.pdf",
    },
    "cited_by_count": 25,
    "referenced_works_count": 40,
    "topics": [
        {
            "id": "T123",
            "name": "Machine Learning",
            "score": 0.99,
            "subfield": {"id": "1702", "name": "Artificial Intelligence"},
            "field": {"id": "17", "name": "Computer Science"},
            "domain": {"id": "4", "name": "Physical Sciences"},
        }
    ],
    "keywords": [{"id": "K123", "name": "Large Language Model", "score": 0.88}],
}


def response_mock(*, json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class OpenAlexToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = OpenAlexTool(email="developer@example.com")

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_search_returns_structured_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 42, "page": 1, "per_page": 3, "next_cursor": "ignored"},
                "results": [SAMPLE_WORK],
            }
        )

        result = self.tool.execute(
            query="AI medicine",
            max_results=3,
            from_publication_date="2024-01-01",
            to_publication_date="2025-12-31",
            publication_year=2025,
            work_type="journal article",
            open_access_only=True,
            min_cited_by_count=10,
        )

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "AI medicine")
        self.assertEqual(result["max_results"], 3)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["cursor"], "")
        self.assertEqual(result["sort"], "relevance_score")
        self.assertEqual(result["from_publication_date"], "2024-01-01")
        self.assertEqual(result["to_publication_date"], "2025-12-31")
        self.assertEqual(result["publication_year"], 2025)
        self.assertEqual(result["work_type"], "article")
        self.assertTrue(result["open_access_only"])
        self.assertEqual(result["min_cited_by_count"], 10)
        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["next_cursor"], "")
        self.assertEqual(result["works"][0], EXPECTED_WORK)

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.openalex.org/works")
        params = request.kwargs["params"]
        self.assertEqual(params["search"], "AI medicine")
        self.assertEqual(params["per-page"], 3)
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["sort"], "relevance_score:desc")
        self.assertEqual(
            params["filter"],
            "from_publication_date:2024-01-01,to_publication_date:2025-12-31,"
            "publication_year:2025,type:article,is_oa:true,cited_by_count:>10",
        )
        self.assertEqual(params["mailto"], "developer@example.com")
        self.assertIn("mailto:developer@example.com", request.kwargs["headers"]["User-Agent"])
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_search_maps_paging_and_sort_aliases(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 100, "page": 3, "per_page": 4, "next_cursor": "token"},
                "results": [],
            }
        )

        result = self.tool.execute(query="AI medicine", max_results=4, page=3, sort="citation_count")

        self.assertEqual(result["page"], 3)
        self.assertEqual(result["sort"], "cited_by_count")
        self.assertEqual(result["returned_results"], 0)
        self.assertEqual(result["next_cursor"], "")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["page"], 3)
        self.assertEqual(params["per-page"], 4)
        self.assertEqual(params["sort"], "cited_by_count:desc")
        self.assertNotIn("filter", params)
        self.assertNotIn("cursor", params)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_cursor_search_returns_next_cursor(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "meta": {"count": 100000, "per_page": 10, "next_cursor": "next-cursor-token"},
                "results": [],
            }
        )

        result = self.tool.execute(query="AI medicine", max_results=10, cursor="*")

        self.assertEqual(result["cursor"], "*")
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["next_cursor"], "next-cursor-token")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["cursor"], "*")
        self.assertNotIn("page", params)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_doi_lookup_normalizes_url_and_returns_one_work(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_WORK)

        result = self.tool.execute(
            query="https://doi.org/10.1000/example",
            mode="WORK",
            max_results=20,
            page=2,
        )

        self.assertEqual(result["mode"], "work")
        self.assertEqual(result["query"], "doi:10.1000/example")
        self.assertEqual(result["max_results"], 1)
        self.assertEqual(result["page"], 1)
        self.assertEqual(result["sort"], "")
        self.assertEqual(result["from_publication_date"], "")
        self.assertIsNone(result["publication_year"])
        self.assertEqual(result["work_type"], "")
        self.assertFalse(result["open_access_only"])
        self.assertIsNone(result["min_cited_by_count"])
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["works"][0], EXPECTED_WORK)

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.openalex.org/works/doi:10.1000/example")
        self.assertEqual(request.kwargs["params"], {"mailto": "developer@example.com"})

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_work_id_lookup_accepts_bare_url_and_api_urls(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_WORK)

        for identifier in (
            "W2741809807",
            "https://openalex.org/W2741809807",
            "https://api.openalex.org/works/W2741809807/",
        ):
            result = self.tool.execute(query=identifier, mode="work")
            self.assertEqual(result["query"], "W2741809807")
            self.assertEqual(result["works"][0]["id"], "W2741809807")

        requested_urls = [call.args[0] for call in mock_get.call_args_list]
        self.assertEqual(
            requested_urls,
            [
                "https://api.openalex.org/works/W2741809807",
                "https://api.openalex.org/works/W2741809807",
                "https://api.openalex.org/works/W2741809807",
            ],
        )

    def test_abstract_reconstruction_handles_sparse_and_invalid_indexes(self) -> None:
        self.assertEqual(OpenAlexTool._reconstruct_abstract(None), "")
        self.assertEqual(OpenAlexTool._reconstruct_abstract("not-a-dict"), "")
        self.assertEqual(OpenAlexTool._reconstruct_abstract({}), "")
        self.assertEqual(
            OpenAlexTool._reconstruct_abstract({"b": [2], "a": [0], "c": [1]}),
            "a c b",
        )
        self.assertEqual(
            OpenAlexTool._reconstruct_abstract({"a": [0], "b": [0, 1]}),
            "a b",
        )
        self.assertEqual(
            OpenAlexTool._reconstruct_abstract({"a": [True, -1, "2"], "b": "bad", "c": [0]}),
            "c",
        )
        self.assertEqual(
            OpenAlexTool._reconstruct_abstract({"late": [10000000], "first": [0]}),
            "first late",
        )

    def test_missing_metadata_returns_empty_values(self) -> None:
        work = OpenAlexTool._parse_work({"id": "https://openalex.org/W1", "display_name": "Fallback title"})

        self.assertEqual(work["id"], "W1")
        self.assertEqual(work["doi"], "")
        self.assertEqual(work["title"], "Fallback title")
        self.assertEqual(work["abstract"], "")
        self.assertEqual(work["publication_year"], 0)
        self.assertEqual(work["publication_date"], "")
        self.assertEqual(work["type"], "")
        self.assertEqual(work["authorships"], [])
        self.assertEqual(work["cited_by_count"], 0)
        self.assertEqual(work["referenced_works_count"], 0)
        self.assertEqual(work["topics"], [])
        self.assertEqual(work["keywords"], [])
        self.assertEqual(
            work["primary_location"],
            {
                "is_oa": False,
                "landing_page_url": "",
                "pdf_url": "",
                "license": "",
                "source": {
                    "id": "",
                    "name": "",
                    "issn_l": "",
                    "issn": [],
                    "type": "",
                    "is_oa": False,
                },
            },
        )
        self.assertEqual(
            work["open_access"],
            {"is_oa": False, "oa_status": "", "oa_url": ""},
        )

    def test_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query="  ")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="AI", mode="doi")
        with self.assertRaisesRegex(ValueError, "between 1 and 200"):
            self.tool.execute(query="AI", max_results=0)
        with self.assertRaisesRegex(ValueError, "between 1 and 200"):
            self.tool.execute(query="AI", max_results=201)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="AI", max_results=True)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="AI", page=0)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="AI", page=True)
        with self.assertRaisesRegex(ValueError, "within the first 10000"):
            self.tool.execute(query="AI", max_results=200, page=51)
        with self.assertRaisesRegex(ValueError, "page must be 1"):
            self.tool.execute(query="AI", page=2, cursor="*")
        with self.assertRaisesRegex(ValueError, "non-empty string"):
            self.tool.execute(query="AI", cursor=" ")
        with self.assertRaisesRegex(ValueError, "sort must be one of"):
            self.tool.execute(query="AI", sort="title")
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            self.tool.execute(query="AI", from_publication_date="2025/01/01")
        with self.assertRaisesRegex(ValueError, "valid date"):
            self.tool.execute(query="AI", to_publication_date="2025-02-30")
        with self.assertRaisesRegex(ValueError, "must not be later"):
            self.tool.execute(query="AI", from_publication_date="2025-02-01", to_publication_date="2025-01-01")
        with self.assertRaisesRegex(ValueError, "publication_year"):
            self.tool.execute(query="AI", publication_year="2025")
        with self.assertRaisesRegex(ValueError, "publication_year"):
            self.tool.execute(query="AI", publication_year=True)
        with self.assertRaisesRegex(ValueError, "work_type"):
            self.tool.execute(query="AI", work_type="article,book")
        with self.assertRaisesRegex(ValueError, "open_access_only"):
            self.tool.execute(query="AI", open_access_only="yes")
        with self.assertRaisesRegex(ValueError, "min_cited_by_count"):
            self.tool.execute(query="AI", min_cited_by_count=-1)
        with self.assertRaisesRegex(ValueError, "min_cited_by_count"):
            self.tool.execute(query="AI", min_cited_by_count=True)
        with self.assertRaisesRegex(ValueError, "valid DOI or OpenAlex work ID"):
            self.tool.execute(query="not-an-identifier", mode="work")

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_api_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"error": "invalid_filter", "message": "The filter value is invalid."}
        )

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("The filter value is invalid.", result["error"]["message"])
        self.assertEqual(result["query"], "AI medicine")
        self.assertEqual(result["works"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_http_error_returns_structured_error(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertIn("429", result["error"]["message"])
        self.assertEqual(result["total_results"], 0)
        self.assertEqual(result["returned_results"], 0)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_connection_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("connection failed")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_error")
        self.assertIn("connection failed", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="AI medicine", page=2, max_results=5)

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["page"], 2)
        self.assertEqual(result["max_results"], 5)

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_json_returns_structured_error(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = response

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex JSON response", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_search_shape_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"meta": {"count": 1}, "results": "not-a-list"})

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex search results", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_metadata_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"results": []})

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("missing OpenAlex search metadata", result["error"]["message"])

        mock_get.return_value = response_mock(json_data={"meta": {"count": True}, "results": []})
        result = self.tool.execute(query="AI medicine")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex result count", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.openalex_tool.requests.get")
    def test_invalid_work_response_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"display_name": "Missing identifier"})

        result = self.tool.execute(query="W123", mode="work")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("missing OpenAlex work id", result["error"]["message"])

        mock_get.return_value = response_mock(json_data=[])
        result = self.tool.execute(query="W123", mode="work")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid OpenAlex response", result["error"]["message"])

    def test_shipped_config_exposes_modes_and_metadata(self) -> None:
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

        self.assertEqual(config["name"], "openalex_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(config["input_keys"], ["query"])
        self.assertEqual(config["metadata"]["type"], "TOOL")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.openalex_tool",
        )
        self.assertEqual(config["metadata"]["class"], "OpenAlexTool")

        description = config["description"]
        for parameter in (
            "query",
            "mode",
            "max_results",
            "page",
            "cursor",
            "sort",
            "from_publication_date",
            "to_publication_date",
            "publication_year",
            "work_type",
            "open_access_only",
            "min_cited_by_count",
        ):
            self.assertIn(parameter, description)
        for mode in ("search", "work"):
            self.assertIn(mode, description)
        for metadata_field in (
            "OpenAlex ID",
            "DOI",
            "title",
            "reconstructed abstract",
            "authorships",
            "ORCID",
            "institutions",
            "positions",
            "primary location",
            "open-access",
            "citation count",
            "referenced-works count",
            "topics",
            "keywords",
        ):
            self.assertIn(metadata_field, description)
        self.assertIn("first 10000 results", description)
        self.assertIn("next_cursor", description)
        self.assertIn("YYYY-MM-DD", description)
        self.assertIn("OPENALEX_EMAIL", description)
        self.assertIn("structured error field", description)
        self.assertIn("metadata only", description)


if __name__ == "__main__":
    unittest.main()
