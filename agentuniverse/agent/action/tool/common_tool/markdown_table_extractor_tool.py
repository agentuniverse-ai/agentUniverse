#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Markdown table extractor tool backed only on the Python standard library.

The tool parses GitHub-Flavored Markdown tables out of arbitrary Markdown text
and returns them as structured data (header + rows), with helpers to render the
result as CSV or JSON. Zero third-party dependencies.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import csv
import io
import json
import re
from typing import Any, Dict, List, Optional

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER

# A table is a header row, a separator row (---|:--|--:), then >=0 data rows.
# We match conservatively: each row must contain at least one pipe.
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
SEPARATOR = re.compile(r"^\s*\|?[\s:|-]*:?-+[\s:|-]*\|?\s*$")
# A separator cell must contain at least one dash; only ':', '-', '|', space allowed.
SEPARATOR_CELL = re.compile(r"^:?-{2,}:?$")

MAX_TEXT_CHARS = 2_000_000
MAX_TABLES = 1_000
MAX_ROWS = 100_000
MAX_COLUMNS = 1_000


class MarkdownTableExtractorTool(Tool):
    """Extract Markdown tables and convert them to structured data.

    Modes:

    * ``extract``       - return all tables as ``{header, rows}`` objects.
    * ``extract_first`` - return only the first table (or an error if none).
    * ``to_csv``        - render all tables as a single CSV string.
    * ``to_json``       - render all tables as a JSON string (list of objects).
    """

    description: str = (
        "Extract Markdown tables into structured data and convert them to "
        "CSV or JSON. Pure-Python regex parsing, zero dependencies."
    )

    def execute(
        self,
        text: str,
        mode: str = "extract",
        table_index: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run the requested operation and return a structured result."""
        try:
            normalized = self._validate_text(text)
            operation = self._mode(mode)
            tables = self._extract_all(normalized)
            if operation == "extract":
                return self._format_extract(tables)
            if operation == "extract_first":
                return self._format_first(tables)
            if operation == "to_csv":
                return self._format_csv(tables, table_index)
            return self._format_json(tables, table_index)
        except (TypeError, ValueError) as exc:
            LOGGER.error(f"MarkdownTableExtractorTool validation error: {exc}")
            return self._error("validation_error", str(exc))
        except Exception as exc:
            LOGGER.error(f"MarkdownTableExtractorTool operation failed: {exc}")
            return self._error("operation_error", f"Table extraction failed: {exc}")

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _error(kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    def _validate_text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if len(value) > MAX_TEXT_CHARS:
            raise ValueError(f"text exceeds MAX_TEXT_CHARS ({MAX_TEXT_CHARS})")
        return value

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"extract", "extract_first", "to_csv", "to_json"}:
            raise ValueError(
                "mode must be extract, extract_first, to_csv, or to_json"
            )
        return mode

    def _resolve_index(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("table_index must be an integer")
        if value < 0:
            raise ValueError("table_index must be >= 0")
        return value

    # --------------------------------------------------------------- parsing
    def _extract_all(self, text: str) -> List[Dict[str, Any]]:
        lines = text.splitlines()
        tables: List[Dict[str, Any]] = []
        index = 0
        while index < len(lines):
            # Find the next candidate header row.
            if not self._is_table_row(lines[index]):
                index += 1
                continue
            header_index = index
            if header_index + 1 >= len(lines):
                index += 1
                continue
            separator_line = lines[header_index + 1]
            if not self._is_separator(separator_line):
                index += 1
                continue
            header_cells = self._split_row(lines[header_index])
            rows: List[List[str]] = []
            cursor = header_index + 2
            while cursor < len(lines) and self._is_table_row(lines[cursor]):
                rows.append(self._split_row(lines[cursor]))
                cursor += 1
            if len(tables) >= MAX_TABLES:
                raise ValueError(f"text contains more than MAX_TABLES ({MAX_TABLES})")
            if len(rows) > MAX_ROWS:
                raise ValueError(f"a table exceeds MAX_ROWS ({MAX_ROWS})")
            tables.append(
                {
                    "header": header_cells,
                    "rows": rows,
                    "row_count": len(rows),
                    "column_count": len(header_cells),
                    "start_line": header_index + 1,
                }
            )
            index = cursor
        return tables

    @staticmethod
    def _is_table_row(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        # A table row is any non-empty line containing an unescaped pipe.
        # GFM permits rows with or without surrounding pipes.
        return "|" in re.sub(r"\\\|", "", stripped)

    def _is_separator(self, line: str) -> bool:
        if not self._is_table_row(line) and "|" not in line:
            # Allow separator rows that omit leading/trailing pipes.
            stripped = line.strip()
            if not stripped or not SEPARATOR.match(stripped):
                return False
        cells = self._split_row(line)
        if not cells:
            return False
        return all(bool(SEPARATOR_CELL.match(cell.strip())) for cell in cells)

    @staticmethod
    def _split_row(line: str) -> List[str]:
        stripped = line.strip()
        # Strip a single leading and trailing pipe.
        if stripped.startswith("|"):
            stripped = stripped[1:]
        if stripped.endswith("|"):
            stripped = stripped[:-1]
        # Split on unescaped pipes.
        parts = re.split(r"(?<!\\)\|", stripped)
        return [part.strip().replace("\\|", "|") for part in parts]

    # --------------------------------------------------------------- formatting
    @staticmethod
    def _format_extract(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": "extract",
            "table_count": len(tables),
            "tables": tables,
        }

    @staticmethod
    def _format_first(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not tables:
            return {
                "status": "success",
                "mode": "extract_first",
                "table_count": 0,
                "table": None,
            }
        first = tables[0]
        return {
            "status": "success",
            "mode": "extract_first",
            "table_count": len(tables),
            "table": first,
        }

    def _format_csv(
        self, tables: List[Dict[str, Any]], table_index: Optional[int]
    ) -> Dict[str, Any]:
        index = self._resolve_index(table_index)
        if not tables:
            return {
                "status": "success",
                "mode": "to_csv",
                "table_count": 0,
                "csv": "",
            }
        selected = tables
        if index is not None:
            if index >= len(tables):
                raise ValueError(
                    f"table_index {index} is out of range (0-{len(tables) - 1})"
                )
            selected = [tables[index]]
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        for position, table in enumerate(selected):
            if position > 0:
                writer.writerow([])
            writer.writerow(table["header"])
            writer.writerows(table["rows"])
        return {
            "status": "success",
            "mode": "to_csv",
            "table_count": len(tables),
            "table_index": index,
            "csv": buffer.getvalue(),
        }

    def _format_json(
        self, tables: List[Dict[str, Any]], table_index: Optional[int]
    ) -> Dict[str, Any]:
        index = self._resolve_index(table_index)
        if not tables:
            return {
                "status": "success",
                "mode": "to_json",
                "table_count": 0,
                "json": "[]",
            }
        selected = tables
        if index is not None:
            if index >= len(tables):
                raise ValueError(
                    f"table_index {index} is out of range (0-{len(tables) - 1})"
                )
            selected = [tables[index]]

        def to_objects(table: Dict[str, Any]) -> List[Dict[str, str]]:
            header = table["header"]
            objects: List[Dict[str, str]] = []
            for row in table["rows"]:
                obj: Dict[str, str] = {}
                for cell_index, value in enumerate(row):
                    key = header[cell_index] if cell_index < len(header) else f"column_{cell_index}"
                    obj[key] = value
                objects.append(obj)
            return objects

        payload = [obj for table in selected for obj in to_objects(table)]
        return {
            "status": "success",
            "mode": "to_json",
            "table_count": len(tables),
            "table_index": index,
            "row_count": len(payload),
            "json": json.dumps(payload, ensure_ascii=False, indent=2),
        }
