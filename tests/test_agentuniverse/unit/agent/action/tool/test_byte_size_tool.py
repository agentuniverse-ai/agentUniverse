#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_byte_size_tool.py

"""Offline unit tests for ByteSizeTool.

The tool is built purely on the standard library (re, decimal) and never
touches the network, so this suite runs fully offline. Every assertion is
deterministic: parse results are checked against exact integer ground
truths for every supported unit (including the bit units, where the x/8
rule is asserted literally, e.g. 10kb = 10000 bits = 1250 bytes), the
format matrix covers both unit systems plus auto, precision and
trailing-zero trimming, convert results are checked against exact Decimal
quotients computed independently in this file, and the error matrix pins
down which failures raise ValueError (malformed parameters) versus which
return structured error payloads (unparsable content).
"""

import os
import unittest
from decimal import Decimal, localcontext

import yaml

from agentuniverse.agent.action.tool.common_tool import ByteSizeTool
from agentuniverse.agent.action.tool.common_tool.byte_size_tool import (
    ByteSizeTool as DirectByteSizeTool,
    _UNITS as UNIT_TABLE,
)

MAX_BYTES = 2**63 - 1


class ByteSizeToolParseTest(unittest.TestCase):
    """Offline deterministic parse-mode tests."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    # ------------------------------------------------------------------ #
    # Exact ground truths — every unit of the table
    # ------------------------------------------------------------------ #

    def test_parse_every_byte_unit_exact(self) -> None:
        cases = [
            ("512B", 512),
            ("512 B", 512),
            ("1 B", 1),
            ("10KB", 10_000),
            ("10kB", 10_000),
            ("2 kB", 2_000),
            ("1MB", 1_000_000),
            ("1mB", 1_000_000),
            ("1GB", 1_000_000_000),
            ("1gB", 1_000_000_000),
            ("1TB", 10**12),
            ("1tB", 10**12),
            ("1PB", 10**15),
            ("1pB", 10**15),
            ("1KiB", 1024),
            ("1MiB", 1024**2),
            ("1GiB", 1024**3),
            ("1TiB", 1024**4),
            ("1PiB", 1024**5),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(result["bytes"], expected)
                self.assertNotIn("error", result)

    def test_parse_bare_number_means_bytes(self) -> None:
        result = self.tool.execute(mode="parse", size="512")
        self.assertEqual(
            result,
            {
                "mode": "parse",
                "input": "512",
                "number": "512",
                "unit": None,
                "unit_kind": "bytes",
                "bytes": 512,
            },
        )

    def test_parse_fractional_values_that_stay_integral(self) -> None:
        cases = [
            ("1.5 KiB", 1536),
            ("0.5 KiB", 512),
            ("2.5 GiB", 2_684_354_560),
            ("1.5MiB", 1_572_864),
            ("0.5 GB", 500_000_000),
            ("1.5 kB", 1500),
            ("0.001 kB", 1),
            ("1.5 MB", 1_500_000),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(
                    self.tool.execute(mode="parse", size=text)["bytes"], expected
                )

    def test_parse_bit_units_divide_by_eight_exactly(self) -> None:
        # x/8 ground truth: 10kb = 10000 bits = 1250 bytes.
        cases = [
            ("10kb", 10_000, 1_250),
            ("10Kb", 10_000, 1_250),
            ("1kb", 1_000, 125),
            ("1.6 kb", 1_600, 200),
            ("0.008 kb", 8, 1),
            ("8b", 8, 1),
            ("64b", 8 * 8, 8),
            ("1Mb", 1_000_000, 125_000),
            ("1mb", 1_000_000, 125_000),
            ("1Gb", 10**9, 125_000_000),
            ("1Tb", 10**12, 125_000_000_000),
            ("1Pb", 10**15, 125_000_000_000_000),
            ("2 gb", 2 * 10**9, 250_000_000),
        ]
        for text, bits, expected_bytes in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(result["unit_kind"], "bits")
                self.assertEqual(result["bits"], bits)
                self.assertEqual(result["bytes"], expected_bytes)
                self.assertEqual(
                    result["note"], "bit unit: bits divided by 8 to bytes"
                )

    def test_parse_whitespace_and_sign_tolerated(self) -> None:
        cases = [
            "  10 KB  ", "10\tKB", "10  KB", " 10KB", "+5 B", "10 kb",
            "\t1.5 MiB\t",
        ]
        for text in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertNotIn("error", result)

    def test_parse_negative_requires_flag(self) -> None:
        result = self.tool.execute(mode="parse", size="-5 B")
        self.assertEqual(result["error"]["type"], "negative_not_allowed")
        self.assertIn("allow_negative", result["error"]["message"])
        allowed = self.tool.execute(
            mode="parse", size="-5 B", allow_negative=True
        )
        self.assertEqual(allowed["bytes"], -5)

    # ------------------------------------------------------------------ #
    # Content-level error payloads
    # ------------------------------------------------------------------ #

    def test_parse_unknown_unit_lists_valid_units(self) -> None:
        for text in ("1k", "1 q", "1 QB", "1 EB", "1 Ki", "1 bytes", "1KBs"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(result["error"]["type"], "invalid_unit")
                message = result["error"]["message"]
                for unit in ("B", "KB", "kB", "KiB", "MiB", "kb", "gb"):
                    self.assertIn(unit, message)

    def test_parse_binary_i_forms_are_case_sensitive(self) -> None:
        for text in ("1 KIB", "1 kib", "1 Kib", "1 kiB", "1 MIB", "1 mib"):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertIn(
                    result["error"]["type"],
                    ("invalid_unit", "invalid_size_string"),
                )

    def test_parse_malformed_syntax_rejected(self) -> None:
        for text in (
            "ten KB", "10..5 KB", "1,000 B", "1e3 B", ".5 B", "10.",
            "KB 10", "10 KB extra", "10 KB/s", "1 KiB 2", "-", "5..B",
        ):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(
                    result["error"]["type"], "invalid_size_string"
                )

    def test_parse_non_integer_bytes_rejected(self) -> None:
        cases = [
            ("0.5 B", "whole number of bytes"),
            ("1.5 b", "whole number of bits"),
            ("1.5 kb", "multiple of 8"),
            ("0.01 kb", "multiple of 8"),
            ("0.0000001 MiB", "whole number of bytes"),
            ("-1.5 B", "whole number of bytes"),
        ]
        for text, fragment in cases:
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(result["error"]["type"], "non_integer_bytes")
                self.assertIn(fragment, result["error"]["message"])

    def test_parse_bounds(self) -> None:
        at_bound = self.tool.execute(
            mode="parse", size="9223372036854775807 B"
        )
        self.assertEqual(at_bound["bytes"], MAX_BYTES)
        for text in (
            "9223372036854775808 B",
            "8192 PiB",
            "10000000000000000000 B",
        ):
            with self.subTest(text=text):
                result = self.tool.execute(mode="parse", size=text)
                self.assertEqual(result["error"]["type"], "out_of_range")
        below = self.tool.execute(mode="parse", size="8191 PiB")
        self.assertEqual(below["bytes"], 8191 * 1024**5)

    def test_parse_error_payload_shape(self) -> None:
        result = self.tool.execute(mode="parse", size="1k")
        self.assertEqual(result["mode"], "parse")
        self.assertEqual(result["input"], "1k")
        self.assertEqual(
            sorted(result["error"]), ["argument", "message", "type"]
        )


class ByteSizeToolFormatTest(unittest.TestCase):
    """Offline deterministic format-mode tests."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    # ------------------------------------------------------------------ #
    # Ground-truth matrix
    # ------------------------------------------------------------------ #

    def test_format_decimal_matrix(self) -> None:
        cases = [
            (0, "0 B", "B"),
            (1, "1 B", "B"),
            (999, "999 B", "B"),
            (1000, "1 KB", "KB"),
            (1500, "1.5 KB", "KB"),
            (999_999, "1 MB", "MB"),  # rounding carries into the next unit
            (1_000_000, "1 MB", "MB"),
            (1_500_000, "1.5 MB", "MB"),
            (10**9, "1 GB", "GB"),
            (10**12, "1 TB", "TB"),
            (10**15, "1 PB", "PB"),
            (MAX_BYTES, "9223.4 PB", "PB"),
        ]
        for value, expected, unit in cases:
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="format", value=value, system="decimal"
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["unit"], unit)
                self.assertEqual(result["system"], "decimal")
                self.assertEqual(result["bytes"], value)

    def test_format_binary_matrix(self) -> None:
        cases = [
            (1023, "1023 B", "B"),
            (1024, "1 KiB", "KiB"),
            (1536, "1.5 KiB", "KiB"),
            (1_048_575, "1 MiB", "MiB"),  # 1023.9995... rounds and carries
            (1_048_576, "1 MiB", "MiB"),
            (1024**3, "1 GiB", "GiB"),
            (1024**4, "1 TiB", "TiB"),
            (1024**5, "1 PiB", "PiB"),
        ]
        for value, expected, unit in cases:
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="format", value=value, system="binary"
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["unit"], unit)

    def test_format_auto_resolves_to_decimal(self) -> None:
        for value in (0, 1, 999, 1000, 1500, 1024, 1536, 999_999, 10**9):
            with self.subTest(value=value):
                auto = self.tool.execute(mode="format", value=value)
                decimal_result = self.tool.execute(
                    mode="format", value=value, system="decimal"
                )
                self.assertEqual(auto["result"], decimal_result["result"])
                self.assertEqual(auto["system"], "auto")
        # The binary reading is available only explicitly: 1536 is
        # "1.5 KB" under auto/decimal but "1.5 KiB" under binary.
        self.assertEqual(
            self.tool.execute(mode="format", value=1536)["result"], "1.5 KB"
        )
        self.assertEqual(
            self.tool.execute(mode="format", value=1536, system="binary")[
                "result"
            ],
            "1.5 KiB",
        )
        # Half-up rounding at precision 0 in the binary system.
        self.assertEqual(
            self.tool.execute(
                mode="format", value=1536, system="binary", precision=0
            )["result"],
            "2 KiB",
        )

    def test_format_precision_and_trailing_zero_trim(self) -> None:
        cases = [
            (1500, None, "1.5 KB"),  # default precision 1, no trailing zero
            (1500, 2, "1.5 KB"),  # "1.50" is trimmed to "1.5"
            (1200, 2, "1.2 KB"),
            (1100, 2, "1.1 KB"),
            (1000, 3, "1 KB"),
            (1048576, 1, "1 MB"),
            (1048576, 2, "1.05 MB"),
            (1048576, 6, "1.048576 MB"),
            (1024, 3, "1.024 KB"),
            (1536, 0, "2 KB"),  # 1.5 rounds half-up to 2 (auto = decimal)
        ]
        for value, precision, expected in cases:
            with self.subTest(value=value, precision=precision):
                result = self.tool.execute(
                    mode="format", value=value, precision=precision
                )
                self.assertEqual(result["result"], expected)
                self.assertNotIn(
                    ".0 ", result["result"] + " "
                )  # never "1.0 KB"

    def test_format_rounding_is_half_up(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="format", value=1500, precision=0)[
                "result"
            ],
            "2 KB",
        )
        self.assertEqual(
            self.tool.execute(mode="format", value=2500, precision=0)[
                "result"
            ],
            "3 KB",
        )
        self.assertEqual(
            self.tool.execute(mode="format", value=1250, precision=0)[
                "result"
            ],
            "1 KB",
        )

    def test_format_bits_strings(self) -> None:
        cases = [
            (0, "0 b", "b"),
            (1, "8 b", "b"),
            (8, "64 b", "b"),
            (124, "992 b", "b"),
            (125, "1 kb", "kb"),
            (1250, "10 kb", "kb"),  # inverse of the parse ground truth
            (125_000, "1 Mb", "Mb"),
            (125_000_000, "1 Gb", "Gb"),
            (125_000_000_000, "1 Tb", "Tb"),
            (125_000_000_000_000, "1 Pb", "Pb"),
        ]
        for value, expected, unit in cases:
            with self.subTest(value=value):
                result = self.tool.execute(
                    mode="format", value=value, as_bits=True
                )
                self.assertEqual(result["result"], expected)
                self.assertEqual(result["unit"], unit)
                self.assertTrue(result["as_bits"])

    def test_format_accepts_digit_string_values(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="format", value="1500")["result"], "1.5 KB"
        )
        self.assertEqual(
            self.tool.execute(
                mode="format", value="+2048", precision=3
            )["result"],
            "2.048 KB",
        )
        self.assertEqual(
            self.tool.execute(mode="format", value="0")["result"], "0 B"
        )

    def test_format_parse_round_trip(self) -> None:
        # Any formatted output must parse back to the same byte count as
        # long as the precision is high enough for the value.
        cases = [
            (123_456_789, "decimal", 6),
            (1536, "binary", 1),
            (1_048_576, "binary", 6),
            (987_654_000, "decimal", 3),
            (1250, None, 1),  # None -> as_bits round trip
        ]
        for value, system, precision in cases:
            with self.subTest(value=value, system=system):
                if system is None:
                    formatted = self.tool.execute(
                        mode="format", value=value, precision=precision,
                        as_bits=True,
                    )
                else:
                    formatted = self.tool.execute(
                        mode="format", value=value, system=system,
                        precision=precision,
                    )
                reparsed = self.tool.execute(
                    mode="parse", size=formatted["result"]
                )
                self.assertNotIn("error", reparsed)
                self.assertEqual(reparsed["bytes"], value)

    # ------------------------------------------------------------------ #
    # Parameter validation raises ValueError
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_format_invalid_values(self) -> None:
        for bad in (-1, -100, 1.5, True, None, "abc", "1e3", "1.5", [1024]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="format", value=bad)

    def test_format_value_bound(self) -> None:
        self.assert_invalid(mode="format", value=2**63)
        self.assert_invalid(mode="format", value=str(2**63))
        ok = self.tool.execute(mode="format", value=MAX_BYTES)
        self.assertEqual(ok["result"], "9223.4 PB")

    def test_format_invalid_options(self) -> None:
        self.assert_invalid(mode="format", value=1, system="si")
        self.assert_invalid(mode="format", value=1, system="nonsense")
        for bad_precision in (-1, 10, 2.5, True, "1"):
            with self.subTest(bad_precision=bad_precision):
                self.assert_invalid(
                    mode="format", value=1, precision=bad_precision
                )
        self.assert_invalid(mode="format", value=1, as_bits="yes")
        self.assert_invalid(
            mode="format", value=1, as_bits=True, system="binary"
        )


class ByteSizeToolConvertTest(unittest.TestCase):
    """Offline deterministic convert-mode tests."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    def test_convert_mib_to_mb_exact_decimal(self) -> None:
        # Ground truth: 10 MiB = 10485760 B = 10.48576 MB exactly.
        result = self.tool.execute(
            mode="convert", size="10 MiB", target_unit="MB"
        )
        self.assertEqual(result["mode"], "convert")
        self.assertEqual(result["source_unit"], "MiB")
        self.assertEqual(result["source_bytes"], 10_485_760)
        self.assertEqual(result["target_unit"], "MB")
        self.assertEqual(result["result"], "10.48576")
        self.assertTrue(result["exact"])
        self.assertEqual(result["value"], 10.48576)
        # The float cannot represent 10.48576 exactly — a note must say so.
        self.assertIn("nearest binary float", result["note"])

    def test_convert_mb_to_mib_exact(self) -> None:
        result = self.tool.execute(
            mode="convert", size="10 MB", target_unit="MiB"
        )
        self.assertEqual(result["result"], "9.5367431640625")
        self.assertTrue(result["exact"])

    def test_convert_identity_and_whole_results_have_no_note(self) -> None:
        result = self.tool.execute(
            mode="convert", size="512 B", target_unit="B"
        )
        self.assertEqual(result["result"], "512")
        self.assertEqual(result["value"], 512.0)
        self.assertNotIn("note", result)
        result = self.tool.execute(
            mode="convert", size="1 kB", target_unit="B"
        )
        self.assertEqual(result["result"], "1000")
        self.assertNotIn("note", result)
        result = self.tool.execute(
            mode="convert", size="1024 B", target_unit="KiB"
        )
        self.assertEqual(result["result"], "1")
        self.assertNotIn("note", result)

    def test_convert_small_value_to_big_unit_inexact_float(self) -> None:
        result = self.tool.execute(
            mode="convert", size="1 B", target_unit="KB"
        )
        self.assertEqual(result["result"], "0.001")
        self.assertTrue(result["exact"])
        self.assertIn("nearest binary float", result["note"])

    def test_convert_to_bit_units(self) -> None:
        result = self.tool.execute(
            mode="convert", size="10 MiB", target_unit="kb"
        )
        self.assertEqual(result["result"], "83886.08")
        self.assertTrue(result["exact"])
        result = self.tool.execute(
            mode="convert", size="10kb", target_unit="B"
        )
        self.assertEqual(result["result"], "1250")
        self.assertEqual(result["source_bytes"], 1250)

    def test_convert_extreme_ratio_stays_exact(self) -> None:
        # 1 / 2^50 terminates in decimal within 100 significant digits.
        with localcontext() as context:
            context.prec = 100
            expected_quotient = Decimal(1) / Decimal(1024**5)
        result = self.tool.execute(
            mode="convert", size="1 B", target_unit="PiB"
        )
        self.assertTrue(result["exact"])
        self.assertNotIn("E", result["result"])  # never scientific notation
        self.assertEqual(Decimal(result["result"]), expected_quotient)

    def test_convert_matches_independent_decimal_arithmetic(self) -> None:
        cases = [
            ("1.5 KiB", "B"),
            ("1.5 KiB", "kB"),
            ("999999 B", "MB"),
            ("3 TB", "GiB"),
            ("7 GiB", "gb"),
            ("2.5 MiB", "KiB"),
        ]
        for size, target_unit in cases:
            with self.subTest(size=size, target_unit=target_unit):
                parsed = self.tool.execute(mode="parse", size=size)
                multiplier = UNIT_TABLE[target_unit][1]
                if UNIT_TABLE[target_unit][0] == "bits":
                    numerator = Decimal(parsed["bytes"] * 8)
                else:
                    numerator = Decimal(parsed["bytes"])
                with localcontext() as context:
                    context.prec = 100
                    expected_quotient = numerator / Decimal(multiplier)
                cleaned = expected_quotient.normalize()
                if cleaned.as_tuple().exponent > 0:
                    cleaned = cleaned.quantize(Decimal(1))
                result = self.tool.execute(
                    mode="convert", size=size, target_unit=target_unit
                )
                self.assertEqual(result["result"], str(cleaned))
                self.assertTrue(result["exact"])

    def test_convert_negative_requires_flag(self) -> None:
        blocked = self.tool.execute(
            mode="convert", size="-1 KB", target_unit="B"
        )
        self.assertEqual(blocked["error"]["type"], "negative_not_allowed")
        allowed = self.tool.execute(
            mode="convert", size="-1 KB", target_unit="B", allow_negative=True
        )
        self.assertEqual(allowed["result"], "-1000")

    def test_convert_invalid_target_unit_raises(self) -> None:
        for bad in ("EB", "kib", "Ki", "", None, 123):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self.tool.execute(
                        mode="convert", size="1 B", target_unit=bad
                    )

    def test_convert_bad_source_returns_payload(self) -> None:
        result = self.tool.execute(
            mode="convert", size="1k", target_unit="MB"
        )
        self.assertEqual(result["mode"], "convert")
        self.assertEqual(result["error"]["type"], "invalid_unit")


class ByteSizeToolCompareTest(unittest.TestCase):
    """Offline deterministic compare-mode tests."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    def test_compare_equal_decimal_forms(self) -> None:
        result = self.tool.execute(
            mode="compare", size_a="10MB", size_b="10000000B"
        )
        self.assertEqual(
            result,
            {
                "mode": "compare",
                "a": {
                    "input": "10MB",
                    "number": "10",
                    "unit": "MB",
                    "unit_kind": "decimal",
                    "bytes": 10_000_000,
                },
                "b": {
                    "input": "10000000B",
                    "number": "10000000",
                    "unit": "B",
                    "unit_kind": "bytes",
                    "bytes": 10_000_000,
                },
                "equal": True,
                "relation": "a == b",
            },
        )

    def test_compare_kib_is_not_kb(self) -> None:
        result = self.tool.execute(
            mode="compare", size_a="1 KiB", size_b="1000 B"
        )
        self.assertFalse(result["equal"])
        self.assertEqual(result["relation"], "a > b")

    def test_compare_bits_equal_bytes(self) -> None:
        result = self.tool.execute(
            mode="compare", size_a="1kb", size_b="125B"
        )
        self.assertTrue(result["equal"])
        result = self.tool.execute(
            mode="compare", size_a="0.5 GiB", size_b="536870912B"
        )
        self.assertTrue(result["equal"])

    def test_compare_ordering(self) -> None:
        result = self.tool.execute(
            mode="compare", size_a="1 kB", size_b="999 B"
        )
        self.assertFalse(result["equal"])
        self.assertEqual(result["relation"], "a > b")
        result = self.tool.execute(
            mode="compare", size_a="999 B", size_b="1 kB"
        )
        self.assertEqual(result["relation"], "a < b")

    def test_compare_negative_with_flag(self) -> None:
        blocked = self.tool.execute(
            mode="compare", size_a="-1 B", size_b="0 B"
        )
        self.assertEqual(blocked["error"]["type"], "negative_not_allowed")
        self.assertEqual(blocked["error"]["argument"], "size_a")
        allowed = self.tool.execute(
            mode="compare",
            size_a="-1 B",
            size_b="0 B",
            allow_negative=True,
        )
        self.assertEqual(allowed["relation"], "a < b")

    def test_compare_bad_input_reports_argument(self) -> None:
        result = self.tool.execute(mode="compare", size_a="1k", size_b="1 B")
        self.assertEqual(result["error"]["argument"], "size_a")
        result = self.tool.execute(mode="compare", size_a="1 B", size_b="1k")
        self.assertEqual(result["error"]["argument"], "size_b")


class ByteSizeToolValidationTest(unittest.TestCase):
    """Parameter-level validation raises ValueError before any work."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        for bad in ("parse!", None, 123, "PARSE"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode=bad)

    def test_size_argument_type_and_emptiness(self) -> None:
        for bad in (None, "", "   ", 123, True, ["10KB"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="parse", size=bad)
        self.assert_invalid(mode="convert", size=None, target_unit="MB")
        self.assert_invalid(mode="compare", size_a="1 B", size_b=None)
        self.assert_invalid(mode="compare", size_a="", size_b="1 B")

    def test_oversized_size_string_rejected(self) -> None:
        self.assert_invalid(mode="parse", size="1" + "0" * 300)

    def test_allow_negative_must_be_boolean(self) -> None:
        for bad in ("yes", 1, 0):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="parse", size="1 B", allow_negative=bad
                )


class ByteSizeToolPackagingTest(unittest.TestCase):
    """Registration, defaults and YAML wiring."""

    def setUp(self) -> None:
        self.tool = ByteSizeTool()

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectByteSizeTool, ByteSizeTool)
        self.assertEqual(self.tool.name, "byte_size_tool")
        self.assertIn("parse", self.tool.description)
        self.assertIn("format", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ByteSizeTool", __all__)

    def test_yaml_wiring(self) -> None:
        import agentuniverse.agent.action.tool.common_tool as package

        yaml_path = os.path.join(
            os.path.dirname(package.__file__), "byte_size_tool.yaml"
        )
        self.assertTrue(os.path.exists(yaml_path), yaml_path)
        with open(yaml_path, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "byte_size_tool")
        self.assertEqual(config["metadata"]["class"], "ByteSizeTool")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.byte_size_tool",
        )
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertIn("mode", config["args_model_schema"]["properties"])
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["parse", "format", "convert", "compare"],
        )


if __name__ == "__main__":
    unittest.main()
