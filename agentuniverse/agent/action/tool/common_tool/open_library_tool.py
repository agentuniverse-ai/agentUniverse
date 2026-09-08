#!/usr/bin/env python3
# ruff: noqa: TRY003, TRY004

"""Book discovery through the Open Library Search API."""

import re
from typing import Any, ClassVar

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool


class OpenLibraryTool(Tool):
    """Search Open Library and return normalized book metadata."""

    SEARCH_FIELDS: ClassVar[set[str]] = {"keyword", "title", "author", "isbn"}
    MAX_OFFSET: ClassVar[int] = 9999
    MAX_FIELD_ITEMS: ClassVar[int] = 20
    RESPONSE_FIELDS: ClassVar[tuple[str, ...]] = (
        "key",
        "title",
        "subtitle",
        "author_name",
        "author_key",
        "isbn",
        "publisher",
        "language",
        "first_publish_year",
        "publish_year",
        "edition_count",
        "cover_i",
        "subject",
        "ebook_access",
    )

    base_url: str = "https://openlibrary.org"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    user_agent: str = (
        "agentUniverse-OpenLibrary-Tool/1.0 "
        "(+https://github.com/agentuniverse-ai/agentUniverse)"
    )

    def execute(
        self,
        query: str,
        search_field: str = "keyword",
        max_results: int = 5,
        page: int = 1,
        from_year: int | None = None,
        until_year: int | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Search for books using keywords, title, author, or ISBN.

        Args:
            query: Text to find, or an ISBN when search_field is isbn.
            search_field: One of keyword, title, author, or isbn.
            max_results: Results per page, from 1 to 20.
            page: One-based result page.
            from_year: Optional inclusive lower bound for first publication year.
            until_year: Optional inclusive upper bound for first publication year.
            language: Optional ISO 639-2 three-letter language code.

        Returns:
            Search context, counts, and normalized books. Network and malformed
            API responses are represented by a structured ``error`` field.

        Raises:
            ValueError: If an input is empty, unsupported, or out of bounds.
        """
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")
        normalized_field = self._normalize_search_field(search_field)
        self._validate_pagination(max_results, page)
        normalized_from_year = self._normalize_year(from_year, "from_year")
        normalized_until_year = self._normalize_year(until_year, "until_year")
        if (
            normalized_from_year is not None
            and normalized_until_year is not None
            and normalized_from_year > normalized_until_year
        ):
            raise ValueError("from_year must not be later than until_year")
        normalized_language = self._normalize_language(language)
        if normalized_field == "isbn":
            normalized_query = self._normalize_isbn(normalized_query)

        offset = (page - 1) * max_results
        context = {
            "query": normalized_query,
            "search_field": normalized_field,
            "max_results": max_results,
            "page": page,
            "offset": offset,
            "from_year": normalized_from_year,
            "until_year": normalized_until_year,
            "language": normalized_language,
        }

        try:
            data = self._search(context)
            docs = self._search_documents(data)
            books = [self._parse_book(doc) for doc in docs]
            total_results = self._as_int(data.get("numFound", data.get("num_found")))
            return {
                **context,
                "total_results": total_results,
                "returned_results": len(books),
                "books": books,
            }
        except requests.Timeout:
            return self._error_result(**context, error_type="request_timeout", message="Open Library request timed out.")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            message = f"Open Library returned HTTP status {status}." if status else "Open Library HTTP request failed."
            return self._error_result(**context, error_type="http_error", message=message)
        except requests.RequestException:
            return self._error_result(**context, error_type="request_error", message="Open Library request failed.")
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context,
                error_type="invalid_response",
                message=f"Unable to parse Open Library response: {exc}",
            )

    def _search(self, context: dict[str, Any]) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/search.json",
            params={
                "q": self._build_query(context),
                "page": context["page"],
                "limit": context["max_results"],
                "fields": ",".join(self.RESPONSE_FIELDS),
            },
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid Open Library JSON response") from exc
        if not isinstance(data, dict):
            raise ValueError("invalid Open Library response")
        return data

    @staticmethod
    def _search_documents(data: dict[str, Any]) -> list[Any]:
        docs = data.get("docs", [])
        if not isinstance(docs, list):
            raise ValueError("invalid search documents")
        return docs

    @classmethod
    def _build_query(cls, context: dict[str, Any]) -> str:
        value = cls._escape_query_value(context["query"])
        search_field = context["search_field"]
        clauses = [value if search_field == "keyword" else f'{search_field}:"{value}"']

        from_year = context["from_year"]
        until_year = context["until_year"]
        if from_year is not None or until_year is not None:
            lower = from_year if from_year is not None else "*"
            upper = until_year if until_year is not None else "*"
            clauses.append(f"first_publish_year:[{lower} TO {upper}]")
        if context["language"]:
            clauses.append(f'language:"{context["language"]}"')
        return " AND ".join(clauses)

    @staticmethod
    def _escape_query_value(value: str) -> str:
        special_characters = set(r'+-&|!(){}[]^"~*?:\\/')
        return "".join(f"\\{character}" if character in special_characters else character for character in value)

    @classmethod
    def _normalize_search_field(cls, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if normalized not in cls.SEARCH_FIELDS:
            raise ValueError(f"search_field must be one of: {', '.join(sorted(cls.SEARCH_FIELDS))}")
        return normalized

    @classmethod
    def _validate_pagination(cls, max_results: int, page: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError("max_results must be an integer between 1 and 20")
        if not 1 <= max_results <= 20:
            raise ValueError("max_results must be between 1 and 20")
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        if (page - 1) * max_results > cls.MAX_OFFSET:
            raise ValueError("page and max_results must produce an offset below 10000")

    @staticmethod
    def _normalize_year(value: int | None, field_name: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")
        if not 1 <= value <= 9999:
            raise ValueError(f"{field_name} must be between 1 and 9999")
        return value

    @staticmethod
    def _normalize_language(value: str | None) -> str:
        if value is None:
            return ""
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if not re.fullmatch(r"[a-z]{3}", normalized):
            raise ValueError("language must be an ISO 639-2 three-letter code")
        return normalized

    @classmethod
    def _normalize_isbn(cls, value: str) -> str:
        normalized = re.sub(r"[-\s]", "", value).upper()
        if not (cls._valid_isbn10(normalized) or cls._valid_isbn13(normalized)):
            raise ValueError("query must contain a valid ISBN-10 or ISBN-13")
        return normalized

    @staticmethod
    def _valid_isbn10(value: str) -> bool:
        if not re.fullmatch(r"\d{9}[\dX]", value):
            return False
        digits = [10 if char == "X" else int(char) for char in value]
        return sum((10 - index) * digit for index, digit in enumerate(digits)) % 11 == 0

    @staticmethod
    def _valid_isbn13(value: str) -> bool:
        if not re.fullmatch(r"\d{13}", value):
            return False
        total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(value[:12]))
        return (10 - total % 10) % 10 == int(value[-1])

    @classmethod
    def _parse_book(cls, doc: Any) -> dict[str, Any]:
        if not isinstance(doc, dict):
            raise ValueError("invalid book document")
        key = cls._string(doc.get("key"))
        cover_id = cls._as_int(doc.get("cover_i"))
        return {
            "work_key": key,
            "title": cls._string(doc.get("title")),
            "subtitle": cls._string(doc.get("subtitle")),
            "authors": cls._string_list(doc.get("author_name")),
            "author_keys": cls._string_list(doc.get("author_key")),
            "isbn": cls._string_list(doc.get("isbn")),
            "publishers": cls._string_list(doc.get("publisher")),
            "languages": cls._string_list(doc.get("language")),
            "first_publish_year": cls._optional_int(doc.get("first_publish_year")),
            "publish_years": cls._int_list(doc.get("publish_year")),
            "edition_count": cls._as_int(doc.get("edition_count")),
            "subjects": cls._string_list(doc.get("subject")),
            "ebook_access": cls._string(doc.get("ebook_access")),
            "cover_url": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
            "work_url": f"https://openlibrary.org{key}" if key.startswith("/works/") else "",
        }

    @staticmethod
    def _string(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _string_list(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in (cls._string(item) for item in value) if item][: cls.MAX_FIELD_ITEMS]

    @classmethod
    def _int_list(cls, value: Any) -> list[int]:
        if not isinstance(value, list):
            return []
        values = [cls._optional_int(item) for item in value]
        return [item for item in values if item is not None][: cls.MAX_FIELD_ITEMS]

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _as_int(cls, value: Any) -> int:
        result = cls._optional_int(value)
        return result if result is not None else 0

    @staticmethod
    def _error_result(
        query: str,
        search_field: str,
        max_results: int,
        page: int,
        offset: int,
        from_year: int | None,
        until_year: int | None,
        language: str,
        error_type: str,
        message: str,
    ) -> dict[str, Any]:
        return {
            "query": query,
            "search_field": search_field,
            "max_results": max_results,
            "page": page,
            "offset": offset,
            "from_year": from_year,
            "until_year": until_year,
            "language": language,
            "total_results": 0,
            "returned_results": 0,
            "books": [],
            "error": {"type": error_type, "message": message},
        }
