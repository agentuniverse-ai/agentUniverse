#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: currency_format_tool.py

"""ISO-4217 currency formatting / reference tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency currency formatting
helper. The tool never looks up exchange rates and never contacts any
service; every output is computed offline from an embedded indicative
table of 39 ISO-4217 currencies.

Three modes behind a single ``execute(mode=..., ...)`` call:

* ``format`` — render an amount for a 3-letter ISO-4217 currency code
  with locale-style digit grouping, the currency's default minor-unit
  (decimal) count, and an optional currency symbol. Locales: ``en``
  (``1,234.56``), ``de`` (``1.234,56``), ``fr`` (``1 234,56``) and
  ``zh`` (``1,234.56``; when a symbol is shown it is always placed as
  a prefix, e.g. ``¥1,234.56``). ``decimals`` overrides the table
  default (JPY / KRW / VND default to 0 minor units, BHD / KWD / OMR
  to 3, most currencies to 2). With ``symbol=True`` the currency's
  symbol is used where the embedded table knows one ($ € ¥ £ ₩ ₹ …);
  currencies without a well-known symbol fall back to their code,
  attached with a space (``CHF 1,234.56``). Symbols attach as a prefix
  without a space in the ``en`` / ``zh`` locales (``$1,234.56``) and
  as a space-separated suffix in ``de`` / ``fr`` (``1.234,56 €``).
* ``info`` — look up one currency code in the embedded table and
  return its name, symbol (``None`` when the table has none), minor
  units, the table size, and the data source (ISO 4217). The table is
  an *indicative* snapshot of ISO 4217 currency names, symbols and
  minor-unit exponents; it is not a live standard publication and
  deliberately includes no exotic / fund codes.
* ``convert_presentation`` — an intentionally honest no-conversion
  helper. It performs **no** exchange-rate lookup (the tool is
  offline); the numeric amount is returned unchanged and only
  re-presented under each currency's minor-unit conventions, e.g.
  ``123.4`` JPY (0 minor units) reads ``123`` JPY while the same
  numeric value presented as USD (2 minor units) reads ``123.40``
  USD. The result states explicitly that no rate was applied, so
  agents do not mistake a re-presentation for a conversion.

Rounding is exact and deterministic: amounts are parsed to
``decimal.Decimal`` (via the shortest decimal representation for
floats, so ``123.4`` never becomes ``123.40000000000001``) and
quantized with ``ROUND_HALF_UP`` — half-up, *not* bankers' rounding
(``ROUND_HALF_EVEN`` would turn ``2.5`` JPY into ``2``; this tool
returns ``3``).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing / mistyped amount or
currency code, a code that is not exactly 3 ASCII letters, a code
absent from the embedded table, a locale outside the whitelist,
``decimals`` outside 0–6 or not an integer, a non-boolean ``symbol``,
non-finite amounts, or a magnitude above 1,000,000,000,000,000) raise
a ``ValueError`` mirroring the other common tools. Negative zero is
normalized to ``0`` so ``-0.0`` never renders as ``-0.00``.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class CurrencyFormatTool(Tool):
    """ISO-4217 currency formatting / reference tool (pure stdlib, offline).

    Attributes:
        max_abs_amount (Decimal): Upper bound on the ``amount`` magnitude;
            amounts beyond it are rejected before any computation.
        max_decimals (int): Upper bound for an explicit ``decimals``
            override.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "currency_format_tool"
    description: str = (
        "Currency format tool — ISO-4217 amount formatting, pure Python "
        "stdlib, no network required. Format an amount with per-currency "
        "minor units and locale-style grouping (mode='format': en "
        "1,234.56 | de 1.234,56 | fr 1 234,56 | zh ¥1,234.56, optional "
        "currency symbol with code fallback), look up a currency's name / "
        "symbol / minor units in an embedded indicative ISO-4217 table "
        "(mode='info'), or re-present an amount under another currency's "
        "minor units with NO exchange-rate lookup — the amount is "
        "unchanged (mode='convert_presentation')."
    )

    MODES: ClassVar[tuple] = ("format", "info", "convert_presentation")
    LOCALES: ClassVar[tuple] = ("en", "de", "fr", "zh")
    # locale -> (thousands group separator, decimal separator). The zh
    # locale groups like en but always prefixes the symbol when one is
    # shown (see _run_format).
    LOCALE_SEPARATORS: ClassVar[dict] = {
        "en": (",", "."),
        "de": (".", ","),
        "fr": (" ", ","),
        "zh": (",", "."),
    }
    # Locales that attach the currency marker as a prefix (no space for a
    # real symbol); de/fr attach it as a space-separated suffix.
    PREFIX_SYMBOL_LOCALES: ClassVar[tuple] = ("en", "zh")

    # Embedded indicative ISO-4217 table: code -> (name, symbol, minor
    # units). A symbol of None means the table has no well-known symbol,
    # so symbol display falls back to the code itself. Source: ISO 4217
    # ("Codes for the representation of currencies") — indicative
    # snapshot, not a live standard publication.
    CURRENCIES: ClassVar[dict] = {
        "USD": ("US Dollar", "$", 2),
        "EUR": ("Euro", "€", 2),
        "GBP": ("Pound Sterling", "£", 2),
        "JPY": ("Yen", "¥", 0),
        "CNY": ("Yuan Renminbi", "¥", 2),
        "KRW": ("Won", "₩", 0),
        "HKD": ("Hong Kong Dollar", "HK$", 2),
        "TWD": ("New Taiwan Dollar", "NT$", 2),
        "SGD": ("Singapore Dollar", "S$", 2),
        "AUD": ("Australian Dollar", "A$", 2),
        "NZD": ("New Zealand Dollar", "NZ$", 2),
        "CAD": ("Canadian Dollar", "C$", 2),
        "CHF": ("Swiss Franc", None, 2),
        "SEK": ("Swedish Krona", "kr", 2),
        "NOK": ("Norwegian Krone", "kr", 2),
        "DKK": ("Danish Krone", "kr", 2),
        "INR": ("Indian Rupee", "₹", 2),
        "RUB": ("Russian Ruble", "₽", 2),
        "BRL": ("Brazilian Real", "R$", 2),
        "MXN": ("Mexican Peso", "MX$", 2),
        "ZAR": ("Rand", "R", 2),
        "TRY": ("Turkish Lira", "₺", 2),
        "AED": ("UAE Dirham", None, 2),
        "SAR": ("Saudi Riyal", None, 2),
        "THB": ("Baht", "฿", 2),
        "IDR": ("Rupiah", "Rp", 2),
        "MYR": ("Malaysian Ringgit", "RM", 2),
        "PHP": ("Philippine Peso", "₱", 2),
        "VND": ("Dong", "₫", 0),
        "PLN": ("Zloty", "zł", 2),
        "CZK": ("Czech Koruna", "Kč", 2),
        "HUF": ("Forint", "Ft", 2),
        "ILS": ("New Israeli Sheqel", "₪", 2),
        "EGP": ("Egyptian Pound", "E£", 2),
        "NGN": ("Naira", "₦", 2),
        "BHD": ("Bahraini Dinar", "BD", 3),
        "KWD": ("Kuwaiti Dinar", "KD", 3),
        "OMR": ("Rial Omani", None, 3),
        "QAR": ("Qatari Rial", "QR", 2),
    }

    SOURCE: ClassVar[str] = "ISO 4217 (embedded indicative table, offline)"
    max_abs_amount: Decimal = Decimal(10) ** 15
    max_decimals: int = 6

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        amount: Any = None,
        currency: Any = None,
        from_currency: Any = None,
        to_currency: Any = None,
        locale: Any = None,
        decimals: Any = None,
        symbol: Any = None,
    ) -> dict[str, Any]:
        """Run one currency formatting / reference operation.

        Args:
            mode (str): One of ``format`` / ``info`` /
                ``convert_presentation``.
            amount (int | float | str): The monetary amount — an int, a
                finite float, or a plain numeric string (no thousands
                separators). Required for the ``format`` and
                ``convert_presentation`` modes; not used by ``info``.
            currency (str): The 3-letter ISO-4217 currency code
                (case-insensitive, e.g. ``"USD"`` / ``"jpy"``). Required
                for the ``format`` and ``info`` modes.
            from_currency (str): ``convert_presentation`` only — the
                3-letter code of the source currency.
            to_currency (str): ``convert_presentation`` only — the
                3-letter code of the target currency (presentation only;
                no exchange rate is applied).
            locale (str): ``format`` only — ``en`` / ``de`` / ``fr`` /
                ``zh`` (case-insensitive); defaults to ``en``.
            decimals (int): ``format`` only — explicit minor-unit
                override (0–6); defaults to the currency's table value
                (JPY / KRW / VND 0, BHD / KWD / OMR 3, most 2).
            symbol (bool): ``format`` only — when True, attach the
                currency symbol where the table knows one, else the code
                itself; prefix (no space) for ``en`` / ``zh``, a
                space-separated suffix for ``de`` / ``fr``.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context) or — for
                ``convert_presentation`` — an explicit
                ``amount_unchanged`` / ``rate_lookup: False`` disclosure.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode == "format":
            return self._run_format(amount, currency, locale, decimals, symbol)
        if mode == "info":
            return self._run_info(currency)
        return self._run_convert_presentation(amount, from_currency, to_currency)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"currency_format_tool: {message}")

    def _validate_amount(self, amount: Any) -> Decimal:
        """Validate the ``amount`` input and return it as a Decimal.

        Accepts ints, finite floats and plain numeric strings (leading /
        trailing whitespace tolerated, thousands separators and
        underscore digit grouping rejected); rejects NaN / infinity and
        any magnitude above ``max_abs_amount``. Floats are converted
        through their shortest decimal representation so binary
        artifacts never reach the formatter.
        """
        if amount is None or isinstance(amount, bool):
            self._invalid(
                "amount is required for the format and convert_presentation "
                f"modes and must be an int, float or numeric string (got {amount!r})"
            )
        if isinstance(amount, (int, float)):
            text = str(amount)
        elif isinstance(amount, str):
            text = amount.strip()
            if "_" in text:
                self._invalid(
                    "amount must be a plain numeric string without "
                    f"underscore or thousands separators (got {amount!r})"
                )
        else:
            self._invalid(
                "amount must be an int, float or numeric string "
                f"(got {amount!r})"
            )
        try:
            value = Decimal(text)
        except (InvalidOperation, ValueError):
            self._invalid(f"amount must be a finite number (got {amount!r})")
        if not value.is_finite():
            self._invalid(f"amount must be a finite number (got {text!r})")
        if abs(value) > self.max_abs_amount:
            self._invalid(
                "|amount| exceeds the "
                f"{self.max_abs_amount:,} limit (got {text!r})"
            )
        return value

    @classmethod
    def _validate_currency(cls, code: Any, label: str) -> str:
        """Validate one currency code; return its uppercase form.

        Accepts exactly 3 ASCII letters, case-insensitive, and requires
        the code to be present in the embedded indicative ISO-4217
        table.
        """
        if code is None or isinstance(code, bool) or not isinstance(code, str):
            cls._invalid(
                f"{label} is required and must be a 3-letter ISO-4217 "
                f"currency code (got {code!r})"
            )
        normalized = code.strip().upper()
        if len(normalized) != 3 or not normalized.isascii() or not normalized.isalpha():
            cls._invalid(
                f"{label} must be exactly 3 ASCII letters, like 'USD' "
                f"(got {code!r})"
            )
        if normalized not in cls.CURRENCIES:
            cls._invalid(
                f"unknown ISO-4217 currency code {normalized!r} — not in "
                f"the embedded indicative table of "
                f"{len(cls.CURRENCIES)} currencies"
            )
        return normalized

    @classmethod
    def _validate_locale(cls, locale: Any) -> str:
        """Validate the format-mode ``locale`` selector."""
        if locale is None:
            return "en"
        if isinstance(locale, bool) or not isinstance(locale, str):
            cls._invalid(
                f"locale must be one of: {', '.join(cls.LOCALES)} (got {locale!r})"
            )
        normalized = locale.strip().lower()
        if normalized not in cls.LOCALES:
            cls._invalid(
                f"locale must be one of: {', '.join(cls.LOCALES)} "
                f"(got {locale!r})"
            )
        return normalized

    def _validate_decimals(self, decimals: Any, default: int) -> int:
        """Validate the format-mode ``decimals`` override."""
        if decimals is None:
            return default
        if isinstance(decimals, bool) or not isinstance(decimals, int):
            self._invalid(
                f"decimals must be an integer between 0 and {self.max_decimals} "
                f"(got {decimals!r})"
            )
        if not 0 <= decimals <= self.max_decimals:
            self._invalid(
                f"decimals must be an integer between 0 and {self.max_decimals} "
                f"(got {decimals!r})"
            )
        return decimals

    @classmethod
    def _validate_symbol(cls, symbol: Any) -> bool:
        """Validate the format-mode ``symbol`` flag."""
        if symbol is None:
            return False
        if not isinstance(symbol, bool):
            cls._invalid(f"symbol must be a boolean (got {symbol!r})")
        return symbol

    # ------------------------------------------------------------------ #
    # Core formatting helpers (deterministic, half-up rounding)
    # ------------------------------------------------------------------ #

    @classmethod
    def _quantize(cls, value: Decimal, decimals: int) -> Decimal:
        """Quantize with ROUND_HALF_UP and normalize negative zero.

        Half-up is deliberate: 2.5 JPY renders as ``3``, not ``2`` as
        bankers' rounding (ROUND_HALF_EVEN) would produce.
        """
        quantized = value.quantize(
            Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP
        )
        if quantized == 0:
            quantized = abs(quantized)
        return quantized

    @staticmethod
    def _group_thousands(digits: str, separator: str) -> str:
        """Group a plain digit string in threes from the right."""
        groups: list[str] = []
        while len(digits) > 3:
            groups.append(digits[-3:])
            digits = digits[:-3]
        groups.append(digits)
        return separator.join(reversed(groups))

    @classmethod
    def _render(cls, value: Decimal, decimals: int, locale: str) -> str:
        """Render a quantized Decimal with locale separators, no symbol.

        The value is already quantized to exactly ``decimals`` places, so
        ``format(value, 'f')`` yields its exact fixed-point form (with no
        decimal point at all for zero-decimal currencies such as JPY).
        """
        plain = format(value, "f")
        sign = ""
        if plain.startswith("-"):
            sign, plain = "-", plain[1:]
        if "." in plain:
            int_part, frac_part = plain.split(".")
        else:
            int_part, frac_part = plain, ""
        group_sep, dec_sep = cls.LOCALE_SEPARATORS[locale]
        body = cls._group_thousands(int_part, group_sep)
        if frac_part:
            body += dec_sep + frac_part
        return sign + body

    @classmethod
    def _present(cls, amount: Decimal, decimals: int) -> str:
        """en-style, symbol-free presentation used by convert_presentation."""
        return cls._render(cls._quantize(amount, decimals), decimals, "en")

    # ------------------------------------------------------------------ #
    # format mode
    # ------------------------------------------------------------------ #

    def _run_format(
        self,
        amount: Any,
        currency: Any,
        locale: Any,
        decimals: Any,
        symbol: Any,
    ) -> dict[str, Any]:
        """Format an amount under a currency's conventions."""
        code = self._validate_currency(currency, "currency")
        clean_locale = self._validate_locale(locale)
        use_symbol = self._validate_symbol(symbol)
        clean_decimals = self._validate_decimals(
            decimals, self.CURRENCIES[code][2]
        )
        value = self._validate_amount(amount)

        quantized = self._quantize(value, clean_decimals)
        rendered = self._render(quantized, clean_decimals, clean_locale)

        marker_used: str | None = None
        if use_symbol:
            table_symbol = self.CURRENCIES[code][1]
            # Currencies without a well-known symbol fall back to the
            # code itself; a real symbol attaches without a space in the
            # prefix locales, while the code fallback keeps one.
            is_real_symbol = table_symbol is not None
            marker_used = table_symbol if is_real_symbol else code
            negative = rendered.startswith("-")
            body = rendered[1:] if negative else rendered
            sign = "-" if negative else ""
            prefix_gap = "" if is_real_symbol else " "
            if clean_locale in self.PREFIX_SYMBOL_LOCALES:
                rendered = sign + marker_used + prefix_gap + body
            else:
                rendered = sign + body + " " + marker_used

        return {
            "mode": "format",
            "currency": code,
            "locale": clean_locale,
            "decimals": clean_decimals,
            "symbol": use_symbol,
            "symbol_used": marker_used,
            "rounded_amount": format(quantized, "f"),
            "result": rendered,
        }

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def _run_info(self, currency: Any) -> dict[str, Any]:
        """Look up one currency code in the embedded indicative table."""
        code = self._validate_currency(currency, "currency")
        name, table_symbol, minor_units = self.CURRENCIES[code]
        symbol_text = (
            table_symbol if table_symbol is not None
            else f"none (falls back to code {code})"
        )
        return {
            "mode": "info",
            "currency": code,
            "name": name,
            "symbol": table_symbol,
            "minor_units": minor_units,
            "table_size": len(self.CURRENCIES),
            "source": self.SOURCE,
            "result": (
                f"{code} — {name}, {minor_units} minor units, "
                f"symbol {symbol_text}"
            ),
        }

    # ------------------------------------------------------------------ #
    # convert_presentation mode (no rate lookup — honest re-presentation)
    # ------------------------------------------------------------------ #

    def _run_convert_presentation(
        self, amount: Any, from_currency: Any, to_currency: Any
    ) -> dict[str, Any]:
        """Re-present an amount under another currency's minor units.

        Deliberately performs NO exchange-rate lookup: the tool is
        offline and the numeric amount is returned unchanged. Only the
        minor-unit presentations differ (e.g. 123.4 JPY -> '123' JPY /
        '123.40' USD); the result says so explicitly so the value is
        never mistaken for a converted one.
        """
        from_code = self._validate_currency(from_currency, "from_currency")
        to_code = self._validate_currency(to_currency, "to_currency")
        value = self._validate_amount(amount)
        from_minor = self.CURRENCIES[from_code][2]
        to_minor = self.CURRENCIES[to_code][2]
        amount_text = str(value)
        from_presentation = self._present(value, from_minor)
        to_presentation = self._present(value, to_minor)
        note = (
            "No exchange rate was applied: this tool is offline and "
            "performs no rate lookups. The numeric amount is unchanged; "
            "only the presentation differs, following each currency's "
            f"ISO-4217 minor units ({from_code}: {from_minor}, "
            f"{to_code}: {to_minor})."
        )
        result = (
            f"{amount_text} {from_code} -> {amount_text} {to_code} "
            f"(unchanged); presented with {from_code} conventions: "
            f"'{from_presentation} {from_code}', with {to_code} "
            f"conventions: '{to_presentation} {to_code}'"
        )
        return {
            "mode": "convert_presentation",
            "amount": amount_text,
            "from_currency": from_code,
            "to_currency": to_code,
            "from_minor_units": from_minor,
            "to_minor_units": to_minor,
            "amount_unchanged": amount_text,
            "from_presentation": from_presentation,
            "to_presentation": to_presentation,
            "rate_lookup": False,
            "note": note,
            "result": result,
        }
