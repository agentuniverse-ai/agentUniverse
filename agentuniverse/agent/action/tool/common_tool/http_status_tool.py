#!/usr/bin/env python3

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: http_status_tool.py

"""HTTP status-code semantics tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency knowledge layer for
HTTP status codes: agents that call remote APIs constantly have to
decide *what a code means* and *whether/how to retry it*, and no
existing common tool provides that. This tool embeds the IANA HTTP
Status Code Registry name table and answers exactly those questions.
It is the knowledge counterpart of request-execution tools: where
``LogParserTool`` reads a status as one numeric log field, this tool
explains the number — name, category semantics, retryability,
cacheability and common causes — so an agent can drive API retry
decisions without a network lookup.

The tool supports four modes:

* ``lookup`` — one code (100..599) to its full semantic record:
  ``code``, ``name`` (the IANA-registered name, or ``"Unassigned"``
  for in-range codes the registry does not list, e.g. 599 or 306),
  ``phrase`` (the recommended reason phrase; the empty string for
  unregistered codes), ``registered``, ``category`` (``1xx``..``5xx``)
  with its RFC 9110 section-15 description, ``retryable`` (documented
  policy: 408, 429, and every 5xx except 501 and 505 — the client
  cannot fix these by editing the request), ``cacheable`` (RFC 9111
  heuristic caching rules: 200, 203, 204, 206, 300, 301, 308, 404,
  405, 410, 414 and 501 are cacheable by default, subject to the
  request method and Cache-Control) and ``common_causes`` (2-3
  diagnostic bullets for the frequent codes, empty list otherwise).
  In-range-but-unregistered codes keep their category semantics, so
  an unknown 5xx is reported as a retryable server error rather than
  an error payload.
* ``batch`` — a list of codes to aggregate fleet/log statistics:
  category histogram (``1xx``..``5xx``), retryable / not-retryable /
  unregistered counts, and the ``top`` most frequent codes (ties
  broken by ascending code; ``top_k`` 1..10, default 3).
* ``is_retryable`` — one code plus an optional HTTP ``method`` to the
  complete retry decision: the status-level ``retryable`` flag with
  its ``reason``, the method's idempotency (RFC 9110 section 9.2.2:
  GET, HEAD, PUT, DELETE, OPTIONS, TRACE are idempotent),
  ``safe_to_retry`` (false when the method is non-idempotent, e.g.
  POST, even for a transient status — the operation may already have
  been applied) and a deterministic ``backoff`` recommendation
  (429/503 honour ``Retry-After`` then back off exponentially; 408
  gets one immediate retry; other retryable 5xx use exponential
  backoff with jitter).
* ``category`` — one of ``1xx``..``5xx`` to the RFC 9110 section-15
  class description, every registered code in the class (``code`` +
  ``name``, ascending) and the retryable subset.

The embedded name table mirrors the IANA HTTP Status Code Registry
(RFC 9110 section 15 plus registered extensions: WebDAV, RFC 6585,
RFC 7725, RFC 8297, RFC 8470 and friends) as published at
https://www.iana.org/assignments/http-status-codes/ — 62 registered
codes at embedding time; 418 carries the registry's ``(Unused)``
name. Every answer is computed from these local constants: the tool
is fully offline and deterministic.

Input validation is strict and happens before any computation:
malformed parameters (wrong types including bool traps, string codes,
out-of-range codes, unknown mode / category, invalid method tokens,
empty or oversized ``codes``, ``top_k`` outside 1..10, or parameters
passed to a mode that does not accept them) raise a ``ValueError``,
mirroring the other common tools. There are no content-level failure
paths: every in-range code has category semantics, so ``lookup``
never needs an error payload.
"""

import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# --------------------------------------------------------------------- #
# Embedded IANA HTTP Status Code Registry (RFC 9110 section 15 plus
# registered extensions: WebDAV RFC 4918/5842, RFC 6585, RFC 7725,
# RFC 8297, RFC 8470, RFC 2774, RFC 3229). Source:
# https://www.iana.org/assignments/http-status-codes/ — 62 codes.
# Names follow the registry's current (RFC 9110) primary names, e.g.
# 413 "Content Too Large" (formerly "Payload Too Large") and 422
# "Unprocessable Content" (formerly "Unprocessable Entity"); 418 keeps
# the registry's "(Unused)" entry.
# --------------------------------------------------------------------- #
HTTP_STATUS_NAMES: dict[int, str] = {
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

# RFC 9110 section 15 class descriptions.
CATEGORY_DESCRIPTIONS: dict[str, str] = {
    "1xx": (
        "Informational: the request was received and processing "
        "continues (interim response)"
    ),
    "2xx": "Successful: the request was received, understood and accepted",
    "3xx": (
        "Redirection: further action is needed to complete the request"
    ),
    "4xx": (
        "Client Error: the request contains bad syntax or cannot be "
        "fulfilled; the client should revise the request"
    ),
    "5xx": (
        "Server Error: the server failed to fulfil an apparently "
        "valid request"
    ),
}

# Documented retry policy: client-visible transient conditions only —
# 408 (request timeout, may not have been processed), 429 (rate
# limited, retry after the indicated delay) and the 5xx class (server
# fault) except 501 (missing functionality) and 505 (wrong protocol
# version), which no amount of retrying fixes. In-range unregistered
# 5xx codes (e.g. 599) inherit the class policy.
NEVER_RETRYABLE: frozenset[int] = frozenset({501, 505})
ALWAYS_RETRYABLE: frozenset[int] = frozenset({408, 429})

# RFC 9111 (HTTP Caching) heuristic caching rules: responses with
# these status codes are cacheable by default (absent Cache-Control,
# and only for heuristically cacheable request methods); anything
# else needs explicit freshness information to be stored.
CACHEABLE_BY_DEFAULT: frozenset[int] = frozenset(
    {
        200, 203, 204, 206, 300, 301, 308,
        404, 405, 410, 414, 501,
    }
)

# RFC 9110 section 9.2.2 idempotent methods.
IDEMPOTENT_METHODS: frozenset[str] = frozenset(
    {"GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE"}
)

# Method tokens: case-sensitive uppercase HTTP method names (RFC 9110
# section 9.1), letters first then letters/digits/hyphens. Anchored
# with \Z (not $) so a trailing newline cannot sneak past the pattern.
_METHOD_RE = re.compile(r"[A-Z][A-Z0-9-]*\Z")

# Deterministic backoff recommendations per retryability class.
RETRY_AFTER_BACKOFF: dict[str, Any] = {
    "strategy": "honor_retry_after_then_exponential_backoff",
    "initial_seconds": 1.0,
    "multiplier": 2.0,
    "max_seconds": 60.0,
    "max_attempts": 5,
    "honor_retry_after": True,
}
EXPONENTIAL_JITTER_BACKOFF: dict[str, Any] = {
    "strategy": "exponential_backoff_with_jitter",
    "initial_seconds": 0.5,
    "multiplier": 2.0,
    "max_seconds": 30.0,
    "max_attempts": 4,
    "honor_retry_after": True,
}
IMMEDIATE_THEN_BACKOFF: dict[str, Any] = {
    "strategy": "immediate_retry_then_exponential_backoff",
    "initial_seconds": 0.5,
    "multiplier": 2.0,
    "max_seconds": 30.0,
    "max_attempts": 4,
    "honor_retry_after": False,
}

# Common-cause diagnostics for the frequent codes (2-3 bullets,
# deterministic); codes outside this map get an empty list.
COMMON_CAUSES: dict[int, tuple[str, ...]] = {
    301: (
        "The resource permanently moved (site migration, canonical URL change) and the Location header points at the new URI.",
        "www/non-www or trailing-slash normalization at the server or CDN.",
        "Old bookmarks, cached links or hardcoded URLs still targeting the previous location.",
    ),
    302: (
        "Temporarily relocated content (maintenance window, A/B test, geo routing).",
        "Post/Redirect/Get flow after a successful form submission.",
        "Load balancer or auth layer bouncing this one request to another endpoint.",
    ),
    304: (
        "Conditional request matched: the If-None-Match ETag or If-Modified-Since date equals the current representation.",
        "An intermediary cache revalidated a still-fresh response on the client's behalf.",
    ),
    400: (
        "Malformed request syntax (invalid JSON body, broken URL encoding, oversized headers or cookies).",
        "A required parameter is missing or has the wrong type or format.",
        "An HTTP protocol violation the server refuses to interpret.",
    ),
    401: (
        "Missing or expired credentials (API key, bearer token, session cookie).",
        "Token present but invalid, revoked, or signed for another audience.",
        "The authentication challenge in WWW-Authenticate was never completed.",
    ),
    403: (
        "Authenticated identity lacks permission for the resource (scope or role mismatch).",
        "WAF rule, IP allowlist or geo-block rejecting the client.",
        "Server policy refuses to reveal whether the resource exists.",
    ),
    404: (
        "Wrong or mistyped path — the endpoint does not exist under this base URL.",
        "The resource was deleted or never existed.",
        "The route is registered under a different method or parameter shape, so no handler matches.",
    ),
    405: (
        "The HTTP verb is not supported by the route (e.g. PUT on a read-only resource).",
        "The route was registered without the method, or a gateway rewrote the verb.",
        "Using the collection endpoint where the item endpoint is required, or vice versa.",
    ),
    408: (
        "The client was too slow transmitting the request body (large upload on a poor link).",
        "The connection was established but the request never completed within the server's timeout.",
        "A middlebox or proxy enforcing a shorter request timeout than the client needs.",
    ),
    409: (
        "Concurrent update conflict (optimistic locking / ETag mismatch / version clash).",
        "Creating a resource that already exists (unique key or duplicate id).",
        "The request state conflicts with the resource's current state (e.g. merging an already-merged record).",
    ),
    410: (
        "The resource was intentionally and permanently removed (deprecated API version).",
        "The server deliberately distinguishes permanent removal from unknown paths.",
        "Content was taken down and the provider signals clients to purge links and caches.",
    ),
    422: (
        "The payload is syntactically valid (it parses) but fails semantic validation rules.",
        "Wrong field types or values outside the allowed domain.",
        "Fields required by business logic are missing although the schema shape matched.",
    ),
    429: (
        "Rate limit or quota exceeded — too many requests in the window.",
        "Bursty traffic pattern (retry storms, thundering herd, too many parallel workers).",
        "The client ignored Retry-After / backoff from previous 429 responses.",
    ),
    451: (
        "Resource unavailable for legal reasons — takedown notice, court order or licensing restriction.",
        "Geo-blocking enforced for regulatory compliance (e.g. regional privacy law).",
        "Government censorship or export-control filtering in the client's jurisdiction.",
    ),
    500: (
        "Unhandled exception or bug in the server application code.",
        "Bad deployment, configuration or environment (missing secrets, broken build).",
        "A downstream dependency failing in a way the application did not anticipate.",
    ),
    502: (
        "The upstream server returned an invalid or empty response the gateway could not parse.",
        "The upstream crashed or is restarting (connection reset mid-request).",
        "The gateway cannot reach the backend (wrong DNS or port, network partition).",
    ),
    503: (
        "Server overloaded — connection or thread pools exhausted under load.",
        "Planned maintenance, or the service is starting up / draining.",
        "A hard dependency (database, auth provider) is unavailable.",
    ),
    504: (
        "The upstream did not answer within the gateway's timeout window.",
        "A slow query or expensive request path exceeding the configured budget.",
        "Network latency or packet loss between the proxy tier and the backend.",
    ),
}


class HttpStatusTool(Tool):
    """HTTP status-code semantics tool built purely on the stdlib.

    The tool embeds the IANA HTTP Status Code Registry name table and
    answers status-code questions offline: what a code is called, what
    its class means, whether it should be retried (and with what
    backoff and method-idempotency caveats), whether a response with
    it is cacheable by default, and what commonly causes it.

    Attributes:
        max_batch_codes (int): Upper bound on the number of codes
            accepted by ``batch`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "http_status_tool"
    description: str = (
        "HTTP status-code semantics tool — pure stdlib with the IANA "
        "status registry embedded, no network required. Look up one "
        "code's full record (mode='lookup': IANA name or 'Unassigned', "
        "reason phrase, 1xx-5xx category with RFC 9110 meaning, "
        "retryability policy 408/429 + 5xx-except-501/505, RFC 9111 "
        "default cacheability, common causes), aggregate a list of "
        "codes (mode='batch': category histogram, retryable and "
        "unregistered counts, top codes), get the complete retry "
        "decision for a code and optional method (mode='is_retryable': "
        "retryable + reason, RFC 9110 method idempotency, safe_to_retry "
        "with a POST note, deterministic backoff recommendation), and "
        "list a class (mode='category': all registered codes of "
        "1xx-5xx plus the class description)."
    )

    MODES: ClassVar[tuple] = ("lookup", "batch", "is_retryable", "category")
    CATEGORIES: ClassVar[tuple] = ("1xx", "2xx", "3xx", "4xx", "5xx")

    max_batch_codes: ClassVar[int] = 10_000
    max_top_k: ClassVar[int] = 10
    default_top_k: ClassVar[int] = 3

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        code: Any = None,
        codes: Any = None,
        method: Any = None,
        category: Any = None,
        top_k: Any = None,
    ) -> dict[str, Any]:
        """Run one status-code semantics operation.

        Args:
            mode (str): One of ``lookup`` / ``batch`` / ``is_retryable``
                / ``category``.
            code (int): Single status code (100..599) for ``lookup``
                and ``is_retryable``.
            codes (list[int]): Status codes (100..599 each) for
                ``batch``; duplicates count once per occurrence.
            method (str): Optional HTTP method (uppercase token, e.g.
                ``GET``, ``POST``) for ``is_retryable``.
            category (str): One of ``1xx``..``5xx`` for ``category``.
            top_k (int): ``batch`` only — how many top codes to report
                (1..10, default 3, ties broken by ascending code).

        Returns:
            Dict[str, Any]: The operation result (semantic record for
            ``lookup``, histogram plus counts and top codes for
            ``batch``, retry decision for ``is_retryable``, class
            listing for ``category``).

        Raises:
            ValueError: If any parameter is malformed or belongs to a
            different mode (before any computation happens).
        """
        if not isinstance(mode, str) or mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "lookup":
            clean_code = self._validate_code(code)
            self._reject_params(
                "lookup",
                ("method", method),
                ("category", category),
                ("top_k", top_k),
                ("codes", codes),
            )
            return self._run_lookup(clean_code)
        if mode == "is_retryable":
            clean_code = self._validate_code(code)
            clean_method = self._validate_method(method)
            self._reject_params(
                "is_retryable",
                ("category", category),
                ("top_k", top_k),
                ("codes", codes),
            )
            return self._run_is_retryable(clean_code, clean_method)
        if mode == "batch":
            self._reject_params(
                "batch",
                ("code", code),
                ("method", method),
                ("category", category),
            )
            clean_codes = self._validate_codes(codes)
            clean_top_k = self._validate_top_k(top_k)
            return self._run_batch(clean_codes, clean_top_k)
        # category mode
        self._reject_params(
            "category",
            ("code", code),
            ("codes", codes),
            ("method", method),
            ("top_k", top_k),
        )
        return self._run_category(category)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"http_status_tool: {message}")

    @classmethod
    def _validate_code(cls, code: Any) -> int:
        """Validate a single status code (int, not bool, 100..599)."""
        if (
            isinstance(code, bool)
            or not isinstance(code, int)
            or not 100 <= code <= 599
        ):
            cls._invalid(
                f"code must be an integer HTTP status code between "
                f"100 and 599 (got {code!r})"
            )
        return code

    @classmethod
    def _validate_codes(cls, codes: Any) -> list[int]:
        """Validate the batch-mode ``codes`` list (non-empty, bounded)."""
        if codes is None:
            cls._invalid("codes must be a non-empty list of status codes")
        if isinstance(codes, (str, bytes, dict)) or not isinstance(
            codes, (list, tuple)
        ):
            cls._invalid(
                f"codes must be a list of integer status codes (got {codes!r})"
            )
        if len(codes) == 0:
            cls._invalid("codes must be a non-empty list of status codes")
        if len(codes) > cls.max_batch_codes:
            cls._invalid(
                f"codes exceeds the {cls.max_batch_codes:,}-entry limit "
                f"(got {len(codes):,} entries)"
            )
        return [cls._validate_code(item) for item in codes]

    @classmethod
    def _validate_method(cls, method: Any) -> str | None:
        """Validate the optional uppercase HTTP method token."""
        if method is None:
            return None
        if (
            isinstance(method, bool)
            or not isinstance(method, str)
            or not _METHOD_RE.match(method)
        ):
            cls._invalid(
                "method must be an uppercase HTTP method token "
                f"(e.g. GET, POST; got {method!r})"
            )
        return method

    @classmethod
    def _validate_top_k(cls, top_k: Any) -> int:
        """Validate the batch-mode ``top_k`` bound."""
        if top_k is None:
            return cls.default_top_k
        if (
            isinstance(top_k, bool)
            or not isinstance(top_k, int)
            or not 1 <= top_k <= cls.max_top_k
        ):
            cls._invalid(
                f"top_k must be an integer between 1 and {cls.max_top_k} "
                f"(got {top_k!r})"
            )
        return top_k

    @classmethod
    def _reject_params(cls, mode: str, *params: tuple[str, Any]) -> None:
        """Reject parameters that do not belong to ``mode``."""
        given = [
            (name, value) for name, value in params if value is not None
        ]
        if given:
            names = ", ".join(name for name, _ in given)
            cls._invalid(
                f"parameters ({names}) are not accepted in {mode} mode"
            )

    # ------------------------------------------------------------------ #
    # Shared semantics helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _category_of(code: int) -> str:
        """Map a code to its ``1xx``..``5xx`` class label."""
        return f"{code // 100}xx"

    # ------------------------------------------------------------------ #
    # lookup mode
    # ------------------------------------------------------------------ #

    def _run_lookup(self, code: int) -> dict[str, Any]:
        """Build the full semantic record for one code."""
        return {
            "mode": "lookup",
            "code": code,
            "name": self._name_of(code),
            "phrase": self._phrase_of(code),
            "registered": code in HTTP_STATUS_NAMES,
            "category": self._category_of(code),
            "category_description": CATEGORY_DESCRIPTIONS[
                self._category_of(code)
            ],
            "retryable": self._retryable(code),
            "retry_reason": self._retry_reason(code),
            "cacheable": self._cacheable(code),
            "cacheable_note": self._cacheable_note(code),
            "common_causes": list(COMMON_CAUSES.get(code, ())),
        }

    @staticmethod
    def _name_of(code: int) -> str:
        """IANA name, or 'Unassigned' for unregistered codes."""
        return HTTP_STATUS_NAMES.get(code, "Unassigned")

    @staticmethod
    def _phrase_of(code: int) -> str:
        """Recommended reason phrase ('' when unregistered)."""
        return HTTP_STATUS_NAMES.get(code, "")

    @staticmethod
    def _cacheable(code: int) -> bool:
        """RFC 9111 heuristic cacheability of one status code."""
        return code in CACHEABLE_BY_DEFAULT

    @staticmethod
    def _cacheable_note(code: int) -> str:
        """Explain the cacheability flag for one status code."""
        if code in CACHEABLE_BY_DEFAULT:
            return (
                "cacheable by default under the RFC 9111 heuristic "
                "caching rules (subject to the request method and "
                "Cache-Control)"
            )
        return (
            "not heuristically cacheable; storing it requires explicit "
            "freshness information (e.g. Cache-Control: max-age) per "
            "RFC 9111"
        )

    # ------------------------------------------------------------------ #
    # batch mode
    # ------------------------------------------------------------------ #

    def _run_batch(
        self, codes: list[int], top_k: int
    ) -> dict[str, Any]:
        """Aggregate a code list into a histogram and top codes."""
        histogram = {label: 0 for label in self.CATEGORIES}
        counts: dict[int, int] = {}
        retryable_count = 0
        unregistered_count = 0
        for code in codes:
            histogram[self._category_of(code)] += 1
            counts[code] = counts.get(code, 0) + 1
            if self._retryable(code):
                retryable_count += 1
            if code not in HTTP_STATUS_NAMES:
                unregistered_count += 1
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        top = [
            {
                "code": code,
                "name": self._name_of(code),
                "count": count,
            }
            for code, count in ranked[:top_k]
        ]
        return {
            "mode": "batch",
            "total": len(codes),
            "unique": len(counts),
            "category_histogram": histogram,
            "retryable_count": retryable_count,
            "not_retryable_count": len(codes) - retryable_count,
            "unregistered_count": unregistered_count,
            "top_k": top_k,
            "top": top,
        }

    # ------------------------------------------------------------------ #
    # is_retryable mode
    # ------------------------------------------------------------------ #

    def _run_is_retryable(
        self, code: int, method: str | None
    ) -> dict[str, Any]:
        """Build the full retry decision for one code and method."""
        retryable = self._retryable(code)
        method_idempotent = (
            method in IDEMPOTENT_METHODS if method is not None else None
        )
        if not retryable:
            safe_to_retry = False
            idempotency_note = None
        elif method is None:
            safe_to_retry = True
            idempotency_note = (
                "no method given — confirm the request is idempotent "
                "(RFC 9110 section 9.2.2) before blindly retrying"
            )
        elif method_idempotent:
            safe_to_retry = True
            idempotency_note = None
        else:
            safe_to_retry = False
            idempotency_note = (
                f"{method} is not idempotent (RFC 9110 section 9.2.2) — "
                "the operation may already have been applied; retry only "
                "with an idempotency key or after confirming no side "
                "effects"
            )
        return {
            "mode": "is_retryable",
            "code": code,
            "name": self._name_of(code),
            "retryable": retryable,
            "reason": self._retry_reason(code),
            "method": method,
            "method_idempotent": method_idempotent,
            "safe_to_retry": safe_to_retry,
            "idempotency_note": idempotency_note,
            "backoff": self._backoff_for(code),
        }

    @staticmethod
    def _backoff_for(code: int) -> dict[str, Any] | None:
        """Deterministic backoff recommendation (None: do not retry)."""
        if code == 429 or code == 503:
            return RETRY_AFTER_BACKOFF
        if code == 408:
            return IMMEDIATE_THEN_BACKOFF
        if 500 <= code <= 599 and code not in NEVER_RETRYABLE:
            return EXPONENTIAL_JITTER_BACKOFF
        return None

    # ------------------------------------------------------------------ #
    # category mode
    # ------------------------------------------------------------------ #

    def _run_category(self, category: str) -> dict[str, Any]:
        """List every registered code of one status class."""
        if (
            not isinstance(category, str)
            or category not in self.CATEGORIES
        ):
            self._invalid(
                "category must be one of: "
                f"{', '.join(self.CATEGORIES)} (got {category!r})"
            )
        members = sorted(
            code for code in HTTP_STATUS_NAMES
            if self._category_of(code) == category
        )
        return {
            "mode": "category",
            "category": category,
            "description": CATEGORY_DESCRIPTIONS[category],
            "count": len(members),
            "codes": [
                {"code": code, "name": self._name_of(code)}
                for code in members
            ],
            "retryable": [
                code for code in members if self._retryable(code)
            ],
        }

    # ------------------------------------------------------------------ #
    # Retry policy
    # ------------------------------------------------------------------ #

    @classmethod
    def _retryable(cls, code: int) -> bool:
        """Documented policy: 408/429 plus 5xx except 501 and 505."""
        if code in ALWAYS_RETRYABLE:
            return True
        if 500 <= code <= 599 and code not in NEVER_RETRYABLE:
            return True
        return False

    @classmethod
    def _retry_reason(cls, code: int) -> str:
        """Explain the retry policy verdict for one code."""
        if code == 408:
            return (
                "request timeout — the server stopped waiting for the "
                "client; the request may not have been fully processed, "
                "so a retry is appropriate"
            )
        if code == 429:
            return (
                "rate limited — the server throttled the client; retry "
                "after the Retry-After delay or with exponential backoff"
            )
        if code == 501:
            return (
                "not implemented — the server lacks the required "
                "functionality; the request must change, not the timing"
            )
        if code == 505:
            return (
                "unsupported HTTP version — the server refuses the "
                "request's protocol version; change the protocol, not "
                "the timing"
            )
        if 500 <= code <= 599:
            suffix = (
                " (unregistered code interpreted by its 5xx class)"
                if code not in HTTP_STATUS_NAMES
                else ""
            )
            return (
                "server error — a transient server-side failure; "
                "retrying after a backoff may succeed" + suffix
            )
        if 400 <= code <= 499:
            return (
                "client error — the request must be changed before it "
                "can succeed; retrying it unchanged will fail again"
            )
        if 300 <= code <= 399:
            return (
                "redirection — follow the Location header instead of "
                "retrying the original URI"
            )
        if 200 <= code <= 299:
            return "success — there is nothing to retry"
        return "informational — interim protocol response, not a final outcome"

    # ------------------------------------------------------------------ #
    # Convenience helpers used by tests and downstream code
    # ------------------------------------------------------------------ #

    @classmethod
    def registered_codes(cls) -> list[int]:
        """Every registered status code, ascending (62 entries)."""
        return sorted(HTTP_STATUS_NAMES)
