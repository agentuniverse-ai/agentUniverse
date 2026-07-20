#!/usr/bin/env python3
"""Bounded CSV, TSV, and JSONL data workflows."""

# Validation errors are returned as structured tool responses.
# ruff: noqa: TRY003, TRY004

import csv
import json
import math
import os
import tempfile
from typing import Any, ClassVar, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool


class TabularDataTool(Tool):
    """Create, read, profile, and transform CSV/TSV/JSONL datasets."""

    base_dir: str = "."
    max_read_bytes: int = 50 * 1024 * 1024
    max_write_bytes: int = 50 * 1024 * 1024
    max_rows: int = 100_000
    max_columns: int = 200
    max_cell_chars: int = 100_000
    max_output_chars: int = 500_000
    max_distinct_values: int = 10_000
    max_filter_values: int = 1_000

    _EXTENSIONS: ClassVar[set[str]] = {".csv", ".tsv", ".jsonl"}
    _OPERATORS: ClassVar[set[str]] = {
        "eq",
        "ne",
        "gt",
        "gte",
        "lt",
        "lte",
        "contains",
        "in",
        "is_null",
    }

    def execute(
        self,
        mode: str,
        file_path: str,
        rows: list[dict[str, Any]] | None = None,
        output_path: str | None = None,
        overwrite: bool = False,
        filters: list[dict[str, Any]] | None = None,
        select_columns: list[str] | None = None,
        sort_by: str | None = None,
        descending: bool = False,
        deduplicate_by: list[str] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Run ``create``, ``read``, ``profile``, or ``transform``."""
        try:
            self._validate_config()
            operation = self._mode(mode)
            path = self._data_path(file_path, "file_path")
            if operation == "create":
                return self._create(path, rows, overwrite)
            source_rows, columns = self._load(path)
            if operation == "read":
                return self._read(path, source_rows, columns, limit)
            if operation == "profile":
                return self._profile(path, source_rows, columns)
            return self._transform(
                path,
                source_rows,
                columns,
                output_path,
                overwrite,
                filters,
                select_columns,
                sort_by,
                descending,
                deduplicate_by,
                limit,
            )
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except Exception as exc:
            return self._error(file_path, "operation_error", f"Tabular data operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "file_path": path}

    def _validate_config(self) -> None:
        for name in (
            "max_read_bytes",
            "max_write_bytes",
            "max_rows",
            "max_columns",
            "max_cell_chars",
            "max_output_chars",
            "max_distinct_values",
            "max_filter_values",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("mode must be a non-empty string")
        operation = value.strip().lower()
        if operation not in {"create", "read", "profile", "transform"}:
            raise ValueError("mode must be create, read, profile, or transform")
        return operation

    def _data_path(self, value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        extension = os.path.splitext(value)[1].lower()
        if extension not in self._EXTENSIONS:
            raise ValueError(f"{field} must have a .csv, .tsv, or .jsonl extension")
        return cast(str, resolve_safe_path(value, self.base_dir))

    def _load(self, path: str) -> tuple[list[dict[str, Any]], list[str]]:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"file_path exceeds max_read_bytes ({self.max_read_bytes})")
        extension = os.path.splitext(path)[1].lower()
        if extension == ".jsonl":
            rows, columns = self._load_jsonl(path)
        else:
            rows, columns = self._load_delimited(path, "\t" if extension == ".tsv" else ",")
        self._validate_shape(rows, columns)
        return rows, columns

    def _load_jsonl(self, path: str) -> tuple[list[dict[str, Any]], list[str]]:
        rows = []
        columns = []
        seen = set()
        with open(path, encoding="utf-8-sig") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                if len(rows) >= self.max_rows:
                    raise ValueError(f"dataset exceeds max_rows ({self.max_rows})")
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
                if not isinstance(row, dict):
                    raise ValueError(f"JSONL line {line_number} must contain an object")
                normalized = self._normalize_row(row, f"line {line_number}")
                for column in normalized:
                    if column not in seen:
                        seen.add(column)
                        columns.append(column)
                rows.append(normalized)
        return rows, columns

    def _load_delimited(self, path: str, delimiter: str) -> tuple[list[dict[str, Any]], list[str]]:
        with open(path, encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter=delimiter)
            if reader.fieldnames is None:
                raise ValueError("delimited file must contain a header row")
            columns = [str(column or "").strip() for column in reader.fieldnames]
            self._validate_columns(columns)
            rows = []
            for row_number, raw in enumerate(reader, start=2):
                if len(rows) >= self.max_rows:
                    raise ValueError(f"dataset exceeds max_rows ({self.max_rows})")
                if None in raw:
                    raise ValueError(f"row {row_number} contains more cells than the header")
                rows.append(self._normalize_row(raw, f"row {row_number}"))
        return rows, columns

    def _validate_shape(self, rows: list[dict[str, Any]], columns: list[str]) -> None:
        self._validate_columns(columns)
        if len(rows) > self.max_rows:
            raise ValueError(f"dataset exceeds max_rows ({self.max_rows})")

    def _validate_columns(self, columns: list[str]) -> None:
        if not columns:
            raise ValueError("dataset must contain at least one column")
        if len(columns) > self.max_columns:
            raise ValueError(f"dataset exceeds max_columns ({self.max_columns})")
        if any(not column for column in columns):
            raise ValueError("column names must be non-empty strings")
        if len(set(columns)) != len(columns):
            raise ValueError("column names must be unique")

    def _normalize_row(self, raw: dict[Any, Any], context: str) -> dict[str, Any]:
        if len(raw) > self.max_columns:
            raise ValueError(f"{context} exceeds max_columns ({self.max_columns})")
        output = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{context} has an invalid column name")
            key = key.strip()
            if value is None or isinstance(value, (str, int, float, bool)):
                if isinstance(value, float) and not math.isfinite(value):
                    raise ValueError(f"{context}.{key} must be finite")
                normalized = value
            else:
                raise ValueError(f"{context}.{key} must be a scalar value")
            if len(str(normalized or "")) > self.max_cell_chars:
                raise ValueError(f"{context}.{key} exceeds max_cell_chars ({self.max_cell_chars})")
            output[key] = normalized
        return output

    def _create(self, path: str, rows: Any, overwrite: Any) -> dict[str, Any]:
        self._check_overwrite(path, overwrite)
        if not isinstance(rows, list) or not rows:
            raise ValueError("rows must be a non-empty list")
        normalized = []
        columns = []
        seen = set()
        if len(rows) > self.max_rows:
            raise ValueError(f"rows exceeds max_rows ({self.max_rows})")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"rows[{index}] must be an object")
            item = self._normalize_row(row, f"rows[{index}]")
            for column in item:
                if column not in seen:
                    seen.add(column)
                    columns.append(column)
            normalized.append(item)
        self._validate_shape(normalized, columns)
        self._write(path, normalized, columns)
        return {
            "status": "success",
            "mode": "create",
            "file_path": path,
            "row_count": len(normalized),
            "columns": columns,
            "file_size": os.path.getsize(path),
            "overwritten": overwrite,
        }

    def _read(self, path: str, rows: list[dict[str, Any]], columns: list[str], limit: Any) -> dict[str, Any]:
        limit = self._limit(limit, len(rows))
        emitted = []
        remaining = self.max_output_chars
        truncated = limit < len(rows)
        for row in rows[:limit]:
            output = {}
            for column in columns:
                value = row.get(column)
                text = str(value or "")
                if len(text) > remaining:
                    output[column] = text[: max(0, remaining - 1)] + ("…" if remaining else "")
                    remaining = 0
                    truncated = True
                else:
                    output[column] = value
                    remaining -= len(text)
            emitted.append(output)
            if remaining == 0:
                break
        return {
            "status": "success",
            "mode": "read",
            "file_path": path,
            "row_count": len(rows),
            "returned_row_count": len(emitted),
            "columns": columns,
            "rows": emitted,
            "truncated": truncated,
        }

    def _profile(self, path: str, rows: list[dict[str, Any]], columns: list[str]) -> dict[str, Any]:
        result = {
            "status": "success",
            "mode": "profile",
            "file_path": path,
            "file_size": os.path.getsize(path),
            "row_count": len(rows),
            "column_count": len(columns),
            "returned_column_count": 0,
            "columns": [],
            "truncated": False,
        }
        for column in columns:
            values = [row.get(column) for row in rows]
            non_null = [value for value in values if value not in (None, "")]
            numeric = [self._number(value) for value in non_null]
            numeric_values = [value for value in numeric if value is not None]
            frequencies: dict[str, int] = {}
            distinct_overflow = False
            for value in non_null:
                key = str(value)
                if key in frequencies:
                    frequencies[key] += 1
                elif len(frequencies) < self.max_distinct_values:
                    frequencies[key] = 1
                else:
                    # Do not retain unbounded attacker-controlled cardinality.
                    # Counts for retained values remain exact, but the complete
                    # distinct count and global top-N are no longer knowable.
                    distinct_overflow = True
            top_values = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))[:5]
            profile = {
                "name": column,
                "null_count": len(values) - len(non_null),
                "non_null_count": len(non_null),
                "distinct_count": None if distinct_overflow else len(frequencies),
                "distinct_count_lower_bound": len(frequencies) + int(distinct_overflow),
                "distinct_count_truncated": distinct_overflow,
                "top_values": [{"value": value, "count": count} for value, count in top_values],
                "top_values_approximate": distinct_overflow,
                "numeric_count": len(numeric_values),
            }
            if numeric_values:
                profile["numeric"] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": sum(numeric_values) / len(numeric_values),
                }
            result["columns"].append(profile)
            result["returned_column_count"] = len(result["columns"])
            if self._json_size(result) <= self.max_output_chars:
                continue
            while profile["top_values"] and self._json_size(result) > self.max_output_chars:
                profile["top_values"].pop()
                profile["top_values_approximate"] = True
            if self._json_size(result) <= self.max_output_chars:
                result["truncated"] = True
                continue
            result["columns"].pop()
            result["returned_column_count"] = len(result["columns"])
            result["truncated"] = True
            break
        return result

    @staticmethod
    def _json_size(value: Any) -> int:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")))

    def _transform(
        self,
        path: str,
        rows: list[dict[str, Any]],
        columns: list[str],
        output_path: Any,
        overwrite: Any,
        filters: Any,
        select_columns: Any,
        sort_by: Any,
        descending: Any,
        deduplicate_by: Any,
        limit: Any,
    ) -> dict[str, Any]:
        if output_path is None:
            raise ValueError("output_path is required for transform mode")
        destination = self._data_path(output_path, "output_path")
        if destination == path:
            raise ValueError("output_path must differ from file_path")
        self._check_overwrite(destination, overwrite)
        if not isinstance(descending, bool):
            raise ValueError("descending must be a boolean")
        predicates = self._filters(filters, columns)
        transformed = [row for row in rows if all(self._matches(row, predicate) for predicate in predicates)]
        if deduplicate_by is not None:
            keys = self._column_list(deduplicate_by, columns, "deduplicate_by")
            seen = set()
            unique_rows = []
            for row in transformed:
                marker = tuple(self._hashable(row.get(key)) for key in keys)
                if marker not in seen:
                    seen.add(marker)
                    unique_rows.append(row)
            transformed = unique_rows
        if sort_by is not None:
            if not isinstance(sort_by, str) or sort_by not in columns:
                raise ValueError("sort_by must name an existing column")
            transformed.sort(key=lambda row: self._sort_key(row.get(sort_by)), reverse=descending)
        limit = self._limit(limit, len(transformed))
        transformed = transformed[:limit]
        output_columns = (
            self._column_list(select_columns, columns, "select_columns") if select_columns is not None else columns
        )
        projected = [{column: row.get(column) for column in output_columns} for row in transformed]
        self._write(destination, projected, output_columns)
        return {
            "status": "success",
            "mode": "transform",
            "file_path": path,
            "output_path": destination,
            "input_row_count": len(rows),
            "output_row_count": len(projected),
            "columns": output_columns,
            "file_size": os.path.getsize(destination),
            "overwritten": overwrite,
        }

    def _filters(self, value: Any, columns: list[str]) -> list[dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list) or len(value) > self.max_columns:
            raise ValueError("filters must be a bounded list")
        output = []
        for index, item in enumerate(value):
            if not isinstance(item, dict) or set(item) - {"column", "operator", "value"}:
                raise ValueError(f"filters[{index}] has invalid fields")
            column, operator = item.get("column"), item.get("operator")
            if column not in columns:
                raise ValueError(f"filters[{index}].column must name an existing column")
            if not isinstance(operator, str) or operator not in self._OPERATORS:
                raise ValueError(f"filters[{index}].operator is invalid")
            if operator == "in":
                item = self._prepare_in_filter(item, index)
            if operator == "is_null" and not isinstance(item.get("value"), bool):
                raise ValueError(f"filters[{index}].value must be a boolean for the is_null operator")
            output.append(item)
        return output

    def _prepare_in_filter(self, item: dict[str, Any], index: int) -> dict[str, Any]:
        expected = item.get("value")
        if not isinstance(expected, list):
            raise ValueError(f"filters[{index}].value must be a list for the in operator")
        if len(expected) > self.max_filter_values:
            raise ValueError(f"filters[{index}].value exceeds max_filter_values ({self.max_filter_values})")
        if any(value is not None and not isinstance(value, (str, int, float, bool)) for value in expected):
            raise ValueError(f"filters[{index}].value must contain scalar values")
        return {
            **item,
            "_exact_values": set(expected),
            "_string_values": {str(candidate) for candidate in expected},
        }

    @staticmethod
    def _matches(row: dict[str, Any], predicate: dict[str, Any]) -> bool:
        actual, expected, operator = row.get(predicate["column"]), predicate.get("value"), predicate["operator"]
        if operator == "is_null":
            return (actual in (None, "")) is bool(expected)
        if operator == "contains":
            return str(expected) in str(actual or "")
        if operator == "in":
            return actual in predicate["_exact_values"] or str(actual) in predicate["_string_values"]
        if operator in {"eq", "ne"}:
            equal = actual == expected or str(actual) == str(expected)
            return equal if operator == "eq" else not equal
        left, right = TabularDataTool._number(actual), TabularDataTool._number(expected)
        if left is None or right is None:
            left, right = str(actual or ""), str(expected or "")
        return {"gt": left > right, "gte": left >= right, "lt": left < right, "lte": left <= right}[operator]

    @staticmethod
    def _number(value: Any) -> float | None:
        if isinstance(value, bool) or value in (None, ""):
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _sort_key(value: Any) -> tuple[int, Any]:
        if value in (None, ""):
            return 2, ""
        number = TabularDataTool._number(value)
        return (0, number) if number is not None else (1, str(value))

    @staticmethod
    def _hashable(value: Any) -> tuple[str, str]:
        return type(value).__name__, str(value)

    @staticmethod
    def _column_list(value: Any, columns: list[str], field: str) -> list[str]:
        if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
            raise ValueError(f"{field} must be a non-empty list of column names")
        if len(set(value)) != len(value) or any(item not in columns for item in value):
            raise ValueError(f"{field} must contain unique existing columns")
        return value

    def _limit(self, value: Any, default: int) -> int:
        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("limit must be a positive integer")
        return min(value, self.max_rows)

    @staticmethod
    def _check_overwrite(path: str, overwrite: Any) -> None:
        if not isinstance(overwrite, bool):
            raise ValueError("overwrite must be a boolean")
        if os.path.exists(path) and not overwrite:
            raise ValueError(f"file already exists: {path}; set overwrite=true to replace it")

    def _write(self, path: str, rows: list[dict[str, Any]], columns: list[str]) -> None:
        extension = os.path.splitext(path)[1].lower()
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                prefix=".tabular-",
                suffix=extension,
                dir=directory,
                delete=False,
            ) as stream:
                temporary_path = stream.name
                if extension == ".jsonl":
                    for row in rows:
                        stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                else:
                    writer = csv.DictWriter(
                        stream,
                        fieldnames=columns,
                        delimiter="\t" if extension == ".tsv" else ",",
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    writer.writerows(rows)
                stream.flush()
                os.fsync(stream.fileno())
            size = os.path.getsize(temporary_path)
            if size > self.max_write_bytes:
                raise ValueError(f"generated dataset exceeds max_write_bytes ({self.max_write_bytes})")
            os.replace(temporary_path, path)
            temporary_path = None
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
