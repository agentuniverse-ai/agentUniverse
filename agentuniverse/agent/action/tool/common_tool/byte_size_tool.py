#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: byte_size_tool.py

"""Byte-size parsing / formatting / conversion tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in integration)
with a zero-network, zero-dependency size utility.  ``NumberFormatterTool``
formats a *number of bytes* into a human-readable string; this tool is the
inverse direction plus the unit-system conversions agents keep re-implementing:
turning strings such as ``"10KB"`` or ``"1.5 MiB"`` back into exact integer
byte counts, switching between the decimal and binary unit systems, and
comparing two size expressions.

Modes
-----

* ``parse`` — a size string to an exact integer byte count.  The unit set is
  strict and closed:

  ============  =====================  ==========================
  Unit(s)       Meaning                Multiplier
  ============  =====================  ==========================
  ``B``         byte (or bare number)  1 byte
  ``KB``/``kB`` decimal kilobyte       1000 bytes
  ``MB``/``mB`` decimal megabyte       1000^2 bytes
  ``GB``/``gB`` decimal gigabyte       1000^3 bytes
  ``TB``/``tB`` decimal terabyte       1000^4 bytes
  ``PB``/``pB`` decimal petabyte       1000^5 bytes
  ``KiB``       binary kibibyte        1024 bytes
  ``MiB``       binary mebibyte        1024^2 bytes
  ``GiB``       binary gibibyte        1024^3 bytes
  ``TiB``       binary tebibyte        1024^4 bytes
  ``PiB``       binary pebibyte        1024^5 bytes
  ``b``         bit                    1 bit
  ``kb``/``Kb`` decimal kilobit        1000 bits
  ``mb``/``Mb`` decimal megabit        1000^2 bits
  ``gb``/``Gb`` decimal gigabit        1000^3 bits
  ``tb``/``Tb`` decimal terabit        1000^4 bits
  ``pb``/``Pb`` decimal petabit        1000^5 bits
  ============  =====================  ==========================

  Exact case rules: byte units end in an uppercase ``B`` and their prefix
  letter is case-insensitive (``KB`` and ``kB`` are both 1000 bytes); the
  IEC/JEDEC binary forms are case-sensitive and must be spelled exactly
  ``KiB`` / ``MiB`` / ``GiB`` / ``TiB`` / ``PiB`` (``KIB``, ``kib`` or
  ``Kib`` are unknown units); any unit ending in a lowercase ``b`` is a
  *bit* unit (so ``"2 gb"`` is 2 gigabits, not 2 gigabytes).  Bit amounts
  are converted with ``x / 8`` — ``"10kb"`` is 10,000 bits = 1250 bytes
  exactly; a bit amount that is not a whole multiple of 8 (``"1.5 kb"`` =
  187.5 bytes) is rejected instead of silently rounded.  A bare number
  (``"512"``) means bytes.  Whitespace between number and unit (and around
  the whole string) is tolerated; scientific notation, thousands separators
  and reversed order are not.  The result must be a whole number of bytes
  (``"1.5 KiB"`` = 1536 is fine, ``"0.5 B"`` is not).

* ``format`` — an integer byte count to the shortest clean string.  The unit
  system is selected with ``system``: ``decimal`` (``B``, ``KB``, ``MB``,
  ...), ``binary`` (``B``, ``KiB``, ``MiB``, ...) or ``auto`` — ``auto``
  resolves to the decimal system, chosen because SI labels are the
  unambiguous, standards-preferred display; pass ``binary`` explicitly when
  the 1024-based reading is wanted.  ``precision`` (default 1, range 0-9)
  bounds the decimals, trailing zeros are trimmed (1500 -> ``"1.5 KB"``,
  not ``"1.50 KB"``) and rounding is half-up with carry into the next unit
  (999999 bytes -> ``"1 MB"``).  ``as_bits=True`` formats the value as a
  bit string (``1250`` -> ``"10 kb"``) using the decimal bit units; bit
  formatting cannot be combined with ``system='binary'``.

* ``convert`` — a size string to an exact quantity in a target unit:
  ``"10 MiB"`` to ``MB`` is exactly ``10.48576``.  Arithmetic is done with
  ``decimal.Decimal`` (never binary floats), the exact decimal string is
  returned as ``result`` alongside the nearest float as ``value``; when the
  float cannot represent the exact value, a ``note`` says so.

* ``compare`` — two size strings to a boolean plus both parsed values:
  ``"10MB"`` vs ``"10000000B"`` are equal.

Byte magnitudes are bounded to the signed 64-bit range (0 to 2^63 - 1).
Negative values are rejected unless ``allow_negative=True``.

Malformed *parameters* — unknown mode / system / target unit, wrong types,
non-integer or negative format values, precision outside 0-9, oversized
input strings — raise ``ValueError`` before any computation, mirroring the
other common tools.  Errors that depend on the *content being parsed* —
unrecognised size syntax, unknown unit (the valid set is listed in the
message), fractional bytes, bit amounts not divisible by 8, negatives
without ``allow_negative``, out-of-range magnitudes — are returned as a
structured ``error`` payload so an agent can react without catching
exceptions.
"""

import re
from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Any, ClassVar, Dict, List, Tuple

from agentuniverse.agent.action.tool.tool import Tool

# size string: optional sign, plain decimal number, optional alphabetic unit;
# whitespace tolerated around the string and between number and unit.
_SIZE_RE = re.compile(r"\A\s*([+-]?)(\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*\Z")
_INTEGRAL_RE = re.compile(r"\A\+?\d+\Z")

# kind is one of: "bytes" (plain B / bare number), "decimal" (1000^n bytes),
# "binary" (1024^n bytes) or "bits" (1000^n bits, or a single bit).
_UNITS: Dict[str, Tuple[str, int]] = {
    "B": ("bytes", 1),
    "KB": ("decimal", 1000),
    "kB": ("decimal", 1000),
    "MB": ("decimal", 1000**2),
    "mB": ("decimal", 1000**2),
    "GB": ("decimal", 1000**3),
    "gB": ("decimal", 1000**3),
    "TB": ("decimal", 1000**4),
    "tB": ("decimal", 1000**4),
    "PB": ("decimal", 1000**5),
    "pB": ("decimal", 1000**5),
    "KiB": ("binary", 1024),
    "MiB": ("binary", 1024**2),
    "GiB": ("binary", 1024**3),
    "TiB": ("binary", 1024**4),
    "PiB": ("binary", 1024**5),
    "b": ("bits", 1),
    "kb": ("bits", 1000),
    "Kb": ("bits", 1000),
    "mb": ("bits", 1000**2),
    "Mb": ("bits", 1000**2),
    "gb": ("bits", 1000**3),
    "Gb": ("bits", 1000**3),
    "tb": ("bits", 1000**4),
    "Tb": ("bits", 1000**4),
    "pb": ("bits", 1000**5),
    "Pb": ("bits", 1000**5),
}

_VALID_UNITS_HELP = (
    "valid units: 'B' (bytes, also the meaning of a bare number); "
    "decimal byte units 'KB'/'kB', 'MB'/'mB', 'GB'/'gB', 'TB'/'tB', "
    "'PB'/'pB' (1000^n bytes); binary byte units 'KiB', 'MiB', 'GiB', "
    "'TiB', 'PiB' (1024^n bytes, case-sensitive); bit units 'b', "
    "'kb'/'Kb', 'mb'/'Mb', 'gb'/'Gb', 'tb'/'Tb', 'pb'/'Pb' (1000^n bits, "
    "divided by 8 to bytes)"
)

# Output label ladders used by the format mode (canonical spellings).
_DECIMAL_LADDER: List[Tuple[int, str]] = [
    (1, "B"), (1000, "KB"), (1000**2, "MB"), (1000**3, "GB"),
    (1000**4, "TB"), (1000**5, "PB"),
]
_BINARY_LADDER: List[Tuple[int, str]] = [
    (1, "B"), (1024, "KiB"), (1024**2, "MiB"), (1024**3, "GiB"),
    (1024**4, "TiB"), (1024**5, "PiB"),
]
_BIT_LADDER: List[Tuple[int, str]] = [
    (1, "b"), (1000, "kb"), (1000**2, "Mb"), (1000**3, "Gb"),
    (1000**4, "Tb"), (1000**5, "Pb"),
]


def _clean_decimal(value: Decimal) -> str:
    """Render a Decimal in plain (never scientific) notation, trailing
    zeros trimmed: ``Decimal('1.50')`` -> ``"1.5"``, ``Decimal('1E+3')`` ->
    ``"1000"``, ``Decimal('8.88E-16')`` -> ``"0.000000000000000888"``.

    ``normalize`` obeys the active context precision, so it runs inside a
    generous context to avoid rounding long quotients.
    """
    with localcontext() as context:
        context.prec = 200
        return format(value.normalize(), "f")


class ByteSizeTool(Tool):
    """Parse, format, convert and compare byte-size strings, stdlib only.

    Attributes:
        max_input_chars (int): Upper bound on the length of a size string;
            longer inputs are rejected before any work.
    """

    name: str = "byte_size_tool"
    description: str = (
        "Byte-size tool — pure Python stdlib, no network required. Parse a "
        "size string to exact integer bytes ('10KB', '1.5 MiB', '2 gb' "
        "bits, '512B', bare numbers mean bytes) (mode='parse'); format an "
        "integer byte count to the shortest clean string with a "
        "decimal/binary/auto unit system, precision and trailing-zero trim "
        "or a bits string (mode='format'); convert between units with "
        "exact decimal arithmetic ('10 MiB' to MB = 10.48576) "
        "(mode='convert'); and compare two size expressions (mode="
        "'compare')."
    )

    MODES: ClassVar[Tuple[str, ...]] = ("parse", "format", "convert", "compare")
    SYSTEMS: ClassVar[Tuple[str, ...]] = ("auto", "decimal", "binary")
    # Byte magnitudes are bounded to the signed 64-bit range.
    MAX_BYTES: ClassVar[int] = 2**63 - 1
    PRECISION_RANGE: ClassVar[Tuple[int, int]] = (0, 9)

    max_input_chars: int = 200

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any,
        size: Any = None,
        target_unit: Any = None,
        size_a: Any = None,
        size_b: Any = None,
        value: Any = None,
        system: Any = None,
        precision: Any = None,
        as_bits: Any = None,
        allow_negative: Any = None,
    ) -> Dict[str, Any]:
        """Run one byte-size operation.

        Args:
            mode (str): One of ``parse`` / ``format`` / ``convert`` /
                ``compare``.
            size (str): The size string — required for ``parse`` and
                ``convert``.
            target_unit (str): ``convert`` only — any unit from the table
                above (byte or bit), e.g. ``"MB"`` or ``"kb"``.
            size_a (str): ``compare`` only — the first size string.
            size_b (str): ``compare`` only — the second size string.
            value (int | str): ``format`` only — the non-negative integer
                byte count (an ``int`` or a digit string; floats are
                rejected to avoid binary precision loss).
            system (str): ``format`` only — ``decimal`` / ``binary`` /
                ``auto``; ``auto`` (the default) resolves to decimal.
            precision (int): ``format`` only — maximum decimals (0-9,
                default 1); trailing zeros are trimmed.
            as_bits (bool): ``format`` only — emit a bit string
                (``1250`` bytes -> ``"10 kb"``); decimal bit units only.
            allow_negative (bool): Permit negative magnitudes in
                ``parse`` / ``convert`` / ``compare`` (default False).

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string for parse/format, exact decimal plus float for
                convert, boolean plus both parsed values for compare) or a
                structured ``error`` payload for content-level failures.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "parse":
            clean_size = self._validate_size_arg("size", size)
            return self._run_parse(clean_size, allow_negative)
        if mode == "format":
            return self._run_format(value, system, precision, as_bits)
        if mode == "convert":
            clean_size = self._validate_size_arg("size", size)
            clean_target = self._validate_target_unit(target_unit)
            return self._run_convert(clean_size, clean_target, allow_negative)
        clean_a = self._validate_size_arg("size_a", size_a)
        clean_b = self._validate_size_arg("size_b", size_b)
        return self._run_compare(clean_a, clean_b, allow_negative)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"byte_size_tool: {message}")

    @classmethod
    def _validate_size_arg(cls, param: str, size: Any) -> str:
        """Validate a size-string parameter (type and length only)."""
        if (
            size is None
            or isinstance(size, bool)
            or not isinstance(size, str)
            or not size.strip()
        ):
            cls._invalid(f"{param} must be a non-empty string (got {size!r})")
        if len(size) > 200:
            cls._invalid(
                f"{param} exceeds the {200}-character limit "
                f"(got {len(size)} characters)"
            )
        return size

    @classmethod
    def _validate_target_unit(cls, target_unit: Any) -> str:
        """Validate the convert-mode target unit."""
        if (
            target_unit is None
            or isinstance(target_unit, bool)
            or not isinstance(target_unit, str)
        ):
            cls._invalid(
                f"target_unit must be a unit string (got {target_unit!r})"
            )
        cleaned = target_unit.strip()
        if cleaned not in _UNITS:
            cls._invalid(
                f"target_unit must be one of: {_VALID_UNITS_HELP} "
                f"(got {target_unit!r})"
            )
        return cleaned

    @classmethod
    def _validate_format_value(cls, value: Any) -> int:
        """Validate the format-mode byte count (non-negative int)."""
        if isinstance(value, bool):
            cls._invalid(f"value must be a non-negative integer (got {value!r})")
        if isinstance(value, int):
            cleaned = value
        elif isinstance(value, str) and _INTEGRAL_RE.match(value.strip()):
            cleaned = int(value.strip())
        else:
            cls._invalid(
                "value must be a non-negative integer byte count given as "
                "an int or a digit string — floats are rejected to avoid "
                f"binary precision loss (got {value!r})"
            )
        if cleaned < 0:
            cls._invalid(f"value must be a non-negative integer (got {cleaned})")
        if cleaned > cls.MAX_BYTES:
            cls._invalid(
                "value exceeds the byte bound of "
                f"2^63 - 1 = {cls.MAX_BYTES} (got {cleaned})"
            )
        return cleaned

    @classmethod
    def _validate_options(
        cls, system: Any, precision: Any, as_bits: Any
    ) -> Tuple[str, int, bool]:
        """Validate the format-mode options."""
        resolved_system = "auto" if system is None else system
        if resolved_system not in cls.SYSTEMS:
            cls._invalid(
                "system must be one of: "
                f"{', '.join(cls.SYSTEMS)} (got {system!r})"
            )
        resolved_precision = 1 if precision is None else precision
        if isinstance(precision, bool) or not isinstance(resolved_precision, int):
            cls._invalid(f"precision must be an integer (got {precision!r})")
        low, high = cls.PRECISION_RANGE
        if not low <= resolved_precision <= high:
            cls._invalid(
                f"precision must be between {low} and {high} "
                f"(got {resolved_precision})"
            )
        resolved_bits = bool(as_bits) if as_bits is not None else False
        if as_bits is not None and not isinstance(as_bits, bool):
            cls._invalid(f"as_bits must be a boolean (got {as_bits!r})")
        if resolved_bits and resolved_system == "binary":
            cls._invalid(
                "bit formatting is decimal-only — system='binary' cannot be "
                "combined with as_bits=True"
            )
        return resolved_system, resolved_precision, resolved_bits

    @classmethod
    def _validate_allow_negative(cls, allow_negative: Any) -> bool:
        """Validate the allow_negative flag."""
        if allow_negative is None:
            return False
        if not isinstance(allow_negative, bool):
            cls._invalid(
                f"allow_negative must be a boolean (got {allow_negative!r})"
            )
        return allow_negative

    # ------------------------------------------------------------------ #
    # Size-string parsing (shared by parse / convert / compare)
    # ------------------------------------------------------------------ #

    def _parse_size_string(
        self, size: str, allow_negative: bool, label: str = "size"
    ) -> Dict[str, Any]:
        """Parse one size string; returns a parsed dict or an error payload."""
        context: Dict[str, Any] = {"input": size}
        match = _SIZE_RE.match(size)
        if match is None:
            return self._error_result(
                context,
                error_type="invalid_size_string",
                message=(
                    "input is not a valid size string — expected a plain "
                    "decimal number with an optional unit, e.g. '10KB', "
                    "'1.5 MiB', '2 gb' (bits) or '512' (bare bytes); "
                    "scientific notation, thousands separators and reversed "
                    f"order are not accepted (got {size[:64]!r})"
                ),
                label=label,
            )
        sign, number, unit = match.group(1), match.group(2), match.group(3)
        if unit is not None and unit not in _UNITS:
            return self._error_result(
                context,
                error_type="invalid_unit",
                message=(
                    f"unknown unit {unit!r} in {label} — {_VALID_UNITS_HELP}; "
                    "a bare number means bytes"
                ),
                label=label,
            )
        kind, multiplier = ("bytes", 1) if unit is None else _UNITS[unit]
        amount = Decimal(f"{sign}{number}") * multiplier
        if kind == "bits":
            if amount != amount.to_integral_value():
                return self._error_result(
                    context,
                    error_type="non_integer_bytes",
                    message=(
                        f"{label} does not describe a whole number of bits: "
                        f"{number}{unit} = {amount} bits; bits are converted "
                        "to bytes with x/8 and the result must be exact"
                    ),
                    label=label,
                )
            bits = int(amount)
            if bits % 8 != 0:
                return self._error_result(
                    context,
                    error_type="non_integer_bytes",
                    message=(
                        f"{label} bit amount is not a whole multiple of 8 "
                        f"bits: {number}{unit} = {bits} bits; bits are "
                        "converted to bytes with x/8 (e.g. 10kb = 10000 "
                        "bits = 1250 bytes)"
                    ),
                    label=label,
                )
            total_bytes = bits // 8
        else:
            if amount != amount.to_integral_value():
                return self._error_result(
                    context,
                    error_type="non_integer_bytes",
                    message=(
                        f"{label} does not describe a whole number of bytes: "
                        f"{number}{unit if unit else ''} = {amount} bytes"
                    ),
                    label=label,
                )
            total_bytes = int(amount)
        if total_bytes < 0 and not allow_negative:
            return self._error_result(
                context,
                error_type="negative_not_allowed",
                message=(
                    f"{label} is negative ({size!r}); pass "
                    "allow_negative=True to accept negative magnitudes"
                ),
                label=label,
            )
        if abs(total_bytes) > self.MAX_BYTES:
            return self._error_result(
                context,
                error_type="out_of_range",
                message=(
                    f"{label} exceeds the byte bound of 2^63 - 1 = "
                    f"{self.MAX_BYTES} (got {total_bytes})"
                ),
                label=label,
            )
        parsed: Dict[str, Any] = {
            "input": size,
            "number": number,
            "unit": unit,
            "unit_kind": kind,
            "bytes": total_bytes,
        }
        if kind == "bits":
            parsed["bits"] = int(amount)
            parsed["note"] = "bit unit: bits divided by 8 to bytes"
        return parsed

    # ------------------------------------------------------------------ #
    # parse mode
    # ------------------------------------------------------------------ #

    def _run_parse(self, size: str, allow_negative: Any) -> Dict[str, Any]:
        """Parse a size string into an exact integer byte count."""
        flag = self._validate_allow_negative(allow_negative)
        return {"mode": "parse", **self._parse_size_string(size, flag)}

    # ------------------------------------------------------------------ #
    # format mode
    # ------------------------------------------------------------------ #

    def _run_format(
        self, value: Any, system: Any, precision: Any, as_bits: Any
    ) -> Dict[str, Any]:
        """Format an integer byte count as the shortest clean string."""
        byte_count = self._validate_format_value(value)
        resolved_system, resolved_precision, bits_mode = self._validate_options(
            system, precision, as_bits
        )
        if bits_mode:
            ladder = _BIT_LADDER
            amount = byte_count * 8
        elif resolved_system == "binary":
            ladder = _BINARY_LADDER
            amount = byte_count
        else:
            ladder = _DECIMAL_LADDER
            amount = byte_count

        index = 0
        for position in range(len(ladder) - 1, -1, -1):
            if amount >= ladder[position][0]:
                index = position
                break
        scaled = Decimal(amount) / Decimal(ladder[index][0])
        rounded = scaled.quantize(
            Decimal(1).scaleb(-resolved_precision), rounding=ROUND_HALF_UP
        )
        # Ratio between consecutive units (1000 for decimal/bits, 1024 for
        # binary); rounding may carry into the next unit (999999 -> "1 MB").
        step = ladder[1][0] // ladder[0][0]
        while index < len(ladder) - 1 and rounded >= step:
            index += 1
            rounded = rounded / Decimal(step)
        return {
            "mode": "format",
            "bytes": byte_count,
            "system": resolved_system,
            "precision": resolved_precision,
            "as_bits": bits_mode,
            "result": f"{_clean_decimal(rounded)} {ladder[index][1]}",
            "unit": ladder[index][1],
        }

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def _run_convert(
        self, size: str, target_unit: str, allow_negative: Any
    ) -> Dict[str, Any]:
        """Convert a size string into an exact quantity of a target unit."""
        flag = self._validate_allow_negative(allow_negative)
        parsed = self._parse_size_string(size, flag)
        if "error" in parsed:
            return {"mode": "convert", **parsed}
        target_kind, target_multiplier = _UNITS[target_unit]
        if target_kind == "bits":
            numerator = Decimal(parsed["bytes"] * 8)
            denominator = Decimal(target_multiplier)
        else:
            numerator = Decimal(parsed["bytes"])
            denominator = Decimal(target_multiplier)
        # Every unit ratio is 2^a * 5^b, so the quotient terminates well
        # within 100 significant digits; exactness is still verified, in a
        # wider context so the verification product itself cannot round.
        with localcontext() as context:
            context.prec = 100
            quotient = numerator / denominator
        with localcontext() as context:
            context.prec = 300
            exact = quotient * denominator == numerator
        text = _clean_decimal(quotient)
        float_value = float(quotient)
        result: Dict[str, Any] = {
            "mode": "convert",
            "input": size,
            "source_unit": parsed["unit"],
            "source_bytes": parsed["bytes"],
            "target_unit": target_unit,
            "result": text,
            "value": float_value,
            "exact": exact,
        }
        if not exact:
            result["note"] = (
                "the division did not terminate within 100 significant "
                "digits; 'result' is truncated and 'value' is approximate"
            )
        elif Decimal(float_value) != quotient:
            result["note"] = (
                "'value' is the nearest binary float to the exact result; "
                "use the 'result' string when exactness matters"
            )
        return result

    # ------------------------------------------------------------------ #
    # compare mode
    # ------------------------------------------------------------------ #

    def _run_compare(
        self, size_a: str, size_b: str, allow_negative: Any
    ) -> Dict[str, Any]:
        """Compare two size strings by their exact byte counts."""
        flag = self._validate_allow_negative(allow_negative)
        parsed_a = self._parse_size_string(size_a, flag, label="size_a")
        if "error" in parsed_a:
            return {"mode": "compare", **parsed_a}
        parsed_b = self._parse_size_string(size_b, flag, label="size_b")
        if "error" in parsed_b:
            return {"mode": "compare", **parsed_b}
        bytes_a, bytes_b = parsed_a["bytes"], parsed_b["bytes"]
        if bytes_a == bytes_b:
            relation = "a == b"
        elif bytes_a < bytes_b:
            relation = "a < b"
        else:
            relation = "a > b"
        return {
            "mode": "compare",
            "a": parsed_a,
            "b": parsed_b,
            "equal": bytes_a == bytes_b,
            "relation": relation,
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        label: str = "size",
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {
                "type": error_type,
                "message": str(message)[:500],
                "argument": label,
            },
        }
