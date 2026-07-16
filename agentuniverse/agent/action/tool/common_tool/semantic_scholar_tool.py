#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A scholarly paper discovery tool based on the Semantic Scholar Graph API."""

import calendar
import re
from datetime import date
from typing import Any, ClassVar, Dict, List, Optional
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _SemanticScholarAPIError(Exception):
    """Raised when Semantic Scholar returns an API-level error response."""


class SemanticScholarTool(Tool):
    """Search papers, retrieve metadata, and explore citation relationships."""

    MODES: ClassVar[set[str]] = {"search", "paper", "citations", "references", "batch"}
    PUBLICATION_TYPES: ClassVar[tuple[str, ...]] = (
        "Review",
        "JournalArticle",
        "CaseReport",
        "ClinicalTrial",
        "Conference",
        "Dataset",
        "Editorial",
        "LettersAndComments",
        "MetaAnalysis",
        "News",
        "Study",
        "Book",
        "BookSection",
    )
    FIELDS_OF_STUDY: ClassVar[tuple[str, ...]] = (
        "Computer Science",
        "Medicine",
        "Chemistry",
        "Biology",
        "Materials Science",
        "Physics",
        "Geology",
        "Psychology",
        "Art",
        "History",
        "Geography",
        "Sociology",
        "Business",
        "Political Science",
        "Economics",
        "Philosophy",
        "Mathematics",
        "Engineering",
        "Environmental Science",
        "Agricultural and Food Sciences",
        "Education",
        "Law",
        "Linguistics",
    )
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
    RELATION_FIELDS: ClassVar[str] = ",".join(("contexts", "intents", "isInfluential", PAPER_FIELDS))

    base_url: str = "https://api.semanticscholar.org/graph/v1"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("S2_API_KEY"))
    user_agent: str = "agentUniverse-Semantic-Scholar-Tool/1.0"

    def execute(
        self,
        query: str | List[str],
        mode: str = "search",
        max_results: int = 5,
        page: int = 1,
        year: Optional[str] = None,
        publication_date_or_year: Optional[str] = None,
        publication_types: Optional[str | List[str]] = None,
        fields_of_study: Optional[str | List[str]] = None,
        venue: Optional[str | List[str]] = None,
        min_citation_count: Optional[int] = None,
        open_access_only: bool = False,
    ) -> Dict[str, Any]:
        """Run a Semantic Scholar paper operation.

        Args:
            query: Search text, one paper identifier, or a list of identifiers
                in batch mode. Supported identifiers include DOI, PMID, PMCID,
                ArXiv, CorpusId, and Semantic Scholar paper IDs.
            mode: One of search, paper, citations, references, or batch.
            max_results: Results per page for search, citations, and references,
                from 1 to 20. Paper and batch modes determine this value.
            page: One-based page for search, citations, and references.
            year: Search year filter such as 2024, 2020-2024, 2020-, or -2024.
            publication_date_or_year: Search date filter using YYYY, YYYY-MM,
                YYYY-MM-DD, or a colon-delimited inclusive range.
            publication_types: Search publication type or list of types.
            fields_of_study: Search field of study or list of fields.
            venue: Search venue or list of venues.
            min_citation_count: Minimum citation count for search results.
            open_access_only: Whether search results must have a public PDF.

        Returns:
            A dictionary containing operation context and normalized papers.
            Network and API failures use a structured ``error`` field.

        Raises:
            ValueError: If an operation or parameter is invalid.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = self._normalize_query(query, normalized_mode)
        self._validate_page(page)
        self._validate_mode_options(
            mode=normalized_mode,
            page=page,
            year=year,
            publication_date_or_year=publication_date_or_year,
            publication_types=publication_types,
            fields_of_study=fields_of_study,
            venue=venue,
            min_citation_count=min_citation_count,
            open_access_only=open_access_only,
        )

        if normalized_mode == "paper":
            effective_max_results = 1
            offset = 0
        elif normalized_mode == "batch":
            effective_max_results = len(normalized_query)
            offset = 0
        else:
            self._validate_max_results(max_results)
            effective_max_results = max_results
            offset = (page - 1) * max_results
            self._validate_result_window(normalized_mode, offset, max_results)

        search_filters = self._normalize_search_filters(
            year=year,
            publication_date_or_year=publication_date_or_year,
            publication_types=publication_types,
            fields_of_study=fields_of_study,
            venue=venue,
            min_citation_count=min_citation_count,
            open_access_only=open_access_only,
        )
        context = self._operation_context(
            mode=normalized_mode,
            query=normalized_query,
            max_results=effective_max_results,
            page=page,
            offset=offset,
            search_filters=search_filters,
        )

        try:
            if normalized_mode == "search":
                result = self._search(
                    query=normalized_query,
                    max_results=effective_max_results,
                    offset=offset,
                    filters=search_filters,
                )
                papers = [self._parse_paper(paper) for paper in result["papers"]]
                return {
                    **context,
                    "total_results": result["total"],
                    "returned_results": len(papers),
                    "next_offset": result["next_offset"],
                    "papers": papers,
                }

            if normalized_mode == "paper":
                paper = self._parse_paper(self._lookup_paper(normalized_query))
                return {
                    **context,
                    "total_results": 1,
                    "returned_results": 1,
                    "papers": [paper],
                }

            if normalized_mode in {"citations", "references"}:
                result = self._related_papers(
                    paper_id=normalized_query,
                    relation=normalized_mode,
                    max_results=effective_max_results,
                    offset=offset,
                    publication_date_or_year=search_filters["publication_date_or_year"],
                )
                papers = [self._parse_relation(item, normalized_mode) for item in result["relations"]]
                return {
                    **context,
                    "total_results": None,
                    "returned_results": len(papers),
                    "next_offset": result["next_offset"],
                    "papers": papers,
                }

            result = self._batch_lookup(normalized_query)
            papers = [self._parse_paper(paper) for paper in result["papers"]]
            return {
                **context,
                "requested_results": len(normalized_query),
                "total_results": len(papers),
                "returned_results": len(papers),
                "not_found_ids": result["not_found_ids"],
                "papers": papers,
            }
        except _SemanticScholarAPIError as exc:
            return self._error_result(
                context=context,
                error_type="api_error",
                message=str(exc),
            )
        except requests.Timeout:
            return self._error_result(
                context=context,
                error_type="request_timeout",
                message="Semantic Scholar request timed out.",
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            return self._error_result(
                context=context,
                error_type="http_error",
                message=self._http_error_message(status_code),
            )
        except requests.RequestException as exc:
            return self._error_result(
                context=context,
                error_type="request_error",
                message=f"Semantic Scholar request failed: {exc}",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                context=context,
                error_type="invalid_response",
                message=f"Unable to parse Semantic Scholar response: {exc}",
            )

    def _search(
        self,
        query: str,
        max_results: int,
        offset: int,
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        params = {
            "query": query,
            "limit": max_results,
            "offset": offset,
            "fields": self.PAPER_FIELDS,
            **self._search_request_filters(filters),
        }
        data = self._request("/paper/search", params=params)
        if not isinstance(data, dict):
            raise ValueError("invalid search response")
        papers = data.get("data")
        if not isinstance(papers, list) or not all(isinstance(paper, dict) for paper in papers):
            raise ValueError("invalid search data")
        total = self._required_nonnegative_integer(data.get("total"), "total result count")
        next_offset = self._optional_nonnegative_integer(data.get("next"), "next offset")
        return {"total": total, "next_offset": next_offset, "papers": papers}

    def _lookup_paper(self, paper_id: str) -> Dict[str, Any]:
        data = self._request(
            f"/paper/{quote(paper_id, safe='')}",
            params={"fields": self.PAPER_FIELDS},
        )
        if not isinstance(data, dict) or not isinstance(data.get("paperId"), str):
            raise ValueError("missing Semantic Scholar paperId")
        return data

    def _related_papers(
        self,
        paper_id: str,
        relation: str,
        max_results: int,
        offset: int,
        publication_date_or_year: str,
    ) -> Dict[str, Any]:
        params = {"offset": offset, "limit": max_results, "fields": self.RELATION_FIELDS}
        if relation == "citations" and publication_date_or_year:
            params["publicationDateOrYear"] = publication_date_or_year
        data = self._request(
            f"/paper/{quote(paper_id, safe='')}/{relation}",
            params=params,
        )
        if not isinstance(data, dict):
            raise ValueError(f"invalid {relation} response")
        relations = data.get("data")
        if not isinstance(relations, list) or not all(isinstance(item, dict) for item in relations):
            raise ValueError(f"invalid {relation} data")
        next_offset = self._optional_nonnegative_integer(data.get("next"), "next offset")
        return {"next_offset": next_offset, "relations": relations}

    def _batch_lookup(self, paper_ids: List[str]) -> Dict[str, Any]:
        data = self._request(
            "/paper/batch",
            params={"fields": self.PAPER_FIELDS},
            json_body={"ids": paper_ids},
        )
        if not isinstance(data, list) or len(data) != len(paper_ids):
            raise ValueError("invalid batch response")
        if not all(item is None or isinstance(item, dict) for item in data):
            raise ValueError("invalid batch paper data")

        papers = []
        not_found_ids = []
        for paper_id, paper in zip(paper_ids, data):
            if paper is None:
                not_found_ids.append(paper_id)
            else:
                papers.append(paper)
        return {"papers": papers, "not_found_ids": not_found_ids}

    def _request(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Any:
        headers = {"User-Agent": self.user_agent}
        if self.api_key:
            headers["x-api-key"] = self.api_key

        request_kwargs = {
            "params": dict(params or {}),
            "headers": headers,
            "timeout": self.timeout,
        }
        url = f"{self.base_url}{path}"
        if json_body is None:
            response = requests.get(url, **request_kwargs)
        else:
            response = requests.post(url, json=json_body, **request_kwargs)
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid Semantic Scholar JSON response") from exc

        if not isinstance(data, (dict, list)):
            raise ValueError("invalid Semantic Scholar response")
        if isinstance(data, dict) and data.get("error"):
            raise _SemanticScholarAPIError(f"Semantic Scholar API error: {data['error']}")
        return data

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized_mode = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized_mode not in cls.MODES:
            raise ValueError("mode must be one of: batch, citations, paper, references, search")
        return normalized_mode

    @classmethod
    def _normalize_query(cls, query: str | List[str], mode: str) -> str | List[str]:
        if mode == "batch":
            return cls._normalize_batch_ids(query)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")
        if mode in {"paper", "citations", "references"}:
            return cls._normalize_paper_id(normalized_query)
        return normalized_query

    @classmethod
    def _normalize_batch_ids(cls, value: Any) -> List[str]:
        if not isinstance(value, list):
            raise ValueError("query must be a list of paper identifiers in batch mode")
        if not 1 <= len(value) <= 500:
            raise ValueError("batch query must contain between 1 and 500 paper identifiers")
        paper_ids = [cls._normalize_paper_id(item) if isinstance(item, str) else "" for item in value]
        if any(not paper_id for paper_id in paper_ids):
            raise ValueError("batch query must contain only string paper identifiers")
        if len(set(paper_ids)) != len(paper_ids):
            raise ValueError("batch query must not contain duplicate paper identifiers")
        return paper_ids

    @staticmethod
    def _validate_max_results(max_results: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")

    @staticmethod
    def _validate_page(page: int) -> None:
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be an integer greater than or equal to 1")

    @staticmethod
    def _validate_result_window(mode: str, offset: int, max_results: int) -> None:
        if mode == "search" and offset + max_results > 1000:
            raise ValueError("search can access only the first 1,000 results")

    @staticmethod
    def _validate_mode_options(
        mode: str,
        page: int,
        year: Optional[str],
        publication_date_or_year: Optional[str],
        publication_types: Optional[str | List[str]],
        fields_of_study: Optional[str | List[str]],
        venue: Optional[str | List[str]],
        min_citation_count: Optional[int],
        open_access_only: bool,
    ) -> None:
        if not isinstance(open_access_only, bool):
            raise ValueError("open_access_only must be a boolean")
        search_only_filters = (year, publication_types, fields_of_study, venue, min_citation_count)
        if mode == "citations":
            if any(value is not None for value in search_only_filters) or open_access_only:
                raise ValueError("citations mode supports only publication_date_or_year filtering")
        elif mode != "search" and (
            any(value is not None for value in search_only_filters)
            or publication_date_or_year is not None
            or open_access_only
        ):
            raise ValueError("search filters can be used only in search mode")
        if mode in {"paper", "batch"} and page != 1:
            raise ValueError(f"page must be 1 in {mode} mode")

    @classmethod
    def _normalize_search_filters(
        cls,
        year: Optional[str],
        publication_date_or_year: Optional[str],
        publication_types: Optional[str | List[str]],
        fields_of_study: Optional[str | List[str]],
        venue: Optional[str | List[str]],
        min_citation_count: Optional[int],
        open_access_only: bool,
    ) -> Dict[str, Any]:
        normalized_year = cls._normalize_year_filter(year)
        normalized_date = cls._normalize_date_filter(publication_date_or_year)
        if normalized_year and normalized_date:
            raise ValueError("year and publication_date_or_year cannot be used together")
        if min_citation_count is not None and (
            isinstance(min_citation_count, bool) or not isinstance(min_citation_count, int) or min_citation_count < 0
        ):
            raise ValueError("min_citation_count must be a non-negative integer")

        return {
            "year": normalized_year,
            "publication_date_or_year": normalized_date,
            "publication_types": cls._normalize_values(publication_types, "publication_types", cls.PUBLICATION_TYPES),
            "fields_of_study": cls._normalize_values(fields_of_study, "fields_of_study", cls.FIELDS_OF_STUDY),
            "venue": cls._normalize_values(venue, "venue"),
            "min_citation_count": min_citation_count,
            "open_access_only": open_access_only,
        }

    @staticmethod
    def _search_request_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
        params = {}
        mappings = (
            ("year", "year"),
            ("publication_date_or_year", "publicationDateOrYear"),
            ("publication_types", "publicationTypes"),
            ("fields_of_study", "fieldsOfStudy"),
            ("venue", "venue"),
            ("min_citation_count", "minCitationCount"),
        )
        for context_name, api_name in mappings:
            value = filters[context_name]
            if isinstance(value, list):
                if value:
                    params[api_name] = ",".join(value)
            elif value is not None and value != "":
                params[api_name] = value
        if filters["open_access_only"]:
            params["openAccessPdf"] = ""
        return params

    @classmethod
    def _normalize_values(
        cls,
        value: Optional[str | List[str]],
        parameter_name: str,
        allowed: Optional[tuple[str, ...]] = None,
    ) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            items = value.split(",")
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            items = value
        else:
            raise ValueError(f"{parameter_name} must be a string or list of strings")

        normalized = []
        canonical = {item.lower(): item for item in allowed or ()}
        for item in items:
            text = item.strip()
            if not text:
                raise ValueError(f"{parameter_name} must not contain empty values")
            if allowed:
                match = canonical.get(text.lower())
                if not match:
                    raise ValueError(f"{parameter_name} contains an unsupported value: {text}")
                text = match
            if text not in normalized:
                normalized.append(text)
        return normalized

    @staticmethod
    def _normalize_year_filter(value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = value.strip() if isinstance(value, str) else ""
        match = re.fullmatch(r"(?:(\d{4})-(\d{4})|(\d{4})-|-(\d{4})|(\d{4}))", normalized)
        if not match:
            raise ValueError("year must use YYYY, YYYY-YYYY, YYYY-, or -YYYY format")
        years = [int(item) for item in match.groups() if item is not None]
        if any(year < 1 for year in years):
            raise ValueError("year values must be greater than zero")
        if match.group(1) and int(match.group(1)) > int(match.group(2)):
            raise ValueError("year range start must not be after its end")
        return normalized

    @classmethod
    def _normalize_date_filter(cls, value: Optional[str]) -> str:
        if value is None:
            return ""
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized or normalized.count(":") > 1:
            raise ValueError("publication_date_or_year must contain a valid date or range")
        if ":" not in normalized:
            cls._date_boundary(normalized, end=False)
            return normalized

        start, end = normalized.split(":", 1)
        if not start and not end:
            raise ValueError("publication_date_or_year range must include a boundary")
        start_date = cls._date_boundary(start, end=False) if start else None
        end_date = cls._date_boundary(end, end=True) if end else None
        if start_date and end_date and start_date > end_date:
            raise ValueError("publication date range start must not be after its end")
        return normalized

    @staticmethod
    def _date_boundary(value: str, end: bool) -> date:
        match = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", value)
        if not match:
            raise ValueError("publication dates must use YYYY, YYYY-MM, or YYYY-MM-DD")
        year = int(match.group(1))
        month_text = match.group(2)
        day_text = match.group(3)
        if year < 1:
            raise ValueError("publication date years must be greater than zero")
        try:
            month = int(month_text) if month_text else (12 if end else 1)
            day = int(day_text) if day_text else (calendar.monthrange(year, month)[1] if end else 1)
            return date(year, month, day)
        except ValueError as exc:
            raise ValueError(f"invalid publication date: {value}") from exc

    @classmethod
    def _normalize_paper_id(cls, value: str) -> str:
        paper_id = value.strip()
        paper_id = re.sub(
            r"^https?://(?:www\.)?semanticscholar\.org/paper/(?:[^/]+/)?",
            "",
            paper_id,
            flags=re.I,
        )
        paper_id = re.sub(r"^https?://(?:dx\.)?doi\.org/", "DOI:", paper_id, flags=re.I)
        paper_id = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "ARXIV:", paper_id, flags=re.I)
        paper_id = re.sub(r"\.pdf$", "", paper_id, flags=re.I)

        prefix_match = re.match(
            r"^(doi|arxiv|pmid|pmcid|corpusid|mag|acl|url)\s*:\s*(.+)$",
            paper_id,
            flags=re.I,
        )
        if prefix_match:
            prefix = {
                "doi": "DOI",
                "arxiv": "ARXIV",
                "pmid": "PMID",
                "pmcid": "PMCID",
                "corpusid": "CorpusId",
                "mag": "MAG",
                "acl": "ACL",
                "url": "URL",
            }[prefix_match.group(1).lower()]
            identifier = prefix_match.group(2).strip()
            if not identifier or any(character.isspace() for character in identifier):
                raise ValueError("query must contain a valid paper identifier")
            if prefix == "DOI" and not cls._is_doi(identifier):
                raise ValueError("query must contain a valid DOI")
            if prefix == "URL" and not re.match(r"^https?://", identifier, flags=re.I):
                raise ValueError("query must contain a valid URL")
            return f"{prefix}:{identifier}"

        if cls._is_doi(paper_id):
            return f"DOI:{paper_id}"
        if re.fullmatch(r"[0-9a-fA-F]{40}", paper_id):
            return paper_id.lower()
        raise ValueError(
            "query must contain a valid paper identifier: DOI, PMID, PMCID, ArXiv ID, "
            "CorpusId, MAG, ACL, URL, or Semantic Scholar paper ID"
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
    def _parse_relation(cls, item: Dict[str, Any], relation: str) -> Dict[str, Any]:
        paper_key = "citingPaper" if relation == "citations" else "citedPaper"
        raw_paper = item.get(paper_key)
        paper = cls._parse_paper(raw_paper if isinstance(raw_paper, dict) else {})
        paper.update(
            {
                "contexts": cls._string_list(item.get("contexts")),
                "intents": cls._string_list(item.get("intents")),
                "is_influential": item.get("isInfluential") is True,
            }
        )
        return paper

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
    def _required_nonnegative_integer(value: Any, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"invalid {field_name}")
        return value

    @classmethod
    def _optional_nonnegative_integer(cls, value: Any, field_name: str) -> Optional[int]:
        if value is None:
            return None
        return cls._required_nonnegative_integer(value, field_name)

    @staticmethod
    def _operation_context(
        mode: str,
        query: str | List[str],
        max_results: int,
        page: int,
        offset: int,
        search_filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        context = {
            "mode": mode,
            "query": query,
            "max_results": max_results,
        }
        if mode in {"search", "citations", "references"}:
            context.update({"page": page, "offset": offset})
        if mode == "search":
            context.update(search_filters)
        elif mode == "citations" and search_filters["publication_date_or_year"]:
            context["publication_date_or_year"] = search_filters["publication_date_or_year"]
        return context

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
        context: Dict[str, Any],
        error_type: str,
        message: str,
    ) -> Dict[str, Any]:
        result = {
            **context,
            "total_results": 0,
            "returned_results": 0,
            "papers": [],
            "error": {"type": error_type, "message": message},
        }
        if context["mode"] == "batch":
            result.update(
                {
                    "requested_results": len(context["query"]),
                    "not_found_ids": [],
                }
            )
        return result
