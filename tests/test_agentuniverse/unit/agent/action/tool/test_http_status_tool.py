#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: test_http_status_tool.py

"""Offline unit tests for HttpStatusTool.

The tool embeds the IANA HTTP Status Code Registry and computes every
answer from local constants, so this suite runs fully offline. Every
assertion is deterministic: names are checked against a ground-truth
transcription of the registry (RFC 9110 section 15 plus the registered
extensions), retryability against the documented policy (408/429 plus
5xx except 501/505), cacheability against the RFC 9111 heuristic list,
the batch aggregates against hand-counted histograms and top lists,
and the validation matrix against the strict parameter contract
(bool traps, string codes, out-of-range values, cross-mode params).
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import HttpStatusTool
from agentuniverse.agent.action.tool.common_tool.http_status_tool import (
    HTTP_STATUS_NAMES as IANA_TABLE,
)
from agentuniverse.agent.action.tool.common_tool.http_status_tool import (
    HttpStatusTool as DirectHttpStatusTool,
)

# --------------------------------------------------------------------- #
# Ground truth: IANA HTTP Status Code Registry transcription
# (https://www.iana.org/assignments/http-status-codes/), RFC 9110
# primary names, 62 registered codes.
# --------------------------------------------------------------------- #
IANA_GROUND_TRUTH = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Content Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "(Unused)",
    421: "Misdirected Request",
    422: "Unprocessable Content",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
}

# Documented retry policy ground truth: 408/429 plus 5xx except
# 501/505 (in-range unregistered 5xx codes inherit the class policy).
RETRYABLE_TRUE = [
    408, 429,
    500, 502, 503, 504, 506, 507, 508, 510, 511,
    550, 599,  # unregistered but within the 5xx class
]
RETRYABLE_FALSE = [
    100, 200, 204, 226, 301, 302, 304, 306,
    400, 401, 403, 404, 418, 421, 425, 451,
    501, 505,
]

# RFC 9111 heuristic caching ground truth: cacheable by default.
CACHEABLE_TRUE = [
    200, 203, 204, 206, 300, 301, 308, 404, 405, 410, 414, 501,
]
CACHEABLE_FALSE = [
    100, 103, 201, 202, 205, 207, 302, 303, 304, 307,
    400, 401, 403, 408, 418, 422, 425, 429, 431, 451,
    500, 502, 503, 504, 505, 511,
    306, 480, 599,  # unregistered codes are never cacheable by default
]


class HttpStatusToolTableTest(unittest.TestCase):
    """The embedded table mirrors the IANA registry exactly."""

    def setUp(self):
        self.tool = HttpStatusTool()

    def test_iana_table_matches_ground_truth(self):
        self.assertEqual(IANA_TABLE, IANA_GROUND_TRUTH)
        self.assertEqual(len(IANA_TABLE), 62)

    def test_registered_codes_listing(self):
        self.assertEqual(self.tool.registered_codes(), sorted(IANA_GROUND_TRUTH))

    def test_spot_names(self):
        # 30 spot checks including the codes called out in review:
        # 103 Early Hints, 451 legal reasons, 425 Too Early, 508 Loop
        # Detected, plus WebDAV / RFC 6585 / RFC 9110-renamed entries.
        spots = {
            100: "Continue", 103: "Early Hints", 200: "OK",
            203: "Non-Authoritative Information", 206: "Partial Content",
            226: "IM Used", 301: "Moved Permanently", 302: "Found",
            304: "Not Modified", 308: "Permanent Redirect",
            400: "Bad Request", 404: "Not Found", 408: "Request Timeout",
            413: "Content Too Large", 418: "(Unused)",
            422: "Unprocessable Content", 425: "Too Early",
            429: "Too Many Requests", 431: "Request Header Fields Too Large",
            451: "Unavailable For Legal Reasons", 500: "Internal Server Error",
            501: "Not Implemented", 503: "Service Unavailable",
            505: "HTTP Version Not Supported", 506: "Variant Also Negotiates",
            507: "Insufficient Storage", 508: "Loop Detected",
            510: "Not Extended", 511: "Network Authentication Required",
            102: "Processing",
        }
        for code, expected_name in spots.items():
            result = self.tool.execute(mode="lookup", code=code)
            self.assertEqual(result["name"], expected_name, code)
            self.assertEqual(result["phrase"], expected_name, code)
            self.assertTrue(result["registered"], code)


class HttpStatusToolLookupTest(unittest.TestCase):
    """Full semantic records for representative codes."""

    def setUp(self):
        self.tool = HttpStatusTool()

    def test_lookup_404_full_record(self):
        result = self.tool.execute(mode="lookup", code=404)
        self.assertEqual(result["mode"], "lookup")
        self.assertEqual(result["code"], 404)
        self.assertEqual(result["name"], "Not Found")
        self.assertEqual(result["phrase"], "Not Found")
        self.assertTrue(result["registered"])
        self.assertEqual(result["category"], "4xx")
        self.assertEqual(
            result["category_description"],
            "Client Error: the request contains bad syntax or cannot be "
            "fulfilled; the client should revise the request",
        )
        self.assertFalse(result["retryable"])
        self.assertTrue(result["cacheable"])
        self.assertEqual(len(result["common_causes"]), 3)
        self.assertIn("endpoint does not exist", result["common_causes"][0])

    def test_lookup_429(self):
        result = self.tool.execute(mode="lookup", code=429)
        self.assertEqual(result["name"], "Too Many Requests")
        self.assertTrue(result["registered"])
        self.assertEqual(result["category"], "4xx")
        self.assertTrue(result["retryable"])
        self.assertFalse(result["cacheable"])
        self.assertEqual(len(result["common_causes"]), 3)
        self.assertIn("Rate limit", result["common_causes"][0])

    def test_lookup_503(self):
        result = self.tool.execute(mode="lookup", code=503)
        self.assertEqual(result["name"], "Service Unavailable")
        self.assertEqual(result["category"], "5xx")
        self.assertTrue(result["retryable"])
        self.assertFalse(result["cacheable"])
        self.assertEqual(len(result["common_causes"]), 3)

    def test_lookup_418_unused_entry(self):
        result = self.tool.execute(mode="lookup", code=418)
        self.assertEqual(result["name"], "(Unused)")
        self.assertTrue(result["registered"])
        self.assertFalse(result["retryable"])
        self.assertEqual(result["common_causes"], [])

    def test_lookup_informational_and_success_reasons(self):
        self.assertIn(
            "informational",
            self.tool.execute(mode="lookup", code=100)["retry_reason"],
        )
        self.assertIn(
            "nothing to retry",
            self.tool.execute(mode="lookup", code=200)["retry_reason"],
        )
        self.assertIn(
            "follow the Location",
            self.tool.execute(mode="lookup", code=302)["retry_reason"],
        )
        self.assertIn(
            "must be changed",
            self.tool.execute(mode="lookup", code=400)["retry_reason"],
        )

    def test_lookup_unassigned_codes_keep_class_semantics(self):
        # 599: in range but unregistered — a retryable 5xx by class.
        result = self.tool.execute(mode="lookup", code=599)
        self.assertEqual(result["name"], "Unassigned")
        self.assertEqual(result["phrase"], "")
        self.assertFalse(result["registered"])
        self.assertEqual(result["category"], "5xx")
        self.assertTrue(result["retryable"])
        self.assertIn("unregistered code", result["retry_reason"])
        self.assertFalse(result["cacheable"])
        self.assertEqual(result["common_causes"], [])
        # 306: unregistered 3xx — redirect semantics, never retried.
        result = self.tool.execute(mode="lookup", code=306)
        self.assertEqual(result["name"], "Unassigned")
        self.assertEqual(result["category"], "3xx")
        self.assertFalse(result["retryable"])
        self.assertIn("follow the Location", result["retry_reason"])
        # 480: unregistered 4xx — client-error semantics.
        result = self.tool.execute(mode="lookup", code=480)
        self.assertEqual(result["name"], "Unassigned")
        self.assertEqual(result["category"], "4xx")
        self.assertFalse(result["retryable"])

    def test_retryability_matrix(self):
        for code in RETRYABLE_TRUE:
            result = self.tool.execute(mode="lookup", code=code)
            self.assertTrue(result["retryable"], code)
        for code in RETRYABLE_FALSE:
            result = self.tool.execute(mode="lookup", code=code)
            self.assertFalse(result["retryable"], code)

    def test_cacheability_matrix(self):
        for code in CACHEABLE_TRUE:
            result = self.tool.execute(mode="lookup", code=code)
            self.assertTrue(result["cacheable"], code)
            self.assertIn("cacheable by default", result["cacheable_note"])
        for code in CACHEABLE_FALSE:
            result = self.tool.execute(mode="lookup", code=code)
            self.assertFalse(result["cacheable"], code)
            self.assertIn(
                "explicit freshness", result["cacheable_note"], code
            )

    def test_lookup_is_deterministic(self):
        first = self.tool.execute(mode="lookup", code=502)
        second = self.tool.execute(mode="lookup", code=502)
        self.assertEqual(first, second)


class HttpStatusToolBatchTest(unittest.TestCase):
    """Hand-counted aggregates for a mixed code list."""

    def setUp(self):
        self.tool = HttpStatusTool()
        self.codes = [200, 201, 301, 404, 404, 503, 599, 503]

    def test_batch_ground_truth(self):
        result = self.tool.execute(mode="batch", codes=self.codes)
        self.assertEqual(result["mode"], "batch")
        self.assertEqual(result["total"], 8)
        self.assertEqual(result["unique"], 6)
        self.assertEqual(
            result["category_histogram"],
            {"1xx": 0, "2xx": 2, "3xx": 1, "4xx": 2, "5xx": 3},
        )
        # Retryable entries: 503, 503, 599.
        self.assertEqual(result["retryable_count"], 3)
        self.assertEqual(result["not_retryable_count"], 5)
        # Unregistered entries: 599.
        self.assertEqual(result["unregistered_count"], 1)
        self.assertEqual(result["top_k"], 3)
        # Ties broken by ascending code: 404 before 503.
        self.assertEqual(
            result["top"],
            [
                {"code": 404, "name": "Not Found", "count": 2},
                {"code": 503, "name": "Service Unavailable", "count": 2},
                {"code": 200, "name": "OK", "count": 1},
            ],
        )

    def test_batch_top_k_variants(self):
        result = self.tool.execute(mode="batch", codes=self.codes, top_k=2)
        self.assertEqual(
            [entry["code"] for entry in result["top"]], [404, 503]
        )
        result = self.tool.execute(mode="batch", codes=self.codes, top_k=10)
        self.assertEqual(len(result["top"]), 6)
        self.assertEqual(result["top"][0]["code"], 404)
        self.assertEqual(result["top"][5]["code"], 599)

    def test_batch_single_code(self):
        result = self.tool.execute(mode="batch", codes=[418])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["unique"], 1)
        self.assertEqual(result["category_histogram"]["4xx"], 1)
        self.assertEqual(result["retryable_count"], 0)
        self.assertEqual(result["not_retryable_count"], 1)
        self.assertEqual(
            result["top"], [{"code": 418, "name": "(Unused)", "count": 1}]
        )

    def test_batch_accepts_boundary_size(self):
        result = self.tool.execute(mode="batch", codes=[200] * 10_000)
        self.assertEqual(result["total"], 10_000)
        self.assertEqual(result["unique"], 1)
        self.assertEqual(result["category_histogram"]["2xx"], 10_000)


class HttpStatusToolIsRetryableTest(unittest.TestCase):
    """Retry decisions incl. method idempotency and backoff policy."""

    def setUp(self):
        self.tool = HttpStatusTool()

    def test_503_get_is_safe_to_retry(self):
        result = self.tool.execute(mode="is_retryable", code=503, method="GET")
        self.assertTrue(result["retryable"])
        self.assertEqual(result["name"], "Service Unavailable")
        self.assertEqual(result["method"], "GET")
        self.assertTrue(result["method_idempotent"])
        self.assertTrue(result["safe_to_retry"])
        self.assertIsNone(result["idempotency_note"])
        backoff = result["backoff"]
        self.assertEqual(
            backoff["strategy"], "honor_retry_after_then_exponential_backoff"
        )
        self.assertTrue(backoff["honor_retry_after"])
        self.assertEqual(backoff["initial_seconds"], 1.0)
        self.assertEqual(backoff["multiplier"], 2.0)
        self.assertEqual(backoff["max_seconds"], 60.0)
        self.assertEqual(backoff["max_attempts"], 5)

    def test_503_post_is_not_safe_to_retry(self):
        result = self.tool.execute(
            mode="is_retryable", code=503, method="POST"
        )
        # The status is transient, but POST may have been applied.
        self.assertTrue(result["retryable"])
        self.assertFalse(result["method_idempotent"])
        self.assertFalse(result["safe_to_retry"])
        self.assertIn("POST is not idempotent", result["idempotency_note"])
        self.assertIn("idempotency key", result["idempotency_note"])

    def test_503_without_method_assumes_caution(self):
        result = self.tool.execute(mode="is_retryable", code=503)
        self.assertIsNone(result["method"])
        self.assertIsNone(result["method_idempotent"])
        self.assertTrue(result["safe_to_retry"])
        self.assertIn("idempotent", result["idempotency_note"])

    def test_429_delete_backoff_honours_retry_after(self):
        result = self.tool.execute(
            mode="is_retryable", code=429, method="DELETE"
        )
        self.assertTrue(result["retryable"])
        self.assertTrue(result["safe_to_retry"])
        self.assertTrue(result["backoff"]["honor_retry_after"])
        self.assertEqual(result["backoff"]["initial_seconds"], 1.0)

    def test_408_gets_one_immediate_retry(self):
        result = self.tool.execute(mode="is_retryable", code=408, method="PUT")
        self.assertTrue(result["retryable"])
        self.assertTrue(result["safe_to_retry"])
        self.assertEqual(
            result["backoff"]["strategy"],
            "immediate_retry_then_exponential_backoff",
        )
        self.assertFalse(result["backoff"]["honor_retry_after"])
        self.assertIn("timeout", result["reason"])

    def test_500_gets_exponential_jitter(self):
        result = self.tool.execute(mode="is_retryable", code=500, method="GET")
        self.assertTrue(result["retryable"])
        self.assertEqual(
            result["backoff"]["strategy"], "exponential_backoff_with_jitter"
        )
        self.assertEqual(result["backoff"]["initial_seconds"], 0.5)
        self.assertEqual(result["backoff"]["max_attempts"], 4)

    def test_unregistered_5xx_inherits_class_policy(self):
        result = self.tool.execute(mode="is_retryable", code=599, method="GET")
        self.assertTrue(result["retryable"])
        self.assertTrue(result["safe_to_retry"])
        self.assertIn("unregistered code", result["reason"])
        self.assertIsNotNone(result["backoff"])

    def test_501_and_505_are_never_retryable(self):
        for code in (501, 505):
            result = self.tool.execute(
                mode="is_retryable", code=code, method="GET"
            )
            self.assertFalse(result["retryable"], code)
            self.assertFalse(result["safe_to_retry"], code)
            self.assertIsNone(result["backoff"], code)
            self.assertIsNone(result["idempotency_note"], code)

    def test_client_error_with_post_has_no_retry_note(self):
        # Nothing to caveat when the status itself forbids retrying.
        result = self.tool.execute(
            mode="is_retryable", code=404, method="POST"
        )
        self.assertFalse(result["retryable"])
        self.assertFalse(result["safe_to_retry"])
        self.assertIsNone(result["backoff"])
        self.assertIsNone(result["idempotency_note"])

    def test_custom_method_token_is_valid_but_not_idempotent(self):
        result = self.tool.execute(
            mode="is_retryable", code=500, method="M-SEARCH"
        )
        self.assertEqual(result["method"], "M-SEARCH")
        self.assertFalse(result["method_idempotent"])
        self.assertFalse(result["safe_to_retry"])


class HttpStatusToolCategoryTest(unittest.TestCase):
    """Class listings against hand-counted registry slices."""

    def setUp(self):
        self.tool = HttpStatusTool()

    def test_category_counts(self):
        expected_counts = {"1xx": 4, "2xx": 10, "3xx": 8, "4xx": 29, "5xx": 11}
        for label, expected in expected_counts.items():
            result = self.tool.execute(mode="category", category=label)
            self.assertEqual(result["mode"], "category")
            self.assertEqual(result["category"], label)
            self.assertEqual(result["count"], expected, label)
            self.assertTrue(result["description"], label)
            self.assertEqual(len(result["codes"]), expected, label)

    def test_1xx_listing(self):
        result = self.tool.execute(mode="category", category="1xx")
        self.assertEqual(
            result["codes"],
            [
                {"code": 100, "name": "Continue"},
                {"code": 101, "name": "Switching Protocols"},
                {"code": 102, "name": "Processing"},
                {"code": 103, "name": "Early Hints"},
            ],
        )
        self.assertIn("Informational", result["description"])
        self.assertEqual(result["retryable"], [])

    def test_4xx_listing_bounds_and_retryable(self):
        result = self.tool.execute(mode="category", category="4xx")
        self.assertEqual(result["codes"][0], {"code": 400, "name": "Bad Request"})
        self.assertEqual(result["codes"][-1]["code"], 451)
        self.assertEqual(result["retryable"], [408, 429])

    def test_5xx_retryable_excludes_501_and_505(self):
        result = self.tool.execute(mode="category", category="5xx")
        self.assertEqual(result["codes"][0]["code"], 500)
        self.assertEqual(result["codes"][-1]["code"], 511)
        self.assertEqual(
            result["retryable"],
            [500, 502, 503, 504, 506, 507, 508, 510, 511],
        )

    def test_2xx_description(self):
        result = self.tool.execute(mode="category", category="2xx")
        self.assertTrue(result["description"].startswith("Successful:"))
        self.assertEqual(result["retryable"], [])


class HttpStatusToolValidationTest(unittest.TestCase):
    """Strict parameter contract: wrong types, ranges and cross-mode
    parameters raise ValueError before any computation."""

    def setUp(self):
        self.tool = HttpStatusTool()

    def assert_invalid(self, fragment, **kwargs):
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        self.assertIn("http_status_tool:", str(ctx.exception))
        self.assertIn(fragment, str(ctx.exception))

    # -- mode ----------------------------------------------------------- #

    def test_mode_must_be_known(self):
        for bad in (None, "nope", "LOOKUP", 123, True):
            self.assert_invalid("mode must be one of", mode=bad)

    # -- code (lookup / is_retryable) ----------------------------------- #

    def test_lookup_requires_code(self):
        self.assert_invalid("code must be an integer", mode="lookup")

    def test_code_rejects_bool_traps(self):
        for bad in (True, False):
            self.assert_invalid(
                "code must be an integer", mode="lookup", code=bad
            )

    def test_code_rejects_non_integers(self):
        for bad in (404.0, "404", [404], {"code": 404}, 404.5):
            self.assert_invalid(
                "code must be an integer", mode="lookup", code=bad
            )

    def test_code_rejects_out_of_range(self):
        for bad in (99, 600, -1, 0, 1000, 6000):
            self.assert_invalid(
                "code must be an integer", mode="is_retryable", code=bad
            )

    def test_code_accepts_boundaries(self):
        for good in (100, 599):
            result = self.tool.execute(mode="lookup", code=good)
            self.assertEqual(result["code"], good)

    # -- codes (batch) --------------------------------------------------- #

    def test_batch_requires_codes(self):
        self.assert_invalid("codes must be a non-empty list", mode="batch")

    def test_batch_rejects_non_list_codes(self):
        for bad in ("404,500", 404, {"a": 1}, None):
            self.assert_invalid("codes must be a", mode="batch", codes=bad)

    def test_batch_rejects_empty_list(self):
        self.assert_invalid(
            "codes must be a non-empty list", mode="batch", codes=[]
        )

    def test_batch_rejects_bad_elements(self):
        for bad_element in ("500", True, 99, 600, 404.0, [404], None):
            self.assert_invalid(
                "code must be an integer",
                mode="batch",
                codes=[200, bad_element],
            )

    def test_batch_rejects_oversized_list(self):
        self.assert_invalid(
            "10,000-entry limit", mode="batch", codes=[200] * 10_001
        )

    # -- top_k ----------------------------------------------------------- #

    def test_top_k_bounds(self):
        for bad in (0, 11, -1, 100, True, 2.5, "3"):
            self.assert_invalid(
                "top_k must be an integer", mode="batch",
                codes=[200], top_k=bad,
            )

    # -- method ----------------------------------------------------------- #

    def test_method_rejects_non_tokens(self):
        for bad in ("get", True, 5, "", "POST ", "POST\n", ["POST"], "post"):
            self.assert_invalid(
                "method must be an uppercase HTTP method token",
                mode="is_retryable", code=503, method=bad,
            )

    # -- category ---------------------------------------------------------- #

    def test_category_must_be_known(self):
        for bad in (None, "6xx", "client", "XX", "4XX", 4, True, "4x"):
            self.assert_invalid(
                "category must be one of", mode="category", category=bad
            )

    # -- cross-mode parameters ---------------------------------------------- #

    def test_lookup_rejects_foreign_parameters(self):
        self.assert_invalid(
            "not accepted in lookup mode",
            mode="lookup", code=404, method="GET",
        )
        self.assert_invalid(
            "not accepted in lookup mode",
            mode="lookup", code=404, category="4xx",
        )
        self.assert_invalid(
            "not accepted in lookup mode",
            mode="lookup", code=404, top_k=3,
        )
        self.assert_invalid(
            "not accepted in lookup mode",
            mode="lookup", code=404, codes=[200],
        )

    def test_is_retryable_rejects_foreign_parameters(self):
        self.assert_invalid(
            "not accepted in is_retryable mode",
            mode="is_retryable", code=503, category="5xx",
        )
        self.assert_invalid(
            "not accepted in is_retryable mode",
            mode="is_retryable", code=503, top_k=3,
        )
        self.assert_invalid(
            "not accepted in is_retryable mode",
            mode="is_retryable", code=503, codes=[503],
        )

    def test_batch_rejects_foreign_parameters(self):
        self.assert_invalid(
            "not accepted in batch mode",
            mode="batch", codes=[200], code=200,
        )
        self.assert_invalid(
            "not accepted in batch mode",
            mode="batch", codes=[200], method="GET",
        )
        self.assert_invalid(
            "not accepted in batch mode",
            mode="batch", codes=[200], category="2xx",
        )

    def test_category_rejects_foreign_parameters(self):
        self.assert_invalid(
            "not accepted in category mode",
            mode="category", category="4xx", code=404,
        )
        self.assert_invalid(
            "not accepted in category mode",
            mode="category", category="4xx", codes=[404],
        )
        self.assert_invalid(
            "not accepted in category mode",
            mode="category", category="4xx", method="GET",
        )
        self.assert_invalid(
            "not accepted in category mode",
            mode="category", category="4xx", top_k=3,
        )

    # -- error message prefix ------------------------------------------------ #

    def test_direct_import_matches_package_export(self):
        self.assertIs(DirectHttpStatusTool, HttpStatusTool)


if __name__ == "__main__":
    unittest.main()
