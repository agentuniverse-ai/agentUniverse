#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: collection_stats_tool.py

"""Descriptive statistics over a collection of numbers, pure stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency statistics utility
agents can call to summarise numeric data: a sensor reading log, a
column of scores, response times, or any list of measurements.

The tool is a thin, strictly-validated façade over the standard
library ``statistics`` / ``math`` / ``json`` modules and supports three
modes:

* ``stats`` — a full descriptive summary of the numbers: ``count``,
  ``min``, ``max``, ``range``, ``sum``, ``mean``, ``median``, ``mode``
  (the list of most-frequent values), population and sample variance
  and standard deviation, quartiles ``q1`` / ``q2`` / ``q3`` computed
  with the *inclusive* method, the interquartile range, the 1.5*IQR
  outlier fences and the list of outlier values they select.
* ``frequencies`` — a value-to-count table sorted by count descending
  then value ascending, with the distinct-value count and an optional
  ``top_n`` truncation.
* ``zscore`` — one z-score per input value, computed against the
  sample's own mean and *sample* standard deviation; when every value
  is identical the sample stdev is 0, z-scores are undefined, and the
  result carries a structured ``note`` explaining that while reporting
  ``null`` z-scores instead of raising.

Numbers are accepted as a JSON array string (``"[1, 2.5, -3e2]"``), as
one-per-line plain text (leniently: blank lines are skipped and commas
or spaces may also separate tokens), or as an actual Python sequence
of ints/floats for programmatic callers. Every form accepts the same
number grammar — an optional sign, digits with an optional fractional
part, and an optional exponent, so scientific notation such as
``-3e2`` or ``1.5E-3`` and forms like ``+.5`` parse in JSON, text and
sequence string elements alike. All values are normalised to
finite floats: ``NaN``, infinities, booleans and any other
non-numeric token are rejected with their position (element index for
sequences and JSON arrays; line and token number for text).

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, missing ``numbers``, a non-string
non-sequence ``numbers`` value, a count outside 2..10,000, oversized
input text, an invalid ``top_n``) raise a ``ValueError``, mirroring
the other common tools. Errors that depend on the *content being
processed* — a non-numeric or non-finite token, a malformed JSON
array — are returned as a structured ``error`` payload so an agent
can react without catching exceptions.
"""

import json
import math
import re
import statistics
from collections import Counter
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# A strict numeric token: optional sign, digits with an optional
# fractional part and an optional exponent. Deliberately excludes
# "nan", "inf", "infinity", "1_000", "0x10" and every other spelling
# float() would quietly accept.
_NUMBER_TOKEN = re.compile(
    r"\A[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\Z"
)
# Lenient text separators: whitespace runs and commas.
_TOKEN_SEPARATORS = re.compile(r"[\s,]+")


class _ContentError(Exception):
    """Internal carrier for content-level parse failures."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class CollectionStatsTool(Tool):
    """Descriptive statistics over a collection of numbers, pure stdlib.

    Attributes:
        max_input_chars (int): Upper bound on the ``numbers`` string
            length; longer inputs are rejected before any parsing.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "collection_stats_tool"
    description: str = (
        "Collection statistics tool — pure Python stdlib, no network "
        "required. Descriptive statistics over a list of numbers: "
        "mode='stats' (count, min, max, range, sum, mean, median, "
        "mode, population and sample variance/stdev, inclusive-method "
        "quartiles Q1/Q2/Q3, IQR, 1.5*IQR outlier fences and outlier "
        "list), mode='frequencies' (value-to-count table sorted by "
        "count desc then value, optional top_n) and mode='zscore' "
        "(per-value z-scores against the sample's own mean and sample "
        "stdev, with a structured note when the stdev is 0). Numbers "
        "are accepted as a JSON list string, one-per-line text or a "
        "sequence; non-numeric tokens are rejected with their position."
    )

    MODES: ClassVar[tuple] = ("stats", "frequencies", "zscore")
    MIN_NUMBERS: ClassVar[int] = 2
    MAX_NUMBERS: ClassVar[int] = 10_000

    max_input_chars: int = 200_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        numbers: Any = None,
        top_n: Any = None,
    ) -> dict[str, Any]:
        """Run one statistics operation.

        Args:
            mode (str): One of ``stats`` / ``frequencies`` / ``zscore``.
            numbers (str | sequence): The numbers to analyse — a JSON
                array string such as ``"[1, 2.5, -3e2]"``, plain text
                with one number per line (leniently: blank lines are
                skipped and commas or spaces also separate tokens), or
                a list/tuple of ints/floats. Between 2 and 10,000
                finite values are required.
            top_n (int): ``frequencies`` mode only — keep just the
                first ``top_n`` entries of the (sorted) frequency
                table. A positive integer or None.

        Returns:
            Dict[str, Any]: The operation result (the summary, the
                frequency table, or the per-value z-scores, always with
                the call context) or a structured ``error`` payload for
                content-level failures (non-numeric tokens, non-finite
                values, malformed JSON).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens), including a value count outside
                the 2..10,000 bounds.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        try:
            values, source = self._parse_numbers(numbers)
        except _ContentError as exc:
            return self._error_result({"mode": mode}, exc.error_type, exc.message)
        count = len(values)
        if not self.MIN_NUMBERS <= count <= self.MAX_NUMBERS:
            self._invalid(
                f"numbers must contain between {self.MIN_NUMBERS} and "
                f"{self.MAX_NUMBERS:,} values (got {count:,})"
            )
        if mode == "stats":
            return self._run_stats(values, source)
        if mode == "frequencies":
            return self._run_frequencies(values, source, top_n)
        return self._run_zscore(values, source)

    # ------------------------------------------------------------------ #
    # Input parsing (content errors carried, not raised)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"collection_stats_tool: {message}")

    def _parse_numbers(self, numbers: Any) -> tuple[list[float], str]:
        """Normalise any accepted ``numbers`` form to finite floats.

        Returns a ``(values, source)`` pair where ``source`` describes
        the accepted input shape (``json_list`` / ``text`` /
        ``sequence``). Content-level problems raise the internal
        ``_ContentError`` for the caller to convert into a structured
        error payload.
        """
        if numbers is None or isinstance(numbers, bool):
            self._invalid(
                "numbers is required and must be a JSON list string, "
                f"one-per-line text or a sequence of numbers (got {numbers!r})"
            )
        if isinstance(numbers, str):
            if len(numbers) > self.max_input_chars:
                self._invalid(
                    f"numbers text exceeds the {self.max_input_chars:,}"
                    f"-character limit (got {len(numbers):,} characters)"
                )
            text = numbers.strip()
            if not text:
                return [], "text"
            if text.startswith("["):
                return self._parse_json_list(text)
            return self._parse_text_tokens(text)
        if isinstance(numbers, (list, tuple)):
            return self._convert_elements(list(numbers)), "sequence"
        self._invalid(
            "numbers must be a JSON list string, one-per-line text or "
            f"a sequence of numbers (got {numbers!r})"
        )

    @staticmethod
    def _parse_json_list(text: str) -> tuple[list[float], str]:
        """Parse a JSON array string into finite floats."""
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise _ContentError(
                "invalid_json",
                "numbers is not a valid JSON array: "
                f"{exc.msg} at line {exc.lineno} column {exc.colno} "
                f"(got {text[:64]!r})",
            ) from exc
        if not isinstance(data, list):
            raise _ContentError(
                "invalid_json",
                "numbers must be a JSON array of numbers "
                f"(got {text[:64]!r})",
            )
        return CollectionStatsTool._convert_elements(data), "json_list"

    @staticmethod
    def _parse_text_tokens(text: str) -> tuple[list[float], str]:
        """Parse lenient one-per-line text into finite floats."""
        values: list[float] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            tokens = [token for token in _TOKEN_SEPARATORS.split(line) if token]
            for token_no, token in enumerate(tokens, start=1):
                where = f"line {line_no}, token {token_no}"
                if not _NUMBER_TOKEN.match(token):
                    raise _ContentError(
                        "invalid_numbers",
                        f"non-numeric token {token!r} at {where}",
                    )
                numeric = float(token)
                if not math.isfinite(numeric):
                    raise _ContentError(
                        "invalid_numbers",
                        f"token {token!r} at {where} is not finite "
                        "(it overflows the floating-point range)",
                    )
                values.append(numeric)
        return values, "text"

    @staticmethod
    def _convert_elements(elements: list[Any]) -> list[float]:
        """Convert sequence / JSON-array elements to finite floats.

        Each element must be an int or float (bools are rejected even
        though ``bool`` subclasses ``int``); numeric strings are
        accepted leniently and validated with the same strict token
        grammar as text input.
        """
        values: list[float] = []
        for index, element in enumerate(elements):
            candidate: Any = element
            if isinstance(candidate, str):
                token = candidate.strip()
                candidate = (
                    float(token) if _NUMBER_TOKEN.match(token) else None
                )
            if (
                candidate is None
                or isinstance(candidate, bool)
                or not isinstance(candidate, (int, float))
            ):
                raise _ContentError(
                    "invalid_numbers",
                    f"element at index {index} is not a number "
                    f"(got {str(element)[:64]!r})",
                )
            try:
                numeric = float(candidate)
            except OverflowError:
                raise _ContentError(
                    "invalid_numbers",
                    f"element at index {index} is out of the "
                    "floating-point range (got "
                    f"{str(element)[:32]})",
                ) from None
            if not math.isfinite(numeric):
                raise _ContentError(
                    "invalid_numbers",
                    f"element at index {index} is not finite "
                    "(NaN or infinity)",
                )
            values.append(numeric)
        return values

    # ------------------------------------------------------------------ #
    # stats mode
    # ------------------------------------------------------------------ #

    def _run_stats(self, values: list[float], source: str) -> dict[str, Any]:
        """Compute the full descriptive summary.

        Quartiles use the *inclusive* method — the same estimator as
        ``statistics.quantiles(..., method='inclusive')``: the p-th
        quantile of N sorted values sits at 0-based fractional
        position ``p * (N - 1)`` and linearly interpolates between the
        two adjacent order statistics, so ``q2`` always equals the
        median. Outliers are the values falling outside the fences
        ``q1 - 1.5 * IQR`` and ``q3 + 1.5 * IQR``.
        """
        count = len(values)
        ordered = sorted(values)
        minimum, maximum = ordered[0], ordered[-1]
        total = math.fsum(values)
        mean = total / count
        mode_counts = Counter(values)
        highest = max(mode_counts.values())
        mode_values = sorted(
            value for value, seen in mode_counts.items() if seen == highest
        )
        q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = sorted(
            value for value in values
            if value < lower_fence or value > upper_fence
        )
        # NOTE: unlike the other modes, the stats payload does not
        # carry a "mode" selector string — the key is reserved for the
        # statistical mode (the most-frequent value list) here.
        return {
            "source": source,
            "count": count,
            "min": minimum,
            "max": maximum,
            "range": maximum - minimum,
            "sum": total,
            "mean": mean,
            "median": float(statistics.median(values)),
            "mode": mode_values,
            "variance_population": statistics.pvariance(values),
            "variance_sample": statistics.variance(values),
            "stdev_population": statistics.pstdev(values),
            "stdev_sample": statistics.stdev(values),
            "quartiles": {
                "method": "inclusive (linear interpolation at position p*(N-1))",
                "q1": q1,
                "q2": q2,
                "q3": q3,
            },
            "iqr": iqr,
            "outlier_fences": {
                "rule": "1.5 * IQR",
                "lower": lower_fence,
                "upper": upper_fence,
            },
            "outliers": outliers,
        }

    # ------------------------------------------------------------------ #
    # frequencies mode
    # ------------------------------------------------------------------ #

    def _run_frequencies(
        self, values: list[float], source: str, top_n: Any
    ) -> dict[str, Any]:
        """Build the value-to-count table (count desc, value asc)."""
        clean_top_n = self._validate_top_n(top_n)
        counts = Counter(values)
        entries = [
            {"value": value, "count": seen}
            for value, seen in sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )
        ]
        result: dict[str, Any] = {
            "mode": "frequencies",
            "source": source,
            "count": len(values),
            "distinct": len(counts),
            "frequencies": entries,
        }
        if clean_top_n is not None:
            # A top_n larger than the number of distinct values simply
            # returns every entry.
            result["top_n"] = clean_top_n
            result["frequencies"] = entries[:clean_top_n]
        return result

    @classmethod
    def _validate_top_n(cls, top_n: Any) -> int | None:
        """Validate the optional ``frequencies`` truncation size."""
        if top_n is None:
            return None
        if isinstance(top_n, bool) or not isinstance(top_n, int):
            cls._invalid(
                f"top_n must be a positive integer or None (got {top_n!r})"
            )
        if top_n < 1:
            cls._invalid(f"top_n must be a positive integer or None (got {top_n})")
        return top_n

    # ------------------------------------------------------------------ #
    # zscore mode
    # ------------------------------------------------------------------ #

    def _run_zscore(self, values: list[float], source: str) -> dict[str, Any]:
        """Standardise every value against the sample itself.

        z = (value - mean) / sample_stdev with the sample (``ddof=1``)
        standard deviation of the very same numbers. When every value
        is identical the stdev is 0, division is undefined, and each
        z-score is reported as ``null`` with an explanatory note.
        """
        count = len(values)
        mean = math.fsum(values) / count
        stdev = statistics.stdev(values)
        result: dict[str, Any] = {
            "mode": "zscore",
            "source": source,
            "count": count,
            "mean": mean,
            "stdev": stdev,
            "stdev_kind": "sample",
        }
        if stdev == 0.0:
            return {
                **result,
                "zscores": [
                    {"value": value, "zscore": None} for value in values
                ],
                "note": (
                    "sample stdev is 0 (all values are identical): "
                    "z-scores are undefined and reported as null"
                ),
            }
        return {
            **result,
            "zscores": [
                {"value": value, "zscore": (value - mean) / stdev}
                for value in values
            ],
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
