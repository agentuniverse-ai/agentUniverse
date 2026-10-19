#!/usr/bin/env python3

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: csv_json_tool.py

"""CSV <-> JSON conversion tool built purely on the stdlib csv + json modules.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency tabular converter
agents can call to bridge raw CSV text and JSON record arrays — the
missing piece between the SQL-like CSV queries of CSVQueryTool and the
config-format conversions of JsonYamlTool.

The tool is a thin, strictly-validated facade over the standard library
``csv`` and ``json`` modules and supports two modes:

* ``to_json`` — parse CSV text into a JSON array of row objects. The
  first row is used as object keys by default (``has_header=True``);
  with ``has_header=False`` keys are generated as ``column_1`` ..
  ``column_n``. Type inference (``type_inference=True`` by default)
  coerces cells to int / float / bool / null: ``true`` / ``false``
  (case-insensitive) become booleans, an empty cell becomes ``null``,
  and canonical integer / decimal / scientific-notation literals become
  numbers. Locale-ambiguous strings are deliberately left untouched:
  values with an unnecessary leading zero (``007``, ``007.5``,
  ``000``) stay strings so codes and ZIP-like data are not corrupted,
  and ``NaN`` / ``Infinity`` spellings stay strings. With
  ``type_inference=False`` every value stays a string. Cells are
  matched as-is — surrounding whitespace is never trimmed.
* ``to_csv`` — serialize a JSON array of objects back to CSV text. The
  header is the union of all object keys in first-seen order; an
  explicit ``key_order`` list (or JSON-array string) pins the leading
  columns, and any remaining union keys are appended in first-seen
  order. Ragged rows fill missing cells with empty strings. ``None``
  becomes an empty cell, booleans become ``true`` / ``false``, numbers
  use their canonical string form, and nested dicts / lists are
  JSON-stringified (compact, non-ASCII kept verbatim). Quoting follows
  RFC 4180 via ``csv.writer`` with ``QUOTE_MINIMAL`` and ``\n`` line
  terminators.

The delimiter defaults to auto-sniffing among ``,`` ``;`` ``\\t`` ``|``
by counting candidate occurrences *outside double-quoted sections* and
preferring ``,`` on ties; an explicit ``delimiter`` option overrides
sniffing.

Round-trip guarantee: for rectangular, uniform CSV data (same fields
in every row, ``has_header=True``), ``to_csv(to_json(csv))`` reproduces
the original text — same headers, same cell values, same RFC 4180
quoting — except for cells whose numeric spelling is non-canonical
(e.g. ``1e5`` normalizes to ``100000.0``); the logical values always
round-trip. ``to_json(to_csv(records))`` reproduces the original array
of objects whenever ``type_inference`` matches how the values were
encoded.

Malformed parameters (wrong types, empty input text, unknown mode or
delimiter, non-boolean ``has_header`` / ``type_inference``, invalid or
unknown-key ``key_order``, oversized text / row / column counts) raise
a ``ValueError`` before any conversion, mirroring the other common
tools. Errors that depend on the *content being processed* — CSV that
the stdlib reader rejects, JSON text that does not parse, and JSON that
parses but is not an array of objects — are returned as a structured
``error`` payload so an agent can react without catching exceptions.
"""

# Validation errors carry contextual messages, mirroring sibling tools.
# ruff: noqa: TRY003

import csv
import io
import json
import math
import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Canonical integer literals: optional sign, ASCII digits only.
_INT_PATTERN = re.compile(r"\A[+-]?[0-9]+\Z")
# Canonical float literals: decimal or scientific notation, finite only.
_FLOAT_PATTERN = re.compile(r"\A[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
# Unnecessary leading zero ("007", "007.5", "000"): kept as a string.
_LEADING_ZERO = re.compile(r"\A[+-]?0[0-9]")

# Candidate delimiters for auto-sniffing, in tie-break priority order.
_DELIMITER_CANDIDATES: tuple = (",", ";", "\t", "|")


def _sniff_delimiter(text: str) -> str:
    """Count candidate delimiters outside double-quoted sections.

    A simple state machine walks the text toggling the in-quote state on
    every double quote (so doubled ``""`` escapes net out). The candidate
    with the highest outside-quote count wins; ties prefer the earlier
    candidate in ``_DELIMITER_CANDIDATES`` (comma first). A text with no
    outside-quote delimiter at all sniffs to comma.
    """
    counts = dict.fromkeys(_DELIMITER_CANDIDATES, 0)
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            continue
        if not in_quotes and char in counts:
            counts[char] += 1
    return max(
        _DELIMITER_CANDIDATES,
        key=lambda candidate: (counts[candidate], -_DELIMITER_CANDIDATES.index(candidate)),
    )


class CsvJsonTool(Tool):
    """CSV <-> JSON conversion tool built purely on the stdlib.

    Attributes:
        max_input_chars (int): Upper bound on the ``csv_text`` /
            ``json_text`` input length; longer inputs are rejected
            before any work.
        max_rows (int): Upper bound on the number of rows / records
            converted in one call.
        max_columns (int): Upper bound on the number of columns /
            keys converted in one call.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    name: str = "csv_json_tool"
    description: str = (
        "CSV <-> JSON conversion tool — pure Python stdlib csv + json, no "
        "network required. to_json mode parses CSV text into a JSON array "
        "of row objects (first row as headers by default, or generated "
        "column_1..column_n keys; optional int/float/bool/null type "
        "inference that keeps leading-zero strings like '007' untouched; "
        "delimiter auto-sniffed among , ; tab | or set explicitly). "
        "to_csv mode serializes a JSON array of objects back to CSV text "
        "(header from the union of keys in first-seen order or an explicit "
        "key_order, ragged rows fill missing cells, nested values "
        "JSON-stringified, RFC 4180 quoting)."
    )

    MODES: ClassVar[tuple] = ("to_json", "to_csv")

    max_input_chars: int = 100_000
    max_rows: int = 10_000
    max_columns: int = 1_000

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        csv_text: Any = None,
        json_text: Any = None,
        delimiter: Any = None,
        has_header: Any = None,
        type_inference: Any = None,
        key_order: Any = None,
    ) -> dict[str, Any]:
        """Run one CSV <-> JSON conversion.

        Args:
            mode (str): ``to_json`` (CSV text -> JSON records) or
                ``to_csv`` (JSON records -> CSV text).
            csv_text (str): The CSV text to parse. Required for the
                ``to_json`` mode; not used by ``to_csv``.
            json_text (str): The JSON text to serialize — must parse to
                an array of objects. Required for the ``to_csv`` mode;
                not used by ``to_json``.
            delimiter (str): Optional explicit delimiter, one of ``,``
                ``;`` ``\\t`` ``|``. When omitted, ``to_json`` sniffs the
                delimiter by counting candidates outside quoted
                sections (ties prefer ``,``) and ``to_csv`` writes ``,``.
            has_header (bool | str): ``to_json`` only — treat the first
                row as object keys (default ``true``); ``false`` keys
                rows ``column_1`` .. ``column_n``. Accepts booleans or
                ``"true"`` / ``"false"`` strings.
            type_inference (bool | str): ``to_json`` only — coerce cells
                to int / float / bool / null (default ``true``);
                ``false`` keeps every value a string. Leading-zero
                strings such as ``007`` are never coerced.
            key_order (list[str] | str): ``to_csv`` only — explicit
                leading header keys as a list (or a JSON-array string);
                remaining union keys are appended in first-seen order.

        Returns:
            Dict[str, Any]: The conversion result (always a ``result``
                string plus the call context) or a structured ``error``
                payload for content-level failures (unparseable CSV,
                invalid JSON, JSON that is not an array of objects).

        Raises:
            ValueError: If any parameter is malformed or oversized
                (before any conversion happens).
        """
        if mode not in self.MODES:
            self._invalid(f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})")
        if mode == "to_json":
            return self._run_to_json(csv_text, delimiter, has_header, type_inference)
        return self._run_to_csv(json_text, delimiter, key_order)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any conversion)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"csv_json_tool: {message}")

    @classmethod
    def _validate_text(cls, text: Any, label: str) -> str:
        """Validate the ``csv_text`` / ``json_text`` input."""
        if text is None or isinstance(text, bool) or not isinstance(text, str):
            cls._invalid(f"{label} must be a non-empty string (got {text!r})")
        if not text:
            cls._invalid(f"{label} must be a non-empty string (got '')")
        if len(text) > 100_000:
            cls._invalid(f"{label} exceeds the {100_000:,}-character limit (got {len(text):,} characters)")
        return text

    @classmethod
    def _validate_delimiter(cls, delimiter: Any) -> Any:
        """Validate the optional explicit ``delimiter``.

        ``None`` means auto (sniff for ``to_json``, comma for
        ``to_csv``); otherwise the delimiter must be exactly one of the
        supported candidates.
        """
        if delimiter is None:
            return None
        if isinstance(delimiter, bool) or not isinstance(delimiter, str):
            cls._invalid(
                "delimiter must be one of: "
                + " ".join(repr(c) for c in _DELIMITER_CANDIDATES)
                + f" or None (got {delimiter!r})"
            )
        if delimiter not in _DELIMITER_CANDIDATES:
            cls._invalid(
                "delimiter must be one of: "
                + " ".join(repr(c) for c in _DELIMITER_CANDIDATES)
                + f" or None (got {delimiter!r})"
            )
        return delimiter

    @classmethod
    def _validate_flag(cls, flag: Any, label: str, default: bool) -> bool:
        """Validate a boolean option (``has_header`` / ``type_inference``).

        Accepts ``None`` (use the default), a real boolean, or the
        case-insensitive strings ``"true"`` / ``"false"``.
        """
        if flag is None:
            return default
        if isinstance(flag, bool):
            return flag
        if isinstance(flag, str):
            lowered = flag.strip().lower()
            if lowered == "true":
                return True
            if lowered == "false":
                return False
        cls._invalid(f"{label} must be a boolean or 'true'/'false' (got {flag!r})")
        return default  # unreachable — _invalid always raises

    def _validate_key_order(self, key_order: Any, known_keys: set) -> list:
        """Validate the ``to_csv`` ``key_order`` option.

        Accepts a list / tuple of key strings or a JSON-array string of
        key strings, de-duplicates preserving first occurrences, and
        rejects keys that never appear in the records.
        """
        if isinstance(key_order, str):
            try:
                parsed = json.loads(key_order)
            except json.JSONDecodeError:
                self._invalid(
                    f"key_order must be a list of key strings or a JSON array string (got {key_order[:64]!r})"
                )
        elif isinstance(key_order, (list, tuple)):
            parsed = key_order
        else:
            self._invalid(f"key_order must be a list of key strings or a JSON array string (got {key_order!r})")
        if not all(isinstance(key, str) for key in parsed):
            self._invalid(
                "key_order entries must all be strings (got "
                f"{[key for key in parsed if not isinstance(key, str)][:3]!r})"
            )
        ordered: list = []
        for key in parsed:
            if key not in ordered:
                ordered.append(key)
        unknown = [key for key in ordered if key not in known_keys]
        if unknown:
            self._invalid(f"key_order contains keys that never appear in the records (got {unknown[:5]!r})")
        return ordered

    # ------------------------------------------------------------------ #
    # to_json mode
    # ------------------------------------------------------------------ #

    def _run_to_json(
        self,
        csv_text: Any,
        delimiter: Any,
        has_header: Any,
        type_inference: Any,
    ) -> dict[str, Any]:
        """Parse CSV text into a JSON array of row objects."""
        clean_text = self._validate_text(csv_text, "csv_text")
        clean_delimiter = self._validate_delimiter(delimiter)
        used_delimiter = clean_delimiter if clean_delimiter is not None else _sniff_delimiter(clean_text)
        clean_has_header = self._validate_flag(has_header, "has_header", True)
        clean_inference = self._validate_flag(type_inference, "type_inference", True)
        context: dict[str, Any] = {
            "mode": "to_json",
            "delimiter": used_delimiter,
            "has_header": clean_has_header,
            "type_inference": clean_inference,
        }
        try:
            rows = list(csv.reader(io.StringIO(clean_text), delimiter=used_delimiter))
        except csv.Error as exc:
            return self._error_result(
                context,
                error_type="csv_parse_error",
                message=(f"the stdlib csv reader rejected the input: {exc} (delimiter {used_delimiter!r})"),
            )
        # Blank lines parse as empty rows and are ignored.
        rows = [row for row in rows if row]
        if len(rows) > self.max_rows:
            self._invalid(f"input exceeds the {self.max_rows:,}-row limit (got {len(rows):,} rows)")
        width = max(len(row) for row in rows) if rows else 0
        if width > self.max_columns:
            self._invalid(f"input exceeds the {self.max_columns:,}-column limit (got {width:,} columns)")
        if not rows:
            return {**context, "row_count": 0, "result": "[]"}

        if clean_has_header:
            headers = self._normalize_headers(rows[0])
            data_rows = rows[1:]
        else:
            headers = None
            data_rows = rows

        records = [self._row_to_record(row, headers, clean_inference) for row in data_rows]
        result = json.dumps(records, ensure_ascii=False, indent=2)
        return {**context, "row_count": len(records), "result": result}

    @classmethod
    def _row_to_record(cls, row: list, headers: Any, infer: bool) -> dict:
        """Convert one parsed CSV row into a record object.

        With headers, cells map positionally to header keys: rows
        shorter than the header fill missing cells with empty strings
        (``null`` under inference) and longer rows append generated
        ``column_{n}`` keys. Without headers every value gets a
        generated ``column_{n}`` key.
        """
        if headers is None:
            record = {f"column_{index + 1}": value for index, value in enumerate(row)}
        else:
            record = {key: (row[index] if index < len(row) else "") for index, key in enumerate(headers)}
            for index in range(len(headers), len(row)):
                record[f"column_{index + 1}"] = row[index]
        if infer:
            record = {key: cls._infer_value(v) for key, v in record.items()}
        return record

    @staticmethod
    def _normalize_headers(header_row: list) -> list:
        """Turn a header row into unique, non-empty key strings.

        Empty header cells fall back to ``column_{n}`` positional keys;
        repeated headers are de-duplicated with ``_2`` / ``_3`` ...
        suffixes so no column of data is silently lost.
        """
        headers: list = []
        seen: set = set()
        for index, raw in enumerate(header_row):
            key = raw if raw else f"column_{index + 1}"
            if key in seen:
                suffix = 2
                while f"{key}_{suffix}" in seen:
                    suffix += 1
                key = f"{key}_{suffix}"
            seen.add(key)
            headers.append(key)
        return headers

    @classmethod
    def _infer_value(cls, raw: str) -> Any:
        """Coerce one CSV cell to a JSON scalar under type inference.

        ``true`` / ``false`` (case-insensitive) become booleans, an
        empty cell becomes ``null``, and canonical int / float literals
        become numbers. Values with an unnecessary leading zero
        (``007``), non-finite spellings (``NaN``, ``Infinity``), and
        anything with surrounding whitespace stay strings; cells are
        never trimmed.
        """
        if raw == "":
            return None
        lowered = raw.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if _INT_PATTERN.match(raw) and not _LEADING_ZERO.match(raw):
            return int(raw)
        if _FLOAT_PATTERN.match(raw) and not _LEADING_ZERO.match(raw):
            value = float(raw)
            if math.isfinite(value):
                return value
        return raw

    # ------------------------------------------------------------------ #
    # to_csv mode
    # ------------------------------------------------------------------ #

    def _run_to_csv(self, json_text: Any, delimiter: Any, key_order: Any) -> dict[str, Any]:
        """Serialize a JSON array of objects into CSV text."""
        clean_text = self._validate_text(json_text, "json_text")
        clean_delimiter = self._validate_delimiter(delimiter)
        used_delimiter = clean_delimiter if clean_delimiter is not None else ","
        context: dict[str, Any] = {
            "mode": "to_csv",
            "delimiter": used_delimiter,
        }
        data, error = self._load_records(clean_text)
        if error is not None:
            return self._error_result(context, error_type=error[0], message=error[1])
        if len(data) > self.max_rows:
            self._invalid(f"input exceeds the {self.max_rows:,}-record limit (got {len(data):,} records)")
        header = self._ordered_header(data, key_order)
        if len(header) > self.max_columns:
            self._invalid(f"input exceeds the {self.max_columns:,}-column limit (got {len(header):,} columns)")
        if not data:
            return {
                **context,
                "row_count": 0,
                "columns": [],
                "result": "",
            }
        buffer = io.StringIO()
        writer = csv.writer(
            buffer,
            delimiter=used_delimiter,
            lineterminator="\n",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writerow(header)
        for item in data:
            writer.writerow([self._to_cell(item.get(key)) for key in header])
        return {
            **context,
            "row_count": len(data),
            "columns": header,
            "result": buffer.getvalue(),
        }

    @staticmethod
    def _load_records(clean_text: str) -> tuple:
        """Parse ``json_text`` into a list of record objects.

        Returns ``(records, None)`` on success, or ``(None, error)``
        with a structured ``(type, message)`` error pair when the text
        does not parse (``invalid_json``) or parses to something other
        than an array of objects (``invalid_records``).
        """
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            return None, (
                "invalid_json",
                f"json_text is not valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}",
            )
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            first = type(data[0]).__name__ if isinstance(data, list) and data else "n/a"
            return None, (
                "invalid_records",
                "json_text must parse to a JSON array of objects "
                "(a list of {...} records); scalars, nested arrays "
                "and top-level objects are rejected "
                f"(got {type(data).__name__} of {first})",
            )
        return data, None

    def _ordered_header(self, data: list, key_order: Any) -> list:
        """Compute the ``to_csv`` header from the union of record keys.

        Keys are collected in first-seen order; an explicit
        ``key_order`` pins the leading columns and the remaining union
        keys are appended in first-seen order.
        """
        union_keys: list = []
        known: set = set()
        for item in data:
            for key in item:
                if key not in known:
                    known.add(key)
                    union_keys.append(key)
        if key_order is None:
            return union_keys
        ordered = self._validate_key_order(key_order, known)
        ordered_set = set(ordered)
        return ordered + [key for key in union_keys if key not in ordered_set]

    @staticmethod
    def _to_cell(value: Any) -> str:
        """Render one JSON value as a CSV cell.

        ``None`` becomes empty, booleans become ``true`` / ``false``,
        numbers use their canonical string form, strings pass through,
        and nested dicts / lists are JSON-stringified compactly with
        non-ASCII characters kept verbatim.
        """
        if value is None:
            return ""
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return str(value) if math.isfinite(value) else json.dumps(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(context: dict[str, Any], error_type: str, message: str) -> dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
