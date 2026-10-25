#!/usr/bin/env python3
"""Bounded CSV read, write, append, and inspection tool."""

import codecs
import contextlib
import csv
import io
import os
import tempfile
from collections.abc import Iterable
from typing import Any, cast

from agentuniverse.agent.action.tool.common_tool.file_path_utils import resolve_safe_path
from agentuniverse.agent.action.tool.tool import Tool

# Public execute() converts validation exceptions to structured tool responses.
# ruff: noqa: TRY003


class CSVTool(Tool):
    """Read, write, append to, and inspect bounded CSV files.

    The tool never trusts the caller with an unrestricted path. Every path is
    resolved below ``base_dir``, and reads and writes are bounded by explicit
    row, column, field, character, and byte budgets. Mutating operations write
    to a temporary file in the destination directory and replace the target
    only after all validation has succeeded, so a rejected request cannot
    corrupt an existing file.
    """

    base_dir: str = "."
    max_read_bytes: int = 50 * 1024 * 1024
    max_write_bytes: int = 50 * 1024 * 1024
    max_rows: int = 100_000
    max_columns: int = 1_000
    max_field_chars: int = 100_000
    max_total_chars: int = 10_000_000

    def execute(
        self,
        mode: str,
        file_path: str,
        rows: list[list[Any]] | None = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        """Run one CSV operation and return a structured result.

        Args:
            mode: One of ``read``, ``write``, ``append``, or ``info``.
            file_path: CSV path resolved below ``base_dir``.
            rows: Rectangular rows for ``write`` and ``append``.
            delimiter: Single-character CSV delimiter.
            encoding: Text encoding used for reading and writing.
            has_header: Whether the first record is a header row.
            overwrite: Whether ``write`` may replace an existing file.
        """
        try:
            self._validate_config()
            operation = self._mode(mode)
            path = self._csv_path(file_path)
            separator = self._delimiter(delimiter)
            text_encoding = self._encoding(encoding)
            header = self._boolean(has_header, "has_header")
            replace = self._boolean(overwrite, "overwrite")
            if operation == "read":
                return self._read(path, separator, text_encoding, header)
            if operation == "write":
                return self._write(path, rows, separator, text_encoding, header, replace)
            if operation == "append":
                return self._append(path, rows, separator, text_encoding, header)
            return self._info(path, separator, text_encoding, header)
        except (TypeError, ValueError) as exc:
            return self._error(file_path, "validation_error", str(exc))
        except csv.Error as exc:
            return self._error(file_path, "operation_error", f"CSV operation failed: {exc}")
        except Exception as exc:
            return self._error(file_path, "operation_error", f"CSV operation failed: {exc}")

    @staticmethod
    def _error(path: Any, kind: str, message: str) -> dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message, "file_path": path}

    @staticmethod
    def _remove_temporary(path: str | None) -> None:
        """Remove a temporary file without a racy exists()/unlink() window."""
        if path is None:
            return
        with contextlib.suppress(FileNotFoundError):
            os.unlink(path)

    def _validate_config(self) -> None:
        # Reject booleans explicitly: bool is an int subclass, and a flag such as
        # ``max_rows=True`` would otherwise create a confusing one-row budget.
        for name in (
            "max_read_bytes",
            "max_write_bytes",
            "max_rows",
            "max_columns",
            "max_field_chars",
            "max_total_chars",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.base_dir, str) or not self.base_dir:
            raise ValueError("base_dir must be a non-empty string")

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"read", "write", "append", "info"}:
            raise ValueError("mode must be read, write, append, or info")
        return mode

    def _csv_path(self, value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("file_path must be a non-empty string")
        if os.path.splitext(value)[1].lower() != ".csv":
            raise ValueError("file_path must have a .csv extension")
        return cast(str, resolve_safe_path(value, self.base_dir))

    @staticmethod
    def _delimiter(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("delimiter must be a string")
        if len(value) != 1:
            raise ValueError("delimiter must be exactly one character")
        # Python's csv module rejects newlines and NUL, while a quote delimiter
        # makes quoting ambiguous. Reject them here so every caller gets the
        # same validation error instead of a backend-specific exception.
        if value in {"\r", "\n", "\x00", '"'}:
            raise ValueError("delimiter must not be a newline, NUL, or quote character")
        return value

    @staticmethod
    def _encoding(value: Any) -> str:
        if not isinstance(value, str) or not value:
            raise ValueError("encoding must be a non-empty string")
        try:
            codec = codecs.lookup(value)
        except LookupError as exc:
            raise ValueError(f"unsupported encoding: {value}") from exc
        # codecs.lookup also resolves byte-to-byte codecs such as base64. Text
        # mode cannot use those, so probe the codec with a plain string.
        if not getattr(codec, "_is_text_encoding", True):
            raise ValueError(f"encoding must be a text encoding: {value}")
        try:
            "".encode(value)
        except (LookupError, TypeError, UnicodeError) as exc:
            raise ValueError(f"encoding must be a text encoding: {value}") from exc
        return value

    @staticmethod
    def _boolean(value: Any, field: str) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"{field} must be a boolean")
        return value

    def _check_readable(self, path: str) -> None:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        if os.path.getsize(path) > self.max_read_bytes:
            raise ValueError(f"file exceeds max_read_bytes ({self.max_read_bytes})")

    def _validate_rows(self, rows: Any) -> list[list[str]]:
        """Validate and normalize caller-supplied rows before writing them.

        Rows must be rectangular and contain only scalar values. This keeps the
        warm path deterministic and means a bad cell is rejected before any
        temporary file is created.
        """
        if not isinstance(rows, list) or not rows:
            raise ValueError("rows must be a non-empty list of rows")
        if len(rows) > self.max_rows:
            raise ValueError(f"rows exceed max_rows ({self.max_rows})")
        width: int | None = None
        total_chars = 0
        prepared: list[list[str]] = []
        for row_index, row in enumerate(rows):
            width = self._validate_row_shape(row, row_index, width)
            prepared_row: list[str] = []
            for field_index, value in enumerate(row):
                text = self._scalar_text(value, row_index, field_index)
                if len(text) > self.max_field_chars:
                    raise ValueError(
                        f"rows[{row_index}][{field_index}] exceeds max_field_chars " f"({self.max_field_chars})"
                    )
                total_chars += len(text)
                prepared_row.append(text)
            prepared.append(prepared_row)
        if total_chars > self.max_total_chars:
            raise ValueError(f"rows exceed max_total_chars ({self.max_total_chars})")
        return prepared

    def _validate_row_shape(self, row: Any, row_index: int, width: int | None) -> int:
        """Validate one row's container shape and return the common width."""
        if not isinstance(row, list) or not row:
            raise ValueError(f"rows[{row_index}] must be a non-empty list")
        if len(row) > self.max_columns:
            raise ValueError(f"rows[{row_index}] exceeds max_columns ({self.max_columns})")
        if width is None:
            return len(row)
        if len(row) != width:
            raise ValueError("rows must all have the same number of columns")
        return width

    @staticmethod
    def _scalar_text(value: Any, row_index: int, field_index: int) -> str:
        """Normalize one scalar cell to the text csv.writer should emit."""
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            # csv.writer accepts arbitrary objects, but accepting only scalars
            # keeps the YAML schema and runtime behaviour in sync and prevents
            # accidental repr() serialization.
            return str(value)
        raise ValueError(f"rows[{row_index}][{field_index}] must be a scalar value")

    def _scan(
        self,
        path: str,
        delimiter: str,
        encoding: str,
        has_header: bool,
        collect_rows: bool,
    ) -> dict[str, Any]:
        """Stream a CSV file once, enforcing all read-side budgets."""
        self._check_readable(path)
        with open(path, encoding=encoding, newline="") as stream:
            return self._scan_lines(stream, delimiter, has_header, collect_rows)

    def _read_text(self, path: str, encoding: str) -> str:
        """Read an existing CSV file as text while enforcing max_read_bytes."""
        self._check_readable(path)
        with open(path, encoding=encoding, newline="") as stream:
            return stream.read()

    def _scan_lines(
        self,
        lines: Iterable[str],
        delimiter: str,
        has_header: bool,
        collect_rows: bool,
    ) -> dict[str, Any]:
        """Parse records from a line iterable while enforcing read budgets.

        Records are counted as they are parsed instead of materialized so the
        ``info`` path stays bounded even for large files. ``first_width`` and
        ``rectangular`` let append reject files whose records do not share one
        consistent shape.
        """
        header: list[str] | None = None
        rows: list[list[str]] = []
        physical_rows = 0
        column_count = 0
        first_width: int | None = None
        rectangular = True
        total_chars = 0

        for row in csv.reader(lines, delimiter=delimiter):
            physical_rows += 1
            if physical_rows > self.max_rows:
                raise ValueError(f"file exceeds max_rows ({self.max_rows})")
            if first_width is None:
                first_width = len(row)
            elif len(row) != first_width:
                rectangular = False
            column_count, total_chars = self._check_record(row, column_count, total_chars)
            if physical_rows == 1 and has_header:
                header = row
                continue
            if collect_rows:
                rows.append(row)

        data_rows = physical_rows - (1 if has_header and physical_rows else 0)
        return {
            "header": header,
            "rows": rows,
            "physical_rows": physical_rows,
            "row_count": data_rows,
            "column_count": column_count,
            "total_chars": total_chars,
            "first_width": first_width,
            "rectangular": rectangular,
        }

    def _check_record(self, row: list[str], column_count: int, total_chars: int) -> tuple[int, int]:
        """Enforce column/field/character budgets for one parsed record."""
        if len(row) > self.max_columns:
            raise ValueError(f"file exceeds max_columns ({self.max_columns})")
        row_chars = 0
        for field_index, value in enumerate(row):
            if len(value) > self.max_field_chars:
                raise ValueError(f"field {field_index} exceeds max_field_chars ({self.max_field_chars})")
            row_chars += len(value)
        total_chars += row_chars
        if total_chars > self.max_total_chars:
            raise ValueError(f"file exceeds max_total_chars ({self.max_total_chars})")
        return max(column_count, len(row)), total_chars

    def _read(self, path: str, delimiter: str, encoding: str, has_header: bool) -> dict[str, Any]:
        scanned = self._scan(path, delimiter, encoding, has_header, collect_rows=True)
        result = {
            "status": "success",
            "mode": "read",
            "file_path": path,
            "rows": scanned["rows"],
            "row_count": scanned["row_count"],
            "column_count": scanned["column_count"],
            "delimiter": delimiter,
            "encoding": encoding,
            "has_header": has_header,
        }
        if has_header:
            result["header"] = scanned["header"]
        return result

    def _info(self, path: str, delimiter: str, encoding: str, has_header: bool) -> dict[str, Any]:
        scanned = self._scan(path, delimiter, encoding, has_header, collect_rows=False)
        return {
            "status": "success",
            "mode": "info",
            "file_path": path,
            "file_size": os.path.getsize(path),
            "row_count": scanned["row_count"],
            "column_count": scanned["column_count"],
            "delimiter": delimiter,
            "encoding": encoding,
            "has_header": has_header,
        }

    def _write(
        self,
        path: str,
        rows: Any,
        delimiter: str,
        encoding: str,
        has_header: bool,
        overwrite: bool,
    ) -> dict[str, Any]:
        if os.path.exists(path) and not overwrite:
            raise ValueError(f"file exists: {path}; set overwrite=true")
        prepared = self._validate_rows(rows)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                prefix=".csv-",
                suffix=".csv",
                dir=os.path.dirname(path),
                encoding=encoding,
                newline="",
                delete=False,
            ) as output:
                temporary = output.name
                csv.writer(output, delimiter=delimiter).writerows(prepared)
            if os.path.getsize(temporary) > self.max_write_bytes:
                raise ValueError(f"generated CSV exceeds max_write_bytes ({self.max_write_bytes})")
            os.replace(temporary, path)
            temporary = None
        finally:
            self._remove_temporary(temporary)
        return {
            "status": "success",
            "mode": "write",
            "file_path": path,
            "rows_written": len(prepared),
            "row_count": len(prepared) - (1 if has_header else 0),
            "column_count": len(prepared[0]),
            "delimiter": delimiter,
            "encoding": encoding,
            "has_header": has_header,
            "file_size": os.path.getsize(path),
        }

    def _append(
        self,
        path: str,
        rows: Any,
        delimiter: str,
        encoding: str,
        has_header: bool,
    ) -> dict[str, Any]:
        if not os.path.isfile(path):
            raise ValueError(f"file_path does not exist: {path}")
        prepared = self._validate_rows(rows)
        # Decode the whole existing file with the requested encoding before
        # touching the destination. Rewriting this text below guarantees that
        # the result is uniformly encoded instead of mixing byte sequences from
        # two encodings in one file.
        existing_text = self._read_text(path, encoding)
        existing = self._scan_lines(io.StringIO(existing_text), delimiter, has_header, collect_rows=False)
        if existing["physical_rows"]:
            if not existing["rectangular"] or existing["first_width"] is None:
                raise ValueError("existing CSV records do not all have the same number of columns")
            if any(len(row) != existing["first_width"] for row in prepared):
                raise ValueError("appended rows must match the existing column count")
        if existing["physical_rows"] + len(prepared) > self.max_rows:
            raise ValueError(f"resulting file would exceed max_rows ({self.max_rows})")
        added_chars = sum(len(value) for row in prepared for value in row)
        if existing["total_chars"] + added_chars > self.max_total_chars:
            raise ValueError(f"resulting file would exceed max_total_chars ({self.max_total_chars})")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                prefix=".csv-",
                suffix=".csv",
                dir=os.path.dirname(path),
                encoding=encoding,
                newline="",
                delete=False,
            ) as output:
                temporary = output.name
                output.write(existing_text)
                if existing_text and not existing_text.endswith(("\n", "\r")):
                    # Terminate a missing final line before appending, otherwise
                    # the first new field would be concatenated to the last one.
                    output.write("\n")
                csv.writer(output, delimiter=delimiter).writerows(prepared)
            if os.path.getsize(temporary) > self.max_write_bytes:
                raise ValueError(f"resulting CSV exceeds max_write_bytes ({self.max_write_bytes})")
            os.replace(temporary, path)
            temporary = None
        finally:
            self._remove_temporary(temporary)
        # Appending to an empty file with has_header=True means the first
        # appended record becomes the header rather than a data row.
        appended_data_rows = len(prepared) - (1 if has_header and existing["physical_rows"] == 0 else 0)
        row_count = existing["row_count"] + appended_data_rows
        return {
            "status": "success",
            "mode": "append",
            "file_path": path,
            "rows_appended": len(prepared),
            "row_count": row_count,
            "column_count": max(existing["column_count"], len(prepared[0])),
            "delimiter": delimiter,
            "encoding": encoding,
            "has_header": has_header,
            "file_size": os.path.getsize(path),
        }
