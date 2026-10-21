#!/usr/bin/env python3
"""HTTP header field validation, parsing, and security-header auditing."""

# stdlib only; strict validation, bounded inputs, deterministic output.

import calendar
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# RFC 7230 section 3.2.6 token grammar: token = 1*tchar.
_TOKEN_CHARS = frozenset(
    "!#$%&'*+-.^_`|~"
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
# RFC 7230 section 3.2 field-value: visible US-ASCII (0x21-0x7E) plus SP/HTAB.
_FIELD_VALUE_CHARS = frozenset(chr(c) for c in range(0x21, 0x7F)) | {" ", "\t"}

# Known fields curated from RFC 7230/7231/7234/6797 and common practice.
_REQUEST_ONLY_FIELDS = frozenset({
    "host", "accept", "accept-charset", "accept-encoding", "accept-language",
    "authorization", "expect", "from", "if-match", "if-modified-since",
    "if-none-match", "if-range", "if-unmodified-since", "max-forwards",
    "proxy-authorization", "range", "referer", "te", "user-agent", "cookie",
    "origin", "dnt", "upgrade-insecure-requests", "sec-fetch-site",
    "sec-fetch-mode", "sec-fetch-dest", "x-requested-with",
})
_RESPONSE_ONLY_FIELDS = frozenset({
    "age", "server", "set-cookie", "set-cookie2", "www-authenticate",
    "proxy-authenticate", "location", "retry-after", "etag", "last-modified",
    "accept-ranges", "content-range", "allow", "x-powered-by",
    "strict-transport-security", "content-security-policy",
    "content-security-policy-report-only", "x-frame-options",
    "x-content-type-options", "referrer-policy", "permissions-policy",
    "x-xss-protection", "cross-origin-opener-policy",
    "cross-origin-embedder-policy", "cross-origin-resource-policy",
    "timing-allow-origin", "expect-ct",
})
_BOTH_FIELDS = frozenset({
    "cache-control", "connection", "date", "pragma", "trailer",
    "transfer-encoding", "upgrade", "via", "warning", "content-type",
    "content-length", "vary", "link",
})

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# RFC 6265 section 5.1.1 delimiter set: %x09 / %x20-2F / %x3B-40 / %x5B-60 /
# %x7B-7E. Note ':' (0x3A) is NOT a delimiter, so "10:18:14" stays one token.
_COOKIE_DATE_DELIMS = frozenset(
    "\t"
    + "".join(chr(c) for c in range(0x20, 0x30))
    + "".join(chr(c) for c in range(0x3B, 0x41))
    + "".join(chr(c) for c in range(0x5B, 0x61))
    + "".join(chr(c) for c in range(0x7B, 0x7F))
)
# The trailing "( non-digit *OCTET )" of the time/day-of-month/year
# productions is applied as optional: a mandatory reading would reject the
# canonical "Wed, 09 Jun 2021 10:18:14 GMT" form every browser accepts.
_TIME_RE = re.compile(r"^(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\D.*)?$")
_DAY_RE = re.compile(r"^(\d{1,2})(?:\D.*)?$")
_YEAR_RE = re.compile(r"^(\d{2,4})(?:\D.*)?$")

# RFC 7231 section 5.3.1 qvalue: "0" [ "." 0*3DIGIT ] / "1" [ "." 0*3"0" ].
_QVALUE_RE = re.compile(r"^(?:0(?:\.\d{0,3})?|1(?:\.0{0,3})?)$")
_DIGITS_RE = re.compile(r"^\d+$")

_FETCH_DIRECTIVES = frozenset({
    "child-src", "connect-src", "default-src", "font-src", "frame-src",
    "img-src", "manifest-src", "media-src", "object-src", "prefetch-src",
    "script-src", "script-src-elem", "script-src-attr", "style-src",
    "style-src-elem", "style-src-attr", "worker-src", "base-uri", "form-action",
    "frame-ancestors",
})
_CSP_DIRECTIVES = _FETCH_DIRECTIVES | frozenset({
    "sandbox", "report-uri", "report-to", "upgrade-insecure-requests",
    "require-trusted-types-for", "trusted-types", "block-all-mixed-content",
    "plugin-types", "navigate-to",
})
_DEPRECATED_CSP_HEADERS = frozenset({"x-webkit-csp", "x-content-security-policy"})
# CSP3 section 2.3.1 grammar: nonce-source/hash-source are single-quoted
# ("'nonce-<base64>'", "'sha256-...'"); without the quotes the token parses as
# a host-source and the intended nonce/hash is never applied.
_CSP_QUOTED_NONCE_HASH = ("'nonce-", "'sha256-", "'sha384-", "'sha512-")
_CSP_UNQUOTED_NONCE_HASH = ("nonce-", "sha256-", "sha384-", "sha512-")
_HSTS_LOW_BAR_SECONDS = 15552000  # OWASP recommendation: at least 180 days.
_MAX_HSTS_MAX_AGE = 2 ** 31 - 1
_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
_ERROR_ORDER = {"error": 0, "warning": 1, "info": 2}


def _cookie_date(value: str | None) -> dict[str, Any] | None:
    """RFC 6265 section 5.1.1 cookie-date algorithm (lenient by design)."""
    if not value:
        return None
    tokens: list[str] = []
    current: list[str] = []
    for char in value:
        if char in _COOKIE_DATE_DELIMS:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(char)
    if current:
        tokens.append("".join(current))

    found_time = found_day = found_month = found_year = False
    hour = minute = second = day = month = year = 0
    for token in tokens:
        if not found_time:
            match = _TIME_RE.fullmatch(token)
            if match:
                hour, minute, second = (int(g) for g in match.groups())
                found_time = True
                continue
        if not found_day:
            match = _DAY_RE.fullmatch(token)
            if match:
                day = int(match.group(1))
                found_day = True
                continue
        if not found_month:
            if len(token) >= 3 and token[:3].lower() in _MONTHS:
                month = _MONTHS[token[:3].lower()]
                found_month = True
                continue
        if not found_year:
            match = _YEAR_RE.fullmatch(token)
            if match:
                year = int(match.group(1))
                found_year = True

    if not (found_time and found_day and found_month and found_year):
        return None
    if not 1 <= day <= 31:
        return None
    if 70 <= year <= 99:
        year += 1900
    elif year <= 69:
        year += 2000
    if year < 1601 or hour > 23 or minute > 59 or second > 59:
        return None
    calendar_valid = 1 <= day <= calendar.monthrange(year, month)[1]
    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "calendar_valid": calendar_valid,
        "iso": (
            f"{year:04d}-{month:02d}-{day:02d}"
            f"T{hour:02d}:{minute:02d}:{second:02d}Z"
        ) if calendar_valid else None,
    }


def _split_unquoted(value: str, sep: str) -> tuple[list[str], bool]:
    """Split on sep outside RFC 7230 quoted-strings (section 3.2.6).

    Backslash escapes only apply inside quoted-strings. Returns
    (parts, unterminated_quoted_string).
    """
    parts: list[str] = []
    current: list[str] = []
    in_quotes = False
    escaped = False
    for char in value:
        if in_quotes:
            if escaped:
                current.append(char)
                escaped = False
            elif char == "\\":
                current.append(char)
                escaped = True
            else:
                current.append(char)
                if char == '"':
                    in_quotes = False
            continue
        if char == '"':
            current.append(char)
            in_quotes = True
        elif char == sep:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return parts, in_quotes


def _unquote(value: str) -> str:
    """Strip one quoted-string layer, resolving quoted-pairs."""
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        inner = value[1:-1]
        out: list[str] = []
        i = 0
        while i < len(inner):
            if inner[i] == "\\" and i + 1 < len(inner):
                out.append(inner[i + 1])
                i += 2
            else:
                out.append(inner[i])
                i += 1
        return "".join(out)
    return value


class HttpHeaderTool(Tool):
    """Validate, parse, and audit HTTP header fields (RFC 7230/7231/6265, OWASP)."""

    max_name_len: int = 1024
    max_value_len: int = 16384
    max_list_elements: int = 1000
    max_audit_bytes: int = 65536
    max_audit_lines: int = 200
    max_cookie_len: int = 8192

    _MODES: ClassVar[frozenset[str]] = frozenset(
        {"validate", "parse_list", "security_audit", "parse_cookie"}
    )
    _WHICH: ClassVar[frozenset[str]] = frozenset({"request", "response", "both"})

    def execute(
        self,
        mode: str,
        name: str | None = None,
        value: str | None = None,
        which: str = "both",
        header: str | None = None,
        headers: str | None = None,
    ) -> dict[str, Any]:
        operation = None
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "validate":
                return self._validate(name, value, which)
            if operation == "parse_list":
                return self._parse_list(value, header)
            if operation == "security_audit":
                return self._security_audit(headers)
            return self._parse_cookie(value)
        except (TypeError, ValueError) as exc:
            return self._error(operation or mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive
            return self._error(operation or mode, "operation_error", f"Header operation failed: {exc}")

    # ------------------------------------------------------------------ util

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {
            "mode": mode if isinstance(mode, str) else "",
            "status": "error",
            "error_type": kind,
            "error": message,
        }

    def _validate_config(self) -> None:
        for bound_name in (
            "max_name_len", "max_value_len", "max_list_elements",
            "max_audit_bytes", "max_audit_lines", "max_cookie_len",
        ):
            bound = getattr(self, bound_name)
            if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
                raise ValueError(f"{bound_name} must be a positive integer")

    def _mode(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in self._MODES:
            raise ValueError("mode must be validate, parse_list, security_audit, or parse_cookie")
        return mode

    # ------------------------------------------------------------ validate

    def _validate(self, name: Any, value: Any, which: Any) -> dict[str, Any]:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        if not isinstance(which, str) or which.strip().lower() not in self._WHICH:
            raise ValueError("which must be request, response, or both")
        scope = which.strip().lower()
        if len(name) > self.max_name_len:
            raise ValueError(f"name exceeds max_name_len ({self.max_name_len})")
        if len(value) > self.max_value_len:
            raise ValueError(f"value exceeds max_value_len ({self.max_value_len})")

        name_valid, name_findings = self._check_name(name)
        value_valid, value_findings = self._check_value(value)
        findings = name_findings + value_findings

        known = False
        category = None
        if name_valid:
            key = name.lower()
            if key in _REQUEST_ONLY_FIELDS:
                category = "request"
            elif key in _RESPONSE_ONLY_FIELDS:
                category = "response"
            elif key in _BOTH_FIELDS:
                category = "both"
            known = category is not None
            if known and scope != "both" and category != scope and category != "both":
                direction = "response-only" if category == "response" else "request-only"
                role = "client request" if scope == "request" else "server response"
                findings.append({
                    "code": "field_cross_usage",
                    "severity": "warning",
                    "span": [0, len(name)],
                    "message": f"{name} is a {direction} header field; it is unexpected in a {role} message",
                })
        return {
            "mode": "validate",
            "status": "success",
            "name": name,
            "value": value,
            "name_valid": name_valid,
            "value_valid": value_valid,
            "findings": findings,
            "known_field": known,
            "field_category": category,
            "which": scope,
            "notes": [
                "Header field names are case-insensitive (RFC 7230 section 5.1); "
                f"comparison key: {name.lower()}.",
                "Leading/trailing OWS (SP/HTAB) around the value is tolerated: "
                "recipients strip it (RFC 7230 section 3.2.3); senders must not send it.",
            ],
        }

    def _check_name(self, name: str) -> tuple[bool, list[dict[str, Any]]]:
        findings: list[dict[str, Any]] = []
        if not name:
            findings.append({
                "code": "name_empty",
                "severity": "error",
                "span": [0, 0],
                "message": "Header field name is empty; RFC 7230 section 3.2 requires at least one tchar",
            })
            return False, findings
        flagged = 0
        for index, char in enumerate(name):
            if char in _TOKEN_CHARS:
                continue
            if char in "\r\n":
                reason = "CR/LF (request-smuggling vector)"
            elif char == "\x00":
                reason = "NUL byte"
            elif char in " \t":
                reason = "whitespace"
            elif ord(char) < 0x20 or ord(char) == 0x7F:
                reason = f"control character U+{ord(char):04X}"
            elif ord(char) > 0x7E:
                reason = f"non-ASCII character U+{ord(char):04X}"
            else:
                reason = f"non-token delimiter {char!r}"
            findings.append({
                "code": "name_non_token",
                "severity": "error",
                "span": [index, index + 1],
                "message": (
                    f"Header name contains {reason} at offset {index}; the RFC 7230 "
                    "token grammar (tchar: ALPHA/DIGIT/!#$%&'*+-.^_`|~) forbids it"
                ),
            })
            flagged += 1
            if flagged >= 8:
                findings.append({
                    "code": "name_non_token",
                    "severity": "error",
                    "span": [index, len(name)],
                    "message": f"... {len(name) - index - 1} further characters unchecked; name rejected",
                })
                break
        return not findings, findings

    def _check_value(self, value: str) -> tuple[bool, list[dict[str, Any]]]:
        findings: list[dict[str, Any]] = []
        lead = value[:1] in " \t"
        trail = value[-1:] in " \t"
        if lead or trail:
            side = "leading" if lead and not trail else ("trailing" if trail else "leading/trailing")
            findings.append({
                "code": f"value_ows_{side.replace('/', '_')}",
                "severity": "info",
                "span": [0, len(value)],
                "message": (
                    f"Value carries {side} OWS (SP/HTAB); recipients strip it "
                    "(RFC 7230 section 3.2.3), senders must not produce it"
                ),
            })
        flagged = 0
        in_fold = False
        for i, char in enumerate(value):
            if char in "\r\n":
                nxt = value[i + 1] if i + 1 < len(value) else ""
                fold = (
                    nxt in " \t"
                    or (char == "\r" and nxt == "\n" and value[i + 2:i + 3] in (" ", "\t"))
                )
                if fold and not in_fold:
                    in_fold = True
                    findings.append({
                        "code": "value_obs_fold",
                        "severity": "error",
                        "span": [i, min(i + 3, len(value))],
                        "message": (
                            "obs-fold (CR/LF line continuation) deprecated by RFC "
                            "7230 section 3.2.4: a server MUST reject the message "
                            "or replace each fold with SP before interpretation; "
                            "folding is a header-injection vehicle"
                        ),
                    })
                elif not fold and not in_fold:
                    in_fold = True
                    findings.append({
                        "code": "value_cr_lf_injection",
                        "severity": "error",
                        "span": [i, min(i + 2, len(value))],
                        "message": (
                            "Bare CR/LF in header value: response-splitting / "
                            "header-injection vector; the message must be rejected"
                        ),
                    })
                flagged += 1
                if flagged >= 8:
                    break
                continue
            in_fold = False
            if char not in _FIELD_VALUE_CHARS:
                if char == "\x00":
                    code, message = (
                        "value_nul",
                        "NUL byte in value: NUL-truncation truncation-bypass "
                        "vector; forbidden by RFC 7230 field-value",
                    )
                elif ord(char) < 0x20 or ord(char) == 0x7F:
                    code, message = (
                        "value_ctl_char",
                        f"Control character U+{ord(char):04X}: field-value allows "
                        "only visible US-ASCII plus SP/HTAB (RFC 7230 section 3.2)",
                    )
                else:
                    code, message = (
                        "value_non_ascii",
                        f"Non-ASCII character U+{ord(char):04X}: RFC 7230 "
                        "field-values are US-ASCII; non-ASCII data needs RFC "
                        "8187/percent encoding",
                    )
                findings.append({"code": code, "severity": "error", "span": [i, i + 1], "message": message})
                flagged += 1
                if flagged >= 8:
                    findings.append({
                        "code": "value_too_many_issues",
                        "severity": "error",
                        "span": [i, len(value)],
                        "message": f"... {len(value) - i - 1} further characters unchecked; value rejected",
                    })
                    break
        return not any(f["severity"] == "error" for f in findings), findings

    # ---------------------------------------------------------- parse_list

    def _parse_list(self, value: Any, header: Any) -> dict[str, Any]:
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        if header is not None and not isinstance(header, str):
            raise TypeError("header must be a string or null")
        if len(value) > self.max_value_len:
            raise ValueError(f"value exceeds max_value_len ({self.max_value_len})")
        notes: list[str] = []
        if header and header.strip().lower() in ("set-cookie", "set-cookie2"):
            notes.append(
                "Set-Cookie is not a comma-mergeable list (RFC 6265 section 3): "
                "Expires dates embed commas, so comma splitting is unsafe; use "
                "mode=parse_cookie per Set-Cookie line instead"
            )
        elements, unterminated = _split_unquoted(value, ",")
        if unterminated:
            notes.append(
                "Unterminated quoted-string: RFC 7230 section 3.2.6 requires a "
                "closing DQUOTE; parsed leniently to end of input"
            )
        parsed: list[dict[str, Any]] = []
        empty_count = 0
        for element in elements:
            if not element.strip(" \t"):
                empty_count += 1
                continue
            parsed.append(self._parse_element(element, len(parsed)))
            if len(parsed) > self.max_list_elements:
                raise ValueError(f"list produces more than max_list_elements ({self.max_list_elements})")
        if empty_count:
            notes.append(
                f"{empty_count} empty list element(s) ignored (RFC 7231 section "
                "5.3.2 lets recipients skip empty elements)"
            )
        return {
            "mode": "parse_list",
            "status": "success",
            "header": header,
            "value": value,
            "elements": parsed,
            "element_count": len(parsed),
            "empty_elements_ignored": empty_count,
            "notes": notes,
        }

    def _parse_element(self, element: str, order: int) -> dict[str, Any]:
        segments, _unterminated = _split_unquoted(element, ";")
        token = segments[0].strip(" \t")
        params: list[dict[str, Any]] = []
        params_map: dict[str, Any] = {}
        for raw in segments[1:]:
            name_part, eq, value_part = raw.partition("=")
            pname = name_part.strip(" \t")
            if not pname:
                params.append({"name": "", "value": None})
                continue
            if eq:
                pvalue: str | None = _unquote(value_part.strip(" \t"))
            else:
                pvalue = None
            params.append({"name": pname, "value": pvalue})
            params_map[pname] = pvalue

        q = None
        q_raw = None
        q_malformed = False
        q_duplicate = False
        q_index = None
        for position, param in enumerate(params):
            if param["name"].lower() != "q":
                continue
            if q_index is not None:
                q_duplicate = True
                continue
            q_index = position
            q_raw = param["value"]
            if q_raw is not None and _QVALUE_RE.fullmatch(q_raw):
                q = float(q_raw)
            else:
                q_malformed = True
        notes: list[str] = []
        if q_duplicate:
            notes.append("Duplicate q parameter: RFC 7231 section 5.3.1 allows one weight per element (first kept)")
        if q_malformed:
            notes.append(
                f"Malformed qvalue {q_raw!r}: RFC 7231 grammar is qvalue = "
                "( \"0\" [ \".\" 0*3DIGIT ] / \"1\" [ \".\" 0*3\"0\" ] )"
            )
        if q_index is not None and q_index != 0:
            notes.append("q parameter is not the first parameter; RFC 7231 section 5.3.1 places the weight first")
        return {
            "token": token,
            "params": params_map,
            "params_list": params,
            "q": q,
            "q_raw": q_raw,
            "q_malformed": q_malformed,
            "order": order,
            "notes": notes,
        }

    # ------------------------------------------------------ security_audit

    def _security_audit(self, headers: Any) -> dict[str, Any]:
        if not isinstance(headers, str):
            raise TypeError("headers must be a string of 'Name: value' lines")
        if len(headers) > self.max_audit_bytes:
            raise ValueError(f"headers exceeds max_audit_bytes ({self.max_audit_bytes})")
        lines = headers.splitlines()
        if len(lines) > self.max_audit_lines:
            raise ValueError(f"headers exceeds max_audit_lines ({self.max_audit_lines})")
        seen: dict[str, list[str]] = {}
        findings: list[dict[str, Any]] = []
        for number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            name, colon, value = line.partition(":")
            if not colon or not name.strip():
                findings.append({
                    "header": None,
                    "code": "audit_line_unparsed",
                    "severity": "info",
                    "message": f"Line {number} has no 'Name: value' structure",
                })
                continue
            seen.setdefault(name.strip().lower(), []).append(value.strip())
        for key in sorted(seen):
            if len(seen[key]) > 1 and key != "set-cookie":
                findings.append({
                    "header": key,
                    "code": "audit_duplicate_header",
                    "severity": "info",
                    "message": f"Header {key} appears {len(seen[key])} times; recipients may join or drop later values",
                })

        self._audit_hsts(seen, findings)
        csp_directives = self._audit_csp(seen, findings)
        self._audit_xcto(seen, findings)
        self._audit_referrer_policy(seen, findings)
        self._audit_permissions_policy(seen, findings)
        if "x-frame-options" in seen:
            self._audit_xfo(seen["x-frame-options"][0], findings)
        self._audit_xss_protection(seen, findings)
        self._audit_caching(seen, findings)
        self._audit_info_leak(seen, findings)
        self._audit_cookies(seen, findings)

        findings.sort(key=lambda f: (
            _SEVERITY_ORDER.get(f["severity"], 9), str(f.get("header")), f["code"],
        ))
        counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            counts[finding["severity"]] += 1
        return {
            "mode": "security_audit",
            "status": "success",
            "headers_seen": sorted(seen),
            "csp_directives": csp_directives,
            "findings": findings,
            "summary": {"finding_count": len(findings), "by_severity": counts},
        }

    @staticmethod
    def _finding(header: str, code: str, severity: str, message: str) -> dict[str, Any]:
        return {"header": header, "code": code, "severity": severity, "message": message}

    def _audit_hsts(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        label = "Strict-Transport-Security"
        values = seen.get("strict-transport-security")
        if values is None:
            findings.append(self._finding(
                label, "hsts_missing", "medium",
                "HSTS header missing; HSTS mitigates TLS downgrade / SSL-stripping "
                "and session-cookie hijacking over plaintext redirects (it is only "
                "meaningful on HTTPS responses)",
            ))
            return
        value = values[0]
        max_age = None
        include_subdomains = False
        preload = False
        nonconforming = False
        seen_names: set[str] = set()
        for directive in value.split(";"):
            directive = directive.strip()
            if not directive:
                continue
            name, eq, dvalue = directive.partition("=")
            name = name.strip()
            dvalue = dvalue.strip()
            lname = name.lower()
            if lname in seen_names:
                # RFC 6797 section 6.1: "All directives MUST appear only once
                # in an STS header field" and a UA MUST ignore any header that
                # does not conform - so a repeat voids the whole header.
                nonconforming = True
                findings.append(self._finding(
                    label, "hsts_duplicate_directive", "high",
                    f"Directive {name!r} appears more than once: RFC 6797 section 6.1 "
                    "requires every directive to appear exactly once, and conforming "
                    "UAs MUST ignore the entire STS header field - no HSTS protection "
                    "is applied",
                ))
                continue
            seen_names.add(lname)
            if lname == "max-age":
                if not eq or not dvalue:
                    nonconforming = True
                    findings.append(self._finding(
                        label, "hsts_max_age_invalid", "high",
                        f"Directive {directive!r} has no value; RFC 6797 section 6.1.1 "
                        "requires max-age=delta-seconds; a conforming UA MUST ignore "
                        "the entire STS header field (RFC 6797 section 6.1)",
                    ))
                    continue
                if dvalue.startswith('"') or not _DIGITS_RE.fullmatch(dvalue):
                    nonconforming = True
                    findings.append(self._finding(
                        label, "hsts_max_age_invalid", "high",
                        f"max-age value {dvalue!r} is not an unquoted delta-seconds "
                        "integer (RFC 6797 section 6.1.1); a conforming UA MUST ignore "
                        "the entire STS header field (RFC 6797 section 6.1)",
                    ))
                    continue
                max_age = int(dvalue)
                if max_age > _MAX_HSTS_MAX_AGE:
                    findings.append(self._finding(
                        label, "hsts_max_age_overflow", "low",
                        f"max-age {max_age} exceeds 2^31-1; some UAs clamp or reject it",
                    ))
                elif max_age == 0:
                    findings.append(self._finding(
                        label, "hsts_max_age_zero", "medium",
                        "max-age=0 instructs UAs to delete the HSTS entry (header effectively disabled)",
                    ))
                elif max_age < _HSTS_LOW_BAR_SECONDS:
                    findings.append(self._finding(
                        label, "hsts_max_age_low", "low",
                        f"max-age {max_age} is below the OWASP bar of {_HSTS_LOW_BAR_SECONDS} seconds (180 days)",
                    ))
            elif lname == "includesubdomains":
                include_subdomains = True
                if eq and dvalue:
                    findings.append(self._finding(
                        label, "hsts_flag_with_value", "low", "includeSubDomains takes no value",
                    ))
            elif lname == "preload":
                preload = True
                if eq and dvalue:
                    findings.append(self._finding(
                        label, "hsts_flag_with_value", "low", "preload takes no value",
                    ))
            else:
                findings.append(self._finding(
                    label, "hsts_unknown_directive", "info",
                    f"Unrecognized directive {name!r} ignored",
                ))
        if max_age is None:
            findings.append(self._finding(
                label, "hsts_max_age_missing", "high",
                "HSTS present without a valid max-age: RFC 6797 section 6.1.1 says "
                "the UA MUST ignore the entire header (no protection is applied)",
            ))
            return
        if nonconforming:
            # The parsed max-age is moot: RFC 6797 section 6.1 makes the whole
            # header ignorable, so scope advice would be misleading.
            return
        missing_scope = [n for n, present in (
            ("includeSubDomains", include_subdomains), ("preload", preload)) if not present]
        if missing_scope:
            findings.append(self._finding(
                label, "hsts_scope_limited", "low",
                f"HSTS scope limited: missing {', '.join(missing_scope)}",
            ))

    def _audit_csp(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        label = "Content-Security-Policy"
        for deprecated in sorted(_DEPRECATED_CSP_HEADERS):
            if deprecated in seen:
                findings.append(self._finding(
                    deprecated, "csp_header_deprecated", "low",
                    f"{deprecated} is a deprecated pre-standard CSP header; modern UAs ignore it, remove it",
                ))
        values = seen.get("content-security-policy")
        if values is None:
            findings.append(self._finding(
                label, "csp_missing", "high",
                "Content-Security-Policy missing: a restrictive CSP is the primary "
                "mitigation for XSS (script injection) and data exfiltration",
            ))
            return []
        csp = values[0]
        directives: list[dict[str, Any]] = []
        inventory: dict[str, list[str]] = {}
        for chunk in csp.split(";"):
            chunk = chunk.strip()
            if not chunk:
                continue
            parts = chunk.split()
            name = parts[0].lower()
            tokens = parts[1:]
            directives.append({"name": name, "values": tokens})
            inventory.setdefault(name, []).extend(tokens)

        unsafe_inline: set[str] = set()
        unsafe_inline_ignored: set[str] = set()
        for directive in directives:
            values = directive["values"]
            if directive["name"] not in _FETCH_DIRECTIVES or "'unsafe-inline'" not in values:
                continue
            # CSP source matching: 'unsafe-inline' is ignored by conforming
            # UAs when the same source list carries a nonce or hash, and
            # 'strict-dynamic' ignores every allowlist/source expression.
            has_nonce_hash = any(v.startswith(p) for v in values for p in _CSP_QUOTED_NONCE_HASH)
            has_strict_dynamic = (
                directive["name"] == "script-src" and "'strict-dynamic'" in values
            )
            if has_nonce_hash or has_strict_dynamic:
                unsafe_inline_ignored.add(directive["name"])
            else:
                unsafe_inline.add(directive["name"])
        if unsafe_inline:
            findings.append(self._finding(
                label, "csp_unsafe_inline", "high",
                f"'unsafe-inline' in {', '.join(sorted(unsafe_inline))}: allows inline "
                "script/style injection, defeating the CSP XSS mitigation; use nonces or hashes",
            ))
        if unsafe_inline_ignored:
            findings.append(self._finding(
                label, "csp_unsafe_inline_ignored_by_nonce", "info",
                f"'unsafe-inline' in {', '.join(sorted(unsafe_inline_ignored))} is ignored "
                "by conforming UAs: a nonce-source or hash-source in the same source "
                "list takes precedence, and 'strict-dynamic' ignores every allowlist "
                "expression; inline behavior stays nonce/hash-governed",
            ))
        unsafe_eval = sorted(
            d for d, toks in inventory.items()
            if d in _FETCH_DIRECTIVES and "'unsafe-eval'" in toks
        )
        if unsafe_eval:
            findings.append(self._finding(
                label, "csp_unsafe_eval", "medium",
                f"'unsafe-eval' in {', '.join(unsafe_eval)}: permits eval()/Function() code-injection sinks",
            ))
        insecure_sources: set[str] = set()
        ignored_by_strict_dynamic: set[str] = set()
        for directive in directives:
            name = directive["name"]
            if name not in ("script-src", "script-src-elem", "script-src-attr",
                            "worker-src", "default-src"):
                continue
            if not any(t == "http:" or t.startswith("http://") for t in directive["values"]):
                continue
            # CSP3: 'strict-dynamic' in script-src makes UAs ignore host
            # allowlists entirely, so plaintext sources there are inert.
            if name == "script-src" and "'strict-dynamic'" in directive["values"]:
                ignored_by_strict_dynamic.add(name)
            else:
                insecure_sources.add(name)
        if insecure_sources:
            findings.append(self._finding(
                label, "csp_insecure_source", "medium",
                f"Plaintext-http script source in {', '.join(sorted(insecure_sources))}: "
                "an on-path attacker can inject scripts",
            ))
        if ignored_by_strict_dynamic:
            findings.append(self._finding(
                label, "csp_insecure_source_ignored_by_strict_dynamic", "info",
                "Plaintext-http source in script-src carries no effect: with "
                "'strict-dynamic' present, conforming UAs ignore host allowlists "
                "(only nonces/hashes and propagated loader grants apply)",
            ))
        unquoted_nonce_hash = sorted({
            d["name"] for d in directives
            if d["name"] in _FETCH_DIRECTIVES
            and any(v.startswith(p) for v in d["values"] for p in _CSP_UNQUOTED_NONCE_HASH)
        })
        if unquoted_nonce_hash:
            findings.append(self._finding(
                label, "csp_unquoted_nonce_or_hash", "low",
                f"Unquoted nonce-/hash- token in {', '.join(unquoted_nonce_hash)}: CSP "
                "grammar requires single quotes ('nonce-...', 'sha256-...'); unquoted, "
                "the token is a host-source and the intended nonce/hash never applies",
            ))
        unknown = sorted(d for d in inventory if d not in _CSP_DIRECTIVES)
        if unknown:
            findings.append(self._finding(
                label, "csp_unknown_directive", "info",
                f"Unrecognized directive(s): {', '.join(unknown)}",
            ))
        # sandbox with no value is valid (it applies the maximum restriction
        # set); upgrade-insecure-requests/block-all-mixed-content are flags.
        # require-trusted-types-for however REQUIRES the "'script'" argument.
        empty = sorted({
            d["name"] for d in directives
            if not d["values"] and d["name"] not in (
                "upgrade-insecure-requests", "block-all-mixed-content", "sandbox")
        })
        if empty:
            findings.append(self._finding(
                label, "csp_empty_directive", "info",
                f"Directive(s) without values: {', '.join(empty)}",
            ))
        for directive in directives:
            if "'none'" in directive["values"] and len(directive["values"]) > 1:
                findings.append(self._finding(
                    label, "csp_none_with_sources", "info",
                    f"Directive {directive['name']} mixes 'none' with other sources; 'none' must stand alone",
                ))
        if "default-src" not in inventory:
            findings.append(self._finding(
                label, "csp_no_default_src", "low",
                "No default-src fallback: any fetch directive omitted from the "
                "policy leaves that resource type unrestricted",
            ))
        if "report-uri" in inventory:
            findings.append(self._finding(
                label, "csp_report_uri_deprecated", "info",
                "report-uri is deprecated in favor of report-to (CSP3): wire a "
                "Reporting-Endpoints endpoint group and switch the directive",
            ))
        if "report-to" in inventory and "reporting-endpoints" not in seen and "report-to" not in seen:
            findings.append(self._finding(
                label, "csp_report_to_no_endpoints", "info",
                "report-to references an endpoint group, but no Reporting-Endpoints "
                "(or legacy Report-To) response header declares it: violations "
                "cannot be delivered anywhere",
            ))
        return directives

    def _audit_xcto(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        label = "X-Content-Type-Options"
        values = seen.get("x-content-type-options")
        if values is None:
            findings.append(self._finding(
                label, "xcto_missing", "medium",
                "X-Content-Type-Options: nosniff missing; mitigates browser MIME "
                "sniffing turning uploaded text into executable content",
            ))
        elif "nosniff" not in values[0].lower():
            findings.append(self._finding(
                label, "xcto_invalid", "medium", "X-Content-Type-Options must be 'nosniff'",
            ))

    def _audit_referrer_policy(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        if "referrer-policy" not in seen:
            findings.append(self._finding(
                "Referrer-Policy", "referrer_policy_missing", "low",
                "Referrer-Policy missing; mitigates cross-origin leakage of full "
                "URLs, which can embed credentials or tokens in the query string",
            ))

    def _audit_permissions_policy(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        if "permissions-policy" not in seen:
            findings.append(self._finding(
                "Permissions-Policy", "permissions_policy_missing", "low",
                "Permissions-Policy missing; mitigates abuse of powerful features "
                "(camera, microphone, geolocation) by embedded or injected content",
            ))

    def _audit_xfo(self, value: str, findings: list[dict[str, Any]]) -> None:
        label = "X-Frame-Options"
        upper = value.strip().upper()
        if upper in ("DENY", "SAMEORIGIN"):
            return
        if upper.startswith("ALLOW-FROM"):
            findings.append(self._finding(
                label, "xfo_allow_from_deprecated", "medium",
                "ALLOW-FROM is deprecated and unsupported by modern browsers "
                "(RFC 7034 appendix B); migrate to CSP frame-ancestors",
            ))
            return
        findings.append(self._finding(
            label, "xfo_invalid", "medium",
            f"X-Frame-Options value {value!r} is not DENY or SAMEORIGIN; invalid "
            "values are ignored, which re-enables clickjacking via framing",
        ))

    def _audit_xss_protection(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        label = "X-XSS-Protection"
        if "x-xss-protection" not in seen:
            return
        value = seen["x-xss-protection"][0].strip().lower()
        if value in ("0", "0; mode=block"):
            findings.append(self._finding(
                label, "xss_filter_disabled", "info",
                "X-XSS-Protection is deprecated (browsers removed the auditor); "
                "'0' or removal is the correct posture",
            ))
        else:
            findings.append(self._finding(
                label, "xss_filter_deprecated", "low",
                "X-XSS-Protection is deprecated and the old auditor itself "
                "introduced vulnerabilities; prefer a CSP without 'unsafe-inline'",
            ))

    def _audit_caching(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        sensitive = "set-cookie" in seen or "www-authenticate" in seen
        if not sensitive:
            return
        cache = seen.get("cache-control")
        if cache is None:
            findings.append(self._finding(
                "Cache-Control", "cache_control_missing_sensitive", "medium",
                "Sensitive response (Set-Cookie/WWW-Authenticate) without "
                "Cache-Control: use 'no-store' to keep it out of shared caches",
            ))
            return
        directives = {d.strip().lower() for d in cache[0].split(",")}
        if "no-store" not in directives:
            findings.append(self._finding(
                "Cache-Control", "cache_control_no_store_missing", "medium",
                "Sensitive response without Cache-Control: no-store; intermediaries "
                "may retain the response",
            ))

    def _audit_info_leak(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        for key, label in (("server", "Server"), ("x-powered-by", "X-Powered-By")):
            if key in seen:
                findings.append(self._finding(
                    label, "server_version_info_leak", "low",
                    f"{label} discloses implementation/version details that aid "
                    "targeted attacks; suppress or genericize it",
                ))

    def _audit_cookies(self, seen: dict[str, list[str]], findings: list[dict[str, Any]]) -> None:
        for raw in seen.get("set-cookie", []):
            parsed = self._parse_cookie(raw)
            attributes = parsed.get("attributes") or {}
            label = parsed.get("name") or (raw[:32] or "<empty>")
            if not attributes.get("secure"):
                findings.append(self._finding(
                    "Set-Cookie", "cookie_missing_secure", "high",
                    f"Cookie {label!r} without Secure: it can be disclosed over plaintext HTTP",
                ))
            if not attributes.get("httponly"):
                findings.append(self._finding(
                    "Set-Cookie", "cookie_missing_httponly", "medium",
                    f"Cookie {label!r} without HttpOnly: readable by scripts (XSS "
                    "token theft) unless the cookie is deliberately JS-accessible",
                ))
            samesite = attributes.get("samesite")
            if not samesite:
                findings.append(self._finding(
                    "Set-Cookie", "cookie_missing_samesite", "low",
                    f"Cookie {label!r} without SameSite: weaker CSRF defense; prefer Lax or Strict",
                ))
            elif str(samesite).lower() == "none" and not attributes.get("secure"):
                findings.append(self._finding(
                    "Set-Cookie", "cookie_samesite_none_requires_secure", "high",
                    f"Cookie {label!r}: SameSite=None requires Secure; modern UAs reject the pair otherwise",
                ))

    # -------------------------------------------------------- parse_cookie

    def _parse_cookie(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        if len(value) > self.max_cookie_len:
            raise ValueError(f"value exceeds max_cookie_len ({self.max_cookie_len})")
        pairs = value.split(";")
        name, eq, val = pairs[0].partition("=")
        if not eq:
            return {
                "mode": "parse_cookie",
                "status": "success",
                "ignored": True,
                "reason": "missing_equals",
                "message": "RFC 6265 section 5.2 step 2: a name-value pair "
                           "without '=' makes the UA ignore the whole set-cookie-string",
                "rfc6265_strict": [{
                    "code": "no_name_value_pair", "severity": "error",
                    "message": "No '=' in name-value pair",
                }],
            }
        issues: list[dict[str, Any]] = []
        if name.strip(" \t") != name or val.strip(" \t") != val:
            issues.append({
                "code": "cookie_pair_trimmed", "severity": "info",
                "message": "Whitespace around name/value trimmed per RFC 6265 "
                           "section 5.2 steps 4-6 (senders must not add it)",
            })
        cookie_name = name.strip(" \t")
        cookie_value = val.strip(" \t")
        if not cookie_name:
            return {
                "mode": "parse_cookie",
                "status": "success",
                "ignored": True,
                "reason": "empty_name",
                "message": "RFC 6265 section 5.2 step 5: an empty cookie-name "
                           "makes the UA ignore the whole set-cookie-string",
                "rfc6265_strict": [{
                    "code": "empty_name", "severity": "error",
                    "message": "Empty cookie name",
                }],
            }
        quoted = len(cookie_value) >= 2 and cookie_value[0] == '"' and cookie_value[-1] == '"'
        if quoted:
            issues.append({
                "code": "cookie_value_quoted", "severity": "info",
                "message": "DQUOTE-wrapped value: RFC 6265 keeps the quotes in the "
                           "stored value (unlike http.cookies, which unquotes)",
            })
        # RFC 6265 section 4.1.1: cookie-name = token (RFC 7230 tchar set).
        if not all(char in _TOKEN_CHARS for char in cookie_name):
            name_flags = 0
            for index, char in enumerate(cookie_name):
                if char in _TOKEN_CHARS:
                    continue
                issues.append({
                    "code": "cookie_name_illegal_char", "severity": "warning",
                    "span": [index, index + 1],
                    "message": f"Character U+{ord(char):04X} is not a token "
                               "character (RFC 6265 section 4.1.1 cookie-name = token)",
                })
                name_flags += 1
                if name_flags >= 4:
                    break
        illegal_value_flags = 0
        # RFC 6265 section 4.1.1 cookie-octet: %x21-2B / %x2D-3A / %x3C-5B /
        # %x5D-7E (visible US-ASCII minus DQUOTE, COMMA, SEMI, BSLASH).
        for index, char in enumerate(cookie_value):
            if quoted and index in (0, len(cookie_value) - 1):
                continue
            code = ord(char)
            legal = 0x21 <= code <= 0x7E and char not in ('"', ',', ';', '\\')
            if not legal:
                issues.append({
                    "code": "cookie_value_illegal_char", "severity": "warning",
                    "span": [index, index + 1],
                    "message": f"Character U+{code:04X} is outside the RFC 6265 "
                               "cookie-octet set (CTL/SP/DQUOTE/COMMA/SEMI/BSLASH/DEL/non-ASCII)",
                })
                illegal_value_flags += 1
                if illegal_value_flags >= 4:
                    break

        attributes: dict[str, Any] = {
            "expires": None, "max_age": None, "max_age_raw": None,
            "domain": None, "path": None, "secure": False, "httponly": False,
            "samesite": None,
        }
        unknown_attributes: list[dict[str, Any]] = []
        for chunk in pairs[1:]:
            if not chunk.strip(" \t"):
                continue
            aname, aeq, avalue = chunk.partition("=")
            aname = aname.strip(" \t")
            avalue = avalue.strip(" \t") if aeq else None
            lname = aname.lower()
            if lname == "expires":
                parsed = _cookie_date(avalue)
                attributes["expires"] = {"raw": avalue, "parsed": parsed}
                if parsed is None:
                    issues.append({
                        "code": "cookie_expires_invalid", "severity": "warning",
                        "message": f"Expires value {avalue!r} is not a valid "
                                   "cookie-date (RFC 6265 section 5.1.1); the "
                                   "attribute is ignored (section 5.2.1)",
                    })
            elif lname == "max-age":
                attributes["max_age_raw"] = avalue
                if avalue is not None and re.fullmatch(r"-?\d+", avalue):
                    attributes["max_age"] = int(avalue)
                    if attributes["max_age"] <= 0:
                        issues.append({
                            "code": "cookie_max_age_non_positive", "severity": "info",
                            "message": f"Max-Age {avalue} expires the cookie "
                                       "immediately (RFC 6265 section 5.3 step 3)",
                        })
                else:
                    issues.append({
                        "code": "cookie_max_age_invalid", "severity": "warning",
                        "message": f"Max-Age value {avalue!r} is not an integer; "
                                   "RFC 6265 section 5.2.2 ignores the attribute",
                    })
            elif lname == "domain":
                if not avalue:
                    issues.append({
                        "code": "cookie_domain_invalid", "severity": "warning",
                        "message": "Domain attribute without a value",
                    })
                else:
                    normalized = avalue[1:] if avalue.startswith(".") else avalue
                    attributes["domain"] = normalized.lower()
                    if normalized != avalue:
                        issues.append({
                            "code": "cookie_domain_leading_dot", "severity": "info",
                            "message": "Leading '.' in Domain ignored per RFC 6265 section 5.2.3",
                        })
                    if not re.fullmatch(
                        r"[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)*",
                        normalized,
                    ):
                        issues.append({
                            "code": "cookie_domain_invalid", "severity": "warning",
                            "message": f"Domain value {avalue!r} is not a dot-separated host string",
                        })
            elif lname == "path":
                if avalue and avalue.startswith("/"):
                    attributes["path"] = avalue
                else:
                    issues.append({
                        "code": "cookie_path_not_absolute", "severity": "warning",
                        "message": f"Path value {avalue!r} is not absolute; RFC 6265 "
                                   "section 5.2.4 ignores it (default-path applies)",
                    })
            elif lname == "secure":
                attributes["secure"] = True
                if avalue:
                    issues.append({
                        "code": "cookie_secure_with_value", "severity": "info",
                        "message": f"Secure attribute carried a value {avalue!r}; it "
                                   "is a valueless flag (RFC 6265 section 5.2.5)",
                    })
            elif lname == "httponly":
                attributes["httponly"] = True
                if avalue:
                    issues.append({
                        "code": "cookie_httponly_with_value", "severity": "info",
                        "message": f"HttpOnly attribute carried a value {avalue!r}; "
                                   "it is a valueless flag (RFC 6265 section 5.2.6)",
                    })
            elif lname == "samesite":
                if avalue is None:
                    issues.append({
                        "code": "cookie_samesite_missing_value", "severity": "warning",
                        "message": "SameSite attribute without a value",
                    })
                else:
                    attributes["samesite"] = avalue
                    if avalue.lower() not in ("strict", "lax", "none"):
                        issues.append({
                            "code": "cookie_samesite_invalid", "severity": "warning",
                            "message": f"SameSite value {avalue!r} is not Strict, "
                                       "Lax, or None (case-insensitive)",
                        })
            elif aname.startswith("$"):
                issues.append({
                    "code": "cookie_legacy_rfc2965_attribute", "severity": "warning",
                    "message": f"Attribute {aname!r} is RFC 2109/2965 metasyntax; "
                               "RFC 6265 keeps it as an unknown attribute "
                               "(http.cookies instead attaches it to the preceding cookie)",
                })
                unknown_attributes.append({"name": aname, "value": avalue})
            else:
                issues.append({
                    "code": "cookie_unknown_attribute", "severity": "info",
                    "message": f"Unrecognized attribute {aname!r} ignored per RFC 6265 section 5.2",
                })
                unknown_attributes.append({"name": aname, "value": avalue})
        # Post-pass rule (attribute order must not matter).
        if str(attributes["samesite"] or "").lower() == "none" and not attributes["secure"]:
            issues.append({
                "code": "cookie_samesite_none_requires_secure", "severity": "warning",
                "message": "SameSite=None without Secure is rejected by modern "
                           "user agents",
            })
        return {
            "mode": "parse_cookie",
            "status": "success",
            "name": cookie_name,
            "value": cookie_value,
            "ignored": False,
            "quoted": quoted,
            "attributes": attributes,
            "size": len(cookie_name) + len(cookie_value),
            "unknown_attributes": unknown_attributes,
            "rfc6265_strict": issues,
        }
