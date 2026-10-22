#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_roman_numeral_tool.py

"""Offline unit tests for RomanNumeralTool.

The tool is built purely on the standard library and never touches the
network, so this suite runs fully offline. Every assertion is
deterministic: the converter is checked against literal spot vectors,
a round-trip loop covers the entire representable range 1-3999, the
non-canonical rejection matrix asserts the exact violated rule cited
in each message, and the arithmetic modes are checked against known
sums / differences / products including out-of-range results.
"""

import random
import unittest

from agentuniverse.agent.action.tool.common_tool import RomanNumeralTool
from agentuniverse.agent.action.tool.common_tool.roman_numeral_tool import (
    RomanNumeralTool as DirectRomanNumeralTool,
)

# --------------------------------------------------------------------- #
# Literal spot vectors (independent of the implementation under test)
# --------------------------------------------------------------------- #
SPOT_VECTORS = [
    (1, "I"),
    (4, "IV"),
    (9, "IX"),
    (14, "XIV"),
    (40, "XL"),
    (58, "LVIII"),
    (90, "XC"),
    (400, "CD"),
    (444, "CDXLIV"),
    (999, "CMXCIX"),
    (1900, "MCM"),
    (1954, "MCMLIV"),
    (1990, "MCMXC"),
    (1999, "MCMXCIX"),
    (2026, "MMXXVI"),
    (3549, "MMMDXLIX"),
    (3888, "MMMDCCCLXXXVIII"),  # longest canonical numeral: 15 chars
    (3999, "MMMCMXCIX"),
]

# --------------------------------------------------------------------- #
# Independent per-digit reference encoder (distinct algorithm from the
# tool's greedy value table), used by the mutation-invariant test.
# --------------------------------------------------------------------- #
_REF_THOUSANDS = ("", "M", "MM", "MMM")
_REF_HUNDREDS = (
    "", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM",
)
_REF_TENS = ("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC")
_REF_ONES = ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")


def _ref_encode(value: int) -> str:
    return (
        _REF_THOUSANDS[value // 1000]
        + _REF_HUNDREDS[value // 100 % 10]
        + _REF_TENS[value // 10 % 10]
        + _REF_ONES[value % 10]
    )


def _ref_scan(numeral: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for index, symbol in enumerate(numeral):
        if (
            index + 1 < len(numeral)
            and values[symbol] < values[numeral[index + 1]]
        ):
            total -= values[symbol]
        else:
            total += values[symbol]
    return total


def _ref_is_canonical(numeral: str) -> bool:
    if not numeral or any(ch not in "MDCLXVI" for ch in numeral):
        return False
    value = _ref_scan(numeral)
    return 1 <= value <= 3999 and numeral == _ref_encode(value)


class RomanNumeralToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib RomanNumeralTool."""

    def setUp(self) -> None:
        self.tool = RomanNumeralTool()

    # ------------------------------------------------------------------ #
    # to_roman mode
    # ------------------------------------------------------------------ #

    def test_to_roman_spot_vectors(self) -> None:
        for value, expected in SPOT_VECTORS:
            with self.subTest(value=value):
                result = self.tool.execute(mode="to_roman", number=value)
                self.assertEqual(
                    result,
                    {"mode": "to_roman", "input": value, "result": expected},
                )

    def test_to_roman_accepts_pure_digit_string(self) -> None:
        result = self.tool.execute(mode="to_roman", number="1954")
        self.assertEqual(result["input"], "1954")
        self.assertEqual(result["result"], "MCMLIV")

    def test_to_roman_is_deterministic(self) -> None:
        first = self.tool.execute(mode="to_roman", number=3999)["result"]
        second = self.tool.execute(mode="to_roman", number=3999)["result"]
        self.assertEqual(first, second)

    def test_to_roman_output_is_strictly_subtractive(self) -> None:
        # The canonical encoding never needs more than one subtractive
        # pair per decimal digit and never four identical symbols in a row.
        for value, expected in SPOT_VECTORS:
            numeral = self.tool.execute(mode="to_roman", number=value)["result"]
            self.assertEqual(numeral, expected)
            for bad in ("IIII", "VV", "XXXX", "LL", "CCCC", "DD", "MMMM"):
                self.assertNotIn(bad, numeral)

    # ------------------------------------------------------------------ #
    # from_roman mode
    # ------------------------------------------------------------------ #

    def test_from_roman_spot_vectors(self) -> None:
        for value, numeral in SPOT_VECTORS:
            with self.subTest(numeral=numeral):
                result = self.tool.execute(mode="from_roman", numeral=numeral)
                self.assertEqual(
                    result,
                    {"mode": "from_roman", "input": numeral, "result": value},
                )

    def test_from_roman_case_insensitive(self) -> None:
        for raw in ("mcmxcix", "McMxCiX", "MCMXCIX", "mCmXcIx"):
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="from_roman", numeral=raw)
                self.assertEqual(result["input"], raw)
                self.assertEqual(result["result"], 1999)

    # ------------------------------------------------------------------ #
    # Round trip over the entire representable range 1-3999
    # ------------------------------------------------------------------ #

    def test_round_trip_entire_range(self) -> None:
        for value in range(1, 4000):
            numeral = self.tool.execute(mode="to_roman", number=value)["result"]
            back = self.tool.execute(mode="from_roman", numeral=numeral)
            if back.get("result") != value or "error" in back:
                self.fail(
                    f"round trip failed for {value}: {numeral!r} -> {back}"
                )
            lowered = self.tool.execute(
                mode="from_roman", numeral=numeral.lower()
            )
            self.assertEqual(
                lowered.get("result"),
                value,
                f"lowercase round trip failed for {value}: {numeral!r}",
            )

    def test_round_trip_round_trip_is_identity_on_numerals(self) -> None:
        for value in range(1, 4000):
            numeral = self.tool.execute(mode="to_roman", number=value)["result"]
            again = self.tool.execute(
                mode="to_roman",
                number=self.tool.execute(
                    mode="from_roman", numeral=numeral
                )["result"],
            )["result"]
            self.assertEqual(again, numeral)

    def test_single_character_mutation_invariant(self) -> None:
        # Every single-character mutation (one symbol inserted, deleted
        # or duplicated at any position) of a canonical numeral must
        # either be canonical itself — and then parse to exactly its own
        # value against the independent reference — or be rejected as
        # invalid_roman with a rule citation. A mutation is never
        # accepted with a wrong value or rejected when canonical.
        # Deterministic bounded sample of the exhaustive sweep.
        rng = random.Random(20261019)
        accepted = rejected = 0
        for value in sorted(rng.sample(range(1, 4000), 40)):
            base = _ref_encode(value)
            mutations = set()
            for pos in range(len(base) + 1):
                for symbol in "IVXLCDM":
                    mutations.add(base[:pos] + symbol + base[pos:])
            for pos in range(len(base)):
                mutations.add(base[:pos] + base[pos + 1:])
                mutations.add(base[:pos] + base[pos] * 2 + base[pos + 1:])
            for mutation in sorted(mutations):
                if not mutation:
                    # Deleting the only character of a one-symbol
                    # numeral leaves the empty string, which is a
                    # malformed parameter (ValueError) by contract.
                    with self.assertRaises(ValueError):
                        self.tool.execute(mode="from_roman", numeral=mutation)
                    continue
                result = self.tool.execute(
                    mode="from_roman", numeral=mutation
                )
                if _ref_is_canonical(mutation):
                    accepted += 1
                    self.assertEqual(
                        result.get("result"),
                        _ref_scan(mutation),
                        msg=mutation,
                    )
                else:
                    rejected += 1
                    self.assertNotIn("result", result, msg=mutation)
                    self.assertEqual(
                        result["error"]["type"],
                        "invalid_roman",
                        msg=mutation,
                    )
                    self.assertRegex(
                        result["error"]["message"], r"rule [1-4] ", msg=mutation
                    )
        # The sample exercises both directions of the invariant.
        self.assertGreater(accepted, 0)
        self.assertGreater(rejected, 0)

    # ------------------------------------------------------------------ #
    # Non-canonical rejection matrix with rule citations
    # ------------------------------------------------------------------ #

    def assert_invalid_roman(self, raw: str, *fragments: str) -> None:
        result = self.tool.execute(mode="from_roman", numeral=raw)
        self.assertEqual(result["mode"], "from_roman")
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["type"], "invalid_roman")
        for fragment in fragments:
            self.assertIn(fragment, result["error"]["message"])

    def test_non_canonical_repetition_of_repeatable_symbols(self) -> None:
        # I, X, C, M may appear at most three times in a row.
        for raw in ("IIII", "XVIIII", "XXXX", "LXXXX", "CCCC", "DCCCC", "MMMM"):
            with self.subTest(raw=raw):
                self.assert_invalid_roman(
                    raw, "rule 2 (repetition)", "at most three times"
                )

    def test_non_canonical_never_repeat_symbols(self) -> None:
        # V, L, D may never repeat.
        for raw in ("VV", "XVV", "LL", "CCLL", "DD", "MDD"):
            with self.subTest(raw=raw):
                self.assert_invalid_roman(raw, "rule 2 (repetition)", "never repeat")

    def test_non_canonical_illegal_subtraction_pairs(self) -> None:
        # I may only be subtracted from V or X.
        self.assert_invalid_roman("IM", "rule 3 (subtraction)", "'I'", "'V' or 'X'")
        self.assert_invalid_roman("IL", "rule 3 (subtraction)", "'I'", "'V' or 'X'")
        self.assert_invalid_roman("IC", "rule 3 (subtraction)")
        self.assert_invalid_roman("ID", "rule 3 (subtraction)")
        # X may only be subtracted from L or C.
        self.assert_invalid_roman("XD", "rule 3 (subtraction)", "'X'", "'L' or 'C'")
        self.assert_invalid_roman("XM", "rule 3 (subtraction)", "'X'", "'L' or 'C'")
        # V, L, D (and M) may never be subtracted at all.
        self.assert_invalid_roman("VX", "rule 3 (subtraction)", "never", "be subtracted")
        self.assert_invalid_roman("VL", "rule 3 (subtraction)", "never", "be subtracted")
        self.assert_invalid_roman("LC", "rule 3 (subtraction)", "never", "be subtracted")
        self.assert_invalid_roman("DM", "rule 3 (subtraction)", "never", "be subtracted")

    def test_non_canonical_symbol_violation(self) -> None:
        for raw in ("ABC", "X I", "XI ", "  ", "I+I", "N", "Ⅵ", "hello"):
            with self.subTest(raw=raw):
                self.assert_invalid_roman(raw, "rule 1 (symbols)")

    def test_non_canonical_not_the_canonical_encoding(self) -> None:
        # Valid pairs and repetitions, but not the canonical encoding.
        self.assert_invalid_roman(
            "IXX", "rule 4 (canonical form)", "19 in canonical form is 'XIX'"
        )
        self.assert_invalid_roman(
            "CMM", "rule 4 (canonical form)", "1900 in canonical form is 'MCM'"
        )
        self.assert_invalid_roman(
            "XIVI", "rule 4 (canonical form)", "15 in canonical form is 'XV'"
        )
        self.assert_invalid_roman(
            "iviv".upper(), "rule 4 (canonical form)"
        )

    def test_non_canonical_value_out_of_range(self) -> None:
        # MMMCMCM scans to 4800: legal pairs, no over-repetition, but
        # outside the classical 1-3999 range.
        self.assert_invalid_roman("MMMCMCM", "rule 4 (range)", "1-3999", "4800")

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def test_validate_accepts_canonical_numerals(self) -> None:
        result = self.tool.execute(mode="validate", numeral="MCMLIV")
        self.assertEqual(
            result,
            {
                "mode": "validate",
                "input": "MCMLIV",
                "valid": True,
                "value": 1954,
                "canonical": "MCMLIV",
                "reason": "canonical strict subtractive notation for 1954",
            },
        )

    def test_validate_returns_canonical_uppercase_for_lowercase(self) -> None:
        result = self.tool.execute(mode="validate", numeral="mcmxcix")
        self.assertTrue(result["valid"])
        self.assertEqual(result["value"], 1999)
        self.assertEqual(result["canonical"], "MCMXCIX")

    def test_validate_rejects_with_reason(self) -> None:
        cases = {
            "IIII": "rule 2 (repetition)",
            "IM": "rule 3 (subtraction)",
            "VX": "rule 3 (subtraction)",
            "ZZ": "rule 1 (symbols)",
            "IXX": "rule 4 (canonical form)",
        }
        for raw, fragment in cases.items():
            with self.subTest(raw=raw):
                result = self.tool.execute(mode="validate", numeral=raw)
                self.assertEqual(result["mode"], "validate")
                self.assertIs(result["valid"], False)
                self.assertNotIn("value", result)
                self.assertIn(fragment, result["reason"])

    def test_validate_agrees_with_from_roman_over_entire_range(self) -> None:
        for value in range(1, 4000, 97):  # deterministic sample of the range
            numeral = self.tool.execute(mode="to_roman", number=value)["result"]
            verdict = self.tool.execute(mode="validate", numeral=numeral)
            self.assertTrue(verdict["valid"])
            self.assertEqual(verdict["value"], value)

    # ------------------------------------------------------------------ #
    # Arithmetic modes
    # ------------------------------------------------------------------ #

    def test_add_known_results(self) -> None:
        result = self.tool.execute(mode="add", a="X", b="IX")
        self.assertEqual(
            result,
            {
                "mode": "add",
                "a": "X",
                "b": "IX",
                "a_value": 10,
                "b_value": 9,
                "expression": "10 + 9 = 19",
                "result": "XIX",
                "value": 19,
            },
        )

    def test_subtract_known_results(self) -> None:
        result = self.tool.execute(mode="subtract", a="M", b="I")
        self.assertEqual(result["result"], "CMXCIX")
        self.assertEqual(result["value"], 999)
        self.assertEqual(result["expression"], "1000 - 1 = 999")

    def test_multiply_known_results(self) -> None:
        result = self.tool.execute(mode="multiply", a="XL", b="XC")
        self.assertEqual(result["a_value"], 40)
        self.assertEqual(result["b_value"], 90)
        self.assertEqual(result["value"], 3600)
        self.assertEqual(result["result"], "MMMDC")
        self.assertEqual(result["expression"], "40 * 90 = 3600")

    def test_arithmetic_identity_and_boundaries(self) -> None:
        one = self.tool.execute(mode="multiply", a="I", b="I")
        self.assertEqual(one["result"], "I")
        self.assertEqual(one["value"], 1)
        top = self.tool.execute(mode="add", a="MMM", b="CMXCIX")
        self.assertEqual(top["result"], "MMMCMXCIX")
        self.assertEqual(top["value"], 3999)

    def test_arithmetic_case_insensitive_operands(self) -> None:
        result = self.tool.execute(mode="add", a="m", b="M")
        self.assertEqual(result["result"], "MM")
        self.assertEqual(result["value"], 2000)

    def test_arithmetic_round_trip_against_integer_math(self) -> None:
        triples = [("XX", "VII", "add"), ("C", "XL", "subtract"), ("XIV", "III", "multiply")]
        expected = {"add": 27, "subtract": 60, "multiply": 42}
        for x, y, mode in triples:
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, a=x, b=y)
                self.assertEqual(result["value"], expected[mode])
                again = self.tool.execute(mode="from_roman", numeral=result["result"])
                self.assertEqual(again["result"], expected[mode])

    def test_arithmetic_out_of_range_zero(self) -> None:
        result = self.tool.execute(mode="subtract", a="I", b="I")
        self.assertEqual(result["mode"], "subtract")
        self.assertEqual(result["error"]["type"], "out_of_range")
        self.assertIn("0", result["error"]["message"])
        self.assertIn("1-3999", result["error"]["message"])

    def test_arithmetic_out_of_range_negative(self) -> None:
        result = self.tool.execute(mode="subtract", a="X", b="M")
        self.assertEqual(result["error"]["type"], "out_of_range")
        self.assertIn("-990", result["error"]["message"])

    def test_arithmetic_out_of_range_above_max(self) -> None:
        for mode, x, y in (
            ("add", "MMMCMXCIX", "I"),
            ("multiply", "C", "XL"),
        ):
            with self.subTest(mode=mode):
                result = self.tool.execute(mode=mode, a=x, b=y)
                self.assertEqual(result["error"]["type"], "out_of_range")
                self.assertNotIn("result", result)

    def test_arithmetic_invalid_operand(self) -> None:
        second = self.tool.execute(mode="add", a="X", b="IIII")
        self.assertEqual(second["error"]["type"], "invalid_roman")
        self.assertTrue(second["error"]["message"].startswith("operand b:"))
        self.assertIn("rule 2 (repetition)", second["error"]["message"])

        first = self.tool.execute(mode="multiply", a="VX", b="X")
        self.assertEqual(first["error"]["type"], "invalid_roman")
        self.assertTrue(first["error"]["message"].startswith("operand a:"))
        self.assertIn("rule 3 (subtraction)", first["error"]["message"])

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="convert", number=10)
        self.assert_invalid(mode=None, number=10)
        self.assert_invalid(mode=123, number=10)
        self.assert_invalid(mode="TO_ROMAN", number=10)

    def test_to_roman_invalid_number(self) -> None:
        for bad in (0, -1, 4000, 4000, 3.5, "0", "4000", "-5", "1.5", "1e3",
                    " 12", "12 ", "+12", "1_2", "12a", "Ⅻ", True, False,
                    None, [4], {"n": 4}):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="to_roman", number=bad)

    def test_to_roman_boundary_values_accepted(self) -> None:
        self.assertEqual(
            self.tool.execute(mode="to_roman", number=1)["result"], "I"
        )
        self.assertEqual(
            self.tool.execute(mode="to_roman", number=3999)["result"],
            "MMMCMXCIX",
        )

    def test_from_roman_invalid_parameter(self) -> None:
        for bad in (None, 123, True, ["X"], {"x": 1}, ""):
            with self.subTest(bad=bad):
                self.assert_invalid(mode="from_roman", numeral=bad)
                self.assert_invalid(mode="validate", numeral=bad)

    def test_numeral_length_limit(self) -> None:
        oversized = "I" * 65
        self.assert_invalid(mode="from_roman", numeral=oversized)
        self.assert_invalid(mode="validate", numeral=oversized)
        # 64 characters is accepted as a parameter (then rejected as
        # content with the repetition rule).
        result = self.tool.execute(mode="from_roman", numeral="I" * 64)
        self.assertEqual(result["error"]["type"], "invalid_roman")

    def test_arithmetic_missing_or_malformed_operands(self) -> None:
        for mode in ("add", "subtract", "multiply"):
            with self.subTest(mode=mode):
                self.assert_invalid(mode=mode, a="X")
                self.assert_invalid(mode=mode, b="X")
                self.assert_invalid(mode=mode, a="X", b=None)
                self.assert_invalid(mode=mode, a=None, b="X")
                self.assert_invalid(mode=mode, a=10, b="X")
                self.assert_invalid(mode=mode, a="X", b=True)
                self.assert_invalid(mode=mode, a="X", b="")

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectRomanNumeralTool, RomanNumeralTool)
        self.assertEqual(self.tool.name, "roman_numeral_tool")
        self.assertIn("to_roman", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("RomanNumeralTool", __all__)


if __name__ == "__main__":
    unittest.main()
