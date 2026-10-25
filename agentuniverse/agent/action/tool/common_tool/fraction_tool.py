#!/usr/bin/env python3
"""Exact rational arithmetic for agents, pinned to fractions.Fraction semantics."""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003, TRY301

import re
import unicodedata
from fractions import Fraction
from math import isfinite
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

# Exact values of the Unicode vulgar-fraction characters: the Latin-1
# halves/quarters plus the Number Forms thirds/fifths/sixths/sevenths/
# eighths/ninths/tenths blocks.
_VULGAR_VALUES: dict[str, tuple[int, int]] = {
    "¼": (1, 4),
    "½": (1, 2),
    "¾": (3, 4),
    "⅐": (1, 7),
    "⅑": (1, 9),
    "⅒": (1, 10),
    "⅓": (1, 3),
    "⅔": (2, 3),
    "⅕": (1, 5),
    "⅖": (2, 5),
    "⅗": (3, 5),
    "⅘": (4, 5),
    "⅙": (1, 6),
    "⅚": (5, 6),
    "⅛": (1, 8),
    "⅜": (3, 8),
    "⅝": (5, 8),
    "⅞": (7, 8),
}
_VULGAR_CHARS = "".join(_VULGAR_VALUES)

_SIGNED = r"([+-]?)"
_UNSIGNED_INT = r"([0-9]+)"

# '3/4', '1/-2' (signs on either part) and mixed numbers like '-2 3/8'. For a
# mixed number any negative sign applies to the whole value, wherever it sits.
_MIXED_RE = re.compile(rf"^{_SIGNED}{_UNSIGNED_INT}\s+{_SIGNED}{_UNSIGNED_INT}/{_UNSIGNED_INT}$")
_FRACTION_RE = re.compile(rf"^{_SIGNED}{_UNSIGNED_INT}\s*/\s*{_SIGNED}{_UNSIGNED_INT}$")
_VULGAR_RE = re.compile(rf"^{_SIGNED}([{re.escape(_VULGAR_CHARS)}])$")
# Plain decimals and scientific notation; Fraction() yields the exact value.
_DECIMAL_RE = re.compile(rf"^{_SIGNED}(?=[0-9.])([0-9]*)(?:\.([0-9]*))?(?:[eE]([+-]?[0-9]+))?$")
# Repeating-decimal notation: '0.(3)', '0.1(6)', '-2.1(6)'. No exponent form.
_REPEATING_RE = re.compile(rf"^{_SIGNED}([0-9]*)(?:\.([0-9]*))?(?:\(([0-9]+)\))?$")

# Expression tokens: slash fractions, decimals/integers/scientific notation,
# vulgar characters, operators, and parentheses.
_NUMBER_TOKEN = (
    r"[0-9]+/[0-9]+"
    r"|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
    r"|[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)?"
    rf"|[{re.escape(_VULGAR_CHARS)}]"
)
_TOKEN_RE = re.compile(rf"\s*(?P<token>{_NUMBER_TOKEN}|[-+*/()])\s*")
# After a '/' operator an unspaced 'N/N' must NOT glue into one literal, so
# that '3.75 / 80/45' evaluates left-associatively like ordinary division.
_NUMBER_TOKEN_WITHOUT_FRACTION = (
    r"[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
    r"|[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)?"
    rf"|[{re.escape(_VULGAR_CHARS)}]"
)
_TOKEN_NO_FRACTION_RE = re.compile(rf"\s*(?P<token>{_NUMBER_TOKEN_WITHOUT_FRACTION}|[-+*/()])\s*")

_PREVIEW_DIGITS = 20


class FractionTool(Tool):
    """Parse, compute with, and convert exact rational numbers.

    All arithmetic uses fractions.Fraction, so results carry no floating-point
    error. Mixed numbers ('1 1/2'), signed parts ('1/-2', '2 -1/2'), Unicode
    vulgar fractions ('½ ⅓ ⅔ ¾ ⅕..⅞') and repeating-decimal notation
    ('0.1(6)') are supported. Every mode is deterministic and bounded by the
    configured caps.
    """

    max_input_length: int = 10_000
    max_expression_length: int = 10_000
    max_operations: int = 10_000
    max_parse_depth: int = 200
    max_digits: int = 30
    max_digits_limit: int = 10_000
    max_period: int = 10_000
    max_denominator: int = 1_000_000

    _MODES: ClassVar[tuple[str, ...]] = ("parse", "compute", "to_decimal", "to_fraction", "compare")

    def execute(
        self,
        mode: str,
        value: Any = None,
        expression: str | None = None,
        other: str | None = None,
        max_digits: int | None = None,
        max_denominator: int | None = None,
        normalize: bool = False,
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            if not isinstance(normalize, bool):
                raise TypeError("normalize must be a boolean")
            operation = self._mode(mode)
            if operation == "parse":
                return self._parse(value, normalize)
            if operation == "compute":
                return self._compute(expression)
            if operation == "to_decimal":
                return self._to_decimal(value, max_digits, normalize)
            if operation == "to_fraction":
                return self._to_fraction(value, max_denominator, normalize)
            return self._compare(value, other, normalize)
        except ZeroDivisionError as exc:
            return self._error(mode, "arithmetic_error", str(exc))
        except (TypeError, ValueError, RecursionError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error(mode, "operation_error", f"Fraction operation failed: {exc}")

    # ------------------------------------------------------------------ modes

    def _parse(self, value: Any, normalize: bool) -> dict[str, Any]:
        parsed = self._parse_value(value, normalize)
        return {
            "status": "success",
            "ok": True,
            "mode": "parse",
            "value": value,
            "fraction": self._fraction_fields(parsed["fraction"]),
            "normalized": str(parsed["fraction"]),
            "form": parsed["form"],
            "issues": parsed["issues"],
        }

    def _compute(self, expression: Any) -> dict[str, Any]:
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("expression must be a non-empty string")
        if len(expression) > self.max_expression_length:
            raise ValueError(f"expression exceeds max_expression_length ({self.max_expression_length})")
        result, steps = _ExpressionParser(self, expression).parse()
        return {
            "status": "success",
            "ok": True,
            "mode": "compute",
            "expression": expression,
            "result": str(result),
            "result_fraction": self._fraction_fields(result),
            "decimal_preview": self._preview(result),
            "steps": steps,
            "operation_count": len(steps),
        }

    def _to_decimal(self, value: Any, max_digits: Any, normalize: bool) -> dict[str, Any]:
        parsed = self._parse_value(value, normalize)
        fraction = parsed["fraction"]
        limit = self._digit_limit(max_digits)
        expansion = self._expand(fraction.numerator, fraction.denominator, limit)
        reduced_denominator = fraction.denominator
        for factor in (2, 5):
            while reduced_denominator % factor == 0:
                reduced_denominator //= factor
        terminating = reduced_denominator == 1
        period: int | None = 0
        period_capped = False
        if not terminating:
            period = self._multiplicative_order(reduced_denominator)
            if period is None:
                period_capped = True
        if expansion["repetend"] is not None:
            # A closed remainder cycle is exact evidence of the period length.
            period = len(expansion["repetend"])
        return {
            "status": "success",
            "ok": True,
            "mode": "to_decimal",
            "value": value,
            "fraction": self._fraction_fields(fraction),
            "normalized": str(fraction),
            "decimal": expansion["decimal"],
            "terminating": terminating,
            "repetend": expansion["repetend"],
            "cycle_start": expansion["cycle_start"],
            "period_length": period,
            "period_capped": period_capped,
            "truncated": expansion["truncated"],
            "digits_emitted": expansion["digits_emitted"],
            "issues": parsed["issues"],
        }

    def _to_fraction(self, value: Any, max_denominator: Any, normalize: bool) -> dict[str, Any]:
        issues: list[str] = []
        if isinstance(value, bool):
            raise TypeError("value must be a string or number, not bool")
        if isinstance(value, int):
            return self._to_fraction_result(Fraction(value), "integer", True, None, issues)
        if isinstance(value, float):
            return self._to_fraction_float(value, max_denominator, issues)
        if not isinstance(value, str):
            raise TypeError("value must be a string, int, or float")
        if len(value) > self.max_input_length:
            raise ValueError(f"value exceeds max_input_length ({self.max_input_length})")
        text = value.strip()
        if not text:
            raise ValueError("value must be a non-empty string")
        match = _REPEATING_RE.match(text)
        if match and match.group(4) is not None:
            return self._to_fraction_result(self._repeating_value(match), "repeating_string", True, None, issues)
        parsed = self._parse_value(value, normalize)
        kind = "decimal_string" if parsed["form"] == "decimal" else "fraction_string"
        issues.extend(parsed["issues"])
        return self._to_fraction_result(parsed["fraction"], kind, True, None, issues)

    def _to_fraction_float(self, value: float, max_denominator: Any, issues: list[str]) -> dict[str, Any]:
        if not isfinite(value):
            raise ValueError("value must be a finite float (no inf or nan)")
        limit = self.max_denominator if max_denominator is None else max_denominator
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("max_denominator must be a positive integer")
        exact_binary = Fraction(value)
        result = exact_binary.limit_denominator(limit)
        error = abs(exact_binary - result)
        return self._to_fraction_result(result, "float", error == 0, error, issues)

    def _to_fraction_result(
        self, fraction: Fraction, kind: str, exact: bool, error: Fraction | None, issues: list[str]
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": "success",
            "ok": True,
            "mode": "to_fraction",
            "fraction": self._fraction_fields(fraction),
            "normalized": str(fraction),
            "input_kind": kind,
            "exact": exact,
            "issues": issues,
        }
        if error is not None:
            result["error_bound"] = self._fraction_fields(error)
        return result

    def _compare(self, value: Any, other: Any, normalize: bool) -> dict[str, Any]:
        left = self._parse_value(value, normalize)
        right = self._parse_value(other, normalize)
        outcome = (left["fraction"] > right["fraction"]) - (left["fraction"] < right["fraction"])
        return {
            "status": "success",
            "ok": True,
            "mode": "compare",
            "result": outcome,
            "relation": {1: "greater", 0: "equal", -1: "less"}[outcome],
            "a": {"normalized": str(left["fraction"]), "decimal_preview": self._preview(left["fraction"])},
            "b": {"normalized": str(right["fraction"]), "decimal_preview": self._preview(right["fraction"])},
        }

    # ---------------------------------------------------------------- parsing

    def _parse_value(self, value: Any, normalize: bool = False) -> dict[str, Any]:
        if not isinstance(value, str):
            raise TypeError("value must be a string (mode to_fraction also accepts float input)")
        text = value.strip()
        if not text:
            raise ValueError("value must be a non-empty string")
        if len(value) > self.max_input_length:
            raise ValueError(f"value exceeds max_input_length ({self.max_input_length})")
        issues: list[str] = []
        vulgar = self._vulgar(text)
        if vulgar is not None:
            return {"fraction": vulgar, "form": "vulgar", "issues": issues}
        if normalize:
            converted = unicodedata.normalize("NFKC", text)
            converted = "".join(str(unicodedata.decimal(ch, ch)) if ch.isdecimal() else ch for ch in converted)
            if converted != text:
                issues.append("value normalized via Unicode NFKC and decimal-digit folding")
            text = converted.strip()
        elif any(character.isdigit() and not character.isascii() for character in text):
            raise ValueError("value contains non-ASCII digits; retry with normalize=True")
        repeating = _REPEATING_RE.match(text)
        if repeating and repeating.group(4) is not None:
            return {"fraction": self._repeating_value(repeating), "form": "repeating", "issues": issues}
        matched = self._match_form(text, issues)
        if matched is not None:
            return matched
        raise ValueError(f"unrecognized fraction value: {value!r}")

    @staticmethod
    def _match_form(text: str, issues: list[str]) -> dict[str, Any] | None:
        """Match an ASCII text form: mixed number, slash fraction, or decimal."""
        mixed = _MIXED_RE.match(text)
        if mixed:
            return FractionTool._mixed(mixed, issues)
        plain = _FRACTION_RE.match(text)
        if plain:
            return FractionTool._plain_fraction(plain, issues)
        decimal = _DECIMAL_RE.match(text)
        if decimal and (decimal.group(2) or decimal.group(3)):
            fraction = Fraction(text)
            form = "integer" if decimal.group(3) is None and decimal.group(4) is None else "decimal"
            return {"fraction": fraction, "form": form, "issues": issues}
        return None

    @staticmethod
    def _vulgar(text: str) -> Fraction | None:
        match = _VULGAR_RE.match(text)
        if not match:
            return None
        numerator, denominator = _VULGAR_VALUES[match.group(2)]
        fraction = Fraction(numerator, denominator)
        return -fraction if match.group(1) == "-" else fraction

    @staticmethod
    def _mixed(match: re.Match, issues: list[str]) -> dict[str, Any]:
        whole_sign, whole, fraction_sign, numerator, denominator = match.groups()
        if int(denominator) == 0:
            raise ValueError("zero denominator in mixed number")
        if fraction_sign == "-":
            issues.append("negative sign on the fractional part of a mixed number is applied to the whole value")
        if whole_sign == "-" and fraction_sign == "-":
            issues.append("mixed number carries a sign on both parts; the signs are multiplied")
        if int(numerator) >= int(denominator):
            issues.append("fractional part of a mixed number is not proper")
        value = Fraction(int(whole), 1) + Fraction(int(numerator), int(denominator))
        negations = (whole_sign == "-") + (fraction_sign == "-")
        if negations % 2 == 1:
            value = -value
        return {"fraction": value, "form": "mixed", "issues": issues}

    @staticmethod
    def _plain_fraction(match: re.Match, issues: list[str]) -> dict[str, Any]:
        numerator_sign, numerator, denominator_sign, denominator = match.groups()
        if int(denominator) == 0:
            raise ValueError("zero denominator in fraction")
        if denominator_sign:
            issues.append("sign on the denominator normalized onto the numerator")
        value = Fraction(int(numerator), int(denominator))
        if (numerator_sign == "-") != (denominator_sign == "-"):
            value = -value
        form = "proper" if abs(value.numerator) < value.denominator else "improper"
        return {"fraction": value, "form": form, "issues": issues}

    @staticmethod
    def _repeating_value(match: re.Match) -> Fraction:
        sign, integer_part, nonrepeating, repetend = match.groups()
        if not (integer_part or nonrepeating):
            raise ValueError("repeating decimal needs an integer or fractional part before the repetend")
        prefix = nonrepeating or ""
        scaled = int(prefix + repetend) - int(prefix or "0")
        divisor = 10 ** (len(prefix) + len(repetend)) - 10 ** len(prefix)
        value = Fraction(int(integer_part or 0), 1) + Fraction(scaled, divisor)
        return -value if sign == "-" else value

    # ----------------------------------------------------------- decimal core

    def _expand(self, numerator: int, denominator: int, max_digits: int) -> dict[str, Any]:
        """Long division with remainder tracking; exact when a cycle closes.

        Truncated expansions end with an ellipsis character and set the
        truncated flag; repetends are parenthesized, e.g. '0.1(6)'.
        """
        sign = "-" if numerator < 0 else ""
        quotient, remainder = divmod(abs(numerator), denominator)
        digits: list[str] = []
        seen: dict[int, int] = {}
        index = 0
        while remainder and index < max_digits:
            if remainder in seen:
                start = seen[remainder]
                nonrepeating = "".join(digits[:start])
                repetend = "".join(digits[start:])
                return {
                    "decimal": self._join(sign, quotient, nonrepeating, repetend),
                    "repetend": repetend,
                    "cycle_start": start,
                    "truncated": False,
                    "digits_emitted": len(digits),
                }
            seen[remainder] = index
            remainder *= 10
            digit, remainder = divmod(remainder, denominator)
            digits.append(str(digit))
            index += 1
        fraction_digits = "".join(digits)
        truncated = remainder != 0
        decimal = self._join(sign, quotient, fraction_digits, None) + ("…" if truncated else "")
        return {
            "decimal": decimal,
            "repetend": None,
            # Terminating expansions never cycle, so the position after the last
            # digit is reported; a truncated expansion may hide a cycle that
            # starts anywhere, so no cycle_start claim is made (None).
            "cycle_start": None if truncated else len(digits),
            "truncated": truncated,
            "digits_emitted": len(digits),
        }

    @staticmethod
    def _join(sign: str, quotient: int, digits: str, repetend: str | None) -> str:
        whole = f"{sign}{quotient}"
        if repetend is not None:
            return f"{whole}.{digits}({repetend})"
        return whole if not digits else f"{whole}.{digits}"

    def _preview(self, fraction: Fraction) -> str:
        if fraction.denominator == 1:
            return str(fraction.numerator)
        return self._expand(fraction.numerator, fraction.denominator, _PREVIEW_DIGITS)["decimal"]

    def _multiplicative_order(self, denominator: int) -> int | None:
        """Multiplicative order of 10 modulo denominator (2s and 5s removed).

        The search is capped at max_period iterations; a denominator whose
        period exceeds the cap reports None via period_capped instead of
        searching unboundedly.
        """
        value = 10 % denominator
        order = 1
        while value != 1:
            if order >= self.max_period:
                return None
            value = value * 10 % denominator
            order += 1
        return order

    # ------------------------------------------------------------- validation

    @staticmethod
    def _fraction_fields(fraction: Fraction) -> dict[str, int]:
        return {"numerator": fraction.numerator, "denominator": fraction.denominator}

    def _mode(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in self._MODES:
            raise ValueError("mode must be parse, compute, to_decimal, to_fraction, or compare")
        return mode

    def _digit_limit(self, max_digits: Any) -> int:
        limit = self.max_digits if max_digits is None else max_digits
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("max_digits must be an integer")
        if limit < 1 or limit > self.max_digits_limit:
            raise ValueError(f"max_digits must be between 1 and {self.max_digits_limit}")
        return limit

    def _validate_config(self) -> None:
        for name in (
            "max_input_length",
            "max_expression_length",
            "max_operations",
            "max_parse_depth",
            "max_digits",
            "max_digits_limit",
            "max_period",
            "max_denominator",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_digits > self.max_digits_limit:
            raise ValueError("max_digits must not exceed max_digits_limit")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "ok": False, "mode": mode, "error_type": kind, "error": message}


class _ExpressionParser:
    """Recursive-descent evaluator: factor, then '*'/'/', then '+'/'-'.

    Operands are fraction literals ('3/4', '0.75', '1.5e-3', vulgar
    characters); unary signs and parentheses are supported. An unspaced
    'N/N' pair reads as a single fraction literal unless it sits inside an
    open division chain, where ordinary left-associative division applies —
    so '3.75 / 80/45' equals '(3.75 / 80) / 45' and '7 / -82/82' equals
    '((7 / -82) / 82)', matching standard precedence. Each binary operation
    appends one audit-trail step. No exponent operator.
    """

    def __init__(self, tool: FractionTool, expression: str) -> None:
        self.tool = tool
        self.expression = expression
        self.tokens = self._tokenize()
        self.position = 0
        self.depth = 0
        self.operations = 0
        self.steps: list[str] = []

    def _tokenize(self) -> list[str]:
        tokens: list[str] = []
        position = 0
        # True while an unspaced 'N/N' sits inside an open division chain: a
        # '/' operator with only unary signs or operands pending since. Then
        # gluing would swallow a division Python binds left-associatively
        # ('X / -82/82' is ((X / -82) / 82), never X / -(82/82)).
        inside_division_chain = False
        while position < len(self.expression):
            pattern = _TOKEN_NO_FRACTION_RE if inside_division_chain else _TOKEN_RE
            match = pattern.match(self.expression, position)
            if not match or not match.group("token"):
                rest = self.expression[position:].lstrip()
                if not rest:
                    break
                offset = len(self.expression) - len(rest)
                raise ValueError(f"invalid character {rest[0]!r} at position {offset} in expression")
            lexeme = match.group("token")
            tokens.append(lexeme)
            if lexeme == "/":
                inside_division_chain = True
            elif lexeme == "(" or lexeme not in ("+", "-"):
                inside_division_chain = False
            position = match.end()
        if not tokens:
            raise ValueError("expression contains no operands")
        return tokens

    def parse(self) -> tuple[Fraction, list[str]]:
        value = self._expression()
        if self.position != len(self.tokens):
            raise ValueError(f"unexpected token {self.tokens[self.position]!r} in expression")
        return value, self.steps

    def _expression(self) -> Fraction:
        value = self._term()
        while self.position < len(self.tokens) and self.tokens[self.position] in ("+", "-"):
            operator = self.tokens[self.position]
            self.position += 1
            value = self._apply(value, operator, self._term())
        return value

    def _term(self) -> Fraction:
        value = self._factor()
        while self.position < len(self.tokens) and self.tokens[self.position] in ("*", "/"):
            operator = self.tokens[self.position]
            self.position += 1
            value = self._apply(value, operator, self._factor())
        return value

    def _factor(self) -> Fraction:
        self.depth += 1
        try:
            if self.depth > self.tool.max_parse_depth:
                raise ValueError(f"expression nested deeper than max_parse_depth ({self.tool.max_parse_depth})")
            if self.position >= len(self.tokens):
                raise ValueError("expression ends where an operand was expected")
            lexeme = self.tokens[self.position]
            if lexeme == "-":
                self.position += 1
                return -self._factor()
            if lexeme == "+":
                self.position += 1
                return self._factor()
            if lexeme == "(":
                self.position += 1
                value = self._expression()
                if self.position >= len(self.tokens) or self.tokens[self.position] != ")":
                    raise ValueError("missing closing parenthesis in expression")
                self.position += 1
                return value
            if lexeme in ("*", "/", ")"):
                raise ValueError(f"unexpected token {lexeme!r} where an operand was expected")
            self.position += 1
            return self._literal(lexeme)
        finally:
            self.depth -= 1

    @staticmethod
    def _literal(lexeme: str) -> Fraction:
        if "/" in lexeme:
            if lexeme.split("/")[1] == "0":
                raise ZeroDivisionError(f"fraction literal with zero denominator: {lexeme!r}")
            return Fraction(lexeme)
        if lexeme in _VULGAR_VALUES:
            numerator, denominator = _VULGAR_VALUES[lexeme]
            return Fraction(numerator, denominator)
        return Fraction(lexeme)

    def _apply(self, left: Fraction, operator: str, right: Fraction) -> Fraction:
        if self.operations >= self.tool.max_operations:
            raise ValueError(f"expression exceeds max_operations ({self.tool.max_operations})")
        if operator == "+":
            result = left + right
        elif operator == "-":
            result = left - right
        elif operator == "*":
            result = left * right
        else:
            if right == 0:
                raise ZeroDivisionError(f"division by zero in step {self.operations + 1}: {left} / 0")
            result = left / right
        self.operations += 1
        self.steps.append(f"{left} {operator} {right} = {result}")
        return result


__all__ = ["FractionTool"]
