#!/usr/bin/env python3

# @Time    : 2026/10/6
# @Author  : agentuniverse
# @FileName: csv_query_tool.py

# Validation failures are converted into structured tool responses at the
# public execute boundary, so bespoke exception subclasses would add no
# useful signal.
# ruff: noqa: TRY003, TRY004

"""
CSV query tool.

Executes SQL-like queries - ``SELECT`` projection, ``WHERE`` filtering,
``ORDER BY`` sorting, ``LIMIT`` truncation and simple aggregation
(``COUNT`` / ``SUM`` / ``AVG`` / ``MIN`` / ``MAX``) - directly against CSV
*text*, without loading the data into a database.

The tool is intentionally zero-dependency: it only uses the Python standard
library :mod:`csv` module for parsing. That makes it a convenient building
block for agents that receive tabular data as CSV strings (from files,
spreadsheets, HTTP responses or other tools) and need to slice it without
round-tripping through pandas or a database engine.

Query model
-----------

``execute(csv_text, select, where, order_by, limit)`` pipelines the data
through four stages:

1. **Parse**  - the first record of the CSV text becomes the header, every
   following record becomes a row. Quoted fields, embedded commas and
   embedded newlines are handled by :mod:`csv`.
2. **Filter** - ``where`` keeps the rows matching every condition. Supported
   operators: ``=``, ``!=`` (and ``<>``), ``>``, ``<``, ``>=``, ``<=``,
   ``LIKE``, ``NOT LIKE``, ``IN`` and ``NOT IN``. Multiple conditions may be
   combined with ``AND`` (a list of condition strings is ANDed as well).
3. **Project / aggregate** - ``select`` picks columns (``*`` keeps them all)
   or computes aggregations such as ``COUNT(*)`` or ``AVG(salary)``.
4. **Sort & truncate** - ``order_by`` sorts by one or more columns with
   ``ASC``/``DESC`` direction, ``limit`` caps the number of returned rows.

Comparisons are type-aware: when both the cell and the literal parse as
numbers the comparison is numeric, otherwise it is lexicographic. All values
are returned exactly as they appear in the CSV (as strings).

Every failure (malformed CSV, unknown column, unsupported operator, limit
overflow, ...) is reported as a structured ``{"error": ...}`` dictionary
instead of an exception, so an agent can feed the message straight back into
its reasoning loop.
"""

from __future__ import annotations

import csv
import io
import re
from collections.abc import Sequence
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

# Aggregation function names accepted inside a select expression.
_AGGREGATE_PATTERN = re.compile(
    r"^(COUNT|SUM|AVG|MIN|MAX)\s*\(\s*(\*|[^),\s]+)\s*\)$", re.IGNORECASE
)

# Single condition grammar: <column> <operator> <value>.
# The value is either a quoted string or a bare token; the ``IN`` family is
# handled separately because it takes a parenthesised value list.
_CONDITION_PATTERN = re.compile(
    r"^\s*(?P<column>[^<>=!\s]+)\s*"
    r"(?P<operator>>=|<=|!=|<>|=|>|<|LIKE|NOT\s+LIKE|IN|NOT\s+IN)"
    r"(?P<rest>.*)$",
    re.IGNORECASE,
)

# Splits a where string into AND-combined conditions (case-insensitive).
_AND_SPLIT_PATTERN = re.compile(r"\s+AND\s+", re.IGNORECASE)

# LIKE pattern translation: % -> any run, _ -> a single character.
_LIKE_TRANSLATION = str.maketrans({"%": "\x00", "_": "\x01"})

_WILDCARD_REGEX = re.compile("[\x00\x01]")


def _try_float(value: str) -> float | None:
    """Return ``value`` parsed as a float, or ``None`` when not numeric.

    A bare ``str.isdigit`` check is not enough: scientific notation,
    negatives and decimal points must be accepted, while strings such as
    ``""`` or ``"1.2.3"`` must be rejected.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _compare(cell: str, literal: str) -> int | None:
    """Compare a CSV cell against a literal, type-aware.

    Returns a negative number / zero / a positive number when the cell is
    smaller / equal / greater than the literal, or ``None`` when the two
    operands cannot be compared meaningfully (numeric vs non-numeric).
    """
    cell_num, literal_num = _try_float(cell), _try_float(literal)
    if cell_num is not None and literal_num is not None:
        return (cell_num > literal_num) - (cell_num < literal_num)
    if cell_num is None and literal_num is None:
        return (cell > literal) - (cell < literal)
    return None


def _like_match(cell: str, pattern: str) -> bool:
    """SQL ``LIKE`` matching with ``%`` / ``_`` wildcards.

    Matching is case-insensitive so agents do not have to guess the casing
    used by the data source.
    """
    regex_body = _WILDCARD_REGEX.sub(
        lambda match: ".*" if match.group() == "\x00" else ".",
        re.escape(pattern.translate(_LIKE_TRANSLATION)),
    )
    return re.fullmatch(regex_body, cell, flags=re.IGNORECASE) is not None


def _sort_key(cell: str) -> tuple[int, Any]:
    """Build a sort key that orders numbers before other strings.

    Mixing raw floats and strings inside one ``sort`` would raise a
    ``TypeError``; ranking the two families (0 = numeric, 1 = textual)
    keeps the sort total and deterministic.
    """
    number = _try_float(cell)
    if number is not None:
        return (0, number, "")
    return (1, 0.0, cell)


class CSVQueryTool(Tool):
    """Run SQL-like queries over CSV text without a database.

    Attributes:
        max_input_chars: Upper bound on the size of the accepted CSV text,
            guarding the agent context against accidentally huge payloads.
        max_rows: Upper bound on the number of data rows parsed from the
            CSV text.
    """

    name: str = "csv_query_tool"
    description: str = (
        "Execute SQL-like queries over CSV text without a database. Supports "
        "column projection (select), filtering (where with =, !=, >, <, >=, "
        "<=, LIKE, IN), sorting (order_by ASC/DESC), LIMIT and simple "
        "aggregation (COUNT, SUM, AVG, MIN, MAX). Returns a structured dict "
        "with columns, rows and row_count. Zero dependencies."
    )

    max_input_chars: int = 1_000_000
    max_rows: int = 100_000

    def execute(
        self,
        csv_text: str,
        select: str | Sequence[str] | None = None,
        where: str | Sequence[str] | None = None,
        order_by: str | Sequence[str] | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> dict:
        """Query the CSV text.

        Args:
            csv_text: The raw CSV content. The first record is the header.
            select: Columns to return (``"*"`` / ``None`` keeps all) either
                as a comma separated string or a list; may instead contain
                aggregate expressions such as ``"COUNT(*)"`` or
                ``"AVG(salary)"``.
            where: Filter conditions, either one string (multiple
                conditions may be joined with ``AND``) or a list of
                condition strings (implicit AND). Supported operators:
                ``=``, ``!=``, ``<>``, ``>``, ``<``, ``>=``, ``<=``,
                ``LIKE``, ``NOT LIKE``, ``IN``, ``NOT IN``.
            order_by: Sort specification, e.g. ``"age DESC, name ASC"``.
            limit: Maximum number of rows to return.

        Returns:
            ``{"columns": [...], "rows": [[...], ...], "row_count": n}`` on
            success, or ``{"error": "<message>"}`` when the input is
            invalid.
        """
        try:
            columns, rows = self._parse_csv(csv_text)
            rows = self._apply_where(rows, columns, where)

            select_items = self._normalize_select(select)
            if any(_AGGREGATE_PATTERN.match(item) for item in select_items):
                result_columns, result_rows = self._aggregate(
                    rows, columns, select_items
                )
            else:
                result_columns, result_rows = self._project(
                    rows, columns, select_items
                )
                result_rows = self._apply_order_by(
                    result_rows, result_columns, order_by
                )
                result_rows = self._apply_limit(result_rows, limit)

            return {
                "columns": result_columns,
                "rows": result_rows,
                "row_count": len(result_rows),
            }
        except (ValueError, TypeError, csv.Error) as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_csv(self, csv_text: str) -> tuple[list[str], list[list[str]]]:
        """Parse CSV text into a header list and a list of rows.

        Raises:
            ValueError: If the text is not a str, is empty, has no usable
                header, contains duplicate column names or a row longer
                than the header, or exceeds the configured budgets.
        """
        if not isinstance(csv_text, str):
            raise ValueError("csv_text must be a string containing CSV data.")
        if not csv_text.strip():
            raise ValueError("csv_text is empty; expected a header row and data rows.")
        if len(csv_text) > self.max_input_chars:
            raise ValueError(
                f"csv_text exceeds max_input_chars ({len(csv_text)} > {self.max_input_chars})."
            )

        records = [
            record
            for record in csv.reader(io.StringIO(csv_text.lstrip("\ufeff")))
            if record  # skip blank lines
        ]
        if not records:
            raise ValueError("csv_text contains no parseable records.")

        columns = self._validate_header(records[0])
        rows = self._parse_rows(records, columns)
        return columns, rows

    @staticmethod
    def _validate_header(record: list[str]) -> list[str]:
        """Validate the header record and return the trimmed column names."""
        columns = [name.strip() for name in record]
        if not any(columns):
            raise ValueError("the CSV header row is empty.")
        duplicates = sorted(
            {name for name in columns if columns.count(name) > 1}
        )
        if duplicates:
            raise ValueError(f"duplicate column name(s) in CSV header: {', '.join(duplicates)}.")
        return columns

    def _parse_rows(
        self, records: list[list[str]], columns: list[str]
    ) -> list[list[str]]:
        """Turn the data records into rows aligned with the header.

        Short rows are padded with empty cells; a row longer than the
        header is rejected because its extra values cannot be addressed by
        any column name.
        """
        rows: list[list[str]] = []
        for line_number, record in enumerate(records[1:], start=2):
            if len(record) > len(columns):
                raise ValueError(
                    f"row {line_number} has {len(record)} fields but the header has "
                    f"{len(columns)} columns."
                )
            if len(record) < len(columns):
                record = record + [""] * (len(columns) - len(record))
            rows.append(record)
            if len(rows) > self.max_rows:
                raise ValueError(
                    f"CSV data exceeds max_rows ({self.max_rows})."
                )
        return rows

    @staticmethod
    def _resolve_column(columns: list[str], name: str, context: str) -> str:
        """Resolve a (possibly differently cased) column name to the header.

        Exact matches win; otherwise a unique case-insensitive match is
        accepted, which keeps agents from failing over ``Name`` vs ``name``.
        """
        candidate = name.strip()
        if candidate in columns:
            return candidate
        lowered = [column for column in columns if column.lower() == candidate.lower()]
        if len(lowered) == 1:
            return lowered[0]
        raise ValueError(f"unknown column '{candidate}' in {context}.")

    # ------------------------------------------------------------------
    # WHERE
    # ------------------------------------------------------------------

    def _apply_where(
        self,
        rows: list[list[str]],
        columns: list[str],
        where: str | Sequence[str] | None,
    ) -> list[list[str]]:
        """Keep only the rows matching every AND-combined condition."""
        if where is None:
            return rows
        if isinstance(where, str):
            condition_strings: list[str] = [where] if where.strip() else []
        elif isinstance(where, Sequence):
            condition_strings = [item for item in where if str(item).strip()]
        else:
            raise ValueError("where must be a string or a list of condition strings.")

        conditions: list[tuple[str, str, Any]] = []
        for raw in condition_strings:
            for chunk in _AND_SPLIT_PATTERN.split(str(raw)):
                if chunk.strip():
                    conditions.append(self._parse_condition(columns, chunk))

        if not conditions:
            return rows
        return [
            row for row in rows
            if all(self._row_matches(row, columns, condition) for condition in conditions)
        ]

    def _parse_condition(
        self, columns: list[str], text: str
    ) -> tuple[str, str, Any]:
        """Parse ``column <operator> value`` into a comparable triple.

        Returns:
            ``(column, operator, expected)`` where ``expected`` is the
            literal for simple operators or the value list for ``IN``.
        """
        match = _CONDITION_PATTERN.match(text)
        if not match:
            raise ValueError(
                f"cannot parse where condition '{text.strip()}'; expected "
                "'<column> <op> <value>' with op in =, !=, <>, >, <, >=, <=, "
                "LIKE, NOT LIKE, IN, NOT IN."
            )
        column = self._resolve_column(columns, match.group("column"), "where condition")
        operator = re.sub(r"\s+", " ", match.group("operator").upper())
        rest = match.group("rest").strip()

        if operator in ("IN", "NOT IN"):
            return column, operator, self._parse_in_values(rest, text)
        if operator not in ("LIKE", "NOT LIKE") and not rest:
            raise ValueError(f"missing value in where condition '{text.strip()}'.")
        return column, operator, self._strip_quotes(rest)

    @staticmethod
    def _parse_in_values(rest: str, original: str) -> list[str]:
        """Parse the parenthesised value list of an ``IN`` condition."""
        if not (rest.startswith("(") and rest.endswith(")")):
            raise ValueError(
                f"IN condition '{original.strip()}' expects a value list like "
                "(a, b, c)."
            )
        inner = rest[1:-1].strip()
        if not inner:
            return []
        parsed = list(csv.reader(io.StringIO(inner), skipinitialspace=True))
        if len(parsed) != 1:
            raise ValueError(f"cannot parse IN value list in '{original.strip()}'.")
        return [CSVQueryTool._strip_quotes(value) for value in parsed[0]]

    @staticmethod
    def _strip_quotes(value: str) -> str:
        """Remove one pair of matching surrounding quotes, if present."""
        trimmed = value.strip()
        if len(trimmed) >= 2 and trimmed[0] == trimmed[-1] and trimmed[0] in ("'", '"'):
            return trimmed[1:-1]
        return trimmed

    def _row_matches(
        self, row: list[str], columns: list[str], condition: tuple[str, str, Any]
    ) -> bool:
        """Evaluate one parsed condition against one row."""
        column, operator, expected = condition
        cell = row[columns.index(column)]

        if operator in ("IN", "NOT IN"):
            values = [str(item) for item in expected]
            matched = any(
                _compare(cell, value) == 0 for value in values
            ) or cell in values
            return matched if operator == "IN" else not matched

        if operator in ("LIKE", "NOT LIKE"):
            matched = _like_match(cell, str(expected))
            return matched if operator == "LIKE" else not matched

        literal = str(expected)
        if operator in ("=", "!="):
            equal = _compare(cell, literal) == 0 or cell == literal
            if operator == "=":
                return equal
            return not equal
        # Ordered comparison; incomparable operands never match.
        outcome = _compare(cell, literal)
        if outcome is None:
            return False
        if operator == ">":
            return outcome > 0
        if operator == "<":
            return outcome < 0
        if operator == ">=":
            return outcome >= 0
        return outcome <= 0

    # ------------------------------------------------------------------
    # SELECT / aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_select(
        select: str | Sequence[str] | None
    ) -> list[str]:
        """Normalise the select argument into a list of expressions."""
        if select is None:
            return ["*"]
        if isinstance(select, str):
            items = [item.strip() for item in select.split(",")]
        elif isinstance(select, Sequence):
            items = [str(item).strip() for item in select]
        else:
            raise ValueError("select must be a string or a list of column names.")
        return [item for item in items if item] or ["*"]

    def _project(
        self,
        rows: list[list[str]],
        columns: list[str],
        select_items: list[str],
    ) -> tuple[list[str], list[list[str]]]:
        """Keep only the selected columns, preserving their order."""
        resolved: list[str] = []
        for item in select_items:
            if item == "*":
                for column in columns:
                    if column not in resolved:
                        resolved.append(column)
            else:
                resolved.append(self._resolve_column(columns, item, "select"))
        indexes = [columns.index(column) for column in resolved]
        return resolved, [[row[index] for index in indexes] for row in rows]

    def _aggregate(
        self,
        rows: list[list[str]],
        columns: list[str],
        select_items: list[str],
    ) -> tuple[list[str], list[list[Any]]]:
        """Compute a single aggregate result row for the selected expressions."""
        plain = [
            item for item in select_items
            if item != "*" and not _AGGREGATE_PATTERN.match(item)
        ]
        if plain:
            raise ValueError(
                "aggregates cannot be mixed with plain columns; got: "
                f"{', '.join(plain)}."
            )
        expressions = ["COUNT(*)" if item == "*" else item for item in select_items]

        header: list[str] = []
        computed: list[Any] = []
        for expression in expressions:
            match = _AGGREGATE_PATTERN.match(expression)
            if not match:
                raise ValueError(f"cannot parse aggregate expression '{expression}'.")
            function, target = match.group(1).upper(), match.group(2)
            header.append(f"{function}({target})")
            computed.append(
                self._compute_aggregate(rows, columns, function, target)
            )
        return header, [computed]

    @staticmethod
    def _compute_aggregate(
        rows: list[list[str]],
        columns: list[str],
        function: str,
        target: str,
    ) -> Any:
        """Compute one aggregate over the (already filtered) rows."""
        if function == "COUNT" and target == "*":
            return len(rows)

        column = CSVQueryTool._resolve_aggregate_column(columns, target)
        values = [row[columns.index(column)] for row in rows]
        non_empty = [value for value in values if value.strip()]

        if function == "COUNT":
            return len(non_empty)
        numbers = [number for number in (_try_float(value) for value in non_empty) if number is not None]
        if not numbers:
            return None
        if function == "SUM":
            return round(sum(numbers), 10)
        if function == "AVG":
            return round(sum(numbers) / len(numbers), 10)
        if function == "MIN":
            return min(numbers)
        return max(numbers)

    @staticmethod
    def _resolve_aggregate_column(columns: list[str], target: str) -> str:
        if target == "*":
            raise ValueError("'*' is only supported by COUNT(*).")
        return CSVQueryTool._resolve_column(columns, target, "aggregate expression")

    # ------------------------------------------------------------------
    # ORDER BY / LIMIT
    # ------------------------------------------------------------------

    def _apply_order_by(
        self,
        rows: list[list[str]],
        columns: list[str],
        order_by: str | Sequence[str] | None,
    ) -> list[list[str]]:
        """Sort rows by one or more columns with per-key ASC/DESC direction."""
        if order_by is None:
            return rows
        if isinstance(order_by, str):
            parts = [part for part in order_by.split(",") if part.strip()]
        elif isinstance(order_by, Sequence):
            parts = list(order_by)
        else:
            raise ValueError("order_by must be a string or a list of sort keys.")

        keys: list[tuple[int, bool]] = []
        for part in parts:
            tokens = str(part).split()
            if not tokens:
                continue
            if len(tokens) > 2:
                raise ValueError(f"cannot parse order_by key '{part.strip()}'.")
            direction = tokens[1].upper() if len(tokens) == 2 else "ASC"
            if direction not in ("ASC", "DESC"):
                raise ValueError(
                    f"invalid order_by direction '{tokens[1]}'; expected ASC or DESC."
                )
            column = self._resolve_column(columns, tokens[0], "order_by")
            keys.append((columns.index(column), direction == "DESC"))

        if not keys:
            return rows

        def sort_key(row: list[str]) -> tuple:
            return tuple(
                _SortInverter(_sort_key(row[index])) if descending else _sort_key(row[index])
                for index, descending in keys
            )

        return sorted(rows, key=sort_key)

    @staticmethod
    def _apply_limit(rows: list[list[str]], limit: int | None) -> list[list[str]]:
        """Cap the number of returned rows."""
        if limit is None:
            return rows
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit must be a non-negative integer.")
        if limit < 0:
            raise ValueError("limit must be a non-negative integer.")
        return rows[:limit]


class _SortInverter:
    """Reverse-comparison wrapper enabling DESC ordering in ``sort`` keys.

    Tuples compare element-wise, so wrapping the DESC members in this
    helper inverts their comparison while keeping multi-key sorts working.
    """

    __slots__ = ("_value",)

    def __init__(self, value: Any) -> None:
        self._value = value

    def __lt__(self, other: _SortInverter) -> bool:
        return other._value < self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _SortInverter) and other._value == self._value
