#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: youtube_tool.py

"""YouTube Data API v3 tool.

Searches YouTube videos by keyword and fetches video details /
statistics, addressing the *YouTube* item of issue #252 (tool plug-in
integration).

The tool talks to the public YouTube Data API v3 over ``httpx`` (already a
core agentUniverse dependency — no extra install is required) and supports
two operating modes:

* ``search`` — keyword video search via ``search.list``.
* ``videos`` — details and statistics for one or more video IDs via
  ``videos.list``.

The API key is read from the ``YOUTUBE_API_KEY`` environment variable and is
kept in a pydantic ``SecretStr`` so it is never echoed in results, errors, or
repr output. All inputs are validated strictly before any network request is
made. Each execution issues exactly one request; network, HTTP, rate-limit,
and malformed-response failures are returned as a structured ``error``
payload instead of raising, and every user-visible string is redacted against
the raw key value as a defense in depth.
"""

import re
from typing import Any, ClassVar, Dict, List, Optional, Union

import httpx
from pydantic import ConfigDict, Field, SecretStr

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env

_SOURCE = "YouTube Data API v3 (https://developers.google.com/youtube/v3)"


def _env_secret(env_key: str) -> Optional[SecretStr]:
    """Read an environment variable into a ``SecretStr`` (None when unset)."""
    value = get_from_env(env_key)
    return SecretStr(value) if value else None


class YouTubeTool(Tool):
    """YouTube Data API v3 tool.

    Attributes:
        api_key (Optional[SecretStr]): YouTube Data API key, read from the
            ``YOUTUBE_API_KEY`` environment variable. Held as a
            ``SecretStr`` so the key never leaks into logs or results.
        timeout (float): HTTP request timeout in seconds.
        transport (Optional[httpx.BaseTransport]): Injectable httpx
            transport; used by tests to run fully offline. Production use
            leaves it unset (the default httpx transport is used).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "youtube_tool"
    description: str = (
        "YouTube Data API v3 tool. Searches YouTube videos by keyword "
        "(mode='search') and fetches video details and statistics such as "
        "views, likes, comments and duration for one or more video IDs "
        "(mode='videos'). Requires the YOUTUBE_API_KEY environment variable."
    )

    # Fixed, https-only API endpoint; requests never go anywhere else.
    BASE_URL: ClassVar[str] = "https://www.googleapis.com/youtube/v3"
    SOURCE: ClassVar[str] = _SOURCE
    WATCH_URL: ClassVar[str] = "https://www.youtube.com/watch?v="
    VIDEO_ID_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[A-Za-z0-9_-]{11}$")
    DURATION_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?"
    )

    MODES: ClassVar[tuple] = ("search", "videos")
    DEFAULT_MAX_RESULTS: ClassVar[int] = 5
    MAX_RESULTS_LIMIT: ClassVar[int] = 25          # API allows 50; bound tighter
    MAX_VIDEO_IDS: ClassVar[int] = 10              # API allows 50; bound tighter
    MAX_QUERY_CHARS: ClassVar[int] = 300
    MAX_DESCRIPTION_CHARS: ClassVar[int] = 1000
    MAX_TAGS: ClassVar[int] = 10
    MAX_ERROR_CHARS: ClassVar[int] = 500

    api_key: Optional[SecretStr] = Field(
        default_factory=lambda: _env_secret("YOUTUBE_API_KEY")
    )
    timeout: float = Field(
        default=10.0, gt=0, le=120, description="HTTP request timeout in seconds"
    )
    transport: Optional[httpx.BaseTransport] = Field(
        default=None,
        exclude=True,
        repr=False,
        description="Injectable httpx transport for offline testing.",
    )

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        query: Optional[str] = None,
        video_id: Optional[Union[str, List[str]]] = None,
        max_results: int = DEFAULT_MAX_RESULTS,
    ) -> Dict[str, Any]:
        """Run a YouTube Data API v3 query.

        Args:
            mode (str): One of ``search`` / ``videos``.
            query (str): Search keywords (required in ``search`` mode,
                ignored in ``videos`` mode).
            video_id (str | List[str]): One video ID, or a comma-separated
                string / list of up to 10 IDs (required in ``videos`` mode,
                ignored in ``search`` mode). Each ID is exactly 11
                characters from ``A-Z a-z 0-9 _ -``.
            max_results (int): Number of results in ``search`` mode, from 1
                to 25. Ignored in ``videos`` mode.

        Returns:
            Dict[str, Any]: Normalized result with a ``videos`` list, or a
            structured ``error`` payload on network / HTTP / response
            failures.

        Raises:
            ValueError: If any input is invalid (raised before any network
                request is made) or the API key is missing.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )

        params: Dict[str, Any]
        if mode == "search":
            normalized_query = self._normalize_query(query)
            bounded_max_results = self._validate_max_results(max_results)
            self._require_api_key()
            context = {
                "mode": "search",
                "query": normalized_query,
                "max_results": bounded_max_results,
            }
            params = {
                "part": "snippet",
                "q": normalized_query,
                "type": "video",
                "maxResults": bounded_max_results,
            }
            path = "/search"
        else:
            video_ids = self._normalize_video_ids(video_id)
            self._require_api_key()
            context = {
                "mode": "videos",
                "video_ids": video_ids,
            }
            params = {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
            }
            path = "/videos"

        try:
            data = self._request(path, params)
            if mode == "search":
                return self._parse_search(data, context)
            return self._parse_videos(data, context)
        except httpx.TimeoutException:
            return self._error_result(
                context,
                error_type="request_timeout",
                message="YouTube request timed out.",
            )
        except httpx.HTTPStatusError as exc:
            return self._http_error_result(context, exc.response)
        except httpx.RequestError:
            return self._error_result(
                context,
                error_type="request_error",
                message="YouTube request failed.",
            )
        except ValueError as exc:
            return self._error_result(
                context,
                error_type="invalid_response",
                message=f"Unable to parse YouTube response: {exc}",
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — runs strictly before any request)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"youtube_tool: {message}")

    @classmethod
    def _normalize_query(cls, query: Optional[str]) -> str:
        """Validate and normalize the ``search`` mode query string."""
        if query is None or not isinstance(query, str) or not query.strip():
            cls._invalid("query is required in search mode and must be a non-empty string")
        normalized = " ".join(query.split())
        if len(normalized) > cls.MAX_QUERY_CHARS:
            cls._invalid(
                f"query must be at most {cls.MAX_QUERY_CHARS} characters (got {len(normalized)})"
            )
        return normalized

    @classmethod
    def _validate_max_results(cls, max_results: Any) -> int:
        """Validate the ``search`` mode result-count bound."""
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            cls._invalid(f"max_results must be an integer (got {max_results!r})")
        if not 1 <= max_results <= cls.MAX_RESULTS_LIMIT:
            cls._invalid(
                f"max_results must be between 1 and {cls.MAX_RESULTS_LIMIT} (got {max_results})"
            )
        return max_results

    @classmethod
    def _normalize_video_ids(cls, video_id: Any) -> List[str]:
        """Validate and normalize the ``videos`` mode ID input.

        Accepts a single ID, a comma-separated string, or a list; returns
        the de-duplicated ordered list of valid IDs.
        """
        if video_id is None:
            cls._invalid(
                "video_id is required in videos mode: one video ID (11 characters) "
                f"or a comma-separated list of up to {cls.MAX_VIDEO_IDS} IDs"
            )
        if isinstance(video_id, str):
            raw_ids = [part.strip() for part in video_id.split(",")]
        elif isinstance(video_id, (list, tuple)):
            raw_ids = [str(part).strip() for part in video_id]
        else:
            cls._invalid(
                f"video_id must be a string or a list of strings (got {video_id!r})"
            )
        if not any(raw_ids):
            cls._invalid(
                "video_id is required in videos mode: one video ID (11 characters) "
                f"or a comma-separated list of up to {cls.MAX_VIDEO_IDS} IDs"
            )
        seen = set()
        video_ids: List[str] = []
        for raw in raw_ids:
            if not raw:
                continue
            if not cls.VIDEO_ID_PATTERN.fullmatch(raw):
                cls._invalid(
                    f"invalid YouTube video ID {raw!r}: must be exactly 11 "
                    "characters from letters, digits, '_' or '-'"
                )
            if raw not in seen:
                seen.add(raw)
                video_ids.append(raw)
        if len(video_ids) > cls.MAX_VIDEO_IDS:
            cls._invalid(
                f"too many video IDs: {len(video_ids)} (max {cls.MAX_VIDEO_IDS})"
            )
        return video_ids

    def _require_api_key(self) -> str:
        """Return the raw API key, raising a helpful error when missing."""
        if self.api_key is None:
            self._invalid(
                "YouTube API key is missing. Set the YOUTUBE_API_KEY environment "
                "variable (create a key at "
                "https://console.cloud.google.com/apis/credentials) before "
                "using this tool."
            )
        return self.api_key.get_secret_value()

    # ------------------------------------------------------------------ #
    # HTTP (single request per execution, https-only fixed base URL)
    # ------------------------------------------------------------------ #

    def _request(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Issue one GET request to the YouTube Data API and return its JSON."""
        request_params = dict(params)
        request_params["key"] = self._require_api_key()
        headers = {
            "Accept": "application/json",
            "User-Agent": "agentUniverse-YouTubeTool/1.0",
        }
        with httpx.Client(
            base_url=self.BASE_URL,
            timeout=self.timeout,
            transport=self.transport,
            headers=headers,
        ) as client:
            response = client.get(path, params=request_params)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            raise ValueError("response body is not valid JSON") from None
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    # ------------------------------------------------------------------ #
    # Response parsing (pure — fully testable without a network)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_search(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize a ``search.list`` response."""
        items = cls._safe_list(data.get("items"), "items")
        videos = []
        for item in items:
            if not isinstance(item, dict):
                continue
            video_id = cls._safe_dict(item.get("id")).get("videoId")
            snippet = cls._safe_dict(item.get("snippet"))
            if not isinstance(video_id, str) or not video_id or not snippet:
                continue
            videos.append({
                "video_id": video_id,
                "title": cls._safe_str(snippet.get("title")),
                "channel_title": cls._safe_str(snippet.get("channelTitle")),
                "channel_id": cls._safe_str(snippet.get("channelId")),
                "published_at": cls._safe_str(snippet.get("publishedAt")),
                "description": cls._bound_text(snippet.get("description")),
                "thumbnail_url": cls._thumbnail_url(snippet.get("thumbnails")),
                "url": cls.WATCH_URL + video_id,
            })
        page_info = cls._safe_dict(data.get("pageInfo"))
        return {
            **context,
            "total_results": cls._safe_non_negative_int(page_info.get("totalResults")),
            "returned_results": len(videos),
            "videos": videos,
            "source": cls.SOURCE,
        }

    @classmethod
    def _parse_videos(
        cls, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize a ``videos.list`` response."""
        items = cls._safe_list(data.get("items"), "items")
        videos = []
        returned_ids = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            video_id = item.get("id")
            snippet = cls._safe_dict(item.get("snippet"))
            statistics = cls._safe_dict(item.get("statistics"))
            content_details = cls._safe_dict(item.get("contentDetails"))
            if not isinstance(video_id, str) or not video_id or not snippet:
                continue
            returned_ids.add(video_id)
            videos.append({
                "video_id": video_id,
                "title": cls._safe_str(snippet.get("title")),
                "channel_title": cls._safe_str(snippet.get("channelTitle")),
                "channel_id": cls._safe_str(snippet.get("channelId")),
                "published_at": cls._safe_str(snippet.get("publishedAt")),
                "description": cls._bound_text(snippet.get("description")),
                "tags": cls._safe_tags(snippet.get("tags")),
                "duration_seconds": cls.parse_duration(
                    cls._safe_str(content_details.get("duration"))
                ),
                "view_count": cls._safe_non_negative_int(statistics.get("viewCount")),
                "like_count": cls._safe_non_negative_int(statistics.get("likeCount")),
                "comment_count": cls._safe_non_negative_int(statistics.get("commentCount")),
                "url": cls.WATCH_URL + video_id,
            })
        not_found_ids = [
            vid for vid in context["video_ids"] if vid not in returned_ids
        ]
        return {
            **context,
            "returned_results": len(videos),
            "not_found_ids": not_found_ids,
            "videos": videos,
            "source": cls.SOURCE,
        }

    @staticmethod
    def parse_duration(duration_str: str) -> int:
        """Convert an ISO 8601 YouTube duration (e.g. ``PT1H2M3S``) to seconds."""
        if not duration_str:
            return 0
        match = YouTubeTool.DURATION_PATTERN.fullmatch(duration_str)
        if not match:
            return 0
        days = int(match.group(1) or 0)
        hours = int(match.group(2) or 0)
        minutes = int(match.group(3) or 0)
        seconds = int(match.group(4) or 0)
        return days * 86400 + hours * 3600 + minutes * 60 + seconds

    # ------------------------------------------------------------------ #
    # Error payloads (structured, redacted against the raw API key)
    # ------------------------------------------------------------------ #

    def _error_result(
        self,
        context: Dict[str, Any],
        error_type: str,
        message: str,
        status_code: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build a structured error payload without echoing the API key."""
        error: Dict[str, Any] = {
            "type": error_type,
            "message": self._redact(str(message))[: self.MAX_ERROR_CHARS],
        }
        if status_code is not None:
            error["status_code"] = status_code
        if reason:
            error["reason"] = self._redact(str(reason))[: self.MAX_ERROR_CHARS]
        return {**context, "error": error, "source": self.SOURCE}

    def _http_error_result(
        self, context: Dict[str, Any], response: httpx.Response
    ) -> Dict[str, Any]:
        """Turn a non-2xx response into a structured, redacted error."""
        message = f"YouTube API returned HTTP {response.status_code}."
        reason = None
        try:
            body = response.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            api_error = body.get("error")
            if isinstance(api_error, dict):
                message = (
                    f"YouTube API returned HTTP {response.status_code}: "
                    f"{api_error.get('message', '')}"
                )
                errors = api_error.get("errors")
                if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                    reason = errors[0].get("reason")
        return self._error_result(
            context,
            error_type="http_error",
            message=message,
            status_code=response.status_code,
            reason=reason if isinstance(reason, str) else None,
        )

    def _redact(self, text: str) -> str:
        """Replace any occurrence of the raw API key value with ``***``."""
        if self.api_key is None:
            return text
        raw = self.api_key.get_secret_value()
        if raw and raw in text:
            return text.replace(raw, "***")
        return text

    # ------------------------------------------------------------------ #
    # Small helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _safe_list(cls, value: Any, field: str) -> List[Any]:
        """Require a list field in the API response."""
        if not isinstance(value, list):
            cls._invalid(f"invalid YouTube response: {field!r} must be a list")
        return value

    @staticmethod
    def _safe_dict(value: Any) -> Dict[str, Any]:
        """Coerce an API response fragment to a dict (empty on anything else)."""
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _safe_str(value: Any) -> str:
        """Coerce an API response scalar to a clean string."""
        return value.strip() if isinstance(value, str) else ""

    @classmethod
    def _safe_non_negative_int(cls, value: Any) -> int:
        """Parse a YouTube statistics scalar into a non-negative integer."""
        if value in (None, ""):
            return 0
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        return parsed if parsed > 0 else 0

    @classmethod
    def _bound_text(cls, value: Any) -> str:
        """Bound a free-text API field to ``MAX_DESCRIPTION_CHARS``."""
        text = cls._safe_str(value)
        return text if len(text) <= cls.MAX_DESCRIPTION_CHARS else (
            text[: cls.MAX_DESCRIPTION_CHARS].rstrip() + "…"
        )

    @classmethod
    def _safe_tags(cls, value: Any) -> List[str]:
        """Bound the tag list to ``MAX_TAGS`` non-empty strings."""
        if not isinstance(value, list):
            return []
        tags = [cls._safe_str(tag) for tag in value]
        return [tag for tag in tags if tag][: cls.MAX_TAGS]

    @classmethod
    def _thumbnail_url(cls, value: Any) -> str:
        """Pick a compact thumbnail URL from a YouTube ``thumbnails`` map."""
        thumbnails = cls._safe_dict(value)
        for size in ("medium", "high", "default"):
            url = cls._safe_dict(thumbnails.get(size)).get("url")
            if isinstance(url, str) and url:
                return url
        return ""
