#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: test_unit_converter_tool.py

"""Offline unit tests for UnitConverterTool.

The tool is built purely on the standard library (fractions, decimal,
difflib) and never touches the network, so this suite runs fully
offline. Every assertion is deterministic: conversions are checked
against independently written ground-truth literals (exact decimal
strings where the true value terminates, fixed-`round` values where it
repeats), temperature cases include the affine anchors 0 °C = 32 °F =
273.15 K = 491.67 °R and -40 °C = -40 °F, round trips are asserted to
be exactly the original string, and the error matrix covers unknown
units, cross-category pairs, ambiguity resolution and every malformed
parameter raising ValueError.
"""

import unittest

from agentuniverse.agent.action.tool.common_tool import UnitConverterTool
from agentuniverse.agent.action.tool.common_tool.unit_converter_tool import (
    UnitConverterTool as DirectUnitConverterTool,
    _FOLDED_ALIASES,
    _UNIT_REGISTRY,
)


def convert(tool, **kwargs) -> str:
    """Run one convert call and return its result string."""
    return tool.execute(mode="convert", **kwargs)["result"]


def round_trip(tool, value: str, from_unit: str, to_unit: str) -> str:
    """Convert forward then back; return the final result string."""
    forward = tool.execute(
        mode="convert", value=value, from_unit=from_unit, to_unit=to_unit
    )["result"]
    return tool.execute(
        mode="convert", value=forward, from_unit=to_unit, to_unit=from_unit
    )["result"]


class UnitConverterToolTest(unittest.TestCase):
    """Offline deterministic test cases for the stdlib UnitConverterTool."""

    def setUp(self) -> None:
        self.tool = UnitConverterTool()

    # ------------------------------------------------------------------ #
    # length ground truths
    # ------------------------------------------------------------------ #

    def test_length_ground_truths(self) -> None:
        cases = [
            (1, "mi", "m", "1609.344"),
            (1, "in", "cm", "2.54"),
            (1, "yd", "ft", "3"),
            (1, "ft", "in", "12"),
            (1, "nm", "m", "1852"),
            (1, "nmi", "m", "1852"),
            (1, "li", "km", "0.5"),
            (1, "里", "m", "500"),
            (2, "m", "cm", "200"),
            (1, "m", "mm", "1000"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(from_unit=from_unit, to_unit=to_unit):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_length_repeating_result_default_and_rounded(self) -> None:
        # 10 km = 78125/12573 mi (repeating); 12 significant digits by
        # default, fixed places with round.
        self.assertEqual(
            convert(self.tool, value=10, from_unit="km", to_unit="mi"),
            "6.21371192237",
        )
        self.assertEqual(
            convert(self.tool, value=10, from_unit="km", to_unit="mi",
                    round=6),
            "6.213712",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="m", to_unit="ft"),
            "3.28083989501",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="m", to_unit="ft",
                    round=4),
            "3.2808",
        )

    def test_length_category_context(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="m", to_unit="ft",
            category="length",
        )
        self.assertEqual(result["category"], "length")
        self.assertEqual(result["result"], "3.28083989501")

    # ------------------------------------------------------------------ #
    # mass ground truths
    # ------------------------------------------------------------------ #

    def test_mass_ground_truths(self) -> None:
        cases = [
            (1, "lb", "kg", "0.45359237"),
            (1, "oz", "g", "28.349523125"),
            (1, "斤", "kg", "0.5"),
            (1, "jin", "g", "500"),
            ("2.5", "t", "kg", "2500"),
            (1, "kg", "g", "1000"),
            (16, "oz", "lb", "1"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(from_unit=from_unit, to_unit=to_unit):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_mass_repeating_result_rounded(self) -> None:
        # 1 kg = 2.2046226218487757... lb.
        self.assertEqual(
            convert(self.tool, value=1, from_unit="kg", to_unit="lb",
                    round=10),
            "2.2046226218",
        )
        # 2.5 lb = 1.133980925 kg; round=0 rounds half away from zero
        # only at ties, so this simply truncates the decimals.
        self.assertEqual(
            convert(self.tool, value="2.5", from_unit="lb", to_unit="kg",
                    round=0),
            "1",
        )

    # ------------------------------------------------------------------ #
    # temperature ground truths (affine, not ratios)
    # ------------------------------------------------------------------ #

    def test_temperature_anchor_points_exact(self) -> None:
        # 0 °C = 32 °F = 273.15 K = 491.67 °R, all exactly.
        for from_unit, expected in (("F", "32"), ("K", "273.15"),
                                    ("R", "491.67")):
            with self.subTest(from_unit=from_unit):
                self.assertEqual(
                    convert(self.tool, value=0, from_unit="C",
                            to_unit=from_unit),
                    expected,
                )
        self.assertEqual(
            convert(self.tool, value="273.15", from_unit="K", to_unit="C"),
            "0",
        )
        self.assertEqual(
            convert(self.tool, value="491.67", from_unit="R", to_unit="C"),
            "0",
        )

    def test_temperature_negative_40_crossover(self) -> None:
        # The C/F scales cross at -40: -40 °C = -40 °F, both ways.
        self.assertEqual(
            convert(self.tool, value=-40, from_unit="C", to_unit="F"),
            "-40",
        )
        self.assertEqual(
            convert(self.tool, value=-40, from_unit="F", to_unit="C"),
            "-40",
        )

    def test_temperature_more_exact_vectors(self) -> None:
        cases = [
            (100, "C", "F", "212"),
            (212, "F", "C", "100"),
            (300, "K", "C", "26.85"),
            (37, "C", "F", "98.6"),
            (98.6, "F", "C", "37"),
            (0, "K", "R", "0"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(value=value, pair=(from_unit, to_unit)):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_temperature_repeating_results_rounded(self) -> None:
        # 0 °F = 255.3722... K; 1 °R = 5/9 K = 0.5555... K.
        self.assertEqual(
            convert(self.tool, value=0, from_unit="F", to_unit="K",
                    round=4),
            "255.3722",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="R", to_unit="K",
                    round=6),
            "0.555556",
        )

    def test_temperature_symbol_aliases(self) -> None:
        self.assertEqual(
            convert(self.tool, value=100, from_unit="℃", to_unit="℉"),
            "212",
        )
        self.assertEqual(
            convert(self.tool, value=0, from_unit="°c", to_unit="fahrenheit"),
            "32",
        )
        self.assertEqual(
            convert(self.tool, value=100, from_unit="celsius",
                    to_unit="kelvin"),
            "373.15",
        )

    # ------------------------------------------------------------------ #
    # area ground truths
    # ------------------------------------------------------------------ #

    def test_area_ground_truths(self) -> None:
        cases = [
            (1, "acre", "m2", "4046.8564224"),
            (1, "acre", "ft2", "43560"),
            (1, "km2", "ha", "100"),
            (1, "ha", "m2", "10000"),
            (1, "ft2", "m2", "0.09290304"),
            (3, "mu", "m²", "2000"),  # 1 亩 = 2000/3 m², 3 亩 exactly 2000
            (1, "m²", "m2", "1"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(from_unit=from_unit, to_unit=to_unit):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_area_mu_repeating_result_rounded(self) -> None:
        self.assertEqual(
            convert(self.tool, value=1, from_unit="亩", to_unit="m2",
                    round=6),
            "666.666667",
        )

    # ------------------------------------------------------------------ #
    # volume ground truths (US vs UK gallons distinct)
    # ------------------------------------------------------------------ #

    def test_volume_ground_truths(self) -> None:
        cases = [
            (1, "galUS", "L", "3.785411784"),
            (1, "galUK", "L", "4.54609"),
            (1, "gal", "pint", "8"),  # 1 US gal = exactly 8 US pints
            (1, "m3", "mL", "1000000"),
            (1, "pt", "ml", "473.176473"),
            (2, "L", "mL", "2000"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(from_unit=from_unit, to_unit=to_unit):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_volume_repeating_result_rounded(self) -> None:
        # 1 L = 1/4.54609 imperial gallons = 0.21996924... galUK.
        self.assertEqual(
            convert(self.tool, value=1, from_unit="L", to_unit="galUK",
                    round=8),
            "0.21996925",
        )

    # ------------------------------------------------------------------ #
    # speed ground truths
    # ------------------------------------------------------------------ #

    def test_speed_ground_truths(self) -> None:
        cases = [
            ("3.6", "km/h", "m/s", "1"),  # exact: 1 km/h = 5/18 m/s
            (1, "mph", "m/s", "0.44704"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(pair=(from_unit, to_unit)):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_speed_repeating_results(self) -> None:
        # 100 km/h = 62.1371192237... mph; 1 kn = 463/900 m/s.
        self.assertEqual(
            convert(self.tool, value=100, from_unit="kph", to_unit="mph"),
            "62.1371192237",
        )
        self.assertEqual(
            convert(self.tool, value=100, from_unit="kmh", to_unit="mph",
                    round=2),
            "62.14",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="kn", to_unit="m/s",
                    round=6),
            "0.514444",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="mps", to_unit="kn",
                    round=6),
            "1.943844",
        )

    # ------------------------------------------------------------------ #
    # data ground truths (decimal vs binary families distinct)
    # ------------------------------------------------------------------ #

    def test_data_decimal_family(self) -> None:
        cases = [
            (1, "MB", "KB", "1000"),  # decimal MB, not 1024 KiB-style
            (1, "GB", "MB", "1000"),
            (1, "TB", "GB", "1000"),
            (5, "mB", "KB", "5000"),  # case-insensitive fallback resolves
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(pair=(from_unit, to_unit)):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_data_binary_family(self) -> None:
        cases = [
            (1, "KiB", "B", "1024"),
            (1, "MiB", "KiB", "1024"),
            (2, "mib", "kib", "2048"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(pair=(from_unit, to_unit)):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    def test_data_cross_family_exact(self) -> None:
        # Both directions terminate exactly: 1 MB = 976.5625 KiB and
        # 1 MiB = 1.048576 MB; 1 GB = 976562.5 KiB.
        self.assertEqual(
            convert(self.tool, value=1, from_unit="MB", to_unit="KiB"),
            "976.5625",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="MiB", to_unit="MB"),
            "1.048576",
        )
        self.assertEqual(
            convert(self.tool, value=1, from_unit="GB", to_unit="KiB"),
            "976562.5",
        )

    # ------------------------------------------------------------------ #
    # time ground truths
    # ------------------------------------------------------------------ #

    def test_time_ground_truths(self) -> None:
        cases = [
            ("1.5", "h", "min", "90"),
            (90, "min", "h", "1.5"),
            (1, "day", "h", "24"),
            (1, "week", "day", "7"),
            (1, "w", "hr", "168"),
            (1, "min", "ms", "60000"),
            (1, "ms", "s", "0.001"),
        ]
        for value, from_unit, to_unit, expected in cases:
            with self.subTest(pair=(from_unit, to_unit)):
                self.assertEqual(
                    convert(self.tool, value=value, from_unit=from_unit,
                            to_unit=to_unit),
                    expected,
                )

    # ------------------------------------------------------------------ #
    # Exactness: round trips and float-free arithmetic
    # ------------------------------------------------------------------ #

    def test_round_trips_are_exact(self) -> None:
        cases = [
            ("12.34", "lb", "kg"),
            ("7", "亩", "m2"),
            ("3.6", "km/h", "m/s"),
            ("98.6", "F", "K"),
            ("0.125", "MiB", "B"),
            ("-40", "C", "F"),
            ("0.1", "kg", "oz"),
            ("2.75", "yd", "m"),
            ("123.456", "kmh", "mph"),
        ]
        for value, from_unit, to_unit in cases:
            with self.subTest(pair=(from_unit, to_unit)):
                self.assertEqual(
                    round_trip(self.tool, value, from_unit, to_unit),
                    value,
                )

    def test_exact_36_kmh_is_exactly_1_mps(self) -> None:
        # The classic float-drift trap: 3.6 * (5/18) is exactly 1 with
        # rational arithmetic, never 0.9999999999999999.
        self.assertEqual(
            convert(self.tool, value="3.6", from_unit="km/h", to_unit="m/s"),
            "1",
        )
        self.assertEqual(
            convert(self.tool, value="3.6", from_unit="km/h",
                    to_unit="m/s", round=30),
            "1.000000000000000000000000000000",
        )

    def test_float_input_goes_through_decimal_boundary(self) -> None:
        # 0.1 as a float is converted via its shortest decimal string,
        # so the computation sees exactly 1/10.
        result = self.tool.execute(
            mode="convert", value=0.1, from_unit="kg", to_unit="g"
        )
        self.assertEqual(result["value"], "0.1")
        self.assertEqual(result["result"], "100")

    def test_convert_result_payload_shape(self) -> None:
        result = self.tool.execute(
            mode="convert", value="2", from_unit="斤", to_unit="kg",
            category="mass",
        )
        self.assertEqual(
            result,
            {
                "mode": "convert",
                "category": "mass",
                "from_unit": "jin",
                "to_unit": "kg",
                "value": "2",
                "result": "1",
            },
        )

    # ------------------------------------------------------------------ #
    # categories mode
    # ------------------------------------------------------------------ #

    def test_categories_listing(self) -> None:
        result = self.tool.execute(mode="categories")
        self.assertEqual(result["mode"], "categories")
        self.assertEqual(result["count"], 8)
        self.assertEqual(
            [entry["name"] for entry in result["categories"]],
            ["length", "mass", "temperature", "area", "volume", "speed",
             "data", "time"],
        )
        by_name = {entry["name"]: entry for entry in result["categories"]}
        self.assertEqual(by_name["length"]["base_unit"], "m")
        self.assertEqual(by_name["mass"]["base_unit"], "kg")
        self.assertEqual(by_name["temperature"]["base_unit"], "K")
        self.assertEqual(by_name["area"]["base_unit"], "m2")
        self.assertEqual(by_name["volume"]["base_unit"], "L")
        self.assertEqual(by_name["speed"]["base_unit"], "m/s")
        self.assertEqual(by_name["data"]["base_unit"], "B")
        self.assertEqual(by_name["time"]["base_unit"], "s")

    def test_categories_unit_entries(self) -> None:
        categories = self.tool.execute(mode="categories")["categories"]
        by_name = {entry["name"]: entry for entry in categories}
        length = {u["unit"]: u for u in by_name["length"]["units"]}
        self.assertEqual(length["li"]["symbol"], "里")
        self.assertEqual(length["li"]["factor"], "500")
        self.assertIn("里", length["li"]["aliases"])
        self.assertEqual(length["mi"]["factor"], "1609.344")
        # Non-terminating factors are shown as exact fractions.
        area = {u["unit"]: u for u in by_name["area"]["units"]}
        self.assertEqual(area["mu"]["factor"], "2000/3")
        self.assertEqual(area["mu"]["approx"], "666.666666667")
        # Temperature entries carry affine formulas instead of factors.
        temperature = {u["unit"]: u for u in
                       by_name["temperature"]["units"]}
        self.assertEqual(
            temperature["F"]["to_base"], "K = (value + 459.67) × 5/9"
        )
        self.assertIn("5/9", temperature["R"]["to_base"])
        # Data units are tagged with their family.
        data = {u["unit"]: u for u in by_name["data"]["units"]}
        self.assertEqual(data["KB"]["family"], "decimal")
        self.assertEqual(data["TB"]["family"], "decimal")
        self.assertEqual(data["KiB"]["family"], "binary")
        self.assertEqual(data["MiB"]["family"], "binary")

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def test_info_linear_units(self) -> None:
        result = self.tool.execute(mode="info", unit="斤")
        self.assertEqual(result["category"], "mass")
        self.assertEqual(result["unit"], "jin")
        self.assertEqual(result["symbol"], "斤")
        self.assertEqual(result["factor"], "0.5")
        self.assertEqual(result["base_unit"], "kg")
        self.assertIn("斤", result["aliases"])

    def test_info_non_terminating_factor(self) -> None:
        result = self.tool.execute(mode="info", unit="亩")
        self.assertEqual(result["factor"], "2000/3")
        # 2000/3 = 666.666666666... -> 12 significant digits.
        self.assertEqual(result["approx"], "666.666666667")

    def test_info_speed_units(self) -> None:
        kmh = self.tool.execute(mode="info", unit="km/h")
        self.assertEqual(kmh["category"], "speed")
        self.assertEqual(kmh["factor"], "5/18")
        self.assertEqual(kmh["approx"], "0.277777777778")
        kn = self.tool.execute(mode="info", unit="kn")
        self.assertEqual(kn["factor"], "463/900")

    def test_info_data_families(self) -> None:
        for unit, family in (("KB", "decimal"), ("KiB", "binary")):
            result = self.tool.execute(mode="info", unit=unit)
            self.assertEqual(result["category"], "data")
            self.assertEqual(result["family"], family)

    def test_info_temperature_affine(self) -> None:
        result = self.tool.execute(
            mode="info", unit="R", category="temperature"
        )
        self.assertEqual(result["scale_type"], "affine")
        self.assertEqual(result["to_base"], "K = value × 5/9")
        self.assertNotIn("factor", result)
        fahrenheit = self.tool.execute(mode="info", unit="F")
        self.assertEqual(
            fahrenheit["to_base"], "K = (value + 459.67) × 5/9"
        )

    def test_info_with_category_resolves(self) -> None:
        result = self.tool.execute(mode="info", unit="t", category="mass")
        self.assertEqual(result["unit"], "t")
        self.assertEqual(result["factor"], "1000")

    # ------------------------------------------------------------------ #
    # Error matrix: content-level failures return structured payloads
    # ------------------------------------------------------------------ #

    def test_unknown_unit_gets_suggestions(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="killogram", to_unit="kg"
        )
        self.assertEqual(result["mode"], "convert")
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertIn("kilogram", result["suggestions"])

    def test_unknown_unit_without_close_matches(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="xyz!!", to_unit="s"
        )
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertNotIn("suggestions", result)

    def test_cross_category_suggests_mass_units(self) -> None:
        """kg -> cm must be rejected with the mass units suggested."""
        result = self.tool.execute(
            mode="convert", value=1, from_unit="kg", to_unit="cm"
        )
        self.assertEqual(result["error"]["type"], "category_mismatch")
        self.assertIn("mass", result["error"]["message"])
        self.assertIn("length", result["error"]["message"])
        self.assertEqual(
            result["suggestions"], ["g", "jin", "kg", "lb", "oz", "t"]
        )

    def test_cross_category_reverse_anchors_on_from_category(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="cm", to_unit="kg"
        )
        self.assertEqual(result["error"]["type"], "category_mismatch")
        self.assertEqual(
            result["suggestions"],
            ["cm", "ft", "in", "km", "li", "m", "mi", "mm", "nmi", "yd"],
        )

    def test_cross_category_temperature(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="C", to_unit="L"
        )
        self.assertEqual(result["error"]["type"], "category_mismatch")
        self.assertEqual(result["suggestions"], ["C", "F", "K", "R"])

    def test_category_context_rejects_foreign_unit(self) -> None:
        # 'lb' is valid globally but not within length.
        result = self.tool.execute(
            mode="convert", value=1, from_unit="lb", to_unit="m",
            category="length",
        )
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertIn("length", result["error"]["message"])
        self.assertNotIn("suggestions", result)

    def test_category_context_rejects_too(self) -> None:
        result = self.tool.execute(
            mode="convert", value=1, from_unit="kg", to_unit="cm",
            category="mass",
        )
        self.assertEqual(result["error"]["type"], "unknown_unit")
        self.assertIn("mass", result["error"]["message"])

    def test_info_unknown_unit(self) -> None:
        result = self.tool.execute(mode="info", unit="lightyear")
        self.assertEqual(result["mode"], "info")
        self.assertEqual(result["error"]["type"], "unknown_unit")

    def test_ambiguous_alias_requires_category(self) -> None:
        """The registry is collision-free; exercise the guard anyway."""
        key = "ton"
        _FOLDED_ALIASES.setdefault(key, []).append(("length", "m"))
        try:
            result = self.tool.execute(
                mode="convert", value=1, from_unit="TON", to_unit="km"
            )
            self.assertEqual(result["error"]["type"], "ambiguous_unit")
            self.assertIn("category", result["error"]["message"])
            # The category parameter resolves the ambiguity.
            resolved = self.tool.execute(
                mode="convert", value=1, from_unit="TON", to_unit="km",
                category="length",
            )
            self.assertEqual(resolved["from_unit"], "m")
        finally:
            bucket = [entry for entry in _FOLDED_ALIASES[key]
                      if entry != ("length", "m")]
            if bucket:
                _FOLDED_ALIASES[key] = bucket
            else:
                _FOLDED_ALIASES.pop(key, None)

    def test_registry_has_no_alias_collisions(self) -> None:
        """Case-insensitive alias resolution must stay unambiguous."""
        from collections import defaultdict

        folded = defaultdict(set)
        for category, units in _UNIT_REGISTRY.items():
            canonical = set()
            for name, spec in units.items():
                self.assertNotIn(name, canonical)
                canonical.add(name)
                for spelling in (name, *spec.aliases):
                    folded[spelling.casefold()].add(category)
        collisions = {k: v for k, v in folded.items() if len(v) > 1}
        self.assertEqual(collisions, {})

    # ------------------------------------------------------------------ #
    # Invalid inputs raise ValueError (strict validation)
    # ------------------------------------------------------------------ #

    def assert_invalid(self, **kwargs) -> None:
        with self.assertRaises(ValueError):
            self.tool.execute(**kwargs)

    def test_invalid_mode(self) -> None:
        self.assert_invalid(mode="convrt")
        self.assert_invalid(mode=None)
        self.assert_invalid(mode=123)

    def test_invalid_category(self) -> None:
        self.assert_invalid(
            mode="convert", value=1, from_unit="m", to_unit="ft",
            category="volume2",
        )
        self.assert_invalid(
            mode="convert", value=1, from_unit="m", to_unit="ft",
            category=True,
        )

    def test_invalid_value(self) -> None:
        for bad in (None, "abc", "nan", "inf", "-inf", "1.2.3", "1_000",
                    "0x10", "", "  ", True, [1], {"v": 1}):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="convert", value=bad, from_unit="m", to_unit="ft"
                )

    def test_value_magnitude_cap(self) -> None:
        self.assert_invalid(
            mode="convert", value="1e101", from_unit="m", to_unit="ft"
        )
        self.assert_invalid(
            mode="convert", value=10 ** 101, from_unit="m", to_unit="ft"
        )
        # Exactly at the cap is allowed.
        ok = self.tool.execute(
            mode="convert", value="1e100", from_unit="m", to_unit="m"
        )
        self.assertEqual(ok["result"], "1" + "0" * 100)

    def test_invalid_units(self) -> None:
        for label in ("from_unit", "to_unit"):
            for bad in (None, 5, True, "", "   "):
                with self.subTest(label=label, bad=bad):
                    self.assert_invalid(
                        mode="convert", value=1,
                        **{label: bad, "to_unit" if label == "from_unit"
                           else "from_unit": "m"},
                    )

    def test_convert_missing_arguments(self) -> None:
        self.assert_invalid(mode="convert", from_unit="m", to_unit="ft")
        self.assert_invalid(mode="convert", value=1, to_unit="ft")
        self.assert_invalid(mode="convert", value=1, from_unit="m")
        self.assert_invalid(mode="convert")

    def test_invalid_round(self) -> None:
        for bad in (-1, 31, 1.5, "two", True, [2]):
            with self.subTest(bad=bad):
                self.assert_invalid(
                    mode="convert", value=1, from_unit="m", to_unit="ft",
                    round=bad,
                )
        # round=None means "no rounding" and must stay valid.
        ok = self.tool.execute(
            mode="convert", value=1, from_unit="m", to_unit="ft",
            round=None,
        )
        self.assertEqual(ok["result"], "3.28083989501")

    def test_info_missing_unit(self) -> None:
        self.assert_invalid(mode="info")

    def test_unit_string_length_limit(self) -> None:
        self.assert_invalid(
            mode="convert", value=1, from_unit="a" * 41, to_unit="m"
        )

    # ------------------------------------------------------------------ #
    # Determinism
    # ------------------------------------------------------------------ #

    def test_repeated_calls_are_deterministic(self) -> None:
        first = self.tool.execute(
            mode="convert", value=10, from_unit="km", to_unit="mi"
        )
        for _ in range(5):
            self.assertEqual(
                self.tool.execute(
                    mode="convert", value=10, from_unit="km", to_unit="mi"
                ),
                first,
            )
        listing = self.tool.execute(mode="categories")
        self.assertEqual(self.tool.execute(mode="categories"), listing)

    # ------------------------------------------------------------------ #
    # Packaging / registration
    # ------------------------------------------------------------------ #

    def test_class_defaults_and_export(self) -> None:
        self.assertIs(DirectUnitConverterTool, UnitConverterTool)
        self.assertEqual(self.tool.name, "unit_converter_tool")
        self.assertIn("convert", self.tool.description)
        from agentuniverse.agent.action.tool.common_tool import __all__

        self.assertIn("UnitConverterTool", __all__)


if __name__ == "__main__":
    unittest.main()
