#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer


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
    def test_search_maps_paging_and_filters(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"total": 200, "offset": 10, "next": 12, "data": [SAMPLE_PAPER]}
        )

        result = self.tool.execute(
            query="language models",
            max_results=2,
            page=6,
            year="2020-2024",
            publication_types=["Review", "journalarticle"],
            fields_of_study="medicine,Computer Science",
            venue=["Nature", "NEJM"],
            min_citation_count=100,
            open_access_only=True,
        )

        self.assertEqual(result["page"], 6)
        self.assertEqual(result["offset"], 10)
        self.assertEqual(result["next_offset"], 12)
        self.assertEqual(result["year"], "2020-2024")
        self.assertEqual(result["publication_types"], ["Review", "JournalArticle"])
        self.assertEqual(result["fields_of_study"], ["Medicine", "Computer Science"])
        self.assertEqual(result["venue"], ["Nature", "NEJM"])
        self.assertEqual(result["min_citation_count"], 100)
        self.assertTrue(result["open_access_only"])

        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["offset"], 10)
        self.assertEqual(params["limit"], 2)
        self.assertEqual(params["year"], "2020-2024")
        self.assertEqual(params["publicationTypes"], "Review,JournalArticle")
        self.assertEqual(params["fieldsOfStudy"], "Medicine,Computer Science")
        self.assertEqual(params["venue"], "Nature,NEJM")
        self.assertEqual(params["minCitationCount"], 100)
        self.assertEqual(params["openAccessPdf"], "")

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_search_maps_publication_date_filter(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(json_data={"total": 0, "data": []})

        result = self.tool.execute(
            query="AI medicine",
            publication_date_or_year="2020-02:2024-06-30",
        )

        self.assertEqual(result["publication_date_or_year"], "2020-02:2024-06-30")
        self.assertEqual(
            mock_get.call_args.kwargs["params"]["publicationDateOrYear"],
            "2020-02:2024-06-30",
        )

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
        self.assertEqual(self.tool._normalize_paper_id("mag:112218234"), "MAG:112218234")
        self.assertEqual(self.tool._normalize_paper_id("acl:W12-3903"), "ACL:W12-3903")
        self.assertEqual(
            self.tool._normalize_paper_id("URL:https://acm.org/example"),
            "URL:https://acm.org/example",
        )
        paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
        self.assertEqual(self.tool._normalize_paper_id(paper_id.upper()), paper_id)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_citations_returns_relationship_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "offset": 2,
                "next": 4,
                "data": [
                    {
                        "contexts": ["This work extends the graph approach."],
                        "intents": ["background"],
                        "isInfluential": True,
                        "citingPaper": SAMPLE_PAPER,
                    }
                ],
            }
        )

        result = self.tool.execute(
            query="DOI:10.18653/v1/2020.acl-main.447",
            mode="citations",
            max_results=2,
            page=2,
            publication_date_or_year="2020:",
        )

        self.assertEqual(result["mode"], "citations")
        self.assertEqual(result["offset"], 2)
        self.assertIsNone(result["total_results"])
        self.assertEqual(result["next_offset"], 4)
        self.assertEqual(result["publication_date_or_year"], "2020:")
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["papers"][0]["paper_id"], SAMPLE_PAPER["paperId"])
        self.assertEqual(result["papers"][0]["contexts"], ["This work extends the graph approach."])
        self.assertEqual(result["papers"][0]["intents"], ["background"])
        self.assertTrue(result["papers"][0]["is_influential"])

        request = mock_get.call_args
        self.assertEqual(
            request.args[0],
            "https://api.semanticscholar.org/graph/v1/paper/" "DOI%3A10.18653%2Fv1%2F2020.acl-main.447/citations",
        )
        self.assertEqual(request.kwargs["params"]["offset"], 2)
        self.assertEqual(request.kwargs["params"]["limit"], 2)
        self.assertEqual(request.kwargs["params"]["publicationDateOrYear"], "2020:")
        self.assertIn("contexts", request.kwargs["params"]["fields"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_references_uses_cited_paper(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "offset": 0,
                "data": [
                    {
                        "contexts": [],
                        "intents": [],
                        "isInfluential": False,
                        "citedPaper": SAMPLE_PAPER,
                    }
                ],
            }
        )

        result = self.tool.execute(query="PMID:19872477", mode="references")

        self.assertEqual(result["mode"], "references")
        self.assertIsNone(result["next_offset"])
        self.assertEqual(result["papers"][0]["title"], SAMPLE_PAPER["title"])
        self.assertFalse(result["papers"][0]["is_influential"])
        self.assertTrue(mock_get.call_args.args[0].endswith("/PMID%3A19872477/references"))

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_relation_without_paper_keeps_relationship_metadata(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={
                "data": [
                    {
                        "contexts": ["A retained citation context."],
                        "intents": ["methodology"],
                        "isInfluential": True,
                        "citingPaper": None,
                    }
                ]
            }
        )

        result = self.tool.execute(query="PMID:19872477", mode="citations")

        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["papers"][0]["paper_id"], "")
        self.assertEqual(result["papers"][0]["contexts"], ["A retained citation context."])
        self.assertEqual(result["papers"][0]["intents"], ["methodology"])
        self.assertTrue(result["papers"][0]["is_influential"])

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.post")
    def test_batch_lookup_normalizes_ids_and_reports_missing_papers(self, mock_post: Mock) -> None:
        mock_post.return_value = response_mock(json_data=[SAMPLE_PAPER, None])

        result = self.tool.execute(
            query=["https://doi.org/10.18653/v1/2020.acl-main.447", "pmid:19872477"],
            mode="batch",
        )

        expected_ids = ["DOI:10.18653/v1/2020.acl-main.447", "PMID:19872477"]
        self.assertEqual(result["query"], expected_ids)
        self.assertEqual(result["max_results"], 2)
        self.assertEqual(result["requested_results"], 2)
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["not_found_ids"], ["PMID:19872477"])
        self.assertEqual(result["papers"][0]["paper_id"], SAMPLE_PAPER["paperId"])
        self.assertEqual(
            mock_post.call_args.args[0],
            "https://api.semanticscholar.org/graph/v1/paper/batch",
        )
        self.assertEqual(mock_post.call_args.kwargs["json"], {"ids": expected_ids})
        self.assertEqual(mock_post.call_args.kwargs["params"]["fields"], self.tool.BATCH_FIELDS)
        self.assertEqual(
            set(result["papers"][0]),
            {"paper_id", "title", "venue", "year", "citation_count", "is_open_access"},
        )

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.post")
    def test_maximum_batch_output_is_compact_and_bounded(self, mock_post: Mock) -> None:
        paper_ids = [f"CorpusId:{index}" for index in range(1, self.tool.MAX_BATCH_RESULTS + 1)]
        oversized_paper = {
            **SAMPLE_PAPER,
            "title": "T" * 10_000,
            "venue": "V" * 10_000,
            "abstract": "A" * 100_000,
            "authors": [{"name": "An Author"}] * 1_000,
        }
        mock_post.return_value = response_mock(json_data=[dict(oversized_paper) for _ in paper_ids])

        result = self.tool.execute(query=paper_ids, mode="batch")

        self.assertEqual(result["returned_results"], self.tool.MAX_BATCH_RESULTS)
        self.assertTrue(all(len(paper["title"]) <= self.tool.MAX_BATCH_TITLE_LENGTH for paper in result["papers"]))
        self.assertTrue(all(len(paper["venue"]) <= self.tool.MAX_BATCH_VENUE_LENGTH for paper in result["papers"]))
        self.assertNotIn("abstract", result["papers"][0])
        self.assertNotIn("authors", result["papers"][0])
        serialized = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertLessEqual(len(serialized), self.tool.MAX_BATCH_OUTPUT_BYTES)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.post")
    def test_oversized_utf8_batch_returns_bounded_error(self, mock_post: Mock) -> None:
        paper_ids = [f"CorpusId:{index}" for index in range(1, self.tool.MAX_BATCH_RESULTS + 1)]
        mock_post.return_value = response_mock(
            json_data=[
                {
                    **SAMPLE_PAPER,
                    "title": "\U0001f4da" * self.tool.MAX_BATCH_TITLE_LENGTH,
                    "venue": "\U0001f4da" * self.tool.MAX_BATCH_VENUE_LENGTH,
                }
                for _ in paper_ids
            ]
        )

        result = self.tool.execute(query=paper_ids, mode="batch")

        self.assertEqual(result["error"]["type"], "output_limit_exceeded")
        self.assertEqual(result["papers"], [])
        serialized = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertLessEqual(len(serialized), self.tool.MAX_BATCH_OUTPUT_BYTES)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.post")
    def test_invalid_batch_shape_returns_structured_error(self, mock_post: Mock) -> None:
        mock_post.return_value = response_mock(json_data=[SAMPLE_PAPER])

        result = self.tool.execute(
            query=["PMID:19872477", "DOI:10.18653/v1/2020.acl-main.447"],
            mode="batch",
        )

        self.assertEqual(result["requested_results"], 2)
        self.assertEqual(result["returned_results"], 0)
        self.assertEqual(result["not_found_ids"], [])
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid batch response", result["error"]["message"])

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

    def test_invalid_paging_filters_and_batch_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "page must be an integer"):
            self.tool.execute(query="AI", page=0)
        with self.assertRaisesRegex(ValueError, "page must be an integer"):
            self.tool.execute(query="PMID:19872477", mode="paper", page=True)
        with self.assertRaisesRegex(ValueError, "first 1,000"):
            self.tool.execute(query="AI", max_results=20, page=51)
        with self.assertRaisesRegex(ValueError, "only in search mode"):
            self.tool.execute(query="PMID:19872477", mode="paper", year="2024")
        with self.assertRaisesRegex(ValueError, "supports only publication_date_or_year"):
            self.tool.execute(query="PMID:19872477", mode="citations", year="2024")
        with self.assertRaisesRegex(ValueError, "cannot be used together"):
            self.tool.execute(query="AI", year="2024", publication_date_or_year="2024")
        with self.assertRaisesRegex(ValueError, "year range start"):
            self.tool.execute(query="AI", year="2025-2020")
        with self.assertRaisesRegex(ValueError, "publication date range start"):
            self.tool.execute(query="AI", publication_date_or_year="2025:2020")
        with self.assertRaisesRegex(ValueError, "invalid publication date"):
            self.tool.execute(query="AI", publication_date_or_year="2024-02-30")
        with self.assertRaisesRegex(ValueError, "unsupported value"):
            self.tool.execute(query="AI", publication_types="UnsupportedType")
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            self.tool.execute(query="AI", min_citation_count=-1)
        with self.assertRaisesRegex(ValueError, "must be a list"):
            self.tool.execute(query="PMID:19872477", mode="batch")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query=[], mode="batch")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(
                query=[f"CorpusId:{index}" for index in range(21)],
                mode="batch",
            )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.tool.execute(query=["PMID:19872477", "pmid:19872477"], mode="batch")
        with self.assertRaisesRegex(ValueError, "must not exceed 256"):
            self.tool.execute(query=[f"URL:https://example.com/{'x' * 300}"], mode="batch")

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
    def test_error_response_preserves_search_context(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(
            query="AI medicine",
            max_results=2,
            page=3,
            year="2020-",
            fields_of_study="Medicine",
            open_access_only=True,
        )

        self.assertEqual(result["page"], 3)
        self.assertEqual(result["offset"], 4)
        self.assertEqual(result["year"], "2020-")
        self.assertEqual(result["fields_of_study"], ["Medicine"])
        self.assertTrue(result["open_access_only"])
        self.assertEqual(result["error"]["type"], "request_timeout")

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
        for parameter in (
            "query",
            "mode",
            "max_results",
            "page",
            "year",
            "publication_date_or_year",
            "publication_types",
            "fields_of_study",
            "venue",
            "min_citation_count",
            "open_access_only",
        ):
            self.assertIn(parameter, description)
        for mode in ("search", "paper", "citations", "references", "batch"):
            self.assertIn(mode, description)
        for identifier in (
            "DOI",
            "PMID",
            "PMCID",
            "ArXiv",
            "CorpusId",
            "MAG",
            "ACL",
            "URL",
            "Semantic Scholar paper ID",
        ):
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
        self.assertIn("1,000", description)
        self.assertIn("1 and 20", description)
        self.assertIn("32 KiB", description)
        self.assertIn("compact", description)
        for relationship_field in ("contexts", "intents", "is_influential"):
            self.assertIn(relationship_field, description)
        for batch_field in ("requested_results", "not_found_ids"):
            self.assertIn(batch_field, description)

    @patch("agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool.requests.get")
    def test_shipped_config_initializes_tool(self, mock_get: Mock) -> None:
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
        configer = Configer(str(config_path)).load()
        tool_configer = ToolConfiger(configer).load_by_configer(configer)
        tool = SemanticScholarTool(api_key=None).initialize_by_component_configer(tool_configer)
        mock_get.return_value = response_mock(json_data={"total": 0, "data": []})

        result = tool.execute(query="configuration pipeline")

        self.assertEqual(tool.name, "semantic_scholar_tool")
        self.assertEqual(tool.input_keys, ["query"])
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "configuration pipeline")
        self.assertEqual(result["papers"], [])


if __name__ == "__main__":
    unittest.main()
