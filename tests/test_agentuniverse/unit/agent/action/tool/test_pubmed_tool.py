#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import unittest
from unittest.mock import Mock, patch

import requests

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
          <Title>Example Journal</Title>
          <JournalIssue><PubDate><Year>2026</Year><Month>May</Month><Day>12</Day></PubDate></JournalIssue>
        </Journal>
      </Article>
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

    @patch("agentuniverse.agent.action.tool.common_tool.pubmed_tool.requests.get")
    def test_search_supports_single_date_bound(self, mock_get: Mock) -> None:
        mock_get.return_value = response_mock(
            json_data={"esearchresult": {"count": "0", "idlist": []}}
        )

        result = self.tool.execute(query="AI medicine", mindate="2024", datetype="entrez date")

        self.assertEqual(result["mindate"], "2024")
        self.assertEqual(result["maxdate"], "")
        self.assertEqual(result["datetype"], "edat")

        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["mindate"], "2024")
        self.assertNotIn("maxdate", params)
        self.assertEqual(params["datetype"], "edat")

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
    def test_invalid_xml_returns_structured_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = [
            response_mock(json_data={"esearchresult": {"count": "1", "idlist": ["1"]}}),
            response_mock(content=b"<not-valid"),
        ]

        result = self.tool.execute(query="cancer")

        self.assertEqual(result["error"]["type"], "invalid_response")


if __name__ == "__main__":
    unittest.main()
