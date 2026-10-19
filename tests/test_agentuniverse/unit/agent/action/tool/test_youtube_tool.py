#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_youtube_tool.py

"""Offline unit tests for YouTubeTool.

Every HTTP interaction goes through ``httpx.MockTransport`` — no test in
this module touches the network. A shared ``RecordingTransport`` records
every request so the suite can assert both what was sent and that nothing
was sent at all when validation must reject the input first.
"""

import os
import unittest
from unittest.mock import patch

import httpx

from agentuniverse.agent.action.tool.common_tool.youtube_tool import YouTubeTool

TEST_KEY = "test-key-0123456789abcdef"

SEARCH_RESPONSE = {
    "kind": "youtube#searchListResponse",
    "pageInfo": {"totalResults": 1234, "resultsPerPage": 5},
    "items": [
        {
            "kind": "youtube#searchResult",
            "id": {"kind": "youtube#video", "videoId": "dQw4w9WgXcQ"},
            "snippet": {
                "title": "Machine Learning Tutorial",
                "channelTitle": "Test Channel",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "publishedAt": "2026-01-02T03:04:05Z",
                "description": "A tutorial about machine learning.",
                "thumbnails": {
                    "medium": {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"}
                },
            },
        },
        {
            # Non-video items are skipped defensively.
            "kind": "youtube#searchResult",
            "id": {"kind": "youtube#channel", "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw"},
            "snippet": {"title": "Not a video"},
        },
    ],
}

VIDEOS_RESPONSE = {
    "kind": "youtube#videoListResponse",
    "items": [
        {
            "kind": "youtube#video",
            "id": "dQw4w9WgXcQ",
            "snippet": {
                "title": "Machine Learning Tutorial",
                "channelTitle": "Test Channel",
                "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "publishedAt": "2026-01-02T03:04:05Z",
                "description": "A tutorial about machine learning.",
                "tags": ["ml", "python", "ai"],
            },
            "statistics": {
                "viewCount": "12345",
                "likeCount": "678",
                "commentCount": "9",
            },
            "contentDetails": {"duration": "PT1H2M3S"},
        }
    ],
}


class RecordingTransport(httpx.MockTransport):
    """MockTransport that records every request it serves."""

    def __init__(self, handler):
        self.requests = []
        super().__init__(handler)

    def handle_request(self, request):
        self.requests.append(request)
        return super().handle_request(request)


def json_handler(payload, status_code=200):
    def handler(request):
        return httpx.Response(status_code, json=payload)
    return handler


class YouTubeToolTest(unittest.TestCase):
    """Test cases for the httpx-based YouTubeTool."""

    def setUp(self) -> None:
        self.transport = RecordingTransport(json_handler({}))
        self.tool = YouTubeTool(api_key=TEST_KEY, transport=self.transport)

    # ------------------------------------------------------------------ #
    # search mode
    # ------------------------------------------------------------------ #

    def test_search_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = YouTubeTool(api_key=TEST_KEY, transport=self.transport)

        result = self.tool.execute(mode="search", query="machine learning")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "www.googleapis.com")
        self.assertEqual(request.url.path, "/youtube/v3/search")
        self.assertEqual(request.url.params.get("part"), "snippet")
        self.assertEqual(request.url.params.get("q"), "machine learning")
        self.assertEqual(request.url.params.get("type"), "video")
        self.assertEqual(request.url.params.get("maxResults"), "5")
        self.assertEqual(request.url.params.get("key"), TEST_KEY)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "machine learning")
        self.assertEqual(result["max_results"], 5)
        self.assertEqual(result["total_results"], 1234)
        self.assertEqual(result["returned_results"], 1)  # non-video item skipped
        video = result["videos"][0]
        self.assertEqual(video["video_id"], "dQw4w9WgXcQ")
        self.assertEqual(video["title"], "Machine Learning Tutorial")
        self.assertEqual(video["channel_title"], "Test Channel")
        self.assertEqual(
            video["thumbnail_url"], "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
        )
        self.assertEqual(video["url"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertTrue(result["source"].startswith("YouTube Data API v3"))

    def test_search_result_shape(self) -> None:
        self.tool = YouTubeTool(
            api_key=TEST_KEY,
            transport=RecordingTransport(json_handler(SEARCH_RESPONSE)),
        )
        result = self.tool.execute(mode="search", query="machine learning")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "query",
                "max_results",
                "total_results",
                "returned_results",
                "videos",
                "source",
            },
        )
        self.assertEqual(
            set(result["videos"][0].keys()),
            {
                "video_id",
                "title",
                "channel_title",
                "channel_id",
                "published_at",
                "description",
                "thumbnail_url",
                "url",
            },
        )

    def test_search_query_is_normalized(self) -> None:
        self.tool = YouTubeTool(
            api_key=TEST_KEY,
            transport=RecordingTransport(json_handler(SEARCH_RESPONSE)),
        )
        result = self.tool.execute(mode="search", query="  machine   learning  ")
        self.assertEqual(result["query"], "machine learning")

    # ------------------------------------------------------------------ #
    # videos mode
    # ------------------------------------------------------------------ #

    def test_videos_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(VIDEOS_RESPONSE))
        self.tool = YouTubeTool(api_key=TEST_KEY, transport=self.transport)

        result = self.tool.execute(
            mode="videos", video_id="aaaaaaaaaaa,dQw4w9WgXcQ"
        )

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.path, "/youtube/v3/videos")
        self.assertEqual(
            request.url.params.get("part"), "snippet,statistics,contentDetails"
        )
        self.assertEqual(
            request.url.params.get("id"), "aaaaaaaaaaa,dQw4w9WgXcQ"
        )
        self.assertEqual(request.url.params.get("key"), TEST_KEY)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "videos")
        self.assertEqual(result["video_ids"], ["aaaaaaaaaaa", "dQw4w9WgXcQ"])
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["not_found_ids"], ["aaaaaaaaaaa"])
        video = result["videos"][0]
        self.assertEqual(video["video_id"], "dQw4w9WgXcQ")
        self.assertEqual(video["duration_seconds"], 3723)
        self.assertEqual(video["view_count"], 12345)
        self.assertEqual(video["like_count"], 678)
        self.assertEqual(video["comment_count"], 9)
        self.assertEqual(video["tags"], ["ml", "python", "ai"])
        self.assertEqual(video["url"], "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_videos_result_shape(self) -> None:
        self.tool = YouTubeTool(
            api_key=TEST_KEY,
            transport=RecordingTransport(json_handler(VIDEOS_RESPONSE)),
        )
        result = self.tool.execute(mode="videos", video_id="dQw4w9WgXcQ")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "video_ids",
                "returned_results",
                "not_found_ids",
                "videos",
                "source",
            },
        )
        self.assertEqual(
            set(result["videos"][0].keys()),
            {
                "video_id",
                "title",
                "channel_title",
                "channel_id",
                "published_at",
                "description",
                "tags",
                "duration_seconds",
                "view_count",
                "like_count",
                "comment_count",
                "url",
            },
        )

    def test_videos_accepts_list_and_deduplicates(self) -> None:
        self.transport = RecordingTransport(json_handler(VIDEOS_RESPONSE))
        self.tool = YouTubeTool(api_key=TEST_KEY, transport=self.transport)
        self.tool.execute(
            mode="videos", video_id=["dQw4w9WgXcQ", "dQw4w9WgXcQ"]
        )
        request = self.transport.requests[0]
        self.assertEqual(request.url.params.get("id"), "dQw4w9WgXcQ")

    def test_videos_missing_statistics_default_to_zero(self) -> None:
        payload = {
            "items": [
                {
                    "id": "dQw4w9WgXcQ",
                    "snippet": {"title": "Hidden stats"},
                    "statistics": {"viewCount": "42"},
                }
            ]
        }
        self.tool = YouTubeTool(
            api_key=TEST_KEY, transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="videos", video_id="dQw4w9WgXcQ")
        video = result["videos"][0]
        self.assertEqual(video["view_count"], 42)
        self.assertEqual(video["like_count"], 0)
        self.assertEqual(video["comment_count"], 0)
        self.assertEqual(video["duration_seconds"], 0)

    # ------------------------------------------------------------------ #
    # validation: everything below must fail before any request is sent
    # ------------------------------------------------------------------ #

    def assertNoRequest(self, invoke, message_pattern):
        with self.assertRaises(ValueError) as ctx:
            invoke()
        self.assertRegex(str(ctx.exception), message_pattern)
        self.assertEqual(self.transport.requests, [])

    def test_missing_api_key_raises_before_request(self) -> None:
        tool = YouTubeTool(api_key=None, transport=self.transport)
        self.assertNoRequest(
            lambda: tool.execute(mode="search", query="machine learning"),
            r"YOUTUBE_API_KEY",
        )

    def test_invalid_mode_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="trending"),
            r"mode must be one of",
        )

    def test_blank_query_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="   "),
            r"query is required",
        )

    def test_missing_query_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search"),
            r"query is required",
        )

    def test_overlong_query_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="x" * 301),
            r"at most 300 characters",
        )

    def test_non_integer_max_results_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results="many"),
            r"max_results must be an integer",
        )

    def test_out_of_range_max_results_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results=0),
            r"between 1 and 25",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results=26),
            r"between 1 and 25",
        )

    def test_missing_video_id_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="videos"),
            r"video_id is required",
        )

    def test_malformed_video_id_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="videos", video_id="short"),
            r"invalid YouTube video ID",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="videos", video_id="bad id;drop"),
            r"invalid YouTube video ID",
        )

    def test_too_many_video_ids_rejected(self) -> None:
        ids = ",".join(f"videoid{i:04d}" for i in range(11))
        self.assertNoRequest(
            lambda: self.tool.execute(mode="videos", video_id=ids),
            r"too many video IDs: 11 \(max 10\)",
        )

    def test_invalid_video_id_type_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="videos", video_id=42),
            r"must be a string or a list of strings",
        )

    # ------------------------------------------------------------------ #
    # runtime errors: structured payloads, never an exception, no key leak
    # ------------------------------------------------------------------ #

    def test_http_error_returns_structured_payload(self) -> None:
        payload = {
            "error": {
                "code": 403,
                "message": f"The request failed with key {TEST_KEY}.",
                "errors": [
                    {"reason": "quotaExceeded", "message": "quota exceeded"}
                ],
            }
        }
        self.tool = YouTubeTool(
            api_key=TEST_KEY,
            transport=RecordingTransport(json_handler(payload, status_code=403)),
        )
        result = self.tool.execute(mode="search", query="machine learning")

        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 403)
        self.assertEqual(result["error"]["reason"], "quotaExceeded")
        self.assertNotIn(TEST_KEY, str(result))

    def test_timeout_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectTimeout("timed out")

        self.tool = YouTubeTool(
            api_key=TEST_KEY, transport=RecordingTransport(handler)
        )
        result = self.tool.execute(mode="search", query="machine learning")
        self.assertEqual(result["error"]["type"], "request_timeout")

    def test_connection_error_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectError("no route to host")

        self.tool = YouTubeTool(
            api_key=TEST_KEY, transport=RecordingTransport(handler)
        )
        result = self.tool.execute(mode="videos", video_id="dQw4w9WgXcQ")
        self.assertEqual(result["error"]["type"], "request_error")

    def test_non_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, text="<html>not json</html>")

        self.tool = YouTubeTool(
            api_key=TEST_KEY, transport=RecordingTransport(handler)
        )
        result = self.tool.execute(mode="search", query="machine learning")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_invalid_response_shape_returns_structured_payload(self) -> None:
        self.tool = YouTubeTool(
            api_key=TEST_KEY,
            transport=RecordingTransport(json_handler({"items": "nope"})),
        )
        result = self.tool.execute(mode="search", query="machine learning")
        self.assertEqual(result["error"]["type"], "invalid_response")

    # ------------------------------------------------------------------ #
    # API key handling
    # ------------------------------------------------------------------ #

    def test_api_key_read_from_environment(self) -> None:
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "env-secret-key"}):
            tool = YouTubeTool()
        self.assertEqual(tool.api_key.get_secret_value(), "env-secret-key")
        self.assertNotIn("env-secret-key", repr(tool))

    def test_api_key_never_in_repr(self) -> None:
        self.assertNotIn(TEST_KEY, repr(self.tool))
        self.assertNotIn(TEST_KEY, str(self.tool.model_dump(exclude={"transport"})))

    # ------------------------------------------------------------------ #
    # pure helpers
    # ------------------------------------------------------------------ #

    def test_parse_duration(self) -> None:
        self.assertEqual(YouTubeTool.parse_duration("PT2M"), 120)
        self.assertEqual(YouTubeTool.parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(YouTubeTool.parse_duration("P1DT2H3M4S"), 93784)
        self.assertEqual(YouTubeTool.parse_duration(""), 0)
        self.assertEqual(YouTubeTool.parse_duration("PT1Mbad"), 0)

    def test_description_is_bounded(self) -> None:
        payload = {
            "items": [
                {
                    "id": {"kind": "youtube#video", "videoId": "dQw4w9WgXcQ"},
                    "snippet": {"title": "T", "description": "x" * 5000},
                }
            ]
        }
        self.tool = YouTubeTool(
            api_key=TEST_KEY, transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertLessEqual(len(result["videos"][0]["description"]), 1001)


if __name__ == "__main__":
    unittest.main()
