#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: grade_calculator_tool.py

"""Weighted grade aggregation, letter mapping and curving, pure stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency education-scenario
utility. ``CollectionStatsTool`` already covers plain descriptive
statistics over numbers; this tool covers the grading semantics that
plain statistics cannot express: weighted aggregation, dropping the
lowest-impact assignments, letter mapping and grade curving.

The tool supports four modes:

* ``weighted`` — aggregate ``assignments`` (each ``{name, score,
  weight}``) into a weighted mean ``sum(percent * weight) /
  sum(weight)``. Scores are plain 0-100 numbers or raw marks given
  together with a maximum, either as a nested ``{score, max}`` pair or
  as a sibling ``max`` key; the percent is ``score / max * 100``
  rounded to 2 decimal places. The result carries the per-assignment
  contribution table (percent, weighted points and the contribution to
  the final mean), the total weight, an unweighted mean for
  comparison, and a ``weight_warning`` field whenever the total weight
  is not 100 (the weighted mean itself is scale-invariant, so fraction
  weights summing to 1 work too — they simply trigger the warning).
* ``drop_lowest`` — the same input plus ``drop_n``: the ``drop_n``
  assignments with the lowest *weighted impact* ``percent * weight``
  are removed and the weighted mean is recomputed over the survivors.
  Ranking by impact is deliberately different from ranking by raw
  score: a mediocre mark on a heavily weighted assignment contributes
  more points than a weak mark on a negligible one.
* ``letter`` — map a single 0-100 ``score`` to a letter grade via a
  threshold table. The default table is the American A >= 90, B >= 80,
  C >= 70, D >= 60, F-below-60 scale; a custom table (a JSON array of
  ``{letter, min_score}`` objects or an equivalently ordered mapping)
  is validated for strictly descending thresholds in 0..100. Grade
  points are spaced evenly from 4.0 for the highest band to 0.0 for
  the lowest, which reproduces the standard A=4.0 … F=0.0 points for
  the default five-band table.
* ``curve`` — curve a list of ``scores`` (each 0-100) with
  ``curve='flat_add'`` (add a positive ``amount`` to every score,
  capping at 100) or ``curve='scale_to_max'`` (linear rescale
  ``curved = score * 100 / max(scores)`` so the maximum becomes 100).

All computed statistics are floats rounded to 2 decimal places
(``scale_factor`` to 4), while echoed inputs (``score``, ``weight``,
``max``, ``amount``) are preserved verbatim; the arithmetic itself is
plain float (no ``Decimal``), and percents are rounded before they
enter the aggregate so every reported table is exactly reproducible by
hand.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing ``assignments``/``score``/
``scores``, a non-integer or out-of-bounds ``drop_n``, a missing or
non-positive ``amount`` for ``flat_add``, an over-large collection)
raise a ``ValueError``, mirroring the other common tools. Errors that
depend on the *content being processed* — a malformed JSON array, an
assignment element that is not an object, a missing or non-numeric
``score``/``weight``, a ``max`` of zero or less, an unknown assignment
key, a non-monotonic custom threshold table, weights whose products or
sum overflow the floating-point range, a ``drop_lowest`` call whose
survivors carry no positive weight — are returned as a structured
``error`` payload so an agent can react without catching exceptions.
"""

import json
import math
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class _ContentError(Exception):
    """Internal carrier for content-level parse failures."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class GradeCalculatorTool(Tool):
    """Weighted grade aggregation, letter mapping and curving.

    Attributes:
        max_input_chars (int): Upper bound on any string parameter
            length; longer inputs are rejected before any parsing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "grade_calculator_tool"
    description: str = (
        "Grade calculator tool — pure Python stdlib, no network "
        "required. Education-scenario score aggregation: "
        "mode='weighted' (assignments [{name, score, weight}] with "
        "plain 0-100 scores or raw {score, max} pairs whose percent "
        "is computed → weighted mean sum(percent*weight)/sum(weight), "
        "per-assignment contribution table, total weight with a "
        "warning field when it is not 100, unweighted mean for "
        "comparison), mode='drop_lowest' (same plus drop_n: remove "
        "the drop_n assignments with the lowest weighted impact "
        "percent*weight — not the lowest raw scores — and recompute "
        "the mean over the survivors), mode='letter' (map a 0-100 "
        "score to a letter via the default American A>=90/B>=80/C>=70/"
        "D>=60/F table or a validated strictly-descending custom "
        "threshold table, with 4.0-scale grade points evenly spaced "
        "from 4.0 down to 0.0) and mode='curve' (curve a scores list "
        "with flat_add, adding a positive amount capped at 100, or "
        "scale_to_max, the linear rescale curved = score * 100 / "
        "max(scores)). Malformed parameters raise ValueError; "
        "content-level failures return structured error payloads."
    )

    MODES: ClassVar[tuple] = ("weighted", "drop_lowest", "letter", "curve")
    CURVE_KINDS: ClassVar[tuple] = ("flat_add", "scale_to_max")
    MIN_ASSIGNMENTS: ClassVar[int] = 1
    MAX_ASSIGNMENTS: ClassVar[int] = 500
    MIN_SCORES: ClassVar[int] = 1
    MAX_SCORES: ClassVar[int] = 10_000
    MIN_BANDS: ClassVar[int] = 2
    MAX_BANDS: ClassVar[int] = 10
    # Tolerance for the "total weight is 100" check: totals within
    # 0.01 of 100 count as exactly 100 (float sums such as three
    # 33.333333 weights land at 99.999999).
    TOTAL_WEIGHT_TOLERANCE: ClassVar[float] = 0.01

    DEFAULT_LETTER_TABLE: ClassVar[tuple] = (
        ("A", 90.0),
        ("B", 80.0),
        ("C", 70.0),
        ("D", 60.0),
        ("F", 0.0),
    )

    _ASSIGNMENT_KEYS: ClassVar[frozenset] = frozenset(
        {"name", "score", "max", "weight"}
    )

    max_input_chars: int = 200_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        assignments: Any = None,
        drop_n: Any = None,
        score: Any = None,
        thresholds: Any = None,
        scores: Any = None,
        curve: Any = None,
        amount: Any = None,
    ) -> dict[str, Any]:
        """Run one grade calculation.

        Args:
            mode (str): One of ``weighted`` / ``drop_lowest`` /
                ``letter`` / ``curve``.
            assignments (str | sequence): ``weighted`` and
                ``drop_lowest`` only — the assignments to aggregate,
                as a JSON array string or a sequence of
                ``{name?, score, weight}`` mappings. ``score`` is a
                plain 0-100 number, a nested ``{score, max}`` pair or
                a raw number accompanied by a sibling ``max`` key;
                ``weight`` is a finite number >= 0.
            drop_n (int): ``drop_lowest`` only — how many of the
                lowest-impact assignments to drop. An integer with
                ``1 <= drop_n < len(assignments)``; defaults to 1.
            score (float): ``letter`` only — the 0-100 score to map.
            thresholds (str | sequence | mapping): ``letter`` only —
                a custom table of ``{letter, min_score}`` objects (or
                an equivalently ordered mapping) replacing the default
                A/B/C/D/F scale. 2 to 10 bands with unique letters
                and strictly descending ``min_score`` values in
                0..100.
            scores (str | sequence): ``curve`` only — the 0-100
                scores to curve, as a JSON array string or a sequence
                of numbers.
            curve (str): ``curve`` only — ``flat_add`` or
                ``scale_to_max``.
            amount (float): ``flat_add`` only — the positive number
                of points to add to every score (results cap at 100).

        Returns:
            Dict[str, Any]: The operation result (always with the call
                context) or a structured ``error`` payload for
                content-level failures (malformed JSON, invalid
                assignment elements, degenerate curve input).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        if mode in ("weighted", "drop_lowest"):
            try:
                parsed = self._parse_assignments(assignments)
                count = len(parsed)
                if not self.MIN_ASSIGNMENTS <= count <= self.MAX_ASSIGNMENTS:
                    self._invalid(
                        f"assignments must contain between "
                        f"{self.MIN_ASSIGNMENTS} and {self.MAX_ASSIGNMENTS} "
                        f"entries (got {count})"
                    )
                if mode == "weighted":
                    return self._run_weighted(parsed)
                clean_drop_n = self._validate_drop_n(drop_n, count)
                return self._run_drop_lowest(parsed, clean_drop_n)
            except _ContentError as exc:
                return self._error_result(
                    {"mode": mode}, exc.error_type, exc.message
                )
        if mode == "letter":
            try:
                return self._run_letter(score, thresholds)
            except _ContentError as exc:
                return self._error_result(
                    {"mode": "letter"}, exc.error_type, exc.message
                )
        try:
            return self._run_curve(scores, curve, amount)
        except _ContentError as exc:
            return self._error_result(
                {"mode": "curve"}, exc.error_type, exc.message
            )

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"grade_calculator_tool: {message}")

    @classmethod
    def _number(
        cls,
        value: Any,
        label: str,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
        strict_minimum: bool = False,
    ) -> float:
        """Validate one numeric parameter and return it as a float.

        Booleans are rejected even though ``bool`` subclasses ``int``.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            cls._invalid(f"{label} must be a number (got {value!r})")
        numeric = float(value)
        if not math.isfinite(numeric):
            cls._invalid(f"{label} must be finite (got {value})")
        if minimum is not None:
            if strict_minimum and numeric <= minimum:
                cls._invalid(
                    f"{label} must be greater than {minimum} (got {value})"
                )
            if not strict_minimum and numeric < minimum:
                cls._invalid(
                    f"{label} must be greater than or equal to {minimum} "
                    f"(got {value})"
                )
        if maximum is not None and numeric > maximum:
            cls._invalid(f"{label} must be at most {maximum} (got {value})")
        return numeric

    @classmethod
    def _element_number(
        cls,
        value: Any,
        label: str,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
        strict_minimum: bool = False,
        error_type: str = "invalid_assignments",
    ) -> float:
        """Validate one numeric value inside parsed content.

        Unlike ``_number`` this raises the internal ``_ContentError``
        so element-level problems surface as structured payloads.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise _ContentError(
                error_type, f"{label} is not a number "
                f"(got {str(value)[:64]!r})"
            )
        numeric = float(value)
        if not math.isfinite(numeric):
            raise _ContentError(
                error_type, f"{label} is not finite (got {value})"
            )
        if minimum is not None:
            if strict_minimum and numeric <= minimum:
                raise _ContentError(
                    error_type,
                    f"{label} must be greater than {minimum} (got {value})",
                )
            if not strict_minimum and numeric < minimum:
                raise _ContentError(
                    error_type,
                    f"{label} must be greater than or equal to {minimum} "
                    f"(got {value})",
                )
        if maximum is not None and numeric > maximum:
            raise _ContentError(
                error_type,
                f"{label} must be at most {maximum} (got {value})",
            )
        return numeric

    def _parse_source(self, value: Any, label: str) -> tuple[Any, str]:
        """Normalise a JSON-array-or-sequence parameter.

        Returns a ``(data, source)`` pair where ``source`` names the
        accepted input shape (``json`` for string input, ``sequence``
        for programmatic lists, tuples and mappings). Content-level
        problems raise the internal ``_ContentError``.
        """
        if value is None or isinstance(value, bool):
            self._invalid(
                f"{label} is required and must be a JSON array string or a "
                f"sequence (got {value!r})"
            )
        if isinstance(value, str):
            if len(value) > self.max_input_chars:
                self._invalid(
                    f"{label} text exceeds the {self.max_input_chars:,}"
                    f"-character limit (got {len(value):,} characters)"
                )
            text = value.strip()
            if not text:
                self._invalid(f"{label} is required and must not be empty")
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise _ContentError(
                    "invalid_json",
                    f"{label} is not valid JSON: {exc.msg} at line "
                    f"{exc.lineno} column {exc.colno} "
                    f"(got {text[:64]!r})",
                ) from exc
            return data, "json"
        if isinstance(value, (list, tuple)):
            return list(value), "sequence"
        if isinstance(value, dict):
            return value, "sequence"
        self._invalid(
            f"{label} must be a JSON array string, a sequence or a "
            f"mapping (got {value!r})"
        )

    # ------------------------------------------------------------------ #
    # Assignment parsing (weighted / drop_lowest)
    # ------------------------------------------------------------------ #

    def _parse_assignments(
        self, assignments: Any
    ) -> tuple[dict[str, Any], ...]:
        """Parse and validate the ``assignments`` collection.

        Every element must be a mapping with a numeric ``weight`` and
        a ``score`` given either as a plain 0-100 number, as a nested
        ``{score, max}`` pair or as a raw number with a sibling
        ``max`` key. Returns one normalised record per assignment:
        ``{"index", "name", "score", "max", "percent", "weight"}``
        where ``percent`` is the 2-dp percentage mark.
        """
        data, source = self._parse_source(assignments, "assignments")
        if not isinstance(data, list):
            raise _ContentError(
                "invalid_json",
                "assignments must be a JSON array of objects "
                f"(got {str(assignments)[:64]!r})",
            )
        records: list[dict[str, Any]] = []
        for index, element in enumerate(data):
            records.append(self._parse_assignment(element, index))
        return tuple(records)

    def _parse_assignment(
        self, element: Any, index: int
    ) -> dict[str, Any]:
        """Validate one assignment element into a normalised record."""
        where = f"assignment at index {index}"
        if not isinstance(element, dict):
            raise _ContentError(
                "invalid_assignments",
                f"{where} must be an object with score and weight keys "
                f"(got {str(element)[:64]!r})",
            )
        unknown = set(element) - self._ASSIGNMENT_KEYS
        if unknown:
            raise _ContentError(
                "invalid_assignments",
                f"{where} has unknown key(s) {sorted(unknown)}; allowed "
                f"keys are {sorted(self._ASSIGNMENT_KEYS)}",
            )
        if "score" not in element:
            raise _ContentError(
                "invalid_assignments", f"{where} is missing the score key"
            )
        if "weight" not in element:
            raise _ContentError(
                "invalid_assignments", f"{where} is missing the weight key"
            )
        name = element.get("name", f"assignment {index + 1}")
        if not isinstance(name, str) or not name.strip() or len(name) > 200:
            raise _ContentError(
                "invalid_assignments",
                f"{where} name must be a non-empty string of at most 200 "
                f"characters (got {str(name)[:64]!r})",
            )
        weight = self._element_number(
            element["weight"], f"{where} weight", minimum=0.0
        )
        raw = element["score"]
        sibling_max = element.get("max")
        if isinstance(raw, dict):
            extra = set(raw) - {"score", "max"}
            if extra:
                raise _ContentError(
                    "invalid_assignments",
                    f"{where} score pair has unknown key(s) {sorted(extra)}; "
                    "allowed keys are ['max', 'score']",
                )
            if "score" not in raw or "max" not in raw:
                raise _ContentError(
                    "invalid_assignments",
                    f"{where} score pair needs both score and max keys "
                    f"(got {str(raw)[:64]!r})",
                )
            if sibling_max is not None:
                raise _ContentError(
                    "invalid_assignments",
                    f"{where} combines a nested {{score, max}} pair with a "
                    "sibling max key; use one form or the other",
                )
            maximum = self._element_number(
                raw["max"], f"{where} score pair max",
                minimum=0.0, strict_minimum=True,
            )
            value = self._element_number(
                raw["score"], f"{where} score pair score"
            )
            percent = self._percent(value, maximum, where, "score pair")
        else:
            value = self._element_number(raw, f"{where} score")
            if sibling_max is None:
                if not 0.0 <= value <= 100.0:
                    raise _ContentError(
                        "invalid_assignments",
                        f"{where} score must be between 0 and 100 when no "
                        f"max is given (got {value}); supply a max for raw "
                        "marks",
                    )
                return {
                    "index": index,
                    "name": name,
                    "score": value,
                    "max": None,
                    "percent": round(value, 2),
                    "weight": weight,
                }
            maximum = self._element_number(
                sibling_max, f"{where} max",
                minimum=0.0, strict_minimum=True,
            )
            percent = self._percent(value, maximum, where, "max form")
        return {
            "index": index,
            "name": name,
            "score": value,
            "max": maximum,
            "percent": percent,
            "weight": weight,
        }

    @classmethod
    def _percent(
        cls, value: float, maximum: float, where: str, form: str
    ) -> float:
        """Compute the 2-dp percentage of a raw mark out of ``maximum``."""
        if value < 0.0 or value > maximum:
            raise _ContentError(
                "invalid_assignments",
                f"{where} raw score must be between 0 and its max "
                f"{maximum} in the {form} (got {value} of {maximum})",
            )
        return round(value / maximum * 100.0, 2)

    @staticmethod
    def _validate_drop_n(drop_n: Any, count: int) -> int:
        """Validate the ``drop_lowest`` drop count against the count.

        The default of 1 goes through the same bounds as an explicit
        value, so a single-assignment collection (where no valid drop
        count exists) is rejected up front.
        """
        if drop_n is None:
            drop_n = 1
        elif isinstance(drop_n, bool) or not isinstance(drop_n, int):
            GradeCalculatorTool._invalid(
                f"drop_n must be an integer or None (got {drop_n!r})"
            )
        if drop_n < 1:
            GradeCalculatorTool._invalid(
                f"drop_n must be at least 1 (got {drop_n})"
            )
        if drop_n >= count:
            GradeCalculatorTool._invalid(
                f"drop_n must be strictly less than the assignment count "
                f"({drop_n} requested, {count} assignments)"
            )
        return drop_n

    # ------------------------------------------------------------------ #
    # weighted / drop_lowest computation
    # ------------------------------------------------------------------ #

    @classmethod
    def _aggregate(
        cls, records: tuple[dict[str, Any], ...]
    ) -> dict[str, Any]:
        """Aggregate normalised records into a weighted summary.

        The weighted mean is ``sum(percent * weight) / sum(weight)``,
        scale-invariant in the weights, so percent-style (summing to
        100) and fraction-style (summing to 1) weights give the same
        mean. The contribution table reports, per assignment, the
        2-dp percent, the weighted points ``percent * weight`` and
        the contribution ``percent * weight / total_weight`` those
        points make to the final mean.

        Weights are individually finite but may still be
        astronomically large, so any non-finite intermediate (a
        ``percent * weight`` product, the weight total or the
        weighted sum) is reported as a structured
        ``invalid_assignments`` error instead of leaking ``inf`` or
        ``nan`` into the result.
        """
        try:
            total_weight = math.fsum(record["weight"] for record in records)
        except OverflowError:
            raise _ContentError(
                "invalid_assignments",
                "assignments weights are too large: their total "
                "overflows the floating-point range",
            ) from None
        if total_weight <= 0.0:
            cls._invalid(
                "assignments weights must sum to a positive total "
                "(every weight is 0)"
            )
        table = []
        weighted_sum = 0.0
        percent_sum = 0.0
        for record in records:
            weighted_points = record["percent"] * record["weight"]
            if not math.isfinite(weighted_points):
                raise _ContentError(
                    "invalid_assignments",
                    f"assignment {record['name']!r} overflows: percent "
                    f"{record['percent']} times weight {record['weight']} "
                    "exceeds the floating-point range",
                )
            weighted_sum += weighted_points
            percent_sum += record["percent"]
            entry = {
                "name": record["name"],
                "score": record["score"],
                "percent": record["percent"],
                "weight": record["weight"],
                "weighted_points": round(weighted_points, 2),
                "contribution": round(weighted_points / total_weight, 2),
            }
            if record["max"] is not None:
                entry["max"] = record["max"]
            table.append(entry)
        if not math.isfinite(weighted_sum):
            raise _ContentError(
                "invalid_assignments",
                "assignments are too large: the weighted sum overflows "
                "the floating-point range",
            )
        result: dict[str, Any] = {
            "count": len(records),
            "assignments": table,
            "total_weight": round(total_weight, 2),
            "weighted_mean": round(weighted_sum / total_weight, 2),
            "unweighted_mean": round(percent_sum / len(records), 2),
        }
        if abs(total_weight - 100.0) > cls.TOTAL_WEIGHT_TOLERANCE:
            result["weight_warning"] = (
                f"total weight is {round(total_weight, 2)}, not 100: the "
                "weighted mean is still computed relative to the given "
                "weights, but only a total of exactly 100 makes each "
                "weighted_points entry read directly as final-grade points"
            )
        return result

    def _run_weighted(
        self, records: tuple[dict[str, Any], ...]
    ) -> dict[str, Any]:
        """Aggregate every assignment."""
        return {"mode": "weighted", **self._aggregate(records)}

    def _run_drop_lowest(
        self, records: tuple[dict[str, Any], ...], drop_n: int
    ) -> dict[str, Any]:
        """Drop the ``drop_n`` lowest-impact assignments and recompute.

        The *weighted impact* of an assignment is ``percent * weight``
        — the raw points it contributes to the weighted sum. Ranking
        by impact is deliberately different from ranking by raw
        score: ``{score: 85, weight: 9}`` (impact 765) is dropped
        before ``{score: 60, weight: 90}`` (impact 5400) even though
        60 is the lower score. Ties break deterministically on the
        original element index. When the survivors carry no positive
        weight in total (every remaining assignment has weight 0) no
        weighted mean is defined, and the call returns a structured
        ``degenerate_weights`` error instead of raising.
        """
        before = self._aggregate(records)
        ranked = sorted(
            records,
            key=lambda record: (
                record["percent"] * record["weight"],
                record["index"],
            ),
        )
        dropped, kept = ranked[:drop_n], ranked[drop_n:]
        if math.fsum(record["weight"] for record in kept) <= 0.0:
            return self._error_result(
                {"mode": "drop_lowest", "drop_n": drop_n},
                "degenerate_weights",
                "dropping the lowest-impact assignments leaves only "
                "zero-weight survivors, so no weighted mean is defined "
                "over the kept assignments",
            )
        after = self._aggregate(tuple(kept))
        return {
            "mode": "drop_lowest",
            "drop_n": drop_n,
            "before": {
                "count": before["count"],
                "total_weight": before["total_weight"],
                "weighted_mean": before["weighted_mean"],
            },
            "after": after,
            "mean_change": round(
                after["weighted_mean"] - before["weighted_mean"], 2
            ),
            "dropped": [
                {
                    "name": record["name"],
                    "score": record["score"],
                    "percent": record["percent"],
                    "weight": record["weight"],
                    "impact": round(
                        record["percent"] * record["weight"], 2
                    ),
                }
                for record in dropped
            ],
        }

    # ------------------------------------------------------------------ #
    # letter mode
    # ------------------------------------------------------------------ #

    def _run_letter(self, score: Any, thresholds: Any) -> dict[str, Any]:
        """Map one 0-100 score onto a letter band with grade points.

        Grade points are spaced evenly from 4.0 for the highest band
        down to 0.0 for the lowest: with ``K`` bands the ``i``-th band
        (0-based, descending) earns ``4.0 * (K - 1 - i) / (K - 1)``,
        which for the default five-band table is exactly the American
        A=4.0, B=3.0, C=2.0, D=1.0, F=0.0 scale. The lowest band is
        the catch-all for every score below its threshold.
        """
        clean_score = self._number(
            score, "score", minimum=0.0, maximum=100.0
        )
        if thresholds is None:
            table = list(self.DEFAULT_LETTER_TABLE)
            table_kind = "default"
        else:
            table = self._parse_thresholds(thresholds)
            table_kind = "custom"
        bands = len(table)
        grade_points = [
            round(4.0 * (bands - 1 - position) / (bands - 1), 2)
            for position in range(bands)
        ]
        matched = bands - 1
        for position, (_, minimum) in enumerate(table):
            if clean_score >= minimum:
                matched = position
                break
        letter, minimum = table[matched]
        return {
            "mode": "letter",
            "score": clean_score,
            "letter": letter,
            "grade_points": grade_points[matched],
            "band_min_score": minimum,
            "table_kind": table_kind,
            "table": [
                {
                    "letter": entry_letter,
                    "min_score": entry_minimum,
                    "grade_points": grade_points[position],
                }
                for position, (entry_letter, entry_minimum)
                in enumerate(table)
            ],
        }

    def _parse_thresholds(self, thresholds: Any) -> list[tuple[str, float]]:
        """Validate a custom letter-threshold table (descending).

        Accepts a JSON array string, a sequence of
        ``{letter, min_score}`` mappings or a mapping of
        ``letter -> min_score`` whose insertion order is already
        descending. Validation: 2 to 10 bands, unique non-empty
        letters of at most 8 characters, ``min_score`` finite in
        0..100 and strictly descending in the given order.
        """
        data, _ = self._parse_source(thresholds, "thresholds")
        if isinstance(data, dict):
            bands = [
                {"letter": letter, "min_score": minimum}
                for letter, minimum in data.items()
            ]
        elif isinstance(data, list):
            bands = data
        else:
            self._invalid(
                "thresholds must be a JSON array of {letter, min_score} "
                f"objects or an ordered mapping (got {str(thresholds)[:64]!r})"
            )
        if not self.MIN_BANDS <= len(bands) <= self.MAX_BANDS:
            self._invalid(
                f"thresholds must contain between {self.MIN_BANDS} and "
                f"{self.MAX_BANDS} bands (got {len(bands)})"
            )
        table: list[tuple[str, float]] = []
        seen_letters: set[str] = set()
        for index, band in enumerate(bands):
            if not isinstance(band, dict) or set(band) != {"letter", "min_score"}:
                self._invalid(
                    f"thresholds band {index} must be an object with exactly "
                    f"a letter and a min_score key (got {str(band)[:64]!r})"
                )
            letter = band["letter"]
            if (
                not isinstance(letter, str)
                or not letter.strip()
                or len(letter) > 8
            ):
                self._invalid(
                    f"thresholds band {index} letter must be a non-empty "
                    f"string of at most 8 characters (got {letter!r})"
                )
            if letter in seen_letters:
                self._invalid(
                    f"thresholds letter {letter!r} appears more than once"
                )
            seen_letters.add(letter)
            minimum = self._number(
                band["min_score"],
                f"thresholds band {index} min_score",
                minimum=0.0,
                maximum=100.0,
            )
            if table and minimum >= table[-1][1]:
                self._invalid(
                    f"thresholds must be sorted strictly descending; band "
                    f"{index} min_score {minimum} is not below band "
                    f"{index - 1} min_score {table[-1][1]}"
                )
            table.append((letter, minimum))
        return table

    # ------------------------------------------------------------------ #
    # curve mode
    # ------------------------------------------------------------------ #

    def _run_curve(
        self, scores: Any, curve: Any, amount: Any
    ) -> dict[str, Any]:
        """Curve a list of 0-100 scores.

        ``flat_add`` adds a positive ``amount`` to every score and
        caps each result at 100. ``scale_to_max`` applies the linear
        rescale ``curved = score * 100 / max(scores)`` so the highest
        score becomes exactly 100 and the others keep their relative
        distances. Curved scores are rounded to 2 decimal places and
        the new mean is the mean of those reported values. The
        ``amount`` parameter is validated before ``scores`` is
        parsed, keeping parameter errors ahead of content errors.
        """
        if curve not in self.CURVE_KINDS:
            self._invalid(
                f"curve must be one of: {', '.join(self.CURVE_KINDS)} "
                f"(got {curve!r})"
            )
        if curve == "flat_add":
            clean_amount = self._number(
                amount, "amount", minimum=0.0, strict_minimum=True
            )
        else:
            clean_amount = None
            if amount is not None:
                self._invalid(
                    f"amount applies to flat_add only and must be omitted "
                    f"for scale_to_max (got {amount!r})"
                )
        data, source = self._parse_source(scores, "scores")
        if not isinstance(data, list):
            raise _ContentError(
                "invalid_json",
                "scores must be a JSON array of numbers "
                f"(got {str(scores)[:64]!r})",
            )
        if not self.MIN_SCORES <= len(data) <= self.MAX_SCORES:
            self._invalid(
                f"scores must contain between {self.MIN_SCORES} and "
                f"{self.MAX_SCORES:,} values (got {len(data):,})"
            )
        values = [
            self._element_number(
                value, f"scores element at index {index}",
                minimum=0.0, maximum=100.0,
                error_type="invalid_scores",
            )
            for index, value in enumerate(data)
        ]
        original_mean = round(math.fsum(values) / len(values), 2)
        result: dict[str, Any] = {
            "mode": "curve",
            "curve": curve,
            "source": source,
            "count": len(values),
            "original": {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "mean": original_mean,
            },
        }
        if curve == "flat_add":
            curved = [
                round(min(100.0, value + clean_amount), 2) for value in values
            ]
            return {
                **result,
                "amount": clean_amount,
                "formula": "curved = min(100, score + amount)",
                "curved_scores": curved,
                "capped_count": sum(
                    1 for value in values if value + clean_amount > 100.0
                ),
                "new_mean": round(math.fsum(curved) / len(curved), 2),
                "new_min": min(curved),
                "new_max": max(curved),
            }
        maximum = max(values)
        if maximum <= 0.0:
            return self._error_result(
                {"mode": "curve", "curve": curve},
                "degenerate_scores",
                "scale_to_max requires max(scores) > 0: every score is 0, "
                "so no positive rescale factor exists",
            )
        scale_factor = 100.0 / maximum
        curved = [round(value * scale_factor, 2) for value in values]
        return {
            **result,
            "scale_factor": round(scale_factor, 4),
            "formula": "curved = score * 100 / max(scores)",
            "curved_scores": curved,
            "new_mean": round(math.fsum(curved) / len(curved), 2),
            "new_min": min(curved),
            "new_max": max(curved),
        }

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: dict[str, Any], error_type: str, message: str
    ) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
