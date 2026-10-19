#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: barcode_validator_tool.py

"""Barcode / product-identifier checksum tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency validator agents can
call for identifier plumbing: checking scanned ISBNs, EANs and UPCs,
repairing a mistyped check digit, or decoding the meaning of an ISBN
prefix before quoting it to a user.

The tool covers the five one-dimensional retail / book identifier
schemes an agent meets in practice and supports four modes:

* ``validate`` — check one identifier's checksum. The type is
  auto-detected from the shape of the stripped code (10 characters for
  ISBN-10, 13 digits for ISBN-13 / EAN-13, 12 digits for UPC-A, 8
  digits for EAN-8) unless the explicit ``code_type`` option overrides
  it. The verdict is reported per interpretation, with the full
  checksum arithmetic shown (digit * weight terms, weighted total and
  remainder), the provided and expected check digits and a plain
  reason string. A 13-digit code starting with ``978``/``979`` is
  genuinely ambiguous — it is both a candidate ISBN-13 and a candidate
  EAN-13 — so *both* interpretations are reported; the overall verdict
  is valid when at least one interpretation is valid. Content
  problems (unknown length, non-digit characters) are verdicts
  (``valid: false`` plus a reason), never exceptions.
* ``check_digit`` — compute the correct check digit for a partial
  code: 7 / 9 / 11 / 12 digits are read as EAN-8 / ISBN-10 / UPC-A /
  ISBN-13+EAN-13 data, and a full 8 / 10 / 13-character code is also
  accepted (the computed digit is then compared with the provided
  one). An explicit ``code_type`` pins the intended scheme (e.g. a
  12-character input as a *full* UPC-A rather than an ISBN-13
  partial).
* ``convert`` — ISBN-10 to ISBN-13 (prefix ``978`` plus a recomputed
  mod-10 check digit) and ISBN-13 back to ISBN-10 (drop the ``978``
  prefix, recompute the mod-11 check digit, possibly ``X``). 979-
  prefixed ISBN-13s have no ISBN-10 equivalent and general EAN-13s are
  not ISBNs; both cases return a structured ``not_convertible``
  payload. Inputs must carry a valid checksum.
* ``info`` — decode an ISBN into its GS1 prefix (``978`` / ``979``)
  and registration group via a small built-in prefix table: groups
  ``0``/``1`` English, ``2`` French, ``3`` German, ``4`` Japan,
  ``5`` Russia, ``7`` China, and ``979-0`` music (ISMN). The table is
  a deliberately small, documented-as-indicative subset — the
  authoritative registration-group ranges live with the international
  ISBN agency, and any group outside the table is reported as such.

Checksum arithmetic (standards-implemented, deterministic):

* ISBN-10 — mod 11: ``sum(digit_i * (10 - i))`` over the ten
  characters must be divisible by 11; the check digit may be ``X``
  (= 10) and ``X`` is only legal in the final position. The check
  digit for nine data digits is ``(11 - sum mod 11) mod 11`` (10 → X).
* ISBN-13 / EAN-13 / EAN-8 / UPC-A — mod 10 with alternating weights
  1 and 3 so that the full code (check digit included) sums to a
  multiple of 10. From the left the weights start at 1 for 13-digit
  codes (ISBN-13, EAN-13) and at 3 for even-length codes (UPC-A on 12
  digits, EAN-8 on 8 digits) — equivalently the check digit itself
  always carries weight 1 and the weights alternate 1, 3, 1, ... away
  from it. The check digit for the data digits is
  ``(10 - weighted sum mod 10) mod 10``.

Hyphens and spaces are the only tolerated decorations: they are
stripped everywhere before any checking (a lowercase final ``x`` is
accepted for ISBN-10 and normalised to ``X``); every other character
makes the code invalid.

Malformed parameters (unknown mode, missing / non-string / oversized
``code``, unknown ``code_type``, ``code_type`` passed to a mode that
does not use it) raise a ``ValueError`` before any computation,
mirroring the other common tools. Errors that depend on the *content
being processed* — wrong length or charset for ``check_digit`` /
``convert`` / ``info``, a bad checksum fed to ``convert``, and
non-convertible prefixes — are returned as a structured ``error``
payload so an agent can react without catching exceptions; the
``validate`` mode reports every content problem as a normal
``valid: false`` verdict instead.
"""

from typing import Any, ClassVar, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_DIGITS = frozenset("0123456789")


class BarcodeValidatorTool(Tool):
    """Barcode / product-identifier checksum tool built purely on the stdlib.

    Attributes:
        max_code_chars (int): Upper bound on the raw ``code`` input
            length (before hyphens and spaces are stripped); longer
            inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "barcode_validator_tool"
    description: str = (
        "Barcode / product identifier validator — pure Python stdlib, "
        "no network required. Validates checksums for ISBN-10, ISBN-13, "
        "EAN-13, EAN-8 and UPC-A codes: validate mode auto-detects the "
        "type from the code shape (explicit code_type overrides) and "
        "returns a per-type verdict with the full checksum arithmetic "
        "(13-digit 978/979 codes are reported as both ISBN-13 and "
        "EAN-13); check_digit mode computes the correct check digit for "
        "a partial code; convert mode switches ISBN-10 to ISBN-13 (978 "
        "prefix + recomputed check digit) and back; info mode decodes "
        "an ISBN's 978/979 GS1 prefix and registration group (0/1 "
        "English, 2 French, 3 German, 4 Japan, 5 Russia, 7 China) from "
        "a small built-in indicative table. Hyphens and spaces in the "
        "code are tolerated and stripped."
    )

    MODES: ClassVar[tuple] = ("validate", "check_digit", "convert", "info")
    TYPES: ClassVar[tuple] = ("isbn-10", "isbn-13", "ean-13", "ean-8", "upc-a")
    # code_type aliases, matched after lowercasing and dropping
    # hyphens / underscores / spaces (e.g. "ISBN13", "ean_8", "UPC").
    _TYPE_ALIASES: ClassVar[dict] = {
        "isbn10": "isbn-10",
        "isbn13": "isbn-13",
        "ean13": "ean-13",
        "ean8": "ean-8",
        "upca": "upc-a",
        "upc": "upc-a",
    }
    # Length and checksum scheme per supported identifier type.
    _TYPE_SPECS: ClassVar[dict] = {
        "isbn-10": {"length": 10, "scheme": "mod-11"},
        "isbn-13": {"length": 13, "scheme": "mod-10 (weights 1,3 from left)"},
        "ean-13": {"length": 13, "scheme": "mod-10 (weights 1,3 from left)"},
        "ean-8": {"length": 8, "scheme": "mod-10 (weights 3,1 from left)"},
        "upc-a": {"length": 12, "scheme": "mod-10 (weights 3,1 from left)"},
    }
    _FULL_LENGTHS: ClassVar[dict] = {
        "isbn-10": 10,
        "isbn-13": 13,
        "ean-13": 13,
        "ean-8": 8,
        "upc-a": 12,
    }
    # Auto-detection tables for check_digit: data-digit length ->
    # (display type, full length) and full length -> (type, full).
    _AUTO_PARTIAL: ClassVar[dict] = {
        7: ("ean-8", 8),
        9: ("isbn-10", 10),
        11: ("upc-a", 12),
        12: ("isbn-13/ean-13", 13),
    }
    _AUTO_FULL: ClassVar[dict] = {
        8: ("ean-8", 8),
        10: ("isbn-10", 10),
        13: ("isbn-13/ean-13", 13),
    }
    # Small indicative prefix tables (documented as indicative; the
    # authoritative registration-group ranges live with the ISBN agency).
    _GS1_PREFIXES: ClassVar[dict] = {
        "978": "ISBN 'bookland' — EAN prefix carrying the classic ISBN ranges",
        "979": "ISBN 'bookland' — the newer ISBN prefix (979-0 is music/ISMN)",
    }
    _GROUPS_978: ClassVar[dict] = {
        "0": "English-speaking regions",
        "1": "English-speaking regions",
        "2": "French-speaking regions",
        "3": "German-speaking regions",
        "4": "Japan",
        "5": "Russia and former USSR states",
        "7": "China (mainland)",
    }
    _GROUPS_979: ClassVar[dict] = {
        "0": "Music (ISMN)",
    }

    max_code_chars: int = 64

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        code: Any = None,
        code_type: Any = None,
    ) -> dict[str, Any]:
        """Run one barcode / identifier operation.

        Args:
            mode (str): One of ``validate`` / ``check_digit`` /
                ``convert`` / ``info``.
            code (str): The identifier to work on. Hyphens and spaces
                are stripped; a lowercase final ``x`` is accepted for
                ISBN-10 and normalised to ``X``.
            code_type (str): Optional explicit identifier type — one of
                ``isbn-10`` / ``isbn-13`` / ``ean-13`` / ``ean-8`` /
                ``upc-a`` (case-insensitive, hyphens optional). Used by
                ``validate`` (skip auto-detection) and ``check_digit``
                (pin the scheme); rejected for ``convert`` / ``info``,
                which infer the form from the code itself.

        Returns:
            Dict[str, Any]: Always includes ``mode`` and the call
                context. ``validate`` returns ``valid`` plus
                ``interpretations`` (each with ``code_type``, the
                verdict, provided / expected check digits, the checksum
                arithmetic and a reason); ``check_digit`` /
                ``convert`` / ``info`` return their computed payload or
                a structured ``error`` payload for content-level
                failures (invalid charset / length / checksum, not
                convertible, not an ISBN).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_code = self._validate_code(code)
        if mode in ("validate", "check_digit"):
            clean_type = self._validate_code_type(code_type)
        elif code_type is not None:
            self._invalid(
                "code_type is only accepted by the validate and "
                "check_digit modes; convert and info infer the form "
                "from the code itself"
            )
        else:
            clean_type = None

        if mode == "validate":
            return self._run_validate(clean_code, clean_type)
        if mode == "check_digit":
            return self._run_check_digit(clean_code, clean_type)
        if mode == "convert":
            return self._run_convert(clean_code)
        return self._run_info(clean_code)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"barcode_validator_tool: {message}")

    @classmethod
    def _validate_code(cls, code: Any) -> str:
        """Validate the ``code`` input and return its stripped form.

        Leading / trailing whitespace is removed, embedded hyphens and
        spaces are stripped, and a lowercase ``x`` is normalised to
        ``X``; anything else survives verbatim and is checked later as
        content.
        """
        if code is None or isinstance(code, bool) or not isinstance(code, str):
            cls._invalid(f"code must be a string (got {code!r})")
        if not code.strip():
            cls._invalid(
                f"code must be a non-empty string (got {code.strip()!r})"
            )
        if len(code) > 64:
            cls._invalid(
                f"code exceeds the {64}-character limit "
                f"(got {len(code)} characters)"
            )
        stripped = (
            code.strip().replace("-", "").replace(" ", "").replace("x", "X")
        )
        if not stripped:
            cls._invalid(
                "code must contain at least one character besides "
                "hyphens and spaces"
            )
        return stripped

    @classmethod
    def _validate_code_type(cls, code_type: Any) -> Optional[str]:
        """Validate the optional ``code_type`` selector."""
        if code_type is None:
            return None
        if isinstance(code_type, bool) or not isinstance(code_type, str):
            cls._invalid(
                f"code_type must be a string or None (got {code_type!r})"
            )
        alias = (
            code_type.strip()
            .lower()
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )
        canonical = cls._TYPE_ALIASES.get(alias)
        if canonical is None:
            cls._invalid(
                "code_type must be one of: "
                f"{', '.join(cls.TYPES)} (case-insensitive, optional "
                f"hyphens) (got {code_type!r})"
            )
        return canonical

    @classmethod
    def _charset_error(cls, code: str, allow_x: bool) -> Optional[str]:
        """Return a message describing the first illegal character, or None.

        ``allow_x`` permits a single ``X`` in the final position of a
        10-character code (the ISBN-10 check digit); any other
        non-digit character — including Unicode digits — is rejected.
        """
        for pos, char in enumerate(code):
            if char in _DIGITS:
                continue
            is_final_x = (
                char == "X" and pos == len(code) - 1 and len(code) == 10
            )
            if is_final_x and allow_x:
                continue
            if char == "X":
                return (
                    "'X' is only allowed as the final check digit of a "
                    f"10-character ISBN-10 (found at position {pos + 1})"
                )
            return (
                f"invalid character {char!r} at position {pos + 1}: only "
                "ASCII digits 0-9 are allowed"
            )
        return None

    # ------------------------------------------------------------------ #
    # Checksum arithmetic (pure, standard formulas)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _isbn10_value(char: str) -> int:
        """Numeric value of one ISBN-10 character (X -> 10)."""
        return 10 if char == "X" else int(char)

    @classmethod
    def _isbn10_sum(cls, code10: str) -> int:
        """Weighted sum of a full ISBN-10 (weights 10 down to 1)."""
        return sum(
            cls._isbn10_value(char) * (10 - index)
            for index, char in enumerate(code10)
        )

    @classmethod
    def _isbn10_check_digit(cls, data9: str) -> str:
        """Mod-11 check digit for nine ISBN-10 data digits ('X' for 10)."""
        total = sum(
            int(char) * (10 - index) for index, char in enumerate(data9)
        )
        value = (11 - total % 11) % 11
        return "X" if value == 10 else str(value)

    @staticmethod
    def _gs1_left_start(total_length: int) -> int:
        """Leftmost weight for a full GS1-family code of the given length.

        13-digit codes (ISBN-13, EAN-13) use 1,3,... from the left;
        even-length codes (UPC-A on 12 digits, EAN-8 on 8) use 3,1,...
        In every case the final check digit carries weight 1.
        """
        return 1 if total_length % 2 == 1 else 3

    @classmethod
    def _gs1_sum(cls, code: str) -> int:
        """Weighted sum of a full GS1-family code (check digit included)."""
        start = cls._gs1_left_start(len(code))
        return sum(
            int(char) * (start if index % 2 == 0 else 4 - start)
            for index, char in enumerate(code)
        )

    @classmethod
    def _gs1_check_digit(cls, data: str, total_length: int) -> str:
        """Mod-10 check digit for GS1-family data digits."""
        start = cls._gs1_left_start(total_length)
        total = sum(
            int(char) * (start if index % 2 == 0 else 4 - start)
            for index, char in enumerate(data)
        )
        return str((10 - total % 10) % 10)

    @classmethod
    def _isbn10_terms(cls, code10: str) -> str:
        """Rendered digit*weight terms for a full ISBN-10."""
        return " + ".join(
            f"{'X(10)' if char == 'X' else char}*{10 - index}"
            for index, char in enumerate(code10)
        )

    @staticmethod
    def _gs1_terms(data: str, total_length: int) -> str:
        """Rendered digit*weight terms for GS1-family digits."""
        start = BarcodeValidatorTool._gs1_left_start(total_length)
        return " + ".join(
            f"{char}*{start if index % 2 == 0 else 4 - start}"
            for index, char in enumerate(data)
        )

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(
        self, code: str, code_type: Optional[str]
    ) -> dict[str, Any]:
        """Validate the checksum, auto-detecting the type unless given."""
        result: dict[str, Any] = {"mode": "validate", "code": code}
        if code_type is not None:
            result["code_type"] = code_type
            interpretations = [self._interpretation(code, code_type)]
        else:
            charset_error = self._charset_error(code, allow_x=True)
            if charset_error is not None:
                result.update(
                    valid=False,
                    reason=charset_error,
                    interpretations=[],
                )
                return result
            candidates = self._auto_candidates(code)
            if not candidates:
                result.update(
                    valid=False,
                    reason=(
                        f"unrecognized identifier length: {len(code)} "
                        "characters after stripping hyphens and spaces "
                        "(expected 8 for EAN-8, 10 for ISBN-10, 12 for "
                        "UPC-A or 13 for ISBN-13/EAN-13)"
                    ),
                    interpretations=[],
                )
                return result
            result["auto_detected"] = list(candidates)
            interpretations = [
                self._interpretation(code, candidate) for candidate in candidates
            ]
            if len(candidates) == 2:
                result["note"] = (
                    "13-digit codes starting with 978 or 979 match both "
                    "the ISBN-13 and the EAN-13 interpretation (they "
                    "share the same mod-10 checksum); both are reported"
                )
        result["interpretations"] = interpretations
        result["valid"] = any(item["valid"] for item in interpretations)
        if result["valid"]:
            result["reason"] = "valid as " + ", ".join(
                item["code_type"]
                for item in interpretations
                if item["valid"]
            )
        else:
            result["reason"] = "; ".join(
                item["reason"] for item in interpretations
            )
        return result

    @classmethod
    def _auto_candidates(cls, code: str) -> tuple:
        """Shape-based type candidates for a charset-clean code."""
        length = len(code)
        if length == 13:
            if code.startswith(("978", "979")):
                return ("isbn-13", "ean-13")
            return ("ean-13",)
        if length == 12:
            return ("upc-a",)
        if length == 10:
            return ("isbn-10",)
        if length == 8:
            return ("ean-8",)
        return ()

    def _interpretation(self, code: str, code_type: str) -> dict[str, Any]:
        """Build one per-type verdict for the validate mode."""
        spec = self._TYPE_SPECS[code_type]
        provided = code[-1] if code else ""
        if len(code) != spec["length"]:
            return {
                "code_type": code_type,
                "valid": False,
                "reason": (
                    f"invalid {code_type}: expected {spec['length']} "
                    "characters after stripping hyphens and spaces, got "
                    f"{len(code)}"
                ),
            }
        charset_error = self._charset_error(
            code, allow_x=(code_type == "isbn-10")
        )
        if charset_error is not None:
            return {
                "code_type": code_type,
                "valid": False,
                "reason": f"invalid {code_type}: {charset_error}",
            }

        if code_type == "isbn-10":
            total = self._isbn10_sum(code)
            remainder = total % 11
            expected = self._isbn10_check_digit(code[:9])
            checksum = (
                f"{self._isbn10_terms(code)} = {total}; {total} mod 11 = "
                f"{remainder} -> "
                f"checksum {'valid' if remainder == 0 else 'invalid'}"
            )
            reason = (
                "checksum passes"
                if remainder == 0
                else (
                    "checksum fails: expected check digit "
                    f"{expected!r}, got {provided!r}"
                )
            )
            return {
                "code_type": code_type,
                "valid": remainder == 0,
                "provided_check_digit": provided,
                "expected_check_digit": expected,
                "checksum": checksum,
                "reason": reason,
            }

        prefix_reason = None
        if code_type == "isbn-13" and not code.startswith(("978", "979")):
            prefix_reason = (
                "invalid isbn-13: must start with '978' or '979' (got "
                f"{code[:3]!r}); a 13-digit code with another prefix can "
                "still be a valid EAN-13"
            )
        total = self._gs1_sum(code)
        remainder = total % 10
        expected = self._gs1_check_digit(code[:-1], spec["length"])
        checksum = (
            f"{self._gs1_terms(code, spec['length'])} = {total}; "
            f"{total} mod 10 = {remainder} -> checksum "
            f"{'valid' if remainder == 0 else 'invalid'}"
        )
        checksum_reason = (
            "checksum passes"
            if remainder == 0
            else (
                "checksum fails: expected check digit "
                f"{expected!r}, got {provided!r}"
            )
        )
        return {
            "code_type": code_type,
            "valid": remainder == 0 and prefix_reason is None,
            "provided_check_digit": provided,
            "expected_check_digit": expected,
            "checksum": checksum,
            "reason": prefix_reason if prefix_reason else checksum_reason,
        }

    # ------------------------------------------------------------------ #
    # check_digit mode
    # ------------------------------------------------------------------ #

    def _run_check_digit(
        self, code: str, code_type: Optional[str]
    ) -> dict[str, Any]:
        """Compute the correct check digit for a partial (or full) code."""
        context: dict[str, Any] = {"mode": "check_digit"}
        if code_type is not None:
            full = self._FULL_LENGTHS[code_type]
            label = code_type
            if len(code) == full:
                data, provided = code[:-1], code[-1]
            elif len(code) == full - 1:
                data, provided = code, None
            else:
                return self._error_result(
                    context,
                    error_type="invalid_length",
                    message=(
                        f"{code_type} expects {full - 1} data digits "
                        f"(partial) or the full {full} characters; got "
                        f"{len(code)} characters after stripping hyphens "
                        "and spaces"
                    ),
                )
        else:
            if len(code) == 10 and code.endswith("X"):
                label, data, provided = "isbn-10", code[:9], "X"
            elif len(code) in self._AUTO_PARTIAL:
                label, full = self._AUTO_PARTIAL[len(code)]
                data, provided = code, None
            elif len(code) in self._AUTO_FULL:
                label, full = self._AUTO_FULL[len(code)]
                data, provided = code[:-1], code[-1]
            else:
                return self._error_result(
                    context,
                    error_type="invalid_length",
                    message=(
                        f"unrecognized length: {len(code)} characters "
                        "after stripping hyphens and spaces — expected 7 "
                        "(EAN-8), 9 (ISBN-10), 11 (UPC-A) or 12 "
                        "(ISBN-13/EAN-13) data digits, or a full "
                        "8/10/13-character code"
                    ),
                )

        charset_error = self._charset_error(code, allow_x=(provided == "X"))
        if charset_error is not None:
            return self._error_result(
                context,
                error_type="invalid_charset",
                message=f"{label}: {charset_error}",
            )

        if label == "isbn-10":
            total = sum(
                int(char) * (10 - index) for index, char in enumerate(data)
            )
            value = (11 - total % 11) % 11
            check_digit = "X" if value == 10 else str(value)
            suffix = " -> 'X' (ten)" if value == 10 else ""
            terms = " + ".join(
                f"{char}*{10 - index}" for index, char in enumerate(data)
            )
            arithmetic = (
                f"{terms} = {total}; check digit = (11 - ({total} mod 11)) "
                f"mod 11 = {value}{suffix}"
            )
        else:
            total = sum(
                int(char)
                * (
                    self._gs1_left_start(full)
                    if index % 2 == 0
                    else 4 - self._gs1_left_start(full)
                )
                for index, char in enumerate(data)
            )
            check_digit = str((10 - total % 10) % 10)
            arithmetic = (
                f"{self._gs1_terms(data, full)} = {total}; check digit = "
                f"(10 - ({total} mod 10)) mod 10 = {check_digit}"
            )

        result: dict[str, Any] = {
            "mode": "check_digit",
            "code_type": label,
            "data": data,
            "check_digit": check_digit,
            "full_code": data + check_digit,
            "arithmetic": arithmetic,
        }
        if "/" in label:
            result["note"] = (
                "the mod-10 checksum is identical for ISBN-13 and "
                "EAN-13, so the computed check digit applies to both"
            )
        if provided is not None:
            result["provided_check_digit"] = provided
            result["matches"] = provided == check_digit
        return result

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def _run_convert(self, code: str) -> dict[str, Any]:
        """Convert between ISBN-10 and ISBN-13 (978 prefix)."""
        context: dict[str, Any] = {"mode": "convert"}
        if len(code) == 10:
            charset_error = self._charset_error(code, allow_x=True)
            if charset_error is not None:
                return self._error_result(
                    context,
                    error_type="invalid_charset",
                    message=f"isbn-10: {charset_error}",
                )
            if self._isbn10_sum(code) % 11 != 0:
                return self._error_result(
                    context,
                    error_type="invalid_checksum",
                    message=(
                        "cannot convert: the ISBN-10 checksum is invalid "
                        f"(expected check digit "
                        f"{self._isbn10_check_digit(code[:9])!r}, got "
                        f"{code[-1]!r}) — fix the code first"
                    ),
                )
            data13 = "978" + code[:9]
            isbn13 = data13 + self._gs1_check_digit(data13, 13)
            return {
                "mode": "convert",
                "input": code,
                "from": "isbn-10",
                "to": "isbn-13",
                "result": isbn13,
                "note": (
                    "prefixed with 978 and the ISBN-13 check digit is "
                    "recomputed with the mod-10 1,3 weighting"
                ),
            }

        if len(code) == 13:
            charset_error = self._charset_error(code, allow_x=False)
            if charset_error is not None:
                return self._error_result(
                    context,
                    error_type="invalid_charset",
                    message=f"isbn-13: {charset_error}",
                )
            if not code.startswith(("978", "979")):
                return self._error_result(
                    context,
                    error_type="not_convertible",
                    message=(
                        "only EAN-13 codes starting with 978 or 979 are "
                        "ISBNs; a general EAN-13 cannot be converted to "
                        "ISBN-10"
                    ),
                )
            if self._gs1_sum(code) % 10 != 0:
                return self._error_result(
                    context,
                    error_type="invalid_checksum",
                    message=(
                        "cannot convert: the ISBN-13 checksum is invalid "
                        f"(expected check digit "
                        f"{self._gs1_check_digit(code[:-1], 13)!r}, got "
                        f"{code[-1]!r}) — fix the code first"
                    ),
                )
            if code.startswith("979"):
                return self._error_result(
                    context,
                    error_type="not_convertible",
                    message=(
                        "979-prefixed ISBN-13 codes have no ISBN-10 "
                        "equivalent: the 979 prefix was introduced "
                        "together with ISBN-13"
                    ),
                )
            isbn10 = code[3:12] + self._isbn10_check_digit(code[3:12])
            return {
                "mode": "convert",
                "input": code,
                "from": "isbn-13",
                "to": "isbn-10",
                "result": isbn10,
                "note": (
                    "the 978 prefix is dropped and the ISBN-10 check "
                    "digit is recomputed with the mod-11 weighting"
                ),
            }

        return self._error_result(
            context,
            error_type="invalid_length",
            message=(
                "conversion expects a 10-character ISBN-10 or a "
                f"13-character ISBN-13; got {len(code)} characters after "
                "stripping hyphens and spaces"
            ),
        )

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def _run_info(self, code: str) -> dict[str, Any]:
        """Decode an ISBN into its GS1 prefix and registration group."""
        context: dict[str, Any] = {"mode": "info"}
        if len(code) == 10:
            charset_error = self._charset_error(code, allow_x=True)
            if charset_error is not None:
                return self._error_result(
                    context,
                    error_type="invalid_charset",
                    message=f"isbn-10: {charset_error}",
                )
            input_form = "isbn-10"
            checksum_valid = self._isbn10_sum(code) % 11 == 0
            data13 = "978" + code[:9]
            isbn13 = data13 + self._gs1_check_digit(data13, 13)
            isbn10: Optional[str] = code
            core9 = code[:9]
        elif len(code) == 13:
            charset_error = self._charset_error(code, allow_x=False)
            if charset_error is not None:
                return self._error_result(
                    context,
                    error_type="invalid_charset",
                    message=f"isbn-13: {charset_error}",
                )
            if not code.startswith(("978", "979")):
                return self._error_result(
                    context,
                    error_type="not_isbn",
                    message=(
                        "13-digit codes must start with 978 or 979 to be "
                        f"ISBNs (got {code[:3]!r}); use the validate mode "
                        "to check a plain EAN-13"
                    ),
                )
            input_form = "isbn-13"
            checksum_valid = self._gs1_sum(code) % 10 == 0
            isbn13 = code
            if code.startswith("978"):
                isbn10 = code[3:12] + self._isbn10_check_digit(code[3:12])
            else:
                isbn10 = None
            core9 = code[3:12]
        else:
            return self._error_result(
                context,
                error_type="invalid_length",
                message=(
                    "info expects a 10-character ISBN-10 or a "
                    f"13-character ISBN-13; got {len(code)} characters "
                    "after stripping hyphens and spaces"
                ),
            )

        prefix = isbn13[:3]
        group_digit = core9[0]
        group_table = self._GROUPS_979 if prefix == "979" else self._GROUPS_978
        group_meaning = group_table.get(
            group_digit, "not in the built-in indicative table"
        )
        result: dict[str, Any] = {
            "mode": "info",
            "input_form": input_form,
            "isbn13": isbn13,
            "gs1_prefix": prefix,
            "gs1_prefix_meaning": self._GS1_PREFIXES[prefix],
            "registration_group": group_digit,
            "registration_group_meaning": group_meaning,
            "checksum_valid": checksum_valid,
            "note": (
                "prefix and group meanings come from a small built-in "
                "indicative table (0/1 English, 2 French, 3 German, "
                "4 Japan, 5 Russia, 7 China; 979-0 music) — not the "
                "authoritative ISBN register"
            ),
        }
        result["isbn10"] = isbn10
        return result

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
