#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_checksum_tool.py

"""Offline unit tests for ChecksumTool.

The tool is built purely on the standard library (zlib, base64) and
never touches the network, so this suite runs fully offline. Every
assertion is deterministic: crc32 / adler32 results are checked both
against zlib itself and against pinned published literals (the CRC-32
check value of "123456789" and the Adler-32 example "Wikipedia"),
fletcher16 against an independent reference implementation of the
classic byte-wise algorithm plus pinned literals, and the byte sums
against hand-computed values. Empty-input conventions, the Base64
binary path, UTF-8 CJK bytes, case-insensitive verification and the
strict validation error matrix are all covered.
"""

import base64
import unittest
import zlib

from agentuniverse.agent.action.tool.common_tool import ChecksumTool
from agentuniverse.agent.action.tool.common_tool.checksum_tool import (
    ChecksumTool as DirectChecksumTool,
)

# --------------------------------------------------------------------- #
# Pinned known vectors (independent of the tool implementation)
# --------------------------------------------------------------------- #
# Canonical CRC-32 check value (IEEE 802.3, used by zlib.crc32).
CRC32_123456789 = "cbf43926"
# Adler-32 example value from the algorithm's original description.
ADLER32_WIKIPEDIA = "11e60398"

ALL_VECTORS_123456789 = {
    "crc32": ("cbf43926", 0xCBF43926),
    "adler32": ("091e01de", 0x091E01DE),
    "fletcher16": ("1ede", 0x1EDE),
    "sum8": ("dd", 0xDD),
    "sum16": ("01dd", 0x01DD),
}
ALL_VECTORS_WIKIPEDIA = {
    "crc32": ("adaac02e", 0xADAAC02E),
    "adler32": ("11e60398", 0x11E60398),
    "fletcher16": ("ee9a", 0xEE9A),
    "sum8": ("97", 0x97),
    "sum16": ("0397", 0x0397),
}
ALL_VECTORS_HELLO = {
    "crc32": ("3610a686", 0x3610A686),
    "adler32": ("062c0215", 0x062C0215),
    "fletcher16": ("2d16", 0x2D16),
    "sum8": ("14", 0x14),
    "sum16": ("0214", 0x0214),
}
# Empty-input conventions: crc32(b"")=0, adler32(b"")=1 (the Adler
# modulo starts at 1), fletcher16(b"")=0, sum8/sum16(b"")=0.
EMPTY_VECTORS = {
    "crc32": ("00000000", 0),
    "adler32": ("00000001", 1),
    "fletcher16": ("0000", 0),
    "sum8": ("00", 0),
    "sum16": ("0000", 0),
}
# Fletcher-16 of the classic two-byte example {0x01, 0x02}.
FLETCHER16_0102 = "0403"
# Fletcher-16 of the byte sequence "abcde".
FLETCHER16_ABCDE = "c8f0"
# Published Fletcher-16 test vectors (8-bit data words, modulo-255
# running sums) from the Fletcher's checksum reference literature:
# "abcdef", "abcdefgh" and the check-byte completion property, where
# appending the two derived check bytes to {0x01, 0x02} zeroes the
# total checksum.
PUBLISHED_FLETCHER16 = [
    ("abcdef", "2057"),
    ("abcdefgh", "0627"),
]
FLETCHER16_CHECKBYTE_ZERO = ("AQL4BA==", "0000")
# CJK text "你好世界" — UTF-8 bytes e4bda0 e5a5bd e4b896 e7958c.
CJK_TEXT = "你好世界"
CJK_B64 = "5L2g5aW95LiW55WM"
CJK_VECTORS = {
    "crc32": ("af7317c9", 2_943_555_529),
    "adler32": ("3b2e08c3", 992_872_643),
    "fletcher16": ("5dca", 24_010),
    "sum8": ("c2", 194),
    "sum16": ("08c2", 2_242),
}
# Base64 of bytes([0x01, 0x02]) for the binary-input path.
B64_0102 = "AQI="

MAX_BYTES = 1_048_576


def reference_fletcher16(data: bytes) -> int:
    """Independent classic byte-wise Fletcher-16 reference (mod 255)."""
    sum1 = 0
    sum2 = 0
    for byte in data:
        sum1 = (sum1 + byte) % 255
        sum2 = (sum2 + sum1) % 255
    return (sum2 << 8) | sum1


class ChecksumToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib ChecksumTool."""

    def setUp(self) -> None:
        self.tool = ChecksumTool()

    # ------------------------------------------------------------------ #
    # compute mode — known vectors
    # ------------------------------------------------------------------ #

    def test_compute_known_vectors(self) -> None:
        suites = [
            ("123456789", ALL_VECTORS_123456789),
            ("Wikipedia", ALL_VECTORS_WIKIPEDIA),
            ("hello", ALL_VECTORS_HELLO),
            (CJK_TEXT, CJK_VECTORS),
        ]
        for text, vectors in suites:
            for algorithm, (hex_str, int_val) in vectors.items():
                with self.subTest(text=text[:16], algorithm=algorithm):
                    result = self.tool.execute(
                        mode="compute",
                        input=text,
                        algorithm=algorithm,
                    )
                    self.assertEqual(
                        result,
                        {
                            "mode": "compute",
                            "input_encoding": "utf8-text",
                            "byte_length": len(text.encode("utf-8")),
                            "algorithm": algorithm,
                            "hex": hex_str,
                            "unsigned_int": int_val,
                        },
                    )
                    self.assertEqual(int(result["hex"], 16), result["unsigned_int"])

    def test_crc32_adler32_cross_checked_against_zlib(self) -> None:
        # The pinned literals above must equal what zlib itself reports,
        # guarding against transcription errors in either place.
        self.assertEqual(zlib.crc32(b"123456789") & 0xFFFFFFFF, 0xCBF43926)
        self.assertEqual(zlib.adler32(b"Wikipedia") & 0xFFFFFFFF, 0x11E60398)
        for text in ("123456789", "Wikipedia", "hello", CJK_TEXT, "", "x" * 4096):
            data = text.encode("utf-8")
            with self.subTest(text=text[:16]):
                self.assertEqual(
                    self.tool.execute(mode="compute", input=text, algorithm="crc32")["hex"],
                    f"{zlib.crc32(data) & 0xFFFFFFFF:08x}",
                )
                self.assertEqual(
                    self.tool.execute(mode="compute", input=text, algorithm="adler32")["hex"],
                    f"{zlib.adler32(data) & 0xFFFFFFFF:08x}",
                )

    def test_fletcher16_against_reference_and_literals(self) -> None:
        # Classic byte-wise Fletcher-16 vectors, computed per the
        # published algorithm and pinned here.
        self.assertEqual(
            self.tool.execute(
                mode="compute", input=B64_0102, algorithm="fletcher16",
                input_encoding="base64",
            )["hex"],
            FLETCHER16_0102,
        )
        self.assertEqual(reference_fletcher16(bytes([0x01, 0x02])), 0x0403)
        self.assertEqual(
            self.tool.execute(
                mode="compute", input="abcde", algorithm="fletcher16"
            )["hex"],
            FLETCHER16_ABCDE,
        )
        self.assertEqual(reference_fletcher16(b"abcde"), 0xC8F0)
        for data in (b"", b"abcde", bytes([0x01, 0x02]), bytes(range(256)), CJK_TEXT.encode("utf-8")):
            with self.subTest(data=data[:16]):
                self.assertEqual(
                    self.tool._fletcher16(data), reference_fletcher16(data)
                )

    def test_fletcher16_published_vectors(self) -> None:
        for text, hex_str in PUBLISHED_FLETCHER16:
            with self.subTest(text=text):
                self.assertEqual(
                    self.tool.execute(
                        mode="compute", input=text, algorithm="fletcher16"
                    )["hex"],
                    hex_str,
                )
                self.assertEqual(reference_fletcher16(text.encode("ascii")), int(hex_str, 16))
        b64, hex_str = FLETCHER16_CHECKBYTE_ZERO
        result = self.tool.execute(
            mode="compute", input=b64, algorithm="fletcher16",
            input_encoding="base64",
        )
        self.assertEqual(result["hex"], hex_str)

    def test_fletcher16_mod_255_collision_documented(self) -> None:
        # 0xFF + 0xFF vanishes under mod 255: b"\xff\xff" and the empty
        # input share checksum 0x0000 — short checksums collide by design.
        ff = self.tool.execute(
            mode="compute", input="//8=", algorithm="fletcher16",
            input_encoding="base64",
        )
        self.assertEqual(ff["hex"], "0000")
        empty = self.tool.execute(
            mode="compute", input="", algorithm="fletcher16"
        )
        self.assertEqual(empty["hex"], "0000")

    def test_byte_sums_hand_computed(self) -> None:
        # "hello" bytes sum to 104+101+108+108+111 = 532.
        result8 = self.tool.execute(mode="compute", input="hello", algorithm="sum8")
        self.assertEqual(result8["unsigned_int"], 532 % 256)
        result16 = self.tool.execute(mode="compute", input="hello", algorithm="sum16")
        self.assertEqual(result16["unsigned_int"], 532)
        self.assertEqual(result16["hex"], "0214")

    def test_empty_input_conventions(self) -> None:
        for algorithm, (hex_str, int_val) in EMPTY_VECTORS.items():
            with self.subTest(algorithm=algorithm):
                result = self.tool.execute(
                    mode="compute", input="", algorithm=algorithm
                )
                self.assertEqual(result["byte_length"], 0)
                self.assertEqual(result["hex"], hex_str)
                self.assertEqual(result["unsigned_int"], int_val)
        # The crc32/adler32 conventions are exactly zlib's own.
        self.assertEqual(zlib.crc32(b"") & 0xFFFFFFFF, 0)
        self.assertEqual(zlib.adler32(b"") & 0xFFFFFFFF, 1)

    # ------------------------------------------------------------------ #
    # base64 input path
    # ------------------------------------------------------------------ #

    def test_base64_path_matches_utf8_path(self) -> None:
        all_b64 = self.tool.execute(
            mode="all", input=CJK_B64, input_encoding="base64"
        )
        all_text = self.tool.execute(mode="all", input=CJK_TEXT)
        self.assertEqual(all_b64["byte_length"], len(CJK_TEXT.encode("utf-8")))
        self.assertEqual(all_b64["results"], all_text["results"])

    def test_base64_binary_payload(self) -> None:
        # bytes([0x01, 0x02]) cannot be sent as utf8-text; the Base64
        # path carries it through and matches the pinned vectors.
        result = self.tool.execute(
            mode="compute",
            input=B64_0102,
            input_encoding="base64",
            algorithm="crc32",
        )
        self.assertEqual(result["input_encoding"], "base64")
        self.assertEqual(result["byte_length"], 2)
        self.assertEqual(
            result["hex"], f"{zlib.crc32(bytes([0x01, 0x02])) & 0xFFFFFFFF:08x}"
        )
        self.assertEqual(
            self.tool.execute(
                mode="compute",
                input=B64_0102,
                input_encoding="base64",
                algorithm="sum16",
            )["hex"],
            "0003",
        )

    def test_base64_invalid_content_structured_error(self) -> None:
        for bad in ("not base64!", "aGVsbG8", "####"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="compute",
                    input=bad,
                    input_encoding="base64",
                    algorithm="crc32",
                )
                self.assertEqual(result["input_encoding"], "base64")
                self.assertEqual(result["error"]["type"], "invalid_base64")
                self.assertIn("Base64", result["error"]["message"])

    def test_base64_empty_string_decodes_to_empty(self) -> None:
        result = self.tool.execute(
            mode="compute", input="", input_encoding="base64", algorithm="adler32"
        )
        self.assertEqual(result["hex"], "00000001")

    def test_base64_urlsafe_and_mime_whitespace_rejected(self) -> None:
        for bad in ("-_8=", "aGVs bG8=", "aGVs\nbG8=", "aGVs\tbG8="):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="compute",
                    input=bad,
                    input_encoding="base64",
                    algorithm="crc32",
                )
                self.assertEqual(result["error"]["type"], "invalid_base64")

    def test_base64_exactly_at_cap_accepted(self) -> None:
        payload = b"q" * MAX_BYTES
        result = self.tool.execute(
            mode="compute",
            input=base64.b64encode(payload).decode("ascii"),
            input_encoding="base64",
            algorithm="crc32",
        )
        self.assertEqual(result["byte_length"], MAX_BYTES)
        self.assertEqual(
            result["hex"], f"{zlib.crc32(payload) & 0xFFFFFFFF:08x}"
        )

    def test_input_with_lone_surrogate_rejected_cleanly(self) -> None:
        for bad in ("abc\ud800def", "\udfff", "a\ud800b\ud801c"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(
                        mode="compute", input=bad, algorithm="crc32"
                    )
                message = str(ctx.exception)
                self.assertTrue(message.startswith("checksum_tool:"))
                self.assertIn("UTF-8", message)
                self.assertIn("position", message)
                result = self.tool.execute(
                    mode="all", input=bad, input_encoding="base64"
                )
                self.assertEqual(result["error"]["type"], "invalid_base64")

    # ------------------------------------------------------------------ #
    # verify mode
    # ------------------------------------------------------------------ #

    def test_verify_match_lowercase_and_uppercase(self) -> None:
        for expected in ("cbf43926", "CBF43926", "CbF43926"):
            with self.subTest(expected=expected):
                result = self.tool.execute(
                    mode="verify",
                    input="123456789",
                    algorithm="crc32",
                    expected=expected,
                )
                self.assertEqual(
                    result,
                    {
                        "mode": "verify",
                        "input_encoding": "utf8-text",
                        "byte_length": 9,
                        "algorithm": "crc32",
                        "expected": expected.lower(),
                        "computed_hex": "cbf43926",
                        "match": True,
                    },
                )

    def test_verify_mismatch(self) -> None:
        result = self.tool.execute(
            mode="verify",
            input="123456789",
            algorithm="crc32",
            expected="cbf43927",
        )
        self.assertIs(result["match"], False)
        self.assertEqual(result["computed_hex"], "cbf43926")

    def test_verify_every_algorithm_case_insensitive(self) -> None:
        for algorithm, (hex_str, _) in ALL_VECTORS_WIKIPEDIA.items():
            with self.subTest(algorithm=algorithm):
                ok = self.tool.execute(
                    mode="verify",
                    input="Wikipedia",
                    algorithm=algorithm,
                    expected=hex_str.upper(),
                )
                self.assertIs(ok["match"], True)
                bad = self.tool.execute(
                    mode="verify",
                    input="wikipedia",  # different case -> different bytes
                    algorithm=algorithm,
                    expected=hex_str.upper(),
                )
                self.assertIs(bad["match"], False)

    def test_verify_round_trip_with_compute(self) -> None:
        for text in ("hello", "", CJK_TEXT, "line1\nline2\ttab", "a" * 1000):
            for algorithm in ChecksumTool.ALGORITHMS:
                with self.subTest(text=text[:12], algorithm=algorithm):
                    computed = self.tool.execute(
                        mode="compute", input=text, algorithm=algorithm
                    )["hex"]
                    result = self.tool.execute(
                        mode="verify",
                        input=text,
                        algorithm=algorithm,
                        expected=computed.upper(),
                    )
                    self.assertIs(result["match"], True)

    def test_verify_base64_input_path(self) -> None:
        result = self.tool.execute(
            mode="verify",
            input=CJK_B64,
            input_encoding="base64",
            algorithm="adler32",
            expected="3B2E08C3",
        )
        self.assertIs(result["match"], True)

    def test_verify_empty_input_against_conventions(self) -> None:
        for algorithm, (hex_str, _) in EMPTY_VECTORS.items():
            with self.subTest(algorithm=algorithm):
                result = self.tool.execute(
                    mode="verify", input="", algorithm=algorithm, expected=hex_str
                )
                self.assertIs(result["match"], True)

    # ------------------------------------------------------------------ #
    # all mode
    # ------------------------------------------------------------------ #

    def test_all_mode_contains_every_algorithm(self) -> None:
        result = self.tool.execute(mode="all", input="Wikipedia")
        self.assertEqual(result["mode"], "all")
        self.assertEqual(result["input_encoding"], "utf8-text")
        self.assertEqual(result["byte_length"], 9)
        self.assertEqual(
            list(result["results"].keys()), list(ChecksumTool.ALGORITHMS)
        )
        for algorithm, (hex_str, int_val) in ALL_VECTORS_WIKIPEDIA.items():
            self.assertEqual(
                result["results"][algorithm],
                {"algorithm": algorithm, "hex": hex_str, "unsigned_int": int_val},
            )

    def test_all_mode_consistent_with_individual_computes(self) -> None:
        for text in ("hello", "", CJK_TEXT, B64_0102):
            with self.subTest(text=text[:12]):
                all_result = self.tool.execute(mode="all", input=text)
                for algorithm in ChecksumTool.ALGORITHMS:
                    single = self.tool.execute(
                        mode="compute", input=text, algorithm=algorithm
                    )
                    self.assertEqual(
                        all_result["results"][algorithm]["hex"], single["hex"]
                    )
                    self.assertEqual(
                        all_result["results"][algorithm]["unsigned_int"],
                        single["unsigned_int"],
                    )

    def test_all_mode_repeated_calls_are_idempotent(self) -> None:
        first = self.tool.execute(mode="all", input=CJK_TEXT)
        second = self.tool.execute(mode="all", input=CJK_TEXT)
        self.assertEqual(first, second)
        self.assertEqual(list(first["results"]), list(second["results"]))
        self.assertEqual(list(first["results"]), list(ChecksumTool.ALGORITHMS))

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="hash", input="x", algorithm="crc32")
        self.assert_invalid(mode=None, input="x", algorithm="crc32")
        self.assert_invalid(mode=123, input="x", algorithm="crc32")

    def test_invalid_algorithm(self) -> None:
        for mode in ("compute", "verify"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, input="x", algorithm="md5")
                self.assert_invalid(mode=mode, input="x", algorithm=None)
                self.assert_invalid(mode=mode, input="x", algorithm="CRC32")
                self.assert_invalid(mode=mode, input="x", algorithm=True)

    def test_invalid_input_type(self) -> None:
        for bad in (None, 123, True, b"hello", ["hello"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="compute", input=bad, algorithm="crc32")
                self.assert_invalid(mode="all", input=bad)

    def test_invalid_input_encoding(self) -> None:
        self.assert_invalid(
            mode="compute", input="x", algorithm="crc32", input_encoding="hex"
        )
        self.assert_invalid(
            mode="compute", input="x", algorithm="crc32", input_encoding="utf8"
        )
        self.assert_invalid(
            mode="compute", input="x", algorithm="crc32", input_encoding=True
        )

    def test_default_input_encoding_is_utf8_text(self) -> None:
        result = self.tool.execute(
            mode="compute", input="x", algorithm="crc32", input_encoding=None
        )
        self.assertEqual(result["input_encoding"], "utf8-text")

    def test_input_size_caps(self) -> None:
        # Character-level cap for plain text.
        self.assert_invalid(
            mode="compute", input="a" * (MAX_BYTES + 1), algorithm="crc32"
        )
        # Byte-level cap: CJK characters expand to 3 UTF-8 bytes each,
        # so 349,526 characters encode to 1,048,578 bytes.
        self.assert_invalid(
            mode="compute", input="世" * 349_526, algorithm="crc32"
        )
        # Decoded-byte cap for the Base64 path.
        oversized_b64 = base64.b64encode(b"a" * (MAX_BYTES + 1)).decode("ascii")
        self.assert_invalid(
            mode="compute", input=oversized_b64, input_encoding="base64",
            algorithm="crc32",
        )
        # Character-level cap guarding the Base64 decode itself.
        self.assert_invalid(
            mode="compute", input="A" * (MAX_BYTES * 2 + 1), input_encoding="base64",
            algorithm="crc32",
        )

    def test_input_at_exact_cap_is_accepted(self) -> None:
        boundary = self.tool.execute(
            mode="compute", input="a" * MAX_BYTES, algorithm="crc32"
        )
        self.assertEqual(boundary["byte_length"], MAX_BYTES)
        self.assertEqual(
            boundary["hex"], f"{zlib.crc32(b'a' * MAX_BYTES) & 0xFFFFFFFF:08x}"
        )

    def test_invalid_expected_hex(self) -> None:
        base = dict(mode="verify", input="123456789", algorithm="crc32")
        self.assert_invalid(**base, expected=None)
        self.assert_invalid(**base, expected=123)
        self.assert_invalid(**base, expected=True)
        # Wrong width (crc32 expects exactly 8 digits).
        self.assert_invalid(**base, expected="cbf4392")
        self.assert_invalid(**base, expected="cbf439260")
        self.assert_invalid(**base, expected="")
        # sum8 expects exactly 2 digits.
        self.assert_invalid(
            mode="verify", input="x", algorithm="sum8", expected="014"
        )

    def test_invalid_expected_wrong_width_cross_algorithm(self) -> None:
        # A valid hex string of another algorithm's width must fail the
        # width check rather than silently mismatch.
        widths = ChecksumTool.HEX_WIDTHS
        for algorithm in ChecksumTool.ALGORITHMS:
            for other in ChecksumTool.ALGORITHMS:
                if widths[other] == widths[algorithm]:
                    continue
                other_hex = "a" * widths[other]
                with self.subTest(algorithm=algorithm, other=other):
                    self.assert_invalid(
                        mode="verify",
                        input="123456789",
                        algorithm=algorithm,
                        expected=other_hex,
                    )

    def test_invalid_expected_hex_reports_position(self) -> None:
        base = dict(mode="verify", input="123456789", algorithm="crc32")
        cases = [
            ("1234567z", "'z' at position 7"),
            ("0x12345678", "'x' at position 1"),
            ("1234567 ", "' ' at position 7"),
            ("123-4567", "'-' at position 3"),
        ]
        for expected, fragment in cases:
            with self.subTest(expected=expected):
                with self.assertRaises(ValueError) as ctx:
                    self.tool.execute(**base, expected=expected)
                self.assertIn("position", str(ctx.exception))
                self.assertIn(fragment, str(ctx.exception))

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectChecksumTool, ChecksumTool)
        self.assertEqual(self.tool.name, "checksum_tool")
        self.assertIn("crc32", self.tool.description)
        self.assertEqual(
            ChecksumTool.HEX_WIDTHS,
            {
                "crc32": 8,
                "adler32": 8,
                "fletcher16": 4,
                "sum8": 2,
                "sum16": 4,
            },
        )
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("ChecksumTool", __all__)


if __name__ == "__main__":
    unittest.main()
