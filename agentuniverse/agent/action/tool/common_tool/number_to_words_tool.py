#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: number_to_words_tool.py

"""Number / words conversion tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency converter agents can
call whenever a number must be spoken, rendered or matched as natural
language — and whenever number words coming back from a model or a user
must be turned into an exact number again.

The tool supports two modes and two languages:

* ``number_to_words`` — render a number as English or Chinese words.
  English uses the American short scale (``thousand`` / ``million`` /
  ``billion``), hyphenated compounds (``forty-two``) and no ``and``
  (``1234`` → ``one thousand two hundred thirty-four``). Chinese uses
  the standard 万 / 亿 grouping with canonical 零 insertion
  (``1234`` → ``一千二百三十四``, ``10001`` → ``一万零一``).
  Negatives are ``minus`` / ``negative`` (EN) and ``负`` (ZH);
  decimals read the fractional digits one by one after ``point`` /
  ``点`` (``3.14`` → ``three point one four`` / ``三点一四``).
* ``words_to_number`` — parse words back into a number with a strict
  grammar. The English parser accepts exactly the forms described
  above plus the common variants (space or hyphen compounds, ``minus``
  or ``negative``); the Chinese parser accepts the canonical forms
  plus ``〇`` for ``零`` and ``两`` for ``两``-position ``二``.
  Anything ambiguous — bare digit sequences such as ``一二三``,
  truncated forms such as ``一万二`` (twelve hundred style shortcuts),
  unknown words, repeated scale words, dangling ``point`` — is
  rejected with a structured ``error`` payload instead of guessing.

Both directions round-trip exactly for every value in range:
``words_to_number(number_to_words(n)) == n``.

Range: the integer part is limited to 12 digits (absolute value at
most ``999,999,999,999`` — English ``nine hundred ninety-nine billion
…``, Chinese ``九千九百九十九亿…``); the fractional part is limited
to 12 digits. ``words_to_number`` returns an ``int`` for integers and
an exact decimal string (e.g. ``"3.14"``) for fractional values, so
no binary-float rounding ever enters the result.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode or language, a number
that is neither an ``int`` nor a digit string, leading zeros, ``+``
signs, thousands separators, a second decimal point, an empty or
oversized words string) raise a ``ValueError``, mirroring the other
common tools. Errors that depend on the *content being parsed* — an
unparseable words string or a words value outside the supported
range — are returned as a structured ``error`` payload so an agent
can react without catching exceptions.
"""

import re
from typing import Any, ClassVar, Dict, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Canonical numeric-string: "-123", "0", "3.14" (no leading zeros, no "+").
_NUMBER_RE = re.compile(r"\A-?(?:0|[1-9][0-9]*)(?:\.([0-9]+))?\Z")

# --------------------------------------------------------------------- #
# English word tables (short scale)
# --------------------------------------------------------------------- #
_EN_UNITS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9,
}
_EN_TEENS = {
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19,
}
_EN_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
_EN_SCALES = {"thousand": 3, "million": 6, "billion": 9}
_EN_DIGIT_WORDS = {**_EN_UNITS, "zero": 0}
_EN_SMALL = (
    "zero", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
    "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
)
_EN_TENS_WORDS = (
    "", "", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety",
)

# --------------------------------------------------------------------- #
# Chinese character tables
# --------------------------------------------------------------------- #
_ZH_CHARS = "零一二三四五六七八九"
_ZH_DIGITS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}
_ZH_UNITS = {"十": 10, "百": 100, "千": 1000}
_ZH_DECIMAL_DIGITS = set("零〇一二三四五六七八九")

_MAX_ABS = 999_999_999_999  # 12-digit integer-part bound


class NumberToWordsTool(Tool):
    """Number / words conversion tool (EN + ZH), pure Python stdlib.

    Attributes:
        max_words_chars (int): Upper bound on the ``words`` input
            length; longer inputs are rejected before any work.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "number_to_words_tool"
    description: str = (
        "Number-to-words tool — pure Python stdlib, no network "
        "required. Renders a number as English words (American short "
        "scale, hyphenated compounds, no 'and') or Chinese words "
        "(standard 万/亿 grouping with canonical 零 insertion), and "
        "parses such words back into an exact number. Integers up to "
        "999,999,999,999 and fractional parts up to 12 digits; "
        "negatives via minus/negative/负; decimals read digit by "
        "digit after point/点. Both directions round-trip exactly."
    )

    MODES: ClassVar[tuple] = ("number_to_words", "words_to_number")
    LANGS: ClassVar[tuple] = ("en", "zh")

    max_words_chars: int = 10_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        number: Any = None,
        words: Any = None,
        lang: Any = None,
    ) -> Dict[str, Any]:
        """Run one number/words conversion.

        Args:
            mode (str): ``number_to_words`` or ``words_to_number``.
            number (int | str): The number to render — an ``int`` or a
                digit string such as ``"1234"``, ``"-42"`` or
                ``"3.14"`` (no thousands separators, no ``+``, no
                leading zeros). Required for ``number_to_words``.
            words (str): The words to parse, e.g. ``"one thousand two
                hundred thirty-four"`` or ``"一千二百三十四"``.
                Required for ``words_to_number``.
            lang (str): ``en`` (default) or ``zh``.

        Returns:
            Dict[str, Any]: The conversion result (always a ``result``
                key plus the call context) or a structured ``error``
                payload for content-level failures (unparseable words,
                words value outside the supported range).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_lang = self._validate_lang(lang)
        if mode == "number_to_words":
            sign, int_part, frac_part = self._validate_number(number)
            return {
                "mode": "number_to_words",
                "lang": clean_lang,
                "number": self._canonical(sign, int_part, frac_part),
                "result": self._number_to_words(
                    sign, int_part, frac_part, clean_lang
                ),
            }
        clean_words = self._validate_words(words)
        return self._words_to_number(clean_words, clean_lang)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"number_to_words_tool: {message}")

    @classmethod
    def _validate_lang(cls, lang: Any) -> str:
        """Validate the ``lang`` selector (``None`` means English)."""
        if lang is None:
            return "en"
        if isinstance(lang, bool) or not isinstance(lang, str):
            cls._invalid(f"lang must be one of: {', '.join(cls.LANGS)} (got {lang!r})")
        if lang not in cls.LANGS:
            cls._invalid(
                f"lang must be one of: {', '.join(cls.LANGS)} (got {lang!r})"
            )
        return lang

    @classmethod
    def _validate_number(cls, number: Any) -> Tuple[int, str, str]:
        """Validate the ``number`` input; return ``(sign, int, frac)``.

        ``sign`` is ``1`` or ``-1``; ``int_part`` has no leading zeros;
        ``frac_part`` is ``""`` for integers.
        """
        if number is None or isinstance(number, bool):
            cls._invalid(
                f"number must be an int or a digit string (got {number!r})"
            )
        if isinstance(number, int):
            raw = str(abs(number))
            candidate = ("-" if number < 0 else "") + raw
        elif isinstance(number, float):
            cls._invalid(
                "number must be an int or a digit string, not a float "
                f"(got {number!r}) — pass an exact decimal string such "
                "as '3.14' to avoid binary-float rounding"
            )
        elif isinstance(number, str):
            candidate = number.strip()
        else:
            cls._invalid(
                f"number must be an int or a digit string (got {number!r})"
            )
        match = _NUMBER_RE.match(candidate)
        if match is None:
            cls._invalid(
                "number must be an optionally negative integer or "
                "decimal digit string without separators, '+' signs or "
                f"leading zeros (got {number!r})"
            )
        negative = candidate.startswith("-")
        unsigned = candidate[1:] if negative else candidate
        int_part, _, frac_part = unsigned.partition(".")
        if len(int_part) > 12:
            cls._invalid(
                "number's integer part exceeds the 12-digit limit "
                f"(got {len(int_part)} digits; the maximum absolute "
                "value is 999,999,999,999)"
            )
        if len(frac_part) > 12:
            cls._invalid(
                "number's fractional part exceeds the 12-digit limit "
                f"(got {len(frac_part)} digits)"
            )
        if negative and set(unsigned) <= {"0", "."}:
            cls._invalid(
                f"negative zero is not a valid number (got {number!r})"
            )
        return (-1 if negative else 1), int_part, frac_part

    @classmethod
    def _validate_words(cls, words: Any) -> str:
        """Validate the ``words`` input (type, emptiness, length)."""
        if words is None or isinstance(words, bool) or not isinstance(words, str):
            cls._invalid(f"words must be a non-empty string (got {words!r})")
        clean = words.strip()
        if not clean:
            cls._invalid("words must be a non-empty string (got '')")
        if len(clean) > 10_000:
            cls._invalid(
                f"words exceeds the {10_000:,}-character limit "
                f"(got {len(clean):,} characters)"
            )
        return clean

    @staticmethod
    def _canonical(sign: int, int_part: str, frac_part: str) -> str:
        """Build the canonical numeric string from validated parts."""
        text = f"-{int_part}" if sign < 0 else int_part
        if frac_part:
            text += f".{frac_part}"
        return text

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

    # ------------------------------------------------------------------ #
    # number → words
    # ------------------------------------------------------------------ #

    def _number_to_words(
        self, sign: int, int_part: str, frac_part: str, lang: str
    ) -> str:
        """Render validated number parts as words in the given language."""
        if lang == "zh":
            words = self._zh_integer(int(int_part))
            if frac_part:
                words += "点" + "".join(_ZH_CHARS[int(d)] for d in frac_part)
            prefix = "负" if sign < 0 else ""
        else:
            words = self._en_integer(int(int_part))
            if frac_part:
                words += " point " + " ".join(_EN_SMALL[int(d)] for d in frac_part)
            prefix = "minus " if sign < 0 else ""
        return prefix + words

    @staticmethod
    def _en_under_1000(value: int) -> str:
        """Words for ``1 <= value <= 999``."""
        hundreds, rest = divmod(value, 100)
        parts = []
        if hundreds:
            parts.append(f"{_EN_SMALL[hundreds]} hundred")
        if rest:
            if rest < 20:
                parts.append(_EN_SMALL[rest])
            else:
                tens, unit = divmod(rest, 10)
                word = _EN_TENS_WORDS[tens]
                if unit:
                    word += f"-{_EN_SMALL[unit]}"
                parts.append(word)
        return " ".join(parts)

    @classmethod
    def _en_integer(cls, value: int) -> str:
        """Words for ``0 <= value <= 999,999,999,999`` (short scale)."""
        if value == 0:
            return "zero"
        groups = [
            (value // 10**9 % 1000, "billion"),
            (value // 10**6 % 1000, "million"),
            (value // 10**3 % 1000, "thousand"),
            (value % 1000, ""),
        ]
        parts = []
        for group_value, scale in groups:
            if group_value == 0:
                continue
            words = cls._en_under_1000(group_value)
            parts.append(f"{words} {scale}".strip())
        return " ".join(parts)

    @staticmethod
    def _zh_group(value: int) -> str:
        """Characters for ``1 <= value <= 9999`` (one 万 group)."""
        units = ("", "十", "百", "千")
        chars = []
        emitted = False
        pending_zero = False
        for position in (3, 2, 1, 0):
            digit = value // 10 ** position % 10
            if digit == 0:
                if emitted:
                    pending_zero = True
                continue
            if pending_zero:
                chars.append("零")
                pending_zero = False
            chars.append(_ZH_CHARS[digit] + units[position])
            emitted = True
        return "".join(chars)

    @classmethod
    def _zh_integer(cls, value: int) -> str:
        """Characters for ``0 <= value <= 999,999,999,999``."""
        if value == 0:
            return "零"
        groups = [
            (value // 10**8 % 10000, "亿"),
            (value // 10**4 % 10000, "万"),
            (value % 10000, ""),
        ]
        parts = []
        started = False
        for group_value, unit in groups:
            if group_value == 0:
                continue
            # A lower group below 1000 has no 千 digit — join with 零.
            if started and group_value < 1000:
                parts.append("零")
            parts.append(cls._zh_group(group_value) + unit)
            started = True
        text = "".join(parts)
        # 一十 at the very start of the number is written 十.
        if text.startswith("一十"):
            text = text[1:]
        return text

    # ------------------------------------------------------------------ #
    # words → number
    # ------------------------------------------------------------------ #

    def _words_to_number(self, words: str, lang: str) -> Dict[str, Any]:
        """Parse validated words into a number."""
        context: Dict[str, Any] = {"mode": "words_to_number", "lang": lang}
        if lang == "zh":
            parsed = self._parse_zh(words)
        else:
            parsed = self._parse_en(words)
        if isinstance(parsed, str):
            return self._error_result(
                context, error_type="invalid_words", message=parsed
            )
        sign, int_part, frac_part = parsed
        if len(int_part.lstrip("0") or "0") > 12:
            return self._error_result(
                context,
                error_type="out_of_range",
                message=(
                    "the parsed words describe a number whose integer "
                    "part exceeds the 12-digit limit (the maximum "
                    "absolute value is 999,999,999,999)"
                ),
            )
        if frac_part:
            result: Any = self._canonical(sign, int_part.lstrip("0") or "0", frac_part)
        else:
            value = int(int_part or "0")
            result = -value if sign < 0 else value
        return {**context, "result": result}

    # ------------------------------ English -------------------------- #

    @classmethod
    def _parse_en(cls, words: str) -> Any:
        """Parse English words; return ``(sign, int, frac)`` or an
        error-message string."""
        tokens = re.sub(r"[-,]", " ", words.lower()).split()
        if not tokens:
            return "the words string contains no words to parse"

        index = 0
        sign = 1
        if tokens[0] in ("minus", "negative"):
            sign = -1
            index = 1
            if index == len(tokens):
                return "a bare 'minus'/'negative' sign without a number"

        # ---- integer part ------------------------------------------------
        if index < len(tokens) and tokens[index] == "point":
            return "'point' must follow an integer part (e.g. 'zero point five')"

        scale_exponent = None  # exponent of the last scale word seen
        total = 0
        zero_only = False
        while index < len(tokens) and tokens[index] != "point":
            if tokens[index] == "zero":
                # "zero" is only valid as the entire integer part.
                if total != 0 or (
                    index + 1 < len(tokens) and tokens[index + 1] != "point"
                ):
                    return (
                        "'zero' cannot be combined with other integer "
                        f"words (near {words[:64]!r})"
                    )
                zero_only = True
                index += 1
                continue
            if zero_only:
                return (
                    "'zero' cannot be combined with other integer words "
                    f"(near {words[:64]!r})"
                )
            group_value, index, error = cls._read_en_group(tokens, index)
            if error:
                return error
            if group_value == 0:
                return (
                    "a scale word must be preceded by a number between "
                    f"one and nine hundred ninety-nine (near {words[:64]!r})"
                )
            if index >= len(tokens) or tokens[index] != "point":
                if index < len(tokens) and tokens[index] in _EN_SCALES:
                    exponent = _EN_SCALES[tokens[index]]
                    if scale_exponent is not None and exponent >= scale_exponent:
                        return (
                            "scale words must appear at most once each "
                            "and in descending order (thousand after "
                            f"million, not before) — got {tokens[index]!r} "
                            f"again or out of order (near {words[:64]!r})"
                        )
                    scale_exponent = exponent
                    total += group_value * 10 ** exponent
                    index += 1
                else:
                    if scale_exponent is not None and scale_exponent <= 0:
                        return (
                            "two unit-level groups without a scale word "
                            f"between them (near {words[:64]!r})"
                        )
                    scale_exponent = 0
                    total += group_value
            else:
                if scale_exponent is not None and scale_exponent <= 0:
                    return (
                        "two unit-level groups without a scale word "
                        f"between them (near {words[:64]!r})"
                    )
                scale_exponent = 0
                total += group_value
        integer = 0 if zero_only else total

        # ---- fractional part ---------------------------------------------
        digits = ""
        if index < len(tokens):
            # tokens[index] == "point"
            index += 1
            if index == len(tokens):
                return "'point' must be followed by at least one digit word"
            while index < len(tokens):
                token = tokens[index]
                if token not in _EN_DIGIT_WORDS:
                    return (
                        f"unexpected word {token!r} after 'point' — only "
                        "zero..nine digit words are allowed there"
                    )
                digits += str(_EN_DIGIT_WORDS[token])
                index += 1
        if len(digits) > 12:
            return (
                f"the fractional part exceeds the 12-digit limit "
                f"(got {len(digits)} digits)"
            )
        if zero_only and sign < 0 and not digits:
            return "negative zero is not a valid number"
        int_text = str(integer)
        return sign, int_text, digits

    @staticmethod
    def _read_en_number(tokens: list, index: int) -> Tuple[int, int, Any]:
        """Read one 1..99 number (``[[tens]-]unit`` or a teen).

        Returns ``(value, next_index, error)`` — ``error`` is ``None``
        on success.
        """
        token = tokens[index]
        if token in _EN_TEENS:
            return _EN_TEENS[token], index + 1, None
        if token in _EN_TENS:
            value = _EN_TENS[token]
            if index + 1 < len(tokens) and tokens[index + 1] in _EN_UNITS:
                return value + _EN_UNITS[tokens[index + 1]], index + 2, None
            return value, index + 1, None
        if token in _EN_UNITS:
            return _EN_UNITS[token], index + 1, None
        return 0, index, f"expected a number word, got {token!r}"

    @classmethod
    def _read_en_group(cls, tokens: list, index: int) -> Tuple[int, int, Any]:
        """Read one 1..999 group: ``[unit] hundred [number]`` or ``number``."""
        token = tokens[index]
        # "[unit] hundred" — the hundreds operand must be a bare unit.
        if (
            token in _EN_UNITS
            and index + 1 < len(tokens)
            and tokens[index + 1] == "hundred"
        ):
            hundreds = _EN_UNITS[token]
            index += 2
            if index < len(tokens) and tokens[index] not in (
                "point", *_EN_SCALES
            ) and tokens[index] != "hundred":
                rest, index, error = cls._read_en_number(tokens, index)
                if error:
                    return 0, index, error
                return hundreds * 100 + rest, index, None
            return hundreds * 100, index, None
        if token == "hundred":
            return 0, index, (
                "'hundred' must be preceded by one of the words one..nine"
            )
        value, index, error = cls._read_en_number(tokens, index)
        if error:
            return 0, index, error
        if index < len(tokens) and tokens[index] == "hundred":
            return 0, index, (
                "'hundred' must be preceded by one of the words one..nine "
                "(e.g. 'ten hundred' is not a valid group)"
            )
        return value, index, None

    # ------------------------------ Chinese --------------------------- #

    @classmethod
    def _parse_zh(cls, words: str) -> Any:
        """Parse Chinese numerals; return ``(sign, int, frac)`` or an
        error-message string."""
        text = words
        sign = 1
        if text.startswith("负"):
            sign = -1
            text = text[1:]
            if not text:
                return "a bare '负' sign without a number"
        if not text:
            return "the words string contains no digits to parse"

        integer_text, dot, fraction_text = text.partition("点")
        if dot and not integer_text:
            return "'点' must follow an integer part (e.g. '零点五')"
        if dot and not fraction_text:
            return "'点' must be followed by at least one digit character"
        if "点" in fraction_text:
            return "at most one '点' is allowed"
        for ch in fraction_text:
            if ch not in _ZH_DECIMAL_DIGITS:
                return (
                    f"unexpected character {ch!r} after '点' — only digit "
                    "characters 零〇一...九 are allowed there"
                )
        if " " in integer_text or "\u3000" in integer_text:
            return "unexpected whitespace inside the Chinese numeral"
        if integer_text in ("零", "〇"):
            # The bare zero numeral — the only standalone 零 form.
            if sign < 0 and not fraction_text:
                return "negative zero is not a valid number"
            digits = "".join(str(_ZH_DIGITS[ch]) for ch in fraction_text)
            return sign, "0", digits

        total = 0          # completed 亿-level contribution
        wan_value = 0      # completed 万-level contribution (absolute)
        section = 0        # current 千-level section value
        digit = None       # pending bare digit
        last_unit = 10000  # unit-ordering guard within a section
        wan_seen = False
        zero_pending = False
        leading_ten_ok = True
        after_group_unit = False  # directly after 万 / 亿
        pending_post_group = False  # pending digit read right after 万 / 亿
        for ch in integer_text:
            if ch in _ZH_DIGITS:
                if ch in "零〇":
                    if zero_pending:
                        return "repeated '零' — at most one gap zero is allowed"
                    if not (section or digit is not None or wan_value or total):
                        return (
                            "'零'/'〇' is only allowed between significant "
                            "digits or inside the fractional part"
                        )
                    if digit is not None:
                        return (
                            "positional digit sequences such as '一零五' are "
                            "not supported — use unit characters "
                            "(一百零五)"
                        )
                    zero_pending = True
                    continue
                if digit is not None:
                    return (
                        "two value digits in a row without a unit character "
                        "between them — positional sequences such as '一二三' "
                        "are not supported"
                    )
                if after_group_unit and not zero_pending:
                    # A value digit directly after 万/亿 is only valid when
                    # a unit character follows it (一万一千) or a 零 came
                    # between (一万零一); a digit still pending at the end
                    # is a truncated colloquial form (一万二 → 12000?).
                    pending_post_group = True
                else:
                    pending_post_group = False
                digit = _ZH_DIGITS[ch]
                zero_pending = False
                leading_ten_ok = False
                after_group_unit = False
            elif ch in _ZH_UNITS:
                unit_value = _ZH_UNITS[ch]
                if unit_value >= last_unit:
                    return (
                        f"unit characters must be strictly decreasing "
                        f"within a section (got {ch!r} after a unit of "
                        "equal or higher value)"
                    )
                if digit is None:
                    if ch == "十" and leading_ten_ok:
                        section += 10
                    else:
                        return (
                            f"unit character {ch!r} must be preceded by a "
                            "digit character"
                        )
                else:
                    section += digit * unit_value
                digit = None
                last_unit = unit_value
                zero_pending = False
                leading_ten_ok = False
                after_group_unit = False
                pending_post_group = False
            elif ch == "万":
                if wan_seen:
                    return "at most one '万' per 亿 section is allowed"
                if not (section or digit is not None):
                    return "a bare '万' must be preceded by a number"
                wan_value += (section + (digit or 0)) * 10_000
                section = 0
                digit = None
                last_unit = 10000
                wan_seen = True
                zero_pending = False
                leading_ten_ok = True
                after_group_unit = True
                pending_post_group = False
            elif ch == "亿":
                if not (total or wan_value or section or digit is not None):
                    return "a bare '亿' must be preceded by a number"
                total += (wan_value + section + (digit or 0)) * 100_000_000
                wan_value = 0
                section = 0
                digit = None
                last_unit = 10000
                wan_seen = False
                zero_pending = False
                leading_ten_ok = True
                after_group_unit = True
                pending_post_group = False
            else:
                return (
                    f"unexpected character {ch!r} — expected digit "
                    "characters (零〇一两二三四五六七八九), unit characters "
                    "(十百千), '万', '亿' or '点'"
                )
        if zero_pending:
            return "a trailing '零' is not allowed — the numeral must end with a value"
        if digit is not None and pending_post_group:
            return (
                "truncated forms such as '一万二' are ambiguous and "
                "not supported — write the full form "
                "(一万二千 or 一万零二)"
            )
        integer = total + wan_value + section + (digit or 0)
        int_text = str(integer)
        digits = "".join(str(_ZH_DIGITS[ch]) for ch in fraction_text)
        if len(digits) > 12:
            return (
                f"the fractional part exceeds the 12-digit limit "
                f"(got {len(digits)} digits)"
            )
        if integer == 0 and sign < 0 and not digits:
            return "negative zero is not a valid number"
        return sign, int_text, digits
