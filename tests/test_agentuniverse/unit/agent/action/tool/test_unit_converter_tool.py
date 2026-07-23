#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Tests for UnitConverterTool."""

import math
import os
import unittest

from agentuniverse.agent.action.tool.common_tool import unit_converter_tool as module
from agentuniverse.agent.action.tool.common_tool.unit_converter_tool import (
    UnitConverterTool,
    supported_categories,
    supported_units,
)

YAML_PATH = os.path.join(os.path.dirname(module.__file__), "unit_converter_tool.yaml.example")


class UnitConverterToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = UnitConverterTool()

    # --- length ---------------------------------------------------------
    def test_km_to_mile(self):
        result = self.tool.execute(category="length", value=10, from_unit="km", to_unit="mile")
        self.assertEqual(result["status"], "success")
        self.assertAlmostEqual(result["result"], 6.21371, places=4)

    def test_length_round_trip(self):
        result = self.tool.execute(category="length", value=1, from_unit="mile", to_unit="m")
        self.assertAlmostEqual(result["result"], 1609.344, places=3)
        back = self.tool.execute(category="length", value=result["result"], from_unit="m", to_unit="mile")
        self.assertAlmostEqual(back["result"], 1.0, places=3)

    def test_length_alias_mi_equals_mile(self):
        r1 = self.tool.execute(category="length", value=5, from_unit="mi", to_unit="m")
        r2 = self.tool.execute(category="length", value=5, from_unit="mile", to_unit="m")
        self.assertEqual(r1["result"], r2["result"])

    # --- weight ---------------------------------------------------------
    def test_kg_to_lb(self):
        result = self.tool.execute(category="weight", value=1, from_unit="kg", to_unit="lb")
        self.assertAlmostEqual(result["result"], 2.20462, places=3)

    def test_weight_oz_to_g(self):
        result = self.tool.execute(category="weight", value=1, from_unit="oz", to_unit="g")
        self.assertAlmostEqual(result["result"], 28.3495, places=2)

    # --- temperature (non-linear) --------------------------------------
    def test_celsius_to_fahrenheit(self):
        result = self.tool.execute(category="temperature", value=0, from_unit="c", to_unit="f")
        self.assertAlmostEqual(result["result"], 32.0, places=6)
        boil = self.tool.execute(category="temperature", value=100, from_unit="c", to_unit="f")
        self.assertAlmostEqual(boil["result"], 212.0, places=6)

    def test_fahrenheit_to_celsius(self):
        result = self.tool.execute(category="temperature", value=98.6, from_unit="f", to_unit="c")
        self.assertAlmostEqual(result["result"], 37.0, places=4)

    def test_kelvin_round_trip(self):
        # 0 C = 273.15 K
        k = self.tool.execute(category="temperature", value=0, from_unit="c", to_unit="k")
        self.assertAlmostEqual(k["result"], 273.15, places=4)
        back = self.tool.execute(category="temperature", value=k["result"], from_unit="k", to_unit="c")
        self.assertAlmostEqual(back["result"], 0.0, places=4)

    def test_negative_zero_temperature(self):
        # -40 is the same in C and F; ensure -0.0 is tidied to 0.0.
        result = self.tool.execute(category="temperature", value=-40, from_unit="c", to_unit="f")
        self.assertAlmostEqual(result["result"], -40.0, places=6)
        zero = self.tool.execute(category="temperature", value=32, from_unit="f", to_unit="c")
        self.assertEqual(zero["result"], 0.0)
        self.assertEqual(math.copysign(1.0, zero["result"]), 1.0)

    # --- data -----------------------------------------------------------
    def test_data_kb_to_mb(self):
        result = self.tool.execute(category="data", value=2048, from_unit="kb", to_unit="mb")
        self.assertAlmostEqual(result["result"], 2.0, places=6)

    def test_data_gb_to_bytes(self):
        result = self.tool.execute(category="data", value=1, from_unit="gb", to_unit="b")
        self.assertEqual(result["result"], 1073741824.0)

    # --- time -----------------------------------------------------------
    def test_time_hours_to_seconds(self):
        result = self.tool.execute(category="time", value=1, from_unit="h", to_unit="s")
        self.assertEqual(result["result"], 3600.0)

    def test_time_days_to_minutes(self):
        result = self.tool.execute(category="time", value=1, from_unit="day", to_unit="min")
        self.assertAlmostEqual(result["result"], 1440.0, places=6)

    # --- input flexibility ---------------------------------------------
    def test_value_as_numeric_string(self):
        result = self.tool.execute(category="length", value="  42 ", from_unit="m", to_unit="cm")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], 4200.0)

    def test_same_unit_returns_value(self):
        result = self.tool.execute(category="weight", value=5, from_unit="kg", to_unit="kg")
        self.assertEqual(result["result"], 5.0)

    def test_case_insensitive_units(self):
        result = self.tool.execute(category="length", value=1, from_unit="KM", to_unit="M")
        self.assertEqual(result["result"], 1000.0)

    # --- errors ---------------------------------------------------------
    def test_unknown_unit(self):
        result = self.tool.execute(category="length", value=1, from_unit="smoot", to_unit="m")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("Unknown unit", result["error"])

    def test_unknown_category(self):
        result = self.tool.execute(category="currency", value=1, from_unit="usd", to_unit="eur")
        self.assertEqual(result["status"], "error")
        self.assertIn("Unsupported category", result["error"])

    def test_non_numeric_value(self):
        result = self.tool.execute(category="length", value="abc", from_unit="m", to_unit="cm")
        self.assertEqual(result["status"], "error")
        self.assertIn("not a valid number", result["error"])

    def test_boolean_value_rejected(self):
        result = self.tool.execute(category="length", value=True, from_unit="m", to_unit="cm")
        self.assertEqual(result["status"], "error")

    def test_expression_field_readable(self):
        result = self.tool.execute(category="time", value=2, from_unit="h", to_unit="min")
        self.assertEqual(result["expression"], "2.0 h = 120.0 min")


class UnitConverterHelpersTest(unittest.TestCase):
    def test_supported_categories(self):
        cats = supported_categories()
        for expected in ("length", "weight", "temperature", "data", "time"):
            self.assertIn(expected, cats)

    def test_supported_units_length(self):
        units = supported_units("length")
        for expected in ("m", "km", "mile", "ft", "in", "cm"):
            self.assertIn(expected, units)

    def test_supported_units_temperature(self):
        self.assertEqual(set(supported_units("temperature")), {"c", "f", "k"})

    def test_supported_units_unknown_category(self):
        with self.assertRaises(ValueError):
            supported_units("nope")


class UnitConverterYamlTest(unittest.TestCase):
    def test_yaml_example_exists(self):
        self.assertTrue(os.path.isfile(YAML_PATH))

    def test_yaml_example_has_required_fields(self):
        import yaml

        with open(YAML_PATH, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertEqual(data["name"], "unit_converter_tool")
        self.assertEqual(data["metadata"]["class"], "UnitConverterTool")
        self.assertEqual(data["precision"], 6)
        self.assertIn("category", data["input_keys"])


if __name__ == "__main__":
    unittest.main()
