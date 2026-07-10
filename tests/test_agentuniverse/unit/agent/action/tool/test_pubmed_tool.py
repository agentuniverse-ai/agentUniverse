#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from xml.etree import ElementTree

import requests
import yaml

from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool


SAMPLE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <ArticleTitle>Effect of <i>AI</i> in medicine</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">First section.</AbstractText>
          <AbstractText Label="METHODS">Second section.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><LastName>Smith</LastName><ForeName>Alice</ForeName></Author>
          <Author><CollectiveName>Example Research Group</CollectiveName></Author>
        </AuthorList>
        <Journal>
          <ISSN>1234-5678</ISSN>
          <Title>Example Journal</Title>
          <JournalIssue><PubDate><Year>2026</Year><Month>May</Month><Day>12</Day></PubDate></JournalIssue>
        </Journal>
        <Language>eng</Language>
        <PublicationTypeList>
          <PublicationType>Journal Article</PublicationType>
          <PublicationType>Review</PublicationType>
        </PublicationTypeList>
      </Article>
      <MeshHeadingList>
        <MeshHeading>
          <DescriptorName UI="D000001" MajorTopicYN="Y">Artificial Intelligence</DescriptorName>
          <QualifierName UI="Q000001" MajorTopicYN="N">methods</QualifierName>
        </MeshHeading>
        <MeshHeading>
          <DescriptorName UI="D000002" MajorTopicYN="N">Medicine</DescriptorName>
        </MeshHeading>
      </MeshHeadingList>
      <KeywordList>
        <Keyword>large language models</Keyword>
        <Keyword>medical education</Keyword>
      </KeywordList>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList><ArticleId IdType="doi">10.1000/example</ArticleId></ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>
"""


def response_mock(*, json_data=None, content=b""):
    response = Mock()
    response.json.return_value = json_data
    response.content = content
    response.raise_for_status.return_value = None
    return response


class PubMedToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = PubMedTool()

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_returns_structured_metadata(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            response_mock(json_data={"esearchresult": {"count": "42", "idlist": ["12345678"]}}),
            response_mock(content=SAMPLE_XML),
        ]

        result = self.tool.execute(query="AI medicine")

        self.assertEqual(result["total_results"], 42)
        self.assertEqual(result["returned_results"], 1)
        paper = result["papers"][0]
        self.assertEqual(paper["pmid"], "12345678")
        self.assertEqual(paper["title"], "Effect of AI in medicine")
        self.assertEqual(paper["authors"], ["Alice Smith", "Example Research Group"])
        self.assertEqual(paper["abstract"], "BACKGROUND: First section.\nMETHODS: Second section.")
        self.assertEqual(paper["published"], "2026-May-12")
        self.assertEqual(paper["doi"], "10.1000/example")
        self.assertEqual(paper["entry_url"], "https://pubmed.ncbi.nlm.nih.gov/12345678/")
        self.assertEqual(paper["journal_issn"], "1234-5678")
        self.assertEqual(paper["publication_types"], ["Journal Article", "Review"])
        self.assertEqual(paper["keywords"], ["large language models", "medical education"])
        self.assertEqual(paper["languages"], ["eng"])
        self.assertEqual(
            paper["mesh_terms"],
            [
                {
                    "descriptor": "Artificial Intelligence",
                    "descriptor_ui": "D000001",
                    "major_topic": True,
                    "qualifiers": [
                        {
                            "name": "methods",
                            "ui": "Q000001",
                            "major_topic": False,
                        }
                    ],
                },
                {
                    "descriptor": "Medicine",
                    "descriptor_ui": "D000002",
                    "major_topic": False,
                    "qualifiers": [],
                },
            ],
        )

        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call.kwargs["params"]["retmax"], 5)
        self.assertEqual(search_call.kwargs["params"]["retstart"], 0)
        self.assertEqual(search_call.kwargs["params"]["sort"], "relevance")
        self.assertEqual(search_call.kwargs["params"]["tool"], "agentuniverse_pubmed_tool")

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_supports_paging_and_sorting(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            response_mock(json_data={"esearchresult": {"count": "42", "idlist": ["12345678"]}}),
            response_mock(content=SAMPLE_XML),
        ]

        result = self.tool.execute(
            query="AI medicine",
            max_results=10,
            page=3,
            sort="pub_date",
        )

        self.assertEqual(result["max_results"], 10)
        self.assertEqual(result["page"], 3)
        self.assertEqual(result["retstart"], 20)
        self.assertEqual(result["sort"], "pub_date")

        search_call = mock_get.call_args_list[0]
        self.assertEqual(search_call.kwargs["params"]["retmax"], 10)
        self.assertEqual(search_call.kwargs["params"]["retstart"], 20)
        self.assertEqual(search_call.kwargs["params"]["sort"], "pub_date")

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_normalizes_sort_aliases(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "0", "idlist": []}}
        )

        result = self.tool.execute(query="AI medicine", sort="publication date")

        self.assertEqual(result["sort"], "pub_date")
        self.assertEqual(mock_get.call_args.kwargs["params"]["sort"], "pub_date")

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_keeps_canonical_sort_values_in_result(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "0", "idlist": []}}
        )

        for sort, api_value in (("author", "Author"), ("journal", "JournalName")):
            with self.subTest(sort=sort):
                result = self.tool.execute(query="AI medicine", sort=sort)

                self.assertEqual(result["sort"], sort)
                self.assertEqual(mock_get.call_args.kwargs["params"]["sort"], api_value)

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_supports_date_range_filters(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "0", "idlist": []}}
        )

        result = self.tool.execute(
            query="AI medicine",
            mindate="2024-01-01",
            maxdate="2024-12-31",
            datetype="publication date",
        )

        self.assertEqual(result["mindate"], "2024/01/01")
        self.assertEqual(result["maxdate"], "2024/12/31")
        self.assertEqual(result["datetype"], "pdat")

        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["mindate"], "2024/01/01")
        self.assertEqual(params["maxdate"], "2024/12/31")
        self.assertEqual(params["datetype"], "pdat")

    def test_search_rejects_incomplete_date_range(self) -> None:
        for date_filter in ({"mindate": "2024"}, {"maxdate": "2024"}):
            with self.subTest(date_filter=date_filter):
                with self.assertRaisesRegex(ValueError, "must be provided together"):
                    self.tool.execute(query="AI medicine", **date_filter)

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_enforces_pubmed_paging_limit(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "100000", "idlist": []}}
        )

        result = self.tool.execute(query="AI medicine", max_results=1, page=9999)

        self.assertEqual(result["retstart"], 9998)
        self.assertEqual(mock_get.call_args.kwargs["params"]["retstart"], 9998)
        with self.assertRaisesRegex(ValueError, "first 9,999 results"):
            self.tool.execute(query="AI medicine", max_results=1, page=10000)
        mock_get.assert_called_once()

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_empty_search_does_not_fetch_articles(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "0", "idlist": []}}
        )

        result = self.tool.execute(query="no matching paper", max_results=3)

        self.assertEqual(result["papers"], [])
        self.assertEqual(result["returned_results"], 0)
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.kwargs["params"]["retmax"], 3)

    def test_invalid_input(self) -> None:
        with self.assertRaisesRegex(ValueError, "query must not be empty"):
            self.tool.execute(query="  ")
        with self.assertRaisesRegex(ValueError, "between 1 and 20"):
            self.tool.execute(query="cancer", max_results=0)
        with self.assertRaisesRegex(ValueError, "integer"):
            self.tool.execute(query="cancer", max_results=True)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="cancer", page=0)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            self.tool.execute(query="cancer", page=True)
        with self.assertRaisesRegex(ValueError, "sort must be one of"):
            self.tool.execute(query="cancer", sort="newest")
        with self.assertRaisesRegex(ValueError, "YYYY, YYYY-MM, or YYYY-MM-DD"):
            self.tool.execute(query="cancer", mindate="01-01-2024")
        with self.assertRaisesRegex(ValueError, "valid date"):
            self.tool.execute(query="cancer", maxdate="2024-02-31")
        with self.assertRaisesRegex(ValueError, "greater than or equal"):
            self.tool.execute(query="cancer", mindate="2025", maxdate="2024")
        with self.assertRaisesRegex(ValueError, "datetype must be one of"):
            self.tool.execute(query="cancer", mindate="2024", datetype="published")

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_error_result_preserves_date_filters(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="cancer", mindate="2024-01", maxdate="2024-12")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["mindate"], "2024/01")
        self.assertEqual(result["maxdate"], "2024/12")
        self.assertEqual(result["datetype"], "pdat")

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_timeout_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.Timeout("timed out")

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "request_timeout")
        self.assertEqual(result["papers"], [])

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_http_error_returns_structured_error(self, mock_get: Mock) -> None:
        response = Mock(status_code=429)
        mock_get.side_effect = requests.HTTPError(response=response)

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "http_error")
        self.assertIn("429", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_connection_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.ConnectionError("connection failed")

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "request_error")
        self.assertIn("connection failed", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_esearch_api_errors_return_structured_error(self, mock_get: Mock) -> None:
        responses = (
            ({"error": "API rate limit exceeded", "count": "11"}, "API rate limit exceeded"),
            ({"esearchresult": {"ERROR": "Search backend failed"}}, "Search backend failed"),
        )

        for response_data, expected_message in responses:
            with self.subTest(response_data=response_data):
                mock_get.reset_mock()
                mock_get.return_value = response_mock(json_data=response_data)

                result = self.tool.execute(query="cancer")

                self.assertEqual(result["error"]["type"], "api_error")
                self.assertIn(expected_message, result["error"]["message"])
                mock_get.assert_called_once()

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_efetch_api_error_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            response_mock(json_data={"esearchresult": {"count": "1", "idlist": ["1"]}}),
            response_mock(content=b"<eFetchResult><ERROR>Unable to obtain query</ERROR></eFetchResult>"),
        ]

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "api_error")
        self.assertIn("Unable to obtain query", result["error"]["message"])

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_invalid_esearch_json_returns_structured_error(self, mock_get: Mock) -> None:
        response = response_mock()
        response.json.side_effect = requests.JSONDecodeError("invalid JSON", "", 0)
        mock_get.return_value = response

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("invalid ESearch JSON response", result["error"]["message"])

    def test_missing_extended_metadata_returns_empty_values(self) -> None:
        article = ElementTree.fromstring(
            b"""<PubmedArticle>
              <MedlineCitation>
                <PMID>1</PMID>
                <Article><ArticleTitle>Minimal article</ArticleTitle></Article>
              </MedlineCitation>
            </PubmedArticle>"""
        )

        paper = PubMedTool._parse_article(article)

        self.assertEqual(paper["journal_issn"], "")
        self.assertEqual(paper["publication_types"], [])
        self.assertEqual(paper["keywords"], [])
        self.assertEqual(paper["mesh_terms"], [])
        self.assertEqual(paper["languages"], [])

    def test_shipped_config_exposes_supported_parameters_and_metadata(self) -> None:
        config_path = (
            Path(__file__).resolve().parents[6]
            / "examples"
            / "sample_standard_app"
            / "intelligence"
            / "agentic"
            / "tool"
            / "buildin"
            / "pubmed_tool.yaml"
        )
        with config_path.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)

        self.assertEqual(config["input_keys"], ["query"])
        description = config["description"]
        for parameter in (
            "max_results",
            "page",
            "sort",
            "mindate",
            "maxdate",
            "datetype",
        ):
            self.assertIn(parameter, description)
        for sort_option in ("relevance", "pub_date", "author", "journal"):
            self.assertIn(sort_option, description)
        for date_type in ("pdat", "edat", "mdat", "crdt"):
            self.assertIn(date_type, description)
        for metadata_field in (
            "journal ISSN",
            "publication types",
            "keywords",
            "MeSH terms",
            "languages",
        ):
            self.assertIn(metadata_field, description)
        for example_entry in (
            '"page": 2',
            '"sort": "pub_date"',
            '"mindate": "2024-01-01"',
            '"maxdate": "2024-12-31"',
            '"datetype": "pdat"',
        ):
            self.assertIn(example_entry, description)
        for boundary_contract in (
            "first 9,999 results",
            "Must be provided together with maxdate",
            "Must be provided together with mindate",
            "api_error",
        ):
            self.assertIn(boundary_contract, description)

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_invalid_xml_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            response_mock(json_data={"esearchresult": {"count": "1", "idlist": ["1"]}}),
            response_mock(content=b"<not-valid"),
        ]

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "invalid_response")


if __name__ == "__main__":
    unittest.main()
