#!/usr/bin/env python3
"""Offline JWT structure decoding, claims analysis, and algorithm auditing."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import binascii
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_B64URL_RE = re.compile(r"^[A-Za-z0-9_-]*$")
_B64URL_CHAR_RE = re.compile(r"[A-Za-z0-9_-]")
_REGISTERED_CLAIMS = ("exp", "nbf", "iat", "iss", "aud", "sub")


class JwtTool(Tool):
    """Decode JWT structure and analyze claims and algorithm safety without secrets.

    The tool never verifies signatures and never accepts or stores keys: it
    parses the compact serialization, reports structure errors, performs
    registered-claim time math against a caller-supplied instant, and audits
    the header for algorithm-confusion and untrusted-key-fetch indicators.
    Claim string values longer than ``mask_length`` characters are masked by
    default because decoded claims may carry personal data or secrets.
    """

    max_token_bytes: int = 65536
    max_payload_bytes: int = 262144
    max_claims: int = 200
    max_array_items: int = 50
    max_depth: int = 8
    max_nested_depth: int = 1
    mask_length: int = 24
    max_unmasked_preview: int = 512
    mask_strings: bool = True

    _MODES: ClassVar[set[str]] = {"decode", "analyze_claims", "audit_alg", "explain"}
    _ZERO_WIDTH: ClassVar[dict[str, str]] = {
        "\u200b": "ZWSP U+200B",
        "\u200c": "ZWNJ U+200C",
        "\u200d": "ZWJ U+200D",
        "\u2060": "WJ U+2060",
        "\ufeff": "ZWNBSP U+FEFF",
    }
    _ALG_FAMILIES: ClassVar[dict[str, str]] = {
        "none": "unsecured (no signature)",
        "HS256": "HMAC-SHA-256, symmetric shared secret",
        "HS384": "HMAC-SHA-384, symmetric shared secret",
        "HS512": "HMAC-SHA-512, symmetric shared secret",
        "RS256": "RSASSA-PKCS1-v1_5 with SHA-256, asymmetric RSA",
        "RS384": "RSASSA-PKCS1-v1_5 with SHA-384, asymmetric RSA",
        "RS512": "RSASSA-PKCS1-v1_5 with SHA-512, asymmetric RSA",
        "PS256": "RSASSA-PSS with SHA-256, asymmetric RSA",
        "PS384": "RSASSA-PSS with SHA-384, asymmetric RSA",
        "PS512": "RSASSA-PSS with SHA-512, asymmetric RSA",
        "ES256": "ECDSA with P-256 and SHA-256, asymmetric",
        "ES384": "ECDSA with P-384 and SHA-384, asymmetric",
        "ES512": "ECDSA with P-521 and SHA-512, asymmetric",
        "ES256K": "ECDSA with secp256k1 and SHA-256, asymmetric",
        "EdDSA": "Ed25519 or Ed448 signatures, asymmetric",
    }
    _KID_SUSPICIOUS: ClassVar[tuple[str, ...]] = ("../", "..\\", "://", "\\\\", "/etc/", "%2e%2e")

    def execute(
        self,
        mode: str,
        token: str,
        now: str | None = None,
        skew_seconds: int = 0,
        expected_aud: str | None = None,
        expected_iss: str | None = None,
        mask_strings: bool | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            mask = self.mask_strings if mask_strings is None else self._mask_flag(mask_strings)
            skew = self._skew(skew_seconds)
            self._expected(expected_aud, "expected_aud")
            self._expected(expected_iss, "expected_iss")
            parsed_now = self._now(now)
            text, bearer_stripped = self._token_text(token)
            core = self._decode_core(text)
            if operation == "decode":
                core["bearer_prefix_stripped"] = bearer_stripped
                return self._decode_result(core, mask)
            if core["status"] == "error":
                core["mode"] = operation
                return core
            if operation == "analyze_claims":
                return self._analyze(core, parsed_now, skew, expected_aud, expected_iss, mask)
            if operation == "audit_alg":
                return self._audit(core)
            return self._explain(core, parsed_now, skew, expected_aud, expected_iss, mask, bearer_stripped)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:
            return self._error(mode, "operation_error", f"JWT analysis failed: {exc}")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in ("max_token_bytes", "max_payload_bytes", "max_claims", "max_array_items", "max_depth"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        nested = self.max_nested_depth
        if isinstance(nested, bool) or not isinstance(nested, int) or not 0 <= nested <= 2:
            raise ValueError("max_nested_depth must be an integer between 0 and 2")
        length = self.mask_length
        if isinstance(length, bool) or not isinstance(length, int) or not 4 <= length <= 1024:
            raise ValueError("mask_length must be an integer between 4 and 1024")
        preview = self.max_unmasked_preview
        if isinstance(preview, bool) or not isinstance(preview, int) or preview < length:
            raise ValueError("max_unmasked_preview must be an integer >= mask_length")
        if not isinstance(self.mask_strings, bool):
            raise TypeError("mask_strings must be a boolean")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in JwtTool._MODES:
            raise ValueError("mode must be decode, analyze_claims, audit_alg, or explain")
        return operation

    @staticmethod
    def _mask_flag(value: Any) -> bool:
        if not isinstance(value, bool):
            raise TypeError("mask_strings must be a boolean")
        return value

    @staticmethod
    def _skew(value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("skew_seconds must be an integer")
        if not 0 <= value <= 86400:
            raise ValueError("skew_seconds must be between 0 and 86400")
        return value

    @staticmethod
    def _expected(value: Any, name: str) -> None:
        if value is None:
            return
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")
        if len(value) > 512:
            raise ValueError(f"{name} exceeds 512 characters")

    @staticmethod
    def _now(value: Any) -> float | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("now must be a non-empty ISO 8601 string")
        if len(value) > 64:
            raise ValueError("now exceeds 64 characters")
        text = value.strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            moment = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"now must be an ISO 8601 timestamp: {exc}") from exc
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return moment.timestamp()

    def _token_text(self, value: Any) -> tuple[str, bool]:
        if not isinstance(value, str):
            raise TypeError("token must be a string")
        text = value.strip()
        if not text:
            raise ValueError("token must be a non-empty string")
        if len(text) > self.max_token_bytes:
            raise ValueError(f"token exceeds max_token_bytes ({self.max_token_bytes})")
        stripped = False
        if text[:7].lower() == "bearer " or text.lower() == "bearer":
            text = text[7:].strip()
            stripped = True
            if not text:
                raise ValueError("token contains only a bearer prefix")
        return text, stripped

    @staticmethod
    def _structure_error(code: str, severity: str, detail: str, segment: str | None = None) -> dict[str, Any]:
        entry = {"code": code, "severity": severity, "detail": detail}
        if segment:
            entry["segment"] = segment
        return entry

    def _decode_core(self, text: str) -> dict[str, Any]:  # noqa: C901
        """Split and decode segments; blocking failures still carry best-effort parts."""
        errors: list[dict[str, Any]] = []
        core: dict[str, Any] = {
            "status": "success",
            "text": text,
            "segment_count": 0,
            "token_form": None,
            "header": None,
            "payload": None,
            "payload_raw": None,
            "signature_text": None,
            "structure_errors": errors,
        }
        parts = text.split(".")
        core["segment_count"] = len(parts)
        if len(parts) not in (2, 3):
            errors.append(
                self._structure_error(
                    "segment_count",
                    "high",
                    f"token has {len(parts)} segments; the compact serialization requires 2 (unsecured) or 3 (JWS)",
                )
            )
            core["status"] = "error"
            return core
        core["token_form"] = "unsecured" if len(parts) == 2 else "JWS"
        for index, name in enumerate(("header", "payload")):
            if not parts[index]:
                errors.append(self._structure_error("empty_segment", "high", f"{name} segment is empty", name))
                core["status"] = "error"
        header_obj, _header_text = self._decode_segment(parts[0], "header", errors)
        payload_obj, payload_text = self._decode_segment(parts[1], "payload", errors)
        core["payload_raw"] = payload_text
        if not isinstance(header_obj, dict):
            if header_obj is not None:
                errors.append(
                    self._structure_error("header_not_object", "high", "decoded header is not a JSON object", "header")
                )
            core["status"] = "error"
        core["header"] = header_obj if isinstance(header_obj, dict) else None
        nested_form = isinstance(header_obj, dict) and str(header_obj.get("cty", "")).lower() == "jwt"
        if isinstance(payload_obj, dict) or (isinstance(payload_obj, str) and nested_form):
            core["payload"] = payload_obj
        elif payload_obj is not None:
            errors.append(
                self._structure_error("payload_not_object", "high", "decoded payload is not a JSON object", "payload")
            )
        if core["payload"] is None:
            core["status"] = "error"
        if len(parts) == 3:
            core["signature_text"] = parts[2]
            if isinstance(core["header"], dict) and str(core["header"].get("alg", "")).lower() == "none":
                errors.append(
                    self._structure_error(
                        "alg_none_unsecured",
                        "high",
                        'header declares alg "none" while a signature segment is present',
                    )
                )
        else:
            errors.append(
                self._structure_error(
                    "alg_none_unsecured",
                    "high",
                    "two-segment form: unsecured JWT (alg none); content is not signed and anyone could have produced it",
                )
            )
        if core["status"] == "error":
            core["error_type"] = "structure_error"
        return core

    def _decode_segment(self, text: str, name: str, errors: list[dict[str, Any]]) -> tuple[Any, str | None]:
        raw = self._b64url_decode(text, name, errors)
        if raw is None:
            return None, None
        if len(raw) > self.max_payload_bytes:
            errors.append(
                self._structure_error(
                    "segment_oversize",
                    "high",
                    f"decoded {name} exceeds max_payload_bytes ({self.max_payload_bytes}); it was not parsed",
                    name,
                )
            )
            return None, None
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(self._structure_error("invalid_utf8", "high", f"{name} segment is not valid UTF-8", name))
            return None, None
        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError as exc:
            errors.append(
                self._structure_error("invalid_json", "high", f"{name} segment is not valid JSON: {exc.msg}", name)
            )
            return None, decoded
        found = sorted({self._ZERO_WIDTH[ch] for ch in decoded if ch in self._ZERO_WIDTH})
        if not found:
            found = self._zero_width_in_values(parsed)
        if found:
            errors.append(
                self._structure_error(
                    "zero_width_chars",
                    "high",
                    f"decoded {name} JSON contains zero-width characters ({', '.join(found)}); "
                    "content decoded but visual-spoofing is possible",
                    name,
                )
            )
        return parsed, decoded

    def _zero_width_in_values(self, value: Any) -> list[str]:
        """Find zero-width characters inside parsed JSON string keys and values."""
        found: set[str] = set()
        if isinstance(value, str):
            found |= {self._ZERO_WIDTH[ch] for ch in value if ch in self._ZERO_WIDTH}
        elif isinstance(value, list):
            for item in value:
                found |= set(self._zero_width_in_values(item))
        elif isinstance(value, dict):
            for key, item in value.items():
                if isinstance(key, str):
                    found |= {self._ZERO_WIDTH[ch] for ch in key if ch in self._ZERO_WIDTH}
                found |= set(self._zero_width_in_values(item))
        return sorted(found)

    def _b64url_decode(self, segment: str, name: str, errors: list[dict[str, Any]]) -> bytes | None:
        found = sorted({self._ZERO_WIDTH[ch] for ch in segment if ch in self._ZERO_WIDTH})
        if found:
            errors.append(
                self._structure_error(
                    "zero_width_chars",
                    "high",
                    f"{name} segment contains zero-width characters ({', '.join(found)}) in its base64url form",
                    name,
                )
            )
            return None
        if "=" in segment:
            errors.append(
                self._structure_error(
                    "base64url_padding",
                    "high",
                    f"{name} segment contains '=' padding; JWT base64url segments are unpadded (RFC 7515 Appendix C)",
                    name,
                )
            )
            return None
        if not _B64URL_RE.match(segment):
            bad = sorted({ch for ch in segment if not _B64URL_CHAR_RE.match(ch)})
            errors.append(
                self._structure_error(
                    "base64url_chars", "high", f"{name} segment contains non-base64url characters: {bad[:10]}", name
                )
            )
            return None
        try:
            return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))
        except (binascii.Error, ValueError) as exc:
            errors.append(
                self._structure_error(
                    "base64url_decode", "high", f"{name} segment failed base64url decoding: {exc}", name
                )
            )
            return None

    def _decode_result(self, core: dict[str, Any], mask: bool) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": core["status"],
            "mode": "decode",
            "token_form": core["token_form"],
            "segment_count": core["segment_count"],
            "bearer_prefix_stripped": core.get("bearer_prefix_stripped", False),
            "header": self._header_view(core["header"], mask),
            "payload": self._payload_view(core, mask),
            "signature": self._signature_view(core["signature_text"]),
            "structure_errors": core["structure_errors"],
        }
        nested = self._nested_view(core, mask, depth=1)
        if nested is not None:
            result["nested"] = nested
        return result

    def _payload_view(self, core: dict[str, Any], mask: bool) -> dict[str, Any]:
        claims = core["payload"]
        if isinstance(claims, dict):
            items = list(claims.items())[: self.max_claims]
            return {
                "claims": {key: self._bound_value(value, mask, 1) for key, value in items},
                "claim_count": len(claims),
                "omitted_claims": max(len(claims) - self.max_claims, 0),
                "registered_claims": [name for name in _REGISTERED_CLAIMS if name in claims],
                "custom_claims": [name for name in claims if name not in _REGISTERED_CLAIMS],
            }
        if isinstance(claims, str):
            return {"claims": {"__nested_jwt__": self._mask_str(claims, mask)}}
        if core["payload_raw"] is not None and not any(
            entry["code"] == "segment_oversize" for entry in core["structure_errors"]
        ):
            return {"claims": {"__raw_preview__": self._mask_str(core["payload_raw"], mask)}}
        return {"claims": None}

    def _nested_view(self, core: dict[str, Any], mask: bool, depth: int) -> dict[str, Any] | None:
        header, claims = core["header"], core["payload"]
        if not isinstance(header, dict) or str(header.get("cty", "")).lower() != "jwt":
            return None
        view: dict[str, Any] = {"depth": depth, "detected": True}
        if not isinstance(claims, str) or claims.count(".") not in (1, 2):
            view.update({"decoded": False, "reason": "payload is not a nested JWT string"})
            return view
        if depth > self.max_nested_depth:
            view.update(
                {
                    "decoded": False,
                    "truncated_at_depth": True,
                    "reason": f"nesting deeper than max_nested_depth ({self.max_nested_depth})",
                }
            )
            return view
        inner = self._decode_core(claims)
        view.update(
            {
                "decoded": True,
                "token_form": inner["token_form"],
                "header": self._header_view(inner["header"], mask),
                "payload": self._payload_view(inner, mask),
                "signature": self._signature_view(inner["signature_text"]),
                "structure_errors": inner["structure_errors"],
                "truncated_at_depth": False,
            }
        )
        inner_nested = self._nested_view(inner, mask, depth + 1)
        if inner_nested is not None:
            view["nested"] = inner_nested
            if inner_nested.get("truncated_at_depth"):
                view["truncated_at_depth"] = True
        return view

    def _header_view(self, header: dict[str, Any] | None, mask: bool) -> dict[str, Any]:
        if header is None:
            return {"fields": None, "alg": None, "typ": None, "kid": None}
        alg = header.get("alg")
        typ = header.get("typ")
        kid = header.get("kid")
        return {
            "fields": {key: self._bound_value(value, mask, 1) for key, value in header.items()},
            "alg": alg if isinstance(alg, str) else self._type_name(alg),
            "typ": typ if isinstance(typ, str) else None,
            "kid": self._mask_str(kid, mask) if isinstance(kid, str) else None,
        }

    @staticmethod
    def _signature_view(signature: str | None) -> dict[str, Any]:
        if signature is None:
            return {"present": False, "length": 0, "format": None}
        if not signature:
            return {"present": False, "length": 0, "format": "empty"}
        return {
            "present": True,
            "length": len(signature),
            "format": "base64url" if _B64URL_RE.match(signature) else "non_base64url",
        }

    def _bound_value(self, value: Any, mask: bool, depth: int) -> Any:
        if depth > self.max_depth:
            return {"__truncated__": "nesting deeper than max_depth"}
        if isinstance(value, str):
            return self._mask_str(value, mask)
        if isinstance(value, list):
            items = [self._bound_value(item, mask, depth + 1) for item in value[: self.max_array_items]]
            if len(value) > self.max_array_items:
                items.append({"__truncated_items__": len(value) - self.max_array_items})
            return items
        if isinstance(value, dict):
            bounded: dict[str, Any] = {}
            for key, item in list(value.items())[: self.max_claims]:
                bounded[key] = self._bound_value(item, mask, depth + 1)
            if len(value) > self.max_claims:
                bounded["__omitted_keys__"] = len(value) - self.max_claims
            return bounded
        return value

    def _mask_str(self, value: str, mask: bool) -> str:
        if mask and len(value) > self.mask_length:
            return f"<masked:{len(value)} chars>"
        if len(value) > self.max_unmasked_preview:
            return value[: self.max_unmasked_preview] + f"<truncated:{len(value)} chars>"
        return value

    @staticmethod
    def _type_name(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, str):
            return "string"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, list):
            return "array"
        return "object"

    @staticmethod
    def _numeric_date(value: Any) -> tuple[bool, Any, str]:
        if isinstance(value, bool):
            return False, value, "boolean"
        if isinstance(value, int):
            return True, value, ""
        if isinstance(value, float):
            if not math.isfinite(value):
                return False, value, "non-finite number"
            return True, value, ""
        return False, value, JwtTool._type_name(value)

    def _analyze(
        self,
        core: dict[str, Any],
        now: float | None,
        skew: int,
        expected_aud: str | None,
        expected_iss: str | None,
        mask: bool,
    ) -> dict[str, Any]:
        if now is None:
            now = datetime.now(timezone.utc).timestamp()
        now_iso = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
        claims = core["payload"] if isinstance(core["payload"], dict) else {}
        checks: dict[str, dict[str, Any]] = {}
        invalid: list[dict[str, Any]] = []
        for name in ("exp", "nbf", "iat"):
            checks[name] = self._time_check(claims, name, now, now_iso, skew, invalid)
        result: dict[str, Any] = {
            "status": "success",
            "mode": "analyze_claims",
            "now": now_iso,
            "skew_seconds": skew,
            "checks": checks,
            "missing_registered_claims": [name for name in _REGISTERED_CLAIMS if name not in claims],
            "audience": self._string_claim_check(claims, "aud", expected_aud, mask),
            "issuer": self._string_claim_check(claims, "iss", expected_iss, mask),
            "custom_claims": {
                name: self._type_name(value) for name, value in claims.items() if name not in _REGISTERED_CLAIMS
            },
            "invalid_numeric_dates": invalid,
        }
        if not isinstance(core["payload"], dict):
            result["payload_note"] = "payload is not a claims object; decode the token for its structure"
        return result

    def _time_check(
        self,
        claims: dict[str, Any],
        name: str,
        now: float,
        now_iso: str,
        skew: int,
        invalid: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if name not in claims:
            return {"present": False, "value": None, "verdict": "absent", "note": "registered claim missing (info)"}
        valid, value, reason = self._numeric_date(claims[name])
        if not valid:
            invalid.append(
                {
                    "claim": name,
                    "reason": f"must be a JSON number (RFC 7519 NumericDate); got {reason}",
                    "check": "skipped",
                }
            )
            return {"present": True, "value": None, "verdict": "invalid", "delta_seconds": None, "math": None}
        delta = round(now - value)
        if name == "exp":
            verdict = "expired" if now - skew > value else "valid"
            relation = f"now - exp = {delta:+d}s"
        elif name == "nbf":
            verdict = "not_yet_valid" if value > now + skew else "valid"
            relation = f"nbf - now = {-delta:+d}s"
        else:
            verdict = "issued_in_future" if value > now + skew else "valid"
            relation = f"iat - now = {-delta:+d}s"
        return {
            "present": True,
            "value": value,
            "verdict": verdict,
            "delta_seconds": delta,
            "math": f"{relation} -> {verdict} (skew {skew}s, now {now_iso})",
        }

    def _string_claim_check(
        self, claims: dict[str, Any], name: str, expected: str | None, mask: bool
    ) -> dict[str, Any]:
        result: dict[str, Any] = {"expected": expected, "verdict": "not_checked", "claim_value": None}
        if expected is None:
            return result
        if name not in claims:
            result["verdict"] = "claim_absent"
            return result
        value = claims[name]
        if name == "aud" and isinstance(value, list):
            members = [item for item in value if isinstance(item, str)]
            result["claim_value"] = [self._mask_str(item, mask) for item in members]
            result["verdict"] = "match" if expected in members else "mismatch"
        elif isinstance(value, str):
            result["claim_value"] = self._mask_str(value, mask)
            result["verdict"] = "match" if value == expected else "mismatch"
        else:
            result["claim_value"] = self._type_name(value)
            result["verdict"] = "invalid_type"
        return result

    def _audit(self, core: dict[str, Any]) -> dict[str, Any]:
        header = core["header"]
        findings: list[dict[str, Any]] = []
        alg_value = header.get("alg")
        alg = alg_value if isinstance(alg_value, str) else None
        self._audit_alg(alg, findings)
        self._audit_crit(header, findings)
        self._audit_kid(header, findings)
        for param, code in (("jku", "jku_untrusted_key_fetch"), ("x5u", "x5u_untrusted_key_fetch")):
            if param in header:
                findings.append(
                    {
                        "code": code,
                        "severity": "high",
                        "detail": f"{param} header points to a URL a verifier would fetch key material from; "
                        "treat as untrusted unless pinned to an allowlist (key-substitution and SSRF vector)",
                    }
                )
        nested = isinstance(header.get("cty"), str) and str(header["cty"]).lower() == "jwt"
        if nested:
            findings.append(
                {
                    "code": "nested_jwt",
                    "severity": "info",
                    "detail": "cty=JWT: payload is a nested JWT; mode=decode inspects one bounded level",
                }
            )
        return {
            "status": "success",
            "mode": "audit_alg",
            "alg": alg,
            "alg_family": self._ALG_FAMILIES.get(alg or "", "unrecognized algorithm"),
            "signature_present": core["token_form"] == "JWS" and bool(core["signature_text"]),  # noqa: S105
            "header_parameters": sorted(header),
            "findings": findings,
            "findings_by_severity": {
                severity: sum(1 for item in findings if item["severity"] == severity)
                for severity in ("critical", "high", "medium", "info")
            },
            "nested_jwt": nested,
        }

    @staticmethod
    def _audit_alg(alg: str | None, findings: list[dict[str, Any]]) -> None:
        if alg is None:
            findings.append({"code": "alg_missing", "severity": "critical", "detail": 'header has no "alg" parameter'})
            return
        if alg.lower() == "none":
            findings.append(
                {
                    "code": "alg_none_unsecured",
                    "severity": "critical",
                    "detail": 'alg "none": the token is unsigned; integrity is not protected and anyone could '
                    "have produced it",
                }
            )
            return
        if alg in ("HS256", "HS384", "HS512"):
            findings.append(
                {
                    "code": "symmetric_alg",
                    "severity": "info",
                    "detail": f"{alg} uses a symmetric shared secret; every party able to verify can also forge "
                    "tokens — prefer asymmetric RS/ES/PS families when multiple parties must verify",
                }
            )
            return
        if alg not in JwtTool._ALG_FAMILIES:
            findings.append(
                {
                    "code": "unknown_alg",
                    "severity": "medium",
                    "detail": f"unrecognized algorithm {alg[:32]}; not in the JOSE registered families and a "
                    "confusion risk",
                }
            )

    @staticmethod
    def _audit_crit(header: dict[str, Any], findings: list[dict[str, Any]]) -> None:
        if "crit" not in header:
            return
        crit = header["crit"]
        if not isinstance(crit, list) or not crit or not all(isinstance(item, str) and item for item in crit):
            findings.append(
                {
                    "code": "crit_invalid",
                    "severity": "high",
                    "detail": "crit must be a non-empty array of strings (RFC 7515 section 4.1.11)",
                }
            )
            return
        if "crit" in crit:
            findings.append(
                {"code": "crit_invalid", "severity": "high", "detail": 'crit must not list "crit" itself (RFC 7515)'}
            )
        missing = [name for name in crit if name != "crit" and name not in header]
        if missing:
            findings.append(
                {
                    "code": "crit_parameter_conflict",
                    "severity": "high",
                    "detail": f"crit lists parameters absent from the header: {missing[:10]}",
                }
            )

    @staticmethod
    def _audit_kid(header: dict[str, Any], findings: list[dict[str, Any]]) -> None:
        kid = header.get("kid")
        if not isinstance(kid, str) or not kid:
            return
        lowered = kid.lower()
        suspicious = [needle for needle in JwtTool._KID_SUSPICIOUS if needle.lower() in lowered]
        if kid.startswith(("/", "\\")) or suspicious:
            preview = kid[:16]
            findings.append(
                {
                    "code": "kid_suspicious",
                    "severity": "high",
                    "detail": f"kid value looks like a path or URL reference (prefix: {preview!r}); reject kid "
                    "values used as file paths or key URLs",
                }
            )

    def _explain(  # noqa: C901
        self,
        core: dict[str, Any],
        now: float | None,
        skew: int,
        expected_aud: str | None,
        expected_iss: str | None,
        mask: bool,
        bearer_stripped: bool,
    ) -> dict[str, Any]:
        header = core["header"]
        claims = core["payload"] if isinstance(core["payload"], dict) else {}
        alg_value = header.get("alg")
        alg = alg_value if isinstance(alg_value, str) else None
        family = self._ALG_FAMILIES.get(alg or "", "unrecognized algorithm")
        audit = self._audit(core)
        analysis = self._analyze(core, now, skew, expected_aud, expected_iss, mask)
        lines: list[str] = []
        names = "header.payload.signature" if core["token_form"] == "JWS" else "header.payload"  # noqa: S105
        lines.append(f"JWT compact token, {core['segment_count']} segments ({names}); form: {core['token_form']}.")
        if bearer_stripped:
            lines.append('A "Bearer " prefix was stripped from the input before decoding.')
        lines.append(f"Header alg={alg!r} ({family}); typ={header.get('typ')!r}; kid present: {'kid' in header}.")
        if alg is None:
            lines.append('The header does not declare "alg", so the signing method is unknown.')
        elif alg.lower() == "none":
            lines.append("alg none means the token is not signed: integrity is unprotected and anyone could have produced it.")
        elif alg in ("HS256", "HS384", "HS512"):
            lines.append(f"{alg} signs with a symmetric shared secret; a holder of the secret can both verify and forge tokens.")
        elif alg in self._ALG_FAMILIES:
            lines.append(f"{alg} is an asymmetric signature family; verification needs the signer public key.")
        else:
            lines.append(f"{alg} is not a JOSE-registered algorithm; treat it as a confusion risk.")
        lines.append("This tool did NOT verify any signature: it only decoded and analyzed the structure.")
        signature = self._signature_view(core["signature_text"])
        if signature["present"]:
            lines.append(f"Signature segment present ({signature['length']} chars, {signature['format']}).")
        else:
            lines.append("Signature segment absent.")
        if now is None:
            lines.append(
                f"Claims were analyzed against the system clock (now {analysis['now']}); pass now= for reproducible math."
            )
        for name in ("exp", "nbf", "iat"):
            check = analysis["checks"][name]
            lines.append(f"Claim {name}: {check['math'] if check['present'] else 'missing (info)'}.")
        registered = [name for name in _REGISTERED_CLAIMS if name in claims]
        custom = [name for name in claims if name not in _REGISTERED_CLAIMS]
        lines.append(f"Registered claims present: {registered if registered else 'none'}.")
        if custom:
            summary = ", ".join(f"{name} ({analysis['custom_claims'][name]})" for name in custom)
            lines.append(f"Custom claims (types only): {summary}.")
        if analysis["audience"]["verdict"] != "not_checked":
            lines.append(f"Audience check: {analysis['audience']['verdict']}.")
        if analysis["issuer"]["verdict"] != "not_checked":
            lines.append(f"Issuer check: {analysis['issuer']['verdict']}.")
        if core["structure_errors"]:
            joined = "; ".join(f"{entry['code']} ({entry['severity']})" for entry in core["structure_errors"])
            lines.append(f"Structure errors: {joined}.")
        lines.append(f"Findings by severity: {audit['findings_by_severity']}.")
        verdicts: list[dict[str, Any]] = []
        for name in ("exp", "nbf", "iat"):
            check = analysis["checks"][name]
            if check["present"]:
                severity = "high" if check["verdict"] in ("expired", "not_yet_valid", "issued_in_future", "invalid") else "info"
                verdicts.append({"topic": name, "severity": severity, "verdict": check["verdict"]})
        verdicts.extend({"topic": item["code"], "severity": item["severity"], "verdict": item["detail"]} for item in audit["findings"])
        return {
            "status": "success",
            "mode": "explain",
            "now": analysis["now"],
            "lines": lines,
            "verdicts": verdicts,
            "findings_by_severity": audit["findings_by_severity"],
        }
