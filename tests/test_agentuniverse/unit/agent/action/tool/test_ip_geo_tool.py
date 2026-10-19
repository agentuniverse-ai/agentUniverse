#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_ip_geo_tool.py

"""Offline unit tests for IPGeoTool.

Every HTTP interaction goes through ``httpx.MockTransport`` — no test in
this module touches the network. A shared ``RecordingTransport`` records
every request so the suite can assert both what was sent and that nothing
was sent at all when validation must reject the input first.

The mock payloads mirror the real ipapi.co JSON response shapes
(``/{ip}/json/`` and ``/json/``), including its HTTP-200
``{"error": true, ...}`` error bodies.
"""

import unittest

import httpx

from agentuniverse.agent.action.tool.common_tool.ip_geo_tool import IPGeoTool

LOOKUP_RESPONSE = {
    "ip": "8.8.8.8",
    "network": "8.8.8.0/24",
    "version": "IPv4",
    "city": "Mountain View",
    "region": "California",
    "region_code": "CA",
    "country": "US",
    "country_name": "United States",
    "country_code": "US",
    "country_code_iso3": "USA",
    "country_capital": "Washington",
    "country_tld": ".us",
    "continent_code": "NA",
    "in_eu": False,
    "postal": "94043",
    "latitude": 37.42403,
    "longitude": -122.081665,
    "timezone": "America/Los_Angeles",
    "utc_offset": "-0700",
    "country_calling_code": "+1",
    "currency": "USD",
    "currency_name": "Dollar",
    "languages": "en-US,es-US,haw,fr",
    "country_area": 9629091.0,
    "country_population": 327167434,
    "asn": "AS15169",
    "org": "GOOGLE",
}

LOOKUP_RESPONSE_WITH_HOSTNAME = dict(LOOKUP_RESPONSE, hostname="dns.google")

IPV6_RESPONSE = {
    "ip": "2606:4700:4700::1111",
    "version": "IPv6",
    "city": "Ashburn",
    "region": "Virginia",
    "region_code": "VA",
    "country": "US",
    "country_name": "United States",
    "continent_code": "NA",
    "latitude": 39.04372,
    "longitude": -77.48749,
    "timezone": "America/New_York",
    "asn": "AS13335",
    "org": "CLOUDFLARENET",
}

SELF_RESPONSE = {
    "ip": "203.0.113.24",
    "version": "IPv4",
    "city": "Frankfurt am Main",
    "region": "Hesse",
    "region_code": "HE",
    "country": "DE",
    "country_name": "Germany",
    "continent_code": "EU",
    "timezone": "Europe/Berlin",
    "asn": "AS3320",
    "org": "Deutsche Telekom AG",
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


class IPGeoToolTest(unittest.TestCase):
    """Offline test cases for the keyless ipapi.co-backed IPGeoTool."""

    def setUp(self) -> None:
        self.transport = RecordingTransport(json_handler({}))
        self.tool = IPGeoTool(transport=self.transport)

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    def test_lookup_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(LOOKUP_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)

        result = self.tool.execute(mode="lookup", ip="8.8.8.8")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "ipapi.co")
        self.assertEqual(request.url.path, "/8.8.8.8/json/")
        # The lookup endpoint is a plain GET with no query parameters.
        self.assertEqual(list(request.url.params.keys()), [])
        # ipapi.co is keyless: no credential parameter is ever sent.
        self.assertNotIn("key", request.url.params)
        self.assertNotIn("apiKey", request.url.params)
        self.assertNotIn("token", request.url.params)

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "lookup")
        self.assertEqual(result["ip"], "8.8.8.8")
        self.assertEqual(result["city"], "Mountain View")
        self.assertEqual(result["region"], "California")
        self.assertEqual(result["country_name"], "United States")
        self.assertEqual(result["org"], "GOOGLE")
        self.assertEqual(result["asn"], "AS15169")
        self.assertEqual(result["timezone"], "America/Los_Angeles")
        self.assertTrue(result["source"].startswith("ipapi.co"))
        # The ~19 other response fields are trimmed away.
        self.assertNotIn("latitude", result)
        self.assertNotIn("longitude", result)
        self.assertNotIn("postal", result)
        self.assertNotIn("languages", result)
        self.assertNotIn("country_population", result)
        self.assertNotIn("network", result)
        self.assertNotIn("version", result)

    def test_lookup_result_shape(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(LOOKUP_RESPONSE))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "ip",
                "city",
                "region",
                "country_name",
                "org",
                "asn",
                "timezone",
                "source",
            },
        )

    def test_lookup_result_shape_with_reverse(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(LOOKUP_RESPONSE_WITH_HOSTNAME))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8", reverse=True)
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "ip",
                "city",
                "region",
                "country_name",
                "org",
                "asn",
                "timezone",
                "hostname",
                "source",
            },
        )

    def test_lookup_ipv6_address_is_normalized(self) -> None:
        self.transport = RecordingTransport(json_handler(IPV6_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)

        result = self.tool.execute(
            mode="lookup", ip="2606:4700:4700:0000:0000:0000:0000:1111"
        )

        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "ipapi.co")
        # The longhand IPv6 form is requested in canonical compressed form.
        self.assertEqual(request.url.path, "/2606:4700:4700::1111/json/")
        self.assertNotIn("error", result)
        self.assertEqual(result["ip"], "2606:4700:4700::1111")
        self.assertEqual(result["org"], "CLOUDFLARENET")

    def test_lookup_integer_ip(self) -> None:
        self.transport = RecordingTransport(json_handler(LOOKUP_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)
        # 134744072 is 8.8.8.8 in host byte order.
        self.tool.execute(mode="lookup", ip=134744072)
        self.assertEqual(self.transport.requests[0].url.path, "/8.8.8.8/json/")

    def test_lookup_strips_surrounding_whitespace(self) -> None:
        self.transport = RecordingTransport(json_handler(LOOKUP_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)
        self.tool.execute(mode="lookup", ip="  8.8.8.8  ")
        self.assertEqual(self.transport.requests[0].url.path, "/8.8.8.8/json/")

    def test_lookup_reverse_keeps_hostname(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(LOOKUP_RESPONSE_WITH_HOSTNAME))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8", reverse=True)
        self.assertNotIn("error", result)
        self.assertEqual(result["hostname"], "dns.google")

    def test_lookup_reverse_true_hostname_absent(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(LOOKUP_RESPONSE))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8", reverse=True)
        self.assertNotIn("error", result)
        # Deterministic shape: hostname is empty when the API omits it.
        self.assertEqual(result["hostname"], "")

    def test_lookup_reverse_false_drops_hostname(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(LOOKUP_RESPONSE_WITH_HOSTNAME))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertNotIn("error", result)
        self.assertNotIn("hostname", result)

    def test_lookup_falls_back_to_requested_ip_when_response_omits_it(self) -> None:
        payload = {k: v for k, v in LOOKUP_RESPONSE.items() if k != "ip"}
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertNotIn("error", result)
        self.assertEqual(result["ip"], "8.8.8.8")

    # ------------------------------------------------------------------ #
    # self mode
    # ------------------------------------------------------------------ #

    def test_self_mode(self) -> None:
        self.transport = RecordingTransport(json_handler(SELF_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)

        result = self.tool.execute(mode="self")

        self.assertEqual(len(self.transport.requests), 1)
        request = self.transport.requests[0]
        self.assertEqual(request.url.scheme, "https")
        self.assertEqual(request.url.host, "ipapi.co")
        self.assertEqual(request.url.path, "/json/")
        self.assertEqual(list(request.url.params.keys()), [])

        self.assertNotIn("error", result)
        self.assertEqual(result["mode"], "self")
        self.assertEqual(result["ip"], "203.0.113.24")
        self.assertEqual(result["city"], "Frankfurt am Main")
        self.assertEqual(result["region"], "Hesse")
        self.assertEqual(result["country_name"], "Germany")
        self.assertEqual(result["org"], "Deutsche Telekom AG")
        self.assertEqual(result["asn"], "AS3320")
        self.assertEqual(result["timezone"], "Europe/Berlin")

    def test_self_result_shape(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(SELF_RESPONSE))
        )
        result = self.tool.execute(mode="self")
        self.assertEqual(
            set(result.keys()),
            {
                "mode",
                "ip",
                "city",
                "region",
                "country_name",
                "org",
                "asn",
                "timezone",
                "source",
            },
        )

    def test_self_mode_ignores_ip_argument(self) -> None:
        self.transport = RecordingTransport(json_handler(SELF_RESPONSE))
        self.tool = IPGeoTool(transport=self.transport)
        self.tool.execute(mode="self", ip="8.8.8.8")
        self.assertEqual(self.transport.requests[0].url.path, "/json/")

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
            lambda: self.tool.execute(mode="geolocate"),
            r"mode must be one of",
        )

    def test_missing_ip_in_lookup_rejected(self) -> None:
        for missing in (None, "", "   "):
            self.assertNoRequest(
                lambda missing=missing: self.tool.execute(
                    mode="lookup", ip=missing
                ),
                r"ip is required in lookup mode",
            )

    def test_malformed_ip_rejected(self) -> None:
        for bad_ip in (
            "not-an-ip",
            "8.8.8.256",
            "8.8.8",
            "999.1.1.1",
            "8.8.8.8/24",
            "8.8.8.8:80",
            "http://8.8.8.8",
            "8.8.8.8/../../etc/passwd",
            "010.1.1.1",
            "::gg::1",
            "8.8.8.8 xyz",
        ):
            self.assertNoRequest(
                lambda bad_ip=bad_ip: self.tool.execute(mode="lookup", ip=bad_ip),
                r"ip is not a valid IPv4 or IPv6 address",
            )

    def test_wrong_type_ip_rejected(self) -> None:
        for bad_ip in (42.5, ["8.8.8.8"], {"ip": "8.8.8.8"}, True, False):
            self.assertNoRequest(
                lambda bad_ip=bad_ip: self.tool.execute(mode="lookup", ip=bad_ip),
                r"ip is required in lookup mode",
            )

    def test_out_of_range_integer_ip_rejected(self) -> None:
        self.assertNoRequest(
            lambda: self.tool.execute(mode="lookup", ip=2**128),
            r"ip is not a valid IPv4 or IPv6 address",
        )

    def test_invalid_reverse_type_rejected(self) -> None:
        for bad_reverse in ("yes", 1, None):
            self.assertNoRequest(
                lambda bad_reverse=bad_reverse: self.tool.execute(
                    mode="self", reverse=bad_reverse
                ),
                r"reverse must be a boolean",
            )

    # ------------------------------------------------------------------ #
    # non-routable addresses: structured payload, never a request
    # ------------------------------------------------------------------ #

    def assertReserved(self, ip, reason_pattern=None):
        result = self.tool.execute(mode="lookup", ip=ip)
        self.assertEqual(
            self.transport.requests,
            [],
            f"no request may be sent for non-routable address {ip}",
        )
        self.assertEqual(result["mode"], "lookup")
        self.assertEqual(result["ip"], ip)
        self.assertEqual(result["error"]["type"], "reserved_ip")
        self.assertIn(ip, result["error"]["message"])
        self.assertIn("source", result)
        if reason_pattern is not None:
            self.assertRegex(result["error"]["reason"], reason_pattern)

    def test_private_ipv4_rejected_with_payload(self) -> None:
        self.assertReserved("192.168.1.1", reason_pattern=r"private")
        self.assertReserved("10.0.0.1", reason_pattern=r"private")
        self.assertReserved("172.16.0.1", reason_pattern=r"private")

    def test_reserved_scope_ipv4_rejected_with_payload(self) -> None:
        self.assertReserved("127.0.0.1", reason_pattern=r"loopback")
        self.assertReserved("169.254.1.1", reason_pattern=r"link_local")
        self.assertReserved("0.0.0.0", reason_pattern=r"unspecified")
        self.assertReserved("224.0.0.1", reason_pattern=r"multicast")
        self.assertReserved("240.0.0.1")

    def test_non_routable_ipv6_rejected_with_payload(self) -> None:
        self.assertReserved("::1", reason_pattern=r"loopback")
        self.assertReserved("fe80::1", reason_pattern=r"link_local")
        self.assertReserved("fc00::1")
        self.assertReserved("2001:db8::1")
        self.assertReserved("ff02::1", reason_pattern=r"multicast")

    def test_reserved_payload_shape(self) -> None:
        result = self.tool.execute(mode="lookup", ip="192.168.1.1")
        self.assertEqual(self.transport.requests, [])
        self.assertEqual(
            set(result.keys()), {"mode", "ip", "error", "source"}
        )
        self.assertEqual(
            set(result["error"].keys()), {"type", "message", "reason"}
        )

    # ------------------------------------------------------------------ #
    # runtime errors: structured payloads, never an exception
    # ------------------------------------------------------------------ #

    def test_api_error_body_with_http_200(self) -> None:
        payload = {
            "error": True,
            "reason": "Reserved IP Address",
            "ip": "127.0.0.1",
            "reserved": True,
        }
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(result["mode"], "lookup")
        self.assertEqual(result["error"]["type"], "api_error")
        self.assertEqual(result["error"]["reason"], "Reserved IP Address")
        self.assertIn("Reserved IP Address", result["error"]["message"])

    def test_api_error_body_without_reason(self) -> None:
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler({"error": True}))
        )
        result = self.tool.execute(mode="self")
        self.assertEqual(result["error"]["type"], "api_error")
        self.assertNotIn("reason", result["error"])
        self.assertIn("rejected the lookup", result["error"]["message"])

    def test_http_429_rate_limited(self) -> None:
        payload = {
            "error": True,
            "reason": "RateLimited",
            "message": "You have exceeded your quota",
        }
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload, status_code=429))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 429)
        self.assertEqual(result["error"]["reason"], "RateLimited")
        self.assertIn("quota", result["error"]["message"])

    def test_http_404_text_body_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(404, text="URL Not Found")

        self.tool = IPGeoTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(result["error"]["type"], "http_error")
        self.assertEqual(result["error"]["status_code"], 404)
        self.assertNotIn("reason", result["error"])

    def test_timeout_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectTimeout("timed out")

        self.tool = IPGeoTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(result["error"]["type"], "request_timeout")

    def test_connection_error_returns_structured_payload(self) -> None:
        def handler(request):
            raise httpx.ConnectError("no route to host")

        self.tool = IPGeoTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="self")
        self.assertEqual(result["error"]["type"], "request_error")
        self.assertNotIn("status_code", result["error"])

    def test_non_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, text="<html>not json</html>")

        self.tool = IPGeoTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_non_object_json_response_returns_structured_payload(self) -> None:
        def handler(request):
            return httpx.Response(200, json=[1, 2, 3])

        self.tool = IPGeoTool(transport=RecordingTransport(handler))
        result = self.tool.execute(mode="self")
        self.assertEqual(result["error"]["type"], "invalid_response")

    def test_self_response_missing_ip_returns_structured_payload(self) -> None:
        payload = {"city": "Nowhere", "country_name": "NA"}
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="self")
        self.assertEqual(result["error"]["type"], "invalid_response")
        self.assertIn("missing 'ip'", result["error"]["message"])

    # ------------------------------------------------------------------ #
    # output bounding
    # ------------------------------------------------------------------ #

    def test_fields_are_bounded(self) -> None:
        payload = dict(LOOKUP_RESPONSE, org="x" * 5000, city="y" * 5000)
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertLessEqual(len(result["org"]), 301)
        self.assertLessEqual(len(result["city"]), 301)

    def test_non_string_fields_coerce_to_empty(self) -> None:
        payload = dict(LOOKUP_RESPONSE, city=None, asn=15169, org=["GOOGLE"])
        self.tool = IPGeoTool(
            transport=RecordingTransport(json_handler(payload))
        )
        result = self.tool.execute(mode="lookup", ip="8.8.8.8")
        self.assertNotIn("error", result)
        self.assertEqual(result["city"], "")
        self.assertEqual(result["asn"], "")
        self.assertEqual(result["org"], "")


if __name__ == "__main__":
    unittest.main()
