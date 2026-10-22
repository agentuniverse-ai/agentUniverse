#!/usr/bin/env python3
"""Offline unit tests for UnitsTool.

Oracles:
- Hand-verified exact identities (international definitions).
- The full 4x4 affine temperature matrix at canonical points.
- Fraction round-trip identity on seeded conversions (LCG, deterministic).
- pint (test-only, skipped when absent): float cross-check within 1e-12.
"""

import unittest
from fractions import Fraction

from agentuniverse.agent.action.tool.common_tool.units_tool import UnitsTool

try:
    import pint  # test-only oracle

    _UREG = pint.UnitRegistry()
except Exception:  # pragma: no cover - optional oracle
    _UREG = None


def _lcg(seed, n, mod=2147483647):
    state = seed
    for _ in range(n):
        state = (state * 48271) % mod
        yield state


class UnitsToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = UnitsTool()

    def _conv(self, value, a, b):
        return self.tool.execute(mode="convert", value=value, from_unit=a, to_unit=b)

    # -- exact identity ground truths ---------------------------------- #

    def test_exact_definitions(self):
        cases = [
            (1, "yd", "ft", "3"), (1, "mi", "ft", "5280"), (1, "ft", "in", "12"),
            (1, "nmi", "m", "1852"), (1, "lb", "oz", "16"), (1, "st", "lb", "14"),
            (1, "lb", "g", "453.59237"), (1, "cal", "J", "4.184"),
            (1, "kcal", "cal", "1000"), (1, "kWh", "MJ", "3.6"),
            (1, "atm", "Pa", "101325"), (1, "bar", "Pa", "100000"),
            (1, "BTU", "J", "1055.05585262"),
            (1, "wk", "d", "7"), (1, "kn", "km/h", "1.852"),
            (1, "mph", "mi/h", "1"),
        ]
        for value, a, b, want in cases:
            with self.subTest(f"{value} {a} -> {b}"):
                got = self._conv(value, a, b)
                self.assertEqual(got["value_decimal"], want)
                self.assertTrue(got["decimal_is_exact"])

    def test_temperature_matrix(self):
        # (value, from, to, expected exact decimal)
        cases = [
            (100, "degC", "degF", "212"), (-40, "C", "F", "-40"),
            (0, "degC", "K", "273.15"), (0, "K", "degC", "-273.15"),
            (0, "K", "degF", "-459.67"), (0, "degF", "K", "255.372222222222222222222222222222"),
            (32, "degF", "degC", "0"), (212, "F", "C", "100"),
            (100, "degC", "degR", "671.67"), (0, "degR", "K", "0"),
            (491.67, "degR", "degF", "32"), (1, "degR", "degF", "-458.67"),
            (-273.15, "degC", "degF", "-459.67"),
        ]
        for value, a, b, want in cases:
            with self.subTest(f"{value} {a} -> {b}"):
                self.assertEqual(self._conv(value, a, b)["value_decimal"], want)

    def test_exactness_flags(self):
        terminating = self._conv(1, "mi", "ft")
        self.assertTrue(terminating["decimal_is_exact"])
        repeating = self._conv(1, "kg", "lb")  # 1/0.45359237 does not terminate
        self.assertFalse(repeating["decimal_is_exact"])
        self.assertTrue(repeating["value_decimal"].startswith("2.204622621848"))
        self.assertIn("exact fraction", repeating["exactness"])

    def test_result_is_exact_fraction(self):
        got = self._conv("0.1", "kg", "g")
        self.assertEqual(got["to"]["value"], "100")
        self.assertEqual(got["value_decimal"], "100")

    # -- round-trip identity -------------------------------------------- #

    def test_round_trip_identity(self):
        pairs = [
            ("mi", "mm"), ("lb", "oz"), ("atm", "psi"), ("kcal", "BTU"),
            ("kn", "mph"), ("degC", "degF"), ("degF", "degR"), ("wk", "s"),
            ("nmi", "yd"), ("t", "oz"),
        ]
        for i, (a, b) in enumerate(pairs):
            for r in _lcg(1000 + i, 5):
                value = Fraction(r, 97)  # exact non-terminating decimals too
                out = self._conv(str(value), a, b)
                back = self._conv(out["to"]["value"], b, a)
                with self.subTest(f"{value} {a}->{b}->{a}"):
                    self.assertEqual(Fraction(back["to"]["value"]), value)

    # -- aliases ---------------------------------------------------------- #

    def test_alias_matrix(self):
        cases = [
            ("C", "temperature", "degC"), ("°C", "temperature", "degC"),
            ("celsius", "temperature", "degC"), ("F", "temperature", "degF"),
            ("fahrenheit", "temperature", "degF"), ("R", "temperature", "degR"),
            ("Cal", "energy", "kcal"), ("cal", "energy", "cal"),
            ("Calorie", "energy", "kcal"), ("kilometers", "length", "km"),
            ("kph", "speed", "km/h"), ("kt", "speed", "kn"),
            ("feet", "length", "ft"), ("lbs", "mass", "lb"),
            ("BTU", "energy", "BTU"), ("PSI", "pressure", "psi"),
        ]
        for alias, dim, canon in cases:
            with self.subTest(alias):
                out = self._conv(1, alias, canon)
                self.assertEqual(out["dimension"], dim)
                self.assertEqual(out["from"]["unit"], canon)
                self.assertEqual(out["to"]["value"], "1")

    def test_cal_vs_cal_trap(self):
        self.assertEqual(self._conv(1, "Cal", "cal")["value_decimal"], "1000")
        self.assertEqual(self._conv(1, "cal", "Cal")["value_decimal"], "0.001")

    # -- incompatibility -------------------------------------------------- #

    def test_incompatible_dimensions(self):
        for a, b in [("m", "kg"), ("s", "J"), ("degC", "kg"), ("psi", "mph"), ("lb", "K")]:
            with self.subTest(f"{a} -> {b}"):
                out = self.tool.execute(mode="compatible", from_unit=a, to_unit=b)
                self.assertFalse(out["compatible"])
                self.assertNotEqual(out["from"]["dimension"], out["to"]["dimension"])
                self.assertIn("suggestion", out)
                conv = self._conv(1, a, b)
                self.assertEqual(conv["error"], "dimension_mismatch")

    def test_compatible_same_dimension(self):
        out = self.tool.execute(mode="compatible", from_unit="mi", to_unit="km")
        self.assertTrue(out["compatible"])
        self.assertNotIn("suggestion", out)

    # -- analyze ----------------------------------------------------------- #

    def test_analyze(self):
        out = self.tool.execute(mode="analyze", expression="5 km")
        self.assertEqual(out["si"], {"value": "5000", "decimal": "5000", "unit": "m"})
        out = self.tool.execute(mode="analyze", expression="72 F")
        self.assertEqual(out["si"]["unit"], "K")
        self.assertTrue(out["si"]["decimal"].startswith("295.372"))
        out = self.tool.execute(mode="analyze", expression="1.5 h")
        self.assertEqual(out["si"]["value"], "5400")

    def test_analyze_errors(self):
        for bad in ("5km", "km 5", "", "   ", "5", "5 km extra"):
            with self.subTest(repr(bad)):
                with self.assertRaises(ValueError):
                    self.tool.execute(mode="analyze", expression=bad)

    # -- table ----------------------------------------------------------- #

    def test_table(self):
        out = self.tool.execute(mode="table", dimension="length")
        names = {u["unit"] for u in out["units"]}
        self.assertIn("mi", names)
        self.assertIn("nmi", names)
        temp = self.tool.execute(mode="table", dimension="temperature")
        self.assertEqual({u["unit"] for u in temp["units"]}, {"K", "degC", "degF", "degR"})
        self.assertEqual(temp["units"][0]["kind"], "affine")
        all_dims = self.tool.execute(mode="table", dimension="*")
        self.assertEqual(len(all_dims["dimensions"]), 7)
        with self.assertRaises(ValueError):
            self.tool.execute(mode="table", dimension="volume")

    # -- validation ------------------------------------------------------- #

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.tool.execute(mode="nope")
        with self.assertRaises(ValueError):
            self._conv("abc", "m", "ft")
        with self.assertRaises(ValueError):
            self._conv(float("inf"), "m", "ft")
        with self.assertRaises(ValueError):
            self._conv(1, "cubits", "m")
        with self.assertRaises(ValueError):
            self._conv(1, "", "m")
        with self.assertRaises(ValueError):
            self._conv(True, "m", "ft")

    def test_huge_values_exact(self):
        got = self._conv(10 ** 30, "m", "km")
        self.assertEqual(got["value_decimal"], str(10 ** 27))
        self.assertEqual(got["to"]["value"], str(Fraction(10 ** 27)))

    def test_negative_and_zero(self):
        self.assertEqual(self._conv(-40, "C", "F")["value_decimal"], "-40")
        self.assertEqual(self._conv(0, "kg", "lb")["to"]["value"], "0")

    # -- pint cross-check (optional oracle) -------------------------------- #

    @unittest.skipIf(_UREG is None, "pint not installed")
    def test_pint_cross_check(self):
        # pint's spelling for our canonical names.
        pint_names = {
            "m": "meter", "km": "kilometer", "cm": "centimeter", "mm": "millimeter",
            "mi": "mile", "yd": "yard", "ft": "foot", "in": "inch", "nmi": "nautical_mile",
            "kg": "kilogram", "g": "gram", "t": "metric_ton", "lb": "pound",
            "oz": "ounce", "st": "stone",
            "s": "second", "min": "minute", "h": "hour", "d": "day", "wk": "week",
            "m/s": "meter / second", "km/h": "kilometer / hour",
            "mph": "mile / hour", "kn": "knot",
            "Pa": "pascal", "kPa": "kilopascal", "MPa": "megapascal", "bar": "bar",
            "atm": "atmosphere", "psi": "psi", "mmHg": "mmHg",
            "J": "joule", "kJ": "kilojoule", "MJ": "megajoule", "cal": "calorie",
            "kcal": "kilocalorie", "Wh": "watt_hour", "kWh": "kilowatt_hour",
            "BTU": "british_thermal_unit",
            "degC": "degC", "degF": "degF", "degR": "degR", "K": "kelvin",
        }
        pairs = [
            ("mi", "km"), ("lb", "kg"), ("atm", "psi"), ("kWh", "MJ"),
            ("kn", "m/s"), ("st", "kg"), ("mmHg", "bar"), ("mph", "kn"),
            ("MJ", "kcal"), ("wk", "min"),
        ]
        checked = 0
        for i, (a, b) in enumerate(pairs):
            for r in _lcg(7000 + i, 4):
                value = r / 97.0
                got = float(Fraction(self._conv(value, a, b)["to"]["value"]))
                try:
                    q = (value * _UREG(pint_names[a])).to(pint_names[b])
                except Exception:
                    continue  # unit spelling unavailable in this pint build
                want = q.magnitude
                with self.subTest(f"{value} {a} -> {b} (pint)"):
                    self.assertAlmostEqual(
                        got, want, delta=max(abs(want), 1.0) * 1e-12,
                        msg=f"pint={want} tool={got}",
                    )
                checked += 1
        self.assertGreater(checked, 20)

    @unittest.skipIf(_UREG is None, "pint not installed")
    def test_pint_temperature_cross_check(self):
        scales = ["degC", "degF", "degR", "K"]
        for src in scales:
            for dst in scales:
                for value in (-40, 0, 36.6, 100):
                    got = float(Fraction(self._conv(value, src, dst)["to"]["value"]))
                    q = _UREG.Quantity(value, src).to(_UREG(dst))
                    with self.subTest(f"{value} {src}->{dst} (pint)"):
                        self.assertAlmostEqual(got, q.magnitude, delta=1e-9)


if __name__ == "__main__":
    unittest.main()
