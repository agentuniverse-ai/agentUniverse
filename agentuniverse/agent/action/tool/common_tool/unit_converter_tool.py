#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/07/23
# @FileName: unit_converter_tool.py

"""
Unit Converter Tool — convert values across unit categories.

A dependency-free unit conversion utility for agent workflows. It supports
the common physical quantities an agent is likely to encounter: length,
weight/mass, temperature, data size, and time. Each category has a complete
table of conversion factors relative to a canonical base unit, except
temperature, which is converted via dedicated offset formulas because it is
not a simple multiplicative scale.

The tool exposes a single ``execute`` method that takes ``value``,
``from_unit``, ``to_unit`` and ``category`` and returns a structured dict.
All results carry a ``status`` field (``success`` or ``error``); errors are
returned, never raised, so agents can branch on the response rather than
catch exceptions.

Supported categories and units (case-insensitive aliases accepted):

- **length** (base: metre): m, km, mile, ft, in, cm, mm, yd, mi(=mile).
- **weight** (base: kilogram): kg, g, lb, oz, t (metric tonne), mg.
- **temperature** (special): c (Celsius), f (Fahrenheit), k (Kelvin).
- **data** (base: byte, binary 1024): b, kb, mb, gb, tb, pb.
- **time** (base: second): s, min, h, day, ms, week.

Addresses #252 (common utility tools).
"""

from typing import Any, Callable, Dict, List, Optional

from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions into structured tool
# responses instead of raising.
# ruff: noqa: TRY003

# Hard ceiling on the magnitude of the input value. Anything larger almost
# certainly indicates a caller mistake (for example passing an exponent or a
# file size in bytes instead of a number).
_MAX_ABS_VALUE = 1e18


# ----------------------------------------------------------------------
# Conversion factor tables
# ----------------------------------------------------------------------
# Each table maps a canonical lower-cased unit symbol to its multiplicative
# factor relative to the category's base unit. To convert value V from unit A
# to unit B: result = V * table[A] / table[B].
_LENGTH_FACTORS: Dict[str, float] = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
    "in": 0.0254,
    "ft": 0.3048,
    "yd": 0.9144,
    "mile": 1609.344,
    "mi": 1609.344,  # alias for mile
}

_WEIGHT_FACTORS: Dict[str, float] = {
    "mg": 1e-6,
    "g": 0.001,
    "kg": 1.0,
    "t": 1000.0,  # metric tonne
    "oz": 0.028349523125,
    "lb": 0.45359237,
}

# Data sizes use binary multiples (1024). The base unit is the byte.
_DATA_FACTORS: Dict[str, float] = {
    "b": 1.0,
    "kb": 1024.0,
    "mb": 1024.0 ** 2,
    "gb": 1024.0 ** 3,
    "tb": 1024.0 ** 4,
    "pb": 1024.0 ** 5,
}

_TIME_FACTORS: Dict[str, float] = {
    "ms": 0.001,
    "s": 1.0,
    "min": 60.0,
    "h": 3600.0,
    "day": 86400.0,
    "week": 604800.0,
}

# Temperature has no single base-unit factor table. It is handled by a pair
# of to/from-Celsius functions because of the non-zero offsets.
_SUPPORTED_TEMPERATURE_UNITS = ("c", "f", "k")

# Map category -> factor table. Temperature is deliberately absent.
_FACTOR_TABLES: Dict[str, Dict[str, float]] = {
    "length": _LENGTH_FACTORS,
    "weight": _WEIGHT_FACTORS,
    "data": _DATA_FACTORS,
    "time": _TIME_FACTORS,
}


# ----------------------------------------------------------------------
# Temperature conversion helpers
# ----------------------------------------------------------------------
def _to_celsius(value: float, unit: str) -> float:
    """Convert ``value`` in ``unit`` to degrees Celsius."""
    if unit == "c":
        return value
    if unit == "f":
        return (value - 32.0) * 5.0 / 9.0
    if unit == "k":
        return value - 273.15
    raise ValueError(f"Unknown temperature unit: {unit!r}")


def _from_celsius(celsius: float, unit: str) -> float:
    """Convert ``celsius`` to ``unit``."""
    if unit == "c":
        return celsius
    if unit == "f":
        return celsius * 9.0 / 5.0 + 32.0
    if unit == "k":
        return celsius + 273.15
    raise ValueError(f"Unknown temperature unit: {unit!r}")


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a temperature value between any two supported units."""
    celsius = _to_celsius(value, from_unit)
    return _from_celsius(celsius, to_unit)


class UnitConverterTool(Tool):
    """Convert numeric values between units within a physical category.

    Attributes:
        precision: Number of decimal places to round the result to. Set to
            ``None`` or a non-positive integer to disable rounding. Default 6.
        max_abs_value: Largest absolute input magnitude accepted. Inputs
            whose absolute value exceeds this are rejected with a
            ``validation_error``. Default 1e18.
    """

    name: str = "unit_converter_tool"
    description: Optional[str] = (
        "Convert values across unit categories (length, weight, "
        "temperature, data size, time). Pure Python, no dependencies."
    )
    input_keys: Optional[List[str]] = ["category", "value", "from_unit", "to_unit"]

    precision: Optional[int] = 6
    max_abs_value: float = _MAX_ABS_VALUE

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def execute(
        self,
        category: str,
        value: Any,
        from_unit: str,
        to_unit: str,
        **_: Any,
    ) -> dict:
        """Convert ``value`` from ``from_unit`` to ``to_unit`` in ``category``.

        Returns a structured dict. On success it carries ``result`` (the
        converted number) and ``expression`` (a readable string). On error it
        carries ``error_type`` and ``error``.
        """
        try:
            self._validate_config()
            cat = self._normalize_category(category)
            numeric_value = self._coerce_value(value)
            src = self._normalize_unit(from_unit)
            dst = self._normalize_unit(to_unit)
            if cat == "temperature":
                result = self._convert_temperature(cat, numeric_value, src, dst)
            else:
                result = self._convert_linear(cat, numeric_value, src, dst)
            result = self._round(result)
            return {
                "status": "success",
                "category": cat,
                "value": numeric_value,
                "from_unit": src,
                "to_unit": dst,
                "result": result,
                "expression": f"{numeric_value} {src} = {result} {dst}",
            }
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc), category)
        except Exception as exc:  # pragma: no cover - defensive catch-all
            return self._error("operation_error", f"Conversion failed: {exc}", category)

    # ------------------------------------------------------------------
    # Category / unit normalization
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_category(category: Any) -> str:
        if not isinstance(category, str):
            raise TypeError("category must be a string")
        cat = category.strip().lower()
        supported = set(_FACTOR_TABLES) | {"temperature"}
        if cat not in supported:
            raise ValueError(
                f"Unsupported category {category!r}. Supported: "
                + ", ".join(sorted(supported))
            )
        return cat

    @staticmethod
    def _normalize_unit(unit: Any) -> str:
        if not isinstance(unit, str):
            raise TypeError("unit must be a string")
        return unit.strip().lower()

    def _coerce_value(self, value: Any) -> float:
        """Coerce ``value`` to a finite float, rejecting bad inputs."""
        if isinstance(value, bool):
            # bool is a subclass of int but is almost certainly a mistake here.
            raise TypeError("value must be a number, not a boolean")
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("value must not be an empty string")
            try:
                numeric = float(stripped)
            except ValueError as exc:
                raise ValueError(f"value {value!r} is not a valid number") from exc
        elif isinstance(value, (int, float)):
            numeric = float(value)
        else:
            raise TypeError("value must be a number or numeric string")
        if numeric != numeric:  # NaN check
            raise ValueError("value must not be NaN")
        if numeric in (float("inf"), float("-inf")):
            raise ValueError("value must be finite")
        if abs(numeric) > self.max_abs_value:
            raise ValueError(
                f"|value| ({abs(numeric)}) exceeds max_abs_value "
                f"({self.max_abs_value})"
            )
        return numeric

    def _validate_config(self) -> None:
        if self.precision is not None:
            if isinstance(self.precision, bool) or not isinstance(self.precision, int):
                raise ValueError("precision must be an integer or None")
            if self.precision < 0:
                raise ValueError("precision must be non-negative")
        if isinstance(self.max_abs_value, bool) or not isinstance(self.max_abs_value, (int, float)):
            raise ValueError("max_abs_value must be a number")
        if self.max_abs_value <= 0:
            raise ValueError("max_abs_value must be positive")

    # ------------------------------------------------------------------
    # Conversion logic
    # ------------------------------------------------------------------
    def _convert_linear(
        self,
        category: str,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert using the category's multiplicative factor table."""
        table = _FACTOR_TABLES[category]
        if from_unit not in table:
            raise ValueError(
                f"Unknown unit {from_unit!r} for category {category!r}. "
                f"Supported: {', '.join(sorted(table))}"
            )
        if to_unit not in table:
            raise ValueError(
                f"Unknown unit {to_unit!r} for category {category!r}. "
                f"Supported: {', '.join(sorted(table))}"
            )
        if from_unit == to_unit:
            return value
        # value -> base unit -> target unit
        base = value * table[from_unit]
        return base / table[to_unit]

    def _convert_temperature(
        self,
        category: str,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float:
        """Convert a temperature value between c / f / k."""
        if from_unit not in _SUPPORTED_TEMPERATURE_UNITS:
            raise ValueError(
                f"Unknown unit {from_unit!r} for category 'temperature'. "
                f"Supported: {', '.join(_SUPPORTED_TEMPERATURE_UNITS)}"
            )
        if to_unit not in _SUPPORTED_TEMPERATURE_UNITS:
            raise ValueError(
                f"Unknown unit {to_unit!r} for category 'temperature'. "
                f"Supported: {', '.join(_SUPPORTED_TEMPERATURE_UNITS)}"
            )
        if from_unit == to_unit:
            return value
        return _convert_temperature(value, from_unit, to_unit)

    def _round(self, value: float) -> float:
        """Round the result according to ``precision`` and tidy -0.0 to 0.0."""
        if self.precision is not None and self.precision > 0:
            rounded = round(value, self.precision)
        else:
            rounded = value
        # Avoid "-0.0" in output for cosmetic reasons.
        if rounded == 0:
            return 0.0
        return rounded

    # ------------------------------------------------------------------
    # Error helper
    # ------------------------------------------------------------------
    @staticmethod
    def _error(kind: str, message: str, category: Optional[str]) -> dict:
        result: dict = {"status": "error", "error_type": kind, "error": message}
        if category is not None:
            result["category"] = category
        return result


# ----------------------------------------------------------------------
# Public helper: list supported units per category (useful for tool schemas)
# ----------------------------------------------------------------------
def supported_categories() -> List[str]:
    """Return the list of supported category names."""
    return sorted(set(_FACTOR_TABLES) | {"temperature"})


def supported_units(category: str) -> List[str]:
    """Return the list of supported unit symbols for ``category``."""
    cat = category.strip().lower()
    if cat == "temperature":
        return list(_SUPPORTED_TEMPERATURE_UNITS)
    if cat in _FACTOR_TABLES:
        return sorted(_FACTOR_TABLES[cat])
    raise ValueError(f"Unknown category: {category!r}")
