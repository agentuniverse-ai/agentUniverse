#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_feed_tool.py

"""Offline unit tests for FeedTool.

Every HTTP interaction goes through ``httpx.MockTransport`` — no test in
this module touches the network. A shared ``RecordingTransport`` records
every request so the suite can assert both what was sent and that
nothing was sent at all when validation must reject the input first.

The mock payloads mirror real RSS 2.0 and Atom feed shapes, including
namespaced ``content:encoded`` / ``atom:link`` elements, CDATA-wrapped
HTML, DTD/entity payloads, and redirect chains.
"""

import unittest

import httpx
from pydantic import ValidationError

from agentuniverse.agent.action.tool.common_tool.feed_tool import FeedTool

FEED_URL = "https://blog.example.com/feed.xml"

RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Example Engineering Blog</title>
    <link>https://blog.example.com/</link>
    <description>Posts from the example engineering team</description>
    <atom:link rel="self" href="https://blog.example.com/feed.xml"/>
    <item>
      <title>Post One: &amp; intro</title>
      <link>https://blog.example.com/post-1</link>
      <guid isPermaLink="true">https://blog.example.com/post-1</guid>
      <pubDate>Sat, 17 Oct 2026 09:30:00 GMT</pubDate>
      <description>First post about &lt;b&gt;agents&lt;/b&gt;.</description>
      <content:encoded><![CDATA[<p>Full <b>body</b> of post one &amp; more.</p>]]></content:encoded>
      <atom:link rel="self" href="https://blog.example.com/post-1?format=xml"/>
    </item>
    <item>
      <title>Post Two</title>
      <link>https://blog.example.com/post-2</link>
      <guid>tag:blog.example.com,2026-10-16:post-2</guid>
      <pubDate>Fri, 16 Oct 2026 18:00:00 GMT</pubDate>
      <description>Second post.</description>
    </item>
    <item>
      <title>Post Three</title>
      <link>https://blog.example.com/post-3</link>
      <guid>tag:blog.example.com,2026-10-15:post-3</guid>
      <pubDate>Not a real date</pubDate>
      <description>Third post.</description>
    </item>
  </channel>
</rss>
"""

ATOM_FEED = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Example Feed</title>
  <subtitle>Updates from the example project</subtitle>
  <link rel="self" href="https://example.org/feed.atom"/>
  <link rel="alternate" href="https://example.org/"/>
  <updated>2026-10-18T12:00:00Z</updated>
  <id>urn:uuid:60a76c80-d399-11d9-b93c-0003939e0af6</id>
  <entry>
    <title>Release 1.2</title>
    <link rel="alternate" href="https://example.org/releases/1.2"/>
    <link rel="self" href="https://example.org/releases/1.2.atom"/>
    <id>tag:example.org,2026-10-18:release-1.2</id>
    <published>2026-10-18T08:30:00Z</published>
    <updated>2026-10-18T12:00:00Z</updated>
    <summary>Version 1.2 &lt;em&gt;ships&lt;/em&gt; new tools.</summary>
    <content type="html">&lt;p&gt;Full release notes &amp;amp; details.&lt;/p&gt;</content>
  </entry>
  <entry>
    <title>Release 1.1</title>
    <link href="https://example.org/releases/1.1"/>
    <id>tag:example.org,2026-10-01:release-1.1</id>
    <updated>2026-10-01T10:00:00Z</updated>
    <summary>Version 1.1 bugfixes.</summary>
  </entry>
</feed>
"""

RDF_FEED = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel rdf:about="https://legacy.example.org/rss">
    <title>Legacy RSS 1.0 Feed</title>
    <link>https://legacy.example.org/</link>
    <description>Legacy items</description>
  </channel>
  <item rdf:about="https://legacy.example.org/item-1">
    <title>Legacy Item</title>
    <link>https://legacy.example.org/item-1</link>
    <description>An old-style item.</description>
    <dc:date>2026-10-10T00:00:00Z</dc:date>
  </item>
</rdf:RDF>
"""

DOCTYPE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rss [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<rss version="2.0"><channel><title>evil</title></channel></rss>
"""

BILLION_LAUGHS_FEED = """<?xml version="1.0"?>
<!DOCTYPE lolz [ <!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;"> ]>
<rss version="2.0"><channel><title>&lol2;</title></channel></rss>
"""

DOCTYPE_IN_COMMENT_FEED = """<?xml version="1.0"?>
<!-- <!DOCTYPE rss> mentioned in a comment -->
<rss version="2.0"><channel><title>comment</title></channel></rss>
"""

ENTITY_IN_COMMENT_FEED = """<?xml version="1.0"?>
<!-- <!ENTITY x> mentioned in a comment -->
<rss version="2.0"><channel><title>comment</title></channel></rss>
"""

HTML_BODY = "<html><body>This is not a feed at all.</body></html>"


class RecordingTransport(httpx.MockTransport):
    """MockTransport that records every request it serves."""

    def __init__(self, handler):
        self.requests = []
        super().__init__(handler)

    def handle_request(self, request):
        self.requests.append(request)
        return super().handle_request(request)


def xml_handler(body, status_code=200, content_type="application/rss+xml"):
    def handler(request):
        content = body.encode("utf-8") if isinstance(body, str) else body
        return httpx.Response(
            status_code,
            content=content,
            headers={"Content-Type": content_type},
        )

    return handler


def many_item_rss(count):
    items = "\n".join(
        f"    <item><title>Item {i}</title>"
        f"<link>https://blog.example.com/item-{i}</link>"
        f"<guid>tag:blog.example.com,2026:item-{i}</guid></item>"
        for i in range(1, count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<rss version=\"2.0\"><channel>"
        "<title>Big Feed</title><link>https://blog.example.com/</link>"
        f"{items}</channel></rss>"
    )


class FeedToolTest(unittest.TestCase):
    """Offline test cases for the RSS/Atom FeedTool."""

    def setUp(self) -> None:
        self.transport = RecordingTransport(xml_handler(RSS_FEED))
        self.tool = FeedTool(transport=self.transport)

    # ------------------------------------------------------------------ #
    # headlines mode
    # ------------------------------------------------------------------ #

    def test_headlines_rss(self) -> None:
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "blog.example.com")
        self.assertEqual(request.url.path, "/feed.xml")
        self.assertIn("xml", request.headers["accept"])
        self.assertTrue(
            request.headers["user-agent"].startswith("agentUniverse-FeedTool")
        )
        # Feeds are keyless: no credential header is sent.
        self.assertNotIn("authorization", request.headers)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "headlines")
        self.assertEqual(result["feed_url"], FEED_URL)
        self.assertEqual(result["final_url"], FEED_URL)
        self.assertEqual(result["limit"], 10)
        self.assertEqual(result["feed_type"], "rss")
        self.assertEqual(result["feed_title"], "Example Engineering Blog")
        self.assertEqual(result["feed_link"], "https://blog.example.com/")
        self.assertEqual(result["total_items"], 3)
        self.assertFalse(result["items_truncated"])
        self.assertEqual(result["returned_items"], 3)
        self.assertEqual(len(result["items"]), 3)

        first = result["items"][0]
        self.assertEqual(first["index"], 1)
        # XML entities are unescaped.
        self.assertEqual(first["title"], "Post One: & intro")
        # The plain <link> wins over the namespaced atom:link self URL.
        self.assertEqual(first["link"], "https://blog.example.com/post-1")
        # RFC 822 pubDate is normalized to ISO 8601.
        self.assertEqual(first["published"], "2026-10-17T09:30:00+00:00")
        self.assertEqual(first["guid"], "https://blog.example.com/post-1")
        self.assertEqual(result["items"][1]["index"], 2)
        self.assertEqual(result["items"][2]["index"], 3)
        # An unparseable date is kept as-is.
        self.assertEqual(result["items"][2]["published"], "Not a real date")
        self.assertTrue(result["source"].startswith("RSS 2.0 / Atom"))

    def test_headlines_result_shape(self) -> None:
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "feed_url",
                "limit",
                "final_url",
                "feed_type",
                "feed_title",
                "feed_link",
                "total_items",
                "items_truncated",
                "returned_items",
                "items",
                "source",
            },
        )
        self.assertEqual(
            set(result["items"][0].keys()),
            {"index", "title", "link", "published", "guid"},
        )

    def test_headlines_limit_is_respected(self) -> None:
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL, limit=2)
        self.assertEqual(result["returned_items"], 2)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["total_items"], 3)
        self.assertEqual(result["items"][1]["title"], "Post Two")

    def test_headlines_limit_above_item_count(self) -> None:
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL, limit=50)
        self.assertEqual(result["returned_items"], 3)

    def test_headlines_default_limit_is_ten(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(xml_handler(many_item_rss(12)))
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["returned_items"], 10)
        self.assertEqual(result["items"][0]["index"], 1)
        self.assertEqual(result["items"][9]["index"], 10)
        self.assertEqual(result["total_items"], 12)

    def test_headlines_items_capped_at_fifty(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(xml_handler(many_item_rss(55)))
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["total_items"], 55)
        self.assertTrue(result["items_truncated"])
        self.assertEqual(result["returned_items"], 10)

    def test_headlines_atom(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(ATOM_FEED, content_type="application/atom+xml")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)

        self.assertNotIn("error", result)
        self.assertEqual(result["feed_type"], "atom")
        self.assertEqual(result["feed_title"], "Atom Example Feed")
        # rel="alternate" wins over rel="self".
        self.assertEqual(result["feed_link"], "https://example.org/")
        self.assertEqual(result["total_items"], 2)

        first = result["items"][0]
        self.assertEqual(first["index"], 1)
        self.assertEqual(first["title"], "Release 1.2")
        self.assertEqual(first["link"], "https://example.org/releases/1.2")
        # Atom dates are ISO 8601; 'Z' suffix normalizes to +00:00.
        self.assertEqual(first["published"], "2026-10-18T08:30:00+00:00")
        self.assertEqual(first["guid"], "tag:example.org,2026-10-18:release-1.2")
        second = result["items"][1]
        # No <published>: falls back to <updated>.
        self.assertEqual(second["published"], "2026-10-01T10:00:00+00:00")
        # A <link> without rel is used when there is no alternate.
        self.assertEqual(second["link"], "https://example.org/releases/1.1")

    def test_headlines_rdf_rss_1_0(self) -> None:
        rdf_tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(RDF_FEED, content_type="application/rdf+xml")
            )
        )
        result = rdf_tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["feed_type"], "rss")
        self.assertEqual(result["feed_title"], "Legacy RSS 1.0 Feed")
        self.assertEqual(result["total_items"], 1)
        # dc:date is understood as the publication date.
        self.assertEqual(
            result["items"][0]["published"], "2026-10-10T00:00:00+00:00"
        )

    # ------------------------------------------------------------------ #
    # item mode
    # ------------------------------------------------------------------ #

    def test_item_by_index_rss(self) -> None:
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=1)

        self.assertEqual(len(self.transport.requests), 1)
        self.assertNotIn("error", result)
        self.assertTrue(result["found"])
        item = result["item"]
        self.assertEqual(item["index"], 1)
        self.assertEqual(item["title"], "Post One: & intro")
        self.assertEqual(item["link"], "https://blog.example.com/post-1")
        self.assertEqual(item["published"], "2026-10-17T09:30:00+00:00")
        self.assertEqual(item["guid"], "https://blog.example.com/post-1")
        # HTML in descriptions is stripped to plain text.
        self.assertEqual(item["summary"], "First post about agents.")
        # CDATA-wrapped HTML content is stripped and unescaped.
        self.assertEqual(item["content"], "Full body of post one & more.")

    def test_item_result_shape(self) -> None:
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=2)
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "feed_url",
                "index",
                "final_url",
                "feed_type",
                "feed_title",
                "found",
                "item",
                "source",
            },
        )
        self.assertEqual(
            set(result["item"].keys()),
            {
                "index",
                "title",
                "link",
                "published",
                "guid",
                "summary",
                "content",
            },
        )

    def test_item_by_guid_rss(self) -> None:
        result = self.tool.execute(
            mode="item",
            feed_url=FEED_URL,
            guid="tag:blog.example.com,2026-10-16:post-2",
        )
        self.assertNotIn("error", result)
        self.assertTrue(result["found"])
        self.assertEqual(result["guid"], "tag:blog.example.com,2026-10-16:post-2")
        self.assertEqual(result["item"]["index"], 2)
        self.assertEqual(result["item"]["title"], "Post Two")

    def test_item_by_index_atom(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(ATOM_FEED, content_type="application/atom+xml")
            )
        )
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=1)
        self.assertTrue(result["found"])
        item = result["item"]
        self.assertEqual(item["title"], "Release 1.2")
        # Escaped HTML in summary and content becomes plain text.
        self.assertEqual(item["summary"], "Version 1.2 ships new tools.")
        self.assertEqual(item["content"], "Full release notes & details.")

    def test_item_by_guid_atom(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(ATOM_FEED, content_type="application/atom+xml")
            )
        )
        result = self.tool.execute(
            mode="item",
            feed_url=FEED_URL,
            guid="tag:example.org,2026-10-01:release-1.1",
        )
        self.assertTrue(result["found"])
        self.assertEqual(result["item"]["index"], 2)
        self.assertEqual(result["item"]["content"], "")

    def test_item_index_out_of_range_is_found_false(self) -> None:
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=99)
        self.assertNotIn("error", result)
        self.assertFalse(result["found"])
        self.assertNotIn("item", result)

    def test_item_unknown_guid_is_found_false(self) -> None:
        result = self.tool.execute(
            mode="item", feed_url=FEED_URL, guid="tag:missing,2026:nope"
        )
        self.assertNotIn("error", result)
        self.assertFalse(result["found"])
        self.assertNotIn("item", result)

    def test_item_index_capped_at_parsed_fifty(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(xml_handler(many_item_rss(55)))
        )
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=51)
        self.assertFalse(result["found"])
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=50)
        self.assertTrue(result["found"])
        self.assertEqual(result["item"]["title"], "Item 50")

    # ------------------------------------------------------------------ #
    # DTD / entity guards
    # ------------------------------------------------------------------ #

    def test_doctype_with_external_entity_rejected(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(xml_handler(DOCTYPE_FEED))
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "dtd_rejected")
        self.assertIn("<!DOCTYPE", result["error"]["message"])
        self.assertNotIn("items", result)

    def test_billion_laughs_entity_expansion_rejected(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(BILLION_LAUGHS_FEED, content_type="text/xml")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "dtd_rejected")
        # Both offending tokens are named in the message.
        self.assertIn("<!DOCTYPE", result["error"]["message"])
        self.assertIn("<!ENTITY", result["error"]["message"])

    def test_doctype_in_comment_also_rejected_fail_closed(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(DOCTYPE_IN_COMMENT_FEED, content_type="text/xml")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "dtd_rejected")

    def test_entity_in_comment_also_rejected_fail_closed(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(ENTITY_IN_COMMENT_FEED, content_type="text/xml")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "dtd_rejected")

    def test_case_insensitive_dtd_guard(self) -> None:
        body = (
            '<?xml version="1.0"?>\n'
            "<!doctype rss>\n"
            '<rss version="2.0"><channel><title>x</title></channel></rss>'
        )
        self.tool = FeedTool(
            transport=RecordingTransport(xml_handler(body))
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "dtd_rejected")

    # ------------------------------------------------------------------ #
    # response size limit
    # ------------------------------------------------------------------ #

    def test_response_over_byte_limit_returns_structured_payload(self) -> None:
        transport = RecordingTransport(xml_handler(many_item_rss(200)))
        tool = FeedTool(max_bytes=1024, transport=transport)
        result = tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "response_too_large")
        self.assertIn("1024", result["error"]["message"])
        self.assertEqual(len(transport.requests), 1)

    def test_response_under_byte_limit_passes(self) -> None:
        self.assertLess(len(RSS_FEED.encode("utf-8")), 4096)
        tool = FeedTool(
            max_bytes=4096,
            transport=RecordingTransport(xml_handler(RSS_FEED)),
        )
        result = tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertNotIn("error", result)
        self.assertEqual(result["returned_items"], 3)

    def test_default_byte_limit_is_two_mib(self) -> None:
        self.assertEqual(FeedTool().max_bytes, 2 * 1024 * 1024)

    # ------------------------------------------------------------------ #
    # redirects (bounded, https-only on every hop)
    # ------------------------------------------------------------------ #

    def test_single_redirect_is_followed(self) -> None:
        def handler(request):
            if request.url.path == "/moved":
                return httpx.Response(
                    301, headers={"Location": "https://blog.example.com/feed.xml"}
                )
            return httpx.Response(
                200,
                content=RSS_FEED.encode("utf-8"),
                headers={"Content-Type": "application/rss+xml"},
            )

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(
            mode="headlines", feed_url="https://blog.example.com/moved"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["final_url"], FEED_URL)
        self.assertEqual(result["feed_title"], "Example Engineering Blog")

    def test_relative_redirect_location_is_resolved(self) -> None:
        def handler(request):
            if request.url.path == "/old/feed":
                return httpx.Response(
                    302, headers={"Location": "/feed.xml"}
                )
            return httpx.Response(
                200,
                content=RSS_FEED.encode("utf-8"),
                headers={"Content-Type": "application/rss+xml"},
            )

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(
            mode="headlines", feed_url="https://blog.example.com/old/feed"
        )
        self.assertNotIn("error", result)
        self.assertEqual(result["final_url"], FEED_URL)

    def test_redirect_loop_returns_too_many_redirects(self) -> None:
        def handler(request):
            if request.url.path == "/a":
                return httpx.Response(302, headers={"Location": "/b"})
            return httpx.Response(302, headers={"Location": "/a"})

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(
            mode="headlines", feed_url="https://blog.example.com/a"
        )
        self.assertEqual(result["error"]["type"], "too_many_redirects")
        self.assertIn("3 redirects", result["error"]["message"])

    def test_redirect_to_http_is_unsafe_redirect(self) -> None:
        def handler(request):
            return httpx.Response(
                301, headers={"Location": "http://blog.example.com/feed.xml"}
            )

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "unsafe_redirect")
        self.assertIn("https", result["error"]["message"])

    def test_redirect_to_credentialed_url_is_unsafe_redirect(self) -> None:
        def handler(request):
            return httpx.Response(
                302,
                headers={"Location": "https://user:secret@blog.example.com/f"},
            )

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "unsafe_redirect")
        self.assertIn("credentials", result["error"]["message"])

    def test_redirect_without_location_is_unsafe_redirect(self) -> None:
        def handler(request):
            return httpx.Response(302)

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "unsafe_redirect")
        self.assertIn("Location", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # runtime errors: structured payloads, never an exception
    # ------------------------------------------------------------------ #

    def test_http_error_returns_structured_payload(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler("<error>gone</error>", status_code=404)
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 404)

    def test_timeout_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectTimeout("timed out")

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "request_timeout")

    def test_connection_error_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectError("no route to host")

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=1)
        self.assertEqual(result["error"]["type"], "request_error")
        self.assertNotIn("status_code", result["error"])

    def test_non_xml_content_type_returns_structured_payload(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(HTML_BODY, content_type="text/html")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("text/html", result["error"]["message"])

    def test_html_body_with_xml_content_type_is_invalid(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler("This is not a feed at all. <unclosed")
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("well-formed", result["error"]["message"])

    def test_xml_with_unexpected_root_is_invalid(self) -> None:
        self.tool = FeedTool(
            transport=RecordingTransport(
                xml_handler(
                    '<?xml version="1.0"?><html><body>x</body></html>'
                )
            )
        )
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("unexpected root element", result["error"]["message"])

    def test_empty_channel_feed_returns_no_items(self) -> None:
        body = (
            '<?xml version="1.0"?>'
            '<rss version="2.0"><channel>'
            "<title>Empty</title></channel></rss>"
        )
        self.tool = FeedTool(transport=RecordingTransport(xml_handler(body)))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertNotIn("error", result)
        self.assertEqual(result["feed_title"], "Empty")
        self.assertEqual(result["items"], [])
        self.assertEqual(result["total_items"], 0)

    def test_missing_content_type_header_still_parses(self) -> None:
        def handler(request):
            return httpx.Response(
                200, content=RSS_FEED.encode("utf-8")
            )

        self.tool = FeedTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertNotIn("error", result)
        self.assertEqual(result["returned_items"], 3)

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
            lambda: self.tool.execute(mode="subscribe", feed_url=FEED_URL),
            r"mode must be one of",
        )

    def test_missing_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="headlines"),
            r"feed_url is required",
        )

    def test_blank_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="headlines", feed_url="   "),
            r"feed_url is required",
        )

    def test_feed_url_wrong_type_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="headlines", feed_url=42),
            r"feed_url is required",
        )

    def test_http_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url="http://blog.example.com/feed.xml"
            ),
            r"must use https",
        )

    def test_ftp_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url="ftp://blog.example.com/feed.xml"
            ),
            r"must use https",
        )

    def test_credentialed_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines",
                feed_url="https://user:pass@blog.example.com/feed.xml",
            ),
            r"must not contain credentials",
        )

    def test_missing_host_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url="https:///feed.xml"
            ),
            r"must include a valid host",
        )

    def test_invalid_port_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url="https://blog.example.com:notaport/f"
            ),
            r"invalid port",
        )

    def test_control_characters_in_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url="https://blog.example.com/f\need"
            ),
            r"control characters",
        )

    def test_overlong_feed_url_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines",
                feed_url="https://blog.example.com/" + "x" * 2100,
            ),
            r"at most 2048 characters",
        )

    def test_out_of_range_limit_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="headlines", feed_url=FEED_URL, limit=0),
            r"limit must be between 1 and 50",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url=FEED_URL, limit=51
            ),
            r"limit must be between 1 and 50",
        )

    def test_non_integer_limit_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="headlines", feed_url=FEED_URL, limit="ten"
            ),
            r"limit must be an integer",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="headlines", feed_url=FEED_URL, limit=True),
            r"limit must be an integer",
        )

    def test_item_mode_requires_selector(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", feed_url=FEED_URL),
            r"requires either a 1-based index or a non-empty guid",
        )

    def test_index_and_guid_together_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="item", feed_url=FEED_URL, index=1, guid="tag:x,2026:a"
            ),
            r"at most one of index and guid",
        )

    def test_non_positive_index_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", feed_url=FEED_URL, index=0),
            r"index must be >= 1",
        )
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", feed_url=FEED_URL, index=-3),
            r"index must be >= 1",
        )

    def test_non_integer_index_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", feed_url=FEED_URL, index="1"),
            r"index must be an integer",
        )

    def test_blank_guid_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="item", feed_url=FEED_URL, guid="  "),
            r"non-empty guid",
        )

    def test_overlong_guid_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(
                mode="item", feed_url=FEED_URL, guid="g" * 513
            ),
            r"at most 512 characters",
        )

    def test_invalid_configuration_rejected_at_construction(self) -> None:
        for kwargs in (
            {"timeout": 0},
            {"timeout": 121},
            {"max_bytes": 512},
            {"max_bytes": 33 * 1024 * 1024},
            {"max_redirects": 0},
        ):
            with self.assertRaises(ValidationError):
                FeedTool(**kwargs)

    # ------------------------------------------------------------------ #
    # output bounding
    # ------------------------------------------------------------------ #

    def test_titles_and_summaries_are_bounded(self) -> None:
        body = (
            '<?xml version="1.0"?>'
            '<rss version="2.0"><channel><title>T</title>'
            "<item><title>" + "t" * 900 + "</title>"
            "<link>https://blog.example.com/x</link>"
            "<description>" + "d" * 9000 + "</description>"
            "<content:encoded xmlns:content=\"http://purl.org/rss/1.0/modules/content/\">"
            + "c" * 40000 + "</content:encoded></item>"
            "</channel></rss>"
        )
        self.tool = FeedTool(transport=RecordingTransport(xml_handler(body)))
        result = self.tool.execute(mode="item", feed_url=FEED_URL, index=1)
        self.assertLessEqual(len(result["item"]["title"]), 501)
        self.assertLessEqual(len(result["item"]["summary"]), 5001)
        self.assertLessEqual(len(result["item"]["content"]), 20001)

    def test_unicode_content_survives(self) -> None:
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<rss version="2.0"><channel><title>博客</title>'
            "<item><title>智能体周报</title>"
            "<link>https://blog.example.com/cn-1</link>"
            "<description>中文摘要 — 测试。</description></item>"
            "</channel></rss>"
        )
        self.tool = FeedTool(transport=RecordingTransport(xml_handler(body)))
        result = self.tool.execute(mode="headlines", feed_url=FEED_URL)
        self.assertEqual(result["feed_title"], "博客")
        self.assertEqual(result["items"][0]["title"], "智能体周报")


if __name__ == "__main__":
    unittest.main()
