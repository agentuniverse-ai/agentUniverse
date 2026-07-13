#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A scholarly paper search and metadata tool based on Semantic Scholar."""

import re
from typing import Any, ClassVar, Dict, List, Optional
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _SemanticScholarAPIError(Exception):
    """Raised when Semantic Scholar returns an API-level error response."""


class SemanticScholarTool(Tool):
    """Search Semantic Scholar or retrieve one paper by a supported identifier."""

    MODES: ClassVar[set[str]] = {"search", "paper"}
    PAPER_FIELDS: ClassVar[str] = ",".join(
        (
            "paperId",
            "corpusId",
            "externalIds",
            "url",
            "title",
            "abstract",
            "venue",
            "year",
            "publicationDate",
            "publicationTypes",
            "authors",
            "citationCount",
            "referenceCount",
            "isOpenAccess",
            "openAccessPdf",
            "fieldsOfStudy",
        )
    )

    base_url: str = "https://api.semanticscholar.org/graph/v1"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("S2_API_KEY"))
    user_agent: str = "agentUniverse-Semantic-Scholar-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Search papers or retrieve one paper by a supported identifier.

        Args:
            query: Search keywords in search mode, or a paper identifier in
                paper mode. DOI, PMID, PMCID, ArXiv, CorpusId, and Semantic
                Scholar paper IDs are supported.
            mode: Operation mode. Supports search and paper.
            max_results: Maximum search results to return, from 1 to 20.

        Returns:
            A dictionary containing operation context, result counts, and a
            list of normalized papers. Network and API failures are returned
            in a structured ``error`` field.

        Raises:
            ValueError: If query, mode, or max_results is invalid.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")

        if normalized_mode == "search":
            self._validate_max_results(max_results)
            effective_max_results = max_results
        else:
            normalized_query = self._normalize_paper_id(normalized_query)
            effective_max_results = 1

        try:
            if normalized_mode == "search":
                total_results, raw_papers = self._search(normalized_query, effective_max_results)
            else:
                raw_papers = [self._lookup_paper(normalized_query)]
                total_results = 1

            papers = [self._parse_paper(paper) for paper in raw_papers]
            return {
                "mode": normalized_mode,
                "query": normalized_query,
                "max_results": effective_max_results,
                "total_results": total_results,
                "returned_results": len(papers),
                "papers": papers,
            }
        except _SemanticScholarAPIError as exc:
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="api_error",
                message=str(exc),
            )
        except requests.Timeout:
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="request_timeout",
                message="Semantic Scholar request timed out.",
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = self._http_error_message(status_code)
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="http_error",
                message=message,
            )
        except requests.RequestException as exc:
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="request_error",
                message=f"Semantic Scholar request failed: {exc}",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="invalid_response",
                message=f"Unable to parse Semantic Scholar response: {exc}",
            )

    def _search(self, query: str, max_results: int) -> tuple[int, List[Dict[str, Any]]]:
        data = self._request(
            "/paper/search",
            params={"query": query, "limit": max_results, "fields": self.PAPER_FIELDS},
        )
        papers = data.get("data")
        if not isinstance(papers, list) or not all(isinstance(paper, dict) for paper in papers):
            raise ValueError("invalid search data")
        total = data.get("total", 0)
        if isinstance(total, bool) or not isinstance(total, int):
            raise ValueError("invalid total result count")
        return total, papers

    def _lookup_paper(self, paper_id: str) -> Dict[str, Any]:
        data = self._request(
            f"/paper/{quote(paper_id, safe='')}",
            params={"fields": self.PAPER_FIELDS},
        )
        if not isinstance(data.get("paperId"), str):
            raise ValueError("missing Semantic Scholar paperId")
        return data

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {"User-Agent": self.user_agent}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        response = requests.get(
            f"{self.base_url}{path}",
            params=dict(params or {}),
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid Semantic Scholar JSON response") from exc

        if not isinstance(data, dict):
            raise ValueError("invalid Semantic Scholar response")
        api_error = data.get("error")
        if api_error:
            raise _SemanticScholarAPIError(f"Semantic Scholar API error: {api_error}")
        return data

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized_mode = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized_mode not in cls.MODES:
            raise ValueError("mode must be one of: paper, search")
        return normalized_mode

    @staticmethod
    def _validate_max_results(max_results: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")

    @classmethod
    def _normalize_paper_id(cls, value: str) -> str:
        paper_id = value.strip()
        paper_id = re.sub(r"^https?://(?:www\.)?semanticscholar\.org/paper/(?:[^/]+/)?", "", paper_id, flags=re.I)
        paper_id = re.sub(r"^https?://(?:dx\.)?doi\.org/", "DOI:", paper_id, flags=re.I)
        paper_id = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "ARXIV:", paper_id, flags=re.I)
        paper_id = re.sub(r"\.pdf$", "", paper_id, flags=re.I)

        prefix_match = re.match(r"^(doi|arxiv|pmid|pmcid|corpusid)\s*:\s*(.+)$", paper_id, flags=re.I)
        if prefix_match:
            prefix = {
                "doi": "DOI",
                "arxiv": "ARXIV",
                "pmid": "PMID",
                "pmcid": "PMCID",
                "corpusid": "CorpusId",
            }[prefix_match.group(1).lower()]
            identifier = prefix_match.group(2).strip()
            if not identifier or any(character.isspace() for character in identifier):
                raise ValueError("query must contain a valid paper identifier in paper mode")
            if prefix == "DOI" and not cls._is_doi(identifier):
                raise ValueError("query must contain a valid DOI in paper mode")
            return f"{prefix}:{identifier}"

        if cls._is_doi(paper_id):
            return f"DOI:{paper_id}"
        if re.fullmatch(r"[0-9a-fA-F]{40}", paper_id):
            return paper_id.lower()
        raise ValueError(
            "query must contain a valid paper identifier in paper mode: DOI, PMID, "
            "PMCID, ArXiv ID, CorpusId, or Semantic Scholar paper ID"
        )

    @staticmethod
    def _is_doi(value: str) -> bool:
        return value.startswith("10.") and "/" in value and not any(character.isspace() for character in value)

    @classmethod
    def _parse_paper(cls, paper: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "paper_id": cls._string_value(paper.get("paperId")),
            "corpus_id": cls._integer_value(paper.get("corpusId")),
            "external_ids": cls._external_ids(paper.get("externalIds")),
            "title": cls._string_value(paper.get("title")),
            "authors": cls._authors(paper.get("authors")),
            "abstract": cls._string_value(paper.get("abstract")),
            "venue": cls._string_value(paper.get("venue")),
            "publication_date": cls._string_value(paper.get("publicationDate")),
            "year": cls._integer_value(paper.get("year")),
            "publication_types": cls._string_list(paper.get("publicationTypes")),
            "fields_of_study": cls._string_list(paper.get("fieldsOfStudy")),
            "citation_count": cls._integer_value(paper.get("citationCount")),
            "reference_count": cls._integer_value(paper.get("referenceCount")),
            "is_open_access": paper.get("isOpenAccess") is True,
            "open_access_pdf": cls._open_access_pdf(paper.get("openAccessPdf")),
            "url": cls._string_value(paper.get("url")),
        }

    @classmethod
    def _authors(cls, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return [name for author in value if isinstance(author, dict) if (name := cls._string_value(author.get("name")))]

    @classmethod
    def _external_ids(cls, value: Any) -> Dict[str, str]:
        if not isinstance(value, dict):
            return {}
        return {str(key): normalized for key, item in value.items() if (normalized := cls._scalar_string(item))}

    @classmethod
    def _open_access_pdf(cls, value: Any) -> Dict[str, str]:
        if not isinstance(value, dict):
            return {}
        return {
            field: normalized
            for field in ("url", "status", "license")
            if (normalized := cls._string_value(value.get(field)))
        }

    @classmethod
    def _string_list(cls, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        return [normalized for item in value if (normalized := cls._string_value(item))]

    @staticmethod
    def _string_value(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @staticmethod
    def _scalar_string(value: Any) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, int) and not isinstance(value, bool):
            return str(value)
        return ""

    @staticmethod
    def _integer_value(value: Any) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) else 0

    @staticmethod
    def _http_error_message(status_code: Optional[int]) -> str:
        if status_code == 429:
            return (
                "Semantic Scholar returned HTTP status 429 (rate limited). "
                "Retry later, or configure S2_API_KEY if Semantic Scholar has issued one to you."
            )
        if status_code:
            return f"Semantic Scholar returned HTTP status {status_code}."
        return "Semantic Scholar HTTP request failed."

    @staticmethod
    def _error_result(
        mode: str,
        query: str,
        max_results: int,
        error_type: str,
        message: str,
    ) -> Dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "total_results": 0,
            "returned_results": 0,
            "papers": [],
            "error": {"type": error_type, "message": message},
        }
