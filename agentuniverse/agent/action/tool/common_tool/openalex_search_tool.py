#!/usr/bin/env python3

"""Search scholarly works using the OpenAlex Works API."""

import math
from datetime import date
from typing import Any, ClassVar

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class OpenAlexSearchTool(Tool):
    """Search OpenAlex with bounded results and normalized work metadata.

    Attributes:
        api_key: Optional OpenAlex key, defaulting to OPENALEX_API_KEY.
        timeout: Positive, finite HTTP timeout in seconds.
    """

    API_URL: ClassVar[str] = "https://api.openalex.org/works"
    SORT_FIELDS: ClassVar[set[str]] = {"relevance_score", "publication_date", "cited_by_count"}
    MAX_ABSTRACT_WORDS: ClassVar[int] = 1000
    MAX_ABSTRACT_CHARS: ClassVar[int] = 4000
    MAX_AUTHORS: ClassVar[int] = 20
    WORK_FIELDS: ClassVar[str] = ",".join(
        (
            "id",
            "doi",
            "display_name",
            "publication_year",
            "publication_date",
            "type",
            "language",
            "cited_by_count",
            "authorships",
            "open_access",
            "primary_location",
            "best_oa_location",
            "abstract_inverted_index",
        )
    )

    api_key: str | None = Field(
        default_factory=lambda: get_from_env("OPENALEX_API_KEY"),
        repr=False,
        exclude=True,
    )
    timeout: float = 15.0

    def execute(
        self,
        query: str,
        max_results: int = 5,
        page: int = 1,
        sort: str = "relevance_score",
        order: str = "desc",
        from_publication_date: str | None = None,
        to_publication_date: str | None = None,
        open_access_only: bool = False,
    ) -> dict[str, Any]:
        """Search titles, abstracts, and available indexed full text.

        Args:
            query: Nonempty keywords or an OpenAlex Boolean search expression.
            max_results: Number of works per page, from 1 to 20.
            page: One-based page; page * max_results must not exceed 10,000.
            sort: relevance_score, publication_date, or cited_by_count.
            order: asc or desc, applied by OpenAlex before pagination.
            from_publication_date: Inclusive lower date bound, YYYY-MM-DD.
            to_publication_date: Inclusive upper date bound, YYYY-MM-DD.
            open_access_only: Whether to require open-access works.

        Returns:
            Search context, counts, next_page, and normalized works. Network,
            HTTP, API, and malformed-response failures have an error field.
            Abstracts and author lists have explicit truncation flags.

        Raises:
            ValueError: If arguments, timeout, or encoded query length are invalid.
        """
        self._require(isinstance(query, str) and bool(query.strip()), "query must be a nonempty string")
        query = query.strip()
        self._require(
            type(max_results) is int and 1 <= max_results <= 20, "max_results must be an integer between 1 and 20"
        )
        self._require(type(page) is int and page >= 1, "page must be a positive integer")
        self._require(page * max_results <= 10000, "page * max_results must not exceed 10000")
        self._require(
            isinstance(sort, str) and sort in self.SORT_FIELDS,
            "sort must be relevance_score, publication_date, or cited_by_count",
        )
        self._require(order in ("asc", "desc"), "order must be asc or desc")
        self._require(isinstance(open_access_only, bool), "open_access_only must be a boolean")
        self._validate_date(from_publication_date, "from_publication_date")
        self._validate_date(to_publication_date, "to_publication_date")
        self._require(
            not (from_publication_date and to_publication_date) or from_publication_date <= to_publication_date,
            "from_publication_date must not be later than to_publication_date",
        )
        self._require(
            not isinstance(self.timeout, bool)
            and isinstance(self.timeout, int | float)
            and math.isfinite(self.timeout)
            and self.timeout > 0,
            "timeout must be a positive finite number",
        )

        context = {
            "query": query,
            "max_results": max_results,
            "page": page,
            "sort": sort,
            "order": order,
            "from_publication_date": from_publication_date,
            "to_publication_date": to_publication_date,
            "open_access_only": open_access_only,
        }
        params = {
            "search": query,
            "per_page": max_results,
            "page": page,
            "sort": f"{sort}:{order}",
            "select": self.WORK_FIELDS,
        }
        filters = []
        if from_publication_date:
            filters.append(f"from_publication_date:{from_publication_date}")
        if to_publication_date:
            filters.append(f"to_publication_date:{to_publication_date}")
        if open_access_only:
            filters.append("is_oa:true")
        if filters:
            params["filter"] = ",".join(filters)
        prepared = requests.Request("GET", self.API_URL, params=params).prepare()
        self._require(
            len(prepared.url.encode("utf-8")) <= 4000, "encoded OpenAlex request URL must not exceed 4000 bytes"
        )
        return self._search(context, params)

    def _search(self, context: dict, params: dict) -> dict[str, Any]:
        """Make one request and normalize failures without echoing remote details."""
        headers = {"User-Agent": "agentUniverse-OpenAlex-Search-Tool/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            response = requests.get(
                self.API_URL,
                params=params,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=False,
            )
            if not 200 <= response.status_code < 300:
                message = f"OpenAlex returned HTTP status {response.status_code}."
                if response.status_code == 429:
                    message += " Rate limit or budget exceeded; retry later."
                elif response.status_code in (401, 403):
                    message += " Check OPENALEX_API_KEY and account access."
                return self._error_result(context, "http_error", message, response.status_code)
        except requests.Timeout:
            return self._error_result(context, "request_timeout", "OpenAlex request timed out.")
        except requests.RequestException:
            # Exception strings can include credentials or full request URLs.
            return self._error_result(context, "request_error", "Unable to connect to OpenAlex.")

        try:
            data = response.json()
            self._require(isinstance(data, dict), "expected a response object")
            if "error" in data:
                return self._error_result(
                    context,
                    "api_error",
                    "OpenAlex returned an API error; check query and filters.",
                )
            meta = data.get("meta")
            results = data.get("results")
            self._require(isinstance(meta, dict) and isinstance(results, list), "missing result metadata or works")
            total = meta.get("count")
            self._require(type(total) is int and total >= 0, "invalid result count")
            max_results, page = context["max_results"], context["page"]
            self._require(len(results) <= max_results, "result count exceeds the requested page size")
            works = [self._parse_work(work) for work in results]
            next_page = None
            if works and page * max_results < total and (page + 1) * max_results <= 10000:
                next_page = page + 1
            return {
                **context,
                "total_results": total,
                "returned_results": len(works),
                "next_page": next_page,
                "works": works,
            }
        except (ValueError, TypeError):
            return self._error_result(context, "invalid_response", "Invalid OpenAlex response.")

    @staticmethod
    def _require(condition: bool, message: str) -> None:
        """Keep validation errors consistent across inputs and response fields."""
        if not condition:
            raise ValueError(message)

    @classmethod
    def _validate_date(cls, value: str | None, name: str) -> None:
        if value is None:
            return
        message = f"{name} must be a valid YYYY-MM-DD date"
        cls._require(isinstance(value, str), message)
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            raise ValueError(message) from None
        cls._require(parsed.isoformat() == value, message)

    @classmethod
    def _object(cls, value: Any) -> dict:
        if value is None:
            return {}
        cls._require(isinstance(value, dict), "expected an object")
        return value

    @classmethod
    def _text(cls, value: Any) -> str:
        if value is None:
            return ""
        cls._require(isinstance(value, str), "expected text")
        return value

    @classmethod
    def _optional_integer(cls, value: Any) -> int | None:
        cls._require(value is None or (type(value) is int and value >= 0), "expected a nonnegative integer or null")
        return value

    @classmethod
    def _parse_work(cls, value: Any) -> dict[str, Any]:
        work = cls._object(value)
        work_id = cls._text(work.get("id"))
        cls._require(bool(work_id), "missing work ID")
        location = cls._object(work.get("primary_location"))
        source = cls._object(location.get("source"))
        oa = cls._object(work.get("open_access"))
        is_open_access = oa.get("is_oa")
        cls._require(is_open_access is None or isinstance(is_open_access, bool), "invalid open-access status")
        best_oa = cls._object(work.get("best_oa_location"))
        authorships = work.get("authorships")
        if authorships is None:
            authorships = []
        cls._require(isinstance(authorships, list), "invalid authorships")
        authors = []
        for authorship in authorships[: cls.MAX_AUTHORS]:
            author = cls._object(cls._object(authorship).get("author"))
            authors.append(
                {
                    "id": cls._text(author.get("id")),
                    "name": cls._text(author.get("display_name")),
                    "orcid": cls._text(author.get("orcid")),
                }
            )
        abstract, truncated = cls._abstract(work.get("abstract_inverted_index"))
        return {
            "id": work_id,
            "doi": cls._text(work.get("doi")),
            "title": cls._text(work.get("display_name")),
            "publication_year": cls._optional_integer(work.get("publication_year")),
            "publication_date": cls._text(work.get("publication_date")),
            "type": cls._text(work.get("type")),
            "language": cls._text(work.get("language")),
            "cited_by_count": cls._optional_integer(work.get("cited_by_count")),
            "authors": authors,
            "authors_truncated": len(authorships) > cls.MAX_AUTHORS,
            "venue": cls._text(source.get("display_name")),
            "is_open_access": is_open_access,
            "open_access_url": cls._text(oa.get("oa_url")),
            "pdf_url": cls._text(best_oa.get("pdf_url")),
            "abstract": abstract,
            "abstract_truncated": truncated,
        }

    @classmethod
    def _abstract(cls, value: Any) -> tuple[str, bool]:
        """Reconstruct a bounded abstract without allocating by remote positions."""
        index = cls._object(value)
        tokens = {}
        truncated = False
        for word, positions in index.items():
            cls._require(isinstance(word, str) and isinstance(positions, list), "invalid abstract index")
            for position in positions:
                cls._require(type(position) is int and position >= 0, "invalid abstract position")
                if position >= cls.MAX_ABSTRACT_WORDS:
                    truncated = True
                else:
                    tokens[position] = word
        text = " ".join(tokens[position] for position in sorted(tokens))
        return text[: cls.MAX_ABSTRACT_CHARS], (truncated or len(text) > cls.MAX_ABSTRACT_CHARS)

    @staticmethod
    def _error_result(
        context: dict,
        error_type: str,
        message: str,
        status_code: int | None = None,
    ) -> dict[str, Any]:
        return {
            **context,
            "total_results": None,
            "returned_results": 0,
            "next_page": None,
            "works": [],
            "error": {
                "type": error_type,
                "message": message,
                "status_code": status_code,
            },
        }
