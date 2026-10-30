#!/usr/bin/env python3
# Actionable validation messages are part of this tool's public contract.
# ruff: noqa: TRY003

"""A bounded technical Q&A research tool for the Stack Exchange API."""

import json
import math
import re
import time
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from typing import Any, ClassVar
from urllib.parse import urlparse

import requests
from pydantic import Field, PrivateAttr, SecretStr

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class _StackExchangeAPIError(Exception):
    """Raised when Stack Exchange returns an API-level error response."""


class _MarkupTextExtractor(HTMLParser):
    """Extract readable text from untrusted Stack Exchange HTML."""

    BLOCK_TAGS: ClassVar[set[str]] = {
        "blockquote",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "ol",
        "p",
        "pre",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }
    SKIP_TAGS: ClassVar[set[str]] = {"script", "style"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        normalized_tag = tag.lower()
        if normalized_tag in self.SKIP_TAGS:
            self.skip_depth += 1
        elif not self.skip_depth and normalized_tag in self.BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        if normalized_tag in self.SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif not self.skip_depth and normalized_tag in self.BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        """Return normalized plain text."""
        return " ".join("".join(self.parts).split())


class StackExchangeTool(Tool):
    """Search technical Q&A and return bounded question and answer excerpts."""

    SORT_OPTIONS: ClassVar[set[str]] = {"activity", "creation", "relevance", "votes"}
    ORDER_OPTIONS: ClassVar[set[str]] = {"asc", "desc"}
    MAX_QUERY_LENGTH: ClassVar[int] = 300
    MAX_SITE_LENGTH: ClassVar[int] = 64
    MAX_TAGS: ClassVar[int] = 5
    MAX_TAG_LENGTH: ClassVar[int] = 35
    MAX_PAGE: ClassVar[int] = 100
    MAX_PAGE_SIZE: ClassVar[int] = 8
    MAX_ANSWERS_PER_QUESTION: ClassVar[int] = 3
    MAX_ANSWER_FETCH: ClassVar[int] = 40
    MAX_TITLE_LENGTH: ClassVar[int] = 250
    MAX_QUESTION_EXCERPT_LENGTH: ClassVar[int] = 600
    MAX_ANSWER_EXCERPT_LENGTH: ClassVar[int] = 1000
    MAX_DISPLAY_NAME_LENGTH: ClassVar[int] = 100
    MAX_URL_LENGTH: ClassVar[int] = 500
    MAX_OUTPUT_BYTES: ClassVar[int] = 48 * 1024
    MAX_BACKOFF_SECONDS: ClassVar[int] = 24 * 60 * 60

    name: str = "stack_exchange_tool"
    description: str = (
        "Search Stack Exchange technical questions and return normalized question "
        "metadata with bounded accepted and top-voted answer excerpts."
    )
    base_url: str = "https://api.stackexchange.com/2.3"
    timeout: float = Field(default=15.0, gt=0, le=60, description="HTTP request timeout in seconds")
    api_key: SecretStr | None = Field(
        default_factory=lambda: get_from_env("STACKEXCHANGE_KEY"),
        exclude=True,
        repr=False,
    )
    access_token: SecretStr | None = Field(
        default_factory=lambda: get_from_env("STACKEXCHANGE_ACCESS_TOKEN"),
        exclude=True,
        repr=False,
    )
    user_agent: str = "agentUniverse-Stack-Exchange-Tool/1.0"

    _backoff_until: float = PrivateAttr(default=0.0)

    def execute(
        self,
        query: str,
        site: str = "stackoverflow",
        tags: str | list[str] | None = None,
        sort: str = "relevance",
        order: str = "desc",
        page: int = 1,
        page_size: int = 5,
        from_date: str | None = None,
        to_date: str | None = None,
        answers_per_question: int = 2,
    ) -> dict[str, Any]:
        """Search Stack Exchange for technical questions.

        Args:
            query: Search keywords.
            site: Stack Exchange API site parameter, such as ``stackoverflow``.
            tags: Up to five tags, provided as a list or comma/semicolon-delimited string.
            sort: One of relevance, activity, creation, or votes.
            order: Sort direction, either asc or desc.
            page: One-based result page, capped at 100.
            page_size: Questions per page, from 1 to 8.
            from_date: Optional inclusive lower date bound in YYYY-MM-DD format.
            to_date: Optional inclusive upper date bound in YYYY-MM-DD format.
            answers_per_question: Accepted/top-voted answers retained per question, from 1 to 3.

        Returns:
            A structured dictionary with normalized questions, answer excerpts,
            pagination, quota, and backoff metadata. Request failures use a
            structured ``error`` field.

        Raises:
            TypeError: If an input has the wrong type.
            ValueError: If an input value is invalid.
        """
        normalized_query = self._normalize_query(query)
        normalized_site = self._normalize_site(site)
        normalized_tags = self._normalize_tags(tags)
        normalized_sort = self._normalize_choice(sort, "sort", self.SORT_OPTIONS)
        normalized_order = self._normalize_choice(order, "order", self.ORDER_OPTIONS)
        self._validate_integer(page, "page", 1, self.MAX_PAGE)
        self._validate_integer(page_size, "page_size", 1, self.MAX_PAGE_SIZE)
        self._validate_integer(
            answers_per_question,
            "answers_per_question",
            1,
            self.MAX_ANSWERS_PER_QUESTION,
        )
        normalized_from_date = self._normalize_date(from_date, "from_date")
        normalized_to_date = self._normalize_date(to_date, "to_date")
        self._validate_date_range(normalized_from_date, normalized_to_date)
        self._credential_params()

        context = {
            "query": normalized_query,
            "site": normalized_site,
            "tags": normalized_tags,
            "sort": normalized_sort,
            "order": normalized_order,
            "page": page,
            "page_size": page_size,
            "from_date": normalized_from_date,
            "to_date": normalized_to_date,
            "answers_per_question": answers_per_question,
        }
        remaining_backoff = self._remaining_backoff()
        if remaining_backoff:
            return self._error_result(
                context=context,
                error_type="backoff_active",
                message=f"Stack Exchange requested backoff; retry after {remaining_backoff} seconds.",
                backoff_seconds=remaining_backoff,
            )

        api_state: dict[str, Any] = {
            "quota_remaining": None,
            "quota_max": None,
            "backoff_seconds": 0,
        }
        try:
            search_envelope = self._parse_envelope(
                self._request("/search/advanced", self._search_params(context)),
                label="question search",
                max_items=page_size,
            )
            self._record_api_state(api_state, search_envelope)
            questions = [self._parse_question(item) for item in search_envelope["items"]]
        except (_StackExchangeAPIError, requests.RequestException, KeyError, TypeError, ValueError) as exc:
            error = self._exception_error(exc)
            return self._error_result(
                context=context,
                error_type=error["type"],
                message=error["message"],
                quota_remaining=api_state["quota_remaining"],
                quota_max=api_state["quota_max"],
                backoff_seconds=api_state["backoff_seconds"],
            )

        answer_map: dict[int, dict[int, dict[str, Any]]] = {}
        answers_has_more = False
        answer_error: dict[str, str] | None = None
        if not questions or not any(question["answer_count"] for question in questions):
            answer_fetch_status = "not_needed"
        elif api_state["backoff_seconds"]:
            answer_fetch_status = "backoff"
        elif api_state["quota_remaining"] == 0:
            answer_fetch_status = "quota_exhausted"
        else:
            answer_map, answer_fetch_status, answers_has_more, answer_error = self._retrieve_answers(
                questions=questions,
                site=normalized_site,
                api_state=api_state,
            )

        self._attach_answers(questions, answer_map, answers_per_question)
        result: dict[str, Any] = {
            **context,
            "returned_results": len(questions),
            "has_more": search_envelope["has_more"],
            "quota_remaining": api_state["quota_remaining"],
            "quota_max": api_state["quota_max"],
            "backoff_seconds": api_state["backoff_seconds"],
            "answer_fetch_status": answer_fetch_status,
            "answers_has_more": answers_has_more,
            "questions": questions,
            "output_truncated": False,
        }
        if answer_error:
            result["answer_error"] = answer_error
        return self._enforce_output_limit(result)

    def _retrieve_answers(
        self,
        questions: list[dict[str, Any]],
        site: str,
        api_state: dict[str, Any],
    ) -> tuple[dict[int, dict[int, dict[str, Any]]], str, bool, dict[str, str] | None]:
        """Fetch accepted answers first, then a bounded top-voted answer page."""
        question_ids = [question["question_id"] for question in questions if question["answer_count"]]
        accepted_ids = [
            question["accepted_answer_id"] for question in questions if question["accepted_answer_id"] is not None
        ]
        answer_map: dict[int, dict[int, dict[str, Any]]] = {question_id: {} for question_id in question_ids}
        answers_has_more = False

        if accepted_ids:
            try:
                envelope = self._parse_envelope(
                    self._request(
                        f"/answers/{';'.join(str(answer_id) for answer_id in accepted_ids)}",
                        {
                            "site": site,
                            "filter": "withbody",
                            "pagesize": len(accepted_ids),
                        },
                    ),
                    label="accepted answers",
                    max_items=len(accepted_ids),
                )
                self._record_api_state(api_state, envelope)
                self._add_answers(answer_map, envelope["items"])
                answers_has_more = answers_has_more or envelope["has_more"]
            except (_StackExchangeAPIError, requests.RequestException, KeyError, TypeError, ValueError) as exc:
                return answer_map, "error", answers_has_more, self._exception_error(exc)

            if api_state["backoff_seconds"]:
                return answer_map, "backoff", answers_has_more, None
            if api_state["quota_remaining"] == 0:
                return answer_map, "quota_exhausted", answers_has_more, None

        total_answers = sum(question["answer_count"] for question in questions)
        top_page_size = min(self.MAX_ANSWER_FETCH, max(1, total_answers))
        try:
            envelope = self._parse_envelope(
                self._request(
                    f"/questions/{';'.join(str(question_id) for question_id in question_ids)}/answers",
                    {
                        "site": site,
                        "filter": "withbody",
                        "sort": "votes",
                        "order": "desc",
                        "pagesize": top_page_size,
                    },
                ),
                label="top answers",
                max_items=top_page_size,
            )
            self._record_api_state(api_state, envelope)
            self._add_answers(answer_map, envelope["items"])
            answers_has_more = answers_has_more or envelope["has_more"]
        except (_StackExchangeAPIError, requests.RequestException, KeyError, TypeError, ValueError) as exc:
            status = "partial" if any(answer_map.values()) else "error"
            return answer_map, status, answers_has_more, self._exception_error(exc)

        return answer_map, "partial" if answers_has_more else "complete", answers_has_more, None

    def _request(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        """Send one fixed-origin Stack Exchange API request."""
        request_params = {key: value for key, value in params.items() if value not in (None, "", [])}
        request_params.update(self._credential_params())
        response = requests.get(
            f"{self.base_url}{path}",
            params=request_params,
            headers={"Accept": "application/json", "User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        status_code = response.status_code
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            if status_code >= 400:
                response.raise_for_status()
            raise ValueError("invalid Stack Exchange JSON response") from exc

        if not isinstance(data, dict):
            raise TypeError("invalid Stack Exchange response")
        if self._is_api_error(data):
            raise _StackExchangeAPIError(self._api_error_message(data))
        if status_code >= 400:
            response.raise_for_status()
        return data

    def _parse_envelope(self, data: dict[str, Any], label: str, max_items: int) -> dict[str, Any]:
        """Validate a Stack Exchange response wrapper and record backoff state."""
        items = data.get("items")
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise ValueError(f"invalid {label} items")
        if len(items) > max_items:
            raise ValueError(f"{label} returned too many items")

        has_more = data.get("has_more")
        if not isinstance(has_more, bool):
            raise TypeError(f"invalid {label} has_more value")
        quota_remaining = self._required_nonnegative_integer(data.get("quota_remaining"), "quota_remaining")
        quota_max = self._optional_nonnegative_integer(data.get("quota_max"), "quota_max")
        backoff = self._optional_nonnegative_integer(data.get("backoff"), "backoff") or 0
        if backoff > self.MAX_BACKOFF_SECONDS:
            raise ValueError("invalid Stack Exchange backoff value")
        if backoff:
            self._backoff_until = max(self._backoff_until, time.monotonic() + backoff)

        return {
            "items": items,
            "has_more": has_more,
            "quota_remaining": quota_remaining,
            "quota_max": quota_max,
            "backoff": backoff,
        }

    def _search_params(self, context: dict[str, Any]) -> dict[str, Any]:
        params: dict[str, Any] = {
            "q": context["query"],
            "site": context["site"],
            "sort": context["sort"],
            "order": context["order"],
            "page": context["page"],
            "pagesize": context["page_size"],
            "filter": "withbody",
        }
        if context["tags"]:
            params["tagged"] = ";".join(context["tags"])
        if context["from_date"]:
            params["fromdate"] = self._date_timestamp(context["from_date"], upper=False)
        if context["to_date"]:
            params["todate"] = self._date_timestamp(context["to_date"], upper=True)
        return params

    def _credential_params(self) -> dict[str, str]:
        api_key = self._secret_value(self.api_key)
        access_token = self._secret_value(self.access_token)
        if access_token and not api_key:
            raise ValueError("STACKEXCHANGE_ACCESS_TOKEN requires STACKEXCHANGE_KEY")
        credentials = {}
        if api_key:
            credentials["key"] = api_key
        if access_token:
            credentials["access_token"] = access_token
        return credentials

    @classmethod
    def _parse_question(cls, item: dict[str, Any]) -> dict[str, Any]:
        accepted_answer_id = cls._optional_positive_integer(item.get("accepted_answer_id"))
        return {
            "question_id": cls._required_positive_integer(item.get("question_id"), "question_id"),
            "title": cls._clean_markup(item.get("title"), cls.MAX_TITLE_LENGTH),
            "link": cls._safe_url(item.get("link")),
            "tags": cls._response_tags(item.get("tags")),
            "score": cls._integer_value(item.get("score")),
            "view_count": cls._nonnegative_integer(item.get("view_count")),
            "answer_count": cls._nonnegative_integer(item.get("answer_count")),
            "is_answered": item.get("is_answered") is True,
            "accepted_answer_id": accepted_answer_id,
            "creation_date": cls._timestamp_text(item.get("creation_date")),
            "last_activity_date": cls._timestamp_text(item.get("last_activity_date")),
            "last_edit_date": cls._timestamp_text(item.get("last_edit_date")),
            "content_license": cls._bounded_plain_text(item.get("content_license"), 80),
            "owner": cls._parse_owner(item.get("owner")),
            "body_excerpt": cls._clean_markup(item.get("body"), cls.MAX_QUESTION_EXCERPT_LENGTH),
            "answers": [],
        }

    @classmethod
    def _parse_answer(cls, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "answer_id": cls._required_positive_integer(item.get("answer_id"), "answer_id"),
            "question_id": cls._required_positive_integer(item.get("question_id"), "question_id"),
            "is_accepted": item.get("is_accepted") is True,
            "score": cls._integer_value(item.get("score")),
            "link": cls._safe_url(item.get("link")),
            "creation_date": cls._timestamp_text(item.get("creation_date")),
            "last_activity_date": cls._timestamp_text(item.get("last_activity_date")),
            "last_edit_date": cls._timestamp_text(item.get("last_edit_date")),
            "content_license": cls._bounded_plain_text(item.get("content_license"), 80),
            "owner": cls._parse_owner(item.get("owner")),
            "body_excerpt": cls._clean_markup(item.get("body"), cls.MAX_ANSWER_EXCERPT_LENGTH),
        }

    @classmethod
    def _parse_owner(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}
        owner = {
            "user_id": cls._optional_positive_integer(value.get("user_id")),
            "display_name": cls._clean_markup(value.get("display_name"), cls.MAX_DISPLAY_NAME_LENGTH),
            "reputation": cls._nonnegative_integer(value.get("reputation")),
            "link": cls._safe_url(value.get("link")),
        }
        return {key: item for key, item in owner.items() if item not in (None, "", 0)}

    @classmethod
    def _add_answers(
        cls,
        answer_map: dict[int, dict[int, dict[str, Any]]],
        items: list[dict[str, Any]],
    ) -> None:
        for item in items:
            answer = cls._parse_answer(item)
            question_answers = answer_map.get(answer["question_id"])
            if question_answers is not None:
                question_answers[answer["answer_id"]] = answer

    @staticmethod
    def _attach_answers(
        questions: list[dict[str, Any]],
        answer_map: dict[int, dict[int, dict[str, Any]]],
        answer_limit: int,
    ) -> None:
        for question in questions:
            accepted_answer_id = question["accepted_answer_id"]
            answers = list(answer_map.get(question["question_id"], {}).values())
            for answer in answers:
                if answer["answer_id"] == accepted_answer_id:
                    answer["is_accepted"] = True
            answers.sort(
                key=lambda answer: (
                    not answer["is_accepted"],
                    -answer["score"],
                    answer["answer_id"],
                )
            )
            question["answers"] = answers[:answer_limit]

    @staticmethod
    def _record_api_state(state: dict[str, Any], envelope: dict[str, Any]) -> None:
        quota_remaining = envelope["quota_remaining"]
        if state["quota_remaining"] is None:
            state["quota_remaining"] = quota_remaining
        else:
            state["quota_remaining"] = min(state["quota_remaining"], quota_remaining)
        if state["quota_max"] is None and envelope["quota_max"] is not None:
            state["quota_max"] = envelope["quota_max"]
        state["backoff_seconds"] = max(state["backoff_seconds"], envelope["backoff"])

    def _remaining_backoff(self) -> int:
        return max(0, math.ceil(self._backoff_until - time.monotonic()))

    @classmethod
    def _normalize_query(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("query must be a string")
        query = cls._bounded_plain_text(value, cls.MAX_QUERY_LENGTH + 1)
        if not query:
            raise ValueError("query must not be empty")
        if len(query) > cls.MAX_QUERY_LENGTH:
            raise ValueError(f"query must not exceed {cls.MAX_QUERY_LENGTH} characters")
        return query

    @classmethod
    def _normalize_site(cls, value: Any) -> str:
        site = value.strip().lower() if isinstance(value, str) else ""
        if not site:
            raise ValueError("site must not be empty")
        if len(site) > cls.MAX_SITE_LENGTH:
            raise ValueError(f"site must not exceed {cls.MAX_SITE_LENGTH} characters")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", site) or ".." in site or ".-" in site or "-." in site:
            raise ValueError("site must be a valid Stack Exchange API site parameter")
        return site

    @classmethod
    def _normalize_tags(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            raw_tags = re.split(r"[,;]", value)
        elif isinstance(value, list) and all(isinstance(tag, str) for tag in value):
            raw_tags = value
        else:
            raise ValueError("tags must be a string or list of strings")

        tags = []
        for raw_tag in raw_tags:
            tag = raw_tag.strip().lower()
            if not tag:
                raise ValueError("tags must not contain empty values")
            if len(tag) > cls.MAX_TAG_LENGTH:
                raise ValueError(f"each tag must not exceed {cls.MAX_TAG_LENGTH} characters")
            if not re.fullmatch(r"[a-z0-9.+#-]+", tag):
                raise ValueError("tags may contain only letters, numbers, dot, plus, hash, and hyphen")
            if tag not in tags:
                tags.append(tag)
        if len(tags) > cls.MAX_TAGS:
            raise ValueError(f"tags must contain at most {cls.MAX_TAGS} unique values")
        return tags

    @staticmethod
    def _normalize_choice(value: Any, parameter_name: str, allowed: set[str]) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if normalized not in allowed:
            raise ValueError(f"{parameter_name} must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @staticmethod
    def _validate_integer(value: Any, parameter_name: str, minimum: int, maximum: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
            raise ValueError(f"{parameter_name} must be an integer between {minimum} and {maximum}")

    @staticmethod
    def _normalize_date(value: Any, parameter_name: str) -> str:
        if value is None or value == "":
            return ""
        normalized = value.strip() if isinstance(value, str) else ""
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
            raise ValueError(f"{parameter_name} must use YYYY-MM-DD format")
        try:
            date.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"{parameter_name} must be a valid date") from exc
        return normalized

    @staticmethod
    def _validate_date_range(from_date: str, to_date: str) -> None:
        if from_date and to_date and date.fromisoformat(from_date) > date.fromisoformat(to_date):
            raise ValueError("from_date must not be later than to_date")

    @staticmethod
    def _date_timestamp(value: str, upper: bool) -> int:
        parsed = date.fromisoformat(value)
        hour, minute, second = (23, 59, 59) if upper else (0, 0, 0)
        return int(
            datetime(
                parsed.year,
                parsed.month,
                parsed.day,
                hour,
                minute,
                second,
                tzinfo=timezone.utc,
            ).timestamp()
        )

    @classmethod
    def _clean_markup(cls, value: Any, limit: int) -> str:
        if not isinstance(value, str) or not value.strip():
            return ""
        parser = _MarkupTextExtractor()
        parser.feed(value)
        parser.close()
        return cls._truncate(parser.text(), limit)

    @classmethod
    def _bounded_plain_text(cls, value: Any, limit: int) -> str:
        if not isinstance(value, str):
            return ""
        sanitized = "".join(
            " " if character.isspace() else character
            for character in value
            if character.isspace() or (ord(character) >= 32 and ord(character) != 127)
        )
        return cls._truncate(" ".join(sanitized.split()), limit)

    @staticmethod
    def _truncate(value: str, limit: int) -> str:
        if len(value) <= limit:
            return value
        return value[: max(0, limit - 1)].rstrip() + "…"

    @classmethod
    def _safe_url(cls, value: Any) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > cls.MAX_URL_LENGTH:
            return ""
        url = value.strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            return ""
        return url

    @classmethod
    def _response_tags(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        tags = []
        for item in value:
            tag = cls._bounded_plain_text(item, cls.MAX_TAG_LENGTH)
            if tag and tag not in tags:
                tags.append(tag)
            if len(tags) == cls.MAX_TAGS:
                break
        return tags

    @staticmethod
    def _timestamp_text(value: Any) -> str:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return ""
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        except (OSError, OverflowError, ValueError):
            return ""

    @staticmethod
    def _integer_value(value: Any) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) else 0

    @staticmethod
    def _nonnegative_integer(value: Any) -> int:
        return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0

    @staticmethod
    def _required_positive_integer(value: Any, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"invalid {field_name}")
        return value

    @staticmethod
    def _optional_positive_integer(value: Any) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            return None
        return value

    @staticmethod
    def _required_nonnegative_integer(value: Any, field_name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"invalid {field_name}")
        return value

    @classmethod
    def _optional_nonnegative_integer(cls, value: Any, field_name: str) -> int | None:
        if value is None:
            return None
        return cls._required_nonnegative_integer(value, field_name)

    @staticmethod
    def _is_api_error(data: dict[str, Any]) -> bool:
        return any(key in data for key in ("error_id", "error_name", "error_message"))

    def _api_error_message(self, data: dict[str, Any]) -> str:
        error_id = data.get("error_id")
        error_name = self._bounded_plain_text(data.get("error_name"), 80)
        error_message = self._bounded_plain_text(data.get("error_message"), 300)
        parts = []
        if isinstance(error_id, int) and not isinstance(error_id, bool):
            parts.append(str(error_id))
        if error_name:
            parts.append(error_name)
        if error_message:
            parts.append(error_message)
        message = "Stack Exchange API error" + (": " + " - ".join(parts) if parts else ".")
        for secret in (self._secret_value(self.api_key), self._secret_value(self.access_token)):
            if secret:
                message = message.replace(secret, "[redacted]")
        return message

    @staticmethod
    def _secret_value(value: Any) -> str:
        if isinstance(value, SecretStr):
            return value.get_secret_value()
        return value if isinstance(value, str) else ""

    @staticmethod
    def _exception_error(exc: Exception) -> dict[str, str]:
        if isinstance(exc, _StackExchangeAPIError):
            return {"type": "api_error", "message": str(exc)}
        if isinstance(exc, requests.Timeout):
            return {"type": "request_timeout", "message": "Stack Exchange request timed out."}
        if isinstance(exc, requests.HTTPError):
            status_code = exc.response.status_code if exc.response is not None else None
            if status_code == 429:
                message = "Stack Exchange returned HTTP status 429 (rate limited)."
            elif status_code:
                message = f"Stack Exchange returned HTTP status {status_code}."
            else:
                message = "Stack Exchange HTTP request failed."
            return {"type": "http_error", "message": message}
        if isinstance(exc, requests.RequestException):
            return {"type": "request_error", "message": "Stack Exchange request failed."}
        return {
            "type": "invalid_response",
            "message": f"Unable to parse Stack Exchange response: {exc}",
        }

    @staticmethod
    def _error_result(
        context: dict[str, Any],
        error_type: str,
        message: str,
        quota_remaining: int | None = None,
        quota_max: int | None = None,
        backoff_seconds: int = 0,
    ) -> dict[str, Any]:
        return {
            **context,
            "returned_results": 0,
            "has_more": False,
            "quota_remaining": quota_remaining,
            "quota_max": quota_max,
            "backoff_seconds": backoff_seconds,
            "answer_fetch_status": "not_started",
            "answers_has_more": False,
            "questions": [],
            "output_truncated": False,
            "error": {"type": error_type, "message": message},
        }

    @classmethod
    def _enforce_output_limit(cls, result: dict[str, Any]) -> dict[str, Any]:
        if cls._serialized_size(result) <= cls.MAX_OUTPUT_BYTES:
            return result

        result["output_truncated"] = True
        for question in reversed(result["questions"]):
            question["body_excerpt"] = cls._truncate(question["body_excerpt"], 160)
            for answer in question["answers"]:
                answer["body_excerpt"] = cls._truncate(answer["body_excerpt"], 240)
        while cls._serialized_size(result) > cls.MAX_OUTPUT_BYTES and result["questions"]:
            result["questions"].pop()
        result["returned_results"] = len(result["questions"])
        return result

    @staticmethod
    def _serialized_size(value: dict[str, Any]) -> int:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
