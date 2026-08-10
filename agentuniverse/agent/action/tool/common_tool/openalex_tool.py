#!/usr/bin/env python3

"""Scholarly work discovery through the OpenAlex REST API."""

# Input validation intentionally uses ValueError to match the public contracts of
# the existing built-in scholarly tools.
# ruff: noqa: TRY003, TRY004, TRY301

import re
from calendar import monthrange
from datetime import date
from typing import Any, ClassVar
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _OpenAlexAPIError(Exception):
    """Raised when OpenAlex returns an API-level error response."""


class OpenAlexTool(Tool):
    """Search OpenAlex works or retrieve one work by identifier."""

    MODES: ClassVar[set[str]] = {"search", "work"}
    SORT_FIELDS: ClassVar[dict[str, str]] = {
        "relevance": "relevance_score",
        "relevance_score": "relevance_score",
        "citation_count": "cited_by_count",
        "cited_by_count": "cited_by_count",
        "publication_date": "publication_date",
        "publication_year": "publication_year",
        "title": "display_name",
        "display_name": "display_name",
    }
    ORDERS: ClassVar[set[str]] = {"asc", "desc"}
    SELECT_FIELDS: ClassVar[str] = ",".join(
        (
            "id",
            "doi",
            "display_name",
            "publication_year",
            "publication_date",
            "type",
            "language",
            "authorships",
            "primary_location",
            "open_access",
            "cited_by_count",
            "referenced_works_count",
            "topics",
            "keywords",
            "ids",
            "abstract_inverted_index",
        )
    )
    MAX_AUTHORS: ClassVar[int] = 25
    MAX_TOPICS: ClassVar[int] = 10
    MAX_KEYWORDS: ClassVar[int] = 10

    base_url: str = "https://api.openalex.org"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    api_key: str | None = Field(default_factory=lambda: get_from_env("OPENALEX_API_KEY"))
    email: str | None = Field(default_factory=lambda: get_from_env("OPENALEX_EMAIL"))

    def execute(  # noqa: C901
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
        page: int = 1,
        cursor: str | None = None,
        sort: str = "relevance",
        order: str = "desc",
        from_publication_date: str | None = None,
        to_publication_date: str | None = None,
        work_type: str | None = None,
        open_access_only: bool = False,
        min_citation_count: int = 0,
    ) -> dict[str, Any]:
        """Search works or retrieve one OpenAlex work.

        Args:
            query: Search text, or an OpenAlex, DOI, or PMID identifier.
            mode: Operation mode, either ``search`` or ``work``.
            max_results: Search results per page, from 1 to 20.
            page: One-based page for basic paging.
            cursor: Cursor for deep paging. Start with ``*``.
            sort: Search sort field or supported alias.
            order: Sort direction, either ``asc`` or ``desc``.
            from_publication_date: Inclusive lower publication-date bound.
            to_publication_date: Inclusive upper publication-date bound.
            work_type: Optional OpenAlex work type such as ``article``.
            open_access_only: Whether to require open-access works.
            min_citation_count: Inclusive minimum citation count.

        Returns:
            Operation context and a normalized ``works`` list. Network, API,
            and response errors are returned in a structured ``error`` field.

        Raises:
            ValueError: If an input parameter is invalid.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")
        if len(normalized_query.encode("utf-8")) > 3000:
            raise ValueError("query must be at most 3000 UTF-8 bytes")

        if normalized_mode == "search":
            self._validate_max_results(max_results)
            self._validate_page(page, max_results)
            normalized_cursor = self._normalize_cursor(cursor)
            if normalized_cursor and page != 1:
                raise ValueError("page must be 1 when cursor is provided")
            normalized_sort = self._normalize_sort(sort)
            normalized_order = self._normalize_order(order)
            normalized_from_date = self._normalize_date(
                from_publication_date, "from_publication_date", upper_bound=False
            )
            normalized_to_date = self._normalize_date(to_publication_date, "to_publication_date", upper_bound=True)
            if (
                normalized_from_date
                and normalized_to_date
                and date.fromisoformat(normalized_from_date) > date.fromisoformat(normalized_to_date)
            ):
                raise ValueError("from_publication_date must not be later than to_publication_date")
            normalized_work_type = self._normalize_work_type(work_type)
            self._validate_bool(open_access_only, "open_access_only")
            self._validate_min_citation_count(min_citation_count)
            effective_max_results = max_results
            effective_page = page
        else:
            normalized_query = self._normalize_work_id(normalized_query)
            normalized_cursor = ""
            normalized_sort = ""
            normalized_order = ""
            normalized_from_date = ""
            normalized_to_date = ""
            normalized_work_type = ""
            open_access_only = False
            min_citation_count = 0
            effective_max_results = 1
            effective_page = 1

        context = {
            "mode": normalized_mode,
            "query": normalized_query,
            "max_results": effective_max_results,
            "page": effective_page,
            "cursor": normalized_cursor,
            "sort": normalized_sort,
            "order": normalized_order,
            "from_publication_date": normalized_from_date,
            "to_publication_date": normalized_to_date,
            "work_type": normalized_work_type,
            "open_access_only": open_access_only,
            "min_citation_count": min_citation_count,
        }

        try:
            if normalized_mode == "search":
                data = self._search(
                    query=normalized_query,
                    max_results=effective_max_results,
                    page=effective_page,
                    cursor=normalized_cursor,
                    sort=normalized_sort,
                    order=normalized_order,
                    from_publication_date=normalized_from_date,
                    to_publication_date=normalized_to_date,
                    work_type=normalized_work_type,
                    open_access_only=open_access_only,
                    min_citation_count=min_citation_count,
                )
                meta = data.get("meta")
                raw_works = data.get("results")
                if not isinstance(meta, dict) or not isinstance(raw_works, list):
                    raise ValueError("invalid OpenAlex search response")
                total_results = self._safe_int(meta.get("count"))
                next_cursor = meta.get("next_cursor") or ""
            else:
                raw_works = [self._get_work(normalized_query)]
                total_results = 1
                next_cursor = ""

            works = [self._parse_work(work) for work in raw_works]
            return {
                **context,
                "total_results": total_results,
                "returned_results": len(works),
                "next_cursor": next_cursor,
                "works": works,
            }
        except _OpenAlexAPIError as exc:
            return self._error_result(**context, error_type="api_error", message=str(exc))
        except requests.Timeout:
            return self._error_result(
                **context,
                error_type="request_timeout",
                message="OpenAlex request timed out.",
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = (
                f"OpenAlex returned HTTP status {status_code}." if status_code else "OpenAlex HTTP request failed."
            )
            return self._error_result(**context, error_type="http_error", message=message)
        except requests.RequestException as exc:
            return self._error_result(
                **context,
                error_type="request_error",
                message=f"OpenAlex request failed: {exc}",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context,
                error_type="invalid_response",
                message=f"Unable to parse OpenAlex response: {exc}",
            )

    def _search(
        self,
        query: str,
        max_results: int,
        page: int,
        cursor: str,
        sort: str,
        order: str,
        from_publication_date: str,
        to_publication_date: str,
        work_type: str,
        open_access_only: bool,
        min_citation_count: int,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "search": query,
            "per_page": max_results,
            "sort": f"{sort}:{order}",
            "select": self.SELECT_FIELDS,
        }
        if cursor:
            params["cursor"] = cursor
        else:
            params["page"] = page

        filters = []
        if from_publication_date:
            filters.append(f"from_publication_date:{from_publication_date}")
        if to_publication_date:
            filters.append(f"to_publication_date:{to_publication_date}")
        if work_type:
            filters.append(f"type:{work_type}")
        if open_access_only:
            filters.append("open_access.is_oa:true")
        if min_citation_count > 0:
            filters.append(f"cited_by_count:>{min_citation_count - 1}")
        if filters:
            params["filter"] = ",".join(filters)

        return self._request(f"{self.base_url}/works", params)

    def _get_work(self, work_id: str) -> dict[str, Any]:
        return self._request(
            f"{self.base_url}/works/{quote(work_id, safe=':')}",
            {"select": self.SELECT_FIELDS},
        )

    def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        request_params = dict(params)
        if self.api_key:
            request_params["api_key"] = self.api_key
        if self.email:
            request_params["mailto"] = self.email
        response = requests.get(url, params=request_params, timeout=self.timeout)
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid OpenAlex JSON response") from exc
        if not isinstance(data, dict):
            raise ValueError("invalid OpenAlex response")
        if data.get("error"):
            message = data.get("message") or data.get("error")
            raise _OpenAlexAPIError(f"OpenAlex API error: {message}")
        return data

    @classmethod
    def _parse_work(cls, work: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(work, dict):
            raise ValueError("work must be an object")
        authorships = work.get("authorships") or []
        if not isinstance(authorships, list):
            authorships = []
        authors = [cls._parse_authorship(item) for item in authorships[: cls.MAX_AUTHORS] if isinstance(item, dict)]
        primary_location = work.get("primary_location") or {}
        if not isinstance(primary_location, dict):
            primary_location = {}
        source = primary_location.get("source") or {}
        if not isinstance(source, dict):
            source = {}
        open_access = work.get("open_access") or {}
        if not isinstance(open_access, dict):
            open_access = {}

        return {
            "openalex_id": cls._short_openalex_id(work.get("id")),
            "doi": cls._strip_doi_url(work.get("doi")),
            "title": work.get("display_name") or "",
            "abstract": cls._reconstruct_abstract(work.get("abstract_inverted_index")),
            "publication_year": cls._safe_int(work.get("publication_year")),
            "publication_date": work.get("publication_date") or "",
            "type": work.get("type") or "",
            "language": work.get("language") or "",
            "authors": authors,
            "author_count": len(authorships),
            "authors_truncated": len(authorships) > cls.MAX_AUTHORS,
            "venue": {
                "openalex_id": cls._short_openalex_id(source.get("id")),
                "name": source.get("display_name") or "",
                "issn_l": source.get("issn_l") or "",
                "type": source.get("type") or "",
            },
            "open_access": {
                "is_open_access": bool(open_access.get("is_oa")),
                "status": open_access.get("oa_status") or "",
                "url": open_access.get("oa_url") or "",
            },
            "citation_count": cls._safe_int(work.get("cited_by_count")),
            "reference_count": cls._safe_int(work.get("referenced_works_count")),
            "topics": cls._parse_topics(work.get("topics")),
            "keywords": cls._parse_keywords(work.get("keywords")),
            "landing_page_url": primary_location.get("landing_page_url") or "",
            "pdf_url": primary_location.get("pdf_url") or "",
        }

    @classmethod
    def _parse_authorship(cls, authorship: dict[str, Any]) -> dict[str, Any]:
        author = authorship.get("author") or {}
        if not isinstance(author, dict):
            author = {}
        institutions = authorship.get("institutions") or []
        if not isinstance(institutions, list):
            institutions = []
        return {
            "openalex_id": cls._short_openalex_id(author.get("id")),
            "name": author.get("display_name") or authorship.get("raw_author_name") or "",
            "orcid": author.get("orcid") or "",
            "position": authorship.get("author_position") or "",
            "is_corresponding": bool(authorship.get("is_corresponding")),
            "institutions": [
                {
                    "openalex_id": cls._short_openalex_id(item.get("id")),
                    "name": item.get("display_name") or "",
                    "country_code": item.get("country_code") or "",
                }
                for item in institutions[:5]
                if isinstance(item, dict)
            ],
        }

    @classmethod
    def _parse_topics(cls, raw_topics: Any) -> list[dict[str, Any]]:
        topics = raw_topics if isinstance(raw_topics, list) else []
        return [
            {
                "openalex_id": cls._short_openalex_id(topic.get("id")),
                "name": topic.get("display_name") or "",
                "score": topic.get("score") or 0,
                "field": cls._nested_name(topic, "field"),
                "domain": cls._nested_name(topic, "domain"),
            }
            for topic in topics[: cls.MAX_TOPICS]
            if isinstance(topic, dict)
        ]

    @classmethod
    def _parse_keywords(cls, raw_keywords: Any) -> list[dict[str, Any]]:
        keywords = raw_keywords if isinstance(raw_keywords, list) else []
        return [
            {
                "name": keyword.get("display_name") or "",
                "score": keyword.get("score") or 0,
            }
            for keyword in keywords[: cls.MAX_KEYWORDS]
            if isinstance(keyword, dict)
        ]

    @staticmethod
    def _nested_name(item: dict[str, Any], field: str) -> str:
        nested = item.get(field) or {}
        return nested.get("display_name") or "" if isinstance(nested, dict) else ""

    @staticmethod
    def _reconstruct_abstract(inverted_index: Any) -> str:
        if not isinstance(inverted_index, dict):
            return ""
        positioned_words = []
        for word, positions in inverted_index.items():
            if not isinstance(word, str) or not isinstance(positions, list):
                continue
            positioned_words.extend((position, word) for position in positions if isinstance(position, int))
        return " ".join(word for _, word in sorted(positioned_words))

    @staticmethod
    def _short_openalex_id(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return value.rstrip("/").rsplit("/", 1)[-1]

    @staticmethod
    def _strip_doi_url(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized not in cls.MODES:
            raise ValueError(f"mode must be one of: {', '.join(sorted(cls.MODES))}")
        return normalized

    @classmethod
    def _normalize_sort(cls, sort: str) -> str:
        key = sort.strip().lower().replace("-", "_").replace(" ", "_") if isinstance(sort, str) else ""
        normalized = cls.SORT_FIELDS.get(key)
        if normalized is None:
            raise ValueError(f"sort must be one of: {', '.join(sorted(cls.SORT_FIELDS))}")
        return normalized

    @classmethod
    def _normalize_order(cls, order: str) -> str:
        normalized = order.strip().lower() if isinstance(order, str) else ""
        if normalized not in cls.ORDERS:
            raise ValueError(f"order must be one of: {', '.join(sorted(cls.ORDERS))}")
        return normalized

    @staticmethod
    def _normalize_cursor(cursor: str | None) -> str:
        if cursor is None:
            return ""
        if not isinstance(cursor, str) or not cursor.strip():
            raise ValueError("cursor must be a non-empty string when provided")
        return cursor.strip()

    @staticmethod
    def _normalize_work_type(work_type: str | None) -> str:
        if work_type is None:
            return ""
        if not isinstance(work_type, str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", work_type.strip().lower()):
            raise ValueError("work_type must be a lowercase OpenAlex work type")
        return work_type.strip().lower()

    @staticmethod
    def _normalize_date(value: str | None, field_name: str, upper_bound: bool) -> str:
        if value is None:
            return ""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a date string")
        normalized = value.strip()
        if not re.fullmatch(r"\d{4}(-\d{2}){0,2}", normalized):
            raise ValueError(f"{field_name} must use YYYY, YYYY-MM, or YYYY-MM-DD format")
        parts = [int(part) for part in normalized.split("-")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else (12 if upper_bound else 1)
        day = parts[2] if len(parts) > 2 else (monthrange(year, month)[1] if upper_bound else 1)
        try:
            return date(year, month, day).isoformat()
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a valid date") from exc

    @staticmethod
    def _normalize_work_id(query: str) -> str:
        value = query.strip()
        value = re.sub(r"^https?://(?:api\.)?openalex\.org/works/", "", value, flags=re.I)
        value = re.sub(r"^https?://openalex\.org/", "", value, flags=re.I)
        doi_match = re.match(r"^(?:https?://(?:dx\.)?doi\.org/|doi:)(10\.\S+)$", value, flags=re.I)
        if doi_match:
            return f"doi:{doi_match.group(1)}"
        if re.fullmatch(r"W\d+", value, flags=re.I):
            return value.upper()
        if re.fullmatch(r"pmid:\d+", value, flags=re.I):
            return value.lower()
        raise ValueError("query must be an OpenAlex work ID, DOI, DOI URL, or PMID identifier in work mode")

    @staticmethod
    def _validate_max_results(max_results: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")

    @staticmethod
    def _validate_page(page: int, max_results: int) -> None:
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        if page > 500 or page * max_results > 10000:
            raise ValueError("page and max_results must stay within OpenAlex's first 10,000 results")

    @staticmethod
    def _validate_bool(value: Any, field_name: str) -> None:
        if not isinstance(value, bool):
            raise ValueError(f"{field_name} must be a boolean")

    @staticmethod
    def _validate_min_citation_count(value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("min_citation_count must be a non-negative integer")

    @staticmethod
    def _safe_int(value: Any) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _error_result(
        mode: str,
        query: str,
        max_results: int,
        page: int,
        cursor: str,
        sort: str,
        order: str,
        from_publication_date: str,
        to_publication_date: str,
        work_type: str,
        open_access_only: bool,
        min_citation_count: int,
        error_type: str,
        message: str,
    ) -> dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "page": page,
            "cursor": cursor,
            "sort": sort,
            "order": order,
            "from_publication_date": from_publication_date,
            "to_publication_date": to_publication_date,
            "work_type": work_type,
            "open_access_only": open_access_only,
            "min_citation_count": min_citation_count,
            "total_results": 0,
            "returned_results": 0,
            "next_cursor": "",
            "works": [],
            "error": {"type": error_type, "message": message},
        }
