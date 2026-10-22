#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_basen_encode_tool.py

"""Offline unit tests for BaseNEncodeTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: encodings are checked against literal known vectors and
against an independent in-test reference implementation (plus CPython's
own ``format(n, 'b'/'o'/'x')`` and ``int(s, base)`` oracles), and the
validation paths are checked against an explicit error matrix of
``ValueError`` raises and structured ``error`` payloads.
"""

import os
import sys
import unittest

import yaml

from agentuniverse.agent.action.tool.common_tool import BaseNEncodeTool
from agentuniverse.agent.action.tool.common_tool.basen_encode_tool import (
    BaseNEncodeTool as DirectBaseNEncodeTool,
)

# --------------------------------------------------------------------- #
# Independent reference implementation (oracle for the fuzz-style checks)
# --------------------------------------------------------------------- #
STD_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def reference_encode(number: int, base: int, alphabet: str = STD_ALPHABET) -> str:
    """Independent repeated-division encoder written only for this test."""
    if number == 0:
        return alphabet[0]
    chars = []
    while number:
        number, digit = divmod(number, base)
        chars.append(alphabet[digit])
    return "".join(reversed(chars))


# Fixed value spread: small boundary values, powers of two, big ints.
FUZZ_VALUES = [
    0,
    1,
    2,
    7,
    8,
    15,
    16,
    35,
    36,
    49,
    50,
    255,
    256,
    1023,
    1024,
    65535,
    65536,
    2**31,
    2**32 - 1,
    2**63,
    2**64,
    123456789012345678901234567890,
    2**255 - 1,
    2**256,
    2**1024 - 1,
    10**500,
]

# Literal known vectors (ground truths, not computed).
HEX_255 = "ff"
BIN_255 = "11111111"
OCT_255 = "377"
B36_35 = "z"
B36_36 = "10"
B36_1295 = "zz"
# 2**256 = 1 followed by 64 zero bits -> hex '1' + 64 '0', binary '1' + 256 '0'.
HEX_2_256 = "1" + "0" * 64
BIN_2_256 = "1" + "0" * 256
# 2**256 = 2 * 8**85 -> octal '2' followed by 85 '0'.
OCT_2_256 = "2" + "0" * 85
DEC_10_POW_10000 = "1" + "0" * 10000

CAP = 10**10000


class BaseNEncodeToolKnownVectorTest(unittest.TestCase):
    """Literal ground-truth vectors for encode / decode / convert."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_encode_known_vectors(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base=16),
            {"mode": "encode", "base": 16, "result": HEX_255, "digit_count": 2},
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base=2),
            {"mode": "encode", "base": 2, "result": BIN_255, "digit_count": 8},
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base=8)["result"],
            OCT_255,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base=10)["result"],
            "255",
        )

    def test_decode_known_vectors(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", value=HEX_255, base=16),
            {
                "mode": "decode",
                "base": 16,
                "result": 255,
                "digit_count": 2,
                "negative": False,
            },
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=BIN_255, base=2)["result"], 255
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=OCT_255, base=8)["result"], 255
        )

    def test_encode_string_value(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value="255", base=16)["result"],
            HEX_255,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value="+255", base=16)["result"],
            HEX_255,
        )

    def test_base_defaults_to_ten_for_encode(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=255),
            {"mode": "encode", "base": 10, "result": "255", "digit_count": 3},
        )

    def test_base36_boundary_values(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=35, base=36)["result"], B36_35
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=B36_35, base=36)["result"], 35
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=36, base=36)["result"], B36_36
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=B36_36, base=36)["result"], 36
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=36**2 - 1, base=36)["result"],
            B36_1295,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=36**3 - 1, base=36)["result"],
            "zzz",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=36**3, base=36)["result"],
            "1000",
        )

    def test_power_of_two_literals(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=2**256, base=16)["result"],
            HEX_2_256,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=2**256, base=2)["result"],
            BIN_2_256,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=2**256, base=8)["result"],
            OCT_2_256,
        )

    def test_power_of_two_decodes(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", value=HEX_2_256, base=16)["result"],
            2**256,
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=BIN_2_256, base=2)["result"],
            2**256,
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=OCT_2_256, base=8)["result"],
            2**256,
        )

    def test_binary_hex_octal_cross_conversions(self) -> None:
        # 0b101101001 -> 0x169 -> 0o551 -> back.
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="101101001", from_base=2, to_base=16
            )["result"],
            "169",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="169", from_base=16, to_base=8
            )["result"],
            "551",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="551", from_base=8, to_base=2
            )["result"],
            "101101001",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value=BIN_255, from_base=2, to_base=16
            )["result"],
            HEX_255,
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value=BIN_255, from_base=2, to_base=8
            )["result"],
            OCT_255,
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value=HEX_2_256, from_base=16, to_base=2
            )["result"],
            BIN_2_256,
        )

    def test_convert_result_shape(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="ff", from_base=16, to_base=2
            ),
            {
                "mode": "convert",
                "from_base": 16,
                "to_base": 2,
                "value": 255,
                "result": BIN_255,
                "digit_count": 8,
            },
        )

    def test_zero_round_trips_everywhere(self) -> None:
        for base in range(2, 37):
            encoded = self.tool.execute(mode="encode", value=0, base=base)["result"]
            self.assertEqual(encoded, STD_ALPHABET[0])
            self.assertEqual(
                self.tool.execute(mode="decode", value=encoded, base=base)["result"],
                0,
            )

    def test_uppercase_decode_is_case_insensitive(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", value="FF", base=16)["result"], 255
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="aBcDeF", base=16)["result"],
            0xABCDEF,
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="Zz", base=36)["result"], 35 * 36 + 35
        )

    def test_leading_zeros_are_int_semantics(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", value="00ff", base=16)["result"], 255
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="000", base=2)["result"], 0
        )


class BaseNEncodeToolOracleTest(unittest.TestCase):
    """Compare the tool against independent reference implementations."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_encode_matches_reference_all_bases(self) -> None:
        for number in FUZZ_VALUES:
            for base in range(2, 37):
                self.assertEqual(
                    self.tool.execute(mode="encode", value=number, base=base)[
                        "result"
                    ],
                    reference_encode(number, base),
                    f"value={number} base={base}",
                )

    def test_encode_matches_cpython_format(self) -> None:
        for number in FUZZ_VALUES:
            self.assertEqual(
                self.tool.execute(mode="encode", value=number, base=2)["result"],
                format(number, "b"),
            )
            self.assertEqual(
                self.tool.execute(mode="encode", value=number, base=8)["result"],
                format(number, "o"),
            )
            self.assertEqual(
                self.tool.execute(mode="encode", value=number, base=16)["result"],
                format(number, "x"),
            )

    def test_decode_matches_int_semantics(self) -> None:
        for number in FUZZ_VALUES:
            for base in (2, 8, 10, 16, 36):
                digits = reference_encode(number, base)
                self.assertEqual(
                    self.tool.execute(mode="decode", value=digits, base=base)[
                        "result"
                    ],
                    int(digits, base),
                    f"value={number} base={base}",
                )

    def test_round_trip_all_bases(self) -> None:
        for number in FUZZ_VALUES:
            for base in range(2, 37):
                digits = self.tool.execute(mode="encode", value=number, base=base)[
                    "result"
                ]
                self.assertEqual(
                    self.tool.execute(mode="decode", value=digits, base=base)[
                        "result"
                    ],
                    number,
                    f"value={number} base={base}",
                )

    def test_2_pow_256_round_trips(self) -> None:
        for base in (2, 8, 10, 16, 32, 36):
            digits = self.tool.execute(mode="encode", value=2**256, base=base)[
                "result"
            ]
            self.assertEqual(
                self.tool.execute(mode="decode", value=digits, base=base)["result"],
                2**256,
            )

    def test_convert_matches_two_step(self) -> None:
        for number in FUZZ_VALUES:
            for from_base, to_base in ((10, 16), (16, 36), (2, 10), (36, 8), (16, 16)):
                source = reference_encode(number, from_base)
                direct = self.tool.execute(
                    mode="convert", value=source, from_base=from_base, to_base=to_base
                )
                self.assertEqual(
                    direct["value"],
                    number,
                    f"value={number} {from_base}->{to_base}",
                )
                self.assertEqual(
                    direct["result"],
                    reference_encode(number, to_base),
                    f"value={number} {from_base}->{to_base}",
                )

    def test_convert_uppercase_normalizes(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="FF", from_base=16, to_base=16
            )["result"],
            HEX_255,
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="aBcDeF", from_base=16, to_base=16
            )["result"],
            "abcdef",
        )

    def test_convert_negative_value(self) -> None:
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="-ff", from_base=16, to_base=10
            ),
            {
                "mode": "convert",
                "from_base": 16,
                "to_base": 10,
                "value": -255,
                "result": "-255",
                "digit_count": 3,
            },
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value="-ff", from_base=16, to_base=16
            )["result"],
            "-ff",
        )


class BaseNEncodeToolAlphabetTest(unittest.TestCase):
    """Custom alphabet support for encode / decode."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_custom_binary_alphabet(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=5, base=2, alphabet="ox"),
            {"mode": "encode", "base": 2, "result": "xox", "digit_count": 3},
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=0, base=2, alphabet="ox")["result"],
            "o",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=7, base=2, alphabet="ox")["result"],
            "xxx",
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="xox", base=2, alphabet="ox")[
                "result"
            ],
            5,
        )

    def test_reversed_alphabet(self) -> None:
        alphabet = "ZYXWVUTSRQPONMLKJIHGFEDCBA"
        self.assertEqual(
            self.tool.execute(mode="encode", value=0, base=26, alphabet=alphabet)[
                "result"
            ],
            "Z",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=25, base=26, alphabet=alphabet)[
                "result"
            ],
            "A",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=26, base=26, alphabet=alphabet)[
                "result"
            ],
            "YZ",
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="YZ", base=26, alphabet=alphabet)[
                "result"
            ],
            26,
        )
        for number in (7, 12345, 26**5 + 17):
            digits = self.tool.execute(
                mode="encode", value=number, base=26, alphabet=alphabet
            )["result"]
            self.assertEqual(
                self.tool.execute(
                    mode="decode", value=digits, base=26, alphabet=alphabet
                )["result"],
                number,
            )

    def test_custom_alphabet_matches_reference(self) -> None:
        alphabet = "abcdefghij"  # base 10 with letters
        for number in (0, 5, 99, 1023, 987654321, 10**50):
            self.assertEqual(
                self.tool.execute(
                    mode="encode", value=number, base=10, alphabet=alphabet
                )["result"],
                reference_encode(number, 10, alphabet),
            )

    def test_custom_alphabet_decode_is_case_sensitive(self) -> None:
        result = self.tool.execute(mode="decode", value="ab", base=2, alphabet="ox")
        self.assertEqual(result["error"]["type"], "invalid_digit")
        self.assertIn("position 0", result["error"]["message"])
        result = self.tool.execute(mode="decode", value="AB", base=2, alphabet="ab")
        self.assertEqual(result["error"]["type"], "invalid_digit")

    def test_custom_alphabet_whitespace_digit_rejected(self) -> None:
        # A space between digits is still an invalid char, position 1.
        result = self.tool.execute(mode="decode", value="o x", base=2, alphabet="ox")
        self.assertEqual(result["error"]["type"], "invalid_digit")
        self.assertIn("position 1", result["error"]["message"])

    def test_bad_alphabets_raise(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="encode", value=1, base=2, alphabet="abc")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="encode", value=1, base=16, alphabet="00")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="encode", value=1, base=2, alphabet=" o")
        with self.assertRaises(ValueError):
            self.tool.execute(mode="encode", value=1, base=10, alphabet=12345)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="decode", value="1", base=2, alphabet=True)


class BaseNEncodeToolPrefixTest(unittest.TestCase):
    """Prefix option: prepend on encode, require-and-strip on decode."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_encode_prefix(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base=16, prefix="0x"),
            {
                "mode": "encode",
                "base": 16,
                "prefix": "0x",
                "result": "0xff",
                "digit_count": 2,
            },
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=5, base=2, prefix="0b")["result"],
            "0b101",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=8, base=8, prefix="0o")["result"],
            "0o10",
        )

    def test_prefix_round_trip(self) -> None:
        for prefix, base in (("0x", 16), ("0b", 2), ("0o", 8), ("#", 36)):
            number = 2**128 + 12345
            encoded = self.tool.execute(
                mode="encode", value=number, base=base, prefix=prefix
            )["result"]
            self.assertTrue(encoded.startswith(prefix))
            decoded = self.tool.execute(
                mode="decode", value=encoded, base=base, prefix=prefix
            )
            self.assertEqual(decoded["result"], number)
            self.assertEqual(decoded["digit_count"], len(encoded) - len(prefix))

    def test_decode_requires_prefix_when_given(self) -> None:
        result = self.tool.execute(mode="decode", value="ff", base=16, prefix="0x")
        self.assertEqual(result["error"]["type"], "prefix_mismatch")

    def test_decode_without_prefix_option_rejects_prefix_chars(self) -> None:
        # 'x' is not a base-16 digit, so '0xff' fails at position 1.
        result = self.tool.execute(mode="decode", value="0xff", base=16)
        self.assertEqual(result["error"]["type"], "invalid_digit")
        self.assertIn("position 1", result["error"]["message"])
        self.assertIn("'x'", result["error"]["message"])

    def test_decode_prefix_then_invalid_digit_position(self) -> None:
        result = self.tool.execute(
            mode="decode", value="0xzz", base=16, prefix="0x"
        )
        self.assertEqual(result["error"]["type"], "invalid_digit")
        self.assertIn("position 2", result["error"]["message"])

    def test_bad_prefixes_raise(self) -> None:
        for prefix in ("", " ", "0 x", "€", "0x\t"):
            with self.assertRaises(ValueError):
                self.tool.execute(mode="encode", value=1, base=2, prefix=prefix)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="encode", value=1, base=2, prefix=16)


class BaseNEncodeToolValidationTest(unittest.TestCase):
    """Parameter-level ValueError matrix."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_unknown_mode(self) -> None:
        self.assert_invalid(mode="bogus", value="1")
        self.assert_invalid(mode=None, value="1")
        self.assert_invalid(mode="ENCODE", value="1")

    def test_value_type_errors(self) -> None:
        self.assert_invalid(mode="encode", value=None, base=16)
        self.assert_invalid(mode="encode", value=True, base=16)
        self.assert_invalid(mode="encode", value=1.5, base=16)
        self.assert_invalid(mode="encode", value=[255], base=16)
        self.assert_invalid(mode="encode", value="", base=16)
        self.assert_invalid(mode="decode", value=None, base=16)
        self.assert_invalid(mode="decode", value=255, base=16)
        self.assert_invalid(mode="decode", value="", base=16)
        self.assert_invalid(mode="info", value="")
        self.assert_invalid(mode="info", value=None)
        self.assert_invalid(mode="info", value=255)

    def test_base_range_and_type_errors(self) -> None:
        for base in (1, 37, 0, -16, "1x", "abc", True, 2.5, " 16", "+16", "1_6"):
            self.assert_invalid(mode="encode", value=1, base=base)
            self.assert_invalid(mode="decode", value="1", base=base)

    def test_base_as_digit_string_accepted(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="encode", value=255, base="16")["result"],
            HEX_255,
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=HEX_255, base="16")["result"],
            255,
        )

    def test_decode_requires_base(self) -> None:
        self.assert_invalid(mode="decode", value="ff")

    def test_convert_parameter_errors(self) -> None:
        self.assert_invalid(mode="convert", value="ff", from_base=16)
        self.assert_invalid(mode="convert", value="ff", to_base=16)
        self.assert_invalid(mode="convert", value="ff", from_base=16, to_base=2, base=8)
        self.assert_invalid(
            mode="convert", value="ff", from_base=16, to_base=2, prefix="0x"
        )
        self.assert_invalid(
            mode="convert",
            value="ff",
            from_base=16,
            to_base=2,
            alphabet=STD_ALPHABET[:2],
        )
        self.assert_invalid(mode="convert", value=255, from_base=10, to_base=16)
        self.assert_invalid(mode="convert", value="ff", from_base=1, to_base=16)
        self.assert_invalid(mode="convert", value="ff", from_base=16, to_base=37)

    def test_info_rejects_extra_parameters(self) -> None:
        self.assert_invalid(mode="info", value="ff", base=16)
        self.assert_invalid(mode="info", value="ff", from_base=16)
        self.assert_invalid(mode="info", value="ff", to_base=16)
        self.assert_invalid(mode="info", value="ff", alphabet=STD_ALPHABET)
        self.assert_invalid(mode="info", value="ff", prefix="0x")

    def test_value_length_cap(self) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(mode="decode", value="1" * 100_001, base=2)


class BaseNEncodeToolErrorPayloadTest(unittest.TestCase):
    """Content-level structured error payloads."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_decode_invalid_digit_positions(self) -> None:
        cases = [
            ("129", 8, 2, "'9'"),   # 9 is not an octal digit
            ("12g8", 16, 2, "'g'"),
            ("G00", 16, 0, "'G'"),
            (" 12", 10, 0, "' '"),
            ("12 3", 10, 2, "' '"),
            ("1_0", 2, 1, "'_'"),   # underscores are NOT int() leniency here
            ("12\t", 10, 2, "'\\t'"),
            ("abcz!", 36, 4, "'!'"),
        ]
        for value, base, position, char in cases:
            result = self.tool.execute(mode="decode", value=value, base=base)
            self.assertEqual(result["error"]["type"], "invalid_digit", value)
            self.assertIn(f"position {position}", result["error"]["message"], value)
            self.assertIn(char, result["error"]["message"], value)
            self.assertIn("error", result)
            self.assertNotIn("result", result)

    def test_decode_double_sign_reports_second_sign(self) -> None:
        for value in ("--1", "+-1", "-+1", "++1"):
            result = self.tool.execute(mode="decode", value=value, base=10)
            self.assertEqual(result["error"]["type"], "invalid_digit", value)
            self.assertIn("position 1", result["error"]["message"], value)

    def test_decode_sign_only_missing_digits(self) -> None:
        for value in ("-", "+"):
            result = self.tool.execute(mode="decode", value=value, base=10)
            self.assertEqual(result["error"]["type"], "missing_digits", value)
        for value in ("-", "+"):
            result = self.tool.execute(mode="encode", value=value)
            self.assertEqual(result["error"]["type"], "missing_digits", value)

    def test_encode_invalid_decimal_string_positions(self) -> None:
        cases = [
            ("12a4", 2),
            ("12 4", 2),
            (" 124", 0),
            ("12.5", 2),
            ("1,000", 1),
            ("+12a", 3),
            ("0x10", 1),
            ("1_000", 1),
            ("12\t4", 2),
        ]
        for value, position in cases:
            result = self.tool.execute(mode="encode", value=value)
            self.assertEqual(result["error"]["type"], "invalid_value", value)
            self.assertIn(f"position {position}", result["error"]["message"], value)

    def test_negative_values(self) -> None:
        result = self.tool.execute(mode="encode", value=-5)
        self.assertEqual(result["error"]["type"], "negative_value")
        result = self.tool.execute(mode="encode", value="-5")
        self.assertEqual(result["error"]["type"], "negative_value")
        result = self.tool.execute(mode="encode", value=-(2**64), base=16)
        self.assertEqual(result["error"]["type"], "negative_value")

    def test_decode_accepts_signs(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="decode", value="-ff", base=16),
            {
                "mode": "decode",
                "base": 16,
                "result": -255,
                "digit_count": 2,
                "negative": True,
            },
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="+ff", base=16)["result"], 255
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value="-0", base=8)["result"], 0
        )
        self.assertFalse(
            self.tool.execute(mode="decode", value="-0", base=8)["negative"]
        )

    def test_convert_propagates_content_errors(self) -> None:
        result = self.tool.execute(
            mode="convert", value="129", from_base=8, to_base=16
        )
        self.assertEqual(result["error"]["type"], "invalid_digit")
        self.assertIn("position 2", result["error"]["message"])
        self.assertEqual(result["from_base"], 8)
        self.assertEqual(result["to_base"], 16)
        result = self.tool.execute(mode="convert", value="-", from_base=8, to_base=16)
        self.assertEqual(result["error"]["type"], "missing_digits")

    def test_magnitude_cap(self) -> None:
        # Exactly 10**10000 is allowed ...
        self.assertEqual(
            self.tool.execute(mode="encode", value=CAP, base=10)["result"],
            DEC_10_POW_10000,
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=DEC_10_POW_10000, base=10)[
                "result"
            ],
            DEC_10_POW_10000,
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=DEC_10_POW_10000, base=10)[
                "result"
            ],
            CAP,
        )
        # ... but one order of magnitude more is rejected everywhere.
        self.assertEqual(
            self.tool.execute(mode="encode", value=CAP * 10)["error"]["type"],
            "value_too_large",
        )
        self.assertEqual(
            self.tool.execute(mode="encode", value=DEC_10_POW_10000 + "0")["error"][
                "type"
            ],
            "value_too_large",
        )
        self.assertEqual(
            self.tool.execute(mode="decode", value=DEC_10_POW_10000 + "0", base=10)[
                "error"
            ]["type"],
            "value_too_large",
        )
        self.assertEqual(
            self.tool.execute(
                mode="convert", value=DEC_10_POW_10000 + "0", from_base=10, to_base=16
            )["error"]["type"],
            "value_too_large",
        )

    def test_big_int_round_trip_across_cap_region(self) -> None:
        number = CAP - 1
        for base in (2, 16, 36):
            digits = self.tool.execute(mode="encode", value=number, base=base)[
                "result"
            ]
            self.assertEqual(
                self.tool.execute(mode="decode", value=digits, base=base)["result"],
                number,
            )

    def test_error_payloads_keep_context(self) -> None:
        result = self.tool.execute(mode="decode", value="zz", base=8)
        self.assertEqual(result["mode"], "decode")
        self.assertEqual(result["base"], 8)
        self.assertIn("error", result)
        self.assertNotIn("result", result)
        result = self.tool.execute(mode="encode", value="x", base=8)
        self.assertEqual(result["mode"], "encode")
        self.assertEqual(result["base"], 8)


class BaseNEncodeToolInfoTest(unittest.TestCase):
    """info mode: which bases a string is a valid numeral in."""

    def setUp(self) -> None:
        self.tool = BaseNEncodeTool()

    def test_info_simple(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="info", value="ff"),
            {
                "mode": "info",
                "value": "ff",
                "sign": None,
                "digit_count": 2,
                "valid_bases": list(range(16, 37)),
                "valid_base_count": 21,
                "min_base": 16,
            },
        )

    def test_info_digits_bound_the_minimum_base(self) -> None:
        self.assertEqual(self.tool.execute(mode="info", value="129")["min_base"], 10)
        self.assertEqual(self.tool.execute(mode="info", value="101")["min_base"], 2)
        self.assertEqual(self.tool.execute(mode="info", value="777")["min_base"], 8)
        self.assertEqual(self.tool.execute(mode="info", value="zz")["min_base"], 36)
        self.assertEqual(self.tool.execute(mode="info", value="0")["min_base"], 2)
        self.assertEqual(
            self.tool.execute(mode="info", value="0")["valid_bases"],
            list(range(2, 37)),
        )

    def test_info_sign_is_reported_not_counted(self) -> None:
        result = self.tool.execute(mode="info", value="-129")
        self.assertEqual(result["sign"], "-")
        self.assertEqual(result["digit_count"], 3)
        self.assertEqual(result["min_base"], 10)
        result = self.tool.execute(mode="info", value="+ff")
        self.assertEqual(result["sign"], "+")
        self.assertEqual(result["min_base"], 16)

    def test_info_uppercase_and_lowercase_agree(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="info", value="FF")["valid_bases"],
            self.tool.execute(mode="info", value="ff")["valid_bases"],
        )

    def test_info_no_valid_bases(self) -> None:
        for value in ("!!", "1 2", "12.5", "1_0", "0x!f"):
            result = self.tool.execute(mode="info", value=value)
            self.assertEqual(result["valid_bases"], [], value)
            self.assertIsNone(result["min_base"], value)
            self.assertEqual(result["valid_base_count"], 0, value)

    def test_info_hex_prefix_chars_are_digits_of_high_bases(self) -> None:
        # '0', 'x', '1', 'G' are all standard digits, so '0x1G' is a
        # valid numeral of every base from 34 up — the literal prefix
        # reading does not apply without a prefix option.
        self.assertEqual(
            self.tool.execute(mode="info", value="0x1G")["valid_bases"],
            [34, 35, 36],
        )

    def test_info_matches_decode_validity(self) -> None:
        for value in ("1010", "129", "ff", "zzz", "007", "-10"):
            info = self.tool.execute(mode="info", value=value)
            body = value[1:] if value[:1] in "+-" else value
            for base in range(2, 37):
                decoded = self.tool.execute(mode="decode", value=body, base=base)
                valid = "error" not in decoded
                self.assertEqual(
                    base in info["valid_bases"],
                    valid,
                    f"value={value} base={base}",
                )


class BaseNEncodeToolPackagingTest(unittest.TestCase):
    """Module packaging: imports, class defaults, yaml configuration."""

    def test_direct_module_import_matches_package_export(self) -> None:
        self.assertIs(DirectBaseNEncodeTool, BaseNEncodeTool)

    def test_tool_defaults(self) -> None:
        tool = BaseNEncodeTool()
        self.assertEqual(tool.name, "basen_encode_tool")
        self.assertIn("mode='encode'", tool.description)
        self.assertIn("mode='decode'", tool.description)
        self.assertIn("mode='convert'", tool.description)
        self.assertIn("mode='info'", tool.description)

    def test_yaml_matches_module(self) -> None:
        # The yaml lives next to the module it configures.
        module_file = sys.modules[DirectBaseNEncodeTool.__module__].__file__
        candidate = os.path.join(
            os.path.dirname(os.path.abspath(module_file)),
            "basen_encode_tool.yaml",
        )
        self.assertTrue(os.path.isfile(candidate), candidate)
        with open(candidate, "r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        self.assertEqual(config["name"], "basen_encode_tool")
        self.assertEqual(config["tool_type"], "api")
        self.assertEqual(
            config["metadata"]["module"],
            "agentuniverse.agent.action.tool.common_tool.basen_encode_tool",
        )
        self.assertEqual(config["metadata"]["class"], "BaseNEncodeTool")
        self.assertEqual(config["input_keys"], ["mode"])
        self.assertEqual(config["args_model_schema"]["required"], ["mode"])
        self.assertEqual(
            sorted(config["args_model_schema"]["properties"].keys()),
            ["alphabet", "base", "from_base", "mode", "prefix", "to_base", "value"],
        )
        self.assertEqual(
            config["args_model_schema"]["properties"]["mode"]["enum"],
            ["encode", "decode", "convert", "info"],
        )


if __name__ == "__main__":
    unittest.main()
