#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: basen_encode_tool.py

"""Arbitrary-base integer encoding tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency radix conversion
utility agents can call when plumbing identifiers, hashes or protocol
fields between numeral systems.

This tool is about INTEGER RADIX CONVERSION — rendering one integer in
positional notations from base 2 to base 36 — and is deliberately
distinct from ``TextCodecTool``'s ``base64`` mode, which encodes UTF-8
TEXT into the Base64 binary-to-text transport format. Four modes:

* ``encode`` — render a non-negative integer (given as an ``int`` or a
  decimal digit string) as digits in any base 2-36. An optional
  ``alphabet`` replaces the default ``0-9a-z`` digit characters (its
  length must equal the base and its characters must be unique), and an
  optional ``prefix`` (e.g. ``0x`` / ``0b``) is prepended verbatim.
* ``decode`` — parse digit characters in a given base back to the
  Python integer they represent, with Python's arbitrary-precision
  ``int(s, base)`` semantics implemented as a direct Horner
  accumulation (so inputs up to the documented magnitude cap never hit
  CPython's default 4300-digit conversion limit) and only after strict
  validation: every character must be a digit of the base (for the
  default alphabet upper and lower case are both accepted; a custom
  alphabet is matched exactly), a single leading ``+`` / ``-`` sign is
  allowed, and the first invalid character is reported with its
  position. A ``prefix`` given here must be present on the input and
  is stripped before parsing, so prefixed encodings round-trip.
* ``convert`` — parse ``value`` in ``from_base`` and render it in
  ``to_base`` directly (standard alphabet, sign allowed on input).
* ``info`` — report which of the bases 2-36 the string is a valid
  numeral in, plus its smallest valid base.

Parameter validation is strict and happens before any computation:
malformed parameters (wrong types, empty value, base outside 2-36,
inconsistent / duplicated / whitespace alphabets, non-printable
prefixes, parameters not used by the requested mode) raise a
``ValueError``, mirroring the other common tools. Errors that depend
on the *content being processed* — a non-decimal encode value, an
invalid digit (with its position), a negative value passed to
``encode``, a missing or mismatched prefix, a value with no digits
after its sign, and results whose magnitude exceeds ``10**10000`` —
are returned as a structured ``error`` payload so an agent can react
without catching exceptions.

Big integers are supported natively (Python integers are unbounded);
the documented magnitude cap of ``10**10000`` inclusive keeps decode
work deterministic and bounded.
"""

from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_DEFAULT_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
# Value of every standard digit character, upper and lower case.
_DIGIT_VALUE: Dict[str, int] = {}
for _index, _char in enumerate(_DEFAULT_ALPHABET):
    _DIGIT_VALUE[_char] = _index
    _DIGIT_VALUE[_char.upper()] = _index


class BaseNEncodeTool(Tool):
    """Arbitrary-base integer encoding tool built purely on the stdlib.

    Attributes:
        max_value_chars (int): Upper bound on the ``value`` string
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "basen_encode_tool"
    description: str = (
        "Base-N integer encoding tool — pure Python stdlib, no network "
        "required. Encode a non-negative integer into any base 2-36 "
        "with an optional custom alphabet and prefix such as 0x/0b "
        "(mode='encode'), strictly validated decode of digits in a "
        "given base back to an arbitrary-precision integer, with the "
        "position of the first invalid character (mode='decode'), "
        "direct base-to-base conversion (mode='convert', from_base + "
        "to_base), and validity info listing which bases 2-36 a string "
        "is a valid numeral in (mode='info')."
    )

    MODES: ClassVar[tuple] = ("encode", "decode", "convert", "info")
    MIN_BASE: ClassVar[int] = 2
    MAX_BASE: ClassVar[int] = 36
    # Documented magnitude cap (inclusive) for encoded/decoded values.
    MAX_MAGNITUDE: ClassVar[int] = 10**10000

    max_value_chars: int = 100_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        value: Any = None,
        base: Any = None,
        from_base: Any = None,
        to_base: Any = None,
        alphabet: Any = None,
        prefix: Any = None,
    ) -> Dict[str, Any]:
        """Run one radix operation.

        Args:
            mode (str): One of ``encode`` / ``decode`` / ``convert`` /
                ``info``.
            value (int | str): The value to process. ``encode`` accepts
                a non-negative ``int`` or a decimal digit string
                (an optional single leading ``+`` is tolerated, ``-``
                values are reported as a negative_value error payload);
                ``decode`` / ``convert`` accept digit characters in the
                source base with an optional single leading sign;
                ``info`` accepts any non-empty string.
            base (int | str): Target base for ``encode`` and source
                base for ``decode`` — an integer 2-36 (or its decimal
                string form). Defaults to 10 for ``encode`` and is
                required for ``decode``; not accepted by ``convert``
                (use ``from_base`` / ``to_base``) or ``info``.
            from_base (int | str): Source base 2-36 for ``convert``.
            to_base (int | str): Target base 2-36 for ``convert``.
            alphabet (str): Optional custom digit characters replacing
                the default ``0-9a-z``. Its length must equal the base
                and its characters must be unique and whitespace-free;
                decoding with a custom alphabet is case-sensitive.
                ``encode`` / ``decode`` only.
            prefix (str): Optional non-empty prefix of printable ASCII
                characters (e.g. ``0x``, ``0b``) prepended by
                ``encode``; when given to ``decode`` the input must
                start with it and it is stripped before parsing.
                ``encode`` / ``decode`` only.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                key plus the call context) or a structured ``error``
                payload for content-level failures (invalid digits,
                invalid encode values, negative values, missing or
                mismatched prefixes, missing digits, oversized
                magnitudes).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "info":
            for label, param in (
                ("base", base),
                ("from_base", from_base),
                ("to_base", to_base),
                ("alphabet", alphabet),
                ("prefix", prefix),
            ):
                if param is not None:
                    self._invalid(
                        f"{label} is not accepted in info mode — info only "
                        "inspects the value against the standard bases 2-36"
                    )
            clean_value = self._validate_value_string(value)
            return self._run_info(clean_value)
        if mode == "convert":
            return self._run_convert(value, base, from_base, to_base, alphabet, prefix)

        clean_base = self._validate_base(
            base, required=(mode == "decode"), default=10, label="base"
        )
        clean_alphabet = self._validate_alphabet(alphabet, clean_base)
        clean_prefix = self._validate_prefix(prefix)
        if mode == "encode":
            return self._run_encode(value, clean_base, clean_alphabet, clean_prefix)
        return self._run_decode(value, clean_base, clean_alphabet, clean_prefix)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"basen_encode_tool: {message}")

    @classmethod
    def _validate_base(
        cls, base: Any, required: bool, default: Any, label: str
    ) -> int:
        """Validate a base parameter into an int in [2, 36]."""
        if base is None:
            if required:
                cls._invalid(f"{label} is required for this mode (got None)")
            return default
        if isinstance(base, bool) or not isinstance(base, (int, str)):
            cls._invalid(f"{label} must be an integer from 2 to 36 (got {base!r})")
        if isinstance(base, str):
            if not base.isascii() or not base.isdigit():
                cls._invalid(
                    f"{label} given as a string must be plain decimal digits "
                    f"without sign or whitespace (got {base!r})"
                )
            base = int(base)
        if not cls.MIN_BASE <= base <= cls.MAX_BASE:
            cls._invalid(
                f"{label} must be an integer from {cls.MIN_BASE} to "
                f"{cls.MAX_BASE} (got {base})"
            )
        return base

    @classmethod
    def _validate_alphabet(cls, alphabet: Any, base: int) -> Optional[str]:
        """Validate the optional custom digit alphabet."""
        if alphabet is None:
            return None
        if isinstance(alphabet, bool) or not isinstance(alphabet, str):
            cls._invalid(
                f"alphabet must be a string of {base} unique characters (got {alphabet!r})"
            )
        if len(alphabet) != base:
            cls._invalid(
                f"alphabet length must equal the base ({base}) but got "
                f"{len(alphabet)} characters (got {alphabet!r})"
            )
        if any(char.isspace() for char in alphabet):
            cls._invalid(f"alphabet must not contain whitespace (got {alphabet!r})")
        if len(set(alphabet)) != len(alphabet):
            cls._invalid(f"alphabet characters must be unique (got {alphabet!r})")
        return alphabet

    @classmethod
    def _validate_prefix(cls, prefix: Any) -> str:
        """Validate the optional result prefix (e.g. 0x / 0b)."""
        if prefix is None:
            return ""
        if isinstance(prefix, bool) or not isinstance(prefix, str):
            cls._invalid(f"prefix must be a non-empty string or None (got {prefix!r})")
        if not prefix:
            cls._invalid("prefix must be a non-empty string or None (got '')")
        for char in prefix:
            code = ord(char)
            if code < 0x21 or code > 0x7E:
                cls._invalid(
                    "prefix must only contain printable ASCII characters "
                    f"without whitespace (got {prefix!r})"
                )
        return prefix

    @classmethod
    def _validate_value_string(cls, value: Any) -> str:
        """Validate that ``value`` is a usable non-empty string."""
        if value is None or isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"value must be a non-empty string (got {value!r})")
        if not value:
            cls._invalid("value must be a non-empty string (got '')")
        if len(value) > 100_000:
            cls._invalid(
                f"value exceeds the {100_000:,}-character limit "
                f"(got {len(value):,} characters)"
            )
        return value

    # ------------------------------------------------------------------ #
    # Shared digit scanning helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _first_invalid_standard(
        cls, digits: str, base: int, offset: int
    ) -> Optional[int]:
        """Return the original-string index of the first char that is
        not a digit of ``base`` under the standard (case-insensitive)
        alphabet, or ``None`` when every character is valid."""
        for position, char in enumerate(digits):
            digit = _DIGIT_VALUE.get(char)
            if digit is None or digit >= base:
                return offset + position
        return None

    @staticmethod
    def _render(value: int, base: int, alphabet: str) -> str:
        """Render a non-negative integer as digits of the alphabet."""
        if value == 0:
            return alphabet[0]
        chars: List[str] = []
        remaining = value
        while remaining:
            remaining, digit = divmod(remaining, base)
            chars.append(alphabet[digit])
        chars.reverse()
        return "".join(chars)

    # ------------------------------------------------------------------ #
    # encode mode
    # ------------------------------------------------------------------ #

    def _run_encode(
        self, value: Any, base: int, alphabet: Optional[str], prefix: str
    ) -> Dict[str, Any]:
        """Render a non-negative integer as digits in the target base."""
        context: Dict[str, Any] = {"mode": "encode", "base": base}
        if prefix:
            context["prefix"] = prefix
        if isinstance(value, bool) or not isinstance(value, (int, str)):
            self._invalid(
                "value must be a non-negative integer or a decimal digit "
                f"string (got {value!r})"
            )

        number: int
        if isinstance(value, int):
            if value < 0:
                return self._error_result(
                    context,
                    error_type="negative_value",
                    message=(
                        "encode only accepts non-negative integers; decode "
                        "and convert accept a leading '-' sign instead"
                    ),
                )
            number = value
        else:
            if not value:
                self._invalid("value must be a non-empty string (got '')")
            if len(value) > 100_000:
                self._invalid(
                    f"value exceeds the {100_000:,}-character limit "
                    f"(got {len(value):,} characters)"
                )
            body = value
            sign = body[:1]
            if sign in ("+", "-"):
                body = body[1:]
            offset = len(value) - len(body)
            if not body:
                return self._error_result(
                    context,
                    error_type="missing_digits",
                    message="value has a sign but no digits after it",
                )
            if sign == "-":
                return self._error_result(
                    context,
                    error_type="negative_value",
                    message=(
                        "encode only accepts non-negative integers; decode "
                        "and convert accept a leading '-' sign instead"
                    ),
                )
            bad = self._first_invalid_standard(body, 10, offset=offset)
            if bad is not None:
                return self._error_result(
                    context,
                    error_type="invalid_value",
                    message=(
                        "encode value must be a non-negative integer or a "
                        "decimal digit string (0-9, no underscores, no "
                        f"whitespace); first invalid character {value[bad]!r} "
                        f"at position {bad} (got {value[:64]!r})"
                    ),
                )
            # Horner accumulation keeps values of up to the documented
            # 10**10000 cap parseable under CPython's int-str limit.
            number = 0
            for char in body:
                number = number * 10 + _DIGIT_VALUE[char]

        if number > self.MAX_MAGNITUDE:
            return self._error_result(
                context,
                error_type="value_too_large",
                message=(
                    "value magnitude exceeds the documented cap of "
                    "10**10000 inclusive; big integers are supported natively "
                    "up to that bound"
                ),
            )
        digits = self._render(number, base, alphabet or _DEFAULT_ALPHABET)
        return {
            **context,
            "result": prefix + digits,
            "digit_count": len(digits),
        }

    # ------------------------------------------------------------------ #
    # decode mode
    # ------------------------------------------------------------------ #

    def _run_decode(
        self, value: Any, base: int, alphabet: Optional[str], prefix: str
    ) -> Dict[str, Any]:
        """Strictly parse digits in the given base back to an integer."""
        clean_value = self._validate_value_string(value)
        context: Dict[str, Any] = {"mode": "decode", "base": base}
        if prefix:
            context["prefix"] = prefix

        body = clean_value
        if prefix:
            if not body.startswith(prefix):
                return self._error_result(
                    context,
                    error_type="prefix_mismatch",
                    message=(
                        f"decode input must start with the given prefix "
                        f"{prefix!r} (got {clean_value[:64]!r})"
                    ),
                )
            body = body[len(prefix):]

        sign = ""
        if body[:1] in ("+", "-"):
            sign = body[0]
            body = body[1:]
        if not body:
            return self._error_result(
                context,
                error_type="missing_digits",
                message="value has no digits to decode",
            )

        offset = len(clean_value) - len(body)
        digit_value = (
            _DIGIT_VALUE
            if alphabet is None
            else {char: pos for pos, char in enumerate(alphabet)}
        )
        for position, char in enumerate(body):
            if char not in digit_value or (
                alphabet is None and digit_value[char] >= base
            ):
                return self._invalid_digit_error(
                    context, clean_value, offset + position, base
                )
        # Horner accumulation keeps values of up to the documented
        # 10**10000 cap parseable under CPython's int-str limit.
        number = 0
        for char in body:
            number = number * base + digit_value[char]
        if sign == "-":
            number = -number

        if abs(number) > self.MAX_MAGNITUDE:
            return self._error_result(
                context,
                error_type="value_too_large",
                message=(
                    "decoded magnitude exceeds the documented cap of "
                    "10**10000 inclusive; big integers are supported natively "
                    "up to that bound"
                ),
            )
        return {
            **context,
            "result": number,
            "digit_count": len(body),
            "negative": number < 0,
        }

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def _run_convert(
        self,
        value: Any,
        base: Any,
        from_base: Any,
        to_base: Any,
        alphabet: Any,
        prefix: Any,
    ) -> Dict[str, Any]:
        """Parse ``value`` in ``from_base`` and render it in ``to_base``."""
        if base is not None:
            self._invalid(
                "base is not accepted in convert mode — convert uses "
                "from_base and to_base instead"
            )
        if alphabet is not None:
            self._invalid(
                "alphabet is not accepted in convert mode — custom alphabets "
                "are only supported by the encode/decode modes; convert the "
                "value with decode() first if you need them"
            )
        if prefix is not None:
            self._invalid(
                "prefix is not accepted in convert mode — prefixes are only "
                "supported by the encode/decode modes; add or strip them "
                "around the convert call instead"
            )
        clean_from = self._validate_base(
            from_base, required=True, default=None, label="from_base"
        )
        clean_to = self._validate_base(
            to_base, required=True, default=None, label="to_base"
        )
        parsed = self._run_decode(value, clean_from, alphabet=None, prefix="")
        if "error" in parsed:
            return {
                "mode": "convert",
                "from_base": clean_from,
                "to_base": clean_to,
                "error": parsed["error"],
            }
        number = parsed["result"]
        negative = number < 0
        digits = self._render(abs(number), clean_to, _DEFAULT_ALPHABET)
        return {
            "mode": "convert",
            "from_base": clean_from,
            "to_base": clean_to,
            "value": number,
            "result": ("-" if negative else "") + digits,
            "digit_count": len(digits),
        }

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def _run_info(self, value: str) -> Dict[str, Any]:
        """Report which bases 2-36 the string is a valid numeral in."""
        sign = None
        body = value
        if body[:1] in ("+", "-"):
            sign = body[0]
            body = body[1:]
        max_digit = -1
        for char in body:
            digit = _DIGIT_VALUE.get(char)
            if digit is None:
                max_digit = None
                break
            if digit > max_digit:
                max_digit = digit
        if max_digit is None:
            valid_bases: List[int] = []
            min_base = None
        else:
            valid_bases = list(range(max(self.MIN_BASE, max_digit + 1), self.MAX_BASE + 1))
            min_base = valid_bases[0] if valid_bases else None
        return {
            "mode": "info",
            "value": value,
            "sign": sign,
            "digit_count": len(body),
            "valid_bases": valid_bases,
            "valid_base_count": len(valid_bases),
            "min_base": min_base,
        }

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

    def _invalid_digit_error(
        self, context: Dict[str, Any], value: str, position: int, base: int
    ) -> Dict[str, Any]:
        """Build the structured invalid-digit error payload."""
        return self._error_result(
            context,
            error_type="invalid_digit",
            message=(
                f"character {value[position]!r} at position {position} is not "
                f"a digit of base {base} (got {value[:64]!r})"
            ),
        )
