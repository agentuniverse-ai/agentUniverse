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
        self.assertEqual(search_call.kwargs["params"]["tool"], "agentuniverse_pubmed_tool")

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
