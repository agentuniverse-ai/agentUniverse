#!/usr/bin/env python3
# ruff: noqa: TRY003, TRY004

"""Researcher identity and scholarly works lookup through the ORCID API."""

import re
from typing import Any, ClassVar

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class OrcidTool(Tool):
    """Search ORCID researchers and retrieve public profiles or works."""

    MODES: ClassVar[set[str]] = {"search", "person", "works"}
    MAX_OFFSET: ClassVar[int] = 9999
    ORCID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^(\d{4})-(\d{4})-(\d{4})-(\d{3}[\dX])$", re.IGNORECASE
    )

    base_url: str = "https://pub.orcid.org/v3.0"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    access_token: str | None = Field(default_factory=lambda: get_from_env("ORCID_ACCESS_TOKEN"))
    user_agent: str = "agentUniverse-ORCID-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
        page: int = 1,
    ) -> dict[str, Any]:
        """Search researchers or retrieve an ORCID record's person/works data.

        Args:
            query: Search expression in search mode, or an ORCID iD/URL in
                person and works modes.
            mode: Operation mode: search, person, or works.
            max_results: Number of results to return, from 1 to 20.
            page: One-based page number.

        Returns:
            Structured researcher or work metadata. Network and invalid API
            responses are returned in an ``error`` field.

        Raises:
            ValueError: If an input is empty, unsupported, or out of bounds.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")
        self._validate_pagination(max_results, page)

        if normalized_mode != "search":
            normalized_query = self._normalize_orcid(normalized_query)
        if normalized_mode == "person":
            max_results = 1
            page = 1
        offset = (page - 1) * max_results
        context = {
            "mode": normalized_mode,
            "query": normalized_query,
            "max_results": max_results,
            "page": page,
            "offset": offset,
        }

        try:
            return self._execute_mode(context)
        except requests.Timeout:
            return self._error_result(**context, error_type="request_timeout", message="ORCID request timed out.")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            message = f"ORCID returned HTTP status {status}." if status else "ORCID HTTP request failed."
            return self._error_result(**context, error_type="http_error", message=message)
        except requests.RequestException:
            return self._error_result(**context, error_type="request_error", message="ORCID request failed.")
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context,
                error_type="invalid_response",
                message=f"Unable to parse ORCID response: {exc}",
            )

    def _execute_mode(self, context: dict[str, Any]) -> dict[str, Any]:
        mode = context["mode"]
        if mode == "search":
            return self._execute_search(context)
        if mode == "person":
            return self._execute_person(context)
        return self._execute_works(context)

    def _execute_search(self, context: dict[str, Any]) -> dict[str, Any]:
        data = self._get_json(
            "/expanded-search/",
            params={
                "q": context["query"],
                "start": context["offset"],
                "rows": context["max_results"],
            },
        )
        raw_results = data.get("expanded-result", [])
        if not isinstance(raw_results, list):
            raise ValueError("invalid expanded search results")
        researchers = [self._parse_search_result(item) for item in raw_results]
        return {
            **context,
            "total_results": self._as_int(data.get("num-found")),
            "returned_results": len(researchers),
            "researchers": researchers,
            "works": [],
        }

    def _execute_person(self, context: dict[str, Any]) -> dict[str, Any]:
        orcid = context["query"]
        profile = self._parse_person(orcid, self._get_json(f"/{orcid}/person"))
        return {
            **context,
            "total_results": 1,
            "returned_results": 1,
            "researchers": [profile],
            "works": [],
        }

    def _execute_works(self, context: dict[str, Any]) -> dict[str, Any]:
        orcid = context["query"]
        data = self._get_json(f"/{orcid}/works")
        groups = data.get("group", [])
        if not isinstance(groups, list):
            raise ValueError("invalid works groups")
        works = [self._parse_work(group, orcid) for group in groups]
        offset = context["offset"]
        page_works = works[offset:offset + context["max_results"]]
        return {
            **context,
            "total_results": len(works),
            "returned_results": len(page_works),
            "pagination": "local",
            "api_fetched_results": len(groups),
            "researchers": [],
            "works": page_works,
        }

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = requests.get(
            f"{self.base_url}{path}",
            params=params,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid ORCID JSON response") from exc
        if not isinstance(data, dict):
            raise ValueError("invalid ORCID response")
        return data

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    @classmethod
    def _normalize_mode(cls, mode: str) -> str:
        normalized = mode.strip().lower() if isinstance(mode, str) else ""
        if normalized not in cls.MODES:
            raise ValueError(f"mode must be one of: {', '.join(sorted(cls.MODES))}")
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

    @classmethod
    def _normalize_orcid(cls, value: str) -> str:
        normalized = re.sub(
            r"^https?://(?:www\.)?orcid\.org/", "", value.strip(), flags=re.IGNORECASE
        ).upper().rstrip("/")
        match = cls.ORCID_PATTERN.fullmatch(normalized)
        if match is None or not cls._valid_checksum(normalized):
            raise ValueError("query must contain a valid ORCID iD")
        return normalized

    @staticmethod
    def _valid_checksum(orcid: str) -> bool:
        total = 0
        for character in orcid.replace("-", "")[:-1]:
            total = (total + int(character)) * 2
        remainder = (12 - total % 11) % 11
        expected = "X" if remainder == 10 else str(remainder)
        return orcid[-1].upper() == expected

    @classmethod
    def _parse_search_result(cls, result: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ValueError("invalid expanded search result")
        orcid = cls._string(result.get("orcid-id"))
        return {
            "orcid": orcid,
            "given_names": cls._string(result.get("given-names")),
            "family_name": cls._string(result.get("family-names")),
            "credit_name": cls._string(result.get("credit-name")),
            "other_names": cls._string_list(result.get("other-name")),
            "emails": cls._string_list(result.get("email")),
            "current_institutions": cls._string_list(result.get("institution-name")),
            "past_institutions": cls._string_list(result.get("past-institution-name")),
            "profile_url": f"https://orcid.org/{orcid}" if orcid else "",
        }

    @classmethod
    def _parse_person(cls, orcid: str, person: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(person, dict):
            raise ValueError("invalid person record")
        name = cls._optional_dict(person, "name")
        biography = cls._optional_dict(person, "biography")
        return {
            "orcid": orcid,
            "given_names": cls._value(name.get("given-names")),
            "family_name": cls._value(name.get("family-name")),
            "credit_name": cls._value(name.get("credit-name")),
            "other_names": [
                cls._string(item.get("content"))
                for item in cls._items(person, "other-names", "other-name")
                if cls._string(item.get("content"))
            ],
            "biography": cls._string(biography.get("content")),
            "keywords": [
                cls._string(item.get("content"))
                for item in cls._items(person, "keywords", "keyword")
                if cls._string(item.get("content"))
            ],
            "countries": [
                cls._value(item.get("country"))
                for item in cls._items(person, "addresses", "address")
                if cls._value(item.get("country"))
            ],
            "researcher_urls": [
                {
                    "name": cls._value(item.get("url-name")),
                    "url": cls._value(item.get("url")),
                }
                for item in cls._items(person, "researcher-urls", "researcher-url")
            ],
            "external_identifiers": [
                {
                    "type": cls._string(item.get("external-id-type")),
                    "value": cls._string(item.get("external-id-value")),
                    "url": cls._value(item.get("external-id-url")),
                }
                for item in cls._items(person, "external-identifiers", "external-identifier")
            ],
            "profile_url": f"https://orcid.org/{orcid}",
        }

    @classmethod
    def _parse_work(cls, group: dict[str, Any], orcid: str) -> dict[str, Any]:
        if not isinstance(group, dict):
            raise ValueError("invalid work group")
        summaries = group.get("work-summary") or []
        if not isinstance(summaries, list) or not summaries or not isinstance(summaries[0], dict):
            raise ValueError("work group is missing a summary")
        summary = summaries[0]
        title = cls._optional_dict(summary, "title")
        source = cls._optional_dict(summary, "source")
        put_code = summary.get("put-code")
        return {
            "orcid": orcid,
            "put_code": put_code,
            "title": cls._value(title.get("title")),
            "subtitle": cls._value(title.get("subtitle")),
            "translated_title": cls._value(title.get("translated-title")),
            "journal_title": cls._value(summary.get("journal-title")),
            "type": cls._string(summary.get("type")),
            "publication_date": cls._publication_date(summary.get("publication-date")),
            "external_ids": cls._external_ids(group.get("external-ids")),
            "url": cls._value(summary.get("url")),
            "visibility": cls._string(summary.get("visibility")),
            "source": cls._value(source.get("source-name")),
            "record_url": f"https://orcid.org/{orcid}" + (f"/work/{put_code}" if put_code is not None else ""),
        }

    @classmethod
    def _external_ids(cls, container: Any) -> list[dict[str, str]]:
        items = container.get("external-id", []) if isinstance(container, dict) else []
        if not isinstance(items, list):
            return []
        return [
            {
                "type": cls._string(item.get("external-id-type")),
                "value": cls._string(item.get("external-id-value")),
                "url": cls._value(item.get("external-id-url")),
                "relationship": cls._string(item.get("external-id-relationship")),
            }
            for item in items
            if isinstance(item, dict)
        ]

    @classmethod
    def _publication_date(cls, value: Any) -> str:
        if not isinstance(value, dict):
            return ""
        parts = [cls._value(value.get(key)) for key in ("year", "month", "day")]
        return "-".join(part for part in parts if part)

    @staticmethod
    def _items(container: dict[str, Any], group: str, item: str) -> list[dict[str, Any]]:
        parent = container.get(group) or {}
        values = parent.get(item, []) if isinstance(parent, dict) else []
        return [value for value in values if isinstance(value, dict)] if isinstance(values, list) else []

    @staticmethod
    def _optional_dict(container: dict[str, Any], key: str) -> dict[str, Any]:
        value = container.get(key)
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError(f"invalid {key} object")
        return value

    @classmethod
    def _value(cls, value: Any) -> str:
        return cls._string(value.get("value")) if isinstance(value, dict) else ""

    @staticmethod
    def _string(value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _string_list(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in (cls._string(item) for item in value) if item]

    @staticmethod
    def _as_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _error_result(
        mode: str,
        query: str,
        max_results: int,
        page: int,
        offset: int,
        error_type: str,
        message: str,
    ) -> dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "page": page,
            "offset": offset,
            "total_results": 0,
            "returned_results": 0,
            "researchers": [],
            "works": [],
            "error": {"type": error_type, "message": message},
        }
