#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_currency_format_tool.py

"""Offline unit tests for CurrencyFormatTool.

The tool is built purely on the standard library (decimal) and never
touches the network, so this suite runs fully offline. Every assertion
is deterministic: locale renderings are checked against literal ground
truths (including thousands-grouping boundaries), rounding against
half-up expectations that deliberately differ from bankers' rounding,
and every rejection against its exact error message fragment.
"""

import unittest
from decimal import Decimal

from agentuniverse.agent.action.tool.common_tool import CurrencyFormatTool
from agentuniverse.agent.action.tool.common_tool.currency_format_tool import (
    CurrencyFormatTool as DirectCurrencyFormatTool,
)

# All 39 codes the embedded indicative ISO-4217 table must cover.
EXPECTED_TABLE_CODES = {
    "USD", "EUR", "GBP", "JPY", "CNY", "KRW", "HKD", "TWD", "SGD",
    "AUD", "NZD", "CAD", "CHF", "SEK", "NOK", "DKK", "INR", "RUB",
    "BRL", "MXN", "ZAR", "TRY", "AED", "SAR", "THB", "IDR", "MYR",
    "PHP", "VND", "PLN", "CZK", "HUF", "ILS", "EGP", "NGN", "BHD",
    "KWD", "OMR", "QAR",
}


class CurrencyFormatToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib CurrencyFormatTool."""

    def setUp(self) -> None:
        self.tool = CurrencyFormatTool()

    # ------------------------------------------------------------------ #
    # format mode — locale ground truths
    # ------------------------------------------------------------------ #

    def test_format_locale_en(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="USD", locale="en"
        )
        self.assertEqual(result["result"], "1,234.56")
        self.assertEqual(
            result,
            {
                "mode": "format",
                "currency": "USD",
                "locale": "en",
                "decimals": 2,
                "symbol": False,
                "symbol_used": None,
                "rounded_amount": "1234.56",
                "result": "1,234.56",
            },
        )

    def test_format_locale_de(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="EUR", locale="de"
        )
        self.assertEqual(result["result"], "1.234,56")

    def test_format_locale_fr(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="EUR", locale="fr"
        )
        self.assertEqual(result["result"], "1 234,56")

    def test_format_locale_zh_symbol_prefix(self) -> None:
        result = self.tool.execute(
            mode="format",
            amount=1234.56,
            currency="CNY",
            locale="zh",
            symbol=True,
        )
        self.assertEqual(result["result"], "¥1,234.56")

    def test_format_locale_zh_without_symbol(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="CNY", locale="zh"
        )
        self.assertEqual(result["result"], "1,234.56")

    def test_format_default_locale_is_en(self) -> None:
        result = self.tool.execute(mode="format", amount=1234.56, currency="USD")
        self.assertEqual(result["locale"], "en")
        self.assertEqual(result["result"], "1,234.56")

    def test_format_locale_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="EUR", locale="DE"
        )
        self.assertEqual(result["result"], "1.234,56")

    # ------------------------------------------------------------------ #
    # format mode — symbol placement per locale
    # ------------------------------------------------------------------ #

    def test_symbol_prefix_en(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="USD", symbol=True
        )
        self.assertEqual(result["result"], "$1,234.56")
        self.assertEqual(result["symbol_used"], "$")

    def test_symbol_suffix_de(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="EUR",
            locale="de", symbol=True,
        )
        self.assertEqual(result["result"], "1.234,56 €")

    def test_symbol_suffix_fr(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="EUR",
            locale="fr", symbol=True,
        )
        self.assertEqual(result["result"], "1 234,56 €")

    def test_symbol_fallback_to_code_chf_en(self) -> None:
        # CHF is in the table but carries no well-known symbol, so the
        # code itself is used, attached with a space.
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="CHF", symbol=True
        )
        self.assertEqual(result["result"], "CHF 1,234.56")
        self.assertEqual(result["symbol_used"], "CHF")

    def test_symbol_fallback_to_code_chf_de(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="CHF",
            locale="de", symbol=True,
        )
        self.assertEqual(result["result"], "1.234,56 CHF")

    def test_symbol_fallback_to_code_aed(self) -> None:
        result = self.tool.execute(
            mode="format", amount=100, currency="AED", symbol=True
        )
        self.assertEqual(result["result"], "AED 100.00")

    def test_multi_char_symbol_no_space(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="HKD", symbol=True
        )
        self.assertEqual(result["result"], "HK$1,234.56")

    # ------------------------------------------------------------------ #
    # format mode — thousands grouping boundaries (en, USD)
    # ------------------------------------------------------------------ #

    def test_grouping_boundary_999(self) -> None:
        result = self.tool.execute(mode="format", amount=999, currency="USD")
        self.assertEqual(result["result"], "999.00")

    def test_grouping_boundary_1000(self) -> None:
        result = self.tool.execute(mode="format", amount=1000, currency="USD")
        self.assertEqual(result["result"], "1,000.00")

    def test_grouping_boundary_999999(self) -> None:
        result = self.tool.execute(mode="format", amount=999999, currency="USD")
        self.assertEqual(result["result"], "999,999.00")

    def test_grouping_boundary_1000000(self) -> None:
        result = self.tool.execute(mode="format", amount=1000000, currency="USD")
        self.assertEqual(result["result"], "1,000,000.00")

    def test_upper_bound_inclusive_1e15(self) -> None:
        result = self.tool.execute(
            mode="format", amount=10 ** 15, currency="USD"
        )
        self.assertEqual(
            result["result"], "1,000,000,000,000,000.00"
        )

    def test_grouping_de_locale_boundaries(self) -> None:
        result = self.tool.execute(
            mode="format", amount=999999, currency="EUR", locale="de"
        )
        self.assertEqual(result["result"], "999.999,00")

    # ------------------------------------------------------------------ #
    # format mode — per-currency minor units (JPY 0, BHD/KWD/OMR 3, ...)
    # ------------------------------------------------------------------ #

    def test_jpy_zero_decimals_round_down(self) -> None:
        result = self.tool.execute(mode="format", amount=123.4, currency="JPY")
        self.assertEqual(result["decimals"], 0)
        self.assertEqual(result["result"], "123")

    def test_jpy_zero_decimals_round_half_up(self) -> None:
        result = self.tool.execute(mode="format", amount=123.5, currency="JPY")
        self.assertEqual(result["result"], "124")

    def test_half_up_not_bankers_rounding(self) -> None:
        # Bankers' rounding (ROUND_HALF_EVEN) would give 2 for 2.5;
        # this tool deliberately uses ROUND_HALF_UP and gives 3.
        result = self.tool.execute(mode="format", amount=2.5, currency="JPY")
        self.assertEqual(result["result"], "3")
        result = self.tool.execute(mode="format", amount=0.5, currency="JPY")
        self.assertEqual(result["result"], "1")
        result = self.tool.execute(mode="format", amount=-2.5, currency="JPY")
        self.assertEqual(result["result"], "-3")

    def test_bhd_three_decimals(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1.2345, currency="BHD"
        )
        self.assertEqual(result["decimals"], 3)
        self.assertEqual(result["result"], "1.235")
        result = self.tool.execute(
            mode="format", amount=1.2344, currency="BHD"
        )
        self.assertEqual(result["result"], "1.234")

    def test_kwd_three_decimals(self) -> None:
        result = self.tool.execute(
            mode="format", amount=2.4565, currency="KWD"
        )
        self.assertEqual(result["result"], "2.457")

    def test_omr_three_decimals(self) -> None:
        result = self.tool.execute(
            mode="format", amount=3.14159, currency="OMR"
        )
        self.assertEqual(result["result"], "3.142")

    def test_vnd_zero_decimals(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1500.6, currency="VND"
        )
        self.assertEqual(result["result"], "1,501")

    def test_decimals_override_jpy(self) -> None:
        result = self.tool.execute(
            mode="format", amount=123.4, currency="JPY", decimals=2
        )
        self.assertEqual(result["decimals"], 2)
        self.assertEqual(result["result"], "123.40")

    def test_decimals_override_zero_usd(self) -> None:
        result = self.tool.execute(
            mode="format", amount=1234.56, currency="USD", decimals=0
        )
        self.assertEqual(result["result"], "1,235")

    # ------------------------------------------------------------------ #
    # format mode — amount types, signs, determinism
    # ------------------------------------------------------------------ #

    def test_negative_amount_en(self) -> None:
        result = self.tool.execute(
            mode="format", amount=-1234.56, currency="USD"
        )
        self.assertEqual(result["result"], "-1,234.56")

    def test_negative_amount_with_symbol(self) -> None:
        result = self.tool.execute(
            mode="format", amount=-1234.56, currency="USD", symbol=True
        )
        self.assertEqual(result["result"], "-$1,234.56")
        result = self.tool.execute(
            mode="format", amount=-1234.56, currency="EUR",
            locale="de", symbol=True,
        )
        self.assertEqual(result["result"], "-1.234,56 €")

    def test_negative_zero_normalized(self) -> None:
        result = self.tool.execute(
            mode="format", amount=-0.0, currency="USD"
        )
        self.assertEqual(result["result"], "0.00")
        result = self.tool.execute(
            mode="format", amount="-0.001", currency="USD"
        )
        self.assertEqual(result["result"], "0.00")

    def test_small_negative_not_normalized(self) -> None:
        result = self.tool.execute(
            mode="format", amount=-0.04, currency="USD"
        )
        self.assertEqual(result["result"], "-0.04")

    def test_int_and_string_amounts(self) -> None:
        result = self.tool.execute(mode="format", amount=5, currency="USD")
        self.assertEqual(result["result"], "5.00")
        result = self.tool.execute(
            mode="format", amount="1234.56", currency="USD"
        )
        self.assertEqual(result["result"], "1,234.56")

    def test_string_amount_whitespace_tolerated(self) -> None:
        result = self.tool.execute(
            mode="format", amount=" 1234.56 ", currency="USD"
        )
        self.assertEqual(result["result"], "1,234.56")

    def test_float_and_string_amounts_agree(self) -> None:
        # Floats go through their shortest decimal representation, so a
        # float and its literal string form render identically.
        float_result = self.tool.execute(
            mode="format", amount=123.4, currency="USD"
        )
        string_result = self.tool.execute(
            mode="format", amount="123.4", currency="USD"
        )
        self.assertEqual(float_result, string_result)

    def test_currency_code_case_insensitive(self) -> None:
        result = self.tool.execute(mode="format", amount=123.4, currency="jpy")
        self.assertEqual(result["currency"], "JPY")
        self.assertEqual(result["result"], "123")

    def test_deterministic_repeated_calls(self) -> None:
        first = self.tool.execute(
            mode="format", amount=1234567.891, currency="EUR", locale="fr"
        )
        second = self.tool.execute(
            mode="format", amount=1234567.891, currency="EUR", locale="fr"
        )
        self.assertEqual(first, second)
        self.assertEqual(first["result"], "1 234 567,89")

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def test_info_usd(self) -> None:
        result = self.tool.execute(mode="info", currency="USD")
        self.assertEqual(
            result,
            {
                "mode": "info",
                "currency": "USD",
                "name": "US Dollar",
                "symbol": "$",
                "minor_units": 2,
                "table_size": 39,
                "source": self.tool.SOURCE,
                "result": "USD — US Dollar, 2 minor units, symbol $",
            },
        )

    def test_info_jpy_zero_minor_units(self) -> None:
        result = self.tool.execute(mode="info", currency="JPY")
        self.assertEqual(result["minor_units"], 0)
        self.assertEqual(result["symbol"], "¥")

    def test_info_bhd_three_minor_units(self) -> None:
        result = self.tool.execute(mode="info", currency="BHD")
        self.assertEqual(result["minor_units"], 3)

    def test_info_chf_symbol_none(self) -> None:
        result = self.tool.execute(mode="info", currency="CHF")
        self.assertIsNone(result["symbol"])
        self.assertIn("falls back to code CHF", result["result"])

    def test_info_source_cites_iso_4217(self) -> None:
        result = self.tool.execute(mode="info", currency="EUR")
        self.assertIn("ISO 4217", result["source"])
        self.assertIn("indicative", result["source"])

    def test_table_covers_expected_codes(self) -> None:
        self.assertEqual(len(self.tool.CURRENCIES), 39)
        self.assertEqual(
            set(self.tool.CURRENCIES.keys()), EXPECTED_TABLE_CODES
        )

    def test_info_case_insensitive(self) -> None:
        result = self.tool.execute(mode="info", currency="usd")
        self.assertEqual(result["currency"], "USD")

    # ------------------------------------------------------------------ #
    # convert_presentation mode — honest no-conversion behaviour
    # ------------------------------------------------------------------ #

    def test_convert_presentation_jpy_to_usd(self) -> None:
        result = self.tool.execute(
            mode="convert_presentation",
            amount=123.4,
            from_currency="JPY",
            to_currency="USD",
        )
        self.assertEqual(result["amount"], "123.4")
        self.assertEqual(result["amount_unchanged"], "123.4")
        self.assertEqual(result["from_minor_units"], 0)
        self.assertEqual(result["to_minor_units"], 2)
        self.assertEqual(result["from_presentation"], "123")
        self.assertEqual(result["to_presentation"], "123.40")
        self.assertFalse(result["rate_lookup"])
        self.assertIn("No exchange rate was applied", result["note"])
        self.assertIn("unchanged", result["result"])
        # The numeric value really is unchanged.
        self.assertEqual(float(Decimal(result["amount_unchanged"])), 123.4)

    def test_convert_presentation_usd_to_jpy(self) -> None:
        result = self.tool.execute(
            mode="convert_presentation",
            amount="123.40",
            from_currency="USD",
            to_currency="JPY",
        )
        self.assertEqual(result["from_presentation"], "123.40")
        # 0.40 rounds down under JPY's 0 minor units.
        self.assertEqual(result["to_presentation"], "123")

    def test_convert_presentation_same_currency(self) -> None:
        result = self.tool.execute(
            mode="convert_presentation",
            amount="123.40",
            from_currency="USD",
            to_currency="USD",
        )
        self.assertEqual(
            result["from_presentation"], result["to_presentation"]
        )

    def test_convert_presentation_vnd_to_usd(self) -> None:
        result = self.tool.execute(
            mode="convert_presentation",
            amount=1500.6,
            from_currency="VND",
            to_currency="USD",
        )
        self.assertEqual(result["from_presentation"], "1,501")
        self.assertEqual(result["to_presentation"], "1,500.60")

    def test_convert_presentation_deterministic(self) -> None:
        first = self.tool.execute(
            mode="convert_presentation",
            amount=99.999,
            from_currency="USD",
            to_currency="BHD",
        )
        second = self.tool.execute(
            mode="convert_presentation",
            amount=99.999,
            from_currency="USD",
            to_currency="BHD",
        )
        self.assertEqual(first, second)

    # ------------------------------------------------------------------ #
    # error matrix — malformed parameters raise ValueError
    # ------------------------------------------------------------------ #

    def _assert_invalid(self, fragment: str, **kwargs) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.tool.execute(**kwargs)
        message = str(ctx.exception)
        self.assertTrue(
            message.startswith("currency_format_tool: "),
            f"error not prefixed with the tool name: {message!r}",
        )
        self.assertIn(fragment, message)

    def test_unknown_mode_rejected(self) -> None:
        self._assert_invalid(
            "mode must be one of", mode="convert", amount=1, currency="USD"
        )

    def test_format_missing_amount_rejected(self) -> None:
        self._assert_invalid(
            "amount is required", mode="format", currency="USD"
        )

    def test_format_missing_currency_rejected(self) -> None:
        self._assert_invalid(
            "currency is required", mode="format", amount=1
        )

    def test_amount_bool_rejected(self) -> None:
        self._assert_invalid(
            "amount is required", mode="format", amount=True, currency="USD"
        )

    def test_amount_non_numeric_string_rejected(self) -> None:
        self._assert_invalid(
            "amount must be a finite number",
            mode="format",
            amount="abc",
            currency="USD",
        )

    def test_amount_thousands_separator_string_rejected(self) -> None:
        self._assert_invalid(
            "amount must be a finite number",
            mode="format",
            amount="1,234.56",
            currency="USD",
        )

    def test_amount_underscore_grouping_rejected(self) -> None:
        # Decimal() silently tolerates underscores in almost any
        # position ('_100', '100_', '1__0'), which is outside the
        # documented plain-numeric-string contract — reject them.
        for bad in ("1_000", "_100", "100_", "1__0", "1_0.5"):
            with self.subTest(bad=bad):
                self._assert_invalid(
                    "plain numeric string",
                    mode="format",
                    amount=bad,
                    currency="USD",
                )

    def test_amount_list_rejected(self) -> None:
        self._assert_invalid(
            "amount must be an int, float or numeric string",
            mode="format",
            amount=[1],
            currency="USD",
        )

    def test_amount_nan_rejected(self) -> None:
        self._assert_invalid(
            "amount must be a finite number",
            mode="format",
            amount=float("nan"),
            currency="USD",
        )

    def test_amount_inf_rejected(self) -> None:
        self._assert_invalid(
            "amount must be a finite number",
            mode="format",
            amount=float("inf"),
            currency="USD",
        )

    def test_amount_above_bound_rejected(self) -> None:
        self._assert_invalid(
            "|amount| exceeds the 1,000,000,000,000,000 limit",
            mode="format",
            amount=10 ** 15 + 1,
            currency="USD",
        )

    def test_amount_string_above_bound_rejected(self) -> None:
        self._assert_invalid(
            "|amount| exceeds the",
            mode="format",
            amount="1e16",
            currency="USD",
        )

    def test_bounds_are_configurable_fields(self) -> None:
        # max_abs_amount and max_decimals are documented public fields
        # and must actually bound their inputs (the limit was previously
        # a hardcoded ClassVar and the decimals range a hardcoded 0-6,
        # so overriding either field had no effect).
        self.tool.max_abs_amount = Decimal(1000)
        self._assert_invalid(
            "|amount| exceeds the 1,000 limit",
            mode="format",
            amount=2000,
            currency="USD",
        )
        self.assertEqual(
            self.tool.execute(mode="format", amount=1000, currency="USD")["result"],
            "1,000.00",
        )
        self.tool.max_decimals = 2
        self._assert_invalid(
            "decimals must be an integer between 0 and 2",
            mode="format",
            amount=1.5,
            currency="USD",
            decimals=5,
        )
        self.assertEqual(
            self.tool.execute(
                mode="format", amount=1.5, currency="USD", decimals=2
            )["result"],
            "1.50",
        )

    def test_currency_wrong_length_rejected(self) -> None:
        for bad in ("US", "USDD", ""):
            self._assert_invalid(
                "must be exactly 3 ASCII letters",
                mode="format",
                amount=1,
                currency=bad,
            )

    def test_currency_non_letter_rejected(self) -> None:
        self._assert_invalid(
            "must be exactly 3 ASCII letters",
            mode="format",
            amount=1,
            currency="US$",
        )

    def test_currency_non_string_rejected(self) -> None:
        self._assert_invalid(
            "currency is required",
            mode="format",
            amount=1,
            currency=123,
        )

    def test_unknown_currency_code_lists_the_code(self) -> None:
        self._assert_invalid(
            "unknown ISO-4217 currency code 'XYZ'",
            mode="format",
            amount=1,
            currency="XYZ",
        )
        self._assert_invalid(
            "unknown ISO-4217 currency code 'XXX'",
            mode="info",
            currency="xxx",
        )

    def test_locale_whitelist_enforced(self) -> None:
        self._assert_invalid(
            "locale must be one of: en, de, fr, zh",
            mode="format",
            amount=1,
            currency="USD",
            locale="jp",
        )
        self._assert_invalid(
            "locale must be one of",
            mode="format",
            amount=1,
            currency="USD",
            locale=5,
        )

    def test_decimals_out_of_range_rejected(self) -> None:
        for bad in (-1, 7):
            self._assert_invalid(
                "decimals must be an integer between 0 and 6",
                mode="format",
                amount=1,
                currency="USD",
                decimals=bad,
            )

    def test_decimals_non_integer_rejected(self) -> None:
        for bad in (1.5, "2", True):
            self._assert_invalid(
                "decimals must be an integer between 0 and 6",
                mode="format",
                amount=1,
                currency="USD",
                decimals=bad,
            )

    def test_symbol_non_boolean_rejected(self) -> None:
        self._assert_invalid(
            "symbol must be a boolean",
            mode="format",
            amount=1,
            currency="USD",
            symbol="yes",
        )

    def test_convert_presentation_missing_to_currency(self) -> None:
        self._assert_invalid(
            "to_currency is required",
            mode="convert_presentation",
            amount=1,
            from_currency="USD",
        )

    def test_convert_presentation_unknown_code_lists_the_code(self) -> None:
        self._assert_invalid(
            "unknown ISO-4217 currency code 'ZYX'",
            mode="convert_presentation",
            amount=1,
            from_currency="USD",
            to_currency="zyx",
        )

    def test_convert_presentation_missing_amount(self) -> None:
        self._assert_invalid(
            "amount is required",
            mode="convert_presentation",
            from_currency="USD",
            to_currency="EUR",
        )


if __name__ == "__main__":
    unittest.main()
