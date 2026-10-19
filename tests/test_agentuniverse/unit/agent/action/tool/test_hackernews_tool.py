#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_hackernews_tool.py

"""Offline unit tests for HackerNewsTool.

Every HTTP interaction goes through ``httpx.MockTransport`` — no test in
this module touches the network. A shared ``RecordingTransport`` records
every request so the suite can assert both what was sent and that nothing
was sent at all when validation must reject the input first.

The mock payloads mirror the real Algolia HN Search API response shapes
(``/api/v1/search``, ``/api/v1/search_by_date``, ``/api/v1/items/{id}``,
and ``/api/v1/users/{username}``).
"""

import unittest

import httpx

from agentuniverse.agent.action.tool.common_tool.hackernews_tool import (
    HackerNewsTool,
)

SEARCH_RESPONSE = {
    "hits": [
        {
            "created_at": "2026-09-30T08:15:00Z",
            "title": "Show HN: A vector database built for agents",
            "url": "https://example.com/vdb",
            "author": "pg",
            "points": 142,
            "story_text": None,
            "comment_text": None,
            "num_comments": 57,
            "objectID": "44000001",
        },
        {
            "created_at": "2026-10-02T18:30:00Z",
            "title": "Vector databases are overkill for RAG",
            "url": "https://example.com/blog",
            "author": "tptacek",
            "points": 89,
            "story_text": "We replaced our vector database with SQLite.",
            "comment_text": None,
            "num_comments": 203,
            "objectID": "44000002",
        },
    ],
    "nbHits": 1750,
    "page": 0,
    "nbPages": 175,
    "hitsPerPage": 10,
    "processingTimeMS": 2,
    "query": "vector database",
    "params": "query=vector%20database&tags=story",
}

EMPTY_SEARCH_RESPONSE = {
    "hits": [],
    "nbHits": 0,
    "page": 0,
    "nbPages": 0,
    "hitsPerPage": 10,
    "query": "zzz-no-such-topic-zzz",
}

COMMENT_SEARCH_RESPONSE = {
    "hits": [
        {
            "created_at": "2026-10-01T10:00:00Z",
            "author": "rl3",
            "story_title": "Show HN: A vector database built for agents",
            "story_id": 44000001,
            "comment_text": (
                "<p>We tried it and the <i>recall</i> was great.</p>"
            ),
            "points": None,
            "num_comments": None,
            "objectID": "44000111",
        },
    ],
    "nbHits": 24,
    "page": 0,
    "nbPages": 3,
    "hitsPerPage": 10,
    "query": "recall",
}

ITEM_RESPONSE = {
    "id": 8863,
    "created_at": "2007-04-04T04:01:32Z",
    "type": "story",
    "author": "pg",
    "title": "My YC app: Reddit",
    "url": "https://news.ycombinator.com",
    "text": "<p>This is <b>not</b> a prank.</p>\n",
    "points": 111,
    "children": [
        {
            "id": 8864,
            "created_at": "2007-04-04T04:03:00Z",
            "author": "steve",
            "text": "<p>Congrats!</p>",
            "children": [],
        },
        {"id": 8865, "created_at": "2007-04-04T04:05:00Z", "author": "sam"},
    ],
    "options": [],
}

USER_RESPONSE = {
    "id": "pg",
    "created_at": "2006-10-09T12:38:35Z",
    "karma": 190000,
    "about": "<p>Building <a href=\"https://news.ycombinator.com\">HN</a>.</p>",
    "submitted": [1, 2, 3, 4, 5],
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


class HackerNewsToolTest(unittest.TestCase):
    """Offline test cases for the keyless Algolia-backed HackerNewsTool."""

    def setUp(self) -> None:
        self.transport = RecordingTransport(json_handler({}))
        self.tool = HackerNewsTool(transport=self.transport)

    # ------------------------------------------------------------------ #
    # search mode
    # ------------------------------------------------------------------ #

    def test_search_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)

        result = self.tool.execute(mode="search", query="vector database")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "hn.algolia.com")
        self.assertEqual(request.url.path, "/api/v1/search")
        self.assertEqual(
            request.url.params.get("query"), "vector database"
        )
        self.assertEqual(request.url.params.get("tags"), "story")
        self.assertEqual(request.url.params.get("hitsPerPage"), "10")
        self.assertEqual(request.url.params.get("page"), "0")
        # The Algolia HN API is keyless: no credential parameter is sent.
        self.assertNotIn("key", request.url.params)
        self.assertNotIn("apiKey", request.url.params)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "vector database")
        self.assertEqual(result["tags"], "story")
        self.assertEqual(result["order"], "relevance")
        self.assertEqual(result["max_results"], 10)
        self.assertEqual(result["page"], 0)
        self.assertEqual(result["total_hits"], 1750)
        self.assertEqual(result["total_pages"], 175)
        self.assertEqual(result["returned_hits"], 2)
        first = result["results"][0]
        self.assertEqual(first["object_id"], "44000001")
        self.assertEqual(
            first["title"], "Show HN: A vector database built for agents"
        )
        self.assertEqual(first["author"], "pg")
        self.assertEqual(first["url"], "https://example.com/vdb")
        self.assertEqual(first["points"], 142)
        self.assertEqual(first["num_comments"], 57)
        self.assertEqual(first["created_at"], "2026-09-30T08:15:00Z")
        self.assertEqual(
            first["hn_url"], "https://news.ycombinator.com/item?id=44000001"
        )
        # A story without self-text has an empty text field.
        self.assertEqual(first["text"], "")
        self.assertTrue(result["source"].startswith("Hacker News Algolia"))

    def test_search_result_shape(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(SEARCH_RESPONSE))
        )
        result = self.tool.execute(mode="search", query="vector database")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "query",
                "tags",
                "order",
                "max_results",
                "page",
                "total_hits",
                "total_pages",
                "returned_hits",
                "results",
                "source",
            },
        )
        self.assertEqual(
            set(result["results"][0].keys()),
            {
                "object_id",
                "title",
                "author",
                "url",
                "points",
                "num_comments",
                "created_at",
                "text",
                "hn_url",
            },
        )

    def test_search_recent_order_uses_search_by_date(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)

        result = self.tool.execute(
            mode="search", query="vector database", order="recent"
        )

        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "hn.algolia.com")
        self.assertEqual(request.url.path, "/api/v1/search_by_date")
        self.assertEqual(result["order"], "recent")

    def test_search_comment_tags(self) -> None:
        self.transport = RecordingTransport(json_handler(COMMENT_SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)

        result = self.tool.execute(mode="search", query="recall", tags="comment")

        request = self.transport.requests[0]
        self.assertEqual(request.url.params.get("tags"), "comment")
        self.assertNotIn("error", result)
        self.assertEqual(result["returned_hits"], 1)
        hit = result["results"][0]
        # Comment text is HTML-stripped into the shared text field.
        self.assertEqual(hit["text"], "We tried it and the recall was great.")
        self.assertEqual(
            hit["hn_url"], "https://news.ycombinator.com/item?id=44000111"
        )
        # points / num_comments are absent in comment hits and coerce to 0.
        self.assertEqual(hit["points"], 0)
        self.assertEqual(hit["num_comments"], 0)

    def test_search_story_text_used_when_present(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(SEARCH_RESPONSE))
        )
        result = self.tool.execute(mode="search", query="vector database")
        self.assertEqual(
            result["results"][1]["text"],
            "We replaced our vector database with SQLite.",
        )

    def test_search_query_is_normalized(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)
        result = self.tool.execute(mode="search", query="  vector   database  ")
        self.assertEqual(result["query"], "vector database")
        self.assertEqual(
            self.transport.requests[0].url.params.get("query"),
            "vector database",
        )

    def test_search_weird_but_valid_query_is_escaped_as_parameter(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)
        # Query-string metacharacters must stay inside the encoded
        # parameter — they can never re-shape the URL itself.
        weird = "a/b?x=1&y=2#frag %20+"
        result = self.tool.execute(mode="search", query=weird)
        request = self.transport.requests[0]
        self.assertEqual(request.url.path, "/api/v1/search")
        self.assertEqual(request.url.params.get("query"), weird)
        self.assertNotIn("error", result)

    def test_search_max_results_and_page(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)
        self.tool.execute(
            mode="search", query="ml", max_results=25, page=3
        )
        request = self.transport.requests[0]
        self.assertEqual(request.url.params.get("hitsPerPage"), "25")
        self.assertEqual(request.url.params.get("page"), "3")

    def test_search_empty_results(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(EMPTY_SEARCH_RESPONSE))
        )
        result = self.tool.execute(mode="search", query="zzz no such topic zzz")
        self.assertNotIn("error", result)
        self.assertEqual(result["total_hits"], 0)
        self.assertEqual(result["returned_hits"], 0)
        self.assertEqual(result["results"], [])

    def test_search_skips_malformed_hits(self) -> None:
        payload = {
            "hits": [{"author": "x"}, {"objectID": "99", "title": "Real"}],
            "nbHits": 2,
        }
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="search", query="anything")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["object_id"], "99")

    # ------------------------------------------------------------------ #
    # item mode
    # ------------------------------------------------------------------ #

    def test_item_mode_with_string_id(self) -> None:
        self.transport = RecordingTransport(json_handler(ITEM_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)

        result = self.tool.execute(mode="item", item_id="8863")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "hn.algolia.com")
        self.assertEqual(request.url.path, "/api/v1/items/8863")
        # The item endpoint is a plain GET with no query parameters.
        self.assertEqual(list(request.url.params.keys()), [])

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "item")
        self.assertEqual(result["item_id"], 8863)
        self.assertEqual(result["id"], 8863)
        self.assertEqual(result["type"], "story")
        self.assertEqual(result["title"], "My YC app: Reddit")
        self.assertEqual(result["author"], "pg")
        self.assertEqual(result["url"], "https://news.ycombinator.com")
        self.assertEqual(result["points"], 111)
        self.assertEqual(result["created_at"], "2007-04-04T04:01:32Z")
        # HTML item text is returned as clean plain text.
        self.assertEqual(result["text"], "This is not a prank.")
        self.assertEqual(result["top_level_reply_count"], 2)
        self.assertEqual(len(result["top_level_replies"]), 2)
        first_reply = result["top_level_replies"][0]
        self.assertEqual(first_reply["id"], 8864)
        self.assertEqual(first_reply["author"], "steve")
        self.assertEqual(first_reply["text"], "Congrats!")
        self.assertEqual(
            result["hn_url"], "https://news.ycombinator.com/item?id=8863"
        )

    def test_item_mode_with_integer_id(self) -> None:
        self.transport = RecordingTransport(json_handler(ITEM_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)
        self.tool.execute(mode="item", item_id=8863)
        self.assertEqual(
            self.transport.requests[0].url.path, "/api/v1/items/8863"
        )

    def test_item_result_shape(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(ITEM_RESPONSE))
        )
        result = self.tool.execute(mode="item", item_id="8863")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "item_id",
                "id",
                "type",
                "title",
                "author",
                "url",
                "text",
                "points",
                "created_at",
                "top_level_replies",
                "top_level_reply_count",
                "hn_url",
                "source",
            },
        )
        self.assertEqual(
            set(result["top_level_replies"][0].keys()),
            {"id", "author", "created_at", "text"},
        )

    # ------------------------------------------------------------------ #
    # user mode
    # ------------------------------------------------------------------ #

    def test_user_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(USER_RESPONSE))
        self.tool = HackerNewsTool(transport=self.transport)

        result = self.tool.execute(mode="user", username="pg")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "hn.algolia.com")
        self.assertEqual(request.url.path, "/api/v1/users/pg")
        self.assertEqual(list(request.url.params.keys()), [])

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "user")
        self.assertEqual(result["username"], "pg")
        self.assertEqual(result["karma"], 190000)
        self.assertEqual(result["created_at"], "2006-10-09T12:38:35Z")
        # HTML about text is stripped of tags (tags become spaces) and
        # whitespace is collapsed.
        self.assertEqual(result["about"], "Building HN .")
        self.assertEqual(result["submitted_count"], 5)

    def test_user_result_shape(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(USER_RESPONSE))
        )
        result = self.tool.execute(mode="user", username="pg")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "username",
                "created_at",
                "karma",
                "about",
                "submitted_count",
                "source",
            },
        )

    # ------------------------------------------------------------------ #
    # validation: everything below must fail before any request is sent
    # ------------------------------------------------------------------ #

    def assertNoRequest(self, invoke, message_pattern):
        with self.assertRaises(ValueError) as ctx:
            invoke()
        self.assertRegex(str(ctx.exception), message_pattern)
        self.assertEqual(self.transport.requests, [])

    def test_invalid_mode_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="browse"),
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

    def test_query_wrong_type_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query=42),
            r"query is required",
        )

    def test_control_characters_in_query_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="bad\nquery"),
            r"control characters",
        )

    def test_overlong_query_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="x" * 301),
            r"at most 300 characters",
        )

    def test_invalid_tags_rejected(self) -> None:
        for bad_tags in ("poll", "story,comment", "", None, True):
            self.assertNoRequest(
                lambda bad_tags=bad_tags: self.tool.execute(
                    mode="search", query="ml", tags=bad_tags
                ),
                r"tags must be one of",
            )

    def test_invalid_order_rejected(self) -> None:
        for bad_order in ("newest", "", None, 1):
            self.assertNoRequest(
                lambda bad_order=bad_order: self.tool.execute(
                    mode="search", query="ml", order=bad_order
                ),
                r"order must be one of",
            )

    def test_non_integer_max_results_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results="many"),
            r"max_results must be an integer",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results=True),
            r"max_results must be an integer",
        )

    def test_out_of_range_max_results_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results=0),
            r"between 1 and 50",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", max_results=51),
            r"between 1 and 50",
        )

    def test_non_integer_page_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", page="one"),
            r"page must be an integer",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", page=False),
            r"page must be an integer",
        )

    def test_out_of_range_page_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", page=-1),
            r"page must be between 0 and 49",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="search", query="ml", page=50),
            r"page must be between 0 and 49",
        )

    def test_invalid_item_id_rejected(self) -> None:
        for bad_id in (None, "abc", "-1", "1;drop", "../admin", "88 63", 12.5, True):
            self.assertNoRequest(
                lambda bad_id=bad_id: self.tool.execute(
                    mode="item", item_id=bad_id
                ),
                r"item_id",
            )

    def test_out_of_range_item_id_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", item_id=0),
            r"item_id must be between 1 and 2147483647",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", item_id="2147483648"),
            r"item_id must be between 1 and 2147483647",
        )

    def test_invalid_username_rejected(self) -> None:
        for bad_username in (None, "a", "bad name", "../x", "pg!", "pg#", 123, ""):
            self.assertNoRequest(
                lambda bad_username=bad_username: self.tool.execute(
                    mode="user", username=bad_username
                ),
                r"username is required",
            )

    # ------------------------------------------------------------------ #
    # runtime errors: structured payloads, never an exception
    # ------------------------------------------------------------------ #

    def test_http_error_with_algolia_error_body(self) -> None:
        payload = {"error": "Invalid query"}
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload, status_code=400))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 400)
        self.assertIn("Invalid query", result["error"]["message"])
        self.assertIn("Invalid query", result["error"]["reason"])

    def test_http_404_item_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(404, text="Item not found")

        self.tool = HackerNewsTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="item", item_id="1")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 404)
        self.assertNotIn("reason", result["error"])

    def test_http_error_with_dict_error_body(self) -> None:
        payload = {"error": {"code": "rate_limited", "message": "Slow down"}}
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload, status_code=429))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 429)
        self.assertEqual(result["error"]["reason"], "rate_limited")
        self.assertIn("Slow down", result["error"]["message"])

    def test_timeout_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectTimeout("timed out")

        self.tool = HackerNewsTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "request_timeout")

    def test_connection_error_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectError("no route to host")

        self.tool = HackerNewsTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="item", item_id="8863")
        self.assertEqual(result["error"]["type"], "request_error")
        self.assertNotIn("status_code", result["error"])

    def test_non_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, text="<html>not json</html>")

        self.tool = HackerNewsTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_non_object_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, json=[1, 2, 3])

        self.tool = HackerNewsTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="user", username="pg")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_invalid_search_shape_returns_structured_payload(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler({"hits": "nope"}))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("'hits' must be a list", result["error"]["message"])

    def test_invalid_item_shape_returns_structured_payload(self) -> None:
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler({"foo": "bar"}))
        )
        result = self.tool.execute(mode="item", item_id="8863")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("not an item object", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # output bounding
    # ------------------------------------------------------------------ #

    def test_item_text_is_bounded(self) -> None:
        payload = dict(ITEM_RESPONSE)
        payload["text"] = "x" * 20000
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="item", item_id="8863")
        self.assertLessEqual(len(result["text"]), 5001)

    def test_search_title_is_bounded(self) -> None:
        payload = {
            "hits": [{"objectID": "1", "title": "t" * 8000}],
            "nbHits": 1,
        }
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertLessEqual(len(result["results"][0]["title"]), 5001)

    def test_replies_are_bounded(self) -> None:
        payload = dict(ITEM_RESPONSE)
        payload["children"] = [
            {"id": 9000 + i, "author": "u", "text": "r" * 2000}
            for i in range(25)
        ]
        self.tool = HackerNewsTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="item", item_id="8863")
        self.assertEqual(result["top_level_reply_count"], 25)
        self.assertEqual(len(result["top_level_replies"]), 20)
        self.assertLessEqual(
            len(result["top_level_replies"][0]["text"]), 501
        )


if __name__ == "__main__":
    unittest.main()
