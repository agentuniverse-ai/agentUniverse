#!/usr/bin/env python3

"""A lightweight scholarly metadata tool based on the OpenAlex API."""

import re
from datetime import date
from typing import Any, ClassVar
from urllib.parse import quote

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _OpenAlexAPIError(Exception):
    """Raised when OpenAlex reports an error inside an otherwise valid response."""


class OpenAlexTool(Tool):
    """Search OpenAlex works or retrieve one work by DOI or OpenAlex ID."""

    MODES: ClassVar[set[str]] = {"search", "work"}
    SORT_FIELDS: ClassVar[set[str]] = {
        "cited_by_count",
        "created_date",
        "publication_date",
        "relevance_score",
        "updated_date",
    }
    SORT_ALIASES: ClassVar[dict[str, str]] = {
        "citation_count": "cited_by_count",
        "citations": "cited_by_count",
        "published": "publication_date",
        "relevance": "relevance_score",
    }
    WORK_TYPE_ALIASES: ClassVar[dict[str, str]] = {
        "journal-article": "article",
        "proceedings-article": "article",
        "posted-content": "preprint",
        "book-section": "book-chapter",
    }
    MAX_RESULTS: ClassVar[int] = 200
    MAX_PAGED_RESULTS: ClassVar[int] = 10000

    base_url: str = "https://api.openalex.org"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    email: str | None = Field(default_factory=lambda: get_from_env("OPENALEX_EMAIL"))
    user_agent: str = "agentUniverse-OpenAlex-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
        page: int = 1,
        cursor: str | None = None,
        sort: str = "relevance",
        from_publication_date: str | None = None,
        to_publication_date: str | None = None,
        publication_year: int | None = None,
        work_type: str | None = None,
        open_access_only: bool = False,
        min_cited_by_count: int | None = None,
    ) -> dict[str, Any]:
        """Search OpenAlex works or retrieve metadata for one OpenAlex work.

        Args:
            query: Search keywords in search mode, or a DOI/DOI URL/OpenAlex
                work ID in work mode.
            mode: Operation mode. Supports search and work.
            max_results: Maximum search results to return, from 1 to 200.
            page: One-based search result page. Page-based paging can address
                the first 10,000 results; use cursor paging for deeper results.
            cursor: OpenAlex cursor for deep pagination. Use * for the first
                cursor page, then pass the returned next_cursor value.
            sort: OpenAlex work sort field. Results are sorted in descending order.
            from_publication_date: Inclusive publication date lower bound in
                YYYY-MM-DD format.
            to_publication_date: Inclusive publication date upper bound in
                YYYY-MM-DD format.
            publication_year: Optional exact publication year filter.
            work_type: Optional OpenAlex work type, such as article, book,
                preprint, or review.
            open_access_only: Whether to require an open-access work.
            min_cited_by_count: Optional non-negative citation threshold.
                OpenAlex expresses this filter as a strict lower bound, so a
                value of 10 matches works with more than 10 citations.

        Returns:
            A dictionary containing operation context, result counts, and a
            list of normalized OpenAlex works. Network and API failures are
            returned in a structured ``error`` field.

        Raises:
            ValueError: If query, mode, or any search parameter is invalid.
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
            normalized_sort = self._normalize_sort(sort)
            normalized_from_date = self._normalize_date(from_publication_date, "from_publication_date")
            normalized_to_date = self._normalize_date(to_publication_date, "to_publication_date")
            self._validate_date_range(normalized_from_date, normalized_to_date)
            normalized_publication_year = self._normalize_publication_year(publication_year)
            normalized_work_type = self._normalize_work_type(work_type)
            normalized_open_access_only = self._normalize_open_access_only(open_access_only)
            normalized_min_cited_by_count = self._normalize_min_cited_by_count(min_cited_by_count)
        else:
            normalized_query = self._normalize_work_identifier(normalized_query)
            effective_max_results = 1
            effective_page = 1
            normalized_cursor = ""
            normalized_sort = ""
            normalized_from_date = ""
            normalized_to_date = ""
            normalized_publication_year = None
            normalized_work_type = ""
            normalized_open_access_only = False
            normalized_min_cited_by_count = None

        context = {
            "mode": normalized_mode,
            "query": normalized_query,
            "max_results": effective_max_results,
            "page": effective_page,
            "cursor": normalized_cursor,
            "sort": normalized_sort,
            "from_publication_date": normalized_from_date,
            "to_publication_date": normalized_to_date,
            "publication_year": normalized_publication_year,
            "work_type": normalized_work_type,
            "open_access_only": normalized_open_access_only,
            "min_cited_by_count": normalized_min_cited_by_count,
        }

        try:
            if normalized_mode == "search":
                total_results, raw_works, next_cursor = self._search(
                    query=normalized_query,
                    max_results=effective_max_results,
                    page=effective_page,
                    cursor=normalized_cursor,
                    sort=normalized_sort,
                    from_publication_date=normalized_from_date,
                    to_publication_date=normalized_to_date,
                    publication_year=normalized_publication_year,
                    work_type=normalized_work_type,
                    open_access_only=normalized_open_access_only,
                    min_cited_by_count=normalized_min_cited_by_count,
                )
            else:
                raw_works = [self._lookup_work(normalized_query)]
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
            return self._error_result(context, "api_error", str(exc))
        except requests.Timeout:
            return self._error_result(context, "request_timeout", "OpenAlex request timed out.")
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = (
                f"OpenAlex returned HTTP status {status_code}." if status_code else "OpenAlex HTTP request failed."
            )
            return self._error_result(context, "http_error", message)
        except requests.RequestException as exc:
            return self._error_result(context, "request_error", f"OpenAlex request failed: {exc}")
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(context, "invalid_response", f"Unable to parse OpenAlex response: {exc}")

    def _search(
        self,
        query: str,
        max_results: int,
        page: int,
        cursor: str,
        sort: str,
        from_publication_date: str,
        to_publication_date: str,
        publication_year: int | None,
        work_type: str,
        open_access_only: bool,
        min_cited_by_count: int | None,
    ) -> tuple[int, list[dict[str, Any]], str]:
        params: dict[str, Any] = {
            "search": query,
            "per-page": max_results,
            "sort": f"{sort}:desc",
        }
        if cursor:
            params["cursor"] = cursor
        else:
            params["page"] = page

        filters = self._build_filters(
            from_publication_date=from_publication_date,
            to_publication_date=to_publication_date,
            publication_year=publication_year,
            work_type=work_type,
            open_access_only=open_access_only,
            min_cited_by_count=min_cited_by_count,
        )
        if filters:
            params["filter"] = ",".join(filters)

        data = self._request("/works", params=params)
        results = data.get("results")
        if not isinstance(results, list) or not all(isinstance(result, dict) for result in results):
            raise ValueError("invalid OpenAlex search results")

        meta = data.get("meta")
        if not isinstance(meta, dict):
            raise ValueError("missing OpenAlex search metadata")
        total_results = meta.get("count")
        if isinstance(total_results, bool) or not isinstance(total_results, int):
            raise ValueError("invalid OpenAlex result count")

        next_cursor = ""
        if cursor:
            next_cursor = self._string_value(meta.get("next_cursor"))
        return total_results, results, next_cursor

    @staticmethod
    def _build_filters(
        from_publication_date: str,
        to_publication_date: str,
        publication_year: int | None,
        work_type: str,
        open_access_only: bool,
        min_cited_by_count: int | None,
    ) -> list[str]:
        filters = []
        if from_publication_date:
            filters.append(f"from_publication_date:{from_publication_date}")
        if to_publication_date:
            filters.append(f"to_publication_date:{to_publication_date}")
        if publication_year is not None:
            filters.append(f"publication_year:{publication_year}")
        if work_type:
            filters.append(f"type:{work_type}")
        if open_access_only:
            filters.append("is_oa:true")
        if min_cited_by_count is not None:
            # OpenAlex filters accept comparison operators. Use > to make the
            # minimum citation threshold behave as "more than N citations".
            filters.append(f"cited_by_count:>{min_cited_by_count}")
        return filters

    def _lookup_work(self, identifier: str) -> dict[str, Any]:
        data = self._request(f"/works/{quote(identifier, safe=':/')}")
        if not self._path_id(data.get("id")):
            raise ValueError("missing OpenAlex work id")
        return data

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
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
            raise ValueError("invalid OpenAlex JSON response") from exc

        if not isinstance(data, dict):
            raise ValueError("invalid OpenAlex response")
        if data.get("error"):
            message = self._string_value(data.get("message")) or self._string_value(data.get("error"))
            raise _OpenAlexAPIError(f"OpenAlex API error: {message or 'unknown OpenAlex API error'}")
        return data

    def _user_agent_value(self) -> str:
        if self.email:
            return f"{self.user_agent} (mailto:{self.email})"
        return self.user_agent

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized_mode = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized_mode not in cls.MODES:
            raise ValueError("mode must be one of: search, work")
        return normalized_mode

    @classmethod
    def _validate_max_results(cls, max_results: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError(f"max_results must be an integer between 1 and {cls.MAX_RESULTS}")
        if not 1 <= max_results <= cls.MAX_RESULTS:
            raise ValueError(f"max_results must be between 1 and {cls.MAX_RESULTS}")

    @classmethod
    def _validate_page(cls, page: int, max_results: int) -> None:
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        if page * max_results > cls.MAX_PAGED_RESULTS:
            raise ValueError(
                "page and max_results must address results within the first 10000; use cursor for deeper pages"
            )

    @classmethod
    def _normalize_sort(cls, sort: str) -> str:
        normalized_sort = sort.strip().lower().replace("-", "_") if isinstance(sort, str) else ""
        normalized_sort = cls.SORT_ALIASES.get(normalized_sort, normalized_sort)
        if normalized_sort not in cls.SORT_FIELDS:
            raise ValueError(f"sort must be one of: {', '.join(sorted(cls.SORT_FIELDS))}")
        return normalized_sort

    @staticmethod
    def _normalize_cursor(cursor: str | None) -> str:
        if cursor is None or cursor == "":
            return ""
        normalized_cursor = cursor.strip() if isinstance(cursor, str) else ""
        if not normalized_cursor:
            raise ValueError("cursor must be a non-empty string")
        return normalized_cursor

    @staticmethod
    def _normalize_date(value: str | None, parameter_name: str) -> str:
        if value is None or value == "":
            return ""
        normalized_value = value.strip() if isinstance(value, str) else ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized_value):
            raise ValueError(f"{parameter_name} must use YYYY-MM-DD format")
        try:
            date.fromisoformat(normalized_value)
        except ValueError as exc:
            raise ValueError(f"{parameter_name} must be a valid date") from exc
        return normalized_value

    @staticmethod
    def _validate_date_range(from_publication_date: str, to_publication_date: str) -> None:
        if not from_publication_date or not to_publication_date:
            return
        if from_publication_date > to_publication_date:
            raise ValueError("from_publication_date must not be later than to_publication_date")

    @staticmethod
    def _normalize_publication_year(value: int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("publication_year must be an integer between 1 and 9999")
        if not 1 <= value <= 9999:
            raise ValueError("publication_year must be an integer between 1 and 9999")
        return value

    @classmethod
    def _normalize_work_type(cls, value: str | None) -> str:
        if value is None or value == "":
            return ""
        normalized_value = value.strip().lower().replace(" ", "-").replace("_", "-") if isinstance(value, str) else ""
        normalized_value = cls.WORK_TYPE_ALIASES.get(normalized_value, normalized_value)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", normalized_value):
            raise ValueError("work_type must be a single OpenAlex work type such as article, book, or preprint")
        return normalized_value

    @staticmethod
    def _normalize_open_access_only(value: bool) -> bool:
        if not isinstance(value, bool):
            raise ValueError("open_access_only must be a boolean")
        return value

    @staticmethod
    def _normalize_min_cited_by_count(value: int | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("min_cited_by_count must be a non-negative integer")
        return value

    @classmethod
    def _normalize_work_identifier(cls, value: str) -> str:
        doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value, flags=re.IGNORECASE).strip()
        if doi.startswith("10.") and "/" in doi and not any(character.isspace() for character in doi):
            return f"doi:{doi}"

        work_id_match = re.search(r"(?:^|/|openalex:)(W\d+)$", value.rstrip("/"), flags=re.IGNORECASE)
        if work_id_match:
            return work_id_match.group(1).upper()
        raise ValueError("query must contain a valid DOI or OpenAlex work ID in work mode")

    @classmethod
    def _parse_work(cls, work: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": cls._path_id(work.get("id")),
            "doi": cls._normalize_doi_value(work.get("doi")),
            "title": cls._string_value(work.get("title")) or cls._string_value(work.get("display_name")),
            "abstract": cls._reconstruct_abstract(work.get("abstract_inverted_index")),
            "publication_year": cls._integer_value(work.get("publication_year")),
            "publication_date": cls._string_value(work.get("publication_date")),
            "type": cls._string_value(work.get("type")),
            "authorships": cls._authorships(work.get("authorships")),
            "primary_location": cls._primary_location(work.get("primary_location")),
            "open_access": cls._open_access(work.get("open_access")),
            "cited_by_count": cls._integer_value(work.get("cited_by_count")),
            "referenced_works_count": cls._integer_value(work.get("referenced_works_count")),
            "topics": cls._topics(work.get("topics")),
            "keywords": cls._keywords(work.get("keywords")),
        }

    @classmethod
    def _authorships(cls, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        authorships = []
        for authorship in value:
            if not isinstance(authorship, dict):
                continue
            author = authorship.get("author") if isinstance(authorship.get("author"), dict) else {}
            authorships.append(
                {
                    "author_id": cls._path_id(author.get("id")),
                    "author_name": cls._string_value(author.get("display_name")),
                    "orcid": cls._path_id(author.get("orcid")),
                    "author_position": cls._string_value(authorship.get("author_position")),
                    "is_corresponding": cls._boolean_value(authorship.get("is_corresponding")),
                    "raw_author_name": cls._string_value(authorship.get("raw_author_name")),
                    "institutions": cls._institutions(authorship.get("institutions")),
                    "countries": cls._string_list(authorship.get("countries")),
                }
            )
        return authorships

    @classmethod
    def _institutions(cls, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        institutions = []
        for institution in value:
            if not isinstance(institution, dict):
                continue
            institutions.append(
                {
                    "id": cls._path_id(institution.get("id")),
                    "name": cls._string_value(institution.get("display_name")),
                    "ror": cls._path_id(institution.get("ror")),
                    "country_code": cls._string_value(institution.get("country_code")),
                    "type": cls._string_value(institution.get("type")),
                }
            )
        return institutions

    @classmethod
    def _primary_location(cls, value: Any) -> dict[str, Any]:
        location = value if isinstance(value, dict) else {}
        source = location.get("source") if isinstance(location.get("source"), dict) else {}
        return {
            "is_oa": cls._boolean_value(location.get("is_oa")),
            "landing_page_url": cls._string_value(location.get("landing_page_url")),
            "pdf_url": cls._string_value(location.get("pdf_url")),
            "license": cls._string_value(location.get("license")),
            "source": {
                "id": cls._path_id(source.get("id")),
                "name": cls._string_value(source.get("display_name")),
                "issn_l": cls._string_value(source.get("issn_l")),
                "issn": cls._string_list(source.get("issn")),
                "type": cls._string_value(source.get("type")),
                "is_oa": cls._boolean_value(source.get("is_oa")),
            },
        }

    @classmethod
    def _open_access(cls, value: Any) -> dict[str, Any]:
        open_access = value if isinstance(value, dict) else {}
        return {
            "is_oa": cls._boolean_value(open_access.get("is_oa")),
            "oa_status": cls._string_value(open_access.get("oa_status")),
            "oa_url": cls._string_value(open_access.get("oa_url")),
        }

    @classmethod
    def _topics(cls, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        topics = []
        for topic in value:
            if not isinstance(topic, dict):
                continue
            topics.append(
                {
                    "id": cls._path_id(topic.get("id")),
                    "name": cls._string_value(topic.get("display_name")),
                    "score": cls._number_value(topic.get("score")),
                    "subfield": cls._taxonomy(topic.get("subfield")),
                    "field": cls._taxonomy(topic.get("field")),
                    "domain": cls._taxonomy(topic.get("domain")),
                }
            )
        return topics

    @classmethod
    def _keywords(cls, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        keywords = []
        for keyword in value:
            if not isinstance(keyword, dict):
                continue
            keywords.append(
                {
                    "id": cls._path_id(keyword.get("id")),
                    "name": cls._string_value(keyword.get("display_name")),
                    "score": cls._number_value(keyword.get("score")),
                }
            )
        return keywords

    @classmethod
    def _taxonomy(cls, value: Any) -> dict[str, str]:
        taxonomy = value if isinstance(value, dict) else {}
        return {
            "id": cls._path_id(taxonomy.get("id")),
            "name": cls._string_value(taxonomy.get("display_name")),
        }

    @classmethod
    def _reconstruct_abstract(cls, value: Any) -> str:
        if not isinstance(value, dict):
            return ""

        # OpenAlex stores abstracts as a word-to-positions index. Build a
        # position-to-word map instead of a dense array so sparse or malformed
        # indexes cannot force a large allocation.
        words_by_position: dict[int, str] = {}
        for word, positions in value.items():
            if not isinstance(word, str) or not word or not isinstance(positions, list):
                continue
            for position in positions:
                if isinstance(position, int) and not isinstance(position, bool) and position >= 0:
                    words_by_position.setdefault(position, word)
        if not words_by_position:
            return ""
        return " ".join(words_by_position[position] for position in sorted(words_by_position))

    @classmethod
    def _normalize_doi_value(cls, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.IGNORECASE)

    @classmethod
    def _path_id(cls, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        return value.strip().rstrip("/").rsplit("/", 1)[-1]

    @staticmethod
    def _string_value(value: Any) -> str:
        return " ".join(value.split()) if isinstance(value, str) else ""

    @classmethod
    def _string_list(cls, value: Any) -> list[str]:
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
    def _number_value(value: Any) -> float:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return 0.0

    @staticmethod
    def _boolean_value(value: Any) -> bool:
        return value if isinstance(value, bool) else False

    @staticmethod
    def _error_result(context: dict[str, Any], error_type: str, message: str) -> dict[str, Any]:
        return {
            **context,
            "total_results": 0,
            "returned_results": 0,
            "next_cursor": "",
            "works": [],
            "error": {"type": error_type, "message": message},
        }
