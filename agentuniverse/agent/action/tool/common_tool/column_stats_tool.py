#!/usr/bin/env python3
"""CSV column type inference and statistics, pandas-free and deterministic.

Type-inference grammar (checked in this fixed order per non-empty cell):

1. ``integer``  — optional ``+``/``-`` sign followed by one or more ASCII
   digits ``[0-9]`` only.  Unicode digits (for example Arabic-Indic ``٣``)
   are rejected.  Values with a leading zero (``007``, ``-042``) still match
   the grammar but are reported with a ``leading_zero_suspicious`` note
   because they are often codes rather than quantities.  Integers keep
   arbitrary precision; they are never coerced to float.
2. ``float``    — the JSON number grammar extended with leading-dot forms:
   ``[+-]?([0-9]+(.[0-9]+)? | .[0-9]+)([eE][+-]?[0-9]+)?``.  Trailing-dot
   (``1.``) and bare-dot values are rejected.  ``inf``/``-inf``/``nan`` and
   every other infinity/NaN spelling are NOT floats (they are ``text``):
   NaN is a missing-marker in pandas but is ambiguous in raw CSV, so it is
   reported as text instead of being silently dropped.  A grammar match
   whose ``float()`` value is not finite (for example ``1e999``) is also
   demoted to ``text``.
3. ``boolean``  — the word forms ``true``, ``false``, ``True``, ``False``,
   ``TRUE``, ``FALSE`` only.  ``0``/``1`` are integers, not booleans.
4. ``uuid``     — canonical 8-4-4-4-12 lowercase hex.  Uppercase hex is
   ``text``.
5. ``datetime`` — the value starts with an ASCII digit, is 6-35 characters
   long, contains ``-``, ``/`` or ``:``, and matches the FIRST entry of the
   fixed, ordered format list in ``_DATETIME_FORMATS`` (ISO 8601 dates and
   datetimes with ``T`` or space separators, optional fractional seconds and
   ``Z``/``±HH:MM`` offsets, then ``YYYY/MM/DD``, ``MM/DD/YYYY`` and
   ``DD.MM.YYYY``).  At most ``len(_DATETIME_FORMATS)`` parse attempts are
   made per cell; ``2024-13-45`` therefore fails and becomes ``text``.
6. ``text``     — everything else.

An empty cell is a null (CSV has no true-null: an unquoted empty field and a
quoted empty field both parse to ``''`` and are counted in ``nulls``).

Column verdicts: a column whose non-null cells all match one specific type
gets that type; a column whose cells all fail the specific types is ``text``;
anything else is ``mixed`` with ``type_ratio`` = winning-type count / non-null
count, where the winning type is the highest-count specific type (ties broken
by the order integer > float > boolean > datetime > uuid).  A column with no
non-null cells is ``empty``.  ``winning_type`` is null for ``text`` and
``empty`` columns (no specific type matched anything).

Numeric statistics use the stdlib ``statistics`` module (``mean``/``median``
are exact via Fraction internally; ``stdev``/``pstdev`` are the sample and
population variants; ``p50``/``p90`` come from
``statistics.quantiles(n=100, method="inclusive")`` so ``p50 == median``).
``sum`` is exact integer arithmetic for integer columns and
``statistics.fsum`` for float columns.  Histograms use equal-width bins over
``[min, max]``.  Everything is deterministic; ``sample`` mode uses
``random.Random(seed)`` only.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import csv
import io
import math
import random
import re
import statistics
from datetime import datetime
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class ColumnStatsTool(Tool):
    """Profile CSV columns: infer per-column types and compute statistics."""

    max_csv_bytes: int = 8 * 1024 * 1024
    max_rows: int = 200_000
    max_columns: int = 4_096
    max_cell_bytes: int = 1_048_576
    max_distinct: int = 10_000
    max_top_values: int = 10
    max_value_chars: int = 120
    max_warnings: int = 20
    max_conflict_lines: int = 10
    max_failed_cells: int = 20
    max_sample_rows: int = 1_000
    max_preview_values: int = 5
    histogram_bins: int = 10
    mean_drift_threshold: float = 0.10

    _MODES: ClassVar[tuple[str, ...]] = ("profile", "column_detail", "compare", "sample")
    _SAMPLE_MODES: ClassVar[tuple[str, ...]] = ("first", "last", "random")
    _TYPE_PRIORITY: ClassVar[tuple[str, ...]] = ("integer", "float", "boolean", "datetime", "uuid")
    _BOOLEAN_WORDS: ClassVar[frozenset] = frozenset({"true", "false", "True", "False", "TRUE", "FALSE"})
    _INTEGER_RE: ClassVar["re.Pattern[str]"] = re.compile(r"[+-]?[0-9]+")
    _FLOAT_RE: ClassVar["re.Pattern[str]"] = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
    _UUID_RE: ClassVar["re.Pattern[str]"] = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    _LEADING_ZERO_RE: ClassVar["re.Pattern[str]"] = re.compile(r"[+-]?0[0-9]+")
    _ASCII_DIGITS: ClassVar[frozenset] = frozenset("0123456789")

    # Fixed, ordered datetime format list; the first matching entry wins and
    # the order is part of the documented inference contract.
    _DATETIME_FORMATS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("%Y-%m-%d", "Y-m-d"),
        ("%Y-%m-%dT%H:%M:%S", "iso-T"),
        ("%Y-%m-%dT%H:%M:%S.%f", "iso-T-frac"),
        ("%Y-%m-%dT%H:%M:%S%z", "iso-T-tz"),
        ("%Y-%m-%dT%H:%M:%S.%f%z", "iso-T-frac-tz"),
        ("%Y-%m-%d %H:%M:%S", "iso-space"),
        ("%Y-%m-%d %H:%M:%S.%f", "iso-space-frac"),
        ("%Y/%m/%d", "Y/m/d"),
        ("%m/%d/%Y", "m/d/Y"),
        ("%d.%m.%Y", "d.m.Y"),
    )

    _MODE_PARAMS: ClassVar[dict[str, frozenset]] = {
        "profile": frozenset({"csv_text", "delimiter", "quotechar", "header"}),
        "column_detail": frozenset({"csv_text", "column", "column_index", "delimiter", "quotechar", "header"}),
        "compare": frozenset({"csv_text_a", "csv_text_b", "delimiter", "quotechar", "header"}),
        "sample": frozenset({"csv_text", "n", "sample_mode", "seed", "delimiter", "quotechar", "header"}),
    }

    def execute(
        self,
        mode: str,
        csv_text: str | None = None,
        csv_text_a: str | None = None,
        csv_text_b: str | None = None,
        column: str | None = None,
        column_index: int | None = None,
        n: int | None = None,
        sample_mode: str = "first",
        seed: int = 0,
        delimiter: str = ",",
        quotechar: str = '"',
        header: bool = True,
    ) -> dict[str, Any]:
        """Run one of four modes over CSV text and return a bounded report."""
        try:
            self._validate_config()
            operation = self._mode(mode)
            self._reject_cross_mode_params(operation, csv_text, csv_text_a, csv_text_b, column, column_index, n, sample_mode, seed)
            dialect = self._dialect(delimiter, quotechar)
            if operation == "compare":
                return self._compare(self._text(csv_text_a, "csv_text_a"), self._text(csv_text_b, "csv_text_b"), dialect, header)
            table = self._parse(self._text(csv_text, "csv_text"), dialect, header)
            if operation == "profile":
                return self._profile(table, dialect)
            if operation == "column_detail":
                return self._column_detail(table, column, column_index, dialect)
            return self._sample(table, n, sample_mode, seed)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # defensive: bounded report instead of a raise
            return self._error(mode, "operation_error", f"Column statistics failed: {exc}")

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "mode": mode}

    def _validate_config(self) -> None:
        for name in (
            "max_csv_bytes",
            "max_rows",
            "max_columns",
            "max_cell_bytes",
            "max_distinct",
            "max_top_values",
            "max_value_chars",
            "max_warnings",
            "max_conflict_lines",
            "max_failed_cells",
            "max_sample_rows",
            "max_preview_values",
            "histogram_bins",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        threshold = self.mean_drift_threshold
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or threshold <= 0:
            raise ValueError("mean_drift_threshold must be positive")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        operation = value.strip().lower()
        if operation not in ColumnStatsTool._MODES:
            raise ValueError("mode must be profile, column_detail, compare, or sample")
        return operation

    def _reject_cross_mode_params(
        self,
        operation: str,
        csv_text: Any,
        csv_text_a: Any,
        csv_text_b: Any,
        column: Any,
        column_index: Any,
        n: Any,
        sample_mode: Any,
        seed: Any,
    ) -> None:
        supplied = {
            "csv_text": csv_text is not None,
            "csv_text_a": csv_text_a is not None,
            "csv_text_b": csv_text_b is not None,
            "column": column is not None,
            "column_index": column_index is not None,
            "n": n is not None,
            "sample_mode": sample_mode != "first",
            "seed": seed != 0,
        }
        for name, present in supplied.items():
            if present and name not in self._MODE_PARAMS[operation]:
                raise ValueError(f"{name} is not accepted in {operation} mode")

    @staticmethod
    def _text(value: Any, name: str) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be a non-empty string")
        return value

    @staticmethod
    def _dialect(delimiter: Any, quotechar: Any) -> dict[str, str]:
        if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter in "\r\n" or delimiter == quotechar:
            raise ValueError("delimiter must be a single character distinct from quotechar and not CR/LF")
        if not isinstance(quotechar, str) or len(quotechar) != 1 or quotechar in "\r\n":
            raise ValueError("quotechar must be a single character and not CR/LF")
        return {"delimiter": delimiter, "quotechar": quotechar}

    # ------------------------------------------------------------------
    # parsing

    def _parse(self, text: str, dialect: dict[str, str], header: Any) -> dict[str, Any]:
        if not isinstance(header, bool):
            raise TypeError("header must be a boolean")
        if len(text.encode("utf-8")) > self.max_csv_bytes:
            raise ValueError(f"csv text exceeds max_csv_bytes ({self.max_csv_bytes})")
        if text.startswith("﻿"):  # U+FEFF
            text = text[1:]  # strip a UTF-8 BOM before parsing
        raw_rows = self._read_rows(text, dialect)
        if not raw_rows:
            raise ValueError("csv text contains no rows")
        self._check_cells_bounded(raw_rows)
        header_row = raw_rows[0][0] if header else None
        body = raw_rows[1:] if header else raw_rows
        width = len(header_row if header_row is not None else raw_rows[0][0])
        if width == 0:
            raise ValueError("csv has no columns (empty first row)")
        if width > self.max_columns:
            raise ValueError(f"csv exceeds max_columns ({self.max_columns})")
        rows, lines, ragged = self._normalize_rows(body, width)
        return {"names": self._column_names(header_row, width), "rows": rows, "lines": lines, "width": width, "ragged": ragged, "header": header}

    def _read_rows(self, text: str, dialect: dict[str, str]) -> list[tuple[list[str], int]]:
        """Parse with csv.reader, recording the physical line of each row end."""
        previous_limit = csv.field_size_limit()
        csv.field_size_limit(max(previous_limit, self.max_cell_bytes + 1))
        try:
            reader = csv.reader(io.StringIO(text, newline=""), delimiter=dialect["delimiter"], quotechar=dialect["quotechar"])
            raw_rows: list[tuple[list[str], int]] = []
            for row in reader:
                raw_rows.append((row, reader.line_num))
                if len(raw_rows) > self.max_rows:
                    raise ValueError(f"csv exceeds max_rows ({self.max_rows})")
        except csv.Error as exc:
            raise ValueError(f"csv parsing failed: {exc}") from exc
        finally:
            csv.field_size_limit(previous_limit)
        return raw_rows

    def _check_cells_bounded(self, raw_rows: list[tuple[list[str], int]]) -> None:
        for cells, _ in raw_rows:
            for cell in cells:
                if len(cell.encode("utf-8")) > self.max_cell_bytes:
                    raise ValueError(f"cell exceeds max_cell_bytes ({self.max_cell_bytes})")

    @staticmethod
    def _normalize_rows(body: list[tuple[list[str], int]], width: int) -> tuple[list[list[str]], list[int], list[dict[str, int]]]:
        rows: list[list[str]] = []
        lines: list[int] = []
        ragged: list[dict[str, int]] = []
        for cells, line in body:
            if len(cells) != width:
                ragged.append({"kind": "ragged_row", "line": line, "length": len(cells), "expected": width})
            if len(cells) > width:
                cells = cells[:width]  # extra cells beyond the header are ignored
            elif len(cells) < width:
                cells = cells + [""] * (width - len(cells))  # missing cells count as nulls
            rows.append(cells)
            lines.append(line)
        return rows, lines, ragged

    @staticmethod
    def _column_names(header_row: list[str] | None, width: int) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for index in range(width):
            raw = header_row[index] if header_row is not None and index < len(header_row) else ""
            name = raw.strip() or f"col-{index}"
            if name in seen:  # duplicate or colliding header cells fall back to col-N
                name = f"col-{index}"
            if name in seen:
                name = f"col-{index}-x{index}"
            seen.add(name)
            names.append(name)
        return names

    # ------------------------------------------------------------------
    # type inference

    @classmethod
    def _parse_datetime(cls, value: str) -> tuple[datetime, str] | None:
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        for fmt, key in cls._DATETIME_FORMATS:
            try:
                return datetime.strptime(candidate, fmt), key
            except ValueError:
                continue
        return None

    @classmethod
    def _classify(cls, value: str) -> str:
        """Classify one non-empty cell; order and grammar are documented above."""
        if cls._INTEGER_RE.fullmatch(value):
            return "integer"
        if cls._FLOAT_RE.fullmatch(value):
            try:
                if math.isfinite(float(value)):
                    return "float"
            except ValueError:  # pragma: no cover - regex guarantees parseability
                pass
            return "text"
        if value in cls._BOOLEAN_WORDS:
            return "boolean"
        if cls._UUID_RE.fullmatch(value):
            return "uuid"
        if (
            6 <= len(value) <= 35
            and value[0] in cls._ASCII_DIGITS
            and ("-" in value or "/" in value or ":" in value)
            and cls._parse_datetime(value) is not None
        ):
            return "datetime"
        return "text"

    # ------------------------------------------------------------------
    # per-column analysis

    def _scan_cell(self, scan: dict[str, Any], raw: str) -> None:
        """Fold one non-empty cell into the running column scan."""
        shown = self._display(raw)
        if shown in scan["freq"]:
            scan["freq"][shown] += 1
        elif len(scan["freq"]) >= self.max_distinct:
            scan["freq_capped"] = True
        else:
            scan["freq"][shown] = 1
        scan["lengths"].append(len(raw))
        kind = self._classify(raw)
        scan["counts"][kind] += 1
        if kind == "integer":
            if self._LEADING_ZERO_RE.fullmatch(raw):
                scan["leading_zero"] = True
            scan["numeric"].append(int(raw))
        elif kind == "float":
            scan["numeric"].append(float(raw))
        elif kind == "boolean":
            scan["true" if raw in ("true", "True", "TRUE") else "false"] += 1
        elif kind == "datetime":
            parsed = self._parse_datetime(raw)
            if parsed is not None:  # pragma: no cover - classify guarantees this
                scan["datetimes"].append(parsed)

    def _scan_column(self, table: dict[str, Any], index: int) -> dict[str, Any]:
        """Single pass over one column collecting counts, values and frequencies."""
        scan = {
            "counts": {"integer": 0, "float": 0, "boolean": 0, "datetime": 0, "uuid": 0, "text": 0},
            "true": 0,
            "false": 0,
            "numeric": [],
            "datetimes": [],
            "freq": {},
            "freq_capped": False,
            "lengths": [],
            "non_null": 0,
            "nulls": 0,
            "leading_zero": False,
        }
        for cells in table["rows"]:
            raw = cells[index]
            if raw == "":
                scan["nulls"] += 1
                continue
            scan["non_null"] += 1
            self._scan_cell(scan, raw)
        return scan

    @staticmethod
    def _verdict(counts: dict[str, int], non_null: int) -> tuple[str, float, str | None]:
        """Return (inferred_type, type_ratio, winning_type)."""
        best = None
        best_count = 0
        for kind in ColumnStatsTool._TYPE_PRIORITY:
            if counts[kind] > best_count:
                best, best_count = kind, counts[kind]
        if non_null == 0:
            return "empty", 0.0, best
        if best_count == non_null:
            return best, 1.0, best
        if best_count == 0:
            return "text", 1.0, best
        return "mixed", best_count / non_null, best

    def _stats_for(self, inferred: str, best: str | None, scan: dict[str, Any]) -> dict[str, Any] | None:
        if inferred in ("integer", "float"):
            return self._numeric_stats(scan["numeric"])
        if inferred == "mixed" and best in ("integer", "float"):
            if best == "integer":
                subset = [value for value in scan["numeric"] if isinstance(value, int)]
            else:
                subset = [float(value) for value in scan["numeric"] if isinstance(value, float)]
            return self._numeric_stats(subset)
        if inferred == "boolean":
            return {"true": scan["true"], "false": scan["false"]}
        if inferred == "datetime":
            return self._datetime_stats(scan["datetimes"])
        if inferred == "text":
            return self._text_stats(scan["lengths"], scan["freq"], scan["freq_capped"])
        return None

    def _analyze_column(self, table: dict[str, Any], index: int) -> dict[str, Any]:
        scan = self._scan_column(table, index)
        inferred, ratio, best = self._verdict(scan["counts"], scan["non_null"])
        notes: list[str] = []
        if scan["leading_zero"]:
            notes.append("leading_zero_suspicious")
        stats = self._stats_for(inferred, best, scan)
        if inferred == "mixed" and best in ("integer", "float"):
            notes.append("stats_scope=winning_type_subset")
        conflicts: list[int] = []
        if inferred == "mixed":
            for cells, line in zip(table["rows"], table["lines"], strict=True):
                raw = cells[index]
                if raw != "" and self._classify(raw) != best:
                    conflicts.append(line)
                    if len(conflicts) >= self.max_conflict_lines:
                        break
        return {
            "index": index,
            "name": table["names"][index],
            "inferred_type": inferred,
            "winning_type": best,
            "type_ratio": ratio,
            "type_counts": scan["counts"],
            "non_null": scan["non_null"],
            "nulls": scan["nulls"],
            "distinct": len(scan["freq"]),
            "distinct_capped": scan["freq_capped"],
            "notes": notes,
            "stats": stats,
            "conflict_lines": conflicts,
        }

    def _numeric_stats(self, values: list[int | float]) -> dict[str, Any]:
        all_int = all(isinstance(value, int) for value in values)
        result: dict[str, Any] = {"count": len(values), "kind": "integer" if all_int else "float"}
        notes: list[str] = []
        ordered = sorted(values)
        try:
            result["min"] = ordered[0]
            result["max"] = ordered[-1]
            result["sum"] = sum(ordered) if all_int else statistics.fsum([float(value) for value in ordered])
            result["mean"] = statistics.mean(ordered)
            result["median"] = statistics.median(ordered)
            if len(ordered) >= 2:
                cuts = statistics.quantiles(ordered, n=100, method="inclusive")
                result["p50"], result["p90"] = cuts[49], cuts[89]
            else:
                result["p50"] = result["p90"] = ordered[0]
            result["stdev_population"] = statistics.pstdev(ordered)
            result["stdev_sample"] = statistics.stdev(ordered) if len(ordered) >= 2 else None
            result["histogram"] = self._histogram(ordered)
        except (statistics.StatisticsError, OverflowError, ValueError) as exc:
            notes.append(f"unrepresentable_stat:{type(exc).__name__}")
        result["notes"] = notes
        return result

    def _histogram(self, ordered: list[int | float]) -> dict[str, Any]:
        bins = self.histogram_bins
        low, high = ordered[0], ordered[-1]
        counts = [0] * bins
        width = (high - low) / bins
        if width > 0:
            for value in ordered:
                slot = int((value - low) / width)
                counts[min(max(slot, 0), bins - 1)] += 1
        else:
            counts[0] = len(ordered)
        return {"bins": bins, "lower": low, "upper": high, "counts": counts}

    def _datetime_stats(self, parsed: list[tuple[datetime, str]]) -> dict[str, Any]:
        if not parsed:
            return {"format_guesses": [], "format": None, "min": None, "max": None}
        format_counts: dict[str, int] = {}
        for _, key in parsed:
            format_counts[key] = format_counts.get(key, 0) + 1
        guesses = [
            {"format": key, "count": count}
            for key, count in sorted(format_counts.items(), key=lambda item: (-item[1], self._format_order(item[0])))
        ]
        naive = [dt for dt, _ in parsed if dt.tzinfo is None]
        # Mixed aware/naive values cannot be ordered against each other; the
        # naive subset defines min/max in that case (documented fallback).
        pool = naive if (naive and len(naive) != len(parsed)) else [dt for dt, _ in parsed]
        low, high = min(pool), max(pool)
        return {"format_guesses": guesses, "format": guesses[0]["format"], "min": low.isoformat(), "max": high.isoformat()}

    def _format_order(self, key: str) -> int:
        for position, (_, name) in enumerate(self._DATETIME_FORMATS):
            if name == key:
                return position
        return len(self._DATETIME_FORMATS)

    def _text_stats(self, lengths: list[int], freq: dict[str, int], capped: bool) -> dict[str, Any]:
        stats: dict[str, Any] = {"min_len": min(lengths), "max_len": max(lengths), "avg_len": statistics.mean(lengths)}
        if capped:
            stats["top_values"] = None
        else:
            ranked = sorted(freq.items(), key=lambda item: (-item[1], item[0]))[: self.max_top_values]
            stats["top_values"] = [{"value": value, "count": count} for value, count in ranked]
        return stats

    def _display(self, raw: str) -> str:
        if len(raw) <= self.max_value_chars:
            return raw
        return raw[: self.max_value_chars] + "…[truncated]"

    # ------------------------------------------------------------------
    # modes

    def _profile(self, table: dict[str, Any], dialect: dict[str, str]) -> dict[str, Any]:
        columns = [self._analyze_column(table, index) for index in range(table["width"])]
        warnings: list[dict[str, Any]] = list(table["ragged"])
        truncated = len(table["ragged"]) > self.max_warnings
        if truncated:
            warnings = warnings[: self.max_warnings]
        for entry in columns:
            if entry["inferred_type"] != "mixed":
                continue
            if len(warnings) >= self.max_warnings:
                truncated = True
                break
            warnings.append(
                {
                    "kind": "type_conflict",
                    "column": entry["name"],
                    "winning_type": entry["winning_type"],
                    "sample_lines": entry["conflict_lines"],
                }
            )
        return {
            "status": "success",
            "mode": "profile",
            "dialect": dialect,
            "header": table["header"],
            "row_count": len(table["rows"]),
            "col_count": table["width"],
            "columns": [{key: value for key, value in column.items() if key != "conflict_lines"} for column in columns],
            "warnings": warnings,
            "warnings_truncated": truncated,
        }

    @staticmethod
    def _locate_column(table: dict[str, Any], column: Any, column_index: Any) -> int:
        if column is None and column_index is None:
            raise ValueError("column (name) or column_index is required in column_detail mode")
        index = None
        if column is not None:
            if not isinstance(column, str) or not column:
                raise ValueError("column must be a non-empty string")
            if column not in table["names"]:
                raise ValueError(f"column not found: {column} (available: {table['names']})")
            index = table["names"].index(column)
        if column_index is not None:
            if isinstance(column_index, bool) or not isinstance(column_index, int):
                raise TypeError("column_index must be an integer")
            if not 0 <= column_index < table["width"]:
                raise ValueError(f"column_index out of range (0..{table['width'] - 1})")
            if index is not None and column_index != index:
                raise ValueError("column and column_index disagree")
            index = column_index
        return index

    def _column_detail(self, table: dict[str, Any], column: Any, column_index: Any, dialect: dict[str, str]) -> dict[str, Any]:
        index = self._locate_column(table, column, column_index)
        summary = self._analyze_column(table, index)
        winning = summary["winning_type"]
        previews: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        failed_total = 0
        for cells, line in zip(table["rows"], table["lines"], strict=True):
            raw = cells[index]
            if raw == "":
                continue
            kind = self._classify(raw)
            if kind == winning or winning is None:
                # winning_type is null for pure-text and empty columns: every
                # cell trivially matches, so nothing is a type failure.
                if len(previews) < self.max_preview_values:
                    previews.append({"line": line, "value": self._display(raw), "parsed": self._parse_preview(raw, kind)})
            else:
                failed_total += 1
                if len(failed) < self.max_failed_cells:
                    failed.append({"line": line, "value": self._display(raw), "classified_as": kind})
        frequency = None
        if not summary["distinct_capped"]:
            freq: dict[str, int] = {}
            for cells in table["rows"]:
                raw = cells[index]
                if raw != "":
                    shown = self._display(raw)
                    freq[shown] = freq.get(shown, 0) + 1
            frequency = [
                {"value": value, "count": count}
                for value, count in sorted(freq.items(), key=lambda item: (-item[1], item[0]))[: self.max_top_values]
            ]
        return {
            "status": "success",
            "mode": "column_detail",
            "dialect": dialect,
            "column": {key: value for key, value in summary.items() if key != "conflict_lines"},
            "row_count": len(table["rows"]),
            "value_frequency": frequency,
            "parsed_previews": previews,
            "failed_cells": failed,
            "failed_cells_truncated": failed_total > len(failed),
        }

    @classmethod
    def _parse_preview(cls, raw: str, kind: str) -> int | float | str | bool | None:
        if kind == "integer":
            return int(raw)
        if kind == "float":
            return float(raw)
        if kind == "boolean":
            return raw in ("true", "True", "TRUE")
        if kind == "datetime":
            return cls._parse_datetime(raw)[0].isoformat()
        if kind == "uuid":
            return raw
        return None

    def _compare(self, text_a: str, text_b: str, dialect: dict[str, str], header: bool) -> dict[str, Any]:
        left = self._parse(text_a, dialect, header)
        right = self._parse(text_b, dialect, header)
        columns_a = [self._analyze_column(left, index) for index in range(left["width"])]
        columns_b = [self._analyze_column(right, index) for index in range(right["width"])]
        names_a = [column["name"] for column in columns_a]
        names_b = [column["name"] for column in columns_b]
        set_a, set_b = set(names_a), set(names_b)
        removed = [name for name in names_a if name not in set_b]
        added_by_index = {index: name for index, name in enumerate(names_b) if name not in set_a}
        rename_guesses = [
            {"from": name, "to": added_by_index[position], "index": position}
            for name in removed
            for position in [names_a.index(name)]
            if position in added_by_index
        ]
        guessed = {guess["from"] for guess in rename_guesses}
        by_name_a = {column["name"]: column for column in columns_a}
        by_name_b = {column["name"]: column for column in columns_b}
        type_changes = []
        numeric_drift = []
        for name in names_b:
            if name not in by_name_a or name in guessed:
                continue
            column_a, column_b = by_name_a[name], by_name_b[name]
            if column_a["inferred_type"] != column_b["inferred_type"]:
                type_changes.append({"column": name, "from": column_a["inferred_type"], "to": column_b["inferred_type"]})
                continue
            if column_a["inferred_type"] not in ("integer", "float") or not column_a["stats"] or not column_b["stats"]:
                continue
            mean_a, mean_b = column_a["stats"].get("mean"), column_b["stats"].get("mean")
            if mean_a is None or mean_b is None:
                continue
            shift = mean_b - mean_a
            ratio = abs(shift) / max(abs(mean_a), 1e-12)
            numeric_drift.append(
                {
                    "column": name,
                    "mean_a": mean_a,
                    "mean_b": mean_b,
                    "mean_shift": shift,
                    "mean_shift_ratio": ratio,
                    "drift": ratio > self.mean_drift_threshold,
                    "min_a": column_a["stats"].get("min"),
                    "max_a": column_a["stats"].get("max"),
                    "median_a": column_a["stats"].get("median"),
                    "stdev_population_a": column_a["stats"].get("stdev_population"),
                    "min_b": column_b["stats"].get("min"),
                    "max_b": column_b["stats"].get("max"),
                    "median_b": column_b["stats"].get("median"),
                    "stdev_population_b": column_b["stats"].get("stdev_population"),
                }
            )
        return {
            "status": "success",
            "mode": "compare",
            "dialect": dialect,
            "row_count": {"a": len(left["rows"]), "b": len(right["rows"]), "delta": len(right["rows"]) - len(left["rows"])},
            "column_count": {"a": left["width"], "b": right["width"], "delta": right["width"] - left["width"]},
            "columns_removed": removed,
            "columns_added": [name for name in names_b if name not in set_a],
            "rename_guesses": rename_guesses,
            "type_changes": type_changes,
            "numeric_drift": numeric_drift,
            "drift_threshold": self.mean_drift_threshold,
        }

    def _sample(self, table: dict[str, Any], n: Any, sample_mode: Any, seed: Any) -> dict[str, Any]:
        if n is None:
            raise ValueError("n is required in sample mode")
        if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= self.max_sample_rows:
            raise ValueError(f"n must be an integer between 1 and {self.max_sample_rows}")
        if not isinstance(sample_mode, str):
            raise TypeError("sample_mode must be a string")
        selection = sample_mode.strip().lower()
        if selection not in self._SAMPLE_MODES:
            raise ValueError("sample_mode must be first, last, or random")
        if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a non-negative integer")
        total = len(table["rows"])
        count = min(n, total)
        if selection == "first":
            indices = list(range(count))
        elif selection == "last":
            indices = list(range(total - count, total))
        else:
            # Seeded deterministic sampling; not a cryptographic use.
            indices = sorted(random.Random(seed).sample(range(total), count))  # noqa: S311
        rows = [{"index": position, "line": table["lines"][position], "cells": table["rows"][position]} for position in indices]
        result: dict[str, Any] = {
            "status": "success",
            "mode": "sample",
            "selection": selection,
            "n_requested": n,
            "n_returned": len(rows),
            "row_count": total,
            "header": table["names"],
            "rows": rows,
        }
        if selection == "random":
            result["seed"] = seed
        return result
