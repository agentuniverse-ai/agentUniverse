#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A lightweight PubMed search tool based on NCBI E-utilities."""

from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class PubMedTool(Tool):
    """Search PubMed and return structured article metadata."""

    base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    email: Optional[str] = Field(default_factory=lambda: get_from_env("NCBI_EMAIL"))
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("NCBI_API_KEY"))
    ncbi_tool_name: str = "agentuniverse_pubmed_tool"

    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search PubMed for articles matching a query.

        Args:
            query: PubMed search expression or keywords.
            max_results: Maximum number of articles to return, from 1 to 20.

        Returns:
            A dictionary containing the query, result counts, and article
            metadata. Network and response parsing failures are returned in
            a structured ``error`` field.

        Raises:
            ValueError: If the query is empty or max_results is invalid.
        """
        query = query.strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must not be empty")
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")

        try:
            search_data = self._search(query, max_results)
            search_result = search_data.get("esearchresult", {})
            pmids = search_result.get("idlist", [])
            total_results = int(search_result.get("count", 0))

            papers = self._fetch_articles(pmids) if pmids else []
            return {
                "query": query,
                "total_results": total_results,
                "returned_results": len(papers),
                "papers": papers,
            }
        except requests.Timeout:
            return self._error_result(query, "request_timeout", "PubMed request timed out.")
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = f"PubMed returned HTTP status {status_code}." if status_code else "PubMed HTTP request failed."
            return self._error_result(query, "http_error", message)
        except requests.RequestException as exc:
            return self._error_result(query, "request_error", f"PubMed request failed: {exc}")
        except (ElementTree.ParseError, KeyError, TypeError, ValueError) as exc:
            return self._error_result(query, "invalid_response", f"Unable to parse PubMed response: {exc}")

    def _search(self, query: str, max_results: int) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/esearch.fcgi",
            params={
                **self._common_params(),
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("esearchresult"), dict):
            raise ValueError("missing esearchresult")
        return data

    def _fetch_articles(self, pmids: List[str]) -> List[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/efetch.fcgi",
            params={
                **self._common_params(),
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        root = ElementTree.fromstring(response.content)
        return [self._parse_article(article) for article in root.findall(".//PubmedArticle")]

    def _common_params(self) -> Dict[str, str]:
        params = {"tool": self.ncbi_tool_name}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    @classmethod
    def _parse_article(cls, article: ElementTree.Element) -> Dict[str, Any]:
        pmid = cls._element_text(article.find(".//MedlineCitation/PMID"))
        title = cls._element_text(article.find(".//Article/ArticleTitle"))
        journal = cls._element_text(article.find(".//Article/Journal/Title"))

        authors = []
        for author in article.findall(".//Article/AuthorList/Author"):
            collective_name = cls._element_text(author.find("CollectiveName"))
            if collective_name:
                authors.append(collective_name)
                continue
            fore_name = cls._element_text(author.find("ForeName"))
            last_name = cls._element_text(author.find("LastName"))
            full_name = " ".join(part for part in (fore_name, last_name) if part)
            if full_name:
                authors.append(full_name)

        abstract_parts = []
        for abstract in article.findall(".//Article/Abstract/AbstractText"):
            text = cls._element_text(abstract)
            if not text:
                continue
            label = abstract.attrib.get("Label")
            abstract_parts.append(f"{label}: {text}" if label else text)

        doi = ""
        for article_id in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = cls._element_text(article_id)
                break

        return {
            "pmid": pmid,
            "title": title,
            "authors": authors,
            "abstract": "\n".join(abstract_parts),
            "journal": journal,
            "published": cls._publication_date(article),
            "doi": doi,
            "entry_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        }

    @classmethod
    def _publication_date(cls, article: ElementTree.Element) -> str:
        pub_date = article.find(".//Article/Journal/JournalIssue/PubDate")
        if pub_date is None:
            return ""
        medline_date = cls._element_text(pub_date.find("MedlineDate"))
        if medline_date:
            return medline_date
        parts = [
            cls._element_text(pub_date.find("Year")),
            cls._element_text(pub_date.find("Month")),
            cls._element_text(pub_date.find("Day")),
        ]
        return "-".join(part for part in parts if part)

    @staticmethod
    def _element_text(element: Optional[ElementTree.Element]) -> str:
        if element is None:
            return ""
        return " ".join("".join(element.itertext()).split())

    @staticmethod
    def _error_result(query: str, error_type: str, message: str) -> Dict[str, Any]:
        return {
            "query": query,
            "total_results": 0,
            "returned_results": 0,
            "papers": [],
            "error": {"type": error_type, "message": message},
        }
