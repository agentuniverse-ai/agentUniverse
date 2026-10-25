#!/usr/bin/env python3
"""Byte-payload encoding detection and diagnosis for agents."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import codecs
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# Byte-order signatures, checked longest first so UTF-32 BOMs win over the
# UTF-16 BOMs they start with. Signatures are pure byte tables; no probing.
_BOM_TABLE: tuple[tuple[bytes, str], ...] = (
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xef\xbb\xbf", "utf-8"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
)

# Heuristic signatures that are conventionally treated as BOMs even though a
# decoder never strips them automatically; kept separate because evidence is
# weaker ("BOM signature only, payload not structurally validated").
_SOFT_BOM_TABLE: tuple[tuple[bytes, str], ...] = (
    (b"\x2b\x2f\x76\x38", "utf-7"),
    (b"\x2b\x2f\x76\x39", "utf-7"),
    (b"\x2b\x2f\x76\x2b", "utf-7"),
    (b"\x2b\x2f\x76\x3f", "utf-7"),
    (b"\xf7\x64\x4c", "utf-1"),
)

# Bytes 0x81, 0x8D, 0x8F, 0x90, 0x9D are undefined in windows-1252; any other
# byte in 0x80..0x9F maps to a printable (quotes, dashes, currency) there.
_CP1252_UNDEFINED: frozenset[int] = frozenset((0x81, 0x8D, 0x8F, 0x90, 0x9D))

# Classic UTF-8-read-as-latin-1 mojibake shape: a latin-1 char from the UTF-8
# lead range (C2..F4) followed by continuation-shaped chars (80..BF).
_MOJIBAKE_SEQUENCE = re.compile("[\u00c2-\u00f4][\u0080-\u00bf]{1,3}")

_MAX_MOJIBAKE_LEVELS = 3


class EncodingDetectTool(Tool):
    """Identify and diagnose the encoding of raw byte payloads.

    Payload contract: the caller passes raw bytes either as ``payload`` text
    produced with the latin-1 escape hatch (``payload_bytes.decode('latin-1')``
    preserves every byte as exactly one code point) or as a ``hex`` string for
    exact bytes. Exactly one of the two must be provided.
    """

    max_payload_bytes: int = 4 * 1024 * 1024
    max_errors: int = 50
    max_preview_chars: int = 512
    max_candidates: int = 6

    _MODES: ClassVar[frozenset[str]] = frozenset({"detect", "diagnose", "validate_utf8", "repair_preview"})

    def execute(
        self,
        mode: str,
        payload: str | None = None,
        hex: str | None = None,  # noqa: A002 - matches the yaml property name
        declared: str | None = None,
        target: str | None = None,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            operation = self._mode(mode)
            self._check_mode_params(operation, declared, target)
            data = self._payload_bytes(payload, hex)
            if operation == "detect":
                return self._detect(data, declared)
            if operation == "diagnose":
                return self._diagnose(data, declared)
            if operation == "validate_utf8":
                return self._validate_utf8(data)
            return self._repair_preview(data, target)
        except (TypeError, ValueError, LookupError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive, matches tool conventions
            return self._error(mode, "operation_error", f"Encoding analysis failed: {exc}")

    @staticmethod
    def _error(mode_value: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode_value}

    def _validate_config(self) -> None:
        for name in ("max_payload_bytes", "max_errors", "max_preview_chars", "max_candidates"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in EncodingDetectTool._MODES:
            raise ValueError("mode must be detect, diagnose, validate_utf8, or repair_preview")
        return mode

    @staticmethod
    def _check_mode_params(operation: str, declared: Any, target: Any) -> None:
        """Reject parameters that the selected mode does not accept."""
        if declared is not None and operation not in {"detect", "diagnose"}:
            raise ValueError(f"declared is not accepted by mode {operation}")
        if target is not None and operation != "repair_preview":
            raise ValueError(f"target is not accepted by mode {operation}")
        if operation == "repair_preview" and (not isinstance(target, str) or not target.strip()):
            raise ValueError("repair_preview requires a target encoding")

    def _payload_bytes(self, payload: Any, hex_value: Any) -> bytes:
        if payload is not None and hex_value is not None:
            raise ValueError("provide exactly one of payload or hex, not both")
        if payload is not None:
            return self._payload_from_text(payload)
        if hex_value is not None:
            return self._payload_from_hex(hex_value)
        raise ValueError("provide the payload either as latin-1 escaped text or as a hex string")

    def _payload_from_text(self, payload: Any) -> bytes:
        if not isinstance(payload, str):
            raise TypeError("payload must be a string")
        if len(payload) > self.max_payload_bytes:
            raise ValueError(f"payload exceeds max_payload_bytes ({self.max_payload_bytes})")
        try:
            return payload.encode("latin-1")
        except UnicodeEncodeError as exc:
            raise ValueError(
                "payload must follow the latin-1 escape contract: pass the raw bytes as "
                "payload_bytes.decode('latin-1') so each byte maps to one code point, or "
                "pass exact bytes via the hex option"
            ) from exc

    def _payload_from_hex(self, hex_value: Any) -> bytes:
        if not isinstance(hex_value, str):
            raise TypeError("hex must be a string")
        compact = "".join(hex_value.split())
        if compact.lower().startswith("0x"):
            compact = compact[2:]
        if not compact or len(compact) % 2:
            raise ValueError("hex must contain an even number of hex digits")
        if len(compact) > 2 * self.max_payload_bytes:
            raise ValueError(f"hex exceeds max_payload_bytes ({self.max_payload_bytes})")
        try:
            return bytes.fromhex(compact)
        except ValueError as exc:
            raise ValueError(f"hex contains a non-hex digit: {exc}") from exc

    # ------------------------------------------------------------------
    # BOM sniffing
    # ------------------------------------------------------------------
    @staticmethod
    def _bom(data: bytes) -> dict[str, Any]:
        for signature, name in _BOM_TABLE:
            if data.startswith(signature):
                return {"found": True, "name": name, "offset_consumed": len(signature), "soft": False}
        for signature, name in _SOFT_BOM_TABLE:
            if data.startswith(signature):
                return {"found": True, "name": name, "offset_consumed": 0, "soft": True}
        return {"found": False, "name": None, "offset_consumed": 0, "soft": False}

    # ------------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------------
    def _scan_utf8(self, data: bytes) -> tuple[list[dict[str, Any]], int]:
        """Return capped error list plus the deterministic total error count.

        Offsets follow codecs.UTF-8 strict semantics: an invalid start byte is
        reported at the offending byte, while invalid continuations and
        truncations are reported at the lead byte of the sequence.
        """
        errors: list[dict[str, Any]] = []
        total = 0
        length = len(data)
        index = 0
        while index < length:
            lead = data[index]
            if lead < 0x80:
                index += 1
                continue
            offset = index
            if lead < 0xC0:
                reason = "unexpected continuation byte (stray lead 80-BF)"
                skip = index + 1
            elif lead in (0xC0, 0xC1):
                reason = "overlong encoding (lead C0/C1 can only encode 7-bit code points)"
                skip = index + 1
            elif lead >= 0xF5:
                reason = "invalid start byte (>= F5 encodes code points above U+10FFFF)"
                skip = index + 1
            else:
                reason, skip = self._utf8_sequence_error(data, index, lead)
                if reason is None:
                    index += 1 + self._utf8_sequence_length(lead)
                    continue
            total += 1
            if len(errors) < self.max_errors:
                if reason.startswith("unexpected end"):
                    byte = f"0x{lead:02x}"
                elif skip > offset + 1 and skip <= length:
                    byte = f"0x{data[skip - 1]:02x}"
                else:
                    byte = f"0x{lead:02x}"
                errors.append({"offset": offset, "byte": byte, "reason": reason})
            index = skip
        return errors, total

    @staticmethod
    def _utf8_sequence_length(lead: int) -> int:
        if lead < 0xE0:
            return 1
        if lead < 0xF0:
            return 2
        return 3

    @staticmethod
    def _utf8_continuation_bounds(lead: int) -> tuple[int, int]:
        if lead == 0xE0:
            return 0xA0, 0xBF
        if lead == 0xED:
            return 0x80, 0x9F
        if lead == 0xF0:
            return 0x90, 0xBF
        if lead == 0xF4:
            return 0x80, 0x8F
        return 0x80, 0xBF

    def _utf8_sequence_error(self, data: bytes, index: int, lead: int) -> tuple[str | None, int]:
        """Validate one multibyte sequence; return (reason, skip) or (None, 0)."""
        need = self._utf8_sequence_length(lead)
        low, high = self._utf8_continuation_bounds(lead)
        length = len(data)
        for step in range(need):
            position = index + 1 + step
            if position >= length:
                return "unexpected end of data (sequence truncated)", length
            value = data[position]
            in_range = low <= value <= high if step == 0 else 0x80 <= value <= 0xBF
            if not in_range:
                if step == 0 and lead == 0xE0 and value < 0xA0:
                    reason = "overlong encoding (E0 followed by 80-9F)"
                elif step == 0 and lead == 0xF0 and value < 0x90:
                    reason = "overlong encoding (F0 followed by 80-8F)"
                elif step == 0 and lead == 0xED and value > 0x9F:
                    reason = "UTF-16 surrogate (ED followed by A0-BF)"
                elif step == 0 and lead == 0xF4 and value > 0x8F:
                    reason = "code point above U+10FFFF (F4 followed by 90-BF)"
                else:
                    reason = "invalid continuation byte"
                return reason, position + 1
        return None, 0

    def _utf8_validation(self, data: bytes) -> dict[str, Any]:
        errors, total = self._scan_utf8(data)
        if not total:
            return {"encoding": "utf-8", "valid": True, "error": None}
        return {"encoding": "utf-8", "valid": False, "error": errors[0]}

    @staticmethod
    def _scan_utf16(data: bytes, little: bool) -> dict[str, Any]:
        label = "utf-16-le" if little else "utf-16-be"
        if len(data) % 2:
            return {
                "encoding": label,
                "valid": False,
                "error": {
                    "offset": len(data) - 1,
                    "byte": f"0x{data[-1]:02x}",
                    "reason": "odd-length payload (trailing byte without a pair)",
                },
            }
        units = [int.from_bytes(data[at : at + 2], "little" if little else "big") for at in range(0, len(data), 2)]
        index = 0
        while index < len(units):
            unit = units[index]
            if 0xD800 <= unit <= 0xDBFF:
                if index + 1 >= len(units):
                    return _utf16_error(label, index, units[index], "unpaired high surrogate at end of payload")
                if not 0xDC00 <= units[index + 1] <= 0xDFFF:
                    return _utf16_error(label, index, unit, "unpaired high surrogate (next unit is not a low surrogate)")
                index += 2
                continue
            if 0xDC00 <= unit <= 0xDFFF:
                return _utf16_error(label, index, unit, "lone low surrogate without a preceding high surrogate")
            index += 1
        return {"encoding": label, "valid": True, "error": None}

    @staticmethod
    def _scan_utf32(data: bytes, little: bool) -> dict[str, Any]:
        label = "utf-32-le" if little else "utf-32-be"
        if len(data) % 4:
            return {
                "encoding": label,
                "valid": False,
                "error": {
                    "offset": (len(data) // 4) * 4,
                    "byte": f"0x{data[-1]:02x}",
                    "reason": "payload length is not a multiple of 4 (truncated unit)",
                },
            }
        for index in range(0, len(data), 4):
            value = int.from_bytes(data[index : index + 4], "little" if little else "big")
            if value > 0x10FFFF:
                return {
                    "encoding": label,
                    "valid": False,
                    "error": {
                        "offset": index,
                        "byte": f"0x{data[index]:02x}",
                        "reason": f"code point U+{value:X} is above U+10FFFF",
                    },
                }
            if 0xD800 <= value <= 0xDFFF:
                return {
                    "encoding": label,
                    "valid": False,
                    "error": {
                        "offset": index,
                        "byte": f"0x{data[index]:02x}",
                        "reason": f"code point U+{value:X} is a UTF-16 surrogate",
                    },
                }
        return {"encoding": label, "valid": True, "error": None}

    # ------------------------------------------------------------------
    # Byte statistics
    # ------------------------------------------------------------------
    @staticmethod
    def _stats(data: bytes) -> dict[str, Any]:
        length = len(data)
        if not length:
            return {
                "length": 0,
                "ascii_ratio": 0.0,
                "null_ratio": 0.0,
                "null_even_ratio": 0.0,
                "null_odd_ratio": 0.0,
                "null_phase3_ratio": 0.0,
                "high_ratio": 0.0,
                "control_ratio": 0.0,
                "cp1252_printable_bytes": 0,
                "c1_undefined_bytes": 0,
            }
        nulls = evens = odds = phase3 = 0
        ascii_count = high_count = controls = cp1252_printable = c1_undefined = 0
        for position, value in enumerate(data):
            if value == 0:
                nulls += 1
                if position % 2 == 0:
                    evens += 1
                else:
                    odds += 1
                if position % 4 == 3:
                    phase3 += 1
            if value < 0x80:
                ascii_count += 1
            else:
                high_count += 1
                if 0x80 <= value <= 0x9F:
                    if value in _CP1252_UNDEFINED:
                        c1_undefined += 1
                    else:
                        cp1252_printable += 1
            if value < 0x20 and value not in (0x09, 0x0A, 0x0D):
                controls += 1
        even_slots = (length + 1) // 2
        odd_slots = length // 2
        phase3_slots = length // 4
        return {
            "length": length,
            "ascii_ratio": ascii_count / length,
            "null_ratio": nulls / length,
            "null_even_ratio": evens / even_slots if even_slots else 0.0,
            "null_odd_ratio": odds / odd_slots if odd_slots else 0.0,
            "null_phase3_ratio": phase3 / phase3_slots if phase3_slots else 0.0,
            "high_ratio": high_count / length,
            "control_ratio": (controls + nulls) / length,
            "cp1252_printable_bytes": cp1252_printable,
            "c1_undefined_bytes": c1_undefined,
        }

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------
    def _detect(self, data: bytes, declared: str | None) -> dict[str, Any]:
        bom = self._bom(data)
        stats = self._stats(data)
        validations = {
            "utf-8": self._utf8_validation(data),
            "utf-16-le": self._scan_utf16(data, True),
            "utf-16-be": self._scan_utf16(data, False),
            "utf-32-le": self._scan_utf32(data, True),
            "utf-32-be": self._scan_utf32(data, False),
        }
        candidates, winner = self._rank(data, bom, stats, validations)
        candidates.sort(key=lambda item: (-item["confidence"], item["encoding"]))
        candidates = candidates[: self.max_candidates]
        if declared is not None:
            normalized = self._normalize_encoding(declared)
            if normalized is None:
                raise ValueError(f"declared encoding is not recognized: {declared}")
            conflict = normalized != winner and not (winner == "ascii" and normalized == "utf-8")
            if normalized == winner and any(item["encoding"] == winner for item in candidates):
                for item in candidates:
                    if item["encoding"] == winner and "declared" not in item["evidence"]:
                        item["evidence"].append("declared")
        else:
            conflict = None
        return {
            "status": "success",
            "mode": "detect",
            "length": len(data),
            "bom": bom,
            "validation": validations,
            "candidates": candidates,
            "winner": winner,
            "declared_conflict": conflict,
            **({"declared": declared} if declared is not None else {}),
        }

    def _rank(  # noqa: C901 - the ranking ladder is one deterministic decision table
        self,
        data: bytes,
        bom: dict[str, Any],
        stats: dict[str, Any],
        validations: dict[str, dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str]:
        candidates: list[dict[str, Any]] = []
        if not data:
            return candidates, "unknown"
        if bom["found"]:
            name = bom["name"]
            entry = {"encoding": name, "confidence": 0.99 if not bom["soft"] else 0.9, "evidence": ["bom"]}
            if bom["soft"]:
                entry["note"] = "BOM signature only; payload not structurally validated"
                candidates.append(entry)
            else:
                if name in validations:
                    body = data[bom["offset_consumed"] :]
                    if name.startswith("utf-16"):
                        body_check = self._scan_utf16(body, name == "utf-16-le")
                    elif name.startswith("utf-32"):
                        body_check = self._scan_utf32(body, name == "utf-32-le")
                    else:
                        body_check = self._utf8_validation(body)
                    entry["evidence"].append(f"structural:bom-body-{'valid' if body_check['valid'] else 'invalid'}")
                candidates.append(entry)
                return candidates[: self.max_candidates], name
            return candidates[: self.max_candidates], name
        utf8_valid = validations["utf-8"]["valid"]
        utf16le = validations["utf-16-le"]
        utf16be = validations["utf-16-be"]
        utf32le = validations["utf-32-le"]
        utf32be = validations["utf-32-be"]
        # UTF-32 without BOM: bytes 1..3 of every LE unit are NUL for ASCII-heavy
        # text (phases 1-3 for LE, 0-2 for BE); phase 3 / phase 0 density is the
        # most discriminating single statistic. Checked before the ASCII and
        # UTF-16 branches because padded ASCII satisfies those weaker tests too.
        if len(data) >= 8 and len(data) % 4 == 0:
            if utf32le["valid"] and stats["null_phase3_ratio"] >= 0.9 and stats["null_ratio"] >= 0.5:
                candidates.append(
                    {
                        "encoding": "utf-32-le",
                        "confidence": 0.9,
                        "evidence": [f"null-ratio={stats['null_ratio']:.3f}", "null-ratio:phase3-aligned", "structural:utf-32-valid"],
                    }
                )
                return candidates[: self.max_candidates], "utf-32-le"
            if utf32be["valid"] and stats["null_ratio"] >= 0.5 and _phase0_null_ratio(data) >= 0.9:
                candidates.append(
                    {
                        "encoding": "utf-32-be",
                        "confidence": 0.9,
                        "evidence": [f"null-ratio={stats['null_ratio']:.3f}", "null-ratio:phase0-aligned", "structural:utf-32-valid"],
                    }
                )
                return candidates[: self.max_candidates], "utf-32-be"
        # UTF-16 without BOM: alternating NUL pattern distinguishes endianness.
        # Also checked before the ASCII branch: NUL bytes are byte-wise ASCII,
        # so padded ASCII text would otherwise short-circuit to "ascii".
        if len(data) % 2 == 0 and stats["null_ratio"] >= 0.25:
            if utf16le["valid"] and stats["null_odd_ratio"] >= 0.45 and stats["null_even_ratio"] <= 0.1:
                candidates.append(
                    {
                        "encoding": "utf-16-le",
                        "confidence": 0.8,
                        "evidence": [f"null-ratio={stats['null_ratio']:.3f}", "null-ratio:alternating-odd", "structural:utf-16-valid"],
                    }
                )
                return candidates[: self.max_candidates], "utf-16-le"
            if utf16be["valid"] and stats["null_even_ratio"] >= 0.45 and stats["null_odd_ratio"] <= 0.1:
                candidates.append(
                    {
                        "encoding": "utf-16-be",
                        "confidence": 0.8,
                        "evidence": [f"null-ratio={stats['null_ratio']:.3f}", "null-ratio:alternating-even", "structural:utf-16-valid"],
                    }
                )
                return candidates[: self.max_candidates], "utf-16-be"
        ascii_only = stats["ascii_ratio"] == 1.0 and stats["null_ratio"] == 0.0
        if ascii_only:
            candidates.append(
                {
                    "encoding": "ascii",
                    "confidence": 0.97,
                    "evidence": ["ascii-ratio=1.000", "structural:ascii"],
                }
            )
            candidates.append({"encoding": "utf-8", "confidence": 0.93, "evidence": ["structural:utf-8-valid", "ascii-ratio=1.000"]})
            return candidates[: self.max_candidates], "ascii"
        if utf8_valid:
            candidates.append(
                {
                    "encoding": "utf-8",
                    "confidence": 0.94,
                    "evidence": [
                        "structural:utf-8-valid",
                        f"ascii-ratio={stats['ascii_ratio']:.3f}",
                        f"null-ratio={stats['null_ratio']:.3f}",
                    ],
                }
            )
            others = [
                ("utf-16-le", utf16le, "structural:utf-16-valid"),
                ("utf-16-be", utf16be, "structural:utf-16-valid"),
            ]
            for name, check, evidence in others:
                if check["valid"] and len(data) % 2 == 0:
                    candidates.append({"encoding": name, "confidence": 0.4, "evidence": [evidence, "null-ratio:low"]})
            return candidates[: self.max_candidates], "utf-8"
        # Not valid UTF-8 and no BOM: 8-bit codepage or binary heuristics.
        # Structurally valid UTF-16 remains listed (no NUL pattern proves it,
        # so it cannot win, but the evidence belongs in the report).
        for name, check in (("utf-16-le", utf16le), ("utf-16-be", utf16be)):
            if check["valid"] and len(data) % 2 == 0:
                candidates.append({"encoding": name, "confidence": 0.45, "evidence": ["structural:utf-16-valid", "null-ratio:absent"]})
        binary_score = stats["control_ratio"] + stats["c1_undefined_bytes"] / len(data)
        if binary_score > 0.10:
            candidates.append(
                {
                    "encoding": "binary",
                    "confidence": 0.7,
                    "evidence": [f"control-ratio={stats['control_ratio']:.3f}", f"c1-undefined-ratio={stats['c1_undefined_bytes'] / len(data):.3f}", "structural:utf-8-invalid"],
                }
            )
            return candidates[: self.max_candidates], "binary"
        if stats["cp1252_printable_bytes"]:
            candidates.append(
                {
                    "encoding": "windows-1252",
                    "confidence": 0.55,
                    "evidence": [
                        f"high-0x80-ratio:cp1252-printables={stats['cp1252_printable_bytes']}",
                        "structural:utf-8-invalid",
                    ],
                    "note": "heuristic, low confidence: latin-1 renders these bytes as C1 controls instead",
                }
            )
            candidates.append(
                {
                    "encoding": "latin-1",
                    "confidence": 0.35,
                    "evidence": ["structural:latin-1-always-valid", "structural:utf-8-invalid"],
                    "note": "heuristic, low confidence: accepts every byte but implies C1 controls in text",
                }
            )
            return candidates[: self.max_candidates], "windows-1252"
        candidates.append(
            {
                "encoding": "latin-1",
                "confidence": 0.6,
                "evidence": ["structural:latin-1-always-valid", "structural:utf-8-invalid", f"high-ratio={stats['high_ratio']:.3f}"],
            }
        )
        return candidates[: self.max_candidates], "latin-1"

    # ------------------------------------------------------------------
    # Mojibake repair
    # ------------------------------------------------------------------
    @staticmethod
    def _mojibake_matches(text: str) -> list[str]:
        return _MOJIBAKE_SEQUENCE.findall(text)

    def _mojibake_repair_chain(self, data: bytes) -> dict[str, Any]:
        """Deterministic 1..N level UTF-8-read-as-latin-1 repair chain."""
        view = data.decode("latin-1")
        result: dict[str, Any] = {"detected": False, "levels": 0, "repair_preview": None, "double": False, "samples": []}
        matches = self._mojibake_matches(view)
        if not matches:
            return result
        result["samples"] = matches[:5]
        current = view
        for level in range(1, _MAX_MOJIBAKE_LEVELS + 1):
            try:
                candidate = current.encode("latin-1").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                if level == 1:
                    return result
                break
            if candidate == current:
                break
            current = candidate
            result["levels"] = level
            if level > 1:
                result["double"] = True
            if not self._mojibake_matches(candidate):
                break
        if result["levels"]:
            result["detected"] = True
            preview = current
            result["repair_preview"] = self._preview(preview)
            if result["levels"] > 1:
                result["note"] = "double mojibake; repair is best-effort and flagged"
        return result

    @staticmethod
    def _normalize_encoding(name: str) -> str | None:
        try:
            return codecs.lookup(name).name
        except LookupError:
            return None

    # ------------------------------------------------------------------
    # Mode implementations
    # ------------------------------------------------------------------
    def _diagnose(self, data: bytes, declared: str | None) -> dict[str, Any]:
        detection = self._detect(data, declared)
        stats = self._stats(data)
        findings: list[dict[str, Any]] = self._declared_findings(data, detection["bom"], declared)
        if stats["null_ratio"] >= 0.2:
            findings.append(
                {
                    "finding": "null_byte_ratio",
                    "severity": "info",
                    "detail": f"null byte ratio is {stats['null_ratio']:.3f}; NUL padding without a BOM is the classic UTF-16/UTF-32 hint (phase evidence: even={stats['null_even_ratio']:.3f}, odd={stats['null_odd_ratio']:.3f})",
                }
            )
        if stats["cp1252_printable_bytes"]:
            findings.append(
                {
                    "finding": "high_0x80_ratio_disambiguation",
                    "severity": "info",
                    "confidence": "low",
                    "detail": (
                        f"{stats['cp1252_printable_bytes']} byte(s) in 0x80-0x9F are printable in windows-1252 "
                        "(smart quotes, dashes, currency) but C1 controls in latin-1; this class is inherently ambiguous"
                    ),
                }
            )
        repair = self._mojibake_repair_chain(data)
        if repair["detected"]:
            if repair["levels"] > 1:
                severity = "warning"
                detail = (
                    f"payload matches the UTF-8-read-as-latin-1 signature and the signature SURVIVES one "
                    f"repair round, so the bytes are double-encoded (samples: "
                    f"{', '.join(repr(sample) for sample in repair['samples'])})"
                )
            else:
                severity = "info"
                detail = (
                    "the payload bytes are themselves valid UTF-8; the latin-1 view merely shows the classic "
                    "UTF-8-read-as-latin-1 shape (samples: "
                    f"{', '.join(repr(sample) for sample in repair['samples'])}), and the preview below is the "
                    "UTF-8 interpretation"
                )
            findings.append(
                {
                    "finding": "mojibake_utf8_read_as_latin1",
                    "severity": severity,
                    "detail": detail,
                    "repair_preview": repair["repair_preview"],
                    "levels": repair["levels"],
                }
            )
            if repair["double"]:
                findings.append(
                    {
                        "finding": "double_mojibake",
                        "severity": "warning",
                        "detail": "the signature survives one repair round; a second round was applied best-effort",
                    }
                )
        control_census = self._control_census(data)
        findings.append(control_census)
        findings.append(self._line_census(data, detection))
        return {
            "status": "success",
            "mode": "diagnose",
            "length": len(data),
            "bom": detection["bom"],
            "winner": detection["winner"],
            "declared_conflict": detection["declared_conflict"],
            "findings": findings,
        }

    def _declared_findings(self, data: bytes, bom: dict[str, Any], declared: str | None) -> list[dict[str, Any]]:
        """Return findings derived from the declared encoding, if one was provided."""
        if declared is None:
            return []
        findings: list[dict[str, Any]] = []
        normalized = self._normalize_encoding(declared)
        if normalized is None:
            return [
                {
                    "finding": "declared_encoding_unknown",
                    "severity": "error",
                    "detail": f"declared encoding is not recognized by the codec registry: {declared}",
                }
            ]
        if bom["found"] and normalized != bom["name"]:
            findings.append(
                {
                    "finding": "bom_vs_declared_mismatch",
                    "severity": "warning",
                    "detail": f"BOM indicates {bom['name']} but payload is declared {normalized}; the BOM wins and the declaration is a document author error",
                }
            )
        invalid = self._declared_invalid(data, normalized)
        if invalid is not None:
            findings.append(invalid)
        return findings

    def _declared_invalid(self, data: bytes, normalized: str) -> dict[str, Any] | None:
        structural = {
            "utf-8": lambda: self._utf8_validation(data),
            "utf-16-le": lambda: self._scan_utf16(data, True),
            "utf-16-be": lambda: self._scan_utf16(data, False),
            "utf-32-le": lambda: self._scan_utf32(data, True),
            "utf-32-be": lambda: self._scan_utf32(data, False),
        }
        if normalized in structural:
            check = structural[normalized]()
            if not check["valid"]:
                return {
                    "finding": "invalid_for_declared",
                    "severity": "error",
                    "detail": f"payload is not valid {normalized}",
                    "first_error": check["error"],
                }
            return None
        try:
            data.decode(normalized)
        except UnicodeDecodeError as exc:
            return {
                "finding": "invalid_for_declared",
                "severity": "error",
                "detail": f"payload is not valid {normalized}",
                "first_error": {"offset": exc.start, "byte": f"0x{data[exc.start]:02x}" if exc.start < len(data) else None, "reason": exc.reason},
            }
        return None

    @staticmethod
    def _control_census(data: bytes) -> dict[str, Any]:
        view = data.decode("latin-1")
        c0 = sum(1 for char in view if "\x00" <= char <= "\x1f" and char not in "\t\n\r")
        c1 = sum(1 for char in view if "\x80" <= char <= "\x9f")
        nul = view.count("\x00")
        return {
            "finding": "control_char_census",
            "severity": "info",
            "c0_controls": c0,
            "c1_controls": c1,
            "null_bytes": nul,
        }

    def _line_census(self, data: bytes, detection: dict[str, Any]) -> dict[str, Any]:
        ways: list[str] = []
        winner = detection["winner"]
        if winner in {"ascii", "utf-8"}:
            ways.append(winner)
        else:
            ways.append("utf-8")
        for candidate in detection["candidates"]:
            name = candidate["encoding"]
            if name not in ways and self._normalize_encoding(name) is not None:
                ways.append(name)
            if len(ways) >= 3:
                break
        census: dict[str, Any] = {"finding": "line_ending_census", "severity": "info", "by_decoding": {}}
        for way in ways:
            try:
                text = data.decode(way, errors="replace")
            except (LookupError, UnicodeError):
                continue
            crlf = text.count("\r\n")
            cr = len(re.findall("\r(?!\n)", text))
            lf = len(re.findall("(?<!\r)\n", text))
            census["by_decoding"][way] = {"crlf": crlf, "cr": cr, "lf": lf}
        return census

    def _validate_utf8(self, data: bytes) -> dict[str, Any]:
        errors, total = self._scan_utf8(data)
        return {
            "status": "success",
            "mode": "validate_utf8",
            "length": len(data),
            "valid": total == 0,
            "error_count": total,
            "errors_listed": len(errors),
            "errors_truncated": total > len(errors),
            "errors": errors,
        }

    def _repair_preview(self, data: bytes, target: str) -> dict[str, Any]:
        if not isinstance(target, str) or not target.strip():
            raise ValueError("repair_preview requires a target encoding")
        normalized = self._normalize_encoding(target.strip())
        if normalized is None:
            raise ValueError(f"target encoding is not recognized: {target}")
        text = data.decode(normalized, errors="replace")
        replacements = text.count("\ufffd")
        positions = [index for index, char in enumerate(text) if char == "\ufffd"]
        return {
            "status": "success",
            "mode": "repair_preview",
            "target": normalized,
            "length": len(data),
            "char_length": len(text),
            "replacement_count": replacements,
            "replacement_positions": positions[: self.max_errors],
            "replacement_positions_truncated": len(positions) > self.max_errors,
            "preview": self._preview(text),
        }

    def _preview(self, text: str) -> dict[str, Any]:
        capped = text[: self.max_preview_chars]
        return {
            "text": capped,
            "truncated": len(text) > self.max_preview_chars,
            "total_chars": len(text),
        }


def _utf16_error(label: str, unit_index: int, unit: int, reason: str) -> dict[str, Any]:
    return {
        "encoding": label,
        "valid": False,
        "error": {"offset": unit_index * 2, "byte": f"0x{(unit & 0xFF):02x}", "unit": f"0x{unit:04x}", "reason": reason},
    }


def _phase0_null_ratio(data: bytes) -> float:
    slots = (len(data) + 3) // 4
    if not slots:
        return 0.0
    hits = sum(1 for position in range(0, len(data), 4) if data[position] == 0)
    return hits / slots
