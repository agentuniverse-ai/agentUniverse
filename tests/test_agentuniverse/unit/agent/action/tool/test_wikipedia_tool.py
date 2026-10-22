#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_wikipedia_tool.py

"""Offline unit tests for WikipediaTool.

Every HTTP interaction goes through ``httpx.MockTransport`` — no test in
this module touches the network. A shared ``RecordingTransport`` records
every request so the suite can assert both what was sent and that nothing
was sent at all when validation must reject the input first.

The mock payloads mirror the real MediaWiki API response shapes
(``formatversion=2`` query API and the REST ``page/summary`` endpoint).
"""

import unittest

import httpx
from pydantic import ValidationError

from agentuniverse.agent.action.tool.common_tool.wikipedia_tool import (
    WikipediaTool,
)

SEARCH_RESPONSE = {
    "batchcomplete": True,
    "query": {
        "searchinfo": {"totalhits": 7536},
        "search": [
            {
                "ns": 0,
                "title": "Albert Einstein",
                "pageid": 736,
                "wordcount": 23711,
                "snippet": (
                    "<span class=\"searchmatch\">Albert</span> "
                    "<span class=\"searchmatch\">Einstein</span> (14 March "
                    "1879 \u2013 18 April 1955) was a German-born "
                    "theoretical physicist."
                ),
                "timestamp": "2026-10-09T13:01:06Z",
            },
            {
                "ns": 0,
                "title": "Hans Albert Einstein",
                "pageid": 1373258,
                "wordcount": 1222,
                "snippet": "Hans <b>Albert</b> Einstein was a Swiss-American engineer.",
                "timestamp": "2026-10-01T10:00:00Z",
            },
        ],
    },
}

EMPTY_SEARCH_RESPONSE = {
    "batchcomplete": True,
    "query": {"searchinfo": {"totalhits": 0}, "search": []},
}

SUMMARY_RESPONSE = {
    "type": "standard",
    "title": "Albert Einstein",
    "displaytitle": "Albert Einstein",
    "pageid": 736,
    "lang": "en",
    "description": "German-born theoretical physicist",
    "extract": (
        "Albert Einstein (14 March 1879 – 18 April 1955) was a German-born "
        "theoretical physicist best known for developing the theory of "
        "relativity."
    ),
    "content_urls": {
        "desktop": {"page": "https://en.wikipedia.org/wiki/Albert_Einstein"}
    },
    "thumbnail": {
        "source": "https://thumb.wikimedia.org/einstein.jpg",
        "width": 330,
        "height": 408,
    },
}

DETAILS_RESPONSE = {
    "batchcomplete": True,
    "query": {
        "normalized": [
            {"from": "Albert_Einstein", "to": "Albert Einstein"}
        ],
        "pages": [
            {
                "pageid": 736,
                "ns": 0,
                "title": "Albert Einstein",
                "extract": (
                    "Albert Einstein was a German-born theoretical physicist. "
                    "He developed the theory of relativity."
                ),
                "fullurl": "https://en.wikipedia.org/wiki/Albert_Einstein",
            }
        ],
    },
}

MISSING_PAGE_RESPONSE = {
    "batchcomplete": True,
    "query": {
        "pages": [
            {
                "ns": 0,
                "title": "No Such Page Zzzq 12345",
                "missing": True,
                "fullurl": "https://en.wikipedia.org/wiki/No_Such_Page_Zzzq_12345",
            }
        ]
    },
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


class WikipediaToolTest(unittest.TestCase):
    """Offline test cases for the keyless MediaWiki-based WikipediaTool."""

    def setUp(self) -> None:
        self.transport = RecordingTransport(json_handler({}))
        self.tool = WikipediaTool(transport=self.transport)

    # ------------------------------------------------------------------ #
    # search mode
    # ------------------------------------------------------------------ #

    def test_search_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)

        result = self.tool.execute(mode="search", query="albert einstein")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "en.wikipedia.org")
        self.assertEqual(request.url.path, "/w/api.php")
        self.assertEqual(request.url.params.get("action"), "query")
        self.assertEqual(request.url.params.get("list"), "search")
        self.assertEqual(request.url.params.get("srsearch"), "albert einstein")
        self.assertEqual(request.url.params.get("srlimit"), "5")
        self.assertEqual(
            request.url.params.get("srprop"), "snippet|wordcount|timestamp"
        )
        self.assertEqual(request.url.params.get("format"), "json")
        self.assertEqual(request.url.params.get("formatversion"), "2")
        # The MediaWiki API is keyless: no credential parameter is sent.
        self.assertNotIn("key", request.url.params)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["query"], "albert einstein")
        self.assertEqual(result["max_results"], 5)
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["total_hits"], 7536)
        self.assertEqual(result["returned_results"], 2)
        first = result["results"][0]
        self.assertEqual(first["title"], "Albert Einstein")
        self.assertEqual(first["pageid"], 736)
        self.assertEqual(first["wordcount"], 23711)
        self.assertEqual(first["timestamp"], "2026-10-09T13:01:06Z")
        # Highlight markup is stripped and entities are unescaped.
        self.assertNotIn("<", first["snippet"])
        self.assertNotIn("searchmatch", first["snippet"])
        self.assertTrue(first["snippet"].startswith("Albert Einstein (14 March"))
        self.assertEqual(
            first["url"], "https://en.wikipedia.org/wiki/Albert_Einstein"
        )
        self.assertTrue(result["source"].startswith("Wikipedia MediaWiki API"))

    def test_search_result_shape(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(SEARCH_RESPONSE))
        )
        result = self.tool.execute(mode="search", query="albert einstein")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "query",
                "max_results",
                "language",
                "total_hits",
                "returned_results",
                "results",
                "source",
            },
        )
        self.assertEqual(
            set(result["results"][0].keys()),
            {
                "title",
                "pageid",
                "snippet",
                "wordcount",
                "timestamp",
                "url",
            },
        )

    def test_search_query_is_normalized(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)
        result = self.tool.execute(mode="search", query="  albert   einstein  ")
        self.assertEqual(result["query"], "albert einstein")
        self.assertEqual(
            self.transport.requests[0].url.params.get("srsearch"),
            "albert einstein",
        )

    def test_search_empty_results(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(EMPTY_SEARCH_RESPONSE))
        )
        result = self.tool.execute(mode="search", query="zzz no such topic zzz")
        self.assertNotIn("error", result)
        self.assertEqual(result["total_hits"], 0)
        self.assertEqual(result["returned_results"], 0)
        self.assertEqual(result["results"], [])

    def test_search_skips_malformed_items(self) -> None:
        payload = {
            "query": {
                "searchinfo": {"totalhits": 1},
                "search": [{"ns": 0}, {"ns": 0, "title": "Real Title"}],
            }
        }
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="search", query="anything")
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["title"], "Real Title")

    # ------------------------------------------------------------------ #
    # summary mode
    # ------------------------------------------------------------------ #

    def test_summary_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(SUMMARY_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)

        result = self.tool.execute(mode="summary", title="Albert Einstein")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "en.wikipedia.org")
        self.assertEqual(
            request.url.path, "/api/rest_v1/page/summary/Albert_Einstein"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "summary")
        self.assertEqual(result["title"], "Albert Einstein")
        self.assertEqual(result["description"], "German-born theoretical physicist")
        self.assertTrue(result["extract"].startswith("Albert Einstein (14 March"))
        self.assertEqual(
            result["url"], "https://en.wikipedia.org/wiki/Albert_Einstein"
        )
        self.assertEqual(
            result["thumbnail_url"], "https://thumb.wikimedia.org/einstein.jpg"
        )
        self.assertEqual(result["pageid"], 736)
        self.assertEqual(result["page_type"], "standard")

    def test_summary_underscores_and_spaces_are_equivalent(self) -> None:
        self.transport = RecordingTransport(json_handler(SUMMARY_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)
        self.tool.execute(mode="summary", title="Albert_Einstein")
        self.assertEqual(
            self.transport.requests[0].url.path,
            "/api/rest_v1/page/summary/Albert_Einstein",
        )

    def test_summary_url_falls_back_to_constructed_page_url(self) -> None:
        payload = dict(SUMMARY_RESPONSE)
        payload["content_urls"] = {}
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="summary", title="Albert Einstein")
        self.assertEqual(
            result["url"], "https://en.wikipedia.org/wiki/Albert_Einstein"
        )

    def test_summary_result_shape(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(SUMMARY_RESPONSE))
        )
        result = self.tool.execute(mode="summary", title="Albert Einstein")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "title",
                "language",
                "description",
                "extract",
                "url",
                "thumbnail_url",
                "pageid",
                "page_type",
                "source",
            },
        )

    # ------------------------------------------------------------------ #
    # details mode
    # ------------------------------------------------------------------ #

    def test_details_mode_full_extract(self) -> None:
        self.transport = RecordingTransport(json_handler(DETAILS_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)

        result = self.tool.execute(mode="details", title="Albert Einstein")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "en.wikipedia.org")
        self.assertEqual(request.url.path, "/w/api.php")
        self.assertEqual(request.url.params.get("action"), "query")
        self.assertEqual(request.url.params.get("prop"), "extracts|info")
        self.assertEqual(request.url.params.get("inprop"), "url")
        self.assertEqual(request.url.params.get("explaintext"), "1")
        self.assertEqual(request.url.params.get("redirects"), "1")
        self.assertEqual(
            request.url.params.get("titles"), "Albert Einstein"
        )
        self.assertEqual(request.url.params.get("formatversion"), "2")
        self.assertNotIn("exsentences", request.url.params)
        self.assertNotIn("exchars", request.url.params)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "details")
        self.assertTrue(result["found"])
        self.assertEqual(result["title"], "Albert Einstein")
        self.assertEqual(result["pageid"], 736)
        self.assertTrue(result["extract"].startswith("Albert Einstein was"))
        self.assertEqual(
            result["url"], "https://en.wikipedia.org/wiki/Albert_Einstein"
        )

    def test_details_with_sentences_limit(self) -> None:
        self.transport = RecordingTransport(json_handler(DETAILS_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)
        self.tool.execute(mode="details", title="Albert Einstein", sentences=3)
        request = self.transport.requests[0]
        self.assertEqual(request.url.params.get("exsentences"), "3")
        self.assertNotIn("exchars", request.url.params)

    def test_details_with_chars_limit(self) -> None:
        self.transport = RecordingTransport(json_handler(DETAILS_RESPONSE))
        self.tool = WikipediaTool(transport=self.transport)
        self.tool.execute(mode="details", title="Albert Einstein", chars=500)
        request = self.transport.requests[0]
        self.assertEqual(request.url.params.get("exchars"), "500")
        self.assertNotIn("exsentences", request.url.params)

    def test_details_missing_page_is_found_false_not_error(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(MISSING_PAGE_RESPONSE))
        )
        result = self.tool.execute(mode="details", title="No Such Page Zzzq 12345")
        self.assertNotIn("error", result)
        self.assertFalse(result["found"])
        self.assertEqual(result["extract"], "")
        self.assertEqual(
            result["url"],
            "https://en.wikipedia.org/wiki/No_Such_Page_Zzzq_12345",
        )

    def test_details_result_shape(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(DETAILS_RESPONSE))
        )
        result = self.tool.execute(mode="details", title="Albert Einstein")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "title",
                "language",
                "found",
                "pageid",
                "extract",
                "url",
                "redirected_from",
                "source",
            },
        )

    # ------------------------------------------------------------------ #
    # language editions
    # ------------------------------------------------------------------ #

    def test_language_edition_switching(self) -> None:
        self.transport = RecordingTransport(json_handler(SEARCH_RESPONSE))
        tool = WikipediaTool(language="zh", transport=self.transport)
        result = tool.execute(mode="search", query="阿尔伯特·爱因斯坦")

        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "zh.wikipedia.org")
        self.assertEqual(result["language"], "zh")
        self.assertEqual(
            result["results"][0]["url"],
            "https://zh.wikipedia.org/wiki/Albert_Einstein",
        )

    def test_summary_on_language_edition(self) -> None:
        self.transport = RecordingTransport(json_handler(SUMMARY_RESPONSE))
        tool = WikipediaTool(language="zh", transport=self.transport)
        tool.execute(mode="summary", title="阿尔伯特·爱因斯坦")
        request = self.transport.requests[0]
        self.assertEqual(request.url.host, "zh.wikipedia.org")
        self.assertEqual(
            request.url.path,
            "/api/rest_v1/page/summary/阿尔伯特·爱因斯坦",
        )

    def test_invalid_language_rejected_at_construction(self) -> None:
        for bad_language in ("EN", "english", "e", "../ev1l", "en.", "x"):
            with self.assertRaises(ValidationError):
                WikipediaTool(language=bad_language)

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
            lambda: self.tool.execute(mode="random"),
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

    def test_missing_title_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="summary"),
            r"title is required",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="details"),
            r"title is required",
        )

    def test_blank_and_underscore_only_title_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="summary", title="   "),
            r"title is required",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="summary", title="___"),
            r"title is required",
        )

    def test_title_wrong_type_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="summary", title=["Albert"]),
            r"title is required",
        )

    def test_overlong_title_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="summary", title="x" * 301),
            r"at most 300 characters",
        )

    def test_forbidden_title_characters_rejected(self) -> None:
        for bad_title in ("CSharp|Sharp", "a[b]", "a{b}", "a<b>", "a#b"):
            self.assertNoRequest(
                lambda bad_title=bad_title: self.tool.execute(
                    mode="summary", title=bad_title
                ),
                r"must not contain",
            )

    def test_sentences_and_chars_together_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", sentences=2, chars=200
            ),
            r"at most one of sentences and chars",
        )

    def test_out_of_range_extract_limits_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", sentences=0
            ),
            r"sentences must be between 1 and 10",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", sentences=11
            ),
            r"sentences must be between 1 and 10",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", chars=0
            ),
            r"chars must be between 1 and 1200",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", chars=1201
            ),
            r"chars must be between 1 and 1200",
        )

    def test_non_integer_extract_limits_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", sentences="two"
            ),
            r"sentences must be an integer",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="details", title="Albert Einstein", chars=True
            ),
            r"chars must be an integer",
        )

    # ------------------------------------------------------------------ #
    # runtime errors: structured payloads, never an exception
    # ------------------------------------------------------------------ #

    def test_http_error_with_mediawiki_error_body(self) -> None:
        payload = {
            "error": {
                "code": "srsearch_error",
                "info": "search expression too complex",
            }
        }
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload, status_code=400))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["mode"], "search")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 400)
        self.assertEqual(result["error"]["reason"], "srsearch_error")
        self.assertIn("search expression too complex", result["error"]["message"])

    def test_http_404_summary_returns_structured_payload(self) -> None:
        payload = {"status": 404, "type": "Internal error", "detail": "Page not found"}
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload, status_code=404))
        )
        result = self.tool.execute(mode="summary", title="No Such Page Zzzq")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 404)
        self.assertIn("Page not found", result["error"]["message"])

    def test_http_error_with_non_json_body(self) -> None:
        def handler(request):
            return httpx.Response(503, text="<html>service unavailable</html>")

        self.tool = WikipediaTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 503)

    def test_timeout_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectTimeout("timed out")

        self.tool = WikipediaTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "request_timeout")

    def test_connection_error_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectError("no route to host")

        self.tool = WikipediaTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="summary", title="Albert Einstein")
        self.assertEqual(result["error"]["type"], "request_error")
        self.assertNotIn("status_code", result["error"])

    def test_non_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, text="<html>not json</html>")

        self.tool = WikipediaTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_non_object_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, json=[1, 2, 3])

        self.tool = WikipediaTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_invalid_search_shape_returns_structured_payload(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler({"query": {"search": "nope"}}))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("'search' must be a list", result["error"]["message"])

    def test_invalid_details_shape_returns_structured_payload(self) -> None:
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler({"query": {"pages": []}}))
        )
        result = self.tool.execute(mode="details", title="Albert Einstein")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("'pages' must be a non-empty list", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # output bounding
    # ------------------------------------------------------------------ #

    def test_extract_is_bounded(self) -> None:
        payload = {
            "query": {
                "pages": [
                    {
                        "pageid": 1,
                        "ns": 0,
                        "title": "Big Page",
                        "extract": "x" * 20000,
                        "fullurl": "https://en.wikipedia.org/wiki/Big_Page",
                    }
                ]
            }
        }
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="details", title="Big Page")
        self.assertLessEqual(len(result["extract"]), 10001)

    def test_snippet_is_bounded(self) -> None:
        payload = {
            "query": {
                "searchinfo": {"totalhits": 1},
                "search": [
                    {
                        "ns": 0,
                        "title": "Long Snippet",
                        "snippet": "y" * 5000,
                    }
                ],
            }
        }
        self.tool = WikipediaTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="search", query="ml")
        self.assertLessEqual(len(result["results"][0]["snippet"]), 500)


if __name__ == "__main__":
    unittest.main()
