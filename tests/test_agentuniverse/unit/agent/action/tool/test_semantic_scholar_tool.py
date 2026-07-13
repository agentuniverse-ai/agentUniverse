#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool


SAMPLE_PAPER = {
    "paperId": "649def34f8be52c8b66281af98ae884c09aef38b",
    "corpusId": 215416146,
    "externalIds": {
        "DOI": "10.18653/v1/2020.acl-main.447",
        "ArXiv": "2004.12345",
        "CorpusId": 215416146,
    },
    "url": "https://www.semanticscholar.org/paper/649def34f8be52c8b66281af98ae884c09aef38b",
    "title": "Construction of the Literature Graph in Semantic Scholar",
    "abstract": "A useful scholarly graph abstract.",
    "venue": "ACL",
    "year": 2020,
    "publicationDate": "2020-07-01",
    "publicationTypes": ["JournalArticle", "Review"],
    "authors": [
        {"authorId": "1", "name": "Alice Smith"},
        {"authorId": "2", "name": "Bob Jones"},
    ],
    "citationCount": 299,
    "referenceCount": 27,
    "isOpenAccess": True,
    "openAccessPdf": {
        "url": "https://example.org/paper.pdf",
        "status": "GREEN",
        "license": "CCBY",
    },
    "fieldsOfStudy": ["Computer Science", "Medicine"],
}


def response_mock(*, json_data=None):
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class SemanticScholarToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = SemanticScholarTool(api_key="test-api-key")

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_search_returns_structured_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"total": 42, "offset": 0, "next": 1, "data": [SAMPLE_PAPER]})

        result = self.tool.execute(query="AI medicine", max_results=3)

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "AI medicine")
        self.assertEqual(result["max_results"], 3)
        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(
            result["papers"][0],
            {
                "paper_id": "649def34f8be52c8b66281af98ae884c09aef38b",
                "corpus_id": 215416146,
                "external_ids": {
                    "DOI": "10.18653/v1/2020.acl-main.447",
                    "ArXiv": "2004.12345",
                    "CorpusId": "215416146",
                },
                "title": "Construction of the Literature Graph in Semantic Scholar",
                "authors": ["Alice Smith", "Bob Jones"],
                "abstract": "A useful scholarly graph abstract.",
                "venue": "ACL",
                "publication_date": "2020-07-01",
                "year": 2020,
                "publication_types": ["JournalArticle", "Review"],
                "fields_of_study": ["Computer Science", "Medicine"],
                "citation_count": 299,
                "reference_count": 27,
                "is_open_access": True,
                "open_access_pdf": {
                    "url": "https://example.org/paper.pdf",
                    "status": "GREEN",
                    "license": "CCBY",
                },
                "url": "https://www.semanticscholar.org/paper/649def34f8be52c8b66281af98ae884c09aef38b",
            },
        )

        request = mock_get.call_args
        self.assertEqual(request.args[0], "https://api.semanticscholar.org/graph/v1/paper/search")
        self.assertEqual(request.kwargs["params"]["query"], "AI medicine")
        self.assertEqual(request.kwargs["params"]["limit"], 3)
        self.assertIn("citationCount", request.kwargs["params"]["fields"])
        self.assertEqual(request.kwargs["headers"]["x-api-key"], "test-api-key")
        self.assertEqual(request.kwargs["timeout"], 15.0)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_paper_lookup_normalizes_doi_url(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data=SAMPLE_PAPER)

        result = self.tool.execute(
            query="https://doi.org/10.18653/v1/2020.acl-main.447",
            mode="PAPER",
            max_results=20,
        )

        self.assertEqual(result["mode"], "paper")
        self.assertEqual(result["query"], "DOI:10.18653/v1/2020.acl-main.447")
        self.assertEqual(result["max_results"], 1)
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(
            mock_get.call_args.args[0],
            "https://api.semanticscholar.org/graph/v1/paper/DOI%3A10.18653%2Fv1%2F2020.acl-main.447",
        )

    def test_paper_identifier_normalization(self) -> None:
        self.assertEqual(
            self.tool._normalize_paper_id("https://arxiv.org/abs/2106.15928"),
            "ARXIV:2106.15928",
        )
        self.assertEqual(self.tool._normalize_paper_id("pmid:19872477"), "PMID:19872477")
        self.assertEqual(self.tool._normalize_paper_id("pmcid:2323736"), "PMCID:2323736")
        self.assertEqual(self.tool._normalize_paper_id("corpusid:215416146"), "CorpusId:215416146")
        paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
        self.assertEqual(self.tool._normalize_paper_id(paper_id.upper()), paper_id)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_request_without_api_key_omits_header(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"total": 0, "data": []})
        tool = SemanticScholarTool(api_key=None)

        tool.execute(query="no matching paper")

        self.assertNotIn("x-api-key", mock_get.call_args.kwargs["headers"])

    def test_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query="  ")
        with self.assertRaisesRegex(ValueError, "mode must be one of"):
            self.tool.execute(query="AI", mode="detail")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="AI", max_results=0)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="AI", max_results=True)
        with self.assertRaisesRegex(ValueError, "paper identifier"):
            self.tool.execute(query="not-an-identifier", mode="paper")
        with self.assertRaisesRegex(ValueError, "valid DOI"):
            self.tool.execute(query="doi:not-a-doi", mode="paper")

    def test_missing_metadata_returns_empty_values(self) -> None:
        paper = SemanticScholarTool._parse_paper({"paperId": "abc"})

        self.assertEqual(paper["paper_id"], "abc")
        self.assertEqual(paper["corpus_id"], 0)
        self.assertEqual(paper["external_ids"], {})
        self.assertEqual(paper["title"], "")
        self.assertEqual(paper["authors"], [])
        self.assertEqual(paper["abstract"], "")
        self.assertEqual(paper["publication_types"], [])
        self.assertEqual(paper["fields_of_study"], [])
        self.assertFalse(paper["is_open_access"])
        self.assertEqual(paper["open_access_pdf"], {})

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["papers"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_http_error_returns_structured_error(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertIn("429", result["error"]["message"])
        self.assertIn("S2_API_KEY", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_connection_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("connection failed")

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "request_error")
        self.assertIn("connection failed", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_api_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"error": "Unknown paper id"})

        result = self.tool.execute(query="PMID:19872477", mode="paper")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("Unknown paper id", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_invalid_json_returns_structured_error(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = response

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid Semantic Scholar JSON response", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_invalid_search_shape_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"total": 1, "data": "not-a-list"})

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid search data", result["error"]["message"])

    def test_shipped_config_exposes_modes_identifiers_and_metadata(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "semantic_scholar_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        description = config["description"]
        for parameter in ("query", "mode", "max_results"):
            self.assertIn(parameter, description)
        for mode in ("search", "paper"):
            self.assertIn(mode, description)
        for identifier in ("DOI", "PMID", "PMCID", "ArXiv", "CorpusId", "Semantic Scholar paper ID"):
            self.assertIn(identifier, description)
        for metadata_field in (
            "title",
            "authors",
            "abstract",
            "venue",
            "publication date",
            "citation count",
            "reference count",
            "open access PDF",
        ):
            self.assertIn(metadata_field, description)
        self.assertIn("S2_API_KEY", description)
        self.assertIn("rate", description.lower())


if __name__ == "__main__":
    unittest.main()
