#!/usr/bin/env python3

# @Time    : 2026/10/06
# @FileName: test_number_formatter_tool.py

"""Tests for NumberFormatterTool."""

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import number_formatter_tool as module
from agentuniverse.agent.action.tool.common_tool.number_formatter_tool import (
    NumberFormatterTool,
)

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "number_formatter_tool.yaml")


class NumberFormatterToolFormatTest(unittest.TestCase):
    """mode=format: separators, decimals, prefix/suffix, currency."""

    def setUp(self):
        self.tool = NumberFormatterTool()

    def test_thousands_separator(self):
        result = self.tool.execute(mode="format", value=1234567.891, decimals=2)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["formatted"], "1,234,567.89")

    def test_separator_disabled(self):
        result = self.tool.execute(
            mode="format", value=1234567.891, decimals=2, thousands_separator=False)
        self.assertEqual(result["formatted"], "1234567.89")

    def test_decimals_pad_and_round(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=3.14159, decimals=3)["formatted"],
            "3.142")
        self.assertEqual(
            self.tool.execute(mode="format", value=2.5, decimals=3)["formatted"],
            "2.500")
        self.assertEqual(
            self.tool.execute(mode="format", value=42, decimals=0)["formatted"], "42")

    def test_natural_digits_without_decimals(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=9876543)["formatted"], "9,876,543")

    def test_negative_sign_placement(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=-1234.5, decimals=1)["formatted"],
            "-1,234.5")

    def test_prefix_suffix_and_currency(self):
        result = self.tool.execute(
            mode="format", value=1234.5678, decimals=2,
            prefix="Total: ", suffix=" USD due", currency="usd")
        self.assertEqual(result["formatted"], "Total: $1,234.57 USD due")
        self.assertEqual(result["currency"], "usd")

    def test_currency_sign_before_magnitude(self):
        self.assertEqual(
            self.tool.execute(
                mode="format", value=-95.5, decimals=1, currency="cny")["formatted"],
            "-¥95.5")

    def test_numeric_string_with_commas(self):
        result = self.tool.execute(mode="format", value="1,234,567.89", decimals=2)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["formatted"], "1,234,567.89")

    def test_currency_validation_error(self):
        result = self.tool.execute(mode="format", value=1, currency="zzz")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")


class NumberFormatterToolFileSizeTest(unittest.TestCase):
    """mode=file_size: bytes to human-readable sizes."""

    def setUp(self):
        self.tool = NumberFormatterTool()

    def test_binary_auto_units(self):
        self.assertEqual(
            self.tool.execute(mode="file_size", value=999)["formatted"], "999 B")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1024)["formatted"], "1 KB")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1536)["formatted"], "1.5 KB")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1024**3)["formatted"], "1 GB")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1024**5)["formatted"], "1 PB")

    def test_decimal_system_uses_1000_step(self):
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1000, system="decimal")[
                "formatted"], "1 KB")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1500, system="decimal")[
                "formatted"], "1.5 KB")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1024, system="decimal")[
                "formatted"], "1.02 KB")

    def test_trailing_zeros_stripped(self):
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1024 * 1024)["formatted"],
            "1 MB")

    def test_forced_unit(self):
        result = self.tool.execute(mode="file_size", value=1024**3, unit="MB")
        self.assertEqual(result["formatted"], "1,024 MB")
        self.assertEqual(result["unit"], "MB")

    def test_zero_and_zero_bytes(self):
        self.assertEqual(
            self.tool.execute(mode="file_size", value=0)["formatted"], "0 B")

    def test_negative_and_bad_unit_rejected(self):
        self.assertEqual(
            self.tool.execute(mode="file_size", value=-1)["status"], "error")
        self.assertEqual(
            self.tool.execute(mode="file_size", value=1, unit="XB")["status"],
            "error")


class NumberFormatterToolDurationTest(unittest.TestCase):
    """mode=duration: seconds to human-readable durations."""

    def setUp(self):
        self.tool = NumberFormatterTool()

    def test_compound_compact(self):
        # 1 week + 2 days + 3 hours + 4 minutes + 5 seconds
        total = 7 * 86400 + 2 * 86400 + 3 * 3600 + 4 * 60 + 5
        result = self.tool.execute(mode="duration", value=total)
        self.assertEqual(result["formatted"], "1w 2d 3h 4m 5s")
        self.assertEqual(result["breakdown"]["hours"], 3)

    def test_simple_compact(self):
        self.assertEqual(
            self.tool.execute(mode="duration", value=90)["formatted"], "1m 30s")
        self.assertEqual(
            self.tool.execute(mode="duration", value=3661)["formatted"],
            "1h 1m 1s")

    def test_verbose_pluralisation(self):
        total = 2 * 86400 + 3 * 3600
        result = self.tool.execute(mode="duration", value=total, style="verbose")
        self.assertEqual(result["formatted"], "2 days, 3 hours")
        result = self.tool.execute(mode="duration", value=86400, style="verbose")
        self.assertEqual(result["formatted"], "1 day")

    def test_subsecond(self):
        self.assertEqual(
            self.tool.execute(mode="duration", value=1.5)["formatted"], "1.5s")
        self.assertEqual(
            self.tool.execute(mode="duration", value=0.25, style="verbose")[
                "formatted"], "0.25 seconds")

    def test_zero(self):
        self.assertEqual(
            self.tool.execute(mode="duration", value=0)["formatted"], "0s")
        self.assertEqual(
            self.tool.execute(mode="duration", value=0, style="verbose")[
                "formatted"], "0 seconds")

    def test_negative_rejected(self):
        self.assertEqual(
            self.tool.execute(mode="duration", value=-5)["status"], "error")


class NumberFormatterToolPercentageScientificTest(unittest.TestCase):
    """mode=percentage and mode=scientific."""

    def setUp(self):
        self.tool = NumberFormatterTool()

    def test_percentage_default_one_decimal(self):
        self.assertEqual(
            self.tool.execute(mode="percentage", value=0.1234)["formatted"],
            "12.3%")

    def test_percentage_decimals_and_separator(self):
        self.assertEqual(
            self.tool.execute(mode="percentage", value=0.123456, decimals=3)[
                "formatted"], "12.346%")
        result = self.tool.execute(
            mode="percentage", value=123.4567, decimals=1, thousands_separator=False)
        self.assertEqual(result["formatted"], "12345.7%")
        self.assertEqual(result["percent_value"], 12345.7)

    def test_percentage_negative(self):
        self.assertEqual(
            self.tool.execute(mode="percentage", value=-0.05)["formatted"], "-5.0%")

    def test_scientific(self):
        result = self.tool.execute(mode="scientific", value=1234567)
        self.assertEqual(result["formatted"], "1.234567e+06")
        self.assertEqual(result["mantissa"], 1.234567)
        self.assertEqual(result["exponent"], 6)

    def test_scientific_decimals(self):
        self.assertEqual(
            self.tool.execute(mode="scientific", value=0.00025, decimals=2)[
                "formatted"], "2.50e-04")

    def test_scientific_zero(self):
        result = self.tool.execute(mode="scientific", value=0)
        self.assertEqual(result["exponent"], 0)
        self.assertEqual(result["mantissa"], 0.0)


class NumberFormatterToolValidationTest(unittest.TestCase):
    """Shared argument validation and error envelope."""

    def setUp(self):
        self.tool = NumberFormatterTool()

    def test_unknown_mode(self):
        result = self.tool.execute(mode="nope", value=1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unsupported mode", result["error"])

    def test_non_numeric_value(self):
        result = self.tool.execute(mode="format", value="abc")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")

    def test_boolean_and_none_rejected(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=True)["status"], "error")
        self.assertEqual(
            self.tool.execute(mode="format", value=None)["status"], "error")

    def test_nan_and_infinity_rejected(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=float("nan"))["status"], "error")
        self.assertEqual(
            self.tool.execute(mode="format", value=float("inf"))["status"], "error")

    def test_magnitude_ceiling(self):
        result = self.tool.execute(mode="format", value=10**19)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_abs_value", result["error"])

    def test_decimals_bounds(self):
        self.assertEqual(
            self.tool.execute(mode="format", value=1, decimals=-1)["status"],
            "error")
        self.assertEqual(
            self.tool.execute(mode="format", value=1, decimals=16)["status"],
            "error")

    def test_yaml_exists_and_declares_component(self):
        self.assertTrue(os.path.isfile(YAML_PATH))
        with open(YAML_PATH, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("class: NumberFormatterTool", content)
        self.assertIn(
            "module: agentuniverse.agent.action.tool.common_tool."
            "number_formatter_tool", content)


if __name__ == "__main__":
    unittest.main()
