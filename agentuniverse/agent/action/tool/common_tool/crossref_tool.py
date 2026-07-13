#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""A lightweight scholarly metadata tool based on the Crossref REST API."""

import re
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

    base_url: str = "https://api.crossref.org/v1"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    email: Optional[str] = Field(default_factory=lambda: get_from_env("CROSSREF_EMAIL"))
    user_agent: str = "agentUniverse-Crossref-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "search",
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Search scholarly works or retrieve metadata for a Crossref DOI.

        Args:
            query: Search keywords in search mode, or a DOI/DOI URL in doi mode.
            mode: Operation mode. Supports search and doi.
            max_results: Maximum search results to return, from 1 to 20.

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
            effective_max_results = max_results
        else:
            normalized_query = self._normalize_doi(normalized_query)
            effective_max_results = 1

        try:
            if normalized_mode == "search":
                total_results, raw_works = self._search(normalized_query, effective_max_results)
            else:
                raw_works = [self._lookup_doi(normalized_query)]
                total_results = 1

            works = [self._parse_work(work) for work in raw_works]
            return {
                "mode": normalized_mode,
                "query": normalized_query,
                "max_results": effective_max_results,
                "total_results": total_results,
                "returned_results": len(works),
                "works": works,
            }
        except _CrossrefAPIError as exc:
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
                message="Crossref request timed out.",
            )
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            message = (
                f"Crossref returned HTTP status {status_code}." if status_code else "Crossref HTTP request failed."
            )
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
                message=f"Crossref request failed: {exc}",
            )
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                mode=normalized_mode,
                query=normalized_query,
                max_results=effective_max_results,
                error_type="invalid_response",
                message=f"Unable to parse Crossref response: {exc}",
            )

    def _search(self, query: str, max_results: int) -> tuple[int, List[Dict[str, Any]]]:
        data = self._request(
            "/works",
            params={"query.bibliographic": query, "rows": max_results},
        )
        if data.get("message-type") != "work-list":
            raise ValueError("unexpected message-type for Crossref search")

        message = data.get("message")
        if not isinstance(message, dict):
            raise ValueError("missing search message")
        items = message.get("items")
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise ValueError("invalid search items")
        return int(message.get("total-results", 0)), items

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
            "authors": cls._authors(work.get("author")),
            "abstract": cls._markup_text(work.get("abstract")),
            "container_title": cls._first_text(work.get("container-title")),
            "published": cls._published_date(work.get("published")),
            "publisher": cls._string_value(work.get("publisher")),
            "type": cls._string_value(work.get("type")),
            "url": url,
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
        error_type: str,
        message: str,
    ) -> Dict[str, Any]:
        return {
            "mode": mode,
            "query": query,
            "max_results": max_results,
            "total_results": 0,
            "returned_results": 0,
            "works": [],
            "error": {"type": error_type, "message": message},
        }
