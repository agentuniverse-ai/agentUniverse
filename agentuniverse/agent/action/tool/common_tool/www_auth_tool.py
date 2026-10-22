#!/usr/bin/env python3
"""Parsing, explanation, building, and comparison of HTTP authentication challenge headers.

This tool implements the ``WWW-Authenticate`` / ``Proxy-Authenticate`` grammar of
RFC 7235 plus the scheme-specific parameter models of RFC 7617 (Basic),
RFC 6750 (Bearer), RFC 7616 (Digest), and RFC 4559 (Negotiate).

Grammar recap (RFC 7235 section 4.1 / RFC 7230 section 3.2.6)::

    WWW-Authenticate = 1#challenge
    challenge        = auth-scheme [ 1*SP ( token68 / #auth-param ) ]
    auth-scheme      = token                      (case-insensitive)
    auth-param       = token BWS "=" BWS ( token / quoted-string )
    token68          = 1*( ALPHA / DIGIT / "-" / "." / "_" / "~" / "+" / "/" ) *"="

Challenge-boundary disambiguation (the classic hard part): auth-params are
comma-separated, challenges are comma-separated, so a bare comma is ambiguous.
RFC 7235 section 4.1 openly acknowledges that ``Newauth realm="apps", type=1``
cannot be distinguished from a scheme named ``type`` by grammar alone. The
practical rule implemented here, used with only cosmetic variation by mainstream
clients, is:

1. Split the header on every comma that is **not inside a quoted string**
   (quote state tracks ``\\`` quoted-pairs).
2. A segment whose first token is directly followed by ``=`` (BWS allowed)
   is an auth-param and continues the current challenge.
3. A segment whose first token is followed by whitespace or nothing starts a
   new challenge; its remainder is either a single leading auth-param pair or
   a token68 (schemes that may carry token68 -- Negotiate and unregistered
   schemes -- win the tie when the remainder ends in ``=`` padding, so
   ``Negotiate abc=`` is a token68 while ``Basic realm=`` stays an empty
   param with an error).
4. Duplicate auth-param names inside one challenge keep the **last** value
   (documented choice; each duplicate is also reported under ``errors``).

Everything is strict and deterministic: fixed caps bound work and output, the
only dependency is ``re``, no clocks, no randomness, no network, and no
credential material is ever required or generated -- test realms are synthetic.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# RFC 7230 section 3.2.6 token characters.
_TOKEN_RE = re.compile(r"[!#$%&'*+\-.^_`|~0-9A-Za-z]+")
# RFC 7235 token68: base characters plus trailing "=" padding.
_TOKEN68_RE = re.compile(r"[A-Za-z0-9\-._~+/]+=*")
# ``name = value`` shape of an auth-param, BWS around "=" tolerated.
_PARAM_SHAPE_RE = re.compile(
    r"^(?P<name>[!#$%&'*+\-.^_`|~0-9A-Za-z]+)\s*=\s*(?P<value>.*)$", re.DOTALL
)

_SCHEME_MEANINGS: ClassVar[dict[str, str]] = {
    "basic": "RFC 7617 - userid and password sent base64-encoded within the realm's protection space.",
    "bearer": "RFC 6750 - OAuth 2.0 bearer access token authorization.",
    "digest": "RFC 7616 - challenge/response proof of a shared secret; the password itself is never sent.",
    "negotiate": "RFC 4559 - HTTP Negotiate: SPNEGO/GSSAPI mechanism negotiation, commonly Kerberos.",
}

# Schemes whose challenge grammar allows a token68 immediately after the scheme
# token. Negotiate does; Basic/Bearer/Digest challenges carry auth-params only.
_TOKEN68_SCHEMES: ClassVar[frozenset[str]] = frozenset({"negotiate"})

_CANONICAL_SCHEMES: ClassVar[dict[str, str]] = {
    "basic": "Basic",
    "bearer": "Bearer",
    "digest": "Digest",
    "negotiate": "Negotiate",
}

_BASIC_PARAM_MEANINGS: ClassVar[dict[str, str]] = {
    "realm": 'Protection-space label shown to the user; credentials apply to this realm (RFC 7617 section 2).',
    "charset": 'Client credential encoding hint; RFC 7617 section 2.1 defines only the value "UTF-8".',
}

_BEARER_PARAM_MEANINGS: ClassVar[dict[str, str]] = {
    "realm": "Protection-space label describing the protected area (RFC 6750 section 3).",
    "scope": "Space-delimited (U+0020 separated) scope values the resource requires, per RFC 6749 section 3.3; must not be treated as a single opaque string.",
    "error": "Error code drawn from the Bearer error registry of RFC 6750 section 3 (see bearer_error_registry).",
    "error_description": "Human-readable text aiding the client developer; not meant for end users (RFC 6750 section 3).",
    "error_uri": "URI of a human-readable page with information about the error (RFC 6750 section 3).",
    "error_codes": "Vendor extension, not defined by RFC 6750: machine-readable code list for the OAuth error registry family.",
}

_BEARER_ERROR_REGISTRY: ClassVar[list[dict[str, str]]] = [
    {
        "code": "invalid_request",
        "meaning": "The request is malformed: a required parameter is missing, a parameter is duplicated, the encoding is unsupported, or the Authorization header is malformed.",
        "remediation": "The client should correct the request and retry; no new token is needed.",
    },
    {
        "code": "invalid_token",
        "meaning": "The access token is expired, revoked, malformed, or invalid for the requested audience.",
        "remediation": "The client should obtain a fresh access token and retry the request.",
    },
    {
        "code": "insufficient_scope",
        "meaning": "The token is valid but lacks a scope required by the resource (often named in the scope param).",
        "remediation": "The client should request authorization for the scopes named in the scope param, typically with end-user involvement.",
    },
]

_OAUTH_ERROR_CODES: ClassVar[dict[str, str]] = {
    "invalid_request": "Request malformed: missing required parameter, unsupported parameter, repeated parameter, invalid value format, or multiple client authentication methods.",
    "invalid_client": "Client authentication failed (unknown client, no authentication included, or unsupported authentication method).",
    "invalid_grant": "The authorization grant / refresh token is invalid, expired, revoked, or was issued to another client.",
    "invalid_scope": "The requested scope is invalid, unknown, or malformed.",
    "unauthorized_client": "The client is not authorized to request this method with this grant type.",
    "unsupported_grant_type": "The authorization grant type is not supported by the authorization server.",
    "unsupported_response_type": "The authorization server does not support this response type.",
}

_DIGEST_PARAM_MEANINGS: ClassVar[dict[str, str]] = {
    "realm": "Protection-space label; also mixed into the A1 hash together with username and password (RFC 7616 section 3.3).",
    "domain": "Space-delimited URI list (prefix-matched) of URIs sharing the protection space (RFC 7616 section 3.2.1).",
    "nonce": "Server-generated unique value binding this challenge and the response to it; the response hash includes the nonce (RFC 7616 section 3.3).",
    "opaque": "Server-chosen data the client must return unchanged in the Authorization header (RFC 7616 section 3.3).",
    "stale": "nonce staleness flag: true means the nonce expired and the client SHOULD retry with the SAME credentials and the new nonce; false (or absent) means the credentials themselves were rejected (RFC 7616 section 3.3).",
    "algorithm": "Hash algorithm for A1/A2 and the response, e.g. MD5, SHA-256, SHA-512-256, with -sess variants (RFC 7616 section 3.3; see digest_algorithms).",
    "qop": "Quality-of-protection options offered, comma and space separated inside one quoted string: auth protects the request line, auth-int additionally hashes the body; the client picks exactly one (RFC 7616 section 3.4).",
    "charset": "Encoding hint for username and password; RFC 7616 section 3.3 defines only the value UTF-8.",
    "userhash": "When true, the client sends the username hashed as H(username:realm:password) instead of cleartext (RFC 7616 section 3.4.4); the server must still support cleartext username for interoperability.",
    "cnonce": "Hint that the client will need its own nonce (cnonce) when a -sess algorithm or qop is used; RFC 7616 section 3.4.2 requires cnonce whenever qop is present.",
    "nc": "Hint that the client must track and send the nonce count (00000001 style hex) alongside the nonce (RFC 7616 section 3.4.2).",
}

_DIGEST_ALGORITHMS: ClassVar[list[dict[str, Any]]] = [
    {
        "name": "MD5",
        "strength": "weak",
        "notes": [
            "Unsalted MD5; cryptographically broken for collision resistance and feasible to accelerate.",
            "RFC 7616 keeps MD5 only for backward compatibility with RFC 2617 deployments.",
        ],
    },
    {
        "name": "MD5-sess",
        "strength": "weak",
        "notes": [
            "MD5-based session variant: as weak as MD5.",
            "-sess semantics: A1 = H(username:realm:password):nonce:cnonce, so the client MUST generate a fresh cnonce and maintain the nonce count (nc).",
        ],
    },
    {"name": "SHA-256", "strength": "strong", "notes": ["Current-generation hash for Digest; the recommended default of the SHA-256 family."]},
    {
        "name": "SHA-256-sess",
        "strength": "strong",
        "notes": ["Session variant of SHA-256.", "Requires a client-generated cnonce and nonce-count tracking."],
    },
    {"name": "SHA-512-256", "strength": "strong", "notes": ["SHA-512 truncated to 256 bits; RFC 7616 interoperable option."]},
    {
        "name": "SHA-512-256-sess",
        "strength": "strong",
        "notes": ["Session variant of SHA-512-256.", "Requires a client-generated cnonce and nonce-count tracking."],
    },
]

_DIGEST_ALGORITHM_NAMES: ClassVar[frozenset[str]] = frozenset(entry["name"] for entry in _DIGEST_ALGORITHMS)

# Codes from RFC 6750 section 3 that carry a client-side remediation.
_BEARER_SECURITY_HINTS: ClassVar[dict[str, str]] = {
    "invalid_request": "Request-side problem: fix the request (missing/duplicated/malformed parameters) rather than refreshing the token.",
    "invalid_token": "Token is expired, revoked, malformed or wrong-audience: obtain and send a fresh access token.",
    "insufficient_scope": "Authorization gap, not authentication failure: request the scopes named in the scope param.",
}


class WwwAuthenticateTool(Tool):
    """Parse, explain, build, and compare WWW-Authenticate/Proxy-Authenticate challenge headers.

    Modes (strict, deterministic, stdlib-only, bounded):
      - ``parse``:   ``header`` (+ optional ``scheme`` hint) -> challenges, errors, notes
      - ``explain``: ``challenge`` -> per-param meanings, embedded registries, security notes
      - ``build``:   ``scheme``+``params`` (or ``challenges`` list) -> canonical header value
      - ``compare``: ``header_a``/``header_b`` -> challenge/param diff
    """

    max_header_chars: int = 262144
    max_challenges: int = 256
    max_params_per_challenge: int = 64
    max_param_name_chars: int = 256
    max_param_value_chars: int = 8192
    max_token68_chars: int = 16384
    max_error_entries: int = 100
    max_note_entries: int = 64

    def execute(
        self,
        mode: str,
        header: str | None = None,
        scheme: str | None = None,
        challenge: str | None = None,
        params: dict[str, Any] | None = None,
        token68: str | None = None,
        challenges: list[dict[str, Any]] | None = None,
        header_a: str | None = None,
        header_b: str | None = None,
    ) -> dict[str, Any]:
        operation = mode if isinstance(mode, str) else mode
        try:
            operation = self._mode(mode)
            if operation == "parse":
                return self._parse_mode(header, scheme)
            if operation == "explain":
                return self._explain_mode(challenge)
            if operation == "build":
                return self._build_mode(scheme, params, token68, challenges)
            return self._compare_mode(header_a, header_b)
        except (TypeError, ValueError) as exc:
            return self._error(operation, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive boundary
            return self._error(mode, "operation_error", f"Challenge header processing failed: {exc}")

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_caps(self) -> None:
        for name in (
            "max_header_chars",
            "max_challenges",
            "max_params_per_challenge",
            "max_param_name_chars",
            "max_param_value_chars",
            "max_token68_chars",
            "max_error_entries",
            "max_note_entries",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in {"parse", "explain", "build", "compare"}:
            raise ValueError("mode must be parse, explain, build, or compare")
        return operation

    @staticmethod
    def _required_string(name: str, value: Any) -> str:
        if value is None:
            raise ValueError(f"{name} is required for this mode")
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        if value == "":
            raise ValueError(f"{name} must be a non-empty string")
        return value

    # ------------------------------------------------------------------- parse

    def _parse_mode(self, header: Any, scheme_hint: Any) -> dict[str, Any]:
        self._validate_caps()
        value = self._required_string("header", header)
        if scheme_hint is not None and (not isinstance(scheme_hint, str) or not scheme_hint.strip()):
            raise ValueError("scheme hint must be a non-empty string when provided")
        if len(value) > self.max_header_chars:
            raise ValueError(f"header exceeds max_header_chars ({self.max_header_chars})")

        parsed = self._parse_header(value)
        challenges = parsed["challenges"]
        errors: list[dict[str, Any]] = parsed["errors"]
        notes: list[str] = parsed["notes"]
        if not challenges:
            self._record_error(errors, "empty_header", "no challenge found in header")
        if scheme_hint is not None:
            wanted = scheme_hint.strip().lower()
            matches = [item for item in challenges if item["scheme"].lower() == wanted]
            if matches:
                notes.append(f"scheme hint '{scheme_hint}' matched {len(matches)} challenge(s)")
            else:
                errors.append(
                    {
                        "code": "scheme_mismatch",
                        "detail": (
                            f"scheme hint '{scheme_hint}' not among parsed schemes: "
                            + (", ".join(item["scheme"] for item in challenges) or "none")
                        ),
                    }
                )
        status = "success" if challenges and not errors else ("partial" if challenges else "error")
        return {
            "status": status,
            "mode": "parse",
            "challenges": challenges,
            "challenge_count": len(challenges),
            "errors": errors,
            "notes": notes,
        }

    def _parse_header(self, value: str) -> dict[str, Any]:
        errors: list[dict[str, Any]] = []
        notes: list[str] = []
        segments, split_errors = self._split_segments(value)
        for code, detail in split_errors:
            self._record_error(errors, code, detail)

        challenges: list[dict[str, Any]] = []
        seen_lower_scheme = False
        seen_case_variant = False
        for index, segment in enumerate(segments):
            if len(challenges) >= self.max_challenges:
                self._record_error(
                    errors,
                    "too_many_challenges",
                    f"stopped at max_challenges ({self.max_challenges}); remaining segments not parsed",
                )
                break
            stripped = segment.strip(" \t")
            if not stripped:
                self._record_error(errors, "empty_segment", f"empty challenge/param at segment {index}")
                continue
            self._parse_segment(stripped, index, challenges, errors, notes)
            if challenges:
                last = challenges[-1]
                low = last["scheme"].lower()
                if any(item["scheme"].lower() == low for item in challenges[:-1]):
                    seen_lower_scheme = True
                if last["scheme_raw"] != last["scheme"]:
                    seen_case_variant = True

        notes.append(
            "scheme tokens and auth-param names are case-insensitive; registered schemes are canonical-cased "
            "(e.g. basic -> Basic) and param names are stored lowercase, original spellings kept in scheme_raw/raw"
        )
        if seen_case_variant:
            notes.append("at least one scheme was written in non-canonical case; canonical form used for the scheme field")
        if seen_lower_scheme:
            notes.append("the same scheme appears more than once; RFC 7235 permits repeated challenges of one scheme")
        notes.append(
            "boundary rule: segments shaped 'name=value' continue the previous challenge, bare-token segments start "
            "a new one; RFC 7235 section 4.1 notes this grammar is inherently ambiguous when a param value list "
            "collides with a following scheme, so boundary anomalies are reported as errors instead of guessed"
        )
        self._trim_notes(notes)
        return {"challenges": challenges, "errors": errors, "notes": notes}

    def _split_segments(self, value: str) -> tuple[list[str], list[tuple[str, str]]]:
        segments: list[str] = []
        buffer: list[str] = []
        in_quotes = False
        quote_segment = -1
        index = 0
        control_seen = -1
        while index < len(value):
            char = value[index]
            if in_quotes:
                if char == "\\" and index + 1 < len(value):
                    buffer.append(char)
                    buffer.append(value[index + 1])
                    index += 2
                    continue
                if char == '"':
                    in_quotes = False
                buffer.append(char)
            elif char == '"':
                in_quotes = True
                if quote_segment < 0:
                    quote_segment = len(segments)
                buffer.append(char)
            elif char == ",":
                segments.append("".join(buffer))
                buffer = []
                quote_segment = -1
            else:
                if char < " " and char != "\t":
                    if control_seen < 0:
                        control_seen = index
                    buffer.append(" ")
                else:
                    buffer.append(char)
            index += 1
        segments.append("".join(buffer))
        problems: list[tuple[str, str]] = []
        if control_seen >= 0:
            problems.append(
                (
                    "control_character",
                    f"control character at offset {control_seen} is not valid in a header value; replaced with a space",
                )
            )
        if in_quotes:
            problems.append(("unterminated_quote", f"quoted string opened at segment {max(quote_segment, 0)} never closes"))
        return segments, problems

    def _parse_segment(
        self,
        segment: str,
        index: int,
        challenges: list[dict[str, Any]],
        errors: list[dict[str, Any]],
        notes: list[str],
    ) -> None:
        match = _TOKEN_RE.match(segment)
        if match is None:
            self._record_error(errors, "invalid_token_start", f"segment {index} does not start with a token: {self._preview(segment)}")
            return
        word = match.group(0)
        rest = segment[match.end():]
        rest_stripped = rest.lstrip(" \t")
        if rest_stripped.startswith("="):
            if rest_stripped != rest:
                self._record_error(errors, "bws_around_equals", f"whitespace around '=' at segment {index} is tolerated but not valid RFC 7235 BWS practice")
            self._attach_param(word, rest_stripped[1:].lstrip(" \t"), index, challenges, errors, notes)
            return
        if rest == "" or rest[0] in " \t":
            self._start_challenge(word, rest.strip(" \t"), index, challenges, errors, notes)
            return
        self._record_error(
            errors,
            "malformed_segment",
            f"segment {index}: '{self._preview(word)}' is followed by neither whitespace nor '=': {self._preview(segment)}",
        )

    def _start_challenge(
        self,
        scheme_raw: str,
        tail: str,
        index: int,
        challenges: list[dict[str, Any]],
        errors: list[dict[str, Any]],
        notes: list[str],
    ) -> None:
        lower = scheme_raw.lower()
        scheme = _CANONICAL_SCHEMES.get(lower, scheme_raw)
        challenge: dict[str, Any] = {
            "scheme": scheme,
            "scheme_raw": scheme_raw,
            "params": {},
            "token68": None,
            "raw": scheme_raw,
        }
        if lower not in _CANONICAL_SCHEMES:
            notes.append(
                f"scheme '{scheme_raw}' is not one of Basic/Bearer/Digest/Negotiate; RFC 7235 allows any token as an auth-scheme, so it is kept as written"
            )
        if tail == "":
            challenges.append(challenge)
            return

        # Tie-break between token68 and auth-param, per the documented rule:
        # schemes that may carry token68 (Negotiate and unregistered schemes)
        # win when the whole tail matches the token68 grammar (covers "="
        # padding), so "Negotiate abc=" is a token68; param-only schemes
        # (Basic/Bearer/Digest) fall through to the auth-param shape, so
        # "Basic realm=" stays an empty param with an error.
        token68_ok = lower in _TOKEN68_SCHEMES or lower not in _CANONICAL_SCHEMES
        if token68_ok and _TOKEN68_RE.fullmatch(tail):
            if len(tail) > self.max_token68_chars:
                self._record_error(errors, "token68_too_long", f"token68 exceeds max_token68_chars ({self.max_token68_chars})")
            challenge["token68"] = tail[: self.max_token68_chars]
            challenge["raw"] = f"{scheme_raw} {challenge['token68']}"
            challenges.append(challenge)
            return
        param_shape = _PARAM_SHAPE_RE.match(tail)
        if param_shape:
            gap = re.match(r"[!#$%&'*+\-.^_`|~0-9A-Za-z]+(\s*)=(\s*)", tail)
            if gap is not None and (gap.group(1) or gap.group(2)):
                self._record_error(
                    errors,
                    "bws_around_equals",
                    f"segment {index}: whitespace around '=' after scheme '{scheme_raw}' is tolerated but not valid RFC 7235 BWS practice",
                )
            self._attach_param(
                param_shape.group("name"),
                param_shape.group("value").lstrip(" \t"),
                index,
                challenges,
                errors,
                notes,
                challenge,
            )
            leftover = self._leftover_after_param(param_shape.group("value"))
            self._salvage_leftover(leftover, index, challenge, errors, notes)
            challenges.append(challenge)
            return
        self._record_error(
            errors,
            "unexpected_content",
            f"segment {index}: content after scheme '{scheme_raw}' is neither a token68 nor an auth-param: {self._preview(tail)}",
        )
        challenges.append(challenge)

    def _attach_param(
        self,
        name: str,
        raw_value: str,
        index: int,
        challenges: list[dict[str, Any]],
        errors: list[dict[str, Any]],
        notes: list[str],
        challenge: dict[str, Any] | None = None,
    ) -> None:
        if challenge is None:
            if not challenges:
                self._record_error(errors, "orphan_param", f"segment {index}: param '{self._preview(name)}=' appears before any scheme")
                return
            challenge = challenges[-1]
        if len(name) > self.max_param_name_chars:
            self._record_error(errors, "param_name_too_long", f"param name exceeds max_param_name_chars ({self.max_param_name_chars})")
            return
        lowered = name.lower()
        value, value_errors = self._parse_value(raw_value, index, lowered)
        for code, detail in value_errors:
            self._record_error(errors, code, detail)
        if challenge["token68"] is not None:
            self._record_error(
                errors,
                "param_with_token68",
                f"segment {index}: auth-param '{lowered}' follows a token68; RFC 7235 allows only one of token68/#auth-param per challenge",
            )
        if len(challenge["params"]) >= self.max_params_per_challenge and lowered not in challenge["params"]:
            self._record_error(
                errors,
                "too_many_params",
                f"challenge '{challenge['scheme']}' exceeds max_params_per_challenge ({self.max_params_per_challenge}); '{lowered}' dropped",
            )
            return
        if lowered in challenge["params"]:
            self._record_error(
                errors,
                "duplicate_param",
                f"challenge '{challenge['scheme']}' repeats param '{lowered}'; the last value wins (documented choice)",
            )
        challenge["params"][lowered] = value
        challenge["raw"] = f"{challenge['raw']}, {lowered}={self._render_value(value)}"

    def _parse_value(self, raw: str, index: int, name: str) -> tuple[str, list[tuple[str, str]]]:
        problems: list[tuple[str, str]] = []
        if raw == "":
            return "", [("empty_param_value", f"segment {index}: param '{name}' has an empty value (empty token is not valid grammar; treated as empty string)")]
        if raw[0] == '"':
            chars: list[str] = []
            position = 1
            closed = False
            while position < len(raw):
                char = raw[position]
                if char == "\\" and position + 1 < len(raw):
                    chars.append(raw[position + 1])
                    position += 2
                    continue
                if char == '"':
                    closed = True
                    position += 1
                    break
                chars.append(char)
                position += 1
            value = "".join(chars)
            if not closed:
                problems.append(
                    (
                        "unterminated_quote",
                        f"segment {index}: quoted value for '{name}' never closes; salvaged the remaining text as the value",
                    )
                )
            else:
                leftover = raw[position:].strip(" \t")
                if leftover:
                    problems.append(
                        (
                            "unexpected_content_after_quote",
                            f"segment {index}: extra content after the quoted value of '{name}': {self._preview(leftover)}",
                        )
                    )
            if len(value) > self.max_param_value_chars:
                value = value[: self.max_param_value_chars]
                problems.append(
                    (
                        "param_value_too_long",
                        f"segment {index}: value of '{name}' exceeds max_param_value_chars ({self.max_param_value_chars}); truncated",
                    )
                )
            return value, problems
        token_match = _TOKEN_RE.match(raw)
        if token_match is None:
            first = raw.split(" ", 1)[0]
            problems.append(
                (
                    "invalid_param_value",
                    f"segment {index}: value of '{name}' starts with a non-token character: {self._preview(first)}",
                )
            )
            value = raw.split(" ", 1)[0][: self.max_param_value_chars]
            return value, problems
        value = token_match.group(0)
        leftover = raw[token_match.end():].strip(" \t")
        if leftover:
            problems.append(
                (
                    "unexpected_content_after_token",
                    f"segment {index}: content after the token value of '{name}': {self._preview(leftover)}",
                )
            )
        if len(value) > self.max_param_value_chars:
            value = value[: self.max_param_value_chars]
            problems.append(
                (
                    "param_value_too_long",
                    f"segment {index}: value of '{name}' exceeds max_param_value_chars ({self.max_param_value_chars}); truncated",
                )
            )
        return value, problems

    def _leftover_after_param(self, raw_value: str) -> str:
        if raw_value.startswith('"'):
            position = 1
            while position < len(raw_value):
                char = raw_value[position]
                if char == "\\" and position + 1 < len(raw_value):
                    position += 2
                    continue
                if char == '"':
                    return raw_value[position + 1 :].strip(" \t")
                position += 1
            return ""
        token_match = _TOKEN_RE.match(raw_value)
        if token_match is None:
            return raw_value.split(" ", 1)[1].strip(" \t") if " " in raw_value else ""
        return raw_value[token_match.end():].strip(" \t")

    def _salvage_leftover(
        self,
        leftover: str,
        index: int,
        challenge: dict[str, Any],
        errors: list[dict[str, Any]],
        notes: list[str],
    ) -> None:
        rest = leftover
        guard = 0
        while rest and guard < self.max_params_per_challenge:
            guard += 1
            shape = _PARAM_SHAPE_RE.match(rest)
            if shape is None:
                self._record_error(
                    errors,
                    "missing_comma",
                    f"segment {index}: '{self._preview(rest)}' follows a param without a separating comma and is not a param",
                )
                return
            self._record_error(
                errors,
                "missing_comma",
                f"segment {index}: param '{shape.group('name')}=' is separated by whitespace, not a comma; salvaged",
            )
            self._attach_param(shape.group("name"), shape.group("value").lstrip(" \t"), index, [challenge], errors, notes, challenge)
            rest = self._leftover_after_param(shape.group("value"))

    def _record_error(self, errors: list[dict[str, Any]], code: str, detail: str) -> None:
        if len(errors) >= self.max_error_entries:
            if len(errors) == self.max_error_entries:
                errors.append({"code": "error_list_truncated", "detail": f"only the first max_error_entries ({self.max_error_entries}) errors are reported"})
            return
        errors.append({"code": code, "detail": detail})

    def _trim_notes(self, notes: list[str]) -> None:
        del notes[self.max_note_entries:]

    @staticmethod
    def _preview(text: str) -> str:
        snippet = text[:60]
        return snippet if len(text) <= 60 else f"{snippet}..."

    # ----------------------------------------------------------------- explain

    def _explain_mode(self, challenge: Any) -> dict[str, Any]:
        self._validate_caps()
        value = self._required_string("challenge", challenge)
        if len(value) > self.max_header_chars:
            raise ValueError(f"challenge exceeds max_header_chars ({self.max_header_chars})")
        parsed = self._parse_header(value)
        challenges = parsed["challenges"]
        if not challenges:
            return {
                "status": "error",
                "mode": "explain",
                "error_type": "validation_error",
                "error": "no challenge found in the provided text",
                "errors": parsed["errors"],
            }
        notes: list[str] = list(parsed["notes"])
        if len(challenges) > 1:
            notes.append(f"{len(challenges)} challenges supplied; explaining the first one ({challenges[0]['scheme']})")
        head = challenges[0]
        lower = head["scheme"].lower()
        explained_params = self._explain_params(head)
        tables = self._tables_for(lower)
        security_notes = self._security_notes(lower, head)
        return {
            "status": "success" if not parsed["errors"] else "partial",
            "mode": "explain",
            "scheme": head["scheme"],
            "scheme_raw": head["scheme_raw"],
            "scheme_meaning": _SCHEME_MEANINGS.get(lower, "Unregistered scheme; RFC 7235 allows any token as an auth-scheme."),
            "token68": head["token68"],
            "token68_meaning": self._token68_meaning(head),
            "params": explained_params,
            "param_count": len(explained_params),
            "tables": tables,
            "security_notes": security_notes,
            "errors": parsed["errors"],
            "notes": notes,
        }

    def _explain_params(self, challenge: dict[str, Any]) -> list[dict[str, Any]]:
        lower = challenge["scheme"].lower()
        registry: dict[str, str]
        if lower == "basic":
            registry = _BASIC_PARAM_MEANINGS
        elif lower == "bearer":
            registry = _BEARER_PARAM_MEANINGS
        elif lower == "digest":
            registry = _DIGEST_PARAM_MEANINGS
        else:
            registry = {}
        explained: list[dict[str, Any]] = []
        for name, value in challenge["params"].items():
            meaning = registry.get(name, "Unregistered parameter; not defined by this scheme's RFC grammar (kept as parsed).")
            entry: dict[str, Any] = {"name": name, "value": value, "meaning": meaning}
            if lower == "bearer" and name == "error" and value not in {item["code"] for item in _BEARER_ERROR_REGISTRY}:
                entry["meaning"] += " This value is NOT in the RFC 6750 section 3 registry; it may be a vendor extension drawn from the OAuth registry (see oauth_error_codes)."
            if lower == "digest" and name == "algorithm" and value not in _DIGEST_ALGORITHM_NAMES:
                entry["meaning"] += " Unregistered algorithm token; RFC 7616 allows extension algorithms, treat strength as unknown."
            explained.append(entry)
        return explained

    def _tables_for(self, lower: str) -> dict[str, Any]:
        tables: dict[str, Any] = {}
        if lower == "bearer":
            tables["bearer_error_registry"] = _BEARER_ERROR_REGISTRY
            tables["oauth_error_codes"] = [
                {"code": code, "meaning": meaning} for code, meaning in _OAUTH_ERROR_CODES.items()
            ]
        if lower == "digest":
            tables["digest_algorithms"] = _DIGEST_ALGORITHMS
        return tables

    def _security_notes(self, lower: str, challenge: dict[str, Any]) -> list[str]:
        params = challenge["params"]
        notes: list[str] = []
        if lower == "basic":
            notes.append("Basic sends credentials as base64 text - an encoding, not encryption: never use it outside TLS.")
            charset = params.get("charset")
            if charset is not None and charset.upper() != "UTF-8":
                notes.append(f"charset '{charset}' is not UTF-8; RFC 7617 section 2.1 defines only UTF-8 and legacy behavior differs.")
        elif lower == "bearer":
            error = params.get("error", "")
            hint = _BEARER_SECURITY_HINTS.get(error)
            if hint:
                notes.append(f"error={error}: {hint}")
            if "scope" in params:
                notes.append("scope values are space-delimited per RFC 6749 section 3.3; compare them one scope at a time, never as a whole string.")
        elif lower == "digest":
            algorithm = params.get("algorithm", "MD5")
            entry = next((item for item in _DIGEST_ALGORITHMS if item["name"].lower() == algorithm.lower()), None)
            if entry is not None:
                notes.extend(f"algorithm={entry['name']}: {note}" for note in entry["notes"])
                if entry["strength"] == "weak":
                    notes.append(f"algorithm={entry['name']} is cryptographically weak; prefer SHA-256 or SHA-512-256.")
            else:
                notes.append(f"algorithm={algorithm} is not in the RFC 7616 registry; strength unknown.")
            stale = params.get("stale", "").lower()
            if stale == "true":
                notes.append("stale=true: the nonce expired but the credentials were accepted - retry the request with the SAME credentials and the newly issued nonce.")
            elif "stale" in params:
                notes.append("stale=false: the credentials themselves were rejected; retrying with a new nonce will not help.")
            if "qop" not in params:
                notes.append("No qop offered: the challenge falls back to legacy RFC 2069 compatibility mode, which is weaker (no cnonce/nc binding).")
            if params.get("userhash", "").lower() == "true":
                notes.append("userhash=true: the client will hash the username (H(username:realm:password)) before sending it.")
        elif lower == "negotiate":
            notes.extend(self._negotiate_notes(challenge))
        if "realm" in params:
            notes.append("realm is a protection-space label, not an origin: it is compared case-insensitively only as a display convention and must be combined with the canonical root URI.")
        return notes

    def _token68_meaning(self, challenge: dict[str, Any]) -> str | None:
        if challenge["token68"] is None:
            if challenge["scheme"].lower() == "negotiate":
                return "Challenge without a token: the server invites the client to start the SPNEGO/GSSAPI exchange."
            return None
        return (
            "Raw token68 payload (base64-style, '='-padded): for Negotiate this is a GSSAPI mechanism token, "
            "typically SPNEGO wrapping Kerberos; a second Negotiate challenge carrying the server continuation "
            "token may follow the client response (RFC 4559)."
        )

    @staticmethod
    def _negotiate_notes(challenge: dict[str, Any]) -> list[str]:
        notes = [
            "Negotiate payloads are SPNEGO/GSSAPI mechanism tokens; do not log them - they may embed authenticator material.",
        ]
        if challenge["params"]:
            notes.append("auth-params alongside a token68 violate RFC 7235 (token68 and #auth-param are mutually exclusive); see errors.")
        return notes

    # ------------------------------------------------------------------- build

    def _build_mode(
        self,
        scheme: Any,
        params: Any,
        token68: Any,
        challenges: Any,
    ) -> dict[str, Any]:
        self._validate_caps()
        errors: list[dict[str, Any]] = []
        parts: list[str] = []
        if challenges is not None:
            if not isinstance(challenges, list) or not challenges:
                raise ValueError("challenges must be a non-empty list of {scheme, params, token68} objects")
            if len(challenges) > self.max_challenges:
                raise ValueError(f"challenges exceeds max_challenges ({self.max_challenges})")
            for item in challenges:
                parts.append(self._build_one(item.get("scheme"), item.get("params") or {}, item.get("token68"), errors))
        else:
            if scheme is None:
                raise ValueError("scheme (or challenges) is required for mode='build'")
            if token68 is not None and params:
                raise ValueError("token68 and params are mutually exclusive in one challenge (RFC 7235)")
            parts.append(self._build_one(scheme, params or {}, token68, errors))
        if any(part is None for part in parts):
            return {"status": "error", "mode": "build", "errors": errors}
        value = ", ".join(part for part in parts if part)
        return {
            "status": "success" if not errors else "partial",
            "mode": "build",
            "value": value,
            "challenge_count": len(parts),
            "notes": [
                "parameters are serialized in the order given (deterministic, not sorted)",
                "values that are not bare tokens are emitted as quoted strings with '\\' and '\"' escaped per RFC 7235 auth-param grammar",
                "multiple challenges are joined with ', '",
            ],
            "errors": errors,
        }

    def _build_one(self, scheme: Any, params: Any, token68: Any, errors: list[dict[str, Any]]) -> str | None:
        if not isinstance(scheme, str) or not scheme.strip():
            self._record_error(errors, "invalid_scheme", "each challenge needs a non-empty scheme token")
            return None
        scheme_text = scheme.strip()
        if _TOKEN_RE.fullmatch(scheme_text) is None:
            self._record_error(errors, "invalid_scheme", f"scheme '{self._preview(scheme_text)}' is not a valid RFC 7230 token")
            return None
        if params is None:
            params = {}
        if not isinstance(params, dict):
            self._record_error(errors, "invalid_params", f"params for scheme '{scheme_text}' must be an object of name -> value")
            return None
        if len(params) > self.max_params_per_challenge:
            self._record_error(errors, "too_many_params", f"params exceeds max_params_per_challenge ({self.max_params_per_challenge})")
            return None
        rendered: list[str] = []
        for name, value in params.items():
            if not isinstance(name, str) or _TOKEN_RE.fullmatch(name) is None:
                self._record_error(errors, "invalid_param_name", f"param name {name!r} is not a valid token")
                return None
            if isinstance(value, bool):
                text = "true" if value else "false"
            elif isinstance(value, (int, float)):
                text = str(value)
            elif isinstance(value, str):
                text = value
            else:
                self._record_error(errors, "invalid_param_value", f"value of '{name}' must be a string, number, or boolean")
                return None
            if len(text) > self.max_param_value_chars:
                self._record_error(errors, "param_value_too_long", f"value of '{name}' exceeds max_param_value_chars ({self.max_param_value_chars})")
                return None
            if any(ch != "\t" and not (" " <= ch <= "~" or ord(ch) >= 0x80) for ch in text):
                self._record_error(errors, "invalid_param_value", f"value of '{name}' contains characters that cannot be serialized into a header")
                return None
            rendered.append(f"{name}={self._render_value(text)}")
        token_text = ""
        if token68 is not None:
            if not isinstance(token68, str) or _TOKEN68_RE.fullmatch(token68) is None:
                self._record_error(errors, "invalid_token68", f"token68 {token68!r} does not match the token68 grammar")
                return None
            if len(token68) > self.max_token68_chars:
                self._record_error(errors, "token68_too_long", f"token68 exceeds max_token68_chars ({self.max_token68_chars})")
                return None
            if rendered:
                self._record_error(errors, "token68_and_params", "token68 and params are mutually exclusive in one challenge (RFC 7235)")
                return None
            token_text = f" {token68}"
        body = ", ".join(rendered)
        return f"{scheme_text}{token_text}" + (f" {body}" if body else "")

    @staticmethod
    def _render_value(text: str) -> str:
        if text != "" and _TOKEN_RE.fullmatch(text) is not None:
            return text
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    # ---------------------------------------------------------------- compare

    def _compare_mode(self, header_a: Any, header_b: Any) -> dict[str, Any]:
        self._validate_caps()
        first = self._required_string("header_a", header_a)
        second = self._required_string("header_b", header_b)
        if len(first) > self.max_header_chars or len(second) > self.max_header_chars:
            raise ValueError(f"header exceeds max_header_chars ({self.max_header_chars})")
        parsed_a = self._parse_header(first)
        parsed_b = self._parse_header(second)

        def index_by_scheme(challenges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
            mapping: dict[str, dict[str, Any]] = {}
            for item in challenges:
                mapping.setdefault(item["scheme"].lower(), item)
            return mapping

        map_a = index_by_scheme(parsed_a["challenges"])
        map_b = index_by_scheme(parsed_b["challenges"])
        notes: list[str] = []
        for label, mapping, parsed in (("a", map_a, parsed_a), ("b", map_b, parsed_b)):
            counts = [item["scheme"].lower() for item in parsed["challenges"]]
            duplicated = {name for name in counts if counts.count(name) > 1}
            if duplicated:
                notes.append(f"header {label} repeats scheme(s) {', '.join(sorted(duplicated))}; only the first occurrence is compared")

        only_in_a = [map_a[key]["scheme"] for key in sorted(set(map_a) - set(map_b))]
        only_in_b = [map_b[key]["scheme"] for key in sorted(set(map_b) - set(map_a))]
        per_scheme: list[dict[str, Any]] = []
        same = not only_in_a and not only_in_b
        for key in sorted(set(map_a) & set(map_b)):
            left, right = map_a[key], map_b[key]
            added = sorted(set(right["params"]) - set(left["params"]))
            removed = sorted(set(left["params"]) - set(right["params"]))
            changed = [
                {"name": name, "a": left["params"][name], "b": right["params"][name]}
                for name in sorted(set(left["params"]) & set(right["params"]))
                if left["params"][name] != right["params"][name]
            ]
            token_changed = left["token68"] != right["token68"]
            if added or removed or changed or token_changed:
                same = False
            per_schema_entry: dict[str, Any] = {
                "scheme": left["scheme"],
                "params_added_in_b": added,
                "params_removed_in_b": removed,
                "params_changed": changed,
            }
            if token_changed:
                per_schema_entry["token68_change"] = {"a": left["token68"], "b": right["token68"]}
            per_scheme.append(per_schema_entry)
        errors = [dict(error, header="a") for error in parsed_a["errors"]] + [
            dict(error, header="b") for error in parsed_b["errors"]
        ]
        return {
            "status": "success" if not errors else "partial",
            "mode": "compare",
            "same": same,
            "schemes_only_in_a": only_in_a,
            "schemes_only_in_b": only_in_b,
            "schemes_compared": [entry["scheme"] for entry in per_scheme],
            "per_scheme": per_scheme,
            "errors": errors,
            "notes": notes,
        }
