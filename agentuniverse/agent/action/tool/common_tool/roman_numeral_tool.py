#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: roman_numeral_tool.py

"""Roman numeral conversion / validation / arithmetic tool built purely
on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency numeral utility
agents can call when a prompt or a corpus mixes Roman numerals with
integers: normalizing chapter / section / edition labels, checking
hand-written numerals, or doing small arithmetic that must be reported
back in numerals.

The tool supports six modes, all restricted to the classical range
1..3999 in strict subtractive notation:

* ``to_roman`` — an integer (given as ``int`` or a pure digit string)
  in 1..3999 to its canonical Roman numeral, built from the standard
  subtractive pairs (``IV``, ``IX``, ``XL``, ``XC``, ``CD``, ``CM``).
* ``from_roman`` — a Roman numeral string (case-insensitive) to its
  integer value. Validation is strict-canonical: the input must
  re-encode to exactly itself, so malformed or non-canonical forms
  (``IIII``, ``VX``, ``IM``, ...) are rejected with a structured
  ``error`` payload that cites the specific rule violated.
* ``validate`` — a verdict payload (``valid`` + ``reason``) for a
  numeral string, returning the value and canonical form when valid
  and the violated rule when invalid.
* ``add`` / ``subtract`` / ``multiply`` — arithmetic on two Roman
  numeral operands (case-insensitive), returned as a Roman numeral
  plus its integer value. A result outside 1..3999 (including zero or
  negative results) yields a structured ``out_of_range`` error payload
  instead of raising.

The Roman-numeral rules enforced (cited in every rejection message):

1. Only the symbols ``I``=1, ``V``=5, ``X``=10, ``L``=50, ``C``=100,
   ``D``=500, ``M``=1000 are allowed.
2. ``I``, ``X``, ``C`` and ``M`` may repeat, but at most three times
   in a row; ``V``, ``L`` and ``D`` may never repeat.
3. Only ``I`` before ``V``/``X``, ``X`` before ``L``/``C`` and ``C``
   before ``D``/``M`` are valid subtractive pairs (``IV``, ``IX``,
   ``XL``, ``XC``, ``CD``, ``CM``); a symbol may never be subtracted
   from a larger one in any other combination.
4. The whole numeral must be the canonical (greedy, strict
   subtractive) encoding of its value — verified by round-trip — and
   the value must lie within 1..3999.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, empty strings, unknown mode,
missing or non-string operands, numerals over 64 characters, numbers
outside 1..3999 for ``to_roman``) raise a ``ValueError``, mirroring
the other common tools. Errors that depend on the *content being
processed* — a numeral that is not canonical Roman (wrong characters,
broken repetition / subtraction rules, value outside the classical
range) and arithmetic results outside 1..3999 — are returned as a
structured ``error`` payload so an agent can react without catching
exceptions.
"""

import re
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Greedy value table of the strict subtractive notation: the six
# subtractive pairs interleave the seven symbols in descending order.
_ROMAN_TABLE: Tuple[Tuple[int, str], ...] = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)
_SYMBOL_VALUES: Dict[str, int] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}
# Subtractive pairing rule: which symbols each subtractable symbol may
# stand before, and the only pairs therefore allowed.
_SUBTRACTS_BEFORE: Dict[str, Tuple[str, ...]] = {
    "I": ("V", "X"),
    "X": ("L", "C"),
    "C": ("D", "M"),
}
_ALLOWED_PAIRS = {"IV", "IX", "XL", "XC", "CD", "CM"}
# Repetition rule: I/X/C/M at most three in a row; V/L/D never repeat.
_OVERREPEAT = re.compile(r"(I{4,}|X{4,}|C{4,}|M{4,}|V{2,}|L{2,}|D{2,})")
_BAD_CHARS = re.compile(r"[^MDCLXVI]")
_DIGITS_ONLY = re.compile(r"\A[0-9]+\Z")

MIN_VALUE = 1
MAX_VALUE = 3999


class RomanNumeralTool(Tool):
    """Roman numeral conversion / validation / arithmetic tool.

    Attributes:
        max_numeral_chars (int): Upper bound on the ``numeral`` /
            operand string length; longer inputs are rejected before
            any work (the longest canonical numeral, 3888 =
            ``MMMDCCCLXXXVIII``, has 15 characters).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "roman_numeral_tool"
    description: str = (
        "Roman numeral tool — pure Python stdlib, no network required. "
        "Integer 1-3999 to canonical Roman numeral (mode='to_roman'), "
        "case-insensitive Roman numeral to integer with strict "
        "canonical validation by round-trip (mode='from_roman'), "
        "validity verdict with reason (mode='validate'), and numeral "
        "arithmetic add/subtract/multiply whose result must stay "
        "within 1-3999 (modes='add'/'subtract'/'multiply'). "
        "Non-canonical inputs like 'IIII', 'IM' or 'VX' are rejected "
        "with the specific violated rule."
    )

    MODES: ClassVar[tuple] = (
        "to_roman",
        "from_roman",
        "validate",
        "add",
        "subtract",
        "multiply",
    )
    ARITHMETIC_MODES: ClassVar[tuple] = ("add", "subtract", "multiply")

    max_numeral_chars: int = 64

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        number: Any = None,
        numeral: Any = None,
        a: Any = None,
        b: Any = None,
    ) -> Dict[str, Any]:
        """Run one Roman numeral operation.

        Args:
            mode (str): One of ``to_roman`` / ``from_roman`` /
                ``validate`` / ``add`` / ``subtract`` / ``multiply``.
            number (int | str): ``to_roman`` only — the integer to
                convert, given as an ``int`` or a pure digit string
                (no sign, decimal point or whitespace); must lie
                within 1..3999.
            numeral (str): ``from_roman`` / ``validate`` only — the
                Roman numeral to parse or check; case-insensitive,
                non-empty, at most 64 characters.
            a (str): Arithmetic modes only — the first operand, a
                Roman numeral string (case-insensitive).
            b (str): Arithmetic modes only — the second operand, a
                Roman numeral string (case-insensitive).

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string or integer plus the call context) or a
                structured ``error`` payload for content-level
                failures (non-canonical numerals, arithmetic results
                outside 1..3999).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "to_roman":
            value = self._validate_number(number)
            return {
                "mode": mode,
                "input": number,
                "result": self.to_roman(value),
            }
        if mode == "from_roman":
            raw = self._validate_numeral(numeral)
            value, canonical, error = self._check_canonical(raw)
            if error is not None:
                return self._error_result(
                    {"mode": mode}, error_type="invalid_roman", message=error
                )
            return {"mode": mode, "input": raw, "result": value}
        if mode == "validate":
            raw = self._validate_numeral(numeral)
            value, canonical, error = self._check_canonical(raw)
            if error is not None:
                return {
                    "mode": mode,
                    "input": raw,
                    "valid": False,
                    "reason": error,
                }
            return {
                "mode": mode,
                "input": raw,
                "valid": True,
                "value": value,
                "canonical": canonical,
                "reason": (
                    f"canonical strict subtractive notation for {value}"
                ),
            }
        return self._run_arithmetic(mode, a, b)

    # ------------------------------------------------------------------ #
    # Core conversions (pure functions)
    # ------------------------------------------------------------------ #

    @staticmethod
    def to_roman(value: int) -> str:
        """Encode an integer in 1..3999 to canonical Roman numerals."""
        parts: List[str] = []
        remaining = value
        for amount, symbol in _ROMAN_TABLE:
            count, remaining = divmod(remaining, amount)
            parts.append(symbol * count)
        return "".join(parts)

    @staticmethod
    def from_roman_value(normalized: str) -> int:
        """Decode a symbol-valid numeral to its raw left-to-right value.

        Applies the standard subtractive scan (a smaller symbol before
        a larger one subtracts). The result may be non-canonical or out
        of range — callers must verify with :meth:`_check_canonical`.
        """
        total = 0
        for index, symbol in enumerate(normalized):
            amount = _SYMBOL_VALUES[symbol]
            if (
                index + 1 < len(normalized)
                and amount < _SYMBOL_VALUES[normalized[index + 1]]
            ):
                total -= amount
            else:
                total += amount
        return total

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"roman_numeral_tool: {message}")

    @classmethod
    def _validate_number(cls, number: Any) -> int:
        """Validate the ``to_roman`` number (int or pure digit string)."""
        if isinstance(number, bool):
            cls._invalid(f"number must be an integer 1-3999 (got {number!r})")
        if isinstance(number, int):
            value = number
        elif isinstance(number, str) and _DIGITS_ONLY.match(number):
            value = int(number)
        else:
            cls._invalid(
                "number must be an integer 1-3999 or a pure digit "
                f"string without sign, decimal point or whitespace "
                f"(got {number!r})"
            )
        if not MIN_VALUE <= value <= MAX_VALUE:
            cls._invalid(
                f"number must be within 1-3999 (got {value})"
            )
        return value

    @classmethod
    def _validate_numeral(cls, numeral: Any, label: str = "numeral") -> str:
        """Validate a numeral / operand string (case kept, untrimmed)."""
        if numeral is None or isinstance(numeral, bool) or not isinstance(numeral, str):
            cls._invalid(f"{label} must be a non-empty Roman numeral string (got {numeral!r})")
        if not numeral:
            cls._invalid(f"{label} must be a non-empty Roman numeral string (got '')")
        if len(numeral) > 64:
            cls._invalid(
                f"{label} exceeds the 64-character limit "
                f"(got {len(numeral)} characters)"
            )
        return numeral

    # ------------------------------------------------------------------ #
    # Canonical check with rule citations
    # ------------------------------------------------------------------ #

    @classmethod
    def _check_canonical(cls, raw: str) -> Tuple[int, str, Any]:
        """Check a numeral string against the strict Roman rules.

        Returns a ``(value, canonical, error)`` tuple; ``error`` is
        ``None`` when the numeral is canonical (``value`` and
        ``canonical`` then hold the decoded integer and the canonical
        uppercase form), otherwise it holds a message citing the
        specific violated rule.
        """
        normalized = raw.upper()

        bad = _BAD_CHARS.search(normalized)
        if bad is not None:
            return 0, normalized, (
                "rule 1 (symbols): only the Roman symbols I, V, X, L, "
                "C, D and M are allowed; whitespace and other "
                f"characters are not (found {bad.group(0)!r} in {raw!r})"
            )

        value = cls.from_roman_value(normalized)

        repeated = _OVERREPEAT.search(normalized)
        if repeated is not None:
            token = repeated.group(0)
            if token[0] in "VLD":
                return 0, normalized, (
                    "rule 2 (repetition): V, L and D may never repeat "
                    f"(found {token!r} in {raw!r})"
                )
            return 0, normalized, (
                "rule 2 (repetition): I, X, C and M may appear at "
                f"most three times in a row (found {token!r} in {raw!r})"
            )

        for first, second in zip(normalized, normalized[1:]):
            if (
                _SYMBOL_VALUES[first] < _SYMBOL_VALUES[second]
                and first + second not in _ALLOWED_PAIRS
            ):
                if first in _SUBTRACTS_BEFORE:
                    allowed = " or ".join(
                        repr(symbol) for symbol in _SUBTRACTS_BEFORE[first]
                    )
                    return 0, normalized, (
                        "rule 3 (subtraction): I, X and C are the only "
                        f"subtractable symbols; {first!r} may only be "
                        f"subtracted from {allowed} "
                        f"(found pair {first + second!r} in {raw!r})"
                    )
                return 0, normalized, (
                    "rule 3 (subtraction): I, X and C are the only "
                    "subtractable symbols; V, L, D and M may never "
                    f"be subtracted (found pair {first + second!r} "
                    f"in {raw!r})"
                )

        if value < MIN_VALUE or value > MAX_VALUE:
            return 0, normalized, (
                "rule 4 (range): the value must lie within 1-3999 "
                f"(got {value})"
            )

        canonical = cls.to_roman(value)
        if normalized != canonical:
            return 0, normalized, (
                "rule 4 (canonical form): the numeral is not the "
                "canonical strict subtractive encoding of its value — "
                f"{value} in canonical form is {canonical!r} "
                f"(got {raw!r})"
            )

        return value, canonical, None

    # ------------------------------------------------------------------ #
    # Arithmetic modes
    # ------------------------------------------------------------------ #

    def _run_arithmetic(self, mode: str, a: Any, b: Any) -> Dict[str, Any]:
        """Compute a +|-|* b on two canonical Roman numeral operands."""
        raw_a = self._validate_numeral(a, label="a")
        raw_b = self._validate_numeral(b, label="b")
        context: Dict[str, Any] = {"mode": mode, "a": raw_a, "b": raw_b}
        value_a, _, error_a = self._check_canonical(raw_a)
        if error_a is not None:
            return self._error_result(
                context,
                error_type="invalid_roman",
                message=f"operand a: {error_a}",
            )
        value_b, _, error_b = self._check_canonical(raw_b)
        if error_b is not None:
            return self._error_result(
                context,
                error_type="invalid_roman",
                message=f"operand b: {error_b}",
            )
        left, right = value_a, value_b
        if mode == "add":
            symbol, total = "+", left + right
        elif mode == "subtract":
            symbol, total = "-", left - right
        else:
            symbol, total = "*", left * right
        context["a_value"] = left
        context["b_value"] = right
        context["expression"] = f"{left} {symbol} {right} = {total}"
        if not MIN_VALUE <= total <= MAX_VALUE:
            return self._error_result(
                context,
                error_type="out_of_range",
                message=(
                    f"arithmetic result {raw_a!r} ({left}) {symbol} "
                    f"{raw_b!r} ({right}) = {total} is outside the "
                    "representable Roman numeral range 1-3999"
                ),
            )
        return {**context, "result": self.to_roman(total), "value": total}

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
