#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A lightweight PubMed search tool based on NCBI E-utilities."""

from datetime import date
import re
from typing import Any, ClassVar, Dict, List, Optional
from xml.etree import ElementTree

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class PubMedTool(Tool):
    """Search PubMed and return structured article metadata."""

    SORT_OPTIONS: ClassVar[Dict[str, str]] = {
        "relevance": "relevance",
        "pub_date": "pub_date",
        "publication_date": "pub_date",
        "author": "Author",
        "journal": "JournalName",
    }
    DATE_TYPE_OPTIONS: ClassVar[Dict[str, str]] = {
        "pdat": "pdat",
        "pub_date": "pdat",
        "publication_date": "pdat",
        "edat": "edat",
        "entrez_date": "edat",
        "mdat": "mdat",
        "modification_date": "mdat",
        "crdt": "crdt",
        "create_date": "crdt",
    }

    base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    email: Optional[str] = Field(default_factory=lambda: get_from_env("NCBI_EMAIL"))
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("NCBI_API_KEY"))
    ncbi_tool_name: str = "agentuniverse_pubmed_tool"

    def execute(
        self,
        query: str,
        max_results: int = 5,
        page: int = 1,
        sort: str = "relevance",
        mindate: Optional[str] = None,
        maxdate: Optional[str] = None,
        datetype: str = "pdat",
    ) -> Dict[str, Any]:
        """Search PubMed for articles matching a query.

        Args:
            query: PubMed search expression or keywords.
            max_results: Maximum number of articles to return, from 1 to 20.
            page: One-based page number for paginated results.
            sort: Sort order. Supports relevance, pub_date, author, and journal.
            mindate: Optional lower date bound in YYYY, YYYY-MM, or YYYY-MM-DD format.
            maxdate: Optional upper date bound in YYYY, YYYY-MM, or YYYY-MM-DD format.
            datetype: Date field used by PubMed when mindate or maxdate is set.

        Returns:
            A dictionary containing the query, result counts, and article
            metadata. Network and response parsing failures are returned in
            a structured ``error`` field.

        Raises:
            ValueError: If the query, max_results, page, or sort is invalid.
        """
        query = query.strip() if isinstance(query, str) else ""
        if not query:
            raise ValueError("query must not be empty")
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")
        if isinstance(page, bool) or not isinstance(page, int):
            raise ValueError("page must be a positive integer")
        if page < 1:
            raise ValueError("page must be a positive integer")

        normalized_sort = self._normalize_sort(sort)
        normalized_datetype = self._normalize_datetype(datetype)
        normalized_mindate = self._normalize_date(mindate, "mindate")
        normalized_maxdate = self._normalize_date(maxdate, "maxdate")
        if self._date_sort_value(normalized_maxdate, upper_bound=True) < self._date_sort_value(normalized_mindate):
            raise ValueError("maxdate must be greater than or equal to mindate")
        retstart = (page - 1) * max_results

        try:
            search_data = self._search(
                query,
                max_results,
                retstart,
                normalized_sort,
                normalized_mindate,
                normalized_maxdate,
                normalized_datetype,
            )
            search_result = search_data.get("esearchresult", {})
            pmids = search_result.get("idlist", [])
            total_results = int(search_result.get("count", 0))

            papers = self._fetch_articles(pmids) if pmids else []
            return {
                "query": query,
                "max_results": max_results,
                "page": page,
                "retstart": retstart,
                "sort": normalized_sort,
                "mindate": normalized_mindate,
                "maxdate": normalized_maxdate,
                "datetype": normalized_datetype if normalized_mindate or normalized_maxdate else "",
                "total_results": total_results,
                "returned_results": len(papers),
                "papers": papers,
            }
        except requests.Timeout:
            return self._error_result(
                query,
                "request_timeout",
                "PubMed request timed out.",
                max_results,
                page,
                retstart,
                normalized_sort,
                normalized_mindate,
                normalized_maxdate,
                normalized_datetype,
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = f"PubMed returned HTTP status {status_code}." if status_code else "PubMed HTTP request failed."
            return self._error_result(
                query,
                "http_error",
                message,
                max_results,
                page,
                retstart,
                normalized_sort,
                normalized_mindate,
                normalized_maxdate,
                normalized_datetype,
            )
        except requests.RequestException as exc:
            return self._error_result(
                query,
                "request_error",
                f"PubMed request failed: {exc}",
                max_results,
                page,
                retstart,
                normalized_sort,
                normalized_mindate,
                normalized_maxdate,
                normalized_datetype,
            )
        except (ElementTree.ParseError, KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                query,
                "invalid_response",
                f"Unable to parse PubMed response: {exc}",
                max_results,
                page,
                retstart,
                normalized_sort,
                normalized_mindate,
                normalized_maxdate,
                normalized_datetype,
            )

    def _search(
        self,
        query: str,
        max_results: int,
        retstart: int,
        sort: str,
        mindate: str = "",
        maxdate: str = "",
        datetype: str = "pdat",
    ) -> Dict[str, Any]:
        params = {
            **self._common_params(),
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results,
            "retstart": retstart,
            "sort": sort,
        }
        if mindate or maxdate:
            params["datetype"] = datetype
            if mindate:
                params["mindate"] = mindate
            if maxdate:
                params["maxdate"] = maxdate

        response = requests.get(
            f"{self.base_url}/esearch.fcgi",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("esearchresult"), dict):
            raise ValueError("missing esearchresult")
        return data

    @classmethod
    def _normalize_sort(cls, sort: str) -> str:
        sort_key = sort.strip().lower().replace("-", "_").replace(" ", "_") if isinstance(sort, str) else ""
        normalized_sort = cls.SORT_OPTIONS.get(sort_key)
        if normalized_sort is None:
            valid_options = ", ".join(sorted(cls.SORT_OPTIONS))
            raise ValueError(f"sort must be one of: {valid_options}")
        return normalized_sort

    @classmethod
    def _normalize_datetype(cls, datetype: str) -> str:
        datetype_key = datetype.strip().lower().replace("-", "_").replace(" ", "_") if isinstance(datetype, str) else ""
        normalized_datetype = cls.DATE_TYPE_OPTIONS.get(datetype_key)
        if normalized_datetype is None:
            valid_options = ", ".join(sorted(cls.DATE_TYPE_OPTIONS))
            raise ValueError(f"datetype must be one of: {valid_options}")
        return normalized_datetype

    @staticmethod
    def _normalize_date(value: Optional[str], field_name: str) -> str:
        if value is None:
            return ""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a date string")

        normalized = value.strip().replace("-", "/")
        if not re.fullmatch(r"\d{4}(/\d{2}){0,2}", normalized):
            raise ValueError(f"{field_name} must use YYYY, YYYY-MM, or YYYY-MM-DD format")

        parts = [int(part) for part in normalized.split("/")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else 1
        day = parts[2] if len(parts) > 2 else 1
        try:
            date(year, month, day)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid date") from exc
        return normalized

    @staticmethod
    def _date_sort_value(value: str, upper_bound: bool = False) -> date:
        if not value:
            return date.max if upper_bound else date.min
        parts = [int(part) for part in value.split("/")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else (12 if upper_bound else 1)
        if len(parts) > 2:
            day = parts[2]
        elif upper_bound:
            next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            day = (next_month.toordinal() - date(year, month, 1).toordinal())
        else:
            day = 1
        return date(year, month, day)

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
    def _error_result(
        query: str,
        error_type: str,
        message: str,
        max_results: int = 0,
        page: int = 0,
        retstart: int = 0,
        sort: str = "",
        mindate: str = "",
        maxdate: str = "",
        datetype: str = "",
    ) -> Dict[str, Any]:
        return {
            "query": query,
            "max_results": max_results,
            "page": page,
            "retstart": retstart,
            "sort": sort,
            "mindate": mindate,
            "maxdate": maxdate,
            "datetype": datetype if mindate or maxdate else "",
            "total_results": 0,
            "returned_results": 0,
            "papers": [],
            "error": {"type": error_type, "message": message},
        }
