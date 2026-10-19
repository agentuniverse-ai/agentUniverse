#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: test_phone_format_tool.py

"""Offline unit tests for PhoneFormatTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: each format handling path (international '+', '00'
prefix, national trunk-0 stripping per region, bare digits, NANP
10-digit validation, 7-15 digit bounds) is checked against literal
expected values, classify against the documented longest-prefix /
digit-bound / China-mobile-heuristic ground truths, and extract against
texts with known phone positions, date guards and arithmetic guards.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import PhoneFormatTool
from agentuniverse.agent.action.tool.common_tool.phone_format_tool import (
    PhoneFormatTool as DirectPhoneFormatTool,
)


class PhoneFormatToolFormatTest(unittest.TestCase):
    """Offline deterministic test cases for the format mode."""

    def setUp(self) -> None:
        self.tool = PhoneFormatTool()

    # ------------------------------------------------------------------ #
    # Separator stripping and already-international input
    # ------------------------------------------------------------------ #

    def test_international_with_separators_untouched(self) -> None:
        result = self.tool.execute(mode="format", phone="+86 138 1234 5678")
        self.assertEqual(result["result"], "+8613812345678")
        self.assertEqual(result["e164"], "+8613812345678")
        self.assertEqual(result["output"], "e164")

    def test_international_ignores_region_no_rewrite(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+14155552671", default_region="GB"
        )
        self.assertEqual(result["result"], "+14155552671")

    def test_separators_dashes_dots_parens_spaces(self) -> None:
        for raw in (
            "+86-138-1234-5678",
            "+86.138.1234.5678",
            "+86 (138) 1234 5678",
            " +8613812345678 ",
        ):
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="format", phone=raw)
                self.assertEqual(result["result"], "+8613812345678")

    def test_double_zero_prefix_replaced_with_plus(self) -> None:
        result = self.tool.execute(
            mode="format", phone="0086 138 1234 5678"
        )
        self.assertEqual(result["result"], "+8613812345678")

    def test_double_zero_contiguous(self) -> None:
        result = self.tool.execute(mode="format", phone="00442079460958")
        self.assertEqual(result["result"], "+442079460958")

    # ------------------------------------------------------------------ #
    # National trunk-0 stripping per region
    # ------------------------------------------------------------------ #

    def test_national_zero_stripped_for_cn_landline(self) -> None:
        result = self.tool.execute(
            mode="format", phone="0371 1234 1234", default_region="CN"
        )
        self.assertEqual(result["result"], "+8637112341234")

    def test_national_zero_stripped_for_gb(self) -> None:
        result = self.tool.execute(
            mode="format", phone="020 7946 0958", default_region="GB"
        )
        self.assertEqual(result["result"], "+442079460958")

    def test_national_zero_stripped_for_de(self) -> None:
        result = self.tool.execute(
            mode="format", phone="030 1234567", default_region="DE"
        )
        self.assertEqual(result["result"], "+49301234567")

    def test_russian_trunk_is_eight_not_zero(self) -> None:
        result = self.tool.execute(
            mode="format", phone="8 495 123-45-67", default_region="RU"
        )
        self.assertEqual(result["result"], "+74951234567")

    def test_bare_digits_get_dial_code(self) -> None:
        result = self.tool.execute(
            mode="format", phone="13812345678", default_region="CN"
        )
        self.assertEqual(result["result"], "+8613812345678")

    def test_bare_digits_with_redundant_trunk_zero(self) -> None:
        result = self.tool.execute(
            mode="format", phone="013812345678", default_region="CN"
        )
        self.assertEqual(result["result"], "+8613812345678")

    def test_bare_digits_already_carrying_dial_code(self) -> None:
        result = self.tool.execute(
            mode="format", phone="1-415-555-2671", default_region="US"
        )
        self.assertEqual(result["result"], "+14155552671")

    def test_region_code_case_insensitive(self) -> None:
        result = self.tool.execute(
            mode="format", phone="020 7946 0958", default_region=" gb "
        )
        self.assertEqual(result["result"], "+442079460958")

    def test_dial_code_table_spot_checks(self) -> None:
        cases = [
            ("98765 43210", "IN", "+919876543210"),
            ("3-1234-5678", "JP", "+81312345678"),
            ("02-1234-5678", "KR", "+82212345678"),
            ("912345678", "HK", "+852912345678"),
            ("0491 570 156", "AU", "+61491570156"),
            ("050-1234-5678", "AE", "+9715012345678"),
        ]
        for raw, region, expected in cases:
            with self.subTest(raw=raw):
                result = self.tool.execute(
                    mode="format", phone=raw, default_region=region
                )
                self.assertEqual(result["result"], expected)

    # ------------------------------------------------------------------ #
    # NANP validation and E.164 digit bounds
    # ------------------------------------------------------------------ #

    def test_nanp_ten_digit_forms(self) -> None:
        for raw in ("(415) 555-2671", "415-555-2671", "415.555.2671"):
            with self.subTest(raw=raw):
                result = self.tool.execute(
                    mode="format", phone=raw, default_region="US"
                )
                self.assertEqual(result["result"], "+14155552671")

    def test_nanp_nine_digits_rejected(self) -> None:
        result = self.tool.execute(
            mode="format", phone="415-555-267", default_region="US"
        )
        self.assertEqual(result["error"]["type"], "invalid_nanp")
        self.assertIn("10 digits", result["error"]["message"])

    def test_nanp_international_nine_digits_rejected(self) -> None:
        result = self.tool.execute(mode="format", phone="+1 315 555 267")
        self.assertEqual(result["error"]["type"], "invalid_nanp")

    def test_seven_digit_lower_bound_accepted(self) -> None:
        # Not '+1'-lead: a +1 number must be exactly 11 digits (NANP).
        result = self.tool.execute(mode="format", phone="+2345678")
        self.assertEqual(result["result"], "+2345678")

    def test_six_digits_rejected(self) -> None:
        result = self.tool.execute(mode="format", phone="+234567")
        self.assertEqual(result["error"]["type"], "invalid_length")

    def test_fifteen_digit_upper_bound_accepted(self) -> None:
        result = self.tool.execute(mode="format", phone="+234567890123456")
        self.assertEqual(result["result"], "+234567890123456")

    def test_sixteen_digits_rejected(self) -> None:
        result = self.tool.execute(mode="format", phone="+2345678901234567")
        self.assertEqual(result["error"]["type"], "invalid_length")

    # ------------------------------------------------------------------ #
    # Output variants: display and national
    # ------------------------------------------------------------------ #

    def test_display_cn_mobile_grouping(self) -> None:
        result = self.tool.execute(
            mode="format",
            phone="13812345678",
            default_region="CN",
            output="display",
        )
        self.assertEqual(result["result"], "+86 138 1234 5678")

    def test_display_nanp_grouping(self) -> None:
        result = self.tool.execute(
            mode="format",
            phone="(415) 555-2671",
            default_region="US",
            output="display",
        )
        self.assertEqual(result["result"], "+1 415 555 2671")

    def test_display_other_regions_single_space(self) -> None:
        result = self.tool.execute(
            mode="format",
            phone="020 7946 0958",
            default_region="GB",
            output="display",
        )
        self.assertEqual(result["result"], "+44 2079460958")

    def test_display_three_digit_dial_code(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+852 1234 5678", output="display"
        )
        self.assertEqual(result["result"], "+852 12345678")

    def test_national_gb_adds_trunk_zero(self) -> None:
        result = self.tool.execute(
            mode="format",
            phone="020 7946 0958",
            default_region="GB",
            output="national",
        )
        self.assertEqual(result["result"], "02079460958")

    def test_national_cn_mobile_has_no_trunk_zero(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+8613812345678", output="national"
        )
        self.assertEqual(result["result"], "13812345678")

    def test_national_cn_landline_adds_trunk_zero(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+8637112341234", output="national"
        )
        self.assertEqual(result["result"], "037112341234")

    def test_national_nanp_has_no_trunk(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+14155552671", output="national"
        )
        self.assertEqual(result["result"], "4155552671")

    def test_national_russia_trunk_is_eight(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+74951234567", output="national"
        )
        self.assertEqual(result["result"], "84951234567")

    def test_national_unknown_dial_code(self) -> None:
        result = self.tool.execute(
            mode="format", phone="+35891234567", output="national"
        )
        self.assertEqual(result["error"]["type"], "unknown_dial_code")

    # ------------------------------------------------------------------ #
    # Structured error payloads (content-level failures)
    # ------------------------------------------------------------------ #

    def test_region_required_for_bare_input(self) -> None:
        result = self.tool.execute(mode="format", phone="13812345678")
        self.assertEqual(result["mode"], "format")
        self.assertEqual(result["error"]["type"], "region_required")
        self.assertIn("CN", result["error"]["message"])

    def test_unknown_region(self) -> None:
        for bad in ("XX", "USA", "usa"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="format", phone="13812345678", default_region=bad
                )
                self.assertEqual(result["error"]["type"], "unknown_region")

    def test_letters_rejected(self) -> None:
        for bad in ("138x12345678", "call me", "+86 138x1234", "138-1234 ext.9"):
            with self.subTest(bad=bad):
                result = self.tool.execute(
                    mode="format", phone=bad, default_region="CN"
                )
                self.assertEqual(result["error"]["type"], "invalid_characters")

    def test_plus_only_rejected(self) -> None:
        result = self.tool.execute(mode="format", phone="+")
        self.assertEqual(result["error"]["type"], "invalid_characters")


class PhoneFormatToolClassifyTest(unittest.TestCase):
    """Offline deterministic test cases for the classify mode."""

    def setUp(self) -> None:
        self.tool = PhoneFormatTool()

    def test_longest_prefix_beats_shared_one(self) -> None:
        # +1 264 is Anguilla (AI); the bare shared +1 code is US/CA.
        result = self.tool.execute(mode="classify", phone="+12644971234")
        self.assertEqual(result["region_guess"], "AI")
        self.assertEqual(result["matched_prefix"], "1264")
        self.assertEqual(result["e164"], "+12644971234")

    def test_shared_one_resolves_to_us_ca(self) -> None:
        result = self.tool.execute(mode="classify", phone="+14155552671")
        self.assertEqual(result["region_guess"], "US/CA")
        self.assertEqual(result["matched_prefix"], "1")

    def test_extended_nanp_other_entries(self) -> None:
        result = self.tool.execute(mode="classify", phone="+18765551234")
        self.assertEqual(result["region_guess"], "JM")
        result = self.tool.execute(mode="classify", phone="+16715551234")
        self.assertEqual(result["region_guess"], "GU")

    def test_cn(self) -> None:
        result = self.tool.execute(mode="classify", phone="+8613812345678")
        self.assertEqual(result["region_guess"], "CN")
        self.assertEqual(result["matched_prefix"], "86")
        self.assertEqual(result["cn_mobile_heuristic"], True)

    def test_cn_landline_is_not_mobile_heuristic(self) -> None:
        result = self.tool.execute(mode="classify", phone="+8637112341234")
        self.assertEqual(result["region_guess"], "CN")
        self.assertEqual(result["cn_mobile_heuristic"], False)

    def test_shared_seven_resolves_to_ru_kz(self) -> None:
        result = self.tool.execute(mode="classify", phone="+74951234567")
        self.assertEqual(result["region_guess"], "RU/KZ")

    def test_three_digit_dial_code_hong_kong(self) -> None:
        result = self.tool.execute(mode="classify", phone="+85212345678")
        self.assertEqual(result["region_guess"], "HK")
        self.assertEqual(result["matched_prefix"], "852")

    def test_unknown_dial_code_reports_none(self) -> None:
        result = self.tool.execute(mode="classify", phone="+35891234567")
        self.assertIsNone(result["region_guess"])
        self.assertIsNone(result["matched_prefix"])
        self.assertEqual(result["digit_count_valid"], True)

    def test_digit_count_bounds(self) -> None:
        cases = [
            ("+1234567", 7, True),
            ("+123456789012345", 15, True),
            ("+123456", 6, False),
            ("+1234567890123456", 16, False),
        ]
        for raw, count, valid in cases:
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="classify", phone=raw)
                self.assertEqual(result["digit_count"], count)
                self.assertEqual(result["digit_count_valid"], valid)

    def test_double_zero_accepted(self) -> None:
        result = self.tool.execute(mode="classify", phone="008613812345678")
        self.assertEqual(result["region_guess"], "CN")
        self.assertEqual(result["e164"], "+8613812345678")

    def test_separators_accepted(self) -> None:
        result = self.tool.execute(mode="classify", phone="+1 (415) 555-2671")
        self.assertEqual(result["region_guess"], "US/CA")
        self.assertEqual(result["e164"], "+14155552671")

    def test_bare_number_rejected_as_not_international(self) -> None:
        result = self.tool.execute(mode="classify", phone="442079460958")
        self.assertEqual(result["error"]["type"], "not_international")

    def test_letters_rejected(self) -> None:
        result = self.tool.execute(mode="classify", phone="+86138x12345678")
        self.assertEqual(result["error"]["type"], "invalid_characters")


class PhoneFormatToolExtractTest(unittest.TestCase):
    """Offline deterministic test cases for the extract mode."""

    def setUp(self) -> None:
        self.tool = PhoneFormatTool()

    def test_extract_international_with_separators(self) -> None:
        result = self.tool.execute(
            mode="extract", text="Contact: +86 138 1234 5678 for details."
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["result"], ["+8613812345678"])
        self.assertEqual(result["phones"][0]["raw"], "+86 138 1234 5678")

    def test_extract_cn_mobile_run(self) -> None:
        result = self.tool.execute(
            mode="extract", text="ID 13812345678 end"
        )
        self.assertEqual(result["result"], ["+8613812345678"])
        self.assertEqual(result["phones"][0]["region"], "CN")

    def test_extract_multiple_phones_in_order(self) -> None:
        result = self.tool.execute(
            mode="extract",
            text="Call +86 138 1234 5678 or 13812345678 later.",
        )
        self.assertEqual(
            result["result"], ["+8613812345678", "+8613812345678"]
        )

    def test_extract_nanp_paren_shape(self) -> None:
        result = self.tool.execute(
            mode="extract", text="Call (415) 555-2671 today."
        )
        self.assertEqual(result["result"], ["+14155552671"])
        self.assertEqual(result["phones"][0]["region"], "US")

    def test_extract_nanp_dashed_shape(self) -> None:
        result = self.tool.execute(
            mode="extract", text="Office: 415-555-2671, ask for Bob."
        )
        self.assertEqual(result["result"], ["+14155552671"])

    def test_extract_with_default_region(self) -> None:
        result = self.tool.execute(
            mode="extract",
            text="call 020 7946 0958 tomorrow",
            default_region="GB",
        )
        self.assertEqual(result["result"], ["+442079460958"])

    def test_extract_cn_landline_with_region(self) -> None:
        result = self.tool.execute(
            mode="extract",
            text="tel 0371-1234-1234 or 0371 1234 1235",
            default_region="CN",
        )
        self.assertEqual(
            result["result"], ["+8637112341234", "+8637112341235"]
        )

    def test_extract_date_guard(self) -> None:
        result = self.tool.execute(
            mode="extract", text="On 2023-01-15 we shipped the release."
        )
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["result"], [])

    def test_extract_date_guard_us_order(self) -> None:
        result = self.tool.execute(
            mode="extract", text="Signed 01/15/2023 by the notary."
        )
        self.assertEqual(result["count"], 0)

    def test_extract_arithmetic_operand_guard(self) -> None:
        result = self.tool.execute(
            mode="extract", text="3 +86 137 1234 5678 was the total."
        )
        self.assertEqual(result["count"], 0)

    def test_extract_arithmetic_assignment_guard(self) -> None:
        result = self.tool.execute(
            mode="extract", text="growth = 44 123 456 7890 per year"
        )
        self.assertEqual(result["count"], 0)

    def test_extract_arithmetic_continuation_guard(self) -> None:
        result = self.tool.execute(
            mode="extract", text="total 415 555 2671 = 12 items"
        )
        self.assertEqual(result["count"], 0)

    def test_extract_date_alongside_phone(self) -> None:
        result = self.tool.execute(
            mode="extract",
            text="On 2023-01-15 call +86 138 1234 5678.",
        )
        self.assertEqual(result["result"], ["+8613812345678"])

    def test_extract_unresolvable_candidate_reports_error(self) -> None:
        result = self.tool.execute(
            mode="extract", text="Ref 1234 5678 on file"
        )
        self.assertEqual(result["count"], 1)
        self.assertNotIn("e164", result["phones"][0])
        self.assertEqual(result["phones"][0]["error"]["type"], "region_required")
        self.assertEqual(result["result"], [])

    def test_extract_no_loose_contiguous_runs(self) -> None:
        # Loose 10-digit contiguous runs are deliberately not matched.
        result = self.tool.execute(mode="extract", text="Order 1234567890 x2")
        self.assertEqual(result["count"], 0)

    def test_extract_overlapping_candidates_deduped(self) -> None:
        result = self.tool.execute(
            mode="extract", text="call +8613812345678 now"
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["result"], ["+8613812345678"])

    def test_extract_empty_result_context(self) -> None:
        result = self.tool.execute(mode="extract", text="no numbers here")
        self.assertEqual(result["mode"], "extract")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["phones"], [])


class PhoneFormatToolValidationTest(unittest.TestCase):
    """Parameter-level validation errors (raise ValueError)."""

    def setUp(self) -> None:
        self.tool = PhoneFormatTool()

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="fmt", phone="+1234567")
        self.assert_invalid(mode=None, phone="+1234567")
        self.assert_invalid(mode=123, phone="+1234567")

    def test_invalid_phone_type(self) -> None:
        for bad in (None, 123, True, b"+1234567", ["+1234567"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="format", phone=bad)
                self.assert_invalid(mode="classify", phone=bad)

    def test_empty_phone_rejected(self) -> None:
        self.assert_invalid(mode="format", phone="")
        self.assert_invalid(mode="format", phone="   ")
        self.assert_invalid(mode="classify", phone="")

    def test_phone_length_limit(self) -> None:
        oversized = "+" + "2" * 70
        self.assert_invalid(mode="format", phone=oversized)
        ok = self.tool.execute(mode="format", phone="+" + "2" * 9)
        self.assertEqual(ok["result"], "+" + "2" * 9)

    def test_invalid_output(self) -> None:
        for bad in ("int", "E164", 123, True):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="format", phone="+1234567", output=bad
                )

    def test_invalid_region_type(self) -> None:
        for bad in (123, True, ["CN"]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="format", phone="13812345678", default_region=bad
                )

    def test_invalid_text_type(self) -> None:
        for bad in (None, 123, True, ["call me"]):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="extract", text=bad)

    def test_empty_text_rejected(self) -> None:
        self.assert_invalid(mode="extract", text="")

    def test_text_length_limit(self) -> None:
        self.assert_invalid(mode="extract", text="a" * 100_001)
        ok = self.tool.execute(
            mode="extract", text="a" * 100_000, default_region="CN"
        )
        self.assertEqual(ok["count"], 0)


class PhoneFormatToolPackagingTest(unittest.TestCase):
    """Class defaults, exports and table sanity."""

    def setUp(self) -> None:
        self.tool = PhoneFormatTool()

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectPhoneFormatTool, PhoneFormatTool)
        self.assertEqual(self.tool.name, "phone_format_tool")
        self.assertIn("E.164", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("PhoneFormatTool", __all__)

    def test_dial_code_table_has_documented_regions(self) -> None:
        regions = set()
        for entry in PhoneFormatTool.DIAL_CODES.values():
            regions.update(entry["regions"])
        self.assertEqual(
            regions,
            {
                "US", "CA", "RU", "KZ", "GB", "DE", "FR", "IT", "ES", "BR",
                "MX", "IN", "JP", "KR", "CN", "HK", "SG", "AU", "NZ", "IL",
                "AE", "TR",
            },
        )
        self.assertEqual(len(PhoneFormatTool.DIAL_CODES), 20)

    def test_deterministic_repeat_calls(self) -> None:
        first = self.tool.execute(
            mode="format", phone="0371 1234 1234", default_region="CN"
        )
        second = self.tool.execute(
            mode="format", phone="0371 1234 1234", default_region="CN"
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
