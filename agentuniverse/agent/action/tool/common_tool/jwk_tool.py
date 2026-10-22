#!/usr/bin/env python3
"""Structural analysis for JSON Web Keys (RFC 7517), key sets, and RFC 7638 thumbprints."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import hashlib
import json
import re
from copy import deepcopy
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class JwkTool(Tool):
    """Validate the STRUCTURE of JSON Web Keys without performing cryptography.

    Scope (structure layer only): RFC 7517 parameter inventory, per-kty required
    parameters, strict base64url validation, parameter-model consistency (RSA
    modulus/exponent sizes, EC crv to coordinate byte lengths, oct key length,
    OKP crv to subkey lengths), size/bit-strength reporting, RFC 7638
    thumbprints, JWKS set-level checks, and public-key extraction.

    Explicitly out of scope: signature verification, encryption, point-on-curve
    membership (requires field arithmetic), and any private-key arithmetic.

    Safety invariant: private parameters (d, p, q, dp, dq, qi, oth, k) are
    reported by NAME and size only; their values are never echoed in results.
    """

    max_set_keys: int = 10_000
    max_param_chars: int = 1_048_576
    max_input_chars: int = 16 * 1024 * 1024

    _MODES: ClassVar[tuple[str, ...]] = ("analyze", "analyze_set", "thumbprint", "public_extract")

    # RFC 7517 section 4 common parameters.
    _COMMON_PARAMS: ClassVar[dict[str, str]] = {
        "kty": "Key Type (RFC 7517 4.1)",
        "use": "Public Key Use (RFC 7517 4.2)",
        "key_ops": "Key Operations (RFC 7517 4.3)",
        "alg": "Algorithm (RFC 7517 4.4)",
        "kid": "Key ID (RFC 7517 4.5)",
        "x5u": "X.509 URL (RFC 7517 4.6)",
        "x5c": "X.509 Certificate Chain (RFC 7517 4.7)",
        "x5t": "X.509 Certificate SHA-1 Thumbprint (RFC 7517 4.8)",
        "x5t#S256": "X.509 Certificate SHA-256 Thumbprint (RFC 7517 4.9)",
    }

    # RFC 7517 section 6 kty-specific parameters.
    _KTY_PARAMS: ClassVar[dict[str, dict[str, str]]] = {
        "RSA": {
            "n": "Modulus (RFC 7517 6.3.1.1)",
            "e": "Exponent (RFC 7517 6.3.1.2)",
            "d": "Private Exponent (RFC 7517 6.3.2.1)",
            "p": "First Prime Factor (RFC 7517 6.3.2.2)",
            "q": "Second Prime Factor (RFC 7517 6.3.2.3)",
            "dp": "First Factor CRT Exponent (RFC 7517 6.3.2.4)",
            "dq": "Second Factor CRT Exponent (RFC 7517 6.3.2.5)",
            "qi": "First CRT Coefficient (RFC 7517 6.3.2.6)",
            "oth": "Other Primes Info (RFC 7517 6.3.2.7)",
        },
        "EC": {
            "crv": "Curve (RFC 7517 6.2.1.1)",
            "x": "X Coordinate (RFC 7517 6.2.1.2)",
            "y": "Y Coordinate (RFC 7517 6.2.1.3)",
            "d": "ECC Private Key (RFC 7517 6.2.2.1)",
        },
        "oct": {
            "k": "Key Value (RFC 7517 6.4.1)",
        },
        # RFC 8037 section 2 (OKP is a registered kty extension).
        "OKP": {
            "crv": "Subtype of key pair (RFC 8037 2)",
            "x": "Public key (RFC 8037 2)",
            "d": "Private key (RFC 8037 2)",
        },
    }

    # Parameters whose presence means the JWK carries private/symmetric material.
    _PRIVATE_PARAMS: ClassVar[dict[str, tuple[str, ...]]] = {
        "RSA": ("d", "p", "q", "dp", "dq", "qi", "oth"),
        "EC": ("d",),
        "OKP": ("d",),
        "oct": ("k",),
    }

    # Parameters that are pure base64url octet/integer strings (never echoed).
    _B64URL_PARAMS: ClassVar[dict[str, tuple[str, ...]]] = {
        "RSA": ("n", "e", "d", "p", "q", "dp", "dq", "qi"),
        "EC": ("x", "y", "d"),
        "oct": ("k",),
        "OKP": ("x", "d"),
    }

    # Required public parameters per kty.
    _REQUIRED_PARAMS: ClassVar[dict[str, tuple[str, ...]]] = {
        "RSA": ("n", "e"),
        "EC": ("crv", "x", "y"),
        "oct": ("k",),
        "OKP": ("crv", "x"),
    }

    # EC curve -> coordinate byte length (RFC 7518 6.2.1; P-256K per its
    # IANA registration). P-521 coordinates are 521 bits = 66 bytes (not 64/65).
    _EC_CRV_BYTES: ClassVar[dict[str, int]] = {
        "P-256": 32,
        "P-384": 48,
        "P-521": 66,
        "P-256K": 32,
        "secp256k1": 32,
    }

    # OKP curve -> public/private key byte length (RFC 8037 2: Ed448/X448 are 57).
    _OKP_CRV_BYTES: ClassVar[dict[str, int]] = {
        "Ed25519": 32,
        "X25519": 32,
        "Ed448": 57,
        "X448": 57,
    }

    # RFC 7638 section 3.1: required members per kty for thumbprints.
    _THUMBPRINT_MEMBERS: ClassVar[dict[str, tuple[str, ...]]] = {
        "RSA": ("e", "kty", "n"),
        "EC": ("crv", "kty", "x", "y"),
        "oct": ("k", "kty"),
        "OKP": ("crv", "kty", "x"),
    }

    # RSA strength tiers aligned with NIST SP 800-57 comparable-symmetry table.
    _RSA_TIERS: ClassVar[tuple[tuple[int, str, int, str], ...]] = (
        (4096, "4096", 150, "at least a 4096-bit modulus; comfortably above the NIST SP 800-57 128-bit comparable strength"),
        (3072, "3072", 128, "a 3072-bit modulus matches the NIST SP 800-57 128-bit comparable strength"),
        (2048, "2048", 112, "a 2048-bit modulus matches the NIST SP 800-57 112-bit comparable strength (current minimum)"),
    )

    _SYMMETRIC_TIERS: ClassVar[tuple[tuple[int, str], ...]] = (
        (16, "128-bit (AES-128/HS256 class)"),
        (24, "192-bit (AES-192 class)"),
        (32, "256-bit (AES-256/HS384 class or stronger)"),
    )

    _KEY_OPS_VALUES: ClassVar[tuple[str, ...]] = (
        "sign", "verify", "encrypt", "decrypt", "wrapKey", "unwrapKey", "deriveKey", "deriveBits",
    )

    # First character outside the base64url alphabet (A-Z, a-z, 0-9, '-', '_').
    _INVALID_B64URL_RE: ClassVar[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9_-]")

    def execute(self, mode: str, jwk: Any = None) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "analyze_set":
                return self._analyze_set(jwk)
            params = self._jwk_object(jwk)
            if operation == "thumbprint":
                return self._thumbprint_result(params)
            if operation == "public_extract":
                return self._public_extract(params)
            return self._analyze(params)
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive boundary
            return self._error("operation_error", f"JWK analysis failed: {exc}")

    # ------------------------------------------------------------------ inputs

    def _validate_config(self) -> None:
        for name in ("max_set_keys", "max_param_chars", "max_input_chars"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _error(kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in JwkTool._MODES:
            raise ValueError("mode must be analyze, analyze_set, thumbprint, or public_extract")
        return operation

    def _jwk_object(self, value: Any) -> dict[str, Any]:
        params = self._json_value(value, "jwk")
        if not isinstance(params, dict):
            raise ValueError("jwk must be a JSON object (dict or JSON object text)")
        return params

    def _json_value(self, value: Any, label: str) -> Any:
        if value is None:
            raise ValueError(f"{label} is required")
        if isinstance(value, str):
            text = value.strip()
            if not text:
                raise ValueError(f"{label} must be a non-empty JSON value")
            if len(text) > self.max_input_chars:
                raise ValueError(f"{label} exceeds max_input_chars ({self.max_input_chars})")
            try:
                return json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{label} is not valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}") from exc
        return value

    # ---------------------------------------------------------------- analysis

    def _analyze(self, params: dict[str, Any]) -> dict[str, Any]:
        kty = params.get("kty")
        recognized = isinstance(kty, str) and kty in self._KTY_PARAMS
        errors: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        notes: list[dict[str, Any]] = []
        if "kty" not in params:
            errors.append(self._entry("kty_required", "missing required parameter 'kty' (RFC 7517 4.1)"))
        elif not isinstance(kty, str):
            errors.append(self._entry("kty_type", "'kty' must be a string"))
        elif not recognized:
            errors.append(self._entry(
                "kty_unknown",
                f"unknown kty {kty!r}; recognized values are RSA, EC, oct (RFC 7517) and OKP (RFC 8037)",
            ))

        private_names = self._PRIVATE_PARAMS.get(kty if isinstance(kty, str) else "", ())
        present_private = [name for name in private_names if name in params]
        if present_private:
            warnings.append(self._entry(
                "private_material_present",
                "input contains private key material; parameters reported by name only, values are never echoed",
                params=present_private,
            ))

        inventory = self._inventory(kty if isinstance(kty, str) else None, params, notes)
        decoded: dict[str, bytes] = {}
        strength: dict[str, Any] | None = None
        if recognized:
            self._required_params(kty, params, errors)
            self._common_param_shapes(params, errors, warnings)
            self._decode_b64url_params(kty, params, errors, notes, decoded)
            if kty == "RSA":
                strength = self._rsa_consistency(params, decoded, errors, warnings)
            elif kty == "EC":
                strength = self._ec_consistency(params, decoded, errors, notes)
            elif kty == "oct":
                strength = self._oct_consistency(decoded, warnings, notes)
            else:
                strength = self._okp_consistency(params, decoded, errors, warnings, notes)
        result: dict[str, Any] = {
            "status": "success",
            "mode": "analyze",
            "kty": kty if isinstance(kty, str) else None,
            "recognized": recognized,
            "contains_private_material": bool(present_private),
            "private_parameters": present_private,
            "parameters": inventory["parameters"],
            "unknown_parameters": inventory["unknown"],
        }
        if strength is not None:
            result["strength"] = strength
        thumbprint, thumbprint_error = self._thumbprint(params)
        if thumbprint is not None:
            result["thumbprint"] = thumbprint
        elif thumbprint_error is not None:
            notes.append(self._entry("thumbprint_unavailable", thumbprint_error))
        result["errors"] = errors
        result["warnings"] = warnings
        result["notes"] = notes
        return result

    def _entry(self, code: str, detail: str, **extra: Any) -> dict[str, Any]:
        entry = {"code": code, "detail": detail}
        entry.update(extra)
        return entry

    def _inventory(self, kty: str | None, params: dict[str, Any], notes: list[dict[str, Any]]) -> dict[str, Any]:
        kty_table = self._KTY_PARAMS.get(kty or "", {})
        private_set = set(self._PRIVATE_PARAMS.get(kty or "", ()))
        parameters: list[dict[str, Any]] = []
        unknown: list[str] = []
        for name in params:
            if name in self._COMMON_PARAMS:
                meaning, category = self._COMMON_PARAMS[name], "common"
            elif name in kty_table:
                meaning, category = kty_table[name], "kty-specific"
            else:
                meaning, category = None, "unknown"
            if meaning is None:
                unknown.append(name)
                parameters.append({
                    "name": name,
                    "category": "unknown",
                    "meaning": "not defined by the RFC 7517 parameter tables for this kty",
                })
                continue
            entry = {"name": name, "category": category, "meaning": meaning}
            if name in private_set:
                entry["private"] = True
                entry["note"] = "value never echoed"
            parameters.append(entry)
        if unknown:
            notes.append(self._entry(
                "unknown_parameters",
                "parameters outside the RFC 7517/8037 tables for this kty (reported by name only)",
                params=sorted(unknown),
            ))
        return {"parameters": parameters, "unknown": sorted(unknown)}

    def _required_params(self, kty: str, params: dict[str, Any], errors: list[dict[str, Any]]) -> None:
        for name in self._REQUIRED_PARAMS[kty]:
            if name not in params:
                errors.append(self._entry(
                    "missing_required_parameter",
                    f"kty {kty} requires parameter '{name}' (RFC 7517 section 6)",
                    params=[name],
                ))

    def _common_param_shapes(self, params: dict[str, Any], errors: list[dict[str, Any]], warnings: list[dict[str, Any]]) -> None:
        use = params.get("use")
        if use is not None and use not in ("sig", "enc"):
            errors.append(self._entry("use_value", "'use' must be 'sig' or 'enc' (RFC 7517 4.2)"))
        key_ops = params.get("key_ops")
        if key_ops is not None:
            if not isinstance(key_ops, list) or not all(isinstance(item, str) for item in key_ops):
                errors.append(self._entry("key_ops_type", "'key_ops' must be an array of strings (RFC 7517 4.3)"))
            else:
                if len(set(key_ops)) != len(key_ops):
                    warnings.append(self._entry("key_ops_duplicates", "'key_ops' contains duplicate values (RFC 7517 4.3 requires distinct values)"))
                unknown_ops = sorted({op for op in key_ops if op not in self._KEY_OPS_VALUES})
                if unknown_ops:
                    warnings.append(self._entry("key_ops_unknown", "'key_ops' contains values outside the RFC 7517 4.3 registry", params=unknown_ops))
                if use == "sig" and any(op in ("encrypt", "decrypt", "wrapKey", "unwrapKey", "deriveKey", "deriveBits") for op in key_ops):
                    warnings.append(self._entry("use_key_ops_conflict", "'use' is 'sig' but 'key_ops' contains non-signing operations (RFC 7517 4.3 consistency)"))
                if use == "enc" and any(op in ("sign", "verify") for op in key_ops):
                    warnings.append(self._entry("use_key_ops_conflict", "'use' is 'enc' but 'key_ops' contains signature operations (RFC 7517 4.3 consistency)"))

    # ------------------------------------------------------- base64url handling

    def _decode_b64url_params(
        self,
        kty: str,
        params: dict[str, Any],
        errors: list[dict[str, Any]],
        notes: list[dict[str, Any]],
        decoded: dict[str, bytes],
    ) -> None:
        for name in self._B64URL_PARAMS[kty]:
            if name not in params:
                continue
            value = params[name]
            if not isinstance(value, str):
                errors.append(self._entry("param_type", f"parameter '{name}' must be a base64url string"))
                continue
            if len(value) > self.max_param_chars:
                notes.append({
                    "param": name,
                    "char_length": len(value),
                    "mode": "length_report_only",
                    "detail": f"parameter exceeds max_param_chars ({self.max_param_chars}); length reported, charset/decode and size checks skipped",
                })
                continue
            if self._validate_b64url(name, value, errors):
                decoded[name] = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

    def _validate_b64url(self, name: str, value: str, errors: list[dict[str, Any]]) -> bool:
        """Strict RFC 7517 base64url check; reports the exact position of the first defect."""
        match = self._INVALID_B64URL_RE.search(value)
        if match is not None:
            position = match.start()
            char = match.group()
            if char == "=":
                code = "base64url_padding_present"
                detail = (
                    f"parameter '{name}' position {position}: '=' padding is not used in "
                    "unpadded base64url (RFC 7517 2)"
                )
            else:
                code = "base64url_invalid_character"
                detail = (
                    f"parameter '{name}' position {position}: character {char!r} is not in the base64url "
                    "alphabet (A-Z, a-z, 0-9, '-', '_'; '+' and '/' belong to standard base64, not base64url)"
                )
            errors.append(self._entry(code, detail, param=name, position=position))
        if len(value) % 4 == 1:
            errors.append(self._entry(
                "base64url_invalid_length",
                f"parameter '{name}' length {len(value)} is impossible for base64url "
                f"(length mod 4 may not be 1; character at position {len(value) - 1} has no valid continuation)",
                param=name,
                position=len(value) - 1,
            ))
        return not match and len(value) % 4 != 1

    # ------------------------------------------------------ per-kty consistency

    def _rsa_consistency(
        self,
        params: dict[str, Any],
        decoded: dict[str, bytes],
        errors: list[dict[str, Any]],
        warnings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        report: dict[str, Any] = {"kty": "RSA"}
        modulus_bits = None
        if "n" in decoded:
            modulus = int.from_bytes(decoded["n"], "big")
            modulus_bits = modulus.bit_length()
            report["modulus_bits"] = modulus_bits
            report["modulus_bytes"] = len(decoded["n"])
            if modulus % 2 == 0:
                errors.append(self._entry("rsa_modulus_even", "RSA modulus n must be odd (product of two odd primes)"))
            for bits, tier, security_bits, note in self._RSA_TIERS:
                if modulus_bits >= bits:
                    report["strength_tier"] = tier
                    report["comparable_security_bits"] = security_bits
                    report["nist_note"] = note
                    break
            else:
                report["strength_tier"] = "below-2048"
                report["comparable_security_bits"] = None
                report["nist_note"] = "below the 2048-bit minimum aligned with NIST SP 800-57 (112-bit comparable strength)"
                warnings.append(self._entry(
                    "rsa_modulus_below_2048",
                    f"modulus is {modulus_bits} bits, below the 2048-bit minimum; reported, not enforced",
                ))
        if "e" in decoded:
            exponent = int.from_bytes(decoded["e"], "big")
            exponent_bits = exponent.bit_length()
            report["exponent_bits"] = exponent_bits
            report["exponent_value_ok"] = 3 <= exponent < 2 ** 256
            if not (3 <= exponent < 2 ** 256):
                errors.append(self._entry(
                    "rsa_exponent_range",
                    f"RSA exponent e must be in the range [3, 2^256); reported exponent is {exponent_bits} bits",
                ))
            if exponent % 2 == 0:
                errors.append(self._entry("rsa_exponent_even", "RSA public exponent e must be odd (RFC 8017)"))
            if exponent == 3:
                warnings.append(self._entry("rsa_exponent_weak", "e = 3 is historically weak against certain padding attacks; informational"))
            elif exponent == 65537:
                report["exponent_note"] = "e = 65537 (F4), the common modern choice"
        # CRT material consistency: p and q appear together, CRT exponents need d.
        has_d = "d" in params
        if ("p" in params) != ("q" in params):
            errors.append(self._entry(
                "rsa_prime_pair",
                "RSA private parameters p and q must be present together (RFC 7517 6.3.2)",
                params=[name for name in ("p", "q") if name in params],
            ))
        for name in ("dp", "dq", "qi"):
            if name in params and not has_d:
                errors.append(self._entry(
                    "rsa_crt_without_d",
                    f"RSA CRT parameter '{name}' is present without the private exponent d (RFC 7517 6.3.2)",
                    params=[name],
                ))
        if "oth" in params:
            value = params["oth"]
            if not isinstance(value, list):
                errors.append(self._entry("oth_type", "'oth' must be an array of OtherPrimesInfo objects (RFC 7517 6.3.2.7)"))
        return report

    def _ec_consistency(
        self,
        params: dict[str, Any],
        decoded: dict[str, bytes],
        errors: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        report: dict[str, Any] = {"kty": "EC", "point_on_curve": "not_checked (requires field arithmetic; out of scope for this structure tool)"}
        crv = params.get("crv")
        if not isinstance(crv, str):
            report["crv"] = None
            return report
        report["crv"] = crv
        expected = self._EC_CRV_BYTES.get(crv)
        if expected is None:
            errors.append(self._entry(
                "ec_unknown_crv",
                f"crv {crv!r} is not in the supported table (P-256, P-384, P-521, P-256K/secp256k1); coordinate lengths not checked",
            ))
            return report
        report["coordinate_bytes_expected"] = expected
        report["curve_bits"] = {32: 256, 48: 384, 66: 521}[expected]
        for name in ("x", "y"):
            if name in decoded:
                actual = len(decoded[name])
                report[f"{name}_bytes"] = actual
                if actual != expected:
                    errors.append(self._entry(
                        "ec_coordinate_length",
                        f"parameter '{name}' is {actual} bytes but crv {crv} requires exactly {expected} bytes "
                        f"({'the curve is 521 bits, so coordinates are 66 bytes, not 64 or 65' if crv == 'P-521' else 'coordinates must be the full fixed field size'})",
                        param=name,
                        expected=expected,
                        actual=actual,
                    ))
        return report

    def _oct_consistency(self, decoded: dict[str, bytes], warnings: list[dict[str, Any]], notes: list[dict[str, Any]]) -> dict[str, Any]:
        report: dict[str, Any] = {"kty": "oct"}
        if "k" not in decoded:
            return report
        key_bytes = len(decoded["k"])
        report["key_bytes"] = key_bytes
        report["key_bits"] = key_bytes * 8
        for tier_bytes, tier_note in self._SYMMETRIC_TIERS:
            if key_bytes == tier_bytes:
                report["strength_tier"] = f"{tier_bytes * 8}-bit"
                report["tier_note"] = tier_note
                break
        else:
            if key_bytes < 16:
                warnings.append(self._entry(
                    "oct_key_short",
                    f"oct key is {key_bytes * 8} bits, below the 128-bit symmetric minimum; reported, not enforced",
                ))
                report["strength_tier"] = "below-128-bit"
            else:
                report["strength_tier"] = "non-standard-length"
                notes.append(self._entry(
                    "oct_key_non_standard",
                    f"oct key is {key_bytes} bytes; standard symmetric tiers are 16, 24, and 32 bytes (128/192/256 bits)",
                ))
        return report

    def _okp_consistency(
        self,
        params: dict[str, Any],
        decoded: dict[str, bytes],
        errors: list[dict[str, Any]],
        warnings: list[dict[str, Any]],
        notes: list[dict[str, Any]],
    ) -> dict[str, Any]:
        report: dict[str, Any] = {"kty": "OKP"}
        crv = params.get("crv")
        if not isinstance(crv, str):
            report["crv"] = None
            return report
        report["crv"] = crv
        expected = self._OKP_CRV_BYTES.get(crv)
        if expected is None:
            errors.append(self._entry(
                "okp_unknown_crv",
                f"crv {crv!r} is not in the RFC 8037 table (Ed25519, Ed448, X25519, X448); key lengths not checked",
            ))
            return report
        report["key_bytes_expected"] = expected
        for name in ("x", "d"):
            if name in decoded:
                actual = len(decoded[name])
                report[f"{name}_bytes"] = actual
                if actual != expected:
                    errors.append(self._entry(
                        "okp_key_length",
                        f"parameter '{name}' is {actual} bytes but crv {crv} requires exactly {expected} bytes (RFC 8037 2)",
                        param=name,
                        expected=expected,
                        actual=actual,
                    ))
        return report

    # ------------------------------------------------------------ thumbprints

    def _thumbprint(self, params: dict[str, Any]) -> tuple[str | None, str | None]:
        """RFC 7638: SHA-256 over the lexicographically ordered required members."""
        kty = params.get("kty")
        members = self._THUMBPRINT_MEMBERS.get(kty if isinstance(kty, str) else "")
        if members is None:
            return None, "thumbprint requires a supported kty (RSA, EC, oct, OKP)"
        for member in members:
            if not isinstance(params.get(member), str):
                return None, f"thumbprint requires string values for members {sorted(members)}"
        canonical = "{" + ",".join(
            json.dumps(member) + ":" + json.dumps(params[member], ensure_ascii=False)
            for member in sorted(members)
        ) + "}"
        digest = hashlib.sha256(canonical.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii"), None

    def _thumbprint_result(self, params: dict[str, Any]) -> dict[str, Any]:
        thumbprint, error = self._thumbprint(params)
        if thumbprint is None:
            return self._error("validation_error", error or "thumbprint unavailable")
        return {
            "status": "success",
            "mode": "thumbprint",
            "kty": params.get("kty") if isinstance(params.get("kty"), str) else None,
            "thumbprint": thumbprint,
            "note": "RFC 7638 SHA-256 thumbprint over the lexicographically ordered required members; a public identifier",
        }

    # --------------------------------------------------------- public extract

    def _public_extract(self, params: dict[str, Any]) -> dict[str, Any]:
        kty = params.get("kty")
        if not isinstance(kty, str) or kty not in self._PRIVATE_PARAMS:
            return self._error(
                "validation_error",
                "public_extract requires a recognized kty (RSA, EC, oct, OKP)",
            )
        private_names = [name for name in self._PRIVATE_PARAMS[kty] if name in params]
        public_jwk = deepcopy(params)
        for name in private_names:
            del public_jwk[name]
        return {
            "status": "success",
            "mode": "public_extract",
            "public_jwk": public_jwk,
            "private_params_dropped": private_names,
            "dropped_private_material": bool(private_names),
            "note": (
                "extraction is lossy for private parameters: dropped values are never retained, reported, or recoverable; "
                "an oct key without k retains only descriptive parameters because symmetric keys have no public part"
            ),
        }

    # ------------------------------------------------------------ set analysis

    def _analyze_set(self, value: Any) -> dict[str, Any]:
        document = self._json_value(value, "jwk")
        if not isinstance(document, dict):
            raise ValueError("analyze_set requires a JWK Set object {\"keys\": [...]}")
        if "keys" not in document:
            raise ValueError("JWK Set must contain a 'keys' array (RFC 7517 5)")
        keys = document["keys"]
        if not isinstance(keys, list):
            raise ValueError("'keys' must be an array")
        warnings: list[dict[str, Any]] = []
        total = len(keys)
        truncated = total > self.max_set_keys
        if truncated:
            warnings.append(self._entry(
                "set_truncated",
                f"JWK Set has {total} keys, exceeding max_set_keys ({self.max_set_keys}); analysis covers the first {self.max_set_keys}",
            ))
            keys = keys[: self.max_set_keys]
        if total == 0:
            warnings.append(self._entry("set_empty", "JWK Set contains no keys"))

        analyses: list[dict[str, Any]] = []
        by_kid: dict[str, list[int]] = {}
        by_thumbprint_kid: dict[str, list[tuple[int, str]]] = {}
        kty_census: dict[str, int] = {}
        alg_census: dict[str, int] = {}
        for index, entry in enumerate(keys):
            if not isinstance(entry, dict):
                analyses.append({
                    "index": index,
                    "kid": None,
                    "kty": None,
                    "status": "error",
                    "errors": [self._entry("set_entry_type", "JWK Set member must be a JSON object")],
                })
                continue
            analysis = self._analyze(entry)
            slim = {
                "index": index,
                "kid": entry.get("kid") if isinstance(entry.get("kid"), str) else None,
                "kty": analysis.get("kty"),
                "recognized": analysis.get("recognized"),
                "contains_private_material": analysis.get("contains_private_material"),
                "thumbprint": analysis.get("thumbprint"),
                "errors": analysis.get("errors"),
                "warnings": analysis.get("warnings"),
                "strength": analysis.get("strength"),
            }
            analyses.append(slim)
            kid = slim["kid"]
            if kid is not None:
                by_kid.setdefault(kid, []).append(index)
                if analysis.get("thumbprint"):
                    by_thumbprint_kid.setdefault(kid, []).append((index, analysis["thumbprint"]))
            kty = analysis.get("kty")
            if isinstance(kty, str):
                kty_census[kty] = kty_census.get(kty, 0) + 1
            alg = entry.get("alg")
            alg_key = alg if isinstance(alg, str) and alg else "(unset)"
            alg_census[alg_key] = alg_census.get(alg_key, 0) + 1

        duplicate_kids = []
        thumbprint_conflicts = []
        for kid in sorted(by_kid):
            indices = by_kid[kid]
            if len(indices) < 2:
                continue
            duplicate_kids.append({
                "kid": kid,
                "indices": indices,
                "warning": f"kid {kid!r} used by {len(indices)} keys; key lookup by kid is ambiguous",
            })
            entries = by_thumbprint_kid.get(kid, [])
            thumbprints = {tp for _, tp in entries}
            if len(thumbprints) > 1:
                thumbprint_conflicts.append({
                    "kid": kid,
                    "indices": [index for index, _ in entries],
                    "thumbprints": sorted(thumbprints),
                    "error": f"kid {kid!r} maps to {len(thumbprints)} distinct RFC 7638 thumbprints; same key id, different key material",
                })
        if thumbprint_conflicts:
            warnings.append(self._entry("thumbprint_conflicts", f"{len(thumbprint_conflicts)} kid group(s) map to conflicting key material"))

        return {
            "status": "success",
            "mode": "analyze_set",
            "keys_count": total,
            "keys_analyzed": len(keys),
            "truncated": truncated,
            "keys": analyses,
            "set_checks": {
                "duplicate_kids": duplicate_kids,
                "thumbprint_conflicts": thumbprint_conflicts,
                "kty_census": dict(sorted(kty_census.items())),
                "alg_census": dict(sorted(alg_census.items())),
            },
            "warnings": warnings,
        }
