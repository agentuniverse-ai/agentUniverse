#!/usr/bin/env python3
"""UnitsTool: dimension-aware unit conversion with exact rational arithmetic.

The tool converts values between units of the same dimension (length, mass,
time, speed, pressure, energy, temperature) using exact ``fractions.Fraction``
math, so no rounding ever occurs inside the conversion itself. Temperature is
handled with the correct affine (offset) formulas rather than naive
multiplication, and incompatible dimensions are refused with a diagnostic that
lists the units available in the target dimension.

Supported dimensions and units (factors are exact unless noted):
  length    m, km, cm, mm, um, nm, mi, yd, ft, in, nmi
  mass      kg, g, mg, t, lb, oz, st
  time      s, ms, us, min, h, d, wk
  speed     m/s, km/h, mph, kn
  pressure  Pa, kPa, MPa, bar, atm, psi, mmHg
  energy    J, kJ, MJ, cal, kcal, Wh, kWh, BTU
  temperature K, degC, degF, degR (affine: exact offsets)

All non-temperature factors are defined constants (international yard and
pound, thermochemical calorie, IT British thermal unit, standard-gravity
psi, conventional mmHg); each carries a provenance note surfaced in results.
Output values are reported three ways: the exact fraction, an exact decimal
string when the expansion terminates, and a float preview. Conversions that
round in the decimal string are marked.

Modes:
  convert     -- one value between two units, with the factor chain
  analyze     -- parse an expression such as '5 km' or '72 F'
  compatible  -- dimension check plus suggestions on mismatch
  table       -- list the units of one dimension with exact factors
"""

from fractions import Fraction
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

_MODES = ("convert", "analyze", "compatible", "table")

_MAX_UNIT_CHARS = 64
_MAX_TABLE_UNITS = 64

# Exact decimal constants, converted once to Fraction.
_MI = Fraction("1609.344")        # international mile (exact, 1959 agreement)
_LB = Fraction("0.45359237")      # international avoirdupois pound (exact)
_G0 = Fraction("9.80665")         # standard gravity (exact, defined)
_PSI = _LB * _G0 / Fraction("0.0254") ** 2   # psi = pound-force per square inch
_MMHG = Fraction("133.322387415")            # conventional mmHg (defined)
_BTU = Fraction("1055.05585262")             # IT British thermal unit (defined)


def _f(text: str) -> Fraction:
    return Fraction(text)


# dimension -> canonical unit -> (factor to base, aliases, provenance)
_UNITS: dict = {
    "length": {
        "m": (_f(1), ("meter", "meters", "metre", "metres"), "SI base unit"),
        "km": (_f(1000), ("kilometer", "kilometers", "kilometre", "kilometres"), "exact (SI prefix)"),
        "cm": (_f("0.01"), ("centimeter", "centimeters", "centimetre", "centimetres"), "exact (SI prefix)"),
        "mm": (_f("0.001"), ("millimeter", "millimeters", "millimetre", "millimetres"), "exact (SI prefix)"),
        "um": (_f("0.000001"), ("micrometer", "micrometers", "micron", "microns"), "exact (SI prefix)"),
        "nm": (_f("0.000000001"), ("nanometer", "nanometers", "nanometre", "nanometres"), "exact (SI prefix)"),
        "mi": (_MI, ("mile", "miles"), "international mile, exact 1609.344 m"),
        "yd": (_f("0.9144"), ("yard", "yards"), "international yard, exact"),
        "ft": (_f("0.3048"), ("foot", "feet"), "international foot, exact"),
        "in": (_f("0.0254"), ("inch", "inches"), "international inch, exact"),
        "nmi": (_f(1852), ("nauticalmile", "nautical_mile", "nauticalmiles"), "exact 1852 m (MWO 1929)"),
    },
    "mass": {
        "kg": (_f(1), ("kilogram", "kilograms", "kilo", "kilos"), "SI base unit"),
        "g": (_f("0.001"), ("gram", "grams", "gramme", "grammes"), "exact (SI prefix)"),
        "mg": (_f("0.000001"), ("milligram", "milligrams"), "exact (SI prefix)"),
        "t": (_f(1000), ("tonne", "tonnes", "metricton"), "exact 1000 kg"),
        "lb": (_LB, ("pound", "pounds", "lbm", "lbs"), "international avoirdupois pound, exact"),
        "oz": (_LB / 16, ("ounce", "ounces", "oz."), "1/16 international pound, exact"),
        "st": (_LB * 14, ("stone", "stones"), "14 international pounds, exact"),
    },
    "time": {
        "s": (_f(1), ("sec", "secs", "second", "seconds"), "SI base unit"),
        "ms": (_f("0.001"), ("millisecond", "milliseconds"), "exact (SI prefix)"),
        "us": (_f("0.000001"), ("microsecond", "microseconds"), "exact (SI prefix)"),
        "min": (_f(60), ("minute", "minutes"), "exact"),
        "h": (_f(3600), ("hour", "hours", "hr", "hrs"), "exact"),
        "d": (_f(86400), ("day", "days"), "exact (SI day, 86400 s)"),
        "wk": (_f(604800), ("week", "weeks"), "exact 7 days; calendar months/years excluded on purpose"),
    },
    "speed": {
        "m/s": (_f(1), ("mps", "meterspersecond"), "SI derived unit"),
        "km/h": (_f(1) / _f("3.6"), ("kph", "kmh", "kilometersperhour"), "exact 1/3.6 m/s"),
        "mph": (_MI / _f(3600), ("mi/h", "milesperhour"), "international mile per hour, exact"),
        "kn": (_f(1852) / _f(3600), ("kt", "knot", "knots"), "exact 1852/3600 m/s"),
    },
    "pressure": {
        "Pa": (_f(1), ("pa", "pascal", "pascals"), "SI derived unit"),
        "kPa": (_f(1000), ("kpa", "kilopascal", "kilopascals"), "exact (SI prefix)"),
        "MPa": (_f(1000000), ("mpa", "megapascal", "megapascals"), "exact (SI prefix)"),
        "bar": (_f(100000), ("bars",), "exact 100000 Pa (defined)"),
        "atm": (_f(101325), ("atmosphere", "atmospheres", "stdatm"), "standard atmosphere, exact 101325 Pa"),
        "psi": (_PSI, ("PSI", "lbf/in2", "poundpersquareinch"), "defined via standard gravity 9.80665, exact in that definition"),
        "mmHg": (_MMHG, ("mmhg", "millimeterofmercury"), "conventional mmHg, defined decimal (not the torr)"),
    },
    "energy": {
        "J": (_f(1), ("joule", "joules",), "SI derived unit"),
        "kJ": (_f(1000), ("kj", "kilojoule", "kilojoules"), "exact (SI prefix)"),
        "MJ": (_f(1000000), ("mj", "megajoule", "megajoules"), "exact (SI prefix)"),
        "cal": (_f("4.184"), ("calorie", "calories",), "thermochemical calorie, exact 4.184 J"),
        "kcal": (_f(4184), ("Cal", "Calorie", "Calories", "kilocalorie", "kilocalories", "foodcalorie"), "exact; capital 'Cal' (food) equals kcal"),
        "Wh": (_f(3600), ("wh", "watt_hour", "watthour", "watthours"), "exact"),
        "kWh": (_f("3600000"), ("kwh", "kilowatt_hour", "kilowatthour", "kilowatthours"), "exact"),
        "BTU": (_BTU, ("btu", "Btu", "britishthermalunit"), "IT definition, exact decimal"),
    },
}

# Affine temperature scales: value_base = value * scale + offset (base = K).
_TEMPERATURE = {
    "K": (_f(1), _f(0), ("kelvin", "kelvins"), "SI base unit"),
    "degC": (_f(1), _f("273.15"), ("C", "deg_C", "celsius", "°C", "degc"), "K = C + 273.15, exact"),
    "degF": (_f(5) / 9, _f("459.67") * _f(5) / 9, ("F", "deg_F", "fahrenheit", "°F", "degf"), "K = (F + 459.67)*5/9, exact"),
    "degR": (_f(5) / 9, _f(0), ("R", "deg_R", "rankine", "°R", "degr"), "K = R*5/9, exact"),
}

_ALIAS_TO_DIMENSION: dict = {}


def _build_alias_index() -> None:
    for dim, table in _UNITS.items():
        for canon, (factor, aliases, note) in table.items():
            entries = [canon] + list(aliases)
            for alias in entries:
                key = _norm(alias)
                if key in _ALIAS_TO_DIMENSION and _ALIAS_TO_DIMENSION[key] != (dim, canon):
                    raise RuntimeError(f"alias collision: {alias}")  # pragma: no cover
                _ALIAS_TO_DIMENSION[key] = (dim, canon)
    for canon, (scale, offset, aliases, note) in _TEMPERATURE.items():
        for alias in [canon] + list(aliases):
            key = _norm(alias)
            if key in _ALIAS_TO_DIMENSION and _ALIAS_TO_DIMENSION[key] != ("temperature", canon):
                raise RuntimeError(f"alias collision: {alias}")  # pragma: no cover
            _ALIAS_TO_DIMENSION[key] = ("temperature", canon)


# Case-sensitive spellings that must not be folded onto a different unit:
# C/F/R/K are temperature scales, 'Cal' is the food kilocalorie while 'cal'
# is the small calorie.
_CASE_PROTECTED = {"C", "F", "R", "K", "Cal", "Calorie", "Calories"}


def _norm(unit: str) -> str:
    text = unit.replace("°", "deg").replace("\u00b0", "deg")
    text = text.replace(" ", "").replace("_", "").replace(".", "")
    return text if text in _CASE_PROTECTED else text.lower()


def _resolve(unit: str) -> tuple:
    if not isinstance(unit, str) or not unit or len(unit) > _MAX_UNIT_CHARS:
        raise ValueError(f"invalid unit string: {unit!r:.64}")
    key = _norm(unit)
    if key not in _ALIAS_TO_DIMENSION:
        raise ValueError(
            f"unknown unit {unit!r:.64}; use the 'table' mode with dimension='*' to list every supported unit"
        )
    return _ALIAS_TO_DIMENSION[key]


def _decimal_string(fr: Fraction, max_digits: int = 30) -> tuple:
    """Render a Fraction exactly when terminating, else approximately."""
    sign = "-" if fr < 0 else ""
    fr = abs(fr)
    whole = fr.numerator // fr.denominator
    rem = fr - whole
    denom = rem.denominator
    rest = denom
    for p in (2, 5):
        while rest % p == 0:
            rest //= p
    terminating = rest == 1
    digits = ""
    if rem:
        r = rem.numerator
        for _ in range(max_digits):
            r *= 10
            d, r = divmod(r, denom)
            digits += str(d)
            if r == 0:
                break
        if r != 0:
            digits = digits.rstrip("0") or "0"
    text = f"{sign}{whole}" + (("." + digits) if digits else "")
    return text, terminating


def _to_base(value: Fraction, dimension: str, canon: str) -> Fraction:
    if dimension == "temperature":
        scale, offset, _, _ = _TEMPERATURE[canon]
        return value * scale + offset
    factor, _, _ = _UNITS[dimension][canon]
    return value * factor


def _from_base(value: Fraction, dimension: str, canon: str) -> Fraction:
    if dimension == "temperature":
        scale, offset, _, _ = _TEMPERATURE[canon]
        return (value - offset) / scale
    factor, _, _ = _UNITS[dimension][canon]
    return value / factor


class UnitsTool(Tool):
    """Dimension-aware unit conversion with exact rational arithmetic."""

    name: str = "units_tool"
    description: str = (
        "Convert values between units of the same dimension (length, mass, "
        "time, speed, pressure, energy, temperature) using exact rational "
        "arithmetic, with correct affine temperature handling and "
        "dimension-mismatch diagnostics."
    )
    tool_type: str = "api"

    def execute(self, mode: str = "convert", value: Any = None,
                from_unit: str = "", to_unit: str = "", expression: str = "",
                dimension: str = "length", **kwargs: Any) -> Any:
        """Run one units operation.

        - convert:     value + from_unit + to_unit
        - analyze:     expression such as '5 km' or '72 F'
        - compatible:  from_unit + to_unit
        - table:       dimension ('*' lists all dimensions)
        """
        if mode not in _MODES:
            raise ValueError(f"mode must be one of {_MODES}; got {mode!r:.64}")
        if mode == "convert":
            return self._convert(value, from_unit, to_unit)
        if mode == "analyze":
            return self._analyze(expression)
        if mode == "compatible":
            return self._compatible(from_unit, to_unit)
        return self._table(dimension)

    # ------------------------------------------------------------------ #

    def _parse_value(self, value: Any) -> Fraction:
        if isinstance(value, bool):
            raise ValueError("value must be numeric, not boolean")
        if isinstance(value, int):
            return Fraction(value)
        if isinstance(value, float):
            if value != value or value in (float("inf"), float("-inf")):
                raise ValueError("value must be finite")
            return Fraction(str(value))
        if isinstance(value, str):
            text = value.strip()
            try:
                return Fraction(text)
            except (ValueError, ZeroDivisionError):
                raise ValueError(f"value is not a number: {value!r:.64}")
        raise ValueError(f"value must be int/float/decimal-string, got {type(value).__name__}")

    def _unit_info(self, dimension: str, canon: str) -> dict:
        if dimension == "temperature":
            scale, offset, aliases, note = _TEMPERATURE[canon]
            return {
                "dimension": dimension, "unit": canon, "aliases": sorted(set(aliases) - {canon}),
                "kind": "affine", "note": note,
            }
        factor, aliases, note = _UNITS[dimension][canon]
        return {
            "dimension": dimension, "unit": canon,
            "aliases": sorted(set(aliases) - {canon}), "factor_to_base": str(factor),
            "factor_decimal": _decimal_string(factor)[0], "note": note,
        }

    def _convert(self, value: Any, from_unit: str, to_unit: str) -> dict:
        value_fr = self._parse_value(value)
        dim_a, canon_a = _resolve(from_unit)
        dim_b, canon_b = _resolve(to_unit)
        if dim_a != dim_b:
            return self._mismatch(dim_a, canon_a, dim_b, canon_b, "convert")
        base = _to_base(value_fr, dim_a, canon_a)
        result = _from_base(base, dim_b, canon_b)
        exact_text, terminating = _decimal_string(result)
        chain = [f"{_decimal_string(value_fr)[0]} {canon_a}"]
        if dim_a == "temperature":
            scale_a, off_a, _, _ = _TEMPERATURE[canon_a]
            scale_b, off_b, _, _ = _TEMPERATURE[canon_b]
            chain.append(f"to kelvin: x {_decimal_string(scale_a)[0]} + {_decimal_string(off_a)[0]} = {_decimal_string(base)[0]} K")
            chain.append(f"to {canon_b}: (x - {_decimal_string(off_b)[0]}) / {_decimal_string(scale_b)[0]}")
        else:
            fa, _, _ = _UNITS[dim_a][canon_a]
            fb, _, _ = _UNITS[dim_b][canon_b]
            chain.append(f"to base: x {_decimal_string(fa)[0]} = {_decimal_string(base)[0]} (base units)")
            chain.append(f"to {canon_b}: / {_decimal_string(fb)[0]}")
        return {
            "mode": "convert", "dimension": dim_a,
            "from": {"value": str(value_fr), "unit": canon_a},
            "to": {"value": str(result), "unit": canon_b},
            "value_decimal": exact_text,
            "value_float": float(result),
            "decimal_is_exact": terminating,
            "exactness": "exact" if terminating else "exact fraction; decimal string rounded",
            "factor_chain": chain,
            "notes": [self._unit_info(dim_a, canon_a)["note"], self._unit_info(dim_b, canon_b)["note"]],
        }

    def _analyze(self, expression: str) -> dict:
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("expression must be non-empty text like '5 km'")
        parts = expression.strip().rsplit(None, 1) if " " in expression.strip() else None
        if not parts or len(parts) != 2:
            raise ValueError("expression must look like '<value> <unit>', e.g. '5 km' or '72 F'")
        value_text, unit = parts
        dim, canon = _resolve(unit)
        value_fr = self._parse_value(value_text)
        base = _to_base(value_fr, dim, canon)
        return {
            "mode": "analyze", "expression": expression[:64],
            "value": str(value_fr), "unit": canon, "dimension": dim,
            "si": {"value": str(base), "decimal": _decimal_string(base)[0], "unit": self._si_unit(dim)},
        }

    @staticmethod
    def _si_unit(dimension: str) -> str:
        return {
            "length": "m", "mass": "kg", "time": "s", "speed": "m/s",
            "pressure": "Pa", "energy": "J", "temperature": "K",
        }[dimension]

    def _compatible(self, from_unit: str, to_unit: str) -> dict:
        dim_a, canon_a = _resolve(from_unit)
        dim_b, canon_b = _resolve(to_unit)
        ok = dim_a == dim_b
        out = {
            "mode": "compatible", "compatible": ok,
            "from": {"unit": canon_a, "dimension": dim_a},
            "to": {"unit": canon_b, "dimension": dim_b},
        }
        if not ok:
            out["suggestion"] = (
                f"cannot convert {dim_a} to {dim_b}; units available in the target dimension: "
                + ", ".join(sorted(_UNITS.get(dim_b, _TEMPERATURE)))
            )
        return out

    def _table(self, dimension: str) -> dict:
        if dimension == "*":
            dims = {}
            for dim in list(_UNITS) + ["temperature"]:
                dims[dim] = self._table(dim)["units"]
            return {"mode": "table", "dimension": "*", "dimensions": dims}
        if dimension == "temperature":
            units = [self._unit_info("temperature", c) for c in _TEMPERATURE]
            return {"mode": "table", "dimension": dimension, "units": units}
        if dimension not in _UNITS:
            raise ValueError(
                f"unknown dimension {dimension!r:.64}; choose one of "
                + ", ".join(list(_UNITS) + ["temperature"]) + " or '*'"
            )
        units = [self._unit_info(dimension, c) for c in sorted(_UNITS[dimension])]
        if len(units) > _MAX_TABLE_UNITS:  # pragma: no cover
            units = units[:_MAX_TABLE_UNITS]
        return {"mode": "table", "dimension": dimension, "units": units}

    def _mismatch(self, dim_a, canon_a, dim_b, canon_b, mode) -> dict:
        target = sorted(_UNITS.get(dim_b, _TEMPERATURE))
        return {
            "mode": mode, "error": "dimension_mismatch",
            "from": {"unit": canon_a, "dimension": dim_a},
            "to": {"unit": canon_b, "dimension": dim_b},
            "detail": f"cannot convert {dim_a} to {dim_b}",
            "suggestion": f"units available in {dim_b}: " + ", ".join(target),
        }


_build_alias_index()
