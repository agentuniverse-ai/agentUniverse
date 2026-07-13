#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A lightweight scholarly metadata tool based on the Crossref REST API."""

import re
from calendar import monthrange
from datetime import date
from html.parser import HTMLParser
from typing import Any, ClassVar, Dict, List, Optional
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _CrossrefAPIError(Exception):
    """Raised when Crossref returns an API-level error response."""


class _MarkupTextExtractor(HTMLParser):
    """Extract text from HTML or JATS-style abstract markup."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


class CrossrefTool(Tool):
    """Search Crossref works or retrieve one work by DOI."""

    MODES: ClassVar[set[str]] = {"search", "doi"}
    SORT_FIELDS: ClassVar[set[str]] = {
        "created",
        "deposited",
        "indexed",
        "is-referenced-by-count",
        "issued",
        "published",
        "published-online",
        "published-print",
        "references-count",
        "relevance",
        "score",
        "updated",
    }
    SORT_ALIASES: ClassVar[Dict[str, str]] = {
        "citation-count": "is-referenced-by-count",
        "publication-date": "published",
        "reference-count": "references-count",
    }
    ORDERS: ClassVar[set[str]] = {"asc", "desc"}
    MAX_OFFSET: ClassVar[int] = 9999

    base_url: str = "https://api.crossref.org/v1"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    email: Optional[str] = Field(default_factory=lambda: get_from_env("CROSSREF_EMAIL"))
    user_agent: str = "agentUniverse-Crossref-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
        page: int = 1,
        cursor: Optional[str] = None,
        sort: str = "relevance",
        order: str = "desc",
        from_pub_date: Optional[str] = None,
        until_pub_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search scholarly works or retrieve metadata for a Crossref DOI.

        Args:
            query: Search keywords in search mode, or a DOI/DOI URL in doi mode.
            mode: Operation mode. Supports search and doi.
            max_results: Maximum search results to return, from 1 to 20.
            page: One-based search result page.
            cursor: Crossref cursor for deep pagination. Use * for the first cursor page.
            sort: Crossref field used to sort search results.
            order: Search sort order, either asc or desc.
            from_pub_date: Inclusive publication date lower bound.
            until_pub_date: Inclusive publication date upper bound.

        Returns:
            A dictionary containing operation context, result counts, and a
            list of normalized Crossref works. Network and API failures are
            returned in a structured ``error`` field.

        Raises:
            ValueError: If query, mode, or max_results is invalid.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")

        if normalized_mode == "search":
            self._validate_max_results(max_results)
            self._validate_page(page, max_results)
            normalized_cursor = self._normalize_cursor(cursor)
            if normalized_cursor and page != 1:
                raise ValueError("page must be 1 when cursor is provided")
            effective_max_results = max_results
            effective_page = page
            offset = 0 if normalized_cursor else (page - 1) * max_results
            normalized_sort = self._normalize_sort(sort)
            normalized_order = self._normalize_order(order)
            normalized_from_date = self._normalize_date(from_pub_date, "from_pub_date")
            normalized_until_date = self._normalize_date(until_pub_date, "until_pub_date")
            self._validate_date_range(normalized_from_date, normalized_until_date)
        else:
            normalized_query = self._normalize_doi(normalized_query)
            effective_max_results = 1
            effective_page = 1
            offset = 0
            normalized_cursor = ""
            normalized_sort = ""
            normalized_order = ""
            normalized_from_date = ""
            normalized_until_date = ""

        context = {
            "mode": normalized_mode,
            "query": normalized_query,
            "max_results": effective_max_results,
            "page": effective_page,
            "offset": offset,
            "cursor": normalized_cursor,
            "sort": normalized_sort,
            "order": normalized_order,
            "from_pub_date": normalized_from_date,
            "until_pub_date": normalized_until_date,
        }

        try:
            if normalized_mode == "search":
                total_results, raw_works, next_cursor = self._search(
                    query=normalized_query,
                    max_results=effective_max_results,
                    offset=offset,
                    cursor=normalized_cursor,
                    sort=normalized_sort,
                    order=normalized_order,
                    from_pub_date=normalized_from_date,
                    until_pub_date=normalized_until_date,
                )
            else:
                raw_works = [self._lookup_doi(normalized_query)]
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
        except _CrossrefAPIError as exc:
            return self._error_result(
                **context,
                error_type="api_error",
                message=str(exc),
            )
        except requests.Timeout:
            return self._error_result(
                **context,
                error_type="request_timeout",
                message="Crossref request timed out.",
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = (
                f"Crossref returned HTTP status {status_code}." if status_code else "Crossref HTTP request failed."
            )
            return self._error_result(
                **context,
                error_type="http_error",
                message=message,
            )
        except requests.RequestException as exc:
            return self._error_result(
                **context,
                error_type="request_error",
                message=f"Crossref request failed: {exc}",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context,
                error_type="invalid_response",
                message=f"Unable to parse Crossref response: {exc}",
            )

    def _search(
        self,
        query: str,
        max_results: int,
        offset: int,
        cursor: str,
        sort: str,
        order: str,
        from_pub_date: str,
        until_pub_date: str,
    ) -> tuple[int, List[Dict[str, Any]], str]:
        params: Dict[str, Any] = {
            "query.bibliographic": query,
            "rows": max_results,
            "sort": sort,
            "order": order,
        }
        if cursor:
            params["cursor"] = cursor
        else:
            params["offset"] = offset
        filters = []
        if from_pub_date:
            filters.append(f"from-pub-date:{from_pub_date}")
        if until_pub_date:
            filters.append(f"until-pub-date:{until_pub_date}")
        if filters:
            params["filter"] = ",".join(filters)

        data = self._request("/works", params=params)
        if data.get("message-type") != "work-list":
            raise ValueError("unexpected message-type for Crossref search")

        message = data.get("message")
        if not isinstance(message, dict):
            raise ValueError("missing search message")
        items = message.get("items")
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise ValueError("invalid search items")
        next_cursor = self._string_value(message.get("next-cursor")) if cursor else ""
        return int(message.get("total-results", 0)), items, next_cursor

    def _lookup_doi(self, doi: str) -> Dict[str, Any]:
        data = self._request(f"/works/{quote(doi, safe='')}")
        if data.get("message-type") != "work":
            raise ValueError("unexpected message-type for Crossref DOI lookup")

        message = data.get("message")
        if not isinstance(message, dict):
            raise ValueError("missing DOI message")
        return message

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        request_params = dict(params or {})
        if self.email:
            request_params["mailto"] = self.email

        response = requests.get(
            f"{self.base_url}{path}",
            params=request_params,
            headers={"User-Agent": self._user_agent_value()},
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid Crossref JSON response") from exc

        if not isinstance(data, dict):
            raise ValueError("invalid Crossref response")
        if data.get("status") != "ok":
            message = self._api_error_message(data.get("message"))
            raise _CrossrefAPIError(f"Crossref API error: {message}")
        return data

    def _user_agent_value(self) -> str:
        if self.email:
            return f"{self.user_agent} (mailto:{self.email})"
        return self.user_agent

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized_mode = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized_mode not in cls.MODES:
            raise ValueError("mode must be one of: doi, search")
        return normalized_mode

    @staticmethod
    def _validate_max_results(max_results: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")

    @classmethod
    def _validate_page(cls, page: int, max_results: int) -> None:
        if isinstance(page, bool) or not isinstance(page, int):
            raise ValueError("page must be a positive integer")
        if page < 1:
            raise ValueError("page must be a positive integer")
        if (page - 1) * max_results > cls.MAX_OFFSET:
            raise ValueError("page and max_results must produce an offset below 10000")

    @classmethod
    def _normalize_sort(cls, sort: str) -> str:
        normalized_sort = sort.strip().lower().replace("_", "-") if isinstance(sort, str) else ""
        normalized_sort = cls.SORT_ALIASES.get(normalized_sort, normalized_sort)
        if normalized_sort not in cls.SORT_FIELDS:
            raise ValueError(f"sort must be one of: {', '.join(sorted(cls.SORT_FIELDS))}")
        return normalized_sort

    @classmethod
    def _normalize_order(cls, order: str) -> str:
        normalized_order = order.strip().lower() if isinstance(order, str) else ""
        if normalized_order not in cls.ORDERS:
            raise ValueError("order must be one of: asc, desc")
        return normalized_order

    @staticmethod
    def _normalize_cursor(cursor: Optional[str]) -> str:
        if cursor is None or cursor == "":
            return ""
        normalized_cursor = cursor.strip() if isinstance(cursor, str) else ""
        if not normalized_cursor:
            raise ValueError("cursor must be a non-empty string")
        return normalized_cursor

    @staticmethod
    def _normalize_date(value: Optional[str], parameter_name: str) -> str:
        if value is None or value == "":
            return ""
        normalized_value = value.strip() if isinstance(value, str) else ""
        if not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", normalized_value):
            raise ValueError(f"{parameter_name} must use YYYY, YYYY-MM, or YYYY-MM-DD format")
        try:
            parts = [int(part) for part in normalized_value.split("-")]
            date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
        except ValueError as exc:
            raise ValueError(f"{parameter_name} must be a valid date") from exc
        return normalized_value

    @classmethod
    def _validate_date_range(cls, from_pub_date: str, until_pub_date: str) -> None:
        if not from_pub_date or not until_pub_date:
            return
        if cls._date_bound(from_pub_date, upper=False) > cls._date_bound(until_pub_date, upper=True):
            raise ValueError("from_pub_date must not be later than until_pub_date")

    @staticmethod
    def _date_bound(value: str, upper: bool) -> date:
        parts = [int(part) for part in value.split("-")]
        year = parts[0]
        month = parts[1] if len(parts) > 1 else (12 if upper else 1)
        day = parts[2] if len(parts) > 2 else (monthrange(year, month)[1] if upper else 1)
        return date(year, month, day)

    @staticmethod
    def _normalize_doi(value: str) -> str:
        doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.IGNORECASE).strip()
        if not doi.startswith("10.") or "/" not in doi or any(character.isspace() for character in doi):
            raise ValueError("query must contain a valid DOI in doi mode")
        return doi

    @classmethod
    def _parse_work(cls, work: Dict[str, Any]) -> Dict[str, Any]:
        doi = cls._string_value(work.get("DOI"))
        url = cls._string_value(work.get("URL"))
        if not url and doi:
            url = f"https://doi.org/{quote(doi, safe='/')}"

        return {
            "doi": doi,
            "title": cls._first_text(work.get("title")),
            "subtitle": cls._first_text(work.get("subtitle")),
            "authors": cls._authors(work.get("author")),
            "abstract": cls._markup_text(work.get("abstract")),
            "container_title": cls._first_text(work.get("container-title")),
            "published": cls._published_date(work.get("published")),
            "publisher": cls._string_value(work.get("publisher")),
            "type": cls._string_value(work.get("type")),
            "url": url,
            "issn": cls._string_list(work.get("ISSN")),
            "isbn": cls._string_list(work.get("ISBN")),
            "subjects": cls._string_list(work.get("subject")),
            "language": cls._string_value(work.get("language")),
            "volume": cls._string_value(work.get("volume")),
            "issue": cls._string_value(work.get("issue")),
            "pages": cls._string_value(work.get("page")),
            "citation_count": cls._integer_value(work.get("is-referenced-by-count")),
            "reference_count": cls._integer_value(work.get("references-count")),
            "funders": cls._funders(work.get("funder")),
            "licenses": cls._licenses(work.get("license")),
        }

    @classmethod
    def _authors(cls, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []

        authors = []
        for author in value:
            if not isinstance(author, dict):
                continue
            given = cls._string_value(author.get("given"))
            family = cls._string_value(author.get("family"))
            full_name = " ".join(part for part in (given, family) if part)
            if not full_name:
                full_name = cls._string_value(author.get("name"))
            if full_name:
                authors.append(full_name)
        return authors

    @classmethod
    def _funders(cls, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        funders = []
        for funder in value:
            if not isinstance(funder, dict):
                continue
            name = cls._string_value(funder.get("name"))
            doi = cls._string_value(funder.get("DOI"))
            awards = cls._string_list(funder.get("award"))
            if name or doi or awards:
                funders.append({"name": name, "doi": doi, "awards": awards})
        return funders

    @classmethod
    def _licenses(cls, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        licenses = []
        for license_item in value:
            if not isinstance(license_item, dict):
                continue
            url = cls._string_value(license_item.get("URL"))
            if not url:
                continue
            licenses.append(
                {
                    "url": url,
                    "start_date": cls._published_date(license_item.get("start")),
                    "content_version": cls._string_value(license_item.get("content-version")),
                    "delay_in_days": cls._integer_value(license_item.get("delay-in-days")),
                }
            )
        return licenses

    @staticmethod
    def _markup_text(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        parser = _MarkupTextExtractor()
        parser.feed(value)
        parser.close()
        return parser.text()

    @staticmethod
    def _published_date(value: Any) -> str:
        if not isinstance(value, dict):
            return ""
        date_parts = value.get("date-parts")
        if not isinstance(date_parts, list) or not date_parts or not isinstance(date_parts[0], list):
            return ""

        parts = date_parts[0][:3]
        if not parts or not all(isinstance(part, int) and not isinstance(part, bool) for part in parts):
            return ""
        return "-".join(str(part).zfill(2) if index else str(part).zfill(4) for index, part in enumerate(parts))

    @classmethod
    def _first_text(cls, value: Any) -> str:
        if isinstance(value, str):
            return cls._markup_text(value)
        if isinstance(value, list):
            for item in value:
                text = cls._markup_text(item)
                if text:
                    return text
        return ""

    @staticmethod
    def _string_value(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _string_list(cls, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []
        values = []
        for item in value:
            normalized_item = cls._string_value(item)
            if normalized_item and normalized_item not in values:
                values.append(normalized_item)
        return values

    @staticmethod
    def _integer_value(value: Any) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) else 0

    @staticmethod
    def _api_error_message(value: Any) -> str:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, list):
            messages = []
            for item in value:
                if isinstance(item, dict) and isinstance(item.get("message"), str):
                    messages.append(item["message"].strip())
                elif item is not None:
                    messages.append(str(item))
            if messages:
                return "; ".join(message for message in messages if message)
        return "unknown Crossref API error"

    @staticmethod
    def _error_result(
        mode: str,
        query: str,
        max_results: int,
        page: int,
        offset: int,
        cursor: str,
        sort: str,
        order: str,
        from_pub_date: str,
        until_pub_date: str,
        error_type: str,
        message: str,
    ) -> Dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "page": page,
            "offset": offset,
            "cursor": cursor,
            "sort": sort,
            "order": order,
            "from_pub_date": from_pub_date,
            "until_pub_date": until_pub_date,
            "total_results": 0,
            "returned_results": 0,
            "next_cursor": "",
            "works": [],
            "error": {"type": error_type, "message": message},
        }
