#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: unit_converter_tool.py

"""Measurement unit conversion tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency unit converter agents
can call whenever a task mixes measurement systems: metric / imperial
lengths, masses, areas and volumes, temperature scales, speeds, data
sizes and durations.

The tool supports three modes:

* ``convert`` — convert ``value`` from ``from_unit`` to ``to_unit``
  within one category. Both units are resolved through a
  case-aware alias table (exact spelling first, case-insensitive
  fallback), so ``"MB"`` / ``"mB"`` / ``"mb"`` all resolve to the
  megabyte and the rare letter-case ambiguity between categories is
  resolved by the optional ``category`` context. Chinese aliases
  (``斤`` jin, ``里`` li, ``亩`` mu) are accepted alongside the Latin
  names. An optional ``round`` argument rounds the result to a fixed
  number of decimal places (half away from zero).
* ``categories`` — list every category with its base unit and all of
  its units, factors and aliases.
* ``info`` — report one unit's category, factor, symbol, aliases and
  family (decimal vs binary data units; affine temperature scales).

Exactness: every conversion is computed with exact arithmetic —
values and factors are kept as :class:`fractions.Fraction` integers
ratios and rendered through :class:`decimal.Decimal` only at the
boundary, so ``3.6 km/h`` is exactly ``1 m/s``, ``1 in`` is exactly
``2.54 cm`` and round trips such as ``12.34 lb -> kg -> lb`` return
``12.34``. Floating point is never used inside a computation; float
inputs are accepted only at the boundary and converted through their
shortest decimal representation. Non-terminating factors (``1 里 =
2000/3 m²``, ``1 km/h = 5/18 m/s``, ``1 kn = 463/900 m/s``) stay
exact fractions internally and are displayed rounded to 12
significant digits unless ``round`` is given. Temperature conversions
are affine, not ratios: ``K = (value + offset) x scale`` with
``0 °C = 32 °F = 273.15 K = 491.67 °R`` and ``-40 °C = -40 °F``.

Input validation is strict and happens before any computation:
malformed parameters (wrong types, unknown mode or category, a value
that is not a finite number, magnitudes beyond 1e100, a ``round``
outside 0..30) raise a ``ValueError``, mirroring the other common
tools. Errors that depend on the *content being processed* — an
unknown unit (returned with closest-match suggestions), a cross
category pair such as ``kg -> cm`` (returned with the units of the
anchored category as suggestions) and an ambiguous alias — are
returned as a structured ``error`` payload so an agent can react
without catching exceptions. Conversions never touch the network and
are fully deterministic.
"""

import difflib
import re
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_NUMBER_RE = re.compile(
    r"\A[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z"
)
_MAX_ABS_VALUE = 10 ** 100
_MAX_ROUND = 30
_DISPLAY_PRECISION = 12
_SUGGESTIONS = 3
_MAX_UNIT_CHARS = 40


class _UnitSpec:
    """One unit: either a linear factor or an affine temperature scale."""

    __slots__ = ("name", "symbol", "aliases", "family", "factor",
                 "offset", "scale")

    def __init__(
        self,
        name: str,
        symbol: str,
        aliases: Tuple[str, ...] = (),
        family: Optional[str] = None,
        factor: Optional[Fraction] = None,
        offset: Optional[Fraction] = None,
        scale: Optional[Fraction] = None,
    ) -> None:
        self.name = name
        self.symbol = symbol
        self.aliases = aliases
        self.family = family
        self.factor = factor
        self.offset = offset
        self.scale = scale


def _linear(
    name: str,
    symbol: str,
    factor: Fraction,
    aliases: Tuple[str, ...] = (),
    family: Optional[str] = None,
) -> _UnitSpec:
    """Build a unit that converts to the category base by multiplication."""
    return _UnitSpec(name, symbol, aliases, family, factor=factor)


def _affine(
    name: str,
    symbol: str,
    offset: Fraction,
    scale: Fraction,
    aliases: Tuple[str, ...] = (),
) -> _UnitSpec:
    """Build a temperature unit: ``K = (value + offset) * scale``."""
    return _UnitSpec(name, symbol, aliases, None, offset=offset, scale=scale)


# --------------------------------------------------------------------- #
# Unit registry — canonical name -> spec, per category (ordered).
# Factors are exact fractions relative to the category base unit.
# --------------------------------------------------------------------- #
_UNIT_REGISTRY: Dict[str, Dict[str, _UnitSpec]] = {
    "length": {
        "m": _linear("m", "m", Fraction(1),
                     ("meter", "meters", "metre", "metres")),
        "km": _linear("km", "km", Fraction(1000),
                      ("kilometer", "kilometers", "kilometre", "kilometres")),
        "cm": _linear("cm", "cm", Fraction("0.01"),
                      ("centimeter", "centimeters",
                       "centimetre", "centimetres")),
        "mm": _linear("mm", "mm", Fraction("0.001"),
                      ("millimeter", "millimeters",
                       "millimetre", "millimetres")),
        "nmi": _linear("nmi", "nmi", Fraction(1852), ("nm",)),
        "mi": _linear("mi", "mi", Fraction("1609.344"),
                      ("mile", "miles")),
        "yd": _linear("yd", "yd", Fraction("0.9144"), ("yard", "yards")),
        "ft": _linear("ft", "ft", Fraction("0.3048"), ("foot", "feet")),
        "in": _linear("in", "in", Fraction("0.0254"), ("inch", "inches")),
        "li": _linear("li", "里", Fraction(500), ("里",)),
    },
    "mass": {
        "kg": _linear("kg", "kg", Fraction(1),
                      ("kilo", "kilos", "kilogram", "kilograms")),
        "g": _linear("g", "g", Fraction("0.001"),
                     ("gram", "grams", "gramme", "grammes")),
        "t": _linear("t", "t", Fraction(1000),
                     ("ton", "tons", "tonne", "tonnes",
                      "metricton", "metrictons")),
        "lb": _linear("lb", "lb", Fraction("0.45359237"),
                      ("lbs", "pound", "pounds")),
        "oz": _linear("oz", "oz", Fraction("0.028349523125"),
                      ("ounce", "ounces")),
        "jin": _linear("jin", "斤", Fraction("0.5"), ("斤",)),
    },
    "temperature": {
        "K": _affine("K", "K", Fraction(0), Fraction(1),
                     ("kelvin", "kelvins")),
        "C": _affine("C", "°C", Fraction("273.15"), Fraction(1),
                     ("celsius", "°c", "℃")),
        "F": _affine("F", "°F", Fraction("459.67"), Fraction(5, 9),
                     ("fahrenheit", "°f", "℉")),
        "R": _affine("R", "°R", Fraction(0), Fraction(5, 9),
                     ("rankine", "°r")),
    },
    "area": {
        "m2": _linear("m2", "m²", Fraction(1),
                      ("m²", "sqm", "squaremeter", "squaremeters")),
        "km2": _linear("km2", "km²", Fraction(10 ** 6), ("km²", "sqkm")),
        "ha": _linear("ha", "ha", Fraction(10 ** 4),
                      ("hectare", "hectares")),
        "acre": _linear("acre", "acre", Fraction("4046.8564224"), ()),
        "ft2": _linear("ft2", "ft²", Fraction("0.09290304"),
                       ("ft²", "sqft")),
        "mu": _linear("mu", "亩", Fraction(2000, 3), ("亩",)),
    },
    "volume": {
        "L": _linear("L", "L", Fraction(1),
                     ("l", "liter", "liters", "litre", "litres")),
        "mL": _linear("mL", "mL", Fraction("0.001"), ("ml",)),
        "m3": _linear("m3", "m³", Fraction(1000), ("m³",)),
        "galUS": _linear("galUS", "gal (US)", Fraction("3.785411784"),
                         ("gal", "galus", "usgal", "gallon", "gallons")),
        "galUK": _linear("galUK", "gal (UK)", Fraction("4.54609"),
                         ("galuk", "ukgal", "impgal")),
        "pint": _linear("pint", "pt (US)", Fraction("0.473176473"),
                        ("pt", "uspint")),
    },
    "speed": {
        "m/s": _linear("m/s", "m/s", Fraction(1), ("mps",)),
        "km/h": _linear("km/h", "km/h", Fraction(5, 18), ("kmh", "kph")),
        "mph": _linear("mph", "mph", Fraction("0.44704"), ()),
        "kn": _linear("kn", "kn", Fraction(463, 900), ("kt", "knot", "knots")),
    },
    "data": {
        "B": _linear("B", "B", Fraction(1), ("byte", "bytes"),
                     family="decimal"),
        "KB": _linear("KB", "KB", Fraction(1000),
                      ("kb", "kilobyte", "kilobytes"), family="decimal"),
        "MB": _linear("MB", "MB", Fraction(10 ** 6),
                      ("mb", "megabyte", "megabytes"), family="decimal"),
        "GB": _linear("GB", "GB", Fraction(10 ** 9),
                      ("gb", "gigabyte", "gigabytes"), family="decimal"),
        "TB": _linear("TB", "TB", Fraction(10 ** 12),
                      ("tb", "terabyte", "terabytes"), family="decimal"),
        "KiB": _linear("KiB", "KiB", Fraction(2 ** 10), ("kib",),
                       family="binary"),
        "MiB": _linear("MiB", "MiB", Fraction(2 ** 20), ("mib",),
                       family="binary"),
    },
    "time": {
        "s": _linear("s", "s", Fraction(1),
                     ("sec", "secs", "second", "seconds")),
        "ms": _linear("ms", "ms", Fraction("0.001"),
                      ("msec", "msecs", "millisecond", "milliseconds")),
        "min": _linear("min", "min", Fraction(60), ("minute", "minutes")),
        "h": _linear("h", "h", Fraction(3600), ("hr", "hrs", "hour", "hours")),
        "day": _linear("day", "d", Fraction(86400), ("d", "day", "days")),
        "week": _linear("week", "wk", Fraction(604800),
                        ("w", "wk", "week", "weeks")),
    },
}


class _UnitResolutionError(Exception):
    """Internal carrier for content-level unit lookup failures."""

    def __init__(self, error_type: str, message: str,
                 suggestions: Optional[List[str]] = None) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.suggestions = suggestions or []


def _build_lookup_tables() -> Tuple[Dict[str, Tuple[str, str]],
                                    Dict[str, List[Tuple[str, str]]]]:
    """Build the exact and case-folded alias lookup tables once."""
    exact: Dict[str, Tuple[str, str]] = {}
    folded: Dict[str, List[Tuple[str, str]]] = {}
    for category, units in _UNIT_REGISTRY.items():
        for name, spec in units.items():
            spellings = (name,) + tuple(spec.aliases)
            for spelling in spellings:
                exact[spelling] = (category, name)
                entry = (category, name)
                bucket = folded.setdefault(spelling.casefold(), [])
                if entry not in bucket:
                    bucket.append(entry)
    return exact, folded


_EXACT_ALIASES, _FOLDED_ALIASES = _build_lookup_tables()


class UnitConverterTool(Tool):
    """Measurement unit conversion tool built purely on the stdlib.

    Attributes:
        categories (tuple): The supported category names, in the
            deterministic listing order.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "unit_converter_tool"
    description: str = (
        "Unit converter tool — pure Python stdlib, no network required. "
        "Eight categories (length, mass, temperature, area, volume, "
        "speed, data, time) converted with exact arithmetic. "
        "mode='convert' converts a value between two units of one "
        "category (from_unit/to_unit with an optional category context "
        "and round decimal places); mode='categories' lists every "
        "category with its units and factors; mode='info' reports one "
        "unit's factor, symbol, aliases and family (decimal vs binary "
        "data units, affine temperature scales). Chinese aliases "
        "斤 / 里 / 亩 accepted alongside the Latin names."
    )

    MODES: ClassVar[tuple] = ("convert", "categories", "info")
    CATEGORIES: ClassVar[tuple] = tuple(_UNIT_REGISTRY)

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        value: Any = None,
        from_unit: Any = None,
        to_unit: Any = None,
        category: Any = None,
        unit: Any = None,
        round: Any = None,  # noqa: A002 — friendlier agent-facing name
    ) -> Dict[str, Any]:
        """Run one unit conversion, listing or unit info query.

        Args:
            mode (str): One of ``convert`` / ``categories`` / ``info``.
            value (int | float | str): The numeric value to convert
                (``convert`` mode only). Strings may use decimal or
                exponent notation; floats are converted through their
                shortest decimal representation and never used in the
                computation itself.
            from_unit (str): The source unit (``convert`` mode).
            to_unit (str): The target unit (``convert`` mode).
            category (str): Optional category context — one of
                length / mass / temperature / area / volume / speed /
                data / time. Constrains unit resolution so ambiguous
                aliases are resolved by category.
            unit (str): The unit to describe (``info`` mode).
            round (int): Optional number of decimal places (0..30) for
                the converted result; rounding is half away from zero.
                By default results are rendered to 12 significant
                digits with trailing zeros stripped.

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                string plus the call context) or a structured ``error``
                payload for content-level failures (unknown unit,
                cross-category pair, ambiguous alias) with suggestions.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if category is not None:
            if (isinstance(category, bool) or not isinstance(category, str)
                    or category not in _UNIT_REGISTRY):
                self._invalid(self._category_error_text(category))
        if mode == "categories":
            return self._run_categories()
        if mode == "info":
            return self._run_info(unit, category)
        return self._run_convert(value, from_unit, to_unit, category, round)

    # ------------------------------------------------------------------ #
    # convert mode
    # ------------------------------------------------------------------ #

    def _run_convert(
        self, value: Any, from_unit: Any, to_unit: Any,
        category: Optional[str], round_arg: Any,
    ) -> Dict[str, Any]:
        """Convert ``value`` between two units of one category."""
        value_fraction = self._parse_value(value)
        clean_round = self._validate_round(round_arg)
        from_name = self._validate_unit_string(from_unit, "from_unit")
        to_name = self._validate_unit_string(to_unit, "to_unit")
        try:
            from_category, from_spec = self._resolve_unit(from_name, category)
            to_category, to_spec = self._resolve_unit(to_name, category)
        except _UnitResolutionError as exc:
            return self._error_result(
                {"mode": "convert"}, exc.error_type, exc.message,
                suggestions=exc.suggestions,
            )
        if from_category != to_category:
            return self._category_mismatch_payload(
                from_category, from_name, to_category, to_name, category
            )
        result = self._convert(value_fraction, from_spec, to_spec)
        return {
            "mode": "convert",
            "category": from_category,
            "from_unit": from_spec.name,
            "to_unit": to_spec.name,
            "value": self._format_fraction(value_fraction),
            "result": self._format_fraction(result, clean_round),
        }

    @staticmethod
    def _convert(
        value: Fraction, from_spec: _UnitSpec, to_spec: _UnitSpec
    ) -> Fraction:
        """Exact conversion through the category base unit."""
        if from_spec.factor is not None:
            # Linear category: value * factor_from / factor_to.
            return value * from_spec.factor / to_spec.factor
        # Affine (temperature): K = (value + offset) * scale, then back.
        kelvin = (value + from_spec.offset) * from_spec.scale
        return kelvin / to_spec.scale - to_spec.offset

    def _category_mismatch_payload(
        self,
        from_category: str,
        from_name: str,
        to_category: str,
        to_name: str,
        category: Optional[str],
    ) -> Dict[str, Any]:
        """Build the cross-category error, suggesting anchored units."""
        anchor = category if category is not None else from_category
        suggestions = sorted(_UNIT_REGISTRY[anchor])
        return self._error_result(
            {"mode": "convert"},
            error_type="category_mismatch",
            message=(
                f"cannot convert between categories: 'from' unit "
                f"{from_name!r} is {from_category} but 'to' unit "
                f"{to_name!r} is {to_category}. Convert between units of "
                f"one category — {anchor} units: "
                f"{', '.join(suggestions)}"
            ),
            suggestions=suggestions,
            cap=None,
        )

    # ------------------------------------------------------------------ #
    # categories / info modes
    # ------------------------------------------------------------------ #

    def _run_categories(self) -> Dict[str, Any]:
        """List every category with its units and factors."""
        categories: List[Dict[str, Any]] = []
        for category, units in _UNIT_REGISTRY.items():
            base_name = next(iter(units))
            category_entry: Dict[str, Any] = {
                "name": category,
                "base_unit": base_name,
                "units": [],
            }
            for name, spec in units.items():
                category_entry["units"].append(
                    self._unit_summary(category, name, spec)
                )
            categories.append(category_entry)
        return {
            "mode": "categories",
            "categories": categories,
            "count": len(categories),
        }

    def _run_info(self, unit: Any, category: Optional[str]) -> Dict[str, Any]:
        """Report one unit's factor, symbol, aliases and family."""
        clean_unit = self._validate_unit_string(unit, "unit")
        try:
            unit_category, spec = self._resolve_unit(clean_unit, category)
        except _UnitResolutionError as exc:
            return self._error_result(
                {"mode": "info"}, exc.error_type, exc.message,
                suggestions=exc.suggestions,
            )
        base_name = next(iter(_UNIT_REGISTRY[unit_category]))
        info: Dict[str, Any] = {
            "mode": "info",
            "category": unit_category,
            "unit": spec.name,
            "symbol": spec.symbol,
            "aliases": self._all_spellings(spec),
            "base_unit": base_name,
        }
        summary = self._unit_summary(unit_category, spec.name, spec)
        if spec.factor is not None:
            info["factor"] = summary["factor"]
            if "approx" in summary:
                info["approx"] = summary["approx"]
        else:
            info["to_base"] = summary["to_base"]
            info["from_base"] = summary["from_base"]
            info["scale_type"] = "affine"
        if spec.family is not None:
            info["family"] = spec.family
        return info

    def _unit_summary(
        self, category: str, name: str, spec: _UnitSpec
    ) -> Dict[str, Any]:
        """Build the shared per-unit description (factors / formulas)."""
        entry: Dict[str, Any] = {
            "unit": name,
            "symbol": spec.symbol,
            "aliases": list(spec.aliases),
        }
        if spec.factor is not None:
            exact = self._exact_decimal_or_none(spec.factor)
            if exact is not None:
                entry["factor"] = exact
            else:
                entry["factor"] = (
                    f"{spec.factor.numerator}/{spec.factor.denominator}"
                )
                entry["approx"] = self._format_fraction(spec.factor)
        else:
            entry["to_base"] = self._affine_formula(
                spec.offset, spec.scale, to_base=True
            )
            entry["from_base"] = self._affine_formula(
                spec.offset, spec.scale, to_base=False
            )
        if spec.family is not None:
            entry["family"] = spec.family
        return entry

    # ------------------------------------------------------------------ #
    # Unit resolution (case-aware, category-scoped, with suggestions)
    # ------------------------------------------------------------------ #

    @classmethod
    def _resolve_unit(
        cls, unit: str, category_limit: Optional[str]
    ) -> Tuple[str, _UnitSpec]:
        """Resolve one unit string to its (category, spec).

        Exact (case-sensitive) spellings win; a case-insensitive
        fallback resolves the remaining inputs and is unambiguous for
        the shipped registry. Failures raise ``_UnitResolutionError``
        with closest-match suggestions.
        """
        scope: Dict[str, Dict[str, _UnitSpec]]
        scope = (
            _UNIT_REGISTRY if category_limit is None
            else {category_limit: _UNIT_REGISTRY[category_limit]}
        )
        exact = _EXACT_ALIASES.get(unit)
        if exact is not None and exact[0] in scope:
            return exact[0], _UNIT_REGISTRY[exact[0]][exact[1]]
        matches = [
            (cat, name)
            for cat, name in _FOLDED_ALIASES.get(unit.casefold(), [])
            if cat in scope
        ]
        if len(matches) == 1:
            cat, name = matches[0]
            return cat, _UNIT_REGISTRY[cat][name]
        if len(matches) > 1:
            options = sorted({f"{name} ({cat})" for cat, name in matches})
            raise _UnitResolutionError(
                "ambiguous_unit",
                f"unit {unit!r} matches several categories: "
                f"{', '.join(options)} — pass the 'category' parameter "
                "to resolve it",
                suggestions=options,
            )
        candidates = {spelling for units in scope.values()
                      for spelling in cls._spellings_of(units)}
        suggestions = difflib.get_close_matches(
            unit, sorted(candidates), n=_SUGGESTIONS, cutoff=0.6
        )
        where = (
            f" in category {category_limit!r}" if category_limit is not None
            else ""
        )
        known = ", ".join(sorted(
            name for units in scope.values() for name in units
        ))
        raise _UnitResolutionError(
            "unknown_unit",
            f"unknown unit {unit!r}{where} — closest matches: "
            f"{', '.join(suggestions) if suggestions else '(none)'}. "
            f"Known units{where or ' (all categories)'}: {known}",
            suggestions=suggestions,
        )

    @staticmethod
    def _spellings_of(units: Dict[str, _UnitSpec]) -> List[str]:
        """Every accepted spelling of every unit in one category."""
        spellings: List[str] = []
        for name, spec in units.items():
            spellings.append(name)
            spellings.extend(spec.aliases)
        return spellings

    @classmethod
    def _all_spellings(cls, spec: _UnitSpec) -> List[str]:
        """Every accepted spelling of one unit (canonical first)."""
        return [spec.name, *spec.aliases]

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"unit_converter_tool: {message}")

    @classmethod
    def _category_error_text(cls, category: Any) -> str:
        return (
            "category must be one of: "
            f"{', '.join(_UNIT_REGISTRY)} (got {category!r})"
        )

    @classmethod
    def _validate_unit_string(cls, unit: Any, label: str) -> str:
        """Validate a unit name: a non-empty bounded string."""
        if unit is None or isinstance(unit, bool) or not isinstance(unit, str):
            cls._invalid(f"{label} must be a non-empty string (got {unit!r})")
        clean = unit.strip()
        if not clean:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        if len(clean) > _MAX_UNIT_CHARS:
            cls._invalid(
                f"{label} exceeds the {_MAX_UNIT_CHARS}-character limit "
                f"(got {len(clean)} characters)"
            )
        return clean

    @classmethod
    def _validate_round(cls, round_arg: Any) -> Optional[int]:
        """Validate the optional decimal-places rounding argument."""
        if round_arg is None:
            return None
        if isinstance(round_arg, bool) or not isinstance(round_arg, int):
            cls._invalid(
                f"round must be an integer between 0 and {_MAX_ROUND} "
                f"(got {round_arg!r})"
            )
        if not 0 <= round_arg <= _MAX_ROUND:
            cls._invalid(
                f"round must be an integer between 0 and {_MAX_ROUND} "
                f"(got {round_arg})"
            )
        return round_arg

    @classmethod
    def _parse_value(cls, value: Any) -> Fraction:
        """Parse the numeric value into an exact fraction.

        Accepts int, str (decimal or exponent notation) and float
        (through its shortest decimal representation). Rejects
        non-finite values and magnitudes beyond ``1e100``.
        """
        if value is None or isinstance(value, bool):
            cls._invalid(f"value must be a finite number (got {value!r})")
        if isinstance(value, Fraction):
            fraction = value
        elif isinstance(value, int):
            fraction = Fraction(value)
        elif isinstance(value, float):
            fraction = Fraction(str(value))
        elif isinstance(value, (str, Decimal)):
            text = value.strip() if isinstance(value, str) else str(value)
            if not text or not _NUMBER_RE.match(text):
                cls._invalid(
                    "value must be a finite number in decimal or exponent "
                    f"notation (got {value!r})"
                )
            fraction = Fraction(Decimal(text))
        else:
            cls._invalid(f"value must be a finite number (got {value!r})")
        if abs(fraction) > _MAX_ABS_VALUE:
            cls._invalid(
                f"|value| exceeds the {_MAX_ABS_VALUE:.1e} magnitude cap "
                "(got a value beyond it)"
            )
        return fraction

    # ------------------------------------------------------------------ #
    # Exact rendering (fractions in, decimal strings out)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _format_fraction(
        fraction: Fraction, places: Optional[int] = None
    ) -> str:
        """Render a fraction exactly or rounded, as a decimal string.

        With ``places`` the value is rounded half away from zero using
        pure integer arithmetic (single-step, no double rounding).
        Without it the value is rendered to 12 significant digits with
        trailing zeros stripped.
        """
        if places is not None:
            negative = fraction < 0
            magnitude = abs(fraction)
            scaled = magnitude.numerator * 10 ** places
            quotient, remainder = divmod(scaled, magnitude.denominator)
            if 2 * remainder >= magnitude.denominator:
                quotient += 1
            if quotient == 0:
                negative = False
            digits = str(quotient)
            if places > 0:
                if len(digits) <= places:
                    digits = "0" * (places - len(digits) + 1) + digits
                digits = f"{digits[:-places]}.{digits[-places:]}"
            return f"{'-' if negative else ''}{digits}"
        with localcontext() as ctx:
            ctx.prec = _DISPLAY_PRECISION
            decimal = (
                Decimal(fraction.numerator) / Decimal(fraction.denominator)
            )
        if decimal == 0:
            decimal = Decimal(0)
        else:
            decimal = decimal.normalize()
        return format(decimal, "f")

    @staticmethod
    def _exact_decimal_or_none(fraction: Fraction) -> Optional[str]:
        """Exact decimal string of a fraction, or None when repeating."""
        denominator = fraction.denominator
        for prime in (2, 5):
            while denominator % prime == 0:
                denominator //= prime
        if denominator != 1:
            return None
        with localcontext() as ctx:
            ctx.prec = 60
            decimal = (
                Decimal(fraction.numerator) / Decimal(fraction.denominator)
            )
        if decimal == 0:
            return "0"
        return format(decimal.normalize(), "f")

    @classmethod
    def _affine_formula(
        cls, offset: Fraction, scale: Fraction, to_base: bool
    ) -> str:
        """Human-readable affine formula for a temperature unit."""
        scale_text = cls._fraction_text(scale)
        other_text = cls._fraction_text(1 / scale)
        offset_text = cls._exact_decimal_or_none(offset) or cls._fraction_text(
            offset
        )
        if to_base:
            if scale == 1:
                return f"K = value + {offset_text}" if offset else "K = value"
            if offset:
                return f"K = (value + {offset_text}) × {scale_text}"
            return f"K = value × {scale_text}"
        if scale == 1:
            return f"value = K − {offset_text}" if offset else "value = K"
        if offset:
            return f"value = K × {other_text} − {offset_text}"
        return f"value = K × {other_text}"

    @staticmethod
    def _fraction_text(fraction: Fraction) -> str:
        """Compact text form of a fraction ("5/9", "1", "273.15")."""
        exact = UnitConverterTool._exact_decimal_or_none(fraction)
        if exact is not None:
            return exact
        if fraction.denominator == 1:
            return str(fraction.numerator)
        return f"{fraction.numerator}/{fraction.denominator}"

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any],
        error_type: str,
        message: str,
        suggestions: Optional[List[str]] = None,
        cap: Optional[int] = _SUGGESTIONS,
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        payload: Dict[str, Any] = {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
        if suggestions:
            payload["suggestions"] = (
                suggestions if cap is None else suggestions[:cap]
            )
        return payload
