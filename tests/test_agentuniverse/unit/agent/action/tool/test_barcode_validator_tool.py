#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_barcode_validator_tool.py

"""Offline unit tests for BarcodeValidatorTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: the "known valid" reference identifiers (ISBN-10
0306406152, ISBN-13 9780306406157, EAN-13 4006381333931, EAN-8
96385074, UPC-A 036000291452 and the X-check-digit ISBN-10
080442957X) are first re-verified in-test against an independent
re-implementation of the checksum arithmetic instead of being trusted
blindly; corrupted variants, check-digit computations, conversions and
prefix lookups are all cross-checked against the same helpers.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import BarcodeValidatorTool
from agentuniverse.agent.action.tool.common_tool.barcode_validator_tool import (
    BarcodeValidatorTool as DirectBarcodeValidatorTool,
)


# --------------------------------------------------------------------- #
# Independent checksum helpers (re-implement the standard formulas)
# --------------------------------------------------------------------- #
def isbn10_sum(code: str) -> int:
    """Mod-11 weighted sum (weights 10..1, X = 10)."""
    return sum(
        (10 if ch == "X" else int(ch)) * (10 - i) for i, ch in enumerate(code)
    )


def gs1_sum(code: str) -> int:
    """Mod-10 weighted sum of a full GS1 code (check digit weight 1)."""
    start = 1 if len(code) % 2 else 3
    return sum(
        int(ch) * (start if i % 2 == 0 else 4 - start)
        for i, ch in enumerate(code)
    )


def isbn10_cd(data9: str) -> str:
    total = sum(int(ch) * (10 - i) for i, ch in enumerate(data9))
    value = (11 - total % 11) % 11
    return "X" if value == 10 else str(value)


def gs1_cd(data: str, full_length: int) -> str:
    start = 1 if full_length % 2 else 3
    total = sum(
        int(ch) * (start if i % 2 == 0 else 4 - start)
        for i, ch in enumerate(data)
    )
    return str((10 - total % 10) % 10)


# --------------------------------------------------------------------- #
# Reference identifiers (each is re-verified in-test before use)
# --------------------------------------------------------------------- #
ISBN10_VALID = "0306406152"        # classic worked example (0-306-40615-2)
ISBN10_X_VALID = "080442957X"      # canonical example whose check digit is X
ISBN13_VALID = "9780306406157"     # the same book as ISBN10_VALID
EAN13_VALID = "4006381333931"      # GS1 documentation example
EAN8_VALID = "96385074"            # GS1 documentation example
UPCA_VALID = "036000291452"        # GS1 documentation example

# 13-digit data blocks used to construct additional valid codes whose
# checksums (and therefore exact check digits) are derived in-test.
DATA13_JAPAN = "978406282151"
DATA13_RUSSIA = "978538909912"
DATA13_FRANCE = "978207049912"
DATA13_GERMANY = "978344215366"
DATA13_CHINA = "978711111111"
DATA13_UNKNOWN_GROUP = "978999999999"
DATA13_979_MUSIC = "979012345678"

UNICODE_TEXT_DIGIT = "٠"  # Arabic-Indic zero — must be rejected


class BarcodeValidatorToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib BarcodeValidatorTool."""

    def setUp(self) -> None:
        self.tool = BarcodeValidatorTool()

    # ------------------------------------------------------------------ #
    # Reference-vector self-check (never trust the constants blindly)
    # ------------------------------------------------------------------ #

    def test_reference_vectors_selfcheck(self) -> None:
        self.assertEqual(isbn10_sum(ISBN10_VALID) % 11, 0)
        self.assertEqual(isbn10_sum(ISBN10_X_VALID) % 11, 0)
        self.assertEqual(gs1_sum(ISBN13_VALID) % 10, 0)
        self.assertEqual(gs1_sum(EAN13_VALID) % 10, 0)
        self.assertEqual(gs1_sum(EAN8_VALID) % 10, 0)
        self.assertEqual(gs1_sum(UPCA_VALID) % 10, 0)
        # The two ISBN forms describe the same book.
        self.assertEqual(ISBN13_VALID, "978" + ISBN10_VALID[:9] + gs1_cd("978" + ISBN10_VALID[:9], 13))
        # Constructed codes used by the info tests are valid, too.
        for data in (
            DATA13_JAPAN,
            DATA13_RUSSIA,
            DATA13_FRANCE,
            DATA13_GERMANY,
            DATA13_CHINA,
            DATA13_UNKNOWN_GROUP,
            DATA13_979_MUSIC,
        ):
            self.assertEqual(gs1_sum(data + gs1_cd(data, 13)) % 10, 0)

    # ------------------------------------------------------------------ #
    # validate mode — known-valid identifiers
    # ------------------------------------------------------------------ #

    def test_validate_known_valid_identifiers(self) -> None:
        cases = [
            (ISBN10_VALID, ["isbn-10"], 11, isbn10_sum(ISBN10_VALID)),
            (ISBN13_VALID, ["isbn-13", "ean-13"], 10, gs1_sum(ISBN13_VALID)),
            (EAN13_VALID, ["ean-13"], 10, gs1_sum(EAN13_VALID)),
            (EAN8_VALID, ["ean-8"], 10, gs1_sum(EAN8_VALID)),
            (UPCA_VALID, ["upc-a"], 10, gs1_sum(UPCA_VALID)),
        ]
        for code, detected, modulus, total in cases:
            with self.subTest(code=code):
                result = self.tool.execute(mode="validate", code=code)
                self.assertEqual(result["mode"], "validate")
                self.assertEqual(result["code"], code)
                self.assertEqual(result["auto_detected"], detected)
                self.assertTrue(result["valid"])
                self.assertEqual(
                    result["reason"], "valid as " + ", ".join(detected)
                )
                self.assertEqual(len(result["interpretations"]), len(detected))
                for item in result["interpretations"]:
                    self.assertTrue(item["valid"])
                    self.assertEqual(item["reason"], "checksum passes")
                    self.assertEqual(item["provided_check_digit"], code[-1])
                    self.assertEqual(item["expected_check_digit"], code[-1])
                    self.assertIn(f"= {total}", item["checksum"])
                    self.assertIn(f"mod {modulus}", item["checksum"])
                    self.assertIn("checksum valid", item["checksum"])

    def test_validate_isbn10_with_x_check_digit(self) -> None:
        result = self.tool.execute(mode="validate", code=ISBN10_X_VALID)
        self.assertTrue(result["valid"])
        item = result["interpretations"][0]
        self.assertEqual(item["code_type"], "isbn-10")
        self.assertEqual(item["provided_check_digit"], "X")
        self.assertEqual(item["expected_check_digit"], "X")
        self.assertIn("X(10)*1", item["checksum"])
        self.assertIn(f"= {isbn10_sum(ISBN10_X_VALID)}", item["checksum"])

    def test_validate_lowercase_x_normalised(self) -> None:
        result = self.tool.execute(mode="validate", code="080442957x")
        self.assertEqual(result["code"], "080442957X")
        self.assertTrue(result["valid"])

    def test_validate_hyphen_and_space_tolerance(self) -> None:
        cases = [
            "978-0-306-40615-7",
            "978 0 306 40615 7",
            "0-306-40615-2",
            " 0 306 40615 2 ",
            "0-8044-2957-X",
            "0-8044-2957-x",
            "0 360 00291 452",
            "963 8507 4",
        ]
        for code in cases:
            with self.subTest(code=code):
                result = self.tool.execute(mode="validate", code=code)
                self.assertTrue(result["valid"], result)

    # ------------------------------------------------------------------ #
    # validate mode — corrupted digits are rejected with arithmetic shown
    # ------------------------------------------------------------------ #

    def test_validate_corrupted_check_digits(self) -> None:
        cases = [
            (ISBN10_VALID[:-1] + "3", "isbn-10", "2", 11, isbn10_sum(ISBN10_VALID[:-1] + "3")),
            (ISBN13_VALID[:-1] + "8", "isbn-13", "7", 10, gs1_sum(ISBN13_VALID[:-1] + "8")),
            (EAN13_VALID[:-1] + "2", "ean-13", "1", 10, gs1_sum(EAN13_VALID[:-1] + "2")),
            (EAN8_VALID[:-1] + "5", "ean-8", "4", 10, gs1_sum(EAN8_VALID[:-1] + "5")),
            (UPCA_VALID[:-1] + "3", "upc-a", "2", 10, gs1_sum(UPCA_VALID[:-1] + "3")),
        ]
        for code, code_type, expected, modulus, total in cases:
            with self.subTest(code=code):
                result = self.tool.execute(mode="validate", code=code)
                self.assertFalse(result["valid"])
                item = next(
                    i for i in result["interpretations"]
                    if i["code_type"] == code_type
                )
                self.assertFalse(item["valid"])
                self.assertEqual(item["expected_check_digit"], expected)
                self.assertEqual(item["provided_check_digit"], code[-1])
                self.assertIn("checksum fails", item["reason"])
                self.assertIn(f"expected check digit {expected!r}", item["reason"])
                self.assertIn("checksum invalid", item["checksum"])
                self.assertIn(f"= {total}", item["checksum"])
                self.assertIn(f"mod {modulus}", item["checksum"])
                # The expected check digit is confirmed by the helper.
                if code_type == "isbn-10":
                    self.assertEqual(isbn10_cd(code[:9]), expected)
                else:
                    self.assertEqual(gs1_cd(code[:-1], len(code)), expected)

    def test_validate_corrupted_data_digit_rejected(self) -> None:
        # Corrupt a data digit (not the check digit): flipping the second
        # digit 7 -> 9 of the ISBN-13 breaks the mod-10 checksum.
        corrupted = ISBN13_VALID[0] + "9" + ISBN13_VALID[2:]
        self.assertNotEqual(corrupted, ISBN13_VALID)
        self.assertNotEqual(gs1_sum(corrupted) % 10, 0)
        result = self.tool.execute(mode="validate", code=corrupted)
        self.assertFalse(result["valid"])
        self.assertIn("checksum fails", result["reason"])

    # ------------------------------------------------------------------ #
    # validate mode — 13-digit ambiguity: both interpretations reported
    # ------------------------------------------------------------------ #

    def test_validate_13_digit_978_reports_both_interpretations(self) -> None:
        result = self.tool.execute(mode="validate", code=ISBN13_VALID)
        self.assertEqual(
            [i["code_type"] for i in result["interpretations"]],
            ["isbn-13", "ean-13"],
        )
        self.assertTrue(all(i["valid"] for i in result["interpretations"]))
        self.assertIn("both", result["note"])
        self.assertEqual(result["reason"], "valid as isbn-13, ean-13")

    def test_validate_13_digit_non_bookland_is_ean13_only(self) -> None:
        result = self.tool.execute(mode="validate", code=EAN13_VALID)
        self.assertEqual(
            [i["code_type"] for i in result["interpretations"]], ["ean-13"]
        )
        self.assertNotIn("note", result)
        self.assertEqual(result["reason"], "valid as ean-13")

    # ------------------------------------------------------------------ #
    # validate mode — explicit code_type override
    # ------------------------------------------------------------------ #

    def test_validate_explicit_code_type_single_interpretation(self) -> None:
        result = self.tool.execute(
            mode="validate", code=ISBN13_VALID, code_type="ean-13"
        )
        self.assertEqual(result["code_type"], "ean-13")
        self.assertNotIn("auto_detected", result)
        self.assertEqual(len(result["interpretations"]), 1)
        self.assertEqual(result["interpretations"][0]["code_type"], "ean-13")
        self.assertTrue(result["valid"])

    def test_validate_code_type_aliases_accepted(self) -> None:
        for alias in ("ISBN13", "isbn_13", "isbn13", "EAN-13", "upc", "UPC-A"):
            with self.subTest(alias=alias):
                result = self.tool.execute(
                    mode="validate", code=ISBN13_VALID, code_type=alias
                )
                self.assertIn(result["code_type"], self.tool.TYPES)

    def test_validate_explicit_type_length_mismatch(self) -> None:
        result = self.tool.execute(
            mode="validate", code=ISBN10_VALID, code_type="ean-8"
        )
        self.assertFalse(result["valid"])
        item = result["interpretations"][0]
        self.assertIn("expected 8 characters", item["reason"])
        self.assertIn("got 10", item["reason"])

    def test_validate_explicit_isbn13_prefix_rule(self) -> None:
        result = self.tool.execute(
            mode="validate", code=EAN13_VALID, code_type="isbn-13"
        )
        self.assertFalse(result["valid"])
        item = result["interpretations"][0]
        self.assertIn("'978' or '979'", item["reason"])
        # The checksum arithmetic is still shown even when the prefix rule
        # is what makes the interpretation invalid.
        self.assertIn("checksum", item)
        self.assertTrue(item["checksum"].startswith("4*1"))

    # ------------------------------------------------------------------ #
    # validate mode — verdict-level error matrix (never raises)
    # ------------------------------------------------------------------ #

    def test_validate_unknown_length(self) -> None:
        for code in ("030640615", "03064061521", "0" * 6, "0" * 14, "1" * 9):
            with self.subTest(code=code):
                result = self.tool.execute(mode="validate", code=code)
                self.assertFalse(result["valid"])
                self.assertEqual(result["interpretations"], [])
                self.assertIn("unrecognized identifier length", result["reason"])

    def test_validate_invalid_charset(self) -> None:
        cases = [
            "03064O6152",      # letter O instead of zero
            "О306406152",      # Cyrillic capital O
            "0X06406152",      # X in a non-final position
            "978030640615X",   # 13 characters ending in X (14th removed)
            "9638507X",        # X on an 8-character code
            "978-306-40615-X7",  # X followed by a digit
            UNICODE_TEXT_DIGIT + "306406152",
        ]
        for code in cases:
            with self.subTest(code=code):
                result = self.tool.execute(mode="validate", code=code)
                self.assertFalse(result["valid"])
                self.assertEqual(result["interpretations"], [])

    def test_validate_error_messages_mention_position_and_charset(self) -> None:
        result = self.tool.execute(mode="validate", code="03064O6152")
        self.assertIn("'O'", result["reason"])
        self.assertIn("position 6", result["reason"])
        self.assertIn("digits", result["reason"])
        result = self.tool.execute(mode="validate", code="0X06406152")
        self.assertIn("'X' is only allowed", result["reason"])

    # ------------------------------------------------------------------ #
    # check_digit mode
    # ------------------------------------------------------------------ #

    def test_check_digit_partials(self) -> None:
        cases = [
            (ISBN10_VALID[:9], "isbn-10", isbn10_cd(ISBN10_VALID[:9])),
            (ISBN10_X_VALID[:9], "isbn-10", "X"),
            (ISBN13_VALID[:12], "isbn-13/ean-13", "7"),
            (EAN13_VALID[:12], "isbn-13/ean-13", "1"),
            (EAN8_VALID[:7], "ean-8", "4"),
            (UPCA_VALID[:11], "upc-a", "2"),
        ]
        for data, label, expected in cases:
            with self.subTest(data=data):
                result = self.tool.execute(mode="check_digit", code=data)
                self.assertEqual(result["mode"], "check_digit")
                self.assertEqual(result["code_type"], label)
                self.assertEqual(result["data"], data)
                self.assertEqual(result["check_digit"], expected)
                self.assertEqual(result["full_code"], data + expected)
                # Cross-check with the independent helpers.
                if label == "isbn-10":
                    self.assertEqual(isbn10_cd(data), expected)
                    self.assertIn("mod 11", result["arithmetic"])
                else:
                    full = {"ean-8": 8, "upc-a": 12}.get(label, 13)
                    self.assertEqual(gs1_cd(data, full), expected)
                    self.assertIn("mod 10", result["arithmetic"])
                self.assertIn("check digit = ", result["arithmetic"])

    def test_check_digit_x_value_shown_as_ten(self) -> None:
        result = self.tool.execute(mode="check_digit", code="080442957")
        self.assertEqual(result["check_digit"], "X")
        self.assertIn("= 10 -> 'X' (ten)", result["arithmetic"])

    def test_check_digit_full_codes_compared_with_provided(self) -> None:
        # Note: a 12-character input defaults to an ISBN-13/EAN-13
        # *partial* (a full UPC-A needs the explicit code_type), so the
        # auto full-code comparison covers lengths 8 / 10 / 13 only.
        cases = [
            ISBN10_VALID,
            ISBN10_X_VALID,
            ISBN13_VALID,
            EAN8_VALID,
            EAN13_VALID,
        ]
        for code in cases:
            with self.subTest(code=code):
                result = self.tool.execute(mode="check_digit", code=code)
                self.assertEqual(result["provided_check_digit"], code[-1])
                self.assertTrue(result["matches"])
                self.assertEqual(result["full_code"], code)

    def test_check_digit_full_corrupted_code_reports_mismatch(self) -> None:
        corrupted = ISBN13_VALID[:-1] + "8"
        result = self.tool.execute(mode="check_digit", code=corrupted)
        self.assertEqual(result["check_digit"], "7")
        self.assertEqual(result["provided_check_digit"], "8")
        self.assertFalse(result["matches"])

    def test_check_digit_explicit_upc_a_full_code(self) -> None:
        # 12 characters default to an ISBN-13/EAN-13 partial; the explicit
        # type pins them as a full UPC-A instead.
        result = self.tool.execute(
            mode="check_digit", code=UPCA_VALID, code_type="upc-a"
        )
        self.assertEqual(result["code_type"], "upc-a")
        self.assertEqual(result["data"], UPCA_VALID[:11])
        self.assertEqual(result["check_digit"], "2")
        self.assertTrue(result["matches"])

    def test_check_digit_shared_13_note(self) -> None:
        result = self.tool.execute(mode="check_digit", code=ISBN13_VALID[:12])
        self.assertIn("both", result["note"])

    def test_check_digit_error_matrix(self) -> None:
        cases = [
            ("12345", None, "invalid_length"),
            ("0306406152", "ean-8", "invalid_length"),   # 10 chars vs ean-8
            ("030640615", "upc-a", "invalid_length"),    # 9 chars vs upc-a
            ("08044295X", None, "invalid_charset"),      # X mid-partial
            ("0X0640615", None, "invalid_charset"),
            ("03064O615", None, "invalid_charset"),
        ]
        for code, code_type, error_type in cases:
            with self.subTest(code=code, code_type=code_type):
                result = self.tool.execute(
                    mode="check_digit", code=code, code_type=code_type
                )
                self.assertEqual(result["mode"], "check_digit")
                self.assertEqual(result["error"]["type"], error_type)

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def test_convert_isbn10_to_isbn13(self) -> None:
        result = self.tool.execute(mode="convert", code=ISBN10_VALID)
        self.assertEqual(
            result,
            {
                "mode": "convert",
                "input": ISBN10_VALID,
                "from": "isbn-10",
                "to": "isbn-13",
                "result": ISBN13_VALID,
                "note": result["note"],
            },
        )
        self.assertIn("978", result["note"])
        # Independent cross-check of the recomputed check digit.
        self.assertEqual(gs1_cd("978" + ISBN10_VALID[:9], 13), ISBN13_VALID[-1])

    def test_convert_isbn13_to_isbn10(self) -> None:
        result = self.tool.execute(mode="convert", code=ISBN13_VALID)
        self.assertEqual(result["from"], "isbn-13")
        self.assertEqual(result["to"], "isbn-10")
        self.assertEqual(result["result"], ISBN10_VALID)
        self.assertEqual(isbn10_cd(ISBN13_VALID[3:12]), ISBN10_VALID[-1])

    def test_convert_isbn13_to_isbn10_with_x(self) -> None:
        isbn13 = "978" + ISBN10_X_VALID[:9] + gs1_cd("978" + ISBN10_X_VALID[:9], 13)
        self.assertEqual(gs1_sum(isbn13) % 10, 0)  # vector self-check
        result = self.tool.execute(mode="convert", code=isbn13)
        self.assertEqual(result["result"], ISBN10_X_VALID)

    def test_convert_round_trips(self) -> None:
        valid_isbn10s = [
            ISBN10_VALID,
            ISBN10_X_VALID,
            "0439708184",  # self-checked below via the helper
        ]
        for isbn10 in valid_isbn10s:
            self.assertEqual(isbn10_sum(isbn10) % 11, 0)
            with self.subTest(isbn10=isbn10):
                forward = self.tool.execute(mode="convert", code=isbn10)
                back = self.tool.execute(mode="convert", code=forward["result"])
                self.assertEqual(forward["to"], "isbn-13")
                self.assertEqual(back["to"], "isbn-10")
                self.assertEqual(back["result"], isbn10)

    def test_convert_hyphenated_input(self) -> None:
        result = self.tool.execute(mode="convert", code="978-0-306-40615-7")
        self.assertEqual(result["result"], ISBN10_VALID)

    def test_convert_general_ean13_not_convertible(self) -> None:
        result = self.tool.execute(mode="convert", code=EAN13_VALID)
        self.assertEqual(result["error"]["type"], "not_convertible")
        self.assertIn("only EAN-13", result["error"]["message"])

    def test_convert_979_not_convertible(self) -> None:
        code = DATA13_979_MUSIC + gs1_cd(DATA13_979_MUSIC, 13)
        result = self.tool.execute(mode="convert", code=code)
        self.assertEqual(result["error"]["type"], "not_convertible")
        self.assertIn("979", result["error"]["message"])
        self.assertIn("no ISBN-10 equivalent", result["error"]["message"])

    def test_convert_invalid_checksum(self) -> None:
        corrupted13 = ISBN13_VALID[:-1] + "8"
        result = self.tool.execute(mode="convert", code=corrupted13)
        self.assertEqual(result["error"]["type"], "invalid_checksum")
        self.assertIn("'7'", result["error"]["message"])
        corrupted10 = ISBN10_VALID[:-1] + "3"
        result = self.tool.execute(mode="convert", code=corrupted10)
        self.assertEqual(result["error"]["type"], "invalid_checksum")
        self.assertIn("'2'", result["error"]["message"])

    def test_convert_invalid_length_and_charset(self) -> None:
        result = self.tool.execute(mode="convert", code=UPCA_VALID)
        self.assertEqual(result["error"]["type"], "invalid_length")
        result = self.tool.execute(mode="convert", code="03064O6152")
        self.assertEqual(result["error"]["type"], "invalid_charset")

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def test_info_isbn13_english_group(self) -> None:
        result = self.tool.execute(mode="info", code=ISBN13_VALID)
        self.assertEqual(result["input_form"], "isbn-13")
        self.assertEqual(result["isbn13"], ISBN13_VALID)
        self.assertEqual(result["isbn10"], ISBN10_VALID)
        self.assertEqual(result["gs1_prefix"], "978")
        self.assertIn("bookland", result["gs1_prefix_meaning"])
        self.assertEqual(result["registration_group"], "0")
        self.assertIn("English", result["registration_group_meaning"])
        self.assertTrue(result["checksum_valid"])
        self.assertIn("indicative", result["note"])

    def test_info_isbn10_input(self) -> None:
        result = self.tool.execute(mode="info", code=ISBN10_VALID)
        self.assertEqual(result["input_form"], "isbn-10")
        self.assertEqual(result["isbn13"], ISBN13_VALID)
        self.assertEqual(result["isbn10"], ISBN10_VALID)
        self.assertEqual(result["registration_group"], "0")

    def test_info_registration_groups(self) -> None:
        cases = [
            (DATA13_JAPAN, "4", "Japan"),
            (DATA13_RUSSIA, "5", "Russia"),
            (DATA13_FRANCE, "2", "French"),
            (DATA13_GERMANY, "3", "German"),
            (DATA13_CHINA, "7", "China"),
            (DATA13_UNKNOWN_GROUP, "9", "not in the built-in indicative table"),
        ]
        for data, group, meaning in cases:
            code = data + gs1_cd(data, 13)
            with self.subTest(code=code):
                result = self.tool.execute(mode="info", code=code)
                self.assertEqual(result["registration_group"], group)
                self.assertIn(meaning, result["registration_group_meaning"])

    def test_info_979_music_group(self) -> None:
        code = DATA13_979_MUSIC + gs1_cd(DATA13_979_MUSIC, 13)
        result = self.tool.execute(mode="info", code=code)
        self.assertEqual(result["gs1_prefix"], "979")
        self.assertEqual(result["registration_group"], "0")
        self.assertIn("Music", result["registration_group_meaning"])
        # 979 codes have no ISBN-10 equivalent.
        self.assertIsNone(result["isbn10"])

    def test_info_reports_bad_checksum_without_failing(self) -> None:
        corrupted = ISBN13_VALID[:-1] + "8"
        result = self.tool.execute(mode="info", code=corrupted)
        self.assertNotIn("error", result)
        self.assertFalse(result["checksum_valid"])
        self.assertEqual(result["registration_group"], "0")

    def test_info_not_isbn(self) -> None:
        result = self.tool.execute(mode="info", code=EAN13_VALID)
        self.assertEqual(result["error"]["type"], "not_isbn")
        self.assertIn("978 or 979", result["error"]["message"])

    def test_info_invalid_length_and_charset(self) -> None:
        result = self.tool.execute(mode="info", code=UPCA_VALID)
        self.assertEqual(result["error"]["type"], "invalid_length")
        result = self.tool.execute(mode="info", code="03064O6152")
        self.assertEqual(result["error"]["type"], "invalid_charset")

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict parameter validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="validate!", code=ISBN13_VALID)
        self.assert_invalid(mode=None, code=ISBN13_VALID)
        self.assert_invalid(mode=123, code=ISBN13_VALID)

    def test_invalid_code(self) -> None:
        for bad in (None, 123, True, b"9780306406157", ["x"], "", "   ", "---"):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="validate", code=bad)

    def test_code_length_limit(self) -> None:
        self.assert_invalid(mode="validate", code="0" * 65)
        ok = self.tool.execute(mode="validate", code="0" * 8)
        self.assertIn("valid", ok)

    def test_invalid_code_type(self) -> None:
        for bad in ("isbn", "ean", "foo", 123, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="validate", code=ISBN13_VALID, code_type=bad
                )

    def test_code_type_rejected_for_convert_and_info(self) -> None:
        self.assert_invalid(mode="convert", code=ISBN13_VALID, code_type="isbn-13")
        self.assert_invalid(mode="info", code=ISBN13_VALID, code_type="isbn-13")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectBarcodeValidatorTool, BarcodeValidatorTool)
        self.assertEqual(self.tool.name, "barcode_validator_tool")
        self.assertIn("ISBN", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("BarcodeValidatorTool", __all__)


if __name__ == "__main__":
    unittest.main()
